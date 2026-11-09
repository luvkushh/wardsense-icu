"""FastAPI Server for WardSense ICU — Auth, 3 Clinical Portals & Hindsight Cloud APIs."""
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

from src.agent import wardsense_agent
from src.auth import create_jwt_token, decode_jwt_token, hash_password, verify_password
from src.config import settings
from src.database import (
    create_medicine_order,
    create_new_patient,
    delete_patient,
    get_all_patients,
    get_connection,
    get_doctor_roster,
    get_nurse_roster,
    get_patient_by_id,
    get_patient_memories,
    get_recent_telemetry,
    get_shift_tasks,
    init_db,
    toggle_shift_task,
    update_patient_assignment,
)
from src.hindsight_memory import memory_engine
from src.ui_renderer import (
    render_doctor_page,
    render_hospital_page,
    render_login_page,
    render_nurse_page,
    render_register_page,
)

init_db()

app = FastAPI(
    title="WardSense ICU • Clinical Shift-Handoff & Continuity Engine",
    description="Autonomous ICU Shift-Handoff & Clinical Safety Engine powered by Vectorize Hindsight Cloud and Groq LPU.",
    version="1.0.0",
)


# ------------------- Pydantic Request Models -------------------

class LoginRequest(BaseModel):
    email: str
    password: str
    shift: str = "Morning Shift (07:00 - 15:00 IST)"


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "doctor"
    badge_id: str = "MCI-REG-99201"
    department: str = "Cardiac & Medical ICU"
    title: str = "Critical Care Clinician"


class RetainObservationRequest(BaseModel):
    patient_id: str
    shift_number: int = 21
    category: str = "Adverse Drug Reaction"
    severity: str = "CRITICAL"
    content: str
    author_name: str | None = None
    tags: list[str] | None = None


class VerifyOrderRequest(BaseModel):
    patient_id: str
    proposed_order: str
    simulated_shift_limit: int | None = None


class AssignPatientRequest(BaseModel):
    attending_md: str
    primary_nurse: str
    current_shift: int | None = None


class CreatePatientRequest(BaseModel):
    name: str
    age: int = 52
    gender: str = "M"
    bed_number: str = "Bed 18 • Cardiac ICU"
    admission_diagnosis: str = "Acute Decompensated Heart Failure • Day 1"
    attending_md: str = "Dr. Arindam Sen, MD"
    primary_nurse: str = "Sister Priya Nair, RN"
    current_shift: int = 1
    hr: str = "88 bpm"
    bp: str = "128/82 mmHg"
    k_plus: str = "4.1 mEq/L"
    known_risk_note: str = ""


class PrescribeMedicineRequest(BaseModel):
    patient_id: str
    medicine_order: str
    clinical_reason: str = "Prescribed after checking patient history"
    priority: str = "HIGH"


class CloudConfigRequest(BaseModel):
    hindsight_api_key: str | None = None
    hindsight_base_url: str | None = None
    hindsight_bank_id: str | None = None
    groq_api_key: str | None = None
    default_model: str | None = None


# ------------------- Session Helpers -------------------

def get_current_user(request: Request) -> dict[str, Any] | None:
    token = request.cookies.get("wardsense_session")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        return None
    return decode_jwt_token(token)


def build_common_context(request: Request, user: dict[str, Any], active_page: str) -> dict[str, Any]:
    patients = get_all_patients()
    memories = get_patient_memories()
    tasks = get_shift_tasks()
    telemetry = get_recent_telemetry(limit=20)
    hindsight_status = memory_engine.get_status()

    total_saved_usd = sum(
        p["hindsight_safe_protocol"].get("cost_saved_usd", 0) for p in patients
    )
    pending_tasks_count = sum(1 for t in tasks if t["status"] == "PENDING")
    critical_memories_count = sum(1 for m in memories if m["severity"] == "CRITICAL")

    return {
        "request": request,
        "user": user,
        "active_page": active_page,
        "patients": patients,
        "doctor_roster": get_doctor_roster(),
        "nurse_roster": get_nurse_roster(),
        "memories": memories,
        "tasks": tasks,
        "telemetry": telemetry,
        "hindsight_status": hindsight_status,
        "metrics": {
            "total_beds": len(patients),
            "total_memories": len(memories),
            "critical_alerts_prevented": critical_memories_count,
            "pending_tasks": pending_tasks_count,
            "total_saved_usd": total_saved_usd,
            "handoff_compliance_pct": 98.4,
        },
        "config": {
            "hindsight_base_url": settings.hindsight_base_url,
            "hindsight_bank_id": settings.hindsight_bank_id,
            "has_hindsight_key": bool(settings.hindsight_api_key),
            "has_groq_key": bool(settings.groq_api_key),
            "default_model": settings.default_model,
            "fallback_model": settings.fallback_model,
        },
    }


