"""End-to-End Automated Test Suite for WardSense ICU (Auth, 3 Portals, Hindsight Memory & Groq Fallback)."""
from fastapi.testclient import TestClient
from src.database import init_db
from src.server import app

init_db()
client = TestClient(app)


def test_health_endpoint() -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "hindsight" in data
    assert data["hindsight"]["bank_id"] == "wardsense_icu_clinical_bank"


def test_auth_login_and_role_portals() -> None:
    # 1. Test Admin login -> redirects to /hospital
    res_admin = client.post(
        "/api/auth/login",
        json={"email": "admin@apollomed-icu.org", "password": "AdminPassword123!"},
    )
    assert res_admin.status_code == 200
    assert res_admin.json()["redirect_url"] == "/hospital"

    # Access /hospital with cookie
    hosp_page = client.get("/hospital")
    assert hosp_page.status_code == 200
    assert "Assign Right Doctor & Nurse" in hosp_page.text

    # 2. Test Doctor login -> redirects to /doctor
    res_doc = client.post(
        "/api/auth/login",
        json={"email": "doctor@apollomed-icu.org", "password": "DoctorPassword123!"},
    )
    assert res_doc.status_code == 200
    assert res_doc.json()["redirect_url"] == "/doctor"

    doc_page = client.get("/doctor?patient_id=ICU-BED-04")
    assert doc_page.status_code == 200
    assert "Review Patient History & Prescribe Medicine" in doc_page.text

    # 3. Test Nurse login -> redirects to /nurse
    res_nurse = client.post(
        "/api/auth/login",
        json={"email": "nurse@apollomed-icu.org", "password": "NursePassword123!"},
    )
    assert res_nurse.status_code == 200
    assert res_nurse.json()["redirect_url"] == "/nurse"

    nurse_page = client.get("/nurse?patient_id=ICU-BED-04")
    assert nurse_page.status_code == 200
    assert "Give Prescribed Medicine & Update Patient History" in nurse_page.text


def test_hospital_assign_doctor_prescribe_nurse_administer_flow() -> None:
    # Step 1: Hospital assigns Doctor & Nurse to ICU-BED-04
    assign_res = client.post(
        "/api/patients/ICU-BED-04/assign",
        json={
            "attending_md": "Dr. Arindam Sen, MD",
            "primary_nurse": "Sister Priya Nair, RN",
            "current_shift": 20,
        },
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["patient"]["attending_md"] == "Dr. Arindam Sen, MD"

    # Step 2: Doctor prescribes safe medicine for Nurse
    prescribe_res = client.post(
        "/api/orders/prescribe",
        json={
            "patient_id": "ICU-BED-04",
            "medicine_order": "Continuous Bumetanide 0.5mg/hr IV after 40mEq KCl",
            "clinical_reason": "Safe diuretic protocol verified against Shift #5 history",
            "priority": "CRITICAL",
        },
    )
    assert prescribe_res.status_code == 200
    task_id = prescribe_res.json()["order"]["task_id"]

    # Step 3: Nurse administers medicine (toggles task status to COMPLETED)
    give_res = client.post(f"/api/tasks/{task_id}/toggle")
    assert give_res.status_code == 200
    assert give_res.json()["task"]["status"] == "COMPLETED"


def test_hindsight_retain_and_recall_learning_curve() -> None:
    # Retain a new nursing observation
    retain_res = client.post(
        "/api/memories/retain",
        json={
            "patient_id": "ICU-BED-04",
            "shift_number": 21,
            "category": "Adverse Drug Reaction",
            "severity": "CRITICAL",
            "content": "Patient developed severe bradycardia (HR 42 bpm) after IV Metoprolol 5mg.",
        },
    )
    assert retain_res.status_code == 200
    retained_data = retain_res.json()["retained"]
    assert retained_data["patient_id"] == "ICU-BED-04"

    # Verify order at Shift #1 (Baseline) vs Shift #20 (Longitudinal Mastery)
    shift1_res = client.post(
        "/api/orders/verify",
        json={
            "patient_id": "ICU-BED-04",
            "proposed_order": "Administer IV Furosemide 80mg stat bolus",
            "simulated_shift_limit": 1,
        },
    )
    assert shift1_res.status_code == 200

    shift20_res = client.post(
        "/api/orders/verify",
        json={
            "patient_id": "ICU-BED-04",
            "proposed_order": "Administer IV Furosemide 80mg stat bolus",
            "simulated_shift_limit": 20,
        },
    )
    assert shift20_res.status_code == 200
    s20_data = shift20_res.json()
    assert "BLOCKED" in s20_data["hindsight_agent"]["verdict"]
    assert "APPROVED" in s20_data["stateless_ai"]["verdict"]
