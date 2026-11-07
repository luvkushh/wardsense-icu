"""SQLite Database Schema, Realistic ICU Clinical Dataset & Seed Data for WardSense."""
import json
import sqlite3
from datetime import datetime
from typing import Any
from src.auth import hash_password
from src.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


SEED_USERS = [
    {
        "email": "admin@apollomed-icu.org",
        "password": "AdminPassword123!",
        "full_name": "Dr. Vikramaditya Rao",
        "role": "admin",
        "badge_id": "CMO-IND-1001",
        "department": "Hospital Command & Quality Directorate",
        "title": "Chief Medical Officer & ICU Director",
        "default_shift": "Morning Shift (07:00 - 15:00 IST)",
    },
    {
        "email": "doctor@apollomed-icu.org",
        "password": "DoctorPassword123!",
        "full_name": "Dr. Arindam Sen, MD (Critical Care)",
        "role": "doctor",
        "badge_id": "MCI-DOC-44912",
        "department": "Cardiac & Medical ICU",
        "title": "Senior Attending Intensivist",
        "default_shift": "Morning Shift (07:00 - 15:00 IST)",
    },
    {
        "email": "nurse@apollomed-icu.org",
        "password": "NursePassword123!",
        "full_name": "Sister Priya Nair, RN, CCRN",
        "role": "nurse",
        "badge_id": "INC-RN-88320",
        "department": "Cardiac & Medical ICU",
        "title": "Critical Care Charge Nurse",
        "default_shift": "Night-to-Morning Handoff (07:00 IST)",
    },
]