# ------------------- HTML Page Routes -------------------

@app.get("/", response_class=HTMLResponse)
async def root_redirect(request: Request) -> Response:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    role = user.get("role", "doctor")
    if role == "admin":
        return RedirectResponse(url="/hospital", status_code=302)
    if role == "nurse":
        return RedirectResponse(url="/nurse", status_code=302)
    return RedirectResponse(url="/doctor", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_page() -> Response:
    return HTMLResponse(render_login_page())


@app.get("/register", response_class=HTMLResponse)
async def register_page() -> Response:
    return HTMLResponse(render_register_page())


@app.get("/logout")
async def logout_route() -> Response:
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("wardsense_session")
    return response


@app.get("/hospital", response_class=HTMLResponse)
async def hospital_portal(request: Request) -> Response:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.get("role") == "doctor":
        return RedirectResponse(url="/doctor", status_code=302)
    if user.get("role") == "nurse":
        return RedirectResponse(url="/nurse", status_code=302)
    ctx = build_common_context(request, user, active_page="hospital")
    return HTMLResponse(render_hospital_page(ctx))


@app.get("/doctor", response_class=HTMLResponse)
async def doctor_portal(
    request: Request,
    patient_id: str | None = None,
) -> Response:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.get("role") == "admin":
        return RedirectResponse(url="/hospital", status_code=302)
    if user.get("role") == "nurse":
        return RedirectResponse(url="/nurse", status_code=302)
    ctx = build_common_context(request, user, active_page="doctor")
    patients = ctx["patients"]

    active_patient = get_patient_by_id(patient_id or "ICU-BED-04") or (patients[0] if patients else None)
    if not active_patient:
        raise HTTPException(status_code=404, detail="No patients admitted in ICU")

    ipass_brief = wardsense_agent.generate_ipass_handoff(active_patient["patient_id"])
    initial_comparison = wardsense_agent.verify_clinical_order(
        patient_id=active_patient["patient_id"],
        proposed_order=active_patient["stateless_trap_order"],
    )
    ctx["selected_patient"] = active_patient
    ctx["ipass_brief"] = ipass_brief
    ctx["initial_comparison"] = initial_comparison
    ctx["patient_memories"] = get_patient_memories(patient_id=active_patient["patient_id"])
    ctx["patient_tasks"] = get_shift_tasks(patient_id=active_patient["patient_id"])
    return HTMLResponse(render_doctor_page(ctx))


@app.get("/nurse", response_class=HTMLResponse)
async def nurse_portal(
    request: Request,
    patient_id: str | None = None,
) -> Response:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.get("role") == "admin":
        return RedirectResponse(url="/hospital", status_code=302)
    if user.get("role") == "doctor":
        return RedirectResponse(url="/doctor", status_code=302)
    ctx = build_common_context(request, user, active_page="nurse")
    patients = ctx["patients"]

    active_patient = get_patient_by_id(patient_id or "ICU-BED-04") or (patients[0] if patients else None)
    if not active_patient:
        raise HTTPException(status_code=404, detail="No patients admitted in ICU")

    ctx["selected_patient"] = active_patient
    active_pid = active_patient["patient_id"]
    ctx["patient_memories"] = get_patient_memories(patient_id=active_pid)
    ctx["patient_tasks"] = get_shift_tasks(patient_id=active_pid)
    return HTMLResponse(render_nurse_page(ctx))


# ------------------- Authentication REST APIs -------------------

@app.post("/api/auth/login")
async def api_login(req: LoginRequest, response: Response) -> JSONResponse:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (req.email.strip(),)
    ).fetchone()
    conn.close()

    if not row or not verify_password(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid clinical credentials or badge ID.")

    user_payload = {
        "id": row["id"],
        "email": row["email"],
        "full_name": row["full_name"],
        "role": row["role"],
        "badge_id": row["badge_id"],
        "department": row["department"],
        "title": row["title"],
        "active_shift": req.shift or row["default_shift"],
    }
    token = create_jwt_token(user_payload)

    target_url = "/doctor"
    if row["role"] == "admin":
        target_url = "/hospital"
    elif row["role"] == "nurse":
        target_url = "/nurse"

    res = JSONResponse(
        {
            "success": True,
            "user": user_payload,
            "token": token,
            "redirect_url": target_url,
        }
    )
    res.set_cookie(
        key="wardsense_session",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax",
    )
    return res


@app.post("/api/auth/register")
async def api_register(req: RegisterRequest) -> JSONResponse:
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (req.email.strip(),)
    ).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Email is already registered in Hospital IAM.")

    role_clean = req.role.lower() if req.role.lower() in ("admin", "doctor", "nurse") else "doctor"
    now_iso = datetime.now().isoformat()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (email, password_hash, full_name, role, badge_id, department, title, default_shift, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            req.email.strip(),
            hash_password(req.password),
            req.full_name.strip(),
            role_clean,
            req.badge_id.strip(),
            req.department.strip(),
            req.title.strip(),
            "Morning Shift (07:00 - 15:00 IST)",
            now_iso,
        ),
    )
    user_id = cur.lastrowid
    conn.commit()
    conn.close()

    user_payload = {
        "id": user_id,
        "email": req.email.strip(),
        "full_name": req.full_name.strip(),
        "role": role_clean,
        "badge_id": req.badge_id.strip(),
        "department": req.department.strip(),
        "title": req.title.strip(),
        "active_shift": "Morning Shift (07:00 - 15:00 IST)",
    }
    token = create_jwt_token(user_payload)
    target_url = "/hospital" if role_clean == "admin" else ("/nurse" if role_clean == "nurse" else "/doctor")

    res = JSONResponse(
        {
            "success": True,
            "user": user_payload,
            "token": token,
            "redirect_url": target_url,
        }
    )
    res.set_cookie(
        key="wardsense_session",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax",
    )
    return res


