<div align="center">
  <br/>
  <h1>🏋️ Gym Equipment Analyzer</h1>
  <p>
    <strong>Snap a photo — AI identifies every piece of equipment and shows you how to use it properly with demo videos.</strong>
  </p>
  <p>
    <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white"/>
    <img alt="Flask" src="https://img.shields.io/badge/Flask-3.0+-000000?logo=flask&logoColor=white"/>
    <img alt="Ollama" src="https://img.shields.io/badge/Vision-Gemma3:12b-38FFDA?logo=ollama&logoColor=white"/>
    <img alt="License" src="https://img.shields.io/badge/License-MIT-green"/>
  </p>
  <br/>
</div>

---

## ✨ What It Does

Take or upload a photo of any gym equipment — dumbbells, barbells, cable machines, treadmills, benches, you name it. The app:

1. 🔍 **Detects every piece of equipment** in the photo (even multiple items at once)
2. 📋 **Shows which muscle groups** each equipment targets
3. 🎥 **Plays YouTube demo videos** with proper form demonstrations
4. 📝 **Provides step-by-step instructions** on how to use each equipment
5. ⚠️ **Lists common mistakes and safety tips**

> 🧠 **No more googling "how to use this gym machine" — just snap a photo and learn instantly.**

---

## 🖥️ How It Works

```
              ┌─────────────┐
              │  📸 Snap    │
              │  a Photo    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │  🌐 Cloud   │  ← gemma3:12b via Ollama Cloud
              │  Vision AI  │     (3 different prompts for accuracy)
              └──────┬──────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Barbell  │ │ Dumbbell │ │ Cable    │
    │          │ │          │ │ Machine  │
    └────┬─────┘ └────┬─────┘ └────┬─────┘
         │            │            │
         ▼            ▼            ▼
    ┌─────────────────────────────────────┐
    │     📦 Curated Exercise Database    │
    │   (16 equipment types · 26 moves)   │
    └─────────────────────────────────────┘
         │            │            │
         ▼            ▼            ▼
    ┌─────────────────────────────────────┐
    │     📱 Beautiful Results Cards      │
    │  • Muscle targeting tags 🎯        │
    │  • Step-by-step instructions 📝    │
    │  • YouTube demo videos 🎥          │
    │  • Safety tips & mistakes ⚠️       │
    └─────────────────────────────────────┘
```

### Step-by-step Pipeline

| Step | What Happens | Details |
|:----:|-------------|---------|
| **1** | **Image Upload** | User takes/selects a photo via camera, file picker, or drag & drop |
| **2** | **Multi-pass Vision** | The app sends the image to **Gemma3:12b** (cloud AI) with 3 different prompts asking it to list all visible equipment |
| **3** | **Keyword Matching** | A smart keyword engine scans the AI's descriptions and matches them against the **curated exercise database** |
| **4** | **Retry Logic** | If fewer than 3 items were detected, a 4th "second look" prompt kicks in to catch missed equipment |
| **5** | **Results Assembly** | For each matched equipment, the app pulls full exercise data — muscles worked, step-by-step instructions, YouTube demo videos, safety tips |
| **6** | **Responsive Display** | Results render as a clean grid of cards — 1 column on phone, 2 on tablet, 3-4 on desktop |

---

## 🗄️ Exercise Database

All exercise data is **hand-curated** — no AI-generated instructions that might give bad advice. The database includes:

| Equipment | Exercises | Categories |
|-----------|-----------|------------|
| 🏋️ Barbell | Bench Press, Squat, Deadlift | Free Weight |
| 🏋️ Dumbbell | Bicep Curl, Shoulder Press, Chest Press, Row | Free Weight |
| 🔔 Kettlebell | Kettlebell Swing | Free Weight |
| 💪 Resistance Band | Band Rows | Free Weight |
| 🪑 Weight Bench | Bench Press, Dumbbell Row | Free Weight |
| ⛓️ Cable Machine | Chest Fly, Tricep Pushdown | Cable |
| 🔧 Smith Machine | Smith Machine Squat | Machine |
| 🦵 Leg Press Machine | Leg Press | Machine |
| 🏛️ Multi-Gym / Weight Machine | Lat Pulldown, Seated Cable Row, Chest Press | Machine |
| 🚣 Rowing Machine | Indoor Rowing | Cardio |
| 🔼 Pull-Up Bar | Pull-Up, Chin-Up | Bodyweight |
| 🧘 Yoga Mat / Mat | Plank, Push-Up | Bodyweight |
| 🏃 Treadmill | Walking / Running | Cardio |
| 🚴 Exercise Bike | Stationary Cycling | Cardio |
| 🔄 Elliptical | Elliptical Training | Cardio |

Each exercise entry contains:
- ✅ **Muscles worked** (e.g., Pectoralis Major, Triceps Brachii)
- 📋 **Step-by-step instructions** (numbered, clear)
- ❌ **Common mistakes** to avoid
- 🛡️ **Safety tips** for injury prevention
- 🎥 **YouTube video ID** for a real demonstration

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **An Ollama Cloud API key** (or local Ollama with a vision model like `moondream`)
- **Cloudflared** *(optional, for public access via tunnel)*

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/mapsize17/gym-analyzer.git
cd gym-analyzer

# 2. Install Python dependencies
pip install flask requests

# 3. Set your Ollama API key
export OLLAMA_API_KEY="your_ollama_cloud_key_here"
# Or create a .env file:
echo 'OLLAMA_API_KEY=your_key_here' > .env
```

### Running the App

```bash
# Start the Flask server
python3 app.py
```

The server starts on **`http://localhost:5005`** — open it in your browser and you're ready.