SEED_PATIENTS = [
    {
        "patient_id": "ICU-BED-04",
        "bed_number": "Bed 04 • Cardiac ICU",
        "name": "Rajeshwar Sharma",
        "age": 62,
        "gender": "M",
        "mrn": "MRN-904821",
        "admission_diagnosis": "Post-CABG (x3 Vessel) Day 4 • Acute Decompensated Volume Overload",
        "illness_severity": "CRITICAL / WATCHER",
        "status_badge": "CRITICAL CONTRAINDICATION TRAP",
        "attending_md": "Dr. Arindam Sen",
        "primary_nurse": "Sister Priya Nair, RN",
        "current_shift": 20,
        "vitals": {
            "hr": "96 bpm (Sinus w/ rare PVCs)",
            "bp": "138/84 mmHg (MAP 102)",
            "spo2": "93% on 4L Nasal Cannula",
            "rr": "22 /min",
            "temp": "37.1 °C",
            "k_plus": "3.4 mEq/L (Borderline Low)",
            "creatinine": "1.6 mg/dL",
            "fluid_balance": "+1,450 mL (24h net positive)",
        },
        "stateless_trap_order": "Administer IV Furosemide (Lasix) 80mg stat bolus for acute pulmonary congestion and +1.45L fluid overload.",
        "stateless_ai_response": {
            "verdict": "APPROVED — STANDARD PROTOCOL",
            "reasoning": "Patient has +1,450 mL positive fluid balance and SpO2 93% post-CABG. Standard guideline recommends IV loop diuretic bolus (Furosemide 40–80mg IV) to achieve rapid diuresis.",
            "risk_missed": "Missed severe hypokalemic ventricular tachycardia triggered by IV Furosemide bolus 38 hours ago during Night Shift #2, and missed nephrology mandate for continuous Bumetanide + KCl protocol.",
        },
        "hindsight_safe_protocol": {
            "verdict": "BLOCKED — SEVERE ARRHYTHMIA CONTRAINDICATION",
            "recalled_shift": "Shift #5 (38 hours ago • Night Shift) & Shift #14 (14 hours ago)",
            "recalled_author": "Sister Priya Nair, RN & Dr. K. Kulkarni (Electrophysiology)",
            "clinical_why": "In Shift #5, a 60mg IV Furosemide bolus caused rapid urinary potassium wasting (K+ crashed from 3.8 to 2.7 mEq/L in 90 mins), triggering non-sustained Ventricular Tachycardia (NSVT, 180 bpm) requiring emergency Amiodarone and cardioversion standby.",
            "safe_alternative": "HOLD IV Furosemide bolus. Initiate low-dose continuous Bumetanide infusion at 0.5 mg/hr ONLY AFTER administering 40 mEq IV KCl via central line to target Serum K+ >= 4.2 mEq/L.",
            "cost_saved_usd": 42000,
        },
    },
    {
        "patient_id": "ICU-BED-07",
        "bed_number": "Bed 07 • Medical ICU",
        "name": "Ananya Deshmukh",
        "age": 34,
        "gender": "F",
        "mrn": "MRN-773190",
        "admission_diagnosis": "Urosepsis with Refractory Septic Shock • Day 3",
        "illness_severity": "CRITICAL",
        "status_badge": "HIDDEN DRUG REACTION",
        "attending_md": "Dr. Arindam Sen",
        "primary_nurse": "Nurse R. Thomas, RN",
        "current_shift": 12,
        "vitals": {
            "hr": "108 bpm",
            "bp": "98/60 mmHg (MAP 73 on Norepi 0.06 mcg/kg/min)",
            "spo2": "97% on Room Air",
            "rr": "20 /min",
            "temp": "38.4 °C",
            "k_plus": "4.1 mEq/L",
            "creatinine": "1.2 mg/dL",
            "fluid_balance": "+620 mL (24h)",
        },
        "stateless_trap_order": "Restart IV Piperacillin-Tazobactam (Zosyn) 4.5g q6h for persistent fever spike (38.4°C).",
        "stateless_ai_response": {
            "verdict": "APPROVED — BROAD-SPECTRUM EMPIRIC COVERAGE",
            "reasoning": "Fever spike to 38.4°C in urosepsis warrants broad-spectrum antipseudomonal beta-lactam therapy such as Piperacillin-Tazobactam 4.5g IV q6h.",
            "risk_missed": "Admission allergy field says 'No Known Allergies', so stateless AI approves it—completely missing Shift #4 bedside nurse observation of acute bronchospasm, stridor, and truncal urticaria 20 minutes into Zosyn infusion.",
        },
        "hindsight_safe_protocol": {
            "verdict": "BLOCKED — DELAYED ANAPHYLACTOID HYPERSENSITIVITY",
            "recalled_shift": "Shift #4 (44 hours ago • Evening Shift)",
            "recalled_author": "Nurse R. Thomas, RN & Infectious Disease Consult",
            "clinical_why": "Although baseline admission EHR listed 'No Known Allergies', during Shift #4 (02:15 IST) the patient developed acute periorbital edema, wheezing (SpO2 dropped to 86%), and diffuse urticaria 18 minutes into Piperacillin-Tazobactam infusion.",
            "safe_alternative": "DO NOT administer Beta-Lactams. Continue ID-approved Aztreonam 2g IV q8h + Vancomycin (trough-guided) and send repeat blood cultures from peripheral site.",
            "cost_saved_usd": 38500,
        },
    },
    {
        "patient_id": "ICU-BED-11",
        "bed_number": "Bed 11 • Neuro ICU",
        "name": "Col. Harbinder Singh (Retd.)",
        "age": 71,
        "gender": "M",
        "mrn": "MRN-661204",
        "admission_diagnosis": "Acute Right MCA Ischemic Stroke (Post-Thrombectomy Day 3)",
        "illness_severity": "WATCHER",
        "status_badge": "PERFUSION WINDOW CONSTRAINT",
        "attending_md": "Dr. Arindam Sen",
        "primary_nurse": "Nurse Anjali Menon, RN",
        "current_shift": 15,
        "vitals": {
            "hr": "74 bpm",
            "bp": "166/92 mmHg (MAP 117)",
            "spo2": "96% on Room Air",
            "rr": "16 /min",
            "temp": "36.8 °C",
            "k_plus": "4.3 mEq/L",
            "creatinine": "1.0 mg/dL",
            "fluid_balance": "+110 mL (Euvolemic)",
        },
        "stateless_trap_order": "Administer IV Labetalol 20mg push to lower BP from 166/92 mmHg to target normotension (<130/80 mmHg).",
        "stateless_ai_response": {
            "verdict": "APPROVED — ANTIHYPERTENSIVE CONTROL",
            "reasoning": "BP of 166/92 mmHg represents Stage 2 hypertension. Administering IV Labetalol 20mg will safely reduce blood pressure toward normal range.",
            "risk_missed": "Missed Neuro-ICU Shift #6 & #10 perfusion dependency: whenever MAP drops below 105 mmHg, patient develops acute left-sided hemiparesis and expressive aphasia due to collateral penumbra hypoperfusion.",
        },
        "hindsight_safe_protocol": {
            "verdict": "BLOCKED — ISCHEMIC PENUMBRA HYPOPERFUSION RISK",
            "recalled_shift": "Shift #6 (32 hours ago) & Shift #11 (12 hours ago)",
            "recalled_author": "Dr. S. Kapoor (Stroke Neurology) & Sister Priya Nair",
            "clinical_why": "In Shift #6, lowering SBP from 168 to 134 mmHg caused immediate NIHSS score worsening from 4 to 11 (left arm plegia). Repeat CT perfusion confirmed watershed collateral dependence requiring permissive hypertension.",
            "safe_alternative": "MAINTAIN Permissive Hypertension (Target SBP 155–180 mmHg, MAP > 105 mmHg) for another 24 hours. Antihypertensives strictly contraindicated unless SBP > 185/105 mmHg.",
            "cost_saved_usd": 64000,
        },
    },
    {
        "patient_id": "ICU-BED-15",
        "bed_number": "Bed 15 • Thoracic ICU",
        "name": "Meera Krishnan",
        "age": 49,
        "gender": "F",
        "mrn": "MRN-512098",
        "admission_diagnosis": "Post-VATS Left Lower Lobectomy Day 2 • Thoracic Epidural in Situ",
        "illness_severity": "STABLE / WATCHER",
        "status_badge": "EPIDURAL ANTICOAGULATION HOLD",
        "attending_md": "Dr. Arindam Sen",
        "primary_nurse": "Nurse Deepak Joshi, RN",
        "current_shift": 8,
        "vitals": {
            "hr": "82 bpm",
            "bp": "122/76 mmHg (MAP 91)",
            "spo2": "95% on 2L NC",
            "rr": "18 /min",
            "temp": "37.0 °C",
            "k_plus": "4.0 mEq/L",
            "creatinine": "0.8 mg/dL",
            "fluid_balance": "-200 mL (24h)",
        },
        "stateless_trap_order": "Administer Enoxaparin (Lovenox) 40mg SC now at 08:00 IST for routine post-op DVT prophylaxis.",
        "stateless_ai_response": {
            "verdict": "APPROVED — STANDARD VTE PROPHYLAXIS",
            "reasoning": "Thoracic surgery patients are high risk for DVT/PE. Enoxaparin 40mg SC daily is standard prophylactic therapy on post-op Day 2.",
            "risk_missed": "Missed Anesthesia Pain Service note from Shift #7 (05:30 IST): Thoracic epidural catheter removal is scheduled for 11:00 IST today; giving Lovenox at 08:00 IST risks catastrophic spinal epidural hematoma.",
        },
        "hindsight_safe_protocol": {
            "verdict": "BLOCKED — SPINAL EPIDURAL HEMATOMA TIMING CONFLICT",
            "recalled_shift": "Shift #7 (2.5 hours ago • 05:30 IST Night Shift)",
            "recalled_author": "Dr. M. Iyer (Acute Pain & Regional Anesthesia)",
            "clinical_why": "Shift #7 handoff retained that T6–T7 thoracic epidural catheter removal is scheduled at 11:00 IST today. ASRA guidelines prohibit low-molecular-weight heparin within 12 hours BEFORE or 4 hours AFTER epidural catheter removal.",
            "safe_alternative": "HOLD Enoxaparin dose now. Keep sequential pneumatic compression devices (SCDs) active, remove epidural catheter at 11:00 IST, and reschedule Enoxaparin 40mg SC for 16:00 IST (5 hours post-removal).",
            "cost_saved_usd": 55000,
        },
    },
]


