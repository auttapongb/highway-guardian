# HWAY GUARDIAN 2.0 — ทางหลวงพิทักษ์

## AI Edge Highway Guardian: Safety + Maintenance + Citizen Engagement

**Challenges:** #4 Highway Safety · #3 Maintenance Innovation · #6 Digital Service

> *One edge device on every DOH patrol vehicle = real-time pothole detection + accident detection + LINE citizen alerts. Covers 3 challenges with one unified product.*

---

## 1. The Problem

**Thailand's road crisis:**
- ~20,000 road deaths/year — 9th highest globally
- 70,000+ km of DOH national highways, impossible to inspect manually
- Existing DOH CCTV cameras are manually monitored — no AI
- Traffy (แทรฟฟี่) covers BMA city roads only — NO AI, NO proactive alerts
- Citizens have no LINE-based channel for DOH highway issues
- Pothole/crack inspection is manual, slow, and infrequent

**Current tools are fragmented:**
- Traffy → BMA city roads only, reactive citizen reporting
- Liv-24 → factory safety, not roads
- AIS/TRUE AI cameras → generic, not highway-specific
- DOH legacy PMS → manual visual inspection, outdated

**Nobody offers integrated Safety + Maintenance + Citizen Service on DOH highways.**

---

## 2. The Solution: HWAY GUARDIAN

A **$120 edge-AI device** mounted on DOH patrol vehicles that simultaneously:

| Mode | What It Detects | Challenge |
|------|----------------|-----------|
| 🛣️ **Road Health** | Potholes, cracks, surface defects + GPS tag | #3 Maintenance |
| 🚨 **Safety** | Wrong-way driving, stopped vehicles, accidents, debris | #4 Safety |
| 📱 **LINE Citizen** | AI-verified citizen reports + proactive driver alerts | #6 Digital Service |

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOH Patrol Vehicle                           │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Edge AI Box (RPi5 + Hailo-8 + Camera + 4G + GPS)   │      │
│  │  ┌────────────────────┐  ┌──────────────────────┐    │      │
│  │  │ YOLOv11 Road Defect│  │ YOLOv11 Safety       │    │      │
│  │  │ → Potholes         │  │ → Wrong-way driving  │    │      │
│  │  │ → Cracks           │  │ → Stopped vehicles   │    │      │
│  │  │ → Surface damage   │  │ → Accident detection │    │      │
│  │  │ → GPS-tagged       │  │ → Debris on road     │    │      │
│  │  └────────────────────┘  └──────────────────────┘    │      │
│  │                    │                                  │      │
│  │                    ▼                                  │      │
│  │          ┌─────────────────┐                          │      │
│  │          │ Hailo-8 NPU     │ ← Runs both models       │      │
│  │          │ simultaneously  │    at 30+ FPS             │      │
│  │          └─────────────────┘                          │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Cloud Backend  │
                    │  (FastAPI)      │
                    └───────┬─────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ DOH        │  │ LINE OA    │  │ Public     │
    │ Dashboard  │  │ Alerts     │  │ Map        │
    │ (Dispatch) │  │ (Drivers)  │  │ (Citizens) │
    └────────────┘  └────────────┘  └────────────┘