### Making It Public (Optional)

```bash
# Install cloudflared
# https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/

# Create a public tunnel
cloudflared tunnel --url http://localhost:5005 --no-autoupdate

# Visit the https://xxx.trycloudflare.com URL shown in the output
```

Or use the convenience script:

```bash
bash start.sh
```

---

## 📱 Features

### Camera Capture
Point your phone's camera at gym equipment and snap — works on mobile browsers via the native camera API.

### Upload & Drag & Drop
Desktop users can upload images or drag & drop them directly onto the upload zone.

### Multi-Equipment Detection
One photo can detect **10+ pieces of equipment simultaneously** — the AI lists everything it sees, and the app matches each one against the database.

### Loading Overlay
A full-screen overlay with animated progress steps keeps the UI clean during the ~30-60 second analysis.

### Fully Responsive
- **Mobile** (≤600px): Single column
- **Tablet** (600-960px): 2 columns
- **Desktop** (960-1200px): 3 columns
- **Wide** (≥1200px): 4 columns

### Dark Theme
Easy on the eyes in a gym setting — dark background with blue accent colors.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3 + Flask |
| **Vision AI** | Gemma3:12b via Ollama Cloud API (fallback: local moondream) |
| **Frontend** | Vanilla HTML/CSS/JS (no frameworks) |
| **Public Access** | Cloudflare Tunnel (trycloudflare.com) |
| **Video Embeds** | YouTube (youtube-nocookie.com) |
| **Image Processing** | Base64 encoding + multipart form upload |

### Why no frontend framework?
The app is intentionally **framework-free** — a single `index.html` with vanilla CSS and JS. Zero build step, zero dependencies, instant loading. The responsive CSS grid handles all screen sizes cleanly.

### Why curated database instead of AI generation?
Exercise form advice generated by LLMs can be **dangerously inaccurate**. Every instruction, muscle group, and safety tip in this app is **hand-written** by someone who understands proper lifting form. AI is used only for *vision* (identifying what's in the photo) — the actual exercise data is from a trusted source.

---

## 📁 Project Structure

```
gym-analyzer/
├── app.py              # Flask backend — API routes, vision, keyword matching
├── index.html          # Single-page frontend — camera, upload, results
├── start.sh            # Convenience script (Flask + Cloudflare tunnel)
├── .gitignore          # Excludes uploads/, __pycache__/, .env
└── uploads/            # Temporary storage for uploaded images
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OLLAMA_API_KEY` | ✅ (for cloud vision) | Ollama Cloud API key for Gemma3:12b vision |
| `PORT` | ❌ (default: 5005) | Flask server port |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | HTML | Serves the frontend |
| `POST /analyze` | Multipart | Upload image → returns equipment analysis |
| `GET /equipment-list` | JSON | Lists all supported equipment types |

---

## 📸 Example Result

When you upload a photo, here's what you get back for each detected equipment:

```
┌──────────────────────────────────────┐
│  🏋️ Barbell                         │
│  [free_weight]                       │
│                                      │
│  💪 Primary Muscles:                 │
│    Chest · Back · Legs · Shoulders   │
│                                      │
│  🏋️ EXERCISES (3)                   │
│                                      │
│  ┌──────────────────────────────────┐│
│  │ Barbell Bench Press             ││
│  │ 🎥 [YouTube Video]              ││
│  │                                  ││
│  │ 💪 Muscles Targeted:            ││
│  │   Pectoralis Major · Anterior    ││
│  │   Deltoid · Triceps Brachii     ││
│  │                                  ││
│  │ 📋 How To Do It:               ││
│  │ ① Lie flat, feet planted       ││
│  │ ② Unrack, hold above shoulders ││
│  │ ③ Lower to mid-chest           ││
│  │ ④ Press back up                ││
│  │ ⑤ Lock out without overextend  ││
│  │                                  ││
│  │ ❌ Common Mistakes:             ││
│  │   Bouncing bar · Uneven grip    ││
│  │                                  ││
│  │ ✅ Safety Tips:                 ││
│  │   Always use a spotter          ││
│  │   Keep wrists straight          ││
│  └──────────────────────────────────┘│
│  ... more exercises ...             │
│                                      │
│  ⚠️ Safety Warnings                 │
│  • Always warm up                   │
│  • Start light to practice form     │
│  • Consult a trainer if unsure      │
└──────────────────────────────────────┘
```

---

## 🤝 Contributing

### Adding a New Equipment Type

1. Open `app.py`
2. Add a new entry to the `EXERCISE_DB` dictionary following the existing format
3. Add matching keywords to `find_equipment_keywords()` if needed
4. The app picks it up automatically — no restart required (Flask reloader)

### Adding More Exercises

Just add more entries to the `common_exercises` array of any equipment. Each entry needs:
- `name`: Exercise name
- `video_id`: YouTube video ID for demonstration
- `muscles_worked`: Array of muscle names
- `steps`: Array of numbered step strings
- `common_mistakes`: Array of mistake strings
- `safety_tips`: Array of tip strings

---

## 📄 License

This project is open source under the MIT License.

---

<div align="center">
  <p>Built with ❤️ for people who want to make the most of their gym time.</p>
  <p>
    <a href="https://github.com/mapsize17">@mapsize17</a> ·
    <a href="https://github.com/mapsize17/gym-analyzer/issues">Report Issue</a> ·
    <a href="https://github.com/mapsize17/gym-analyzer">GitHub</a>
  </p>
</div>