SEED_MEMORIES = [
    # Bed 04 longitudinal memories across Shift 1 -> Shift 5 -> Shift 20
    {
        "memory_id": "MEM-B04-S01",
        "patient_id": "ICU-BED-04",
        "shift_number": 1,
        "shift_label": "Shift #1 (Day 1 • 07:00 IST)",
        "author_name": "Dr. Arindam Sen, MD",
        "author_role": "doctor",
        "category": "Admission Baseline",
        "severity": "INFO",
        "content": "Patient admitted to Cardiac ICU post 3-vessel CABG (LIMA to LAD, SVG to OM1 & PDA). Baseline LVEF 42%, baseline Cr 1.3 mg/dL, Serum K+ 4.1 mEq/L. Extubated smoothly on arrival.",
        "tags": ["ICU-BED-04", "CABG", "Baseline", "Shift-1"],
        "created_at": "2026-11-04T07:30:00+05:30",
    },
    {
        "memory_id": "MEM-B04-S05",
        "patient_id": "ICU-BED-04",
        "shift_number": 5,
        "shift_label": "Shift #5 (Day 2 • 23:40 IST Night Shift)",
        "author_name": "Sister Priya Nair, RN",
        "author_role": "nurse",
        "category": "Adverse Drug Reaction",
        "severity": "CRITICAL",
        "content": "CRITICAL ADVERSE EVENT: Administered IV Furosemide (Lasix) 60mg bolus for +1.2L positive balance. Within 90 minutes, urine output surged to 650mL, Serum K+ plummeted from 3.8 to 2.7 mEq/L, triggering 14-beat run of non-sustained Ventricular Tachycardia (NSVT at 182 bpm). Electrophysiology mandated: NEVER give bolus loop diuretics; use continuous low-dose Bumetanide infusion only when K+ >= 4.2 mEq/L.",
        "tags": ["ICU-BED-04", "Furosemide", "Lasix", "Arrhythmia", "Hypokalemia", "Contraindication", "Shift-5"],
        "created_at": "2026-11-05T23:40:00+05:30",
    },
    {
        "memory_id": "MEM-B04-S12",
        "patient_id": "ICU-BED-04",
        "shift_number": 12,
        "shift_label": "Shift #12 (Day 3 • 19:15 IST Evening Shift)",
        "author_name": "Dr. K. Kulkarni (Cardiology)",
        "author_role": "doctor",
        "category": "Protocol Adaptation",
        "severity": "WARNING",
        "content": "Myocardial irritability persists when Serum K+ drops below 4.0 mEq/L or Mg2+ < 2.2 mg/dL. Patient responded safely to continuous Bumetanide 0.5 mg/hr after central-line KCl pre-loading. Also note: patient develops severe nocturnal disorientation if blood draws occur between 02:00 and 04:00 IST.",
        "tags": ["ICU-BED-04", "Bumetanide", "Electrolytes", "Delirium-Prevention", "Shift-12"],
        "created_at": "2026-11-06T19:15:00+05:30",
    },
    {
        "memory_id": "MEM-B04-S20",
        "patient_id": "ICU-BED-04",
        "shift_number": 20,
        "shift_label": "Shift #20 (Day 4 • 06:15 IST Outgoing Night Handoff)",
        "author_name": "Sister Priya Nair, RN",
        "author_role": "nurse",
        "category": "Shift Handoff Directive",
        "severity": "WARNING",
        "content": "Outgoing Night Shift #20 Note: Patient accumulated +1,450 mL net positive fluid overnight with mild bibasilar crackles (SpO2 93% on 4L NC). Morning K+ returned borderline low at 3.4 mEq/L. 40 mEq IV KCl rider started via central line; repeat K+ due at 09:00 IST. Remind incoming day resident NOT to order IV Lasix bolus despite congestion.",
        "tags": ["ICU-BED-04", "Handoff", "Potassium", "Fluid-Overload", "Shift-20"],
        "created_at": "2026-11-07T06:15:00+05:30",
    },
    # Bed 07 memories
    {
        "memory_id": "MEM-B07-S01",
        "patient_id": "ICU-BED-07",
        "shift_number": 1,
        "shift_label": "Shift #1 (Day 1 • Admission)",
        "author_name": "Dr. Arindam Sen, MD",
        "author_role": "doctor",
        "category": "Admission Baseline",
        "severity": "INFO",
        "content": "34F admitted with obstructive urosepsis and hypotension. EHR allergy header recorded as 'No Known Drug Allergies' per family at triage.",
        "tags": ["ICU-BED-07", "Sepsis", "Baseline", "Shift-1"],
        "created_at": "2026-11-05T08:00:00+05:30",
    },
    {
        "memory_id": "MEM-B07-S04",
        "patient_id": "ICU-BED-07",
        "shift_number": 4,
        "shift_label": "Shift #4 (Day 2 • 02:15 IST Night Shift)",
        "author_name": "Sister Priya Nair, RN",
        "author_role": "nurse",
        "category": "Adverse Drug Reaction",
        "severity": "CRITICAL",
        "content": "SEVERE HYPERSENSITIVITY: 18 minutes into second dose of IV Piperacillin-Tazobactam (Zosyn), patient developed acute stridor, wheezing, periorbital angioedema, and SpO2 drop to 86%. Infusion stopped immediately; treated with IM Epinephrine 0.3mg + IV Hydrocortisone. Infectious Disease switched regimen to Aztreonam + Vancomycin. Avoid all penicillins/cephalosporins.",
        "tags": ["ICU-BED-07", "Zosyn", "Piperacillin-Tazobactam", "Anaphylaxis", "Allergy", "Shift-4"],
        "created_at": "2026-11-06T02:15:00+05:30",
    },
    # Bed 11 memories
    {
        "memory_id": "MEM-B11-S06",
        "patient_id": "ICU-BED-11",
        "shift_number": 6,
        "shift_label": "Shift #6 (Day 2 • 14:20 IST)",
        "author_name": "Dr. S. Kapoor (Stroke Neurology)",
        "author_role": "doctor",
        "category": "Hemodynamic Shift",
        "severity": "CRITICAL",
        "content": "PERMISSIVE HYPERTENSION MANDATE: Trial reduction of SBP from 168 to 134 mmHg with IV Labetalol caused immediate left hemiparesis drift and aphasia within 15 minutes (NIHSS worsened from 4 to 11). Symptoms resolved after Norepinephrine push restored MAP > 108 mmHg. DO NOT administer antihypertensives unless SBP > 185 mmHg.",
        "tags": ["ICU-BED-11", "Stroke", "Labetalol", "Permissive-Hypertension", "Shift-6"],
        "created_at": "2026-11-06T14:20:00+05:30",
    },
    # Bed 15 memories
    {
        "memory_id": "MEM-B15-S07",
        "patient_id": "ICU-BED-15",
        "shift_number": 7,
        "shift_label": "Shift #7 (Day 2 • 05:30 IST Night Shift)",
        "author_name": "Sister Priya Nair, RN",
        "author_role": "nurse",
        "category": "Line/Tube Update",
        "severity": "CRITICAL",
        "content": "EPIDURAL HOLD NOTICE: Acute Pain Service scheduled T6-T7 thoracic epidural catheter removal for 11:00 IST today. Hold morning 08:00 IST Enoxaparin (Lovenox) 40mg SC dose to prevent spinal epidural hematoma. Reschedule Lovenox for 16:00 IST (5 hours post-catheter pull).",
        "tags": ["ICU-BED-15", "Enoxaparin", "Lovenox", "Epidural", "Anticoagulation-Hold", "Shift-7"],
        "created_at": "2026-11-07T05:30:00+05:30",
    },
]


