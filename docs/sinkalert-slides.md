# === SinkAlert: AI-Powered Road Collapse Prediction ===
# DOH HACKATHON 2026 — PROJECT SUBMISSION

---

## SLIDE 1: TITLE SLIDE
## SinkAlert
### AI-Powered Road Collapse Prediction Platform
### ระบบพยากรณ์ถนนยุบด้วยปัญญาประดิษฐ์

**Team Name:** [Your Team Name]
**Category:** Highway Maintenance Innovation + Highway Safety Solution
**DOH HACKATHON 2026**

---

## SLIDE 2: THE PROBLEM — ถนนยุบ คือหายนะที่คาดเดาไม่ได้

**Road subsidence (ถนนยุบ) is a growing crisis in Thailand:**

- Sudden road collapses kill and injure drivers WITHOUT warning
- Damage vehicles, disrupt logistics, cost billions in repairs
- Current inspection: visual only by DOH staff — CANNOT detect underground voids
- Climate change → heavier rainfall → MORE collapses every year

**Recent incidents:** [Insert 2-3 news screenshots with dates and locations]

**The gap:** No system exists to PREDICT where the next collapse will happen

> "We only know a road has collapsed AFTER it collapses. By then, it's too late."

---

## SLIDE 3: WHY NOW?

| Factor | Why It Matters |
|--------|---------------|
| **Satellite data is FREE** | ESA Sentinel-1 provides free SAR satellite data globally |
| **AI is accessible** | YOLOv8, XGBoost, TensorFlow are open-source and proven |
| **DOH already has the fleet** | Survey vehicles already drive every highway — just add a camera |
| **Climate urgency** | Extreme rain events are increasing = more subsidence risk |
| **Thailand can lead** | No other ASEAN country has deployed this yet |

**The technology is ready. The timing is now. The need is urgent.**

---

## SLIDE 4: OUR SOLUTION — SinkAlert

### 3 Data Layers + AI = Collapse Risk Score per Road Segment

```
┌────────────────────────────────────────────────────────────┐
│                      SINKALERT                              │
├──────────────┬──────────────────┬──────────────────────────┤
│  🌍 LAYER 1  │   📸 LAYER 2     │   🌧️ LAYER 3             │
│  SATELLITE   │   DASHCAM AI     │   ENVIRONMENT            │
│  InSAR       │   (YOLOv8)       │                          │
├──────────────┼──────────────────┼──────────────────────────┤
│ Sentinel-1   │ DOH fleet cars   │ Rainfall (met dept API)  │
│ SAR satellite│ + Raspberry Pi   │ Soil moisture data       │
│ FREE data     │ ($80/unit)      │ Traffic load (DOH data)  │
│ mm precision │ Real-time cracks │                          │
│ Every 6-12d  │ GPS-tagged       │ Environmental triggers   │
└──────┬───────┴──────┬───────────┴──────────┬───────────────┘
       │              │                      │
       ▼              ▼                      ▼
┌────────────────────────────────────────────────────────────┐
│            🤖 ML FUSION ENGINE (XGBoost)                    │
│  Combines all 3 layers → Collapse Risk Index 0-100          │
└──────────────────────┬─────────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────────┐
│  📊 OUTPUT DASHBOARD                                        │
│  • Color-coded heatmap (Green/Yellow/Red)                  │
│  • Daily updated for all highways                           │
│  • LINE/Web alerts for HIGH RISK zones                     │
└────────────────────────────────────────────────────────────┘
```

---

## SLIDE 5: LAYER 1 — Satellite InSAR (Innovation)

**What:** Interferometric Synthetic Aperture Radar from space

**How it works:**
1. Sentinel-1 satellite passes over Thailand every 6-12 days
2. Sends radar waves to ground → measures return signal phase
3. Compare two passes → detect EARTH SURFACE MOVEMENT at **millimeter precision**
4. Generate deformation rate map showing which road segments are sinking

**Why it's perfect for DOH:**
- Free data from European Space Agency (€0 cost)
- Covers ENTIRE Thai highway network
- Detects subsidence weeks or MONTHS before collapse is visible on surface
- Open-source processing: PySAR / MintPy (Python)

**Visual:** Show satellite → road → deformation map pipeline

---

## SLIDE 6: LAYER 2 — Dashcam AI (Practicality)

**What:** Computer vision on DOH fleet vehicles

**Hardware:**
- Raspberry Pi 4 (4GB) + Pi Camera = **~2,800 THB per vehicle**
- GPS module for location tagging
- 4G USB dongle for data upload

**Software:**
- YOLOv8 Nano (trained on surface damage)
- Converted to TensorFlow Lite for edge deployment
- Detects: cracks, depressions, water pooling, potholes
- Every detection = GPS-tagged photo + timestamp

**Why it works:**
- DOH survey vehicles already drive ALL highways regularly
- No new vehicle cost — just add the $80 kit
- 4-6 FPS detection running on battery
- Open-source code exists (GitHub: anomaly-detection-dashcam-raspberrypi)