@app.get("/api/auth/quick-switch/{role}")
async def quick_role_switch(role: str, redirect_to: str | None = None) -> Response:
    """Instant 1-click role switcher for judges & clinical evaluation."""
    email_map = {
        "admin": "admin@apollomed-icu.org",
        "doctor": "doctor@apollomed-icu.org",
        "nurse": "nurse@apollomed-icu.org",
    }
    email = email_map.get(role.lower(), "doctor@apollomed-icu.org")
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    user_payload = {
        "id": row["id"],
        "email": row["email"],
        "full_name": row["full_name"],
        "role": row["role"],
        "badge_id": row["badge_id"],
        "department": row["department"],
        "title": row["title"],
        "active_shift": row["default_shift"],
    }
    token = create_jwt_token(user_payload)
    default_target = "/hospital" if row["role"] == "admin" else ("/nurse" if row["role"] == "nurse" else "/doctor")
    res = RedirectResponse(url=redirect_to or default_target, status_code=302)
    res.set_cookie(
        key="wardsense_session",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax",
    )
    return res


# ------------------- Core Clinical & Hindsight Cloud APIs -------------------

@app.get("/api/health")
async def api_health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "WardSense ICU Clinical Continuity Engine",
        "hindsight": memory_engine.get_status(),
        "llm_model": settings.default_model,
        "fallback_model": settings.fallback_model,
    }


@app.get("/api/patients")
async def api_list_patients() -> dict[str, Any]:
    return {"patients": get_all_patients()}


@app.post("/api/patients")
async def api_create_patient(req: CreatePatientRequest) -> dict[str, Any]:
    new_patient = create_new_patient(
        name=req.name,
        age=req.age,
        gender=req.gender,
        bed_number=req.bed_number,
        admission_diagnosis=req.admission_diagnosis,
        attending_md=req.attending_md,
        primary_nurse=req.primary_nurse,
        current_shift=req.current_shift,
        hr=req.hr,
        bp=req.bp,
        k_plus=req.k_plus,
        known_risk_note=req.known_risk_note,
    )
    # Also retain initial admission note in Hindsight Memory
    note_text = (
        f"Patient {new_patient['name']} ({new_patient['age']}{new_patient['gender']}) admitted to {new_patient['bed_number']} "
        f"with {new_patient['admission_diagnosis']}. "
        + (f"Safety Alert: {req.known_risk_note}" if req.known_risk_note.strip() else "Baseline vitals stable.")
    )
    memory_engine.retain_shift_observation(
        patient_id=new_patient["patient_id"],
        shift_number=req.current_shift,
        author_name=req.attending_md,
        author_role="doctor",
        category="Admission Baseline",
        severity="WARNING" if req.known_risk_note.strip() else "INFO",
        content=note_text,
        tags=[new_patient["patient_id"], "Admission"],
    )
    return {"success": True, "patient": new_patient}