SEED_TASKS = [
    {
        "task_id": "TSK-101",
        "patient_id": "ICU-BED-04",
        "shift_origin": "Shift #20 (Night Nurse Priya Nair)",
        "title": "Recheck Serum Potassium (K+) stat at 09:00 IST post 40 mEq KCl central-line infusion",
        "priority": "CRITICAL",
        "status": "PENDING",
        "clinical_reason": "Must confirm K+ >= 4.2 mEq/L before starting continuous Bumetanide infusion (Shift #5 VTach history).",
    },
    {
        "task_id": "TSK-102",
        "patient_id": "ICU-BED-07",
        "shift_origin": "Shift #11 (Evening Nurse R. Thomas)",
        "title": "Verify EHR Allergy Banner updated with Piperacillin-Tazobactam anaphylaxis & check Vancomycin trough at 10:00 IST",
        "priority": "HIGH",
        "status": "PENDING",
        "clinical_reason": "Prevent accidental beta-lactam re-order during fever spikes.",
    },
    {
        "task_id": "TSK-103",
        "patient_id": "ICU-BED-11",
        "shift_origin": "Shift #15 (Night Nurse Priya Nair)",
        "title": "Perform hourly NIHSS neuro checks; alert Attending immediately if MAP drops below 105 mmHg",
        "priority": "HIGH",
        "status": "PENDING",
        "clinical_reason": "Collateral penumbra perfusion dependent on SBP 155–180 mmHg.",
    },
    {
        "task_id": "TSK-104",
        "patient_id": "ICU-BED-15",
        "shift_origin": "Shift #7 (Anesthesia Pain Service)",
        "title": "HOLD 08:00 IST Enoxaparin 40mg SC; assist Anesthesia with Thoracic Epidural removal at 11:00 IST",
        "priority": "CRITICAL",
        "status": "PENDING",
        "clinical_reason": "ASRA spinal hematoma prevention protocol.",
    },
]


