# HWAY GUARDIAN 2.0 — ทางหลวงพิทักษ์

**AI Edge Highway Guardian: Safety + Maintenance + Citizen Engagement**

> DOH Hackathon 2026 · Challenges #4 Safety · #3 Maintenance · #6 Digital Service

---

## 🏆 What It Does

**One $120 edge-AI device on DOH patrol vehicles** does 3 jobs simultaneously:

| Mode | What It Detects | Challenge |
|------|----------------|-----------|
| 🛣️ **Road Health** | Potholes, cracks, surface defects + GPS tag | #3 Maintenance |
| 🚨 **Safety** | Wrong-way driving, stopped vehicles, accidents | #4 Safety |
| 📱 **LINE Citizen** | AI-verified citizen reports + proactive alerts | #6 Digital Service |

## 🔥 Why This Wins

**Differentiates from all existing Thai solutions:**

| Vs. | Why We're Different |
|-----|-------------------|
| **Traffy (แทรฟฟี่)** | They're BMA city-only, reactive citizen reporting. We add: AI auto-detection from edge cameras, DOH highways (70,000+ km), proactive LINE alerts |
| **Liv-24 Edge Box** | They're factory safety only. We're road-specific: vehicles-mounted, pothole detection + accident detection |
| **AIS/TRUE AI cameras** | Generic smart city. We're DOH-specific with LINE integration + edge AI that drives with patrol vehicles |

## 🧠 Tech Stack

| Component | Tech | Why |
|-----------|------|-----|
| **Edge AI** | RPi5 + Hailo-8 + Camera + GPS + 4G | $120, 30+ FPS dual YOLO, vehicle-mountable |
| **Detection** | YOLOv11n-seg + YOLOv11n | Road surface defects + safety incidents |
| **Backend** | FastAPI + PostgreSQL + PostGIS | Real-time API, geospatial queries |
| **LINE OA** | LINE Messaging API (Flex Messages) | 94% penetration in Thailand |
| **Dashboard** | Leaflet + Chart.js | Real-time heatmap, by-type stats |

## 📐 Architecture

```
┌─────────────────────────────────────────────────┐
│ DOH Patrol Vehicle → Edge AI (RPi5+Hailo-8+GPS) │
│   → Pothole detection  ─┐                       │
│   → Accident detection  ─┤                       │
│   → GPS-tagged upload   ─┤                       │
└──────────────────────────┼──────────────────────┘
                           │
┌──────────────────────────▼──────────────────────┐
│           Cloud Backend (FastAPI)                │
│   ┌──────────────┐  ┌──────────────┐            │
│   │ Incident DB  │  │ LINE Alerts  │            │
│   │ (PostGIS)    │  │ (Push/Reply) │            │
│   └──────────────┘  └──────────────┘            │
└──────────────────────┬──────────────────────────┘
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ DOH      │ │ LINE     │ │ Public   │
    │ Dashboard│ │ Citizens │ │ Map      │
    └──────────┘ └──────────┘ └──────────┘
```

## 🚀 Quick Start (Docker)

```bash
# 1. Clone
git clone https://github.com/auttapongb/highway-guardian.git
cd highway-guardian

# 2. Configure LINE OA (for alert features)
cp .env.example .env
# Edit .env with your LINE credentials

# 3. Start all services
docker compose up -d

# 4. Open dashboard
open http://localhost:80

# API docs: http://localhost:8000/docs
```

## 🎯 Demo Scenario (5 Minutes)

1. **Edge AI**: Plug RPi5+Hailo8 into car USB → camera faces road
2. **Pothole detection**: Place paper "pothole" → AI detects it → GPS tagged on map
3. **Safety detection**: Place toy car on "shoulder" → AI flags stopped vehicle
4. **LINE citizen**: Open LINE @ทางหลวงพิทักษ์ → send photo → AI verifies → report on map

## 📊 Project Structure

```
hway-guardian/
├── ai-engine/          # YOLOv11 dual detection pipeline
│   ├── detect.py       # Main detection orchestrator
│   └── config.yaml     # Model + hardware config
├── backend/            # FastAPI server
│   ├── main.py         # API + LINE dispatch + dashboard
│   ├── requirements.txt
│   └── init.sql        # PostGIS schema
├── line-bot/           # LINE OA bot
│   ├── bot.py          # Webhook handler
├── dashboard/          # Real-time map dashboard
│   └── index.html      # Leaflet + Chart.js
├── scripts/
│   └── setup.py        # One-command setup
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.linebot
├── PROPOSAL.md         # Full hackathon submission doc
└── .env.example
```

## 📋 5-Pillar Submission

See [`PROPOSAL.md`](./PROPOSAL.md) for the full hackathon submission document.

**Deadline**: 31 May 2026
**Submit via**: Google Form + 5-min video + 10-slide PDF

## 💰 Prototype Cost

| Item | Cost (THB) |
|------|-----------|
| 2x RPi5 + Hailo-8 + camera + GPS + 4G | 28,000 |
| 6 weeks dev × 1 engineer | 225,000 |
| Cloud hosting (3 months) | 10,000 |
| Contingency | 30,000 |
| **Total** | **~298,000 THB** |

## 🏅 Awards

- 1st: 100,000 THB + Certificate
- 2nd: 50,000 THB
- 3rd: 30,000 THB
- HM: 10,000 THB x2

## License

MIT — Intellectual property owned by the team.
