#!/usr/bin/env python3
"""
HWAY GUARDIAN 2.0 — LINE OA Bot

LINE Messaging API bot for citizen reporting and alert notifications.
"""

import os
import json
import hashlib
import hmac
import base64
import logging
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# LINE credentials
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
API_URL = os.getenv("API_URL", "http://localhost:8000")

# LINE API endpoints
LINE_API = "https://api.line.me/v2/bot/message"

WELCOME_MESSAGE = """
🚗 ยินดีต้อนรับสู่ ทางหลวงพิทักษ์ (HWAY GUARDIAN)

บริการแจ้งเหตุและข้อมูลทางหลวงด้วย AI

📸 ส่งรูปถ่าย → AI วิเคราะห์อัตโนมัติ
📍 แจ้งหลุมบ่อ รอยร้าว อุบัติเหตุ สิ่งกีดขวาง
🚨 รับแจ้งเตือนอุบัติเหตุแบบเรียลไทม์

--- คำสั่ง ---
📸 แจ้งเหตุ — ส่งรูปถ่ายพร้อมตำแหน่ง
📊 สถานะ — เช็คสถานะรายงานของฉัน
🗺️ แผนที่ — ดูแผนที่จุดเสี่ยง
🆘 เหตุฉุกเฉิน — โทร 1586 (สายด่วนกรมทางหลวง)
help — คำสั่งทั้งหมด
"""


def reply(reply_token: str, messages):
    """Send reply message via LINE API."""
    if not CHANNEL_ACCESS_TOKEN:
        logger.warning("LINE token not configured")
        return

    if isinstance(messages, str):
        messages = [{"type": "text", "text": messages}]
    elif isinstance(messages, dict):
        messages = [messages]

    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"replyToken": reply_token, "messages": messages}

    try:
        import requests
        resp = requests.post(f"{LINE_API}/reply", headers=headers, json=payload, timeout=10)
        logger.info(f"Reply sent: {resp.status_code}")
        if not resp.ok:
            logger.error(f"LINE API error: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"Reply failed: {e}")


def push(user_id: str, text: str):
    """Push a message to a specific user."""
    if not CHANNEL_ACCESS_TOKEN:
        return
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"to": user_id, "messages": [{"type": "text", "text": text}]}
    try:
        import requests
        resp = requests.post(f"{LINE_API}/push", headers=headers, json=payload, timeout=10)
        logger.info(f"Push to {user_id}: {resp.status_code}")
    except Exception as e:
        logger.error(f"Push failed: {e}")