def init_db() -> None:
    """Initialize SQLite tables and populate realistic ICU clinical data if empty."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            badge_id TEXT NOT NULL,
            department TEXT NOT NULL,
            title TEXT NOT NULL,
            default_shift TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            bed_number TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            mrn TEXT NOT NULL,
            admission_diagnosis TEXT NOT NULL,
            illness_severity TEXT NOT NULL,
            status_badge TEXT NOT NULL,
            attending_md TEXT NOT NULL,
            primary_nurse TEXT NOT NULL,
            current_shift INTEGER NOT NULL,
            vitals_json TEXT NOT NULL,
            stateless_trap_order TEXT NOT NULL,
            stateless_ai_json TEXT NOT NULL,
            hindsight_safe_json TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            memory_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            shift_number INTEGER NOT NULL,
            shift_label TEXT NOT NULL,
            author_name TEXT NOT NULL,
            author_role TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            content TEXT NOT NULL,
            tags_json TEXT NOT NULL,
            cloud_synced INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS shift_tasks (
            task_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            shift_origin TEXT NOT NULL,
            title TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            clinical_reason TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS telemetry_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            bank_id TEXT NOT NULL,
            patient_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            summary TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
        """
    )

    # Seed users
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    if cur.fetchone()["cnt"] == 0:
        now_iso = datetime.now().isoformat()
        for u in SEED_USERS:
            cur.execute(
                """
                INSERT INTO users (email, password_hash, full_name, role, badge_id, department, title, default_shift, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    u["email"],
                    hash_password(u["password"]),
                    u["full_name"],
                    u["role"],
                    u["badge_id"],
                    u["department"],
                    u["title"],
                    u["default_shift"],
                    now_iso,
                ),
            )

    # Seed patients
    cur.execute("SELECT COUNT(*) as cnt FROM patients")
    if cur.fetchone()["cnt"] == 0:
        for p in SEED_PATIENTS:
            cur.execute(
                """
                INSERT INTO patients (
                    patient_id, bed_number, name, age, gender, mrn,
                    admission_diagnosis, illness_severity, status_badge,
                    attending_md, primary_nurse, current_shift,
                    vitals_json, stateless_trap_order, stateless_ai_json, hindsight_safe_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    p["patient_id"],
                    p["bed_number"],
                    p["name"],
                    p["age"],
                    p["gender"],
                    p["mrn"],
                    p["admission_diagnosis"],
                    p["illness_severity"],
                    p["status_badge"],
                    p["attending_md"],
                    p["primary_nurse"],
                    p["current_shift"],
                    json.dumps(p["vitals"]),
                    p["stateless_trap_order"],
                    json.dumps(p["stateless_ai_response"]),
                    json.dumps(p["hindsight_safe_protocol"]),
                ),
            )

    # Seed longitudinal memories
    cur.execute("SELECT COUNT(*) as cnt FROM memories")
    if cur.fetchone()["cnt"] == 0:
        for m in SEED_MEMORIES:
            cur.execute(
                """
                INSERT INTO memories (
                    memory_id, patient_id, shift_number, shift_label,
                    author_name, author_role, category, severity,
                    content, tags_json, cloud_synced, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    m["memory_id"],
                    m["patient_id"],
                    m["shift_number"],
                    m["shift_label"],
                    m["author_name"],
                    m["author_role"],
                    m["category"],
                    m["severity"],
                    m["content"],
                    json.dumps(m["tags"]),
                    0,
                    m["created_at"],
                ),
            )

    # Seed tasks
    cur.execute("SELECT COUNT(*) as cnt FROM shift_tasks")
    if cur.fetchone()["cnt"] == 0:
        for t in SEED_TASKS:
            cur.execute(
                """
                INSERT INTO shift_tasks (
                    task_id, patient_id, shift_origin, title, priority, status, clinical_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    t["task_id"],
                    t["patient_id"],
                    t["shift_origin"],
                    t["title"],
                    t["priority"],
                    t["status"],
                    t["clinical_reason"],
                ),
            )

    conn.commit()
    conn.close()


