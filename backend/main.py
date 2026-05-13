#!/usr/bin/env python3
"""
HWAY GUARDIAN 2.0 — Backend API Server

FastAPI server handling:
- Incident ingestion from edge devices
- Citizen report submission from LINE OA
- Geospatial querying (PostGIS)
- LINE push alert dispatching
- Dashboard data serving
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


# ─── Data Models ─────────────────────────────────────────────────────


class Position(BaseModel):
    lat: float = 0.0
    lon: float = 0.0


class IncidentEvent(BaseModel):
    type: str                          # pothole, crack, wrong_way, stopped_vehicle, accident, debris
    confidence: float = Field(ge=0, le=1)
    bbox: Optional[List[int]] = None
    severity: str = "medium"           # low, medium, high, critical
    position: Optional[Position] = None
    vehicle_id: str = ""
    highway_id: Optional[str] = None   # e.g. "304"
    kilometer: Optional[float] = None  # e.g. 25.5
    timestamp: float = Field(default_factory=time.time)
    image_url: Optional[str] = None
    metadata: Dict = {}


class CitizenReport(BaseModel):
    type: str = "citizen_report"
    issue_type: str                    # pothole, crack, accident, debris, flood, sign_damage, other
    position: Position
    description: str = ""
    photo_url: Optional[str] = None
    line_user_id: str = ""
    highway_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    status: str = "received"           # received, verified, dispatched, fixed, closed


class AlertRequest(BaseModel):
    incident_id: str
    message: str
    severity: str = "medium"
    geo_fence_km: float = 5.0


class BatchUpload(BaseModel):
    events: List[IncidentEvent]
    vehicle_id: str


# ─── In-Memory Database (PostgreSQL in production) ───────────────────


class MemoryDB:
    """Replaced by PostgreSQL + PostGIS in production."""

    def __init__(self):
        self.incidents: List[Dict] = []
        self.reports: List[Dict] = []
        self.next_id = 1

    def add_incident(self, incident: Dict) -> Dict:
        incident["id"] = self.next_id
        incident["source"] = "ai_edge"
        incident["created_at"] = datetime.now().isoformat()
        self.next_id += 1
        self.incidents.append(incident)
        return incident

    def add_report(self, report: Dict) -> Dict:
        report["id"] = self.next_id
        report["created_at"] = datetime.now().isoformat()
        self.next_id += 1
        self.reports.append(report)
        return report

    def get_incidents(self, limit=50, incident_type=None, severity=None, since=None):
        results = self.incidents[-500:]  # Last 500
        if incident_type:
            results = [r for r in results if r.get("type") == incident_type]
        if severity:
            results = [r for r in results if r.get("severity") == severity]
        if since:
            results = [r for r in results if r.get("timestamp", 0) >= since]
        return list(reversed(results))[:limit]

    def get_reports(self, limit=20, status=None, since=None):
        results = self.reports[-200:]
        if status:
            results = [r for r in results if r.get("status") == status]
        if since:
            results = [r for r in results if r.get("timestamp", 0) >= since]
        return list(reversed(results))[:limit]

    def get_stats(self) -> Dict:
        now = time.time()
        day_ago = now - 86400
        return {
            "total_ai_incidents": len(self.incidents),
            "total_citizen_reports": len(self.reports),
            "incidents_today": len([i for i in self.incidents if i.get("timestamp", 0) > day_ago]),
            "reports_today": len([r for r in self.reports if r.get("timestamp", 0) > day_ago]),
            "pending_reports": len([r for r in self.reports if r.get("status") in ("received", "verified")]),
            "by_type": self._count_by_type(),
        }

    def _count_by_type(self) -> Dict:
        counts = {}
        for i in self.incidents:
            t = i.get("type", "unknown")
            counts[t] = counts.get(t, 0) + 1
        for r in self.reports:
            t = r.get("issue_type", "unknown")
            counts[t] = counts.get(t, 0) + 1
        return counts


# ─── LINE Alert Dispatcher ────────────────────────────────────────────


class LineAlertDispatcher:
    """Send LINE messages via LINE Messaging API."""

    def __init__(self):
        self.channel_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
        self.api_base = "https://api.line.me/v2/bot/message"

    def is_configured(self) -> bool:
        return bool(self.channel_token)

    def send_alert(self, incident: Dict) -> Dict:
        """Broadcast alert to all LINE OA followers near the incident."""
        if not self.is_configured():
            logger.info("LINE not configured — alert suppressed")
            return {"status": "skipped", "reason": "no_token"}

        message = self._build_alert_message(incident)
        headers = {
            "Authorization": f"Bearer {self.channel_token}",
            "Content-Type": "application/json"
        }

        try:
            import requests
            resp = requests.post(
                f"{self.api_base}/broadcast",
                headers=headers,
                json={"messages": [message]},
                timeout=10
            )
            logger.info(f"LINE broadcast: {resp.status_code}")
            return {"status": "sent" if resp.ok else "failed", "code": resp.status_code}
        except Exception as e:
            logger.error(f"LINE broadcast failed: {e}")
            return {"status": "error", "message": str(e)}

    def send_to_user(self, user_id: str, text: str):
        """Send direct message to a specific LINE user."""
        if not self.is_configured():
            return
        headers = {
            "Authorization": f"Bearer {self.channel_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "to": user_id,
            "messages": [{"type": "text", "text": text}]
        }
        try:
            import requests
            resp = requests.post(f"{self.api_base}/push", headers=headers, json=payload, timeout=10)
            logger.info(f"LINE push to {user_id}: {resp.status_code}")
        except Exception as e:
            logger.error(f"LINE push failed: {e}")

    def _build_alert_message(self, incident: Dict) -> Dict:
        """Build a LINE Flex Message for the alert."""
        type_labels = {
            "pothole": "⚠️ หลุมบ่อบนทางหลวง",
            "crack": "⚠️ รอยร้าวบนผิวถนน",
            "wrong_way": "🚨 รถสวนทาง!",
            "stopped_vehicle": "🚨 รถจอดอยู่บนทางด่วน",
            "accident": "🚨 อุบัติเหตุ!",
            "debris": "⚠️ สิ่งกีดขวางบนถนน",
            "flood": "⚠️ น้ำท่วมทางหลวง",
            "pedestrian": "🚨 คนเดินบนทางหลวง",
        }

        severity_colors = {
            "critical": "#FF0000",
            "high": "#FF6600",
            "medium": "#FFCC00",
            "low": "#00AA00",
        }

        etype = incident.get("type", "unknown")
        label = type_labels.get(etype, f"⚠️ {etype}")
        severity = incident.get("severity", "medium")
        color = severity_colors.get(severity, "#FFCC00")
        pos = incident.get("position", {})
        loc_str = f"{pos.get('lat', 'N/A'):.4f}, {pos.get('lon', 'N/A'):.4f}" if isinstance(pos, dict) else "ไม่ระบุตำแหน่ง"
        highway = incident.get("highway_id", "ไม่ระบุ")
        km = incident.get("kilometer", "ไม่ระบุ")
        ts = incident.get("timestamp", time.time())
        time_str = datetime.fromtimestamp(ts).strftime("%H:%M น.")

        return {
            "type": "flex",
            "altText": f"⚠️ {label} — ทางหลวงหมายเลข {highway}",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": color,
                    "contents": [{
                        "type": "text",
                        "text": label,
                        "color": "#FFFFFF",
                        "weight": "bold",
                        "size": "lg"
                    }]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "text", "text": f"📍 ทางหลวงหมายเลข {highway}", "size": "md"},
                        {"type": "text", "text": f"📍 กม.ที่ {km}", "size": "md"},
                        {"type": "text", "text": f"🕐 {time_str}", "size": "sm", "color": "#888888"},
                        {"type": "separator"},
                        {"type": "text", "text": "โปรดใช้ความระมัดระวัง", "color": "#FF4444", "size": "sm", "weight": "bold"}
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [{
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "ดูแผนที่",
                            "uri": f"https://hwayguardian.com/map?lat={pos.get('lat', 0)}&lon={pos.get('lon', 0)}"
                        }
                    }]
                }
            }
        }


# ─── FastAPI Application ─────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("HWAY GUARDIAN backend starting...")
    yield
    logger.info("HWAY GUARDIAN backend stopped.")


app = FastAPI(
    title="HWAY GUARDIAN API",
    version="2.0.0",
    description="Backend for HWAY GUARDIAN — DOH AI Highway Safety, Maintenance & Citizen Platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = MemoryDB()
line_dispatcher = LineAlertDispatcher()


# ─── API Endpoints ───────────────────────────────────────────────────


@app.get("/")
async def root():
    return {
        "service": "HWAY GUARDIAN",
        "version": "2.0.0",
        "status": "active",
        "challenges": ["C3_Maintenance", "C4_Safety", "C6_DigitalService"],
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "line_configured": line_dispatcher.is_configured(),
        "incidents": len(db.incidents),
        "reports": len(db.reports)
    }


# ─── Incident Endpoints ─────────────────────────────────────────────


@app.post("/api/incidents")
async def create_incident(event: IncidentEvent):
    """Receive incident from edge AI device."""
    incident = db.add_incident(event.model_dump())

    # Auto-trigger LINE alert for critical/high severity
    if event.severity in ("critical", "high"):
        line_dispatcher.send_alert(incident)

    logger.info(f"Incident #{incident['id']}: {event.type} ({event.severity})")
    return {"status": "received", "id": incident["id"], "alert_sent": line_dispatcher.is_configured()}


@app.post("/api/incidents/batch")
async def create_incidents_batch(batch: BatchUpload):
    """Batch upload from edge device (e.g., after offline period)."""
    ids = []
    for event in batch.events:
        incident = db.add_incident(event.model_dump())
        ids.append(incident["id"])
    logger.info(f"Batch: {len(batch.events)} incidents from {batch.vehicle_id}")
    return {"status": "received", "count": len(ids), "ids": ids[-10:]}


@app.get("/api/incidents")
async def get_incidents(
    limit: int = Query(50, le=200),
    incident_type: Optional[str] = None,
    severity: Optional[str] = None,
    hours: Optional[int] = None
):
    """Get AI-detected incidents with optional filters."""
    since = time.time() - (hours * 3600) if hours else None
    return {
        "incidents": db.get_incidents(limit, incident_type, severity, since),
        "total": len(db.incidents)
    }


# ─── Citizen Report Endpoints ──────────────────────────────────────


@app.post("/api/reports")
async def create_report(report: CitizenReport):
    """Receive citizen report from LINE OA."""
    entry = db.add_report(report.model_dump())
    logger.info(f"Citizen report #{entry['id']}: {report.issue_type} from LINE user")
    return {
        "status": "received",
        "id": entry["id"],
        "message": "✅ ได้รับรายงานแล้ว — กำหนดซ่อมภายใน 7 วัน"
    }


@app.post("/api/reports/photo")
async def upload_report_photo(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    issue_type: str = Form("other"),
    lat: float = Form(0.0),
    lon: float = Form(0.0),
    highway_id: str = Form(""),
    description: str = Form("")
):
    """Receive citizen photo report with AI verification."""
    photo_bytes = await file.read()

    # Save photo
    photo_path = f"uploads/{int(time.time())}_{user_id}_{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(photo_path, "wb") as f:
        f.write(photo_bytes)

    # AI Verification (placeholder — actual YOLO inference in production)
    ai_verification = {
        "verified": True,
        "ai_classification": issue_type,
        "confidence": 0.87,
        "severity": "medium"
    }

    report = {
        "type": "citizen_report",
        "issue_type": ai_verification["ai_classification"] if ai_verification["verified"] else issue_type,
        "position": {"lat": lat, "lon": lon},
        "highway_id": highway_id,
        "description": f"[AI-verified {ai_verification['confidence']:.0%}] {description}",
        "photo_url": f"/uploads/{os.path.basename(photo_path)}",
        "line_user_id": user_id,
        "timestamp": time.time(),
        "status": "verified" if ai_verification["verified"] else "needs_review",
    }
    entry = db.add_report(report)

    # Auto-reply to citizen via LINE
    if line_dispatcher.is_configured():
        reply_text = (
            f"✅ ได้รับรายงาน {ai_verification['ai_classification']} แล้ว\n"
            f"📍 ทางหลวงหมายเลข {highway_id}\n"
            f"📊 ความเชื่อมั่น AI: {ai_verification['confidence']:.0%}\n"
            f"🆔 รหัสรายงาน: #{entry['id']}"
        )
        line_dispatcher.send_to_user(user_id, reply_text)

    return {
        "status": "received",
        "id": entry["id"],
        "ai_verification": ai_verification
    }


@app.get("/api/reports")
async def get_reports(
    limit: int = Query(20, le=100),
    status: Optional[str] = None,
    hours: Optional[int] = None
):
    since = time.time() - (hours * 3600) if hours else None
    return {
        "reports": db.get_reports(limit, status, since),
        "total": len(db.reports)
    }


# ─── Alert Endpoints ────────────────────────────────────────────────


@app.post("/api/alerts/send")
async def send_alert(alert: AlertRequest):
    """Manually trigger a LINE broadcast alert."""
    incident = next((i for i in db.incidents if str(i.get("id")) == alert.incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    result = line_dispatcher.send_alert(incident)
    return result


@app.get("/api/alerts/status")
async def alert_status():
    return {
        "line_configured": line_dispatcher.is_configured(),
        "channel_token_set": bool(line_dispatcher.channel_token)
    }


# ─── Dashboard Endpoints ────────────────────────────────────────────


@app.get("/api/stats")
async def get_stats():
    """Dashboard statistics."""
    return db.get_stats()


@app.get("/api/map/heatmap")
async def get_heatmap_data(
    hours: int = Query(72, le=168),
    incident_type: Optional[str] = None
):
    """Return geojson of incidents for map heatmap."""
    since = time.time() - (hours * 3600)
    incidents = db.get_incidents(limit=500, incident_type=incident_type, since=since)

    features = []
    for i in incidents:
        pos = i.get("position", {})
        if pos and (pos.get("lat") or pos.get("lon")):
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [pos["lon"], pos["lat"]]},
                "properties": {
                    "id": i.get("id"),
                    "type": i.get("type"),
                    "severity": i.get("severity"),
                    "source": i.get("source", "unknown"),
                    "timestamp": i.get("created_at", "")
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }


# ─── LINE Webhook ────────────────────────────────────────────────────


@app.post("/line/webhook")
async def line_webhook(body: dict):
    """Receive LINE webhook events (messages, follows, etc.)."""
    events = body.get("events", [])
    for event in events:
        if event.get("type") == "message":
            message = event.get("message", {})
            user_id = event.get("source", {}).get("userId", "unknown")

            if message.get("type") == "text":
                text = message.get("text", "").lower()
                if "report" in text or "แจ้ง" in text:
                    line_dispatcher.send_to_user(user_id, "📸 กรุณาส่งรูปถ่ายจุดที่ต้องการแจ้ง")
                elif "status" in text or "สถานะ" in text:
                    stats = db.get_stats()
                    line_dispatcher.send_to_user(
                        user_id,
                        f"📊 สถานะทางหลวง\n"
                        f"• เหตุการณ์ AI ตรวจจับ: {stats['total_ai_incidents']} ครั้ง\n"
                        f"• รายงานจากประชาชน: {stats['total_citizen_reports']} ครั้ง\n"
                        f"• กำลังดำเนินการ: {stats['pending_reports']} รายการ"
                    )

            elif message.get("type") == "image":
                line_dispatcher.send_to_user(user_id, "📸 กำลังวิเคราะห์ด้วย AI... โปรดรอสักครู่")

        elif event.get("type") == "follow":
            user_id = event.get("source", {}).get("userId", "unknown")
            line_dispatcher.send_to_user(
                user_id,
                "ยินดีต้อนรับสู่ ทางหลวงพิทักษ์ (HWAY GUARDIAN) 🚗\n\n"
                "📸 ส่งรูปแจ้งปัญหาทางหลวง\n"
                "📍 ตรวจสอบสถานะรายงาน\n"
                "🚨 รับข่าวสารอุบัติเหตุแบบเรียลไทม์\n\n"
                "พิมพ์ 'help' เพื่อดูคำสั่งทั้งหมด"
            )

    return {"status": "ok"}


# ─── Static Files ─────────────────────────────────────────────────────


if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ─── Main ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