**Visual:** Screenshot of YOLO bounding boxes on road cracks

---

## SLIDE 7: LAYER 3 + ML FUSION — The Intelligence

**Layer 3 — Environmental Data:**
| Data | Source | Why |
|------|--------|-----|
| Rainfall | Thai Met Dept API | Water erodes soil → triggers collapse |
| Soil type | Geological survey | Clay soil is more prone to subsidence |
| Traffic load | DOH traffic data | Heavy trucks accelerate road weakening |

**ML Fusion — XGBoost Model:**

```
Input features:  InSAR rate + CV damage score + rainfall_24h + soil_moisture + traffic_load
Output:          Collapse Risk Index 0-100 per 100m road segment
```

**Training:**
- Train on historical collapse locations (feature: collapsed=YES vs NO)
- Retrain automatically after each real collapse → system gets smarter

**Alert threshold:**
- 🔴 RED (risk > 80): Immediate inspection required, send LINE alert
- 🟡 YELLOW (risk 50-80): Weekly monitoring
- 🟢 GREEN (risk < 50): Normal

---

## SLIDE 8: DEMO — Dashboard Mockup

**SinkAlert Dashboard:** [Insert screenshot/mockup here]

**Dashboard shows:**
1. **Map view:** Thailand highway network color-coded by risk
2. **Risk panel:** Top 10 highest-risk segments with details
3. **Alert timeline:** Recent HIGH risk detections with timestamps
4. **Trend chart:** Deformation rate over time for selected segment

**Sample scenario — Highway 1, KM 23:**
```
InSAR rate:    +8.7mm/year (accelerating)  ⚠️ HIGH
Crack density: 7 detections this month      ⚠️ HIGH
Rainfall:      200mm in past 48h            ⚠️ HIGH
Risk score:    92/100 → 🔴 RED ALERT

Auto-notify: LINE to Phra Nakhon Si Ayutthaya Highway District
```
**Mockup description:** [Replace with actual Canva/Figma image of dashboard]

---

## SLIDE 9: PILOT PLAN & BUDGET

### Phase 1 — Pilot (3 months): Highway 1, Bangkok → Nakhon Ratchasima

| Item | Cost (THB) | Details |
|------|-----------|---------|
| 10x Raspberry Pi kits | 28,000 | Pi 4 + camera + case + SD card |
| 10x 4G dongles | 5,000 | USB cellular modems |
| 10x GPS modules | 2,000 | USB GPS receivers |
| Data (3mo 4G + server) | 10,000 | Cloud VPS + cellular data |
| Engineering (part-time) | 5,000 | Setup and calibration |
| **Total Pilot** | **50,000** | |

### Phase 2 — Nationwide (12 months)
| Item | Cost (THB) |
|------|-----------|
| 200x RPi kits (discount) | 300,000 |
| Satellite data processing | 100,000 (server + software) |
| ML model development | 50,000 |
| Dashboard + training | 50,000 |
| **Total Scale** | **~500,000** |

**Cost per km of highway:** < 1,000 THB/km for full coverage

---

## SLIDE 10: IMPACT & VISION

### What This Means for Thailand

**👥 Lives saved**
- Every road collapse predicted = lives not lost
- Drivers warned before roads become death traps

**💰 Cost savings**
- Preventive maintenance costs < emergency repair
- Less economic disruption from road closures

**🌏 Regional leadership**
- Thailand becomes first ASEAN country with AI-powered road collapse prediction
- Technology transfer to DOH = long-term capability

**🎯 Vision Zero**
> "Our goal: **zero road collapse casualties** in Thailand. Every collapse should be predicted before it happens."

### Our Team
[Team member names + roles]

### Thank You
**SinkAlert** — Predict. Prevent. Protect.

---

## APPENDIX (optional, 5 slides max)

### A1: Technical References
1. ESA Sentinel-1: https://scihub.copernicus.eu
2. PySAR/MintPy: github.com/insarlab/MintPy
3. YOLOv8: github.com/ultralytics/ultralytics
4. XGBoost: github.com/dmlc/xgboost
5. RPi dashcam base: github.com/SubhayanBiswas/Anomaly-Detection-Dashcam-Raspberrypi

### A2: Team Profiles
[Brief bio for each team member — expertise relevant to project]

### A3: Data Sources
| Data | Source | Format | Frequency | Cost |
|------|--------|--------|-----------|------|
| Sentinel-1 SAR | ESA Copernicus | .zip (SLC) | Every 6-12 days | Free |
| Rainfall | Thai Met Dept | API/CSV | Hourly | Free |
| Road damage | DOH inspection log | Excel | Monthly | Internal |
| Soil data | DMR Thailand | Shapefile | Static | Free |

### A4: Technical Architecture Detail
[More detailed system architecture diagram]