def get_all_patients() -> list[dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM patients ORDER BY patient_id ASC").fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["vitals"] = json.loads(d.pop("vitals_json"))
        d["stateless_ai_response"] = json.loads(d.pop("stateless_ai_json"))
        d["hindsight_safe_protocol"] = json.loads(d.pop("hindsight_safe_json"))
        result.append(d)
    return result


def get_patient_by_id(patient_id: str) -> dict[str, Any] | None:
    for p in get_all_patients():
        if p["patient_id"] == patient_id:
            return p
    return None


def create_new_patient(
    name: str,
    age: int,
    gender: str,
    bed_number: str,
    admission_diagnosis: str,
    attending_md: str,
    primary_nurse: str,
    current_shift: int = 1,
    hr: str = "86 bpm",
    bp: str = "124/78 mmHg",
    k_plus: str = "4.1 mEq/L",
    known_risk_note: str = "",
) -> dict[str, Any]:
    """Hospital Admin action: Admit a new patient into an ICU bed and initialize history."""
    import re
    import uuid

    conn = get_connection()
    # Extract bed digits if present, else generate unique bed number
    digits = re.findall(r"\d+", bed_number)
    bed_num_str = digits[0].zfill(2) if digits else str(uuid.uuid4().int)[:2]
    patient_id = f"ICU-BED-{bed_num_str}"

    existing = conn.execute(
        "SELECT patient_id FROM patients WHERE patient_id = ?", (patient_id,)
    ).fetchone()
    if existing:
        patient_id = f"ICU-BED-{bed_num_str}-{uuid.uuid4().hex[:2].upper()}"

    mrn = f"MRN-{str(uuid.uuid4().int)[:6]}"
    risk_summary = (
        known_risk_note.strip()
        if known_risk_note.strip()
        else "Monitor hemodynamic stability and renal potassium balance across shifts."
    )

    vitals = {
        "hr": hr if "bpm" in hr.lower() else f"{hr} bpm",
        "bp": bp if "mmhg" in bp.lower() else f"{bp} mmHg",
        "spo2": "97% on 2L NC",
        "rr": "18 /min",
        "temp": "37.0 °C",
        "k_plus": k_plus if "meq" in k_plus.lower() else f"{k_plus} mEq/L",
        "creatinine": "1.1 mg/dL",
        "fluid_balance": "+250 mL (24h)",
    }
    stateless_trap_order = "Administer IV Furosemide (Lasix) 80mg stat bolus"
    stateless_ai_response = {
        "verdict": "APPROVED — STANDARD PROTOCOL",
        "reasoning": f"Standard protocol for {admission_diagnosis}.",
        "risk_missed": f"Missed admission safety alert: {risk_summary}",
    }
    hindsight_safe_protocol = {
        "verdict": "BLOCKED — PAST SHIFT SAFETY CONTRAINDICATION",
        "recalled_shift": f"Shift #{current_shift} (Admission Baseline)",
        "recalled_author": attending_md,
        "clinical_why": risk_summary,
        "safe_alternative": "Follow patient-specific safe titration protocol and verify labs before bolus dosing.",
        "cost_saved_usd": 35000,
    }

    conn.execute(
        """
        INSERT INTO patients (
            patient_id, bed_number, name, age, gender, mrn,
            admission_diagnosis, illness_severity, status_badge,
            attending_md, primary_nurse, current_shift,
            vitals_json, stateless_trap_order, stateless_ai_json, hindsight_safe_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_id,
            bed_number.strip(),
            name.strip(),
            int(age),
            gender.strip().upper()[:1] or "M",
            mrn,
            admission_diagnosis.strip(),
            "WATCHER",
            "ACTIVE SHIFT MONITORING",
            attending_md.strip(),
            primary_nurse.strip(),
            int(current_shift),
            json.dumps(vitals),
            stateless_trap_order,
            json.dumps(stateless_ai_response),
            json.dumps(hindsight_safe_protocol),
        ),
    )

    # Insert initial baseline task for the assigned nurse
    task_id = f"TSK-{uuid.uuid4().hex[:4].upper()}"
    conn.execute(
        """
        INSERT INTO shift_tasks (
            task_id, patient_id, shift_origin, title, priority, status, clinical_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_id,
            patient_id,
            f"Shift #{current_shift} • Admitted by {attending_md}",
            f"Complete admission vitals check & verify medication chart for {name.strip()}",
            "HIGH",
            "PENDING",
            risk_summary,
        ),
    )
    conn.commit()
    conn.close()
    return get_patient_by_id(patient_id)  # type: ignore[return-value]


def update_patient_assignment(
    patient_id: str,
    attending_md: str,
    primary_nurse: str,
    current_shift: int | None = None,
) -> dict[str, Any] | None:
    """Hospital Admin action: Assign right Doctor and Nurse to the right Patient."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM patients WHERE patient_id = ?", (patient_id,)
    ).fetchone()
    if not row:
        conn.close()
        return None
    shift_val = current_shift if current_shift is not None else row["current_shift"]
    conn.execute(
        """
        UPDATE patients
        SET attending_md = ?, primary_nurse = ?, current_shift = ?
        WHERE patient_id = ?
        """,
        (attending_md.strip(), primary_nurse.strip(), int(shift_val), patient_id),
    )
    conn.commit()
    conn.close()
    return get_patient_by_id(patient_id)


def create_medicine_order(
    patient_id: str,
    title: str,
    doctor_name: str,
    nurse_name: str,
    shift_number: int,
    clinical_reason: str = "Prescribed after reviewing patient history",
    priority: str = "HIGH",
) -> dict[str, Any]:
    """Doctor action: Prescribe medicine and assign it to the Nurse's administration queue."""
    import uuid

    task_id = f"MED-{uuid.uuid4().hex[:5].upper()}"
    shift_origin = f"Shift #{shift_number} • Prescribed by {doctor_name} for {nurse_name}"
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO shift_tasks (
            task_id, patient_id, shift_origin, title, priority, status, clinical_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_id,
            patient_id,
            shift_origin,
            title.strip(),
            priority,
            "PENDING",
            clinical_reason.strip(),
        ),
    )
    conn.commit()
    conn.close()
    return {
        "task_id": task_id,
        "patient_id": patient_id,
        "shift_origin": shift_origin,
        "title": title.strip(),
        "priority": priority,
        "status": "PENDING",
        "clinical_reason": clinical_reason.strip(),
    }


