# 🏥 WardSense ICU — Master Architecture & Hackathon Execution Plan

> **Project Title:** WardSense ICU — Autonomous Clinical Shift-Handoff & Continuity Intelligence Engine  
> **Core Memory Layer:** [Vectorize Hindsight Cloud](https://ui.hindsight.vectorize.io) (`hindsight-client` SDK)  
> **LLM Reasoning Layer:** Groq Cloud (`openai/gpt-oss-120b` & `qwen/qwen3-32b` with Function-Calling Error Recovery)  
> **Orchestration & Desktop Runtime:** Band AI Desktop (`https://www.band.ai`)

---

## 1. 🎯 Executive Summary & PDF Alignment

### Why WardSense ICU Fits Every Rule in Both PDFs
1. **Solves a High-Value Real Business Problem ($50+/mo B2B SaaS Test):**
   - According to the Joint Commission, **80% of serious medical errors in hospitals involve miscommunication during shift handoffs** (when nurses and resident doctors change shifts every 8–12 hours).
   - Hospitals lose millions annually to preventable adverse drug events (ADEs), duplicate lab orders, and ICU readmissions caused by context loss across shifts.
   - **Important Positioning:** WardSense is **NOT** a consumer "symptom checker" or "AI doctor." It is a **B2B Hospital Operations, Compliance & Clinical Continuity Handoff System (I-PASS Protocol)**—combining the PDF's *Incident Response Agent*, *Compliance & Audit Agent*, and *Meeting/Shift Prep Agent* into one mission-critical hospital platform.
2. **Makes Hindsight Memory the Star (25% Judging Weight):**
   - **Stateless AI (Before):** Reads only the current prompt or static chart snippet and approves standard protocol (e.g., *IV Furosemide 80mg bolus*), unaware that 38 hours ago during Night Shift #2, the same drug triggered severe hypokalemia ($K^+ = 2.7\text{ mEq/L}$) and ventricular arrhythmia.
   - **WardSense + Hindsight Cloud (After):** Recalls temporal shift memories (`client.recall()`) across days and shifts, immediately blocks the hazardous order, cites the exact shift nurse observation, and recommends the safe, pre-approved alternative protocol.
3. **Demonstrates the Learning Curve (`Interaction 1 -> Interaction 5 -> Interaction 20`):**
   - **Interaction / Shift 1 (Baseline):** Remembers admission diagnosis, baseline vitals, and initial surgical notes.
   - **Interaction / Shift 5 (Personalized Adaptation):** Learns patient-specific drug sensitivities, fluid resuscitation thresholds, and circadian delirium triggers.
   - **Interaction / Shift 20 (Unit-Wide & Longitudinal Mastery):** Synthesizes multi-week cross-specialty patterns, family directives, and unit-level handoff compliance protocols.

---

## 2. ☁️ Required Technology Stack & Hindsight Cloud Integration

### Mandatory Technologies (From Problem Statements PDF Page 2–3)

| Component | Technology / Service | Official Requirement & Implementation Detail |
| :--- | :--- | :--- |
| **1. Agent Memory (Core)** | **Hindsight Cloud** (`https://ui.hindsight.vectorize.io`) + `hindsight-client` Python SDK | Uses real Hindsight Cloud API (`https://api.hindsight.vectorize.io`) with Promo Code **`MEMHACK99`** ($50 free credits). Implements `retain()`, `recall()`, and `reflect()` across unit memory banks (`wardsense_icu_bank`). Includes a live **Hindsight Cloud Connection Manager** in the UI + automatic local SQLite persistence fallback so live demos never fail if Wi-Fi drops. |
| **2. Desktop Runtime** | **Band AI Desktop** (`https://www.band.ai`) | Configured via root `band.json` manifest exposing start, demo, benchmark, and test workflows, environment variables, and REST endpoints for Band AI Desktop inspection. |
| **3. Fast LLM Engine** | **Groq API** (`https://groq.com/`) | Primary models: **`openai/gpt-oss-120b`** and **`qwen/qwen3-32b`** (with fallback to `llama-3.3-70b-versatile`). Includes explicit **Function Calling Error Handler & JSON Repair Middleware** as required on Page 3 of the Problem Statements PDF. |
| **4. Backend & Auth** | **Python 3.11 + FastAPI + SQLite + JWT Auth** | Production-grade REST API, role-based access control (`Hospital Admin`, `Doctor`, `Nurse`), password hashing, shift check-in sessions, and automated `pytest` suite. |
| **5. Frontend UI** | **Multi-Page Clinical Web App (Jinja2 + Tailwind CSS + Lucide Icons)** | Enterprise healthcare aesthetic inspired by **Epic Systems, Philips IntelliVue, and Linear**—zero "AI-generated neon gradient slop." |

---

## 3. ☁️ How to Set Up & Use Hindsight Cloud (`MEMHACK99`) + Band AI

### A. Hindsight Cloud Setup (2 Minutes)
1. Go to **[https://ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io)** and create your account.
2. Open the **Billing** section and enter promo code **`MEMHACK99`** to claim **$50 in free Hindsight Cloud credits**.
3. Generate an **API Key** (`HINDSIGHT_API_KEY`) and create/note your Memory Bank ID (or let WardSense auto-initialize `wardsense_icu_clinical_bank`).
4. Paste `HINDSIGHT_API_KEY` into `.env` **OR** paste it directly inside the **WardSense Cloud Settings Modal** in the web UI!
5. Every time a Nurse logs an observation or a Doctor runs an I-PASS handoff / order check:
   - WardSense calls `hindsight_client.retain(bank_id=..., content=..., context=...)` and `hindsight_client.recall(bank_id=..., query=...)` directly against Hindsight Cloud.
   - You can show judges both the **Live Telemetry Drawer** inside WardSense AND the **Hindsight Cloud Dashboard** (`ui.hindsight.vectorize.io`) receiving memories in real time!

### B. Band AI Desktop Setup
1. Open **Band AI Desktop** (`https://www.band.ai`).
2. Add `/Users/luvkushkumar/Documents/RFI` as your project workspace.
3. Band AI reads `band.json` automatically to run the server (`python3 run.py web`), CLI demo (`python3 run.py demo`), and test suite (`pytest`).

---

## 4. 🎨 Enterprise Clinical UI Design System (Non-AI-Generated Look)

To ensure the application looks like a **$100k/year Enterprise Clinical Platform (Epic / Linear / Cerner)** and **NOT** an AI-generated template:

- **Strict Anti-AI-Slop Rules:**
  - ❌ No purple/magenta/neon gradients.
  - ❌ No floating robot icons or emoji clutter in clinical headers.
  - ❌ No generic chatbot bubbles.
- **Visual Language:**
  - **Surface Palette:** Deep Clinical Slate (`#090D16` background, `#111827` cards, `#1E293B` crisp `1px` borders) with high-contrast `#F8FAFC` typography.
  - **Typography:** `Inter` for clinical narratives + `JetBrains Mono` (`tabular-nums`) for vitals, lab values (`K+ 2.7 mEq/L`, `MAP 62 mmHg`), timestamps (`07:00 IST`), and Hindsight memory latency (`42ms`).
  - **Semantic Clinical Badges:**
    - `STABLE` — Emerald (`#10B981`)
    - `WATCHER / CAUTION` — Amber (`#F59E0B`)
    - `CRITICAL / CONTRAINDICATION` — Crimson (`#EF4444`)
    - `HINDSIGHT CLOUD SYNCED` — Clinical Cyan (`#0EA5E9`)

---

## 5. 🔐 Authentication & 3 Role-Based Portals Architecture

### 0. Authentication Pages (`/login` & `/register`)
- **Staff Login & Shift Check-In (`/login`):**
  - Staff Email / Medical License ID + Password + Active Shift Selector (`Morning 07:00–15:00`, `Evening 15:00–23:00`, `Night 23:00–07:00`).
  - Real JWT token authentication stored in HTTP/session cookies + SQLite `users` table.
  - **1-Click Demo Role Switcher (For Judges):** Instant credential auto-fill buttons for:
    - 🏛️ **CMO / Hospital Admin:** `Dr. Vikramaditya Rao (CMO • Admin)`
    - 🩺 **Attending ICU Doctor:** `Dr. Arindam Sen (MD, Critical Care • Attending)`
    - 👩‍⚕️ **Senior ICU Nurse:** `Sister Priya Nair (RN, CCRN • Charge Nurse)`
- **Staff Registration (`/register`):**
  - Full account creation with Full Name, Staff Badge ID, Role (`admin`, `doctor`, `nurse`), ICU Unit (`Cardiac ICU`, `MICU-East`, `Neuro ICU`), and Password.

---

### Page 1: 🏛️ Hospital Command Center (`/hospital` — Admin & CMO Portal)
*Designed for Hospital Leadership & Quality/Compliance Directors*

1. **Live ICU Floor Telemetry & Bed Matrix (4 Pre-Loaded Realistic ICU Patients):**
   - **ICU-04:** *Rajeshwar Sharma (62M, Post-CABG Cardiac ICU)* — Critical Diuretic/Hypokalemia Arrhythmia History.
   - **ICU-07:** *Ananya Deshmukh (34F, Septic Shock / MICU)* — Delayed Beta-Lactam Anaphylactoid Sensitivity noted 3 shifts ago.
   - **ICU-11:** *Col. Harbinder Singh (71M, Acute Ischemic Stroke / Neuro ICU)* — Strict Permissive Hypertension Window & Nocturnal Delirium Trigger.
   - **ICU-15:** *Meera Krishnan (49F, Post-Lobectomy Thoracic ICU)* — Heparin-Induced Thrombocytopenia (HIT) Watch & Epidural Catheter Hold constraint.
2. **Shift Handoff Compliance & Risk Audit:**
   - Tracks completed vs. pending Nurse-to-Nurse and Doctor-to-Doctor handoffs across shifts.
   - Displays **Prevented Adverse Events Counter** and **Estimated Cost Avoidance ($ / ₹)** powered by Hindsight recalls.
3. **Hindsight Cloud Memory Bank Control Center:**
   - Live connection badge (`Connected to Hindsight Cloud: ui.hindsight.vectorize.io` vs `Hybrid Fallback`).
   - API Key & Bank ID live configuration modal + **"Sync All Seed Memories to Hindsight Cloud"** 1-click button.
   - Global Memory Stream showing every `retain()` and `recall()` operation across the hospital.

---

### Page 2: 🩺 Doctor Clinical Continuity Portal (`/doctor` — Attending / Resident View)
*Designed for Incoming Shift Physicians taking over patient care*

1. **Automated I-PASS Shift Handoff Synthesizer (Powered by `hindsight.recall()`):**
   - Generates structured **I-PASS** brief (*Illness Severity, Patient Summary, Action List, Situation Awareness/Contingency, Synthesis*) by recalling memories from the last 1 to 20 shifts.
   - Highlights exact temporal provenance (e.g., *"Recalled from Shift #2 (38h ago) — Nurse Priya Nair"*).
2. **Medication & Order Safety Verifier (Side-by-Side "Stateless AI vs. Hindsight Memory"):**
   - Doctor tests a clinical order (or clicks 1-click preset orders like *"Order IV Furosemide 80mg Stat Bolus"*).
   - **Left Column (Stateless LLM):** Approves the dangerous order because it only sees current fluid overload.
   - **Right Column (WardSense + Hindsight Cloud):** Fires a **CRITICAL CONTRAINDICATION BLOCK**, cites the exact past shift memory recalled from Hindsight Cloud, and provides the safe contingency order.
3. **Interactive Learning Curve Simulator (`Shift 1 -> Shift 5 -> Shift 20`):**
   - Visualizes how the agent's clinical precision evolves from generic textbook advice at Shift 1, to adverse-reaction awareness at Shift 5, to full longitudinal precision at Shift 20.
4. **Physician Sign-Out & Contingency Logger (`hindsight.retain()`):**
   - Allows the doctor to commit overnight "If/Then" clinical contingencies into Hindsight Cloud for the next shift.

---

### Page 3: 👩‍⚕️ Nurse Bedside & Shift Handoff Portal (`/nurse` — Bedside ICU Nurse View)
*Designed for ICU Nurses recording bedside events and executing shift handoffs*

1. **Bedside Shift Observation & Adverse Event Logger (`hindsight.retain()`):**
   - Structured clinical input for Vitals (`HR`, `BP`, `SpO2`, `Temp`, `K+ / Lactate`), Category (`Medication Reaction`, `Hemodynamic Shift`, `Line/Tube Update`, `Family/Consent Directive`), Severity, and Clinical Narrative.
   - Clicking **"Commit to Hindsight Memory"** executes `client.retain()` in real time and immediately updates the Doctor & Hospital portals.
2. **Cross-Shift Pending Action Tracker (Powered by `hindsight.recall()`):**
   - Automatically surfaces uncompleted tasks left by the outgoing shift nurse (e.g., *"Recheck Serum Potassium at 09:00 IST post-infusion; hold diuretics if K+ < 3.5"*).
3. **1-Click "Simulate Live Bedside Event" Presets:**
   - Lets judges inject a realistic new nursing observation during the live demo and immediately switch to the `/doctor` tab to see Hindsight recall that exact observation when the doctor tries to place a conflicting order!

---

## 6. 🗂️ Project Directory Structure

```text
/Users/luvkushkumar/Documents/RFI/
├── .env                          # Hindsight Cloud & Groq API credentials
├── .env.example                  # Template with MEMHACK99 instructions
├── band.json                     # Band AI Desktop manifest (Mandatory)
├── requirements.txt              # Python dependencies (hindsight-client, fastapi, groq, etc.)
├── pytest.ini                    # Pytest configuration
├── run.py                        # Unified CLI entrypoint (web, demo, compare, test)
├── PLAN.md                       # This Master Plan document
├── README.md                     # Production-grade documentation & architecture
├── article.md                    # Technical article (1,350 words, 0 mentions of "hackathon")
├── docs/
│   └── SUBMISSION_KIT.md         # Title options, LinkedIn post (<800 chars), Reddit guide, Video script
├── data/
│   └── wardsense.db              # SQLite database (Users, Shifts, Beds, Local Memory Mirror)
├── src/
│   ├── __init__.py
│   ├── config.py                 # Env & runtime settings manager
│   ├── database.py               # SQLite schema, seed ICU patients & users
│   ├── auth.py                   # JWT authentication, password hashing, role guards
│   ├── hindsight_memory.py       # Official Hindsight Cloud SDK wrapper (retain/recall/sync)
│   ├── llm_engine.py             # Groq LLM (openai/gpt-oss-120b, qwen/qwen3-32b) + Function-Call Error Handler
│   ├── agent.py                  # Core WardSense clinical handoff & order verification engine
│   ├── server.py                 # FastAPI routes (Pages + REST APIs)
│   └── cli_demo.py               # Rich terminal demonstration for screenshots & video
├── templates/
│   ├── base.html                 # Shared enterprise clinical shell, topbar, Hindsight telemetry drawer
│   ├── login.html                # Clinical Staff Sign-In & 1-Click Role Switcher
│   ├── register.html             # Staff Onboarding & License Registration
│   ├── hospital.html             # Page 1: Hospital Command Center (Admin/CMO)
│   ├── doctor.html               # Page 2: Doctor I-PASS & Order Safety Verifier
│   └── nurse.html                # Page 3: Nurse Bedside Logger & Shift Continuity Checklist
└── tests/
    └── test_wardsense.py         # Automated tests for Auth, Hindsight retain/recall, Groq fallback, APIs
```

---

## 7. 🚨 Mandatory Content & Submission Rules (From Content Guide PDF)

1. **ZERO "HACKATHON" MENTIONS IN CONTENT:**
   - **Rule:** *"Any articles or social posts that mention hackathon in the title or body, including hashtags, will be disqualified."*
   - Both `article.md` and the LinkedIn post in `docs/SUBMISSION_KIT.md` will strictly have **zero occurrences** of the word `hackathon`.
2. **3 Required Links in `article.md`:**
   - Hindsight GitHub: `https://github.com/vectorize-io/hindsight`
   - Hindsight Docs: `https://hindsight.vectorize.io/`
   - Vectorize Agent Memory: `https://vectorize.io/what-is-agent-memory`
3. **Reddit Link Post Requirement:**
   - Publish `article.md` on **Medium, Dev.to, Hashnode, Substack, or LinkedIn Articles**.
   - Share the published URL as a **Link Post** on `r/llmdevs`, `r/sideproject`, `r/aiagents`, or `r/aimemory`.
4. **LinkedIn Post Requirement (< 800 characters):**
   - Written in Andrej Karpathy's direct, technical style.
   - Main post contains the **GitHub Repo Link** + tags **Code.in** + ends with `#AIAgents #AI #Hindsight #AgentMemory #LLM`.
   - **First Comment** contains the **Article URL** and **`https://github.com/vectorize-io/hindsight`**.
5. **YouTube Demo Video (2–5 Minutes, 1080p Public):**
   - Quick intro (30s) $\rightarrow$ Problem without memory (30s) $\rightarrow$ Live Demo showing `retain`/`recall` & before/after (2 min) $\rightarrow$ Key takeaway (30s).
   - Thumbnail generated in 16:9 via Google Nano Banana.

---

## 8. ⏱️ Phased Coding Execution Plan

- **Phase 1: Core Backend, Database, Auth & Hindsight Cloud Engine**
  - `src/config.py`, `src/database.py` (4 realistic ICU patients + 20 shift histories + 3 role accounts), `src/auth.py` (JWT & Role Guards), `src/hindsight_memory.py` (Hindsight Cloud `hindsight-client` SDK + live cloud sync + fallback), `src/llm_engine.py` (Groq `openai/gpt-oss-120b` & `qwen/qwen3-32b` with function-calling error recovery), and `src/agent.py`.
- **Phase 2: Enterprise Clinical Shell + Auth Pages (`/login`, `/register`) + Hospital Page (`/hospital`)**
  - `templates/base.html` (with live Hindsight Cloud Config Modal & Telemetry Drawer), `templates/login.html`, `templates/register.html`, and `templates/hospital.html`.
- **Phase 3: Doctor Portal (`/doctor`) + Nurse Portal (`/nurse`) + FastAPI Server (`src/server.py`)**
  - `templates/doctor.html` (I-PASS Brief, Stateless vs. Hindsight Order Verifier, Shift 1$\rightarrow$5$\rightarrow$20 Learning Curve Simulator), `templates/nurse.html` (Live `retain()` Bedside Logger & Shift Checklist), and `src/server.py`.
- **Phase 4: CLI Demo, `band.json`, Pytest Verification & Disqualification-Proof Content Kit**
  - `src/cli_demo.py`, `band.json`, `tests/test_wardsense.py`, `README.md`, `article.md`, and `docs/SUBMISSION_KIT.md`.