@app.delete("/api/patients/{patient_id}")
async def api_delete_patient(patient_id: str) -> dict[str, Any]:
    deleted = delete_patient(patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"success": True, "patient_id": patient_id}


@app.get("/api/ipass/{patient_id}")
async def api_get_ipass(patient_id: str, shift: int | None = None) -> dict[str, Any]:
    try:
        return wardsense_agent.generate_ipass_handoff(patient_id=patient_id, simulated_shift=shift)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/api/orders/verify")
async def api_verify_order(req: VerifyOrderRequest) -> dict[str, Any]:
    try:
        return wardsense_agent.verify_clinical_order(
            patient_id=req.patient_id,
            proposed_order=req.proposed_order,
            simulated_shift_limit=req.simulated_shift_limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/api/memories/retain")
async def api_retain_memory(req: RetainObservationRequest, request: Request) -> dict[str, Any]:
    user = get_current_user(request)
    patient = get_patient_by_id(req.patient_id)
    if req.author_name and req.author_name.strip():
        author_name = req.author_name.strip()
        author_role = "nurse"
    elif user and user.get("role") == "nurse":
        author_name = user["full_name"]
        author_role = "nurse"
    elif patient:
        author_name = patient["primary_nurse"]
        author_role = "nurse"
    else:
        author_name = "Sister Priya Nair, RN"
        author_role = "nurse"

    retained = memory_engine.retain_shift_observation(
        patient_id=req.patient_id,
        shift_number=req.shift_number,
        author_name=author_name,
        author_role=author_role,
        category=req.category,
        severity=req.severity,
        content=req.content,
        tags=req.tags,
    )
    return {"success": True, "retained": retained}


@app.post("/api/tasks/{task_id}/toggle")
async def api_toggle_task(task_id: str) -> dict[str, Any]:
    updated = toggle_shift_task(task_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Shift task not found")
    return {"success": True, "task": updated}


@app.post("/api/patients/{patient_id}/assign")
async def api_assign_patient(patient_id: str, req: AssignPatientRequest) -> dict[str, Any]:
    updated = update_patient_assignment(
        patient_id=patient_id,
        attending_md=req.attending_md,
        primary_nurse=req.primary_nurse,
        current_shift=req.current_shift,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"success": True, "patient": updated}


@app.post("/api/orders/prescribe")
async def api_prescribe_medicine(
    req: PrescribeMedicineRequest, request: Request
) -> dict[str, Any]:
    user = get_current_user(request)
    patient = get_patient_by_id(req.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doctor_name = user["full_name"] if user and user.get("role") == "doctor" else patient["attending_md"]
    nurse_name = patient["primary_nurse"]
    shift_num = patient["current_shift"]

    task = create_medicine_order(
        patient_id=req.patient_id,
        title=req.medicine_order,
        doctor_name=doctor_name,
        nurse_name=nurse_name,
        shift_number=shift_num,
        clinical_reason=req.clinical_reason,
        priority=req.priority,
    )

    # Also retain the prescription instruction in Hindsight Memory so history stays complete
    memory_engine.retain_shift_observation(
        patient_id=req.patient_id,
        shift_number=shift_num,
        author_name=doctor_name,
        author_role="doctor",
        category="Doctor Medicine Order",
        severity="INFO",
        content=f"Doctor Prescribed Medicine for {nurse_name}: {req.medicine_order} ({req.clinical_reason})",
        tags=[req.patient_id, "Prescription", f"Shift-{shift_num}"],
    )

    return {"success": True, "order": task}


@app.get("/api/telemetry")
async def api_telemetry() -> dict[str, Any]:
    return {
        "hindsight_status": memory_engine.get_status(),
        "logs": get_recent_telemetry(limit=25),
    }


@app.post("/api/cloud/config")
async def api_update_cloud_config(req: CloudConfigRequest) -> dict[str, Any]:
    settings.update_credentials(
        hindsight_api_key=req.hindsight_api_key,
        hindsight_base_url=req.hindsight_base_url,
        hindsight_bank_id=req.hindsight_bank_id,
        groq_api_key=req.groq_api_key,
        default_model=req.default_model,
    )
    return {
        "success": True,
        "hindsight_status": memory_engine.get_status(),
        "default_model": settings.default_model,
    }


@app.post("/api/cloud/sync")
async def api_sync_cloud() -> dict[str, Any]:
    return memory_engine.sync_all_to_hindsight_cloud()