def get_patient_memories(
    patient_id: str | None = None, max_shift: int | None = None
) -> list[dict[str, Any]]:
    conn = get_connection()
    query = "SELECT * FROM memories WHERE 1=1"
    params: list[Any] = []
    if patient_id:
        query += " AND patient_id = ?"
        params.append(patient_id)
    if max_shift is not None:
        query += " AND shift_number <= ?"
        params.append(max_shift)
    query += " ORDER BY shift_number DESC, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d.pop("tags_json"))
        result.append(d)
    return result


def get_shift_tasks(patient_id: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection()
    if patient_id:
        rows = conn.execute(
            "SELECT * FROM shift_tasks WHERE patient_id = ? ORDER BY task_id ASC",
            (patient_id,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM shift_tasks ORDER BY task_id ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_shift_task(task_id: str) -> dict[str, Any] | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM shift_tasks WHERE task_id = ?", (task_id,)
    ).fetchone()
    if not row:
        conn.close()
        return None
    new_status = "COMPLETED" if row["status"] == "PENDING" else "PENDING"
    conn.execute(
        "UPDATE shift_tasks SET status = ? WHERE task_id = ?", (new_status, task_id)
    )
    conn.commit()
    updated = conn.execute(
        "SELECT * FROM shift_tasks WHERE task_id = ?", (task_id,)
    ).fetchone()
    conn.close()
    return dict(updated)


def record_telemetry(
    operation: str,
    bank_id: str,
    patient_id: str,
    mode: str,
    latency_ms: float,
    summary: str,
    payload: dict[str, Any],
) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO telemetry_logs (timestamp, operation, bank_id, patient_id, mode, latency_ms, summary, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%H:%M:%S.%f")[:-3],
            operation,
            bank_id,
            patient_id,
            mode,
            round(latency_ms, 2),
            summary,
            json.dumps(payload),
        ),
    )
    conn.commit()
    conn.close()


def get_recent_telemetry(limit: int = 25) -> list[dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM telemetry_logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["payload"] = json.loads(d.pop("payload_json"))
        out.append(d)
    return out