```

### Citizen LINE OA Flow

```
1. Citizen sees pothole on Highway 304
2. Opens LINE @ทางหลวงพิทักษ์
3. Sends photo + auto-GPS location
4. AI verifies & classifies (pothole / crack / debris / etc.)
5. Report auto-routed to responsible DOH district office
6. Citizen receives: "✅ ได้รับรายงานแล้ว — กำหนดซ่อมภายใน 7 วัน"
7. Public map updates with issue marker
8. When fixed: "✅ หลุมบ่อทางหลวงหมายเลข 304 กม.25+500 ได้รับการซ่อมแซมแล้ว"
```

---

## 3. Differentiation from Existing Solutions

### Vs. Traffy (แทรฟฟี่) — OUR MAIN BENCHMARK

| Aspect | Traffy | HWAY GUARDIAN |
|--------|--------|--------------|
| **Coverage** | BMA city roads only | DOH national highways (70,000+ km) |
| **AI Detection** | ❌ Citizen reports only | ✅ Dual YOLO auto-detection from edge cameras |
| **Photo AI** | ❌ No analysis | ✅ AI verifies & classifies citizen photos |
| **Proactive Alerts** | ❌ None | ✅ LINE push: "⚠️ Accident ahead — slow down" |
| **Hardware** | ❌ Phone only | ✅ Edge AI box on DOH vehicles + phone camera |
| **Dispatch** | Manual routing | ✅ Auto-routed to DOH district office |
| **Transparency** | Basic | ✅ Public map: all issues + fix status |

### Vs. Liv-24 Edge AI Box

| Aspect | Liv-24 | HWAY GUARDIAN |
|--------|--------|--------------|
| **Domain** | Factory/indoor safety | Highway roads |
| **Detection** | PPE compliance, zone intrusion | Potholes, cracks, accidents, wrong-way |
| **Mount** | Fixed indoor | Vehicle-mounted + gantry-mountable |
| **Mobility** | ❌ Static | ✅ Patrols 100+ km/day per vehicle |
| **Connectivity** | Local only | Cellular + cloud dashboard |

### Vs. AIS/TRUE AI Camera Solutions

| Aspect | AIS/TRUE | HWAY GUARDIAN |
|--------|---------|--------------|
| **Cost** | Monthly service fee + camera | One-time ~$120/device, DOH-owned |
| **DOH Integration** | Generic | Built for DOH workflow + LINE |
| **Edge Processing** | Server-side | On-device (Hailo-8 NPU) |
| **Data Ownership** | Vendor-controlled | DOH-owned, open-source |

---

## 4. Technical Architecture

### Hardware (Per Vehicle)

| Component | Model | Cost (THB) |
|-----------|-------|-----------|
| Single-board computer | Raspberry Pi 5 (8GB) | 4,500 |
| AI accelerator | Hailo-8 M.2 | 3,500 |
| Camera | Raspberry Pi Camera Module 3 or USB | 1,500 |
| Connectivity | 4G HAT + SIM (AIS/TRUE/DTAC) | 2,000 |
| GPS | GPS HAT (U-blox) | 1,000 |
| Enclosure | Weatherproof IP65 case | 1,000 |
| Storage | 64GB SD card | 500 |
| **Total per vehicle** | | **~14,000 THB (~$400)** |

### Software Stack

**Edge AI (on RPi5 + Hailo-8):**
- HailoRT runtime + Hailo YOLO pipeline
- YOLOv11n-seg (road surface segmentation) — fine-tuned on Thai road data
- YOLOv11n (safety detection) — pretrained COCO + fine-tuned on highway scenarios
- MQTT/HTTP client for event upload
- GPS NMEA parser

**Backend (Cloud):**
- FastAPI (Python) — REST API + WebSocket
- PostgreSQL + PostGIS — all events geotagged
- LINE Messaging API — push alerts + citizen reporting
- Mapbox GL / Leaflet — dashboard maps
- Docker — containerized deployment

**LINE Bot:**
- LINE Messaging API SDK (Python)
- Photo AI verification pipeline
- Flexible Flex Message alerts (rich UI cards)
- Rich menu with: Report Issue · My Reports · Nearby Hazards · Emergency

---

## 5. Implementation Plan (6 Weeks)

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| **1** | Hardware setup + OS | RPi5 with Hailo-8, camera, GPS, 4G all working |
| **2** | YOLO model pipeline | Dual YOLO running on Hailo-8 at 30+ FPS |
| **3** | Backend + dashboard | FastAPI + PostGIS + Map dashboard with real events |
| **4** | LINE OA integration | Working LINE bot: citizen report → AI verify → dispatch |
| **5** | Edge-to-cloud pipeline | Full flow: camera → edge AI → cloud → LINE alert |
| **6** | Demo + submission | 5-min video, working demo, documentation |

### Demo Scenario

```
1. Show RPi5 + Hailo-8 edge box plugged into car USB
2. Camera faces road → live view on laptop
3. Place a paper "pothole" on the road → AI detects it → GPS tagged
4. Place a toy car "stopped on shoulder" → AI detects it
5. Open LINE @ทางหลวงพิทักษ์ → send photo of fake pothole
6. AI verifies → report appears on dashboard
7. LINE receives: "⚠️ Pothole detected on demo road"
```

---

## 6. Cost Breakdown

| Category | Item | Cost (THB) |
|----------|------|-----------|
| **Hardware** | 2x Edge AI boxes (RPi5 + Hailo-8 + camera + 4G + GPS) | 28,000 |
| **Hardware** | Extra cameras, cables, cases | 5,000 |
| **Dev** | 6 weeks × 1 engineer at 150K THB/month | 225,000 |
| **Cloud** | 3 months hosting (VPS + PostgreSQL + domain) | 10,000 |
| **LINE OA** | LINE official account setup (1 year) | 0 (free) |
| **Contingency** | 15% | 30,000 |
| **Total** | | **~298,000 THB (~$8,600)** |

*Pilot-ready with 2 vehicle units + full cloud backend*

---

## 7. 5-Pillar Submission Outline

### Pillar 1: Problem Statement
> Thailand ranks 9th globally in road deaths. DOH maintains 70,000+ km of highways with manual inspection. Citizens have no way to report issues on national highways. Traffy covers Bangkok only.

### Pillar 2: Solution Overview
> HWAY GUARDIAN: a $120 edge-AI device on DOH vehicles that automatically detects potholes, cracks, accidents, and wrong-way driving — while giving citizens a LINE OA to report issues with AI verification.

### Pillar 3: Technology & Innovation
> Dual YOLOv11 on a RPi5 + Hailo-8 edge AI accelerator running simultaneously at 30+ FPS. All detections GPS-tagged and uploaded via 4G. LINE OA with AI-powered photo verification. Public transparency map. Open-source.

### Pillar 4: Impact & Scalability
> Pilot: 2 vehicles covering 100 km/day = 70+ km of continuous road monitoring per week. Scale: 500+ DOH patrol vehicles nationwide = full highway coverage. LINE OA: zero adoption barrier for citizens. Cost: 14,000 THB per vehicle (vs 500,000+ THB for vendor systems).

### Pillar 5: Team & Feasibility
> 6-week build. All components off-the-shelf. YOLO models are proven (published accuracy >95%). LINE SDK well-documented. Team with production AI deployment experience (trading bots, video pipelines, edge AI).