def verify_signature(body: bytes, signature: str) -> bool:
    """Verify LINE webhook signature."""
    if not CHANNEL_SECRET:
        return True  # Skip verification if no secret configured
    hash = hmac.new(
        CHANNEL_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    expected = base64.b64encode(hash).decode('utf-8')
    return signature == expected


def handle_text_message(event):
    """Handle incoming text from LINE user."""
    text = event.get("message", {}).get("text", "").lower()
    reply_token = event["replyToken"]
    user_id = event.get("source", {}).get("userId", "")

    if any(w in text for w in ["report", "แจ้ง", "ร้องเรียน"]):
        reply(reply_token, "📸 กรุณาส่งรูปถ่ายจุดที่ต้องการแจ้ง\n\nถ่ายรูปสิ่งที่เป็นปัญหาแล้วส่งมาเลย ระบบ AI จะวิเคราะห์ให้อัตโนมัติ")

    elif any(w in text for w in ["status", "สถานะ"]):
        # Check status via backend API
        try:
            import requests
            resp = requests.get(f"{API_URL}/api/stats", timeout=5)
            stats = resp.json()
            msg = (
                f"📊 สถานะทางหลวง\n"
                f"• เหตุการณ์ AI ตรวจจับ: {stats.get('total_ai_incidents', 0)} ครั้ง\n"
                f"• รายงานจากประชาชน: {stats.get('total_citizen_reports', 0)} ครั้ง\n"
                f"• วันนี้: {stats.get('incidents_today', 0)} เหตุการณ์\n"
                f"• กำลังดำเนินการ: {stats.get('pending_reports', 0)} รายการ"
            )
            reply(reply_token, msg)
        except Exception:
            reply(reply_token, "⚠️ ไม่สามารถเชื่อมต่อระบบได้ กรุณาลองใหม่อีกครั้ง")

    elif any(w in text for w in ["help", "ช่วย", "คำสั่ง"]):
        reply(reply_token, WELCOME_MESSAGE)

    elif any(w in text for w in ["map", "แผนที่", "ที่"]):
        reply(reply_token, "🗺️ ดูแผนที่จุดเสี่ยงทางหลวงได้ที่:\nhttps://hwayguardian.com/map")

    elif "1586" in text or "emergency" in text or "ฉุกเฉิน" in text:
        reply(reply_token, "🆘 สายด่วนกรมทางหลวง: 1586\n🚑 แจ้งเหตุฉุกเฉิน: 1669\n🚓 ตำรวจทางหลวง: 1193")

    elif any(w in text for w in ["hello", "hi", "สวัสดี"]):
        reply(reply_token, WELCOME_MESSAGE)

    else:
        reply(reply_token, WELCOME_MESSAGE)


def handle_image_message(event):
    """Handle incoming image — download, forward to AI backend."""
    reply_token = event["replyToken"]
    message_id = event.get("message", {}).get("id", "")
    user_id = event.get("source", {}).get("userId", "")

    # Acknowledge receipt immediately
    reply(reply_token, "📸 รับรูปแล้ว! กำลังวิเคราะห์ด้วย AI... โปรดรอสักครู่")

    # Download image from LINE servers
    if CHANNEL_ACCESS_TOKEN and message_id:
        try:
            headers = {"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
            import requests
            img_resp = requests.get(
                f"https://api-data.line.me/v2/bot/message/{message_id}/content",
                headers=headers,
                timeout=15
            )
            if img_resp.ok:
                # Send to backend for AI analysis
                files = {"file": ("photo.jpg", img_resp.content, "image/jpeg")}
                data = {
                    "user_id": user_id,
                    "issue_type": "unknown",
                    "lat": 0,
                    "lon": 0,
                    "highway_id": "",
                    "description": "ส่งจาก LINE OA"
                }
                try:
                    ai_resp = requests.post(
                        f"{API_URL}/api/reports/photo",
                        files=files,
                        data=data,
                        timeout=15
                    )
                    if ai_resp.ok:
                        result = ai_resp.json()
                        ai = result.get("ai_verification", {})
                        ai_type = ai.get("ai_classification", "unknown")
                        confidence = ai.get("confidence", 0)
                        report_id = result.get("id", "")

                        push(user_id,
                            f"✅ AI วิเคราะห์เสร็จสิ้น!\n"
                            f"📋 ประเภท: {ai_type}\n"
                            f"📊 ความเชื่อมั่น: {confidence:.0%}\n"
                            f"🆔 รหัสรายงาน: #{report_id}"
                        )
                    else:
                        push(user_id, "⚠️ ระบบขัดข้อง กรุณาลองใหม่อีกครั้ง")
                except Exception as e:
                    logger.error(f"AI analysis failed: {e}")
                    push(user_id, "⚠️ ไม่สามารถเชื่อมต่อระบบวิเคราะห์ได้ แต่ว่าได้รับรายงานแล้ว")
            else:
                logger.error(f"LINE image download failed: {img_resp.status_code}")
        except Exception as e:
            logger.error(f"Image processing error: {e}")


# ─── Routes ──────────────────────────────────────────────────────


@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "service": "HWAY GUARDIAN LINE Bot",
        "version": "2.0.0",
        "status": "active",
        "line_configured": bool(CHANNEL_ACCESS_TOKEN)
    })


@app.route("/callback", methods=["POST"])
def callback():
    """LINE webhook endpoint."""
    body = request.data
    signature = request.headers.get("X-Line-Signature", "")

    # Verify signature
    if not verify_signature(body, signature):
        logger.warning("Invalid signature")
        return "Invalid signature", 400

    events = request.json.get("events", [])
    logger.info(f"Received {len(events)} events")

    for event in events:
        event_type = event.get("type")

        if event_type == "message":
            msg_type = event.get("message", {}).get("type")
            if msg_type == "text":
                handle_text_message(event)
            elif msg_type == "image":
                handle_image_message(event)

        elif event_type == "follow":
            # User added the LINE OA as friend
            user_id = event.get("source", {}).get("userId", "")
            push(user_id, WELCOME_MESSAGE)

        elif event_type == "unfollow":
            user_id = event.get("source", {}).get("userId", "")
            logger.info(f"User unfollowed: {user_id}")

    return "OK"


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
