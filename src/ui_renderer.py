"""Clean, Minimal Daylight Hospital UI Renderer for WardSense Health.

Workflow:
1. Hospital (/hospital) : Assign the right Doctor & Nurse to the right Patient.
2. Doctor (/doctor)     : Check Patient's Past History (Hindsight Recall) & Prescribe Medicine to Nurse.
3. Nurse (/nurse)       : Administer Doctor's Prescribed Medicine & Update Patient History (Hindsight Retain).
"""
import html
from pathlib import Path
from typing import Any
from src.config import BASE_DIR


def _esc(val: Any) -> str:
    return html.escape(str(val)) if val is not None else ""


def render_login_page() -> str:
    return (Path(BASE_DIR) / "templates" / "login.html").read_text(encoding="utf-8")


def render_register_page() -> str:
    return (Path(BASE_DIR) / "templates" / "register.html").read_text(encoding="utf-8")


DOCTOR_OPTIONS = [
    "Dr. Arindam Sen, MD",
    "Dr. Kavita Verma, MD",
    "Dr. S. Kapoor, MD (Neuro)",
    "Dr. K. Kulkarni, MD (Cardio)",
]

NURSE_OPTIONS = [
    "Sister Priya Nair, RN",
    "Nurse R. Thomas, RN",
    "Nurse Anjali Menon, RN",
    "Nurse Deepak Joshi, RN",
]


def _render_shell(
    title: str,
    active_page: str,
    user: dict[str, Any],
    patients: list[dict[str, Any]],
    selected_patient_id: str,
    hindsight_status: dict[str, Any],
    config: dict[str, Any],
    body_html: str,
) -> str:
    nav_item = lambda page, step_num, label, sublabel: (
        f"""
        <a href="/{page}" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs transition {
            'bg-teal-50 text-teal-900 font-semibold border border-teal-200/80' if active_page == page else 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
        }">
          <span class="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 {
              'bg-teal-600 text-white' if active_page == page else 'bg-slate-100 text-slate-600'
          }">{step_num}</span>
          <div class="min-w-0">
            <div class="truncate text-sm">{label}</div>
            <div class="text-[11px] text-slate-400 font-normal truncate">{sublabel}</div>
          </div>
        </a>
        """
    )

    target_portal = "/nurse" if active_page == "nurse" else "/doctor"
    sidebar_beds = []
    for p in patients:
        is_sel = p["patient_id"] == selected_patient_id and active_page in ("doctor", "nurse")
        bed_cls = (
            "bg-slate-100 text-slate-900 font-semibold"
            if is_sel
            else "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
        )
        dot_cls = "bg-rose-500" if "CRITICAL" in p["illness_severity"] else "bg-amber-500"
        short_bed = p["patient_id"].replace("ICU-", "")
        sidebar_beds.append(
            f"""
            <a href="{target_portal}?patient_id={_esc(p['patient_id'])}"
               class="flex items-center justify-between px-3 py-2 rounded-xl text-xs transition {bed_cls}">
              <div class="flex items-center gap-2.5 truncate">
                <span class="w-2 h-2 rounded-full {dot_cls} shrink-0"></span>
                <span class="truncate">{_esc(p['name'])}</span>
              </div>
              <span class="font-mono-num text-[11px] text-slate-400 shrink-0">{_esc(short_bed)}</span>
            </a>
            """
        )

    default_model = config.get("default_model", "openai/gpt-oss-120b")
    sel_gpt = "selected" if default_model == "openai/gpt-oss-120b" else ""
    sel_qwen = "selected" if default_model == "qwen/qwen3-32b" else ""
    sel_llama = "selected" if default_model == "llama-3.3-70b-versatile" else ""

    initials = "".join([part[0] for part in user.get("full_name", "Dr").split()[:2]]).upper()

    # 3-Step Visual Workflow Bar at the top of every page
    step_cls = lambda page: (
        "bg-teal-600 text-white border-teal-600 shadow-xs"
        if active_page == page
        else "bg-white text-slate-600 border-slate-200 hover:border-teal-400"
    )
    pt_query = f"?patient_id={_esc(selected_patient_id)}" if selected_patient_id else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_esc(title)}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: #F8FAFC;
      color: #0F172A;
    }}
    .font-mono-num {{
      font-family: 'JetBrains Mono', monospace;
      font-variant-numeric: tabular-nums;
    }}
    .clean-card {{
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03);
    }}
  </style>
</head>
<body class="h-screen overflow-hidden flex bg-[#F8FAFC] text-slate-900 selection:bg-teal-600 selection:text-white">

  <!-- Left Sidebar (Locked on Viewport) -->
  <aside class="hidden lg:flex w-64 h-screen sticky top-0 flex-col justify-between border-r border-slate-200 bg-white shrink-0 overflow-y-auto select-none">
    <div class="p-5 space-y-6">
      <!-- Brand -->
      <a href="/" class="flex items-center gap-3 px-1">
        <div class="w-8 h-8 rounded-lg bg-teal-600 text-white flex items-center justify-center shadow-sm">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        </div>
        <span class="font-bold tracking-tight text-slate-900 text-base">WardSense Health</span>
      </a>

      <!-- 3 Role Portals -->
      <div>
        <div class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 mb-2">
          Hospital Workflow
        </div>
        <nav class="space-y-1.5">
          {nav_item("hospital", "1", "Hospital Admin", "Assign Doctor & Nurse")}
          {nav_item("doctor", "2", "Doctor Portal", "Check History & Prescribe")}
          {nav_item("nurse", "3", "Nurse Station", "Give Medicine & Log History")}
        </nav>
      </div>

      <!-- Patients List -->
      <div>
        <div class="flex items-center justify-between px-3 mb-2">
          <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Select Patient</span>
          <a href="/hospital?add_patient=1" class="text-[11px] font-semibold text-teal-700 hover:text-teal-800">+ Add</a>
        </div>
        <div class="space-y-1">
          {"".join(sidebar_beds)}
        </div>
      </div>
    </div>

    <!-- Bottom Profile & Settings -->
    <div class="p-4 border-t border-slate-100 space-y-3">
      <div class="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-200/70 text-xs">
        <span class="text-slate-600 font-medium">API & Cloud Settings</span>
        <button onclick="openCloudModal()" class="text-teal-700 hover:text-teal-800 font-semibold">
          Configure
        </button>
      </div>

      <div class="flex items-center justify-between px-1 pt-1">
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 flex items-center justify-center font-bold text-xs text-teal-800 shrink-0">
            {_esc(initials)}
          </div>
          <div class="min-w-0">
            <div class="text-xs font-semibold text-slate-900 truncate">{_esc(user.get("full_name"))}</div>
            <div class="text-[11px] text-slate-400 capitalize">{_esc(user.get("role"))}</div>
          </div>
        </div>
        <a href="/logout" class="text-xs text-slate-400 hover:text-rose-600 font-medium">
          Sign out
        </a>
      </div>
    </div>
  </aside>

  <!-- Main Content Area (Scrolls Independently while Left Sidebar stays Locked) -->
  <div class="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">

    <!-- Top 3-Step Hospital Workflow Bar -->
    <div class="sticky top-0 z-20 bg-white/95 backdrop-blur border-b border-slate-200 px-6 py-3 shrink-0">
      <div class="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2 text-xs">
          <a href="/hospital" class="px-3 py-1.5 rounded-lg border font-semibold transition {step_cls('hospital')}">
            1. Hospital: Assign Doctor & Nurse
          </a>
          <span class="text-slate-300">→</span>
          <a href="/doctor{pt_query}" class="px-3 py-1.5 rounded-lg border font-semibold transition {step_cls('doctor')}">
            2. Doctor: Check History & Prescribe Medicine
          </a>
          <span class="text-slate-300">→</span>
          <a href="/nurse{pt_query}" class="px-3 py-1.5 rounded-lg border font-semibold transition {step_cls('nurse')}">
            3. Nurse: Give Medicine & Update History
          </a>
        </div>
        <a href="/login" class="text-xs text-slate-400 hover:text-slate-700 font-medium">Switch Account</a>
      </div>
    </div>

    <main class="flex-1 max-w-6xl w-full mx-auto px-6 py-7">
      {body_html}
    </main>
  </div>

  <!-- Settings Modal -->
  <div id="cloud-modal" class="hidden fixed inset-0 z-50 bg-slate-900/30 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="clean-card rounded-2xl max-w-md w-full p-6 shadow-xl">
      <div class="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
        <h3 class="text-base font-bold text-slate-900">Hindsight Cloud & Groq Settings</h3>
        <button onclick="closeCloudModal()" class="text-slate-400 hover:text-slate-700 text-sm">✕</button>
      </div>

      <form id="cloud-config-form" class="space-y-3.5 text-xs">
        <div>
          <label class="block text-slate-700 font-semibold mb-1">Hindsight Cloud API Key</label>
          <input type="password" id="cfg_hindsight_key" placeholder="Paste API Key from ui.hindsight.vectorize.io"
            class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-mono-num" />
        </div>
        <div>
          <label class="block text-slate-700 font-semibold mb-1">Memory Bank ID</label>
          <input type="text" id="cfg_bank_id" value="{_esc(config.get('hindsight_bank_id'))}"
            class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-mono-num" />
          <input type="hidden" id="cfg_hindsight_url" value="{_esc(config.get('hindsight_base_url'))}" />
        </div>
        <div>
          <label class="block text-slate-700 font-semibold mb-1">Groq API Key</label>
          <input type="password" id="cfg_groq_key" placeholder="gsk_..."
            class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-mono-num" />
        </div>
        <div>
          <label class="block text-slate-700 font-semibold mb-1">LLM Model</label>
          <select id="cfg_model" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-mono-num">
            <option value="openai/gpt-oss-120b" {sel_gpt}>openai/gpt-oss-120b</option>
            <option value="qwen/qwen3-32b" {sel_qwen}>qwen/qwen3-32b</option>
            <option value="llama-3.3-70b-versatile" {sel_llama}>llama-3.3-70b-versatile</option>
          </select>
        </div>

        <div id="cloud-cfg-msg" class="hidden p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 font-medium"></div>

        <div class="flex items-center justify-between pt-3 border-t border-slate-100">
          <button type="button" onclick="syncAllToCloud()" class="text-teal-700 hover:underline font-semibold">
            ↑ Sync Local History to Cloud
          </button>
          <div class="flex items-center gap-2">
            <button type="button" onclick="closeCloudModal()" class="px-3.5 py-2 rounded-xl bg-slate-100 text-slate-600 font-medium">Cancel</button>
            <button type="submit" class="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold">Save</button>
          </div>
        </div>
      </form>
    </div>
  </div>

  <script>
    function openCloudModal() {{ document.getElementById('cloud-modal').classList.remove('hidden'); }}
    function closeCloudModal() {{ document.getElementById('cloud-modal').classList.add('hidden'); }}

    document.getElementById('cloud-config-form').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const msg = document.getElementById('cloud-cfg-msg');
      const res = await fetch('/api/cloud/config', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          hindsight_api_key: document.getElementById('cfg_hindsight_key').value || undefined,
          hindsight_base_url: document.getElementById('cfg_hindsight_url').value,
          hindsight_bank_id: document.getElementById('cfg_bank_id').value,
          groq_api_key: document.getElementById('cfg_groq_key').value || undefined,
          default_model: document.getElementById('cfg_model').value,
        }})
      }});
      if (res.ok) {{
        msg.textContent = 'Settings saved!';
        msg.classList.remove('hidden');
        setTimeout(() => window.location.reload(), 400);
      }}
    }});

    async function syncAllToCloud() {{
      const res = await fetch('/api/cloud/sync', {{ method: 'POST' }});
      const data = await res.json();
      alert(data.message);
      window.location.reload();
    }}
  </script>
</body>
</html>"""


# ==============================================================================
# PAGE 1: HOSPITAL PORTAL — Assign Right Doctor & Nurse to Right Patient
# ==============================================================================
def _shift_label_from_num(shift_num: int) -> str:
    if shift_num <= 2:
        return "Morning Shift"
    if shift_num in (5, 12):
        return "Evening Shift"
    return "Night Shift"


def render_hospital_page(ctx: dict[str, Any]) -> str:
    metrics = ctx["metrics"]
    patients = ctx["patients"]
    tasks = ctx["tasks"]

    bed_cards = []
    for p in patients:
        pid = p["patient_id"]
        v = p["vitals"]
        pending_for_patient = sum(
            1 for t in tasks if t["patient_id"] == pid and t["status"] == "PENDING"
        )

        # Build Doctor options with current doctor selected
        doc_opts = []
        current_doc = p["attending_md"]
        all_docs = list(DOCTOR_OPTIONS)
        if current_doc not in all_docs:
            all_docs.insert(0, current_doc)
        for d in all_docs:
            sel = "selected" if d == current_doc else ""
            doc_opts.append(f'<option value="{_esc(d)}" {sel}>{_esc(d)}</option>')

        # Build Nurse options with current nurse selected
        nurse_opts = []
        current_nurse = p["primary_nurse"]
        all_nurses = list(NURSE_OPTIONS)
        if current_nurse not in all_nurses:
            all_nurses.insert(0, current_nurse)
        for n in all_nurses:
            sel = "selected" if n == current_nurse else ""
            nurse_opts.append(f'<option value="{_esc(n)}" {sel}>{_esc(n)}</option>')

        shift_name = _shift_label_from_num(int(p["current_shift"]))
        sel_morning = "selected" if shift_name == "Morning Shift" else ""
        sel_evening = "selected" if shift_name == "Evening Shift" else ""
        sel_night = "selected" if shift_name == "Night Shift" else ""

        bed_cards.append(
            f"""
            <div class="clean-card rounded-2xl p-6 flex flex-col justify-between">
              <div>
                <!-- Patient Header -->
                <div class="flex items-start justify-between gap-2 mb-4">
                  <div>
                    <span class="text-xs font-semibold text-teal-700">{_esc(p['bed_number'])}</span>
                    <h3 class="text-lg font-bold text-slate-900 mt-0.5">{_esc(p['name'])} ({p['age']}{_esc(p['gender'])})</h3>
                    <p class="text-xs text-slate-500 mt-0.5">{_esc(p['admission_diagnosis'])}</p>
                  </div>
                  <span id="shift-badge-{_esc(pid)}" class="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 shrink-0">
                    {_esc(shift_name)}
                  </span>
                </div>

                <!-- Vitals Strip -->
                <div class="grid grid-cols-3 gap-2 mb-4 p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs">
                  <div>
                    <div class="text-[10px] text-slate-400">Heart Rate</div>
                    <div class="text-slate-800 font-semibold mt-0.5">{_esc(v['hr'].split(' ')[0])} bpm</div>
                  </div>
                  <div>
                    <div class="text-[10px] text-slate-400">Blood Pressure</div>
                    <div class="text-slate-800 font-semibold mt-0.5">{_esc(v['bp'].split(' ')[0])}</div>
                  </div>
                  <div>
                    <div class="text-[10px] text-slate-400">Pending Medicines</div>
                    <div class="text-teal-700 font-semibold mt-0.5">{pending_for_patient} for Nurse</div>
                  </div>
                </div>

                <!-- Hospital Staff Assignment Box -->
                <div class="p-4 rounded-xl bg-teal-50/40 border border-teal-100 space-y-3 text-xs">
                  <div class="flex items-center justify-between">
                    <span class="font-bold text-slate-800">Assign Doctor & Nurse for Shift</span>
                    <span id="assign-msg-{_esc(pid)}" class="hidden text-emerald-700 font-semibold">✓ Assigned!</span>
                  </div>

                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label class="block text-[11px] font-semibold text-slate-600 mb-1">Assigned Doctor</label>
                      <select id="doc-{_esc(pid)}" class="w-full px-3 py-2 rounded-lg bg-white border border-slate-200 text-slate-900 font-medium">
                        {"".join(doc_opts)}
                      </select>
                    </div>
                    <div>
                      <label class="block text-[11px] font-semibold text-slate-600 mb-1">Assigned Nurse</label>
                      <select id="nurse-{_esc(pid)}" class="w-full px-3 py-2 rounded-lg bg-white border border-slate-200 text-slate-900 font-medium">
                        {"".join(nurse_opts)}
                      </select>
                    </div>
                  </div>

                  <div class="flex items-center justify-between pt-1 gap-3">
                    <div class="flex items-center gap-2">
                      <label class="text-[11px] font-semibold text-slate-600">Duty Shift:</label>
                      <select id="shift-{_esc(pid)}" class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-900 font-medium text-xs">
                        <option value="1" {sel_morning}>Morning</option>
                        <option value="5" {sel_evening}>Evening</option>
                        <option value="20" {sel_night}>Night</option>
                      </select>
                    </div>
                    <button type="button" onclick="saveAssignment('{_esc(pid)}')"
                      class="px-4 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-semibold transition">
                      Update Assignment
                    </button>
                  </div>
                </div>
              </div>

              <!-- Quick Role Links for this Patient -->
              <div class="flex items-center justify-between pt-4 mt-4 border-t border-slate-100 text-xs">
                <a href="/doctor?patient_id={_esc(pid)}" class="text-teal-700 hover:text-teal-900 font-semibold">
                  2. Open Doctor View (Prescribe) →
                </a>
                <a href="/nurse?patient_id={_esc(pid)}" class="text-slate-600 hover:text-slate-900 font-semibold">
                  3. Open Nurse View (Give Meds) →
                </a>
              </div>
            </div>
            """
        )

    modal_doc_opts = "".join([f'<option value="{_esc(d)}">{_esc(d)}</option>' for d in DOCTOR_OPTIONS])
    modal_nurse_opts = "".join([f'<option value="{_esc(n)}">{_esc(n)}</option>' for n in NURSE_OPTIONS])

    body = f"""
    <!-- Hospital Page Header -->
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <span class="text-xs font-bold uppercase tracking-wider text-teal-700">Step 1 • Hospital Management</span>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight mt-0.5">
          Assign Right Doctor & Nurse to Each Patient
        </h1>
        <p class="text-sm text-slate-500 mt-0.5">
          Manage ICU bed assignments so the assigned Doctor can prescribe medicines and the assigned Nurse can administer them.
        </p>
      </div>
      <button type="button" onclick="openAddPatientModal()"
        class="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow-xs transition flex items-center gap-2">
        <span class="text-base leading-none">+</span>
        <span>Add New Patient</span>
      </button>
    </div>

    <!-- 4 Simple Summary KPIs -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-7">
      <div class="clean-card rounded-2xl p-4">
        <div class="text-xs text-slate-500">Total ICU Patients</div>
        <div class="text-2xl font-bold text-slate-900 mt-1">{metrics['total_beds']} Patients</div>
      </div>
      <div class="clean-card rounded-2xl p-4">
        <div class="text-xs text-slate-500">Staff Assignment Status</div>
        <div class="text-2xl font-bold text-emerald-700 mt-1">100% Assigned</div>
      </div>
      <div class="clean-card rounded-2xl p-4">
        <div class="text-xs text-slate-500">Pending Medicines for Nurse</div>
        <div class="text-2xl font-bold text-amber-600 mt-1">{metrics['pending_tasks']} Orders</div>
      </div>
      <div class="clean-card rounded-2xl p-4">
        <div class="text-xs text-slate-500">Patient History Records</div>
        <div class="text-2xl font-bold text-teal-700 mt-1">{metrics['total_memories']} Notes</div>
      </div>
    </div>

    <!-- Patient Assignment Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      {"".join(bed_cards)}
    </div>

    <!-- Add New Patient Modal -->
    <div id="add-patient-modal" class="hidden fixed inset-0 z-50 bg-slate-900/35 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="clean-card rounded-2xl max-w-lg w-full p-6 shadow-xl">
        <div class="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
          <div>
            <h3 class="text-base font-bold text-slate-900">Admit New ICU Patient</h3>
            <p class="text-xs text-slate-500">Enter patient details and assign Doctor &amp; Nurse</p>
          </div>
          <button type="button" onclick="closeAddPatientModal()" class="text-slate-400 hover:text-slate-700 text-sm">✕</button>
        </div>

        <form id="add-patient-form" class="space-y-3.5 text-xs">
          <div class="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <div class="sm:col-span-2">
              <label class="block text-slate-700 font-semibold mb-1">Patient Full Name *</label>
              <input type="text" id="new_pt_name" required placeholder="e.g. Vikram Rathore"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-teal-600" />
            </div>
            <div>
              <label class="block text-slate-700 font-semibold mb-1">Age *</label>
              <input type="number" id="new_pt_age" required value="54" min="1" max="120"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-teal-600" />
            </div>
            <div>
              <label class="block text-slate-700 font-semibold mb-1">Gender *</label>
              <select id="new_pt_gender" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium">
                <option value="M">Male (M)</option>
                <option value="F">Female (F)</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-700 font-semibold mb-1">Bed Number &amp; ICU Unit *</label>
              <input type="text" id="new_pt_bed" required value="Bed 18 • Cardiac ICU"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-teal-600" />
            </div>
            <div>
              <label class="block text-slate-700 font-semibold mb-1">Duty Shift</label>
              <select id="new_pt_shift" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium">
                <option value="1">Morning Shift</option>
                <option value="5">Evening Shift</option>
                <option value="20" selected>Night Shift</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-slate-700 font-semibold mb-1">Primary Diagnosis *</label>
            <input type="text" id="new_pt_diag" required placeholder="e.g. Acute Coronary Syndrome • Post-PCI Day 1"
              class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-teal-600" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-700 font-semibold mb-1">Heart Rate</label>
              <input type="text" id="new_pt_hr" value="88 bpm"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium" />
            </div>
            <div>
              <label class="block text-slate-700 font-semibold mb-1">Blood Pressure</label>
              <input type="text" id="new_pt_bp" value="128/82"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium" />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-700 font-semibold mb-1">Assign Doctor</label>
              <select id="new_pt_doc" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium">
                {modal_doc_opts}
              </select>
            </div>
            <div>
              <label class="block text-slate-700 font-semibold mb-1">Assign Nurse</label>
              <select id="new_pt_nurse" class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium">
                {modal_nurse_opts}
              </select>
            </div>
          </div>

          <div>
            <label class="block text-slate-700 font-semibold mb-1">Past Reaction / Drug Allergy Note (Optional)</label>
            <input type="text" id="new_pt_risk" placeholder="e.g. Allergic to Penicillin; avoid Beta-Lactam antibiotics"
              class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 focus:bg-white focus:outline-none focus:border-teal-600" />
          </div>

          <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button type="button" onclick="closeAddPatientModal()" class="px-4 py-2 rounded-xl bg-slate-100 text-slate-600 font-medium">
              Cancel
            </button>
            <button type="submit" id="add-pt-submit-btn" class="px-5 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold">
              Admit Patient &amp; Assign Staff
            </button>
          </div>
        </form>
      </div>
    </div>

    <script>
      function openAddPatientModal() {{
        document.getElementById('add-patient-modal').classList.remove('hidden');
      }}
      function closeAddPatientModal() {{
        document.getElementById('add-patient-modal').classList.add('hidden');
      }}
      if (window.location.search.includes('add_patient=1')) {{
        openAddPatientModal();
      }}

      document.getElementById('add-patient-form').addEventListener('submit', async (e) => {{
        e.preventDefault();
        const btn = document.getElementById('add-pt-submit-btn');
        btn.textContent = 'Admitting...';

        const res = await fetch('/api/patients', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            name: document.getElementById('new_pt_name').value,
            age: parseInt(document.getElementById('new_pt_age').value || '54', 10),
            gender: document.getElementById('new_pt_gender').value,
            bed_number: document.getElementById('new_pt_bed').value,
            admission_diagnosis: document.getElementById('new_pt_diag').value,
            attending_md: document.getElementById('new_pt_doc').value,
            primary_nurse: document.getElementById('new_pt_nurse').value,
            current_shift: parseInt(document.getElementById('new_pt_shift').value || '20', 10),
            hr: document.getElementById('new_pt_hr').value,
            bp: document.getElementById('new_pt_bp').value,
            known_risk_note: document.getElementById('new_pt_risk').value
          }})
        }});
        if (res.ok) {{
          window.location.href = '/hospital';
        }} else {{
          btn.textContent = 'Admit Patient & Assign Staff';
        }}
      }});

      async function saveAssignment(patientId) {{
        const doc = document.getElementById('doc-' + patientId).value;
        const nurse = document.getElementById('nurse-' + patientId).value;
        const shiftEl = document.getElementById('shift-' + patientId);
        const shift = parseInt(shiftEl.value || '20', 10);
        const shiftText = shiftEl.options[shiftEl.selectedIndex].text + ' Shift';
        const msg = document.getElementById('assign-msg-' + patientId);
        const badge = document.getElementById('shift-badge-' + patientId);

        const res = await fetch(`/api/patients/${{patientId}}/assign`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            attending_md: doc,
            primary_nurse: nurse,
            current_shift: shift
          }})
        }});
        if (res.ok) {{
          if (badge) badge.textContent = shiftText;
          msg.classList.remove('hidden');
          setTimeout(() => msg.classList.add('hidden'), 2500);
        }}
      }}
    </script>
    """
    return _render_shell(
        title="Hospital Assignment • WardSense Health",
        active_page="hospital",
        user=ctx["user"],
        patients=patients,
        selected_patient_id=patients[0]["patient_id"],
        hindsight_status=ctx["hindsight_status"],
        config=ctx["config"],
        body_html=body,
    )


# ==============================================================================
# PAGE 2: DOCTOR PORTAL — Check Past History & Prescribe Medicine to Nurse
# ==============================================================================
def render_doctor_page(ctx: dict[str, Any]) -> str:
    import urllib.parse

    patients = ctx["patients"]
    sp = ctx["selected_patient"]
    selected_doctor = ctx.get("selected_doctor") or sp["attending_md"]
    doctor_has_patients = ctx.get("doctor_has_patients", True)
    v = sp["vitals"]
    ipass_brief = ctx["ipass_brief"]
    comp = ctx["initial_comparison"]
    patient_memories = ctx.get("patient_memories", ipass_brief["recalled_memories"])
    patient_tasks = ctx.get("patient_tasks", [])

    # Collect all doctors (standard + any custom assigned in DB)
    all_docs = list(DOCTOR_OPTIONS)
    for p in patients:
        if p["attending_md"] not in all_docs:
            all_docs.append(p["attending_md"])

    # 1. Doctor Tabs
    doctor_tabs = []
    for d in all_docs:
        count = sum(1 for p in patients if p["attending_md"] == d)
        is_active_doc = d == selected_doctor
        tab_cls = (
            "bg-teal-600 text-white font-semibold shadow-xs"
            if is_active_doc
            else "text-slate-600 hover:bg-slate-100 font-medium"
        )
        badge_cls = (
            "bg-teal-700 text-teal-50"
            if is_active_doc
            else "bg-slate-200/80 text-slate-600"
        )
        q_doc = urllib.parse.quote(d)
        short_doc_name = d.replace(", MD", "")
        doctor_tabs.append(
            f"""
            <a href="/doctor?doctor={q_doc}"
               class="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs transition {tab_cls}">
              <span>{_esc(short_doc_name)}</span>
              <span class="px-1.5 py-0.5 rounded-md text-[10px] font-bold {badge_cls}">{count}</span>
            </a>
            """
        )

    # 2. Assigned Patients for Selected Doctor
    assigned_patients = [p for p in patients if p["attending_md"] == selected_doctor]
    assigned_patient_pills = []
    for p in assigned_patients:
        is_sel_pt = doctor_has_patients and p["patient_id"] == sp["patient_id"]
        pt_cls = (
            "bg-teal-50 text-teal-800 border-teal-400 font-semibold"
            if is_sel_pt
            else "bg-white text-slate-600 border-slate-200 hover:border-teal-300"
        )
        q_doc = urllib.parse.quote(selected_doctor)
        assigned_patient_pills.append(
            f"""
            <a href="/doctor?doctor={q_doc}&patient_id={_esc(p['patient_id'])}"
               class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs transition {pt_cls}">
              <span class="w-2 h-2 rounded-full bg-teal-500"></span>
              <span>{_esc(p['name'])} ({_esc(p['bed_number'].split('•')[0].strip())})</span>
            </a>
            """
        )
    if not assigned_patient_pills:
        assigned_patient_pills.append(
            '<span class="text-xs text-slate-400 italic">No patients assigned to this doctor yet — <a href="/hospital" class="text-teal-700 underline font-semibold">Assign from Hospital Page</a></span>'
        )

    # Left Column: Simplified Patient Past History Cards (deduplicated & clean shift names)
    history_cards = []
    seen_mem_contents: set[str] = set()
    for m in patient_memories:
        if m["content"] in seen_mem_contents:
            continue
        seen_mem_contents.add(m["content"])
        is_crit = m["severity"] == "CRITICAL"
        card_cls = (
            "bg-rose-50/60 border-rose-200/80"
            if is_crit
            else "bg-slate-50/80 border-slate-200/60"
        )
        badge_cls = (
            "bg-rose-100 text-rose-800"
            if is_crit
            else "bg-slate-200/70 text-slate-700"
        )
        clean_shift_name = _shift_label_from_num(int(m.get("shift_number", 20)))
        short_author = m["author_name"].split(",")[0].strip()
        clean_note = (
            m["content"]
            .replace("04:15 IST Bedside Alert: ", "")
            .replace("06:30 IST Lab & Telemetry Note: ", "")
            .replace("CRITICAL ADVERSE EVENT: ", "")
            .replace("SEVERE HYPERSENSITIVITY: ", "")
        )
        history_cards.append(
            f"""
            <div class="p-3.5 rounded-xl border {card_cls}">
              <div class="flex items-center justify-between gap-2 text-xs mb-1">
                <span class="font-bold text-slate-800">{_esc(clean_shift_name)} · <span class="font-medium text-slate-500">{_esc(short_author)}</span></span>
                <span class="text-[11px] font-semibold px-2 py-0.5 rounded-md {badge_cls}">
                  {_esc(m['category'])}
                </span>
              </div>
              <p class="text-xs text-slate-700 leading-relaxed">{_esc(clean_note)}</p>
            </div>
            """
        )

    # Active Medicines Assigned to Nurse (deduplicated)
    assigned_meds_html = []
    seen_task_titles: set[str] = set()
    for t in patient_tasks:
        if t["title"] in seen_task_titles:
            continue
        seen_task_titles.add(t["title"])
        is_done = t["status"] == "COMPLETED"
        status_badge = (
            '<span class="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">✓ Given by Nurse</span>'
            if is_done
            else '<span class="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200">Waiting for Nurse</span>'
        )
        assigned_meds_html.append(
            f"""
            <div class="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between gap-3">
              <div>
                <div class="text-xs font-semibold text-slate-900">{_esc(t['title'])}</div>
                <div class="text-[11px] text-slate-500 mt-0.5">{_esc(t['clinical_reason'])}</div>
              </div>
              {status_badge}
            </div>
            """
        )

    safe_med_text = sp["hindsight_safe_protocol"]["safe_alternative"]
    unsafe_med_text = sp["stateless_trap_order"]
    active_shift_label = _shift_label_from_num(int(sp["current_shift"]))

    body = f"""
    <!-- Doctor Header + Doctor & Assigned Patient Selector -->
    <div class="mb-5 space-y-4">
      <div>
        <span class="text-xs font-bold uppercase tracking-wider text-teal-700">Step 2 • Doctor Portal</span>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight mt-0.5">
          Review Patient History & Prescribe Medicine to Nurse
        </h1>
        <p class="text-sm text-slate-500 mt-0.5">
          <strong>{_esc(sp['bed_number'])}: {_esc(sp['name'])} ({sp['age']}{_esc(sp['gender'])})</strong>
          • Assigned Doctor: <span class="text-teal-700 font-semibold">{_esc(selected_doctor)}</span>
          • Assigned Nurse: <span class="text-slate-800 font-semibold">{_esc(sp['primary_nurse'])}</span>
        </p>
      </div>

      <!-- Select Doctor & Assigned Patients Bar -->
      <div class="clean-card rounded-2xl p-4 space-y-3">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider mr-1">Select Doctor:</span>
          <div class="flex flex-wrap items-center gap-1.5 p-1 bg-slate-50 rounded-xl border border-slate-200/70">
            {"".join(doctor_tabs)}
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2 pt-2.5 border-t border-slate-100">
          <span class="text-xs font-semibold text-slate-500 mr-1">
            Assigned Patients for {_esc(selected_doctor.replace(', MD', ''))}:
          </span>
          <div class="flex flex-wrap items-center gap-2">
            {"".join(assigned_patient_pills)}
          </div>
        </div>
      </div>
    </div>

    <!-- Patient Current Vitals Strip -->
    <div class="clean-card rounded-2xl p-4 mb-6 flex flex-wrap items-center justify-between gap-4">
      <div class="flex flex-wrap items-center gap-6 text-xs">
        <div>
          <span class="text-slate-400 block">Diagnosis</span>
          <span class="font-semibold text-slate-900 text-sm">{_esc(sp['admission_diagnosis'])}</span>
        </div>
        <div class="h-7 w-px bg-slate-100"></div>
        <div>
          <span class="text-slate-400 block">Heart Rate</span>
          <span class="font-semibold text-slate-900 text-sm">{_esc(v['hr'].split(' ')[0])} bpm</span>
        </div>
        <div class="h-7 w-px bg-slate-100"></div>
        <div>
          <span class="text-slate-400 block">Blood Pressure</span>
          <span class="font-semibold text-slate-900 text-sm">{_esc(v['bp'].split(' ')[0])} mmHg</span>
        </div>
        <div class="h-7 w-px bg-slate-100"></div>
        <div>
          <span class="text-slate-400 block">Potassium (K+)</span>
          <span class="font-semibold text-amber-700 text-sm">{_esc(v['k_plus'])}</span>
        </div>
      </div>

      <!-- Shift Memory Filter -->
      <div class="flex items-center gap-1.5 text-xs">
        <span class="text-slate-400 font-medium mr-1">Shift View:</span>
        <button onclick="simulateLearningShift(1)" id="shift-btn-1" class="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 font-medium">
          Morning
        </button>
        <button onclick="simulateLearningShift(5)" id="shift-btn-5" class="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 font-medium">
          Evening
        </button>
        <button onclick="simulateLearningShift(20)" id="shift-btn-20" class="px-2.5 py-1 rounded-lg bg-teal-600 text-white font-semibold">
          Night
        </button>
      </div>
    </div>

    <!-- Main 2-Column Doctor Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

      <!-- Left 5 Cols: Simplified Past Patient History -->
      <div class="lg:col-span-5 space-y-4">
        <div class="clean-card rounded-2xl p-5">
          <div class="flex items-center justify-between mb-3">
            <div>
              <h2 class="text-base font-bold text-slate-900">1. Patient Past History</h2>
              <p class="text-xs text-slate-500">Previous shift reactions & nurse notes</p>
            </div>
            <span id="hindsight-latency-badge" class="text-[11px] font-semibold text-teal-700 bg-teal-50 px-2.5 py-0.5 rounded-full">
              {_esc(active_shift_label)}
            </span>
          </div>

          <!-- Simple, Short Known Risk Box -->
          <div class="p-3.5 rounded-xl bg-amber-50/80 border border-amber-200/80 text-xs space-y-1.5 mb-4">
            <div class="font-bold text-amber-900">⚠️ Important Past Reaction Note</div>
            <p class="text-amber-900/90 leading-relaxed">{_esc(sp['hindsight_safe_protocol']['clinical_why'])}</p>
            <div class="pt-1.5 border-t border-amber-200/60 text-emerald-900 font-medium">
              <strong>Recommended Safe Protocol:</strong> {_esc(safe_med_text)}
            </div>
            <div id="ipass-contingency" class="hidden">{_esc(ipass_brief['ipass']['situation_awareness_contingency'])}</div>
          </div>

          <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Previous Shift Notes</div>
          <div class="space-y-2.5 max-h-[420px] overflow-y-auto pr-1">
            {"".join(history_cards)}
          </div>
        </div>
      </div>

      <!-- Right 7 Cols: Structured Medicine Prescription Form + Safety Check -->
      <div class="lg:col-span-7 space-y-5">

        <!-- Prescribe Medicine Form Card -->
        <div class="clean-card rounded-2xl p-6">
          <div class="flex flex-wrap items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-100">
            <div>
              <h2 class="text-base font-bold text-slate-900">
                2. Prescribe Medicine to Nurse ({_esc(sp['primary_nurse'])})
              </h2>
              <p class="text-xs text-slate-500 mt-0.5">
                Fill medicine details below, verify safety against history, and send to Nurse Station
              </p>
            </div>
            <!-- Quick Fill Presets -->
            <div class="flex gap-1.5">
              <button type="button" onclick="fillMedicineOrder('unsafe')"
                class="px-2.5 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-800 border border-rose-200 text-[11px] font-semibold transition">
                Fill Unsafe Example
              </button>
              <button type="button" onclick="fillMedicineOrder('safe')"
                class="px-2.5 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 text-[11px] font-semibold transition">
                Fill Safe Example
              </button>
            </div>
          </div>

          <!-- 4 Structured Prescription Fields -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3.5 text-xs">
            <div class="sm:col-span-1">
              <label class="block font-semibold text-slate-700 mb-1">Medicine Name *</label>
              <input type="text" id="rx-name" list="common-meds" value="Furosemide (Lasix)" oninput="syncOrderInput()"
                placeholder="e.g. Bumetanide"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-teal-600" />
              <datalist id="common-meds">
                <option value="Bumetanide + KCl"></option>
                <option value="Furosemide (Lasix)"></option>
                <option value="Metoprolol"></option>
                <option value="Aztreonam + Vancomycin"></option>
                <option value="Piperacillin-Tazobactam"></option>
                <option value="Norepinephrine"></option>
                <option value="Enoxaparin (LMWH)"></option>
              </datalist>
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Dosage *</label>
              <input type="text" id="rx-dose" value="80mg" oninput="syncOrderInput()"
                placeholder="e.g. 0.5mg/hr or 40mg"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-teal-600" />
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Route & Frequency *</label>
              <select id="rx-route" onchange="syncOrderInput()"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-teal-600">
                <option value="IV Stat Bolus" selected>IV Stat Bolus</option>
                <option value="IV Continuous Infusion">IV Continuous Infusion</option>
                <option value="IV Every 8 Hours (Q8H)">IV Every 8 Hours (Q8H)</option>
                <option value="Oral (PO) Twice Daily">Oral (PO) Twice Daily</option>
                <option value="Subcutaneous (SC)">Subcutaneous (SC)</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-4 gap-3 mb-4 text-xs">
            <div class="sm:col-span-3">
              <label class="block font-semibold text-slate-700 mb-1">Instructions / Clinical Reason for Nurse</label>
              <input type="text" id="rx-notes" value="For acute pulmonary congestion and fluid overload" oninput="syncOrderInput()"
                placeholder="e.g. Give after 40mEq KCl infusion; monitor HR & BP"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 focus:bg-white focus:outline-none focus:border-teal-600" />
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Priority</label>
              <select id="rx-priority"
                class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-teal-600">
                <option value="CRITICAL">Urgent / Stat</option>
                <option value="HIGH">Routine Shift</option>
              </select>
            </div>
          </div>

          <!-- Combined Order Preview & Action Buttons -->
          <input type="hidden" id="proposed-order-input" value="{_esc(unsafe_med_text)}" />

          <div id="prescribe-banner" class="hidden mb-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900"></div>

          <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
            <button type="button" onclick="runOrderVerification()" id="verify-order-btn"
              class="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white font-semibold text-xs transition">
              1. Check History Safety
            </button>

            <button type="button" onclick="prescribeMedicineToNurse()" id="prescribe-btn"
              class="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-xs transition">
              2. Prescribe & Send to Nurse →
            </button>
          </div>

          <!-- Compact Safety Check Result Box -->
          <div class="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-3.5">
            <!-- Without History -->
            <div class="rounded-xl bg-slate-50 border border-slate-200/80 p-3.5">
              <div class="flex items-center justify-between gap-2 mb-1.5">
                <span class="text-[11px] font-semibold text-slate-400 uppercase">Without Past History</span>
                <span id="stateless-verdict" class="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                  {_esc(comp['stateless_ai']['verdict'].split('—')[0].strip())}
                </span>
              </div>
              <p id="stateless-risk" class="text-xs text-rose-700 leading-relaxed">{_esc(comp['stateless_ai']['risk_missed'])}</p>
              <p id="stateless-reasoning" class="hidden">{_esc(comp['stateless_ai']['reasoning'])}</p>
            </div>

            <!-- With Hindsight History -->
            <div class="rounded-xl bg-white border-2 border-teal-500 p-3.5">
              <div class="flex items-center justify-between gap-2 mb-1.5">
                <span class="text-[11px] font-semibold text-teal-700 uppercase">With Hindsight History</span>
                <span id="hindsight-verdict" class="text-[11px] font-semibold px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200">
                  {_esc(comp['hindsight_agent']['verdict'].split('—')[0].strip())}
                </span>
              </div>
              <p id="hindsight-why" class="text-xs text-slate-700 leading-relaxed mb-1.5">{_esc(comp['hindsight_agent']['clinical_why'])}</p>
              <div class="text-[11px] text-emerald-800 bg-emerald-50 px-2.5 py-1.5 rounded-lg border border-emerald-200/70">
                <strong>Safe Option:</strong> <span id="hindsight-alternative">{_esc(comp['hindsight_agent']['safe_alternative'])}</span>
              </div>
              <div id="hindsight-shift-cite" class="hidden"></div>
            </div>
          </div>
        </div>

        <!-- Active Medicines Sent to Nurse -->
        <div class="clean-card rounded-2xl p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-bold text-slate-900">Prescriptions Sent to Nurse ({_esc(sp['primary_nurse'])})</h3>
            <a href="/nurse?patient_id={_esc(sp['patient_id'])}" class="text-xs font-semibold text-teal-700 hover:underline">
              Open Nurse Station →
            </a>
          </div>
          <div class="space-y-2">
            {"".join(assigned_meds_html)}
          </div>
        </div>

      </div>
    </div>

    <script>
      const currentPatientId = "{_esc(sp['patient_id'])}";
      const unsafePreset = `{_esc(unsafe_med_text)}`;
      const safePreset = `{_esc(safe_med_text)}`;
      let currentSimulatedShift = null;

      function syncOrderInput() {{
        const name = document.getElementById('rx-name').value.trim();
        const dose = document.getElementById('rx-dose').value.trim();
        const route = document.getElementById('rx-route').value.trim();
        const notes = document.getElementById('rx-notes').value.trim();
        const combined = `${{name}} ${{dose}} (${{route}})${{notes ? ' — ' + notes : ''}}`.trim();
        document.getElementById('proposed-order-input').value = combined;
      }}

      function fillMedicineOrder(mode) {{
        if (mode === 'safe') {{
          document.getElementById('rx-name').value = 'Bumetanide + 40mEq KCl';
          document.getElementById('rx-dose').value = '0.5mg/hr';
          document.getElementById('rx-route').value = 'IV Continuous Infusion';
          document.getElementById('rx-notes').value = safePreset;
          document.getElementById('proposed-order-input').value = safePreset;
        }} else {{
          document.getElementById('rx-name').value = 'Furosemide (Lasix)';
          document.getElementById('rx-dose').value = '80mg';
          document.getElementById('rx-route').value = 'IV Stat Bolus';
          document.getElementById('rx-notes').value = 'For acute pulmonary congestion and fluid overload';
          document.getElementById('proposed-order-input').value = unsafePreset;
        }}
        runOrderVerification();
      }}

      async function runOrderVerification() {{
        const btn = document.getElementById('verify-order-btn');
        const orderText = document.getElementById('proposed-order-input').value;
        btn.textContent = 'Checking...';

        const res = await fetch('/api/orders/verify', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            patient_id: currentPatientId,
            proposed_order: orderText,
            simulated_shift_limit: currentSimulatedShift
          }})
        }});
        const data = await res.json();
        btn.textContent = '1. Check History Safety';

        document.getElementById('stateless-verdict').textContent = data.stateless_ai.verdict.split('—')[0].strip();
        document.getElementById('stateless-risk').textContent = data.stateless_ai.risk_missed;

        const hv = document.getElementById('hindsight-verdict');
        hv.textContent = data.hindsight_agent.verdict.split('—')[0].strip();
        if (data.hindsight_agent.verdict.includes('APPROVED') || data.hindsight_agent.verdict.includes('SAFE')) {{
          hv.className = 'text-[11px] font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200';
        }} else {{
          hv.className = 'text-[11px] font-semibold px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200';
        }}

        document.getElementById('hindsight-why').textContent = data.hindsight_agent.clinical_why;
        document.getElementById('hindsight-alternative').textContent = data.hindsight_agent.safe_alternative;
        document.getElementById('hindsight-latency-badge').textContent =
          data.hindsight_telemetry.latency_ms + 'ms';
      }}

      async function prescribeMedicineToNurse() {{
        syncOrderInput();
        const btn = document.getElementById('prescribe-btn');
        const banner = document.getElementById('prescribe-banner');
        const orderText = document.getElementById('proposed-order-input').value;
        const notes = document.getElementById('rx-notes').value || 'Prescribed by Doctor after history review';
        const priority = document.getElementById('rx-priority').value || 'CRITICAL';
        btn.textContent = 'Sending to Nurse...';

        const res = await fetch('/api/orders/prescribe', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            patient_id: currentPatientId,
            medicine_order: orderText,
            clinical_reason: notes,
            priority: priority
          }})
        }});
        const data = await res.json();
        btn.textContent = '2. Prescribe & Send to Nurse →';
        if (data.success) {{
          banner.innerHTML = `<strong>✓ Prescription Sent to Nurse!</strong> <a href="/nurse?patient_id=${{currentPatientId}}" class="underline font-bold ml-1">Open Nurse Station to Administer →</a>`;
          banner.classList.remove('hidden');
          setTimeout(() => window.location.reload(), 1100);
        }}
      }}

      async function simulateLearningShift(shiftNum) {{
        currentSimulatedShift = shiftNum;
        [1, 5, 20].forEach(n => {{
          const b = document.getElementById('shift-btn-' + n);
          if (n === shiftNum) {{
            b.className = 'px-2.5 py-1 rounded-lg bg-teal-600 text-white font-semibold';
          }} else {{
            b.className = 'px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 font-medium';
          }}
        }});

        const ipassRes = await fetch(`/api/ipass/${{currentPatientId}}?shift=${{shiftNum}}`);
        const ipassData = await ipassRes.json();
        document.getElementById('ipass-contingency').textContent = ipassData.ipass.situation_awareness_contingency;
        await runOrderVerification();
      }}
    </script>
    """
    return _render_shell(
        title="Doctor Workspace • WardSense Health",
        active_page="doctor",
        user=ctx["user"],
        patients=patients,
        selected_patient_id=sp["patient_id"],
        hindsight_status=ctx["hindsight_status"],
        config=ctx["config"],
        body_html=body,
    )


# ==============================================================================
# PAGE 3: NURSE STATION — Give Medicine & Update Patient History
# ==============================================================================
def render_nurse_page(ctx: dict[str, Any]) -> str:
    import urllib.parse

    patients = ctx["patients"]
    sp = ctx["selected_patient"]
    selected_nurse = ctx.get("selected_nurse") or sp["primary_nurse"]
    nurse_has_patients = ctx.get("nurse_has_patients", True)
    patient_tasks = ctx["patient_tasks"]
    patient_memories = ctx["patient_memories"]

    # Collect all nurses (standard + any custom assigned in DB)
    all_nurses = list(NURSE_OPTIONS)
    for p in patients:
        if p["primary_nurse"] not in all_nurses:
            all_nurses.append(p["primary_nurse"])

    # 1. Nurse Tabs (in the red-marked area)
    nurse_tabs = []
    for n in all_nurses:
        count = sum(1 for p in patients if p["primary_nurse"] == n)
        is_active_nurse = n == selected_nurse
        tab_cls = (
            "bg-teal-600 text-white font-semibold shadow-xs"
            if is_active_nurse
            else "text-slate-600 hover:bg-slate-100 font-medium"
        )
        badge_cls = (
            "bg-teal-700 text-teal-50"
            if is_active_nurse
            else "bg-slate-200/80 text-slate-600"
        )
        q_nurse = urllib.parse.quote(n)
        short_nurse_name = n.replace(", RN", "")
        nurse_tabs.append(
            f"""
            <a href="/nurse?nurse={q_nurse}"
               class="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs transition {tab_cls}">
              <span>{_esc(short_nurse_name)}</span>
              <span class="px-1.5 py-0.5 rounded-md text-[10px] font-bold {badge_cls}">{count}</span>
            </a>
            """
        )

    # 2. Assigned Patients for the Selected Nurse
    assigned_patients = [p for p in patients if p["primary_nurse"] == selected_nurse]
    assigned_patient_pills = []
    for p in assigned_patients:
        is_sel_pt = nurse_has_patients and p["patient_id"] == sp["patient_id"]
        pt_cls = (
            "bg-teal-50 text-teal-800 border-teal-400 font-semibold"
            if is_sel_pt
            else "bg-white text-slate-600 border-slate-200 hover:border-teal-300"
        )
        q_nurse = urllib.parse.quote(selected_nurse)
        assigned_patient_pills.append(
            f"""
            <a href="/nurse?nurse={q_nurse}&patient_id={_esc(p['patient_id'])}"
               class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs transition {pt_cls}">
              <span class="w-2 h-2 rounded-full bg-teal-500"></span>
              <span>{_esc(p['name'])} ({_esc(p['bed_number'].split('•')[0].strip())})</span>
            </a>
            """
        )
    if not assigned_patient_pills:
        assigned_patient_pills.append(
            '<span class="text-xs text-slate-400 italic">No patients assigned to this nurse yet — <a href="/hospital" class="text-teal-700 underline font-semibold">Assign from Hospital Page</a></span>'
        )

    task_cards = []
    seen_nurse_tasks: set[str] = set()
    for t in patient_tasks:
        if t["title"] in seen_nurse_tasks:
            continue
        seen_nurse_tasks.add(t["title"])
        is_done = t["status"] == "COMPLETED"
        title_cls = "line-through text-slate-400" if is_done else "text-slate-900 font-semibold"
        card_bg = "bg-slate-50 border-slate-100" if is_done else "bg-amber-50/40 border-amber-200"
        btn_cls = (
            "bg-emerald-50 border-emerald-200 text-emerald-700"
            if is_done
            else "bg-teal-600 hover:bg-teal-700 border-teal-600 text-white shadow-xs"
        )
        btn_label = "✓ Medicine Given" if is_done else "Give Medicine Now"
        safe_title_js = _esc(t["title"]).replace("'", "\\'")

        task_cards.append(
            f"""
            <div class="p-4 rounded-xl border {card_bg} flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div class="{title_cls} text-xs">{_esc(t['title'])}</div>
                <div class="text-slate-500 text-[11px] mt-1">{_esc(t['clinical_reason'])}</div>
                <div class="text-slate-400 text-[10px] mt-0.5">{_esc(t['shift_origin'])}</div>
              </div>
              <button onclick="giveMedicineAndPrepareLog('{_esc(t['task_id'])}', '{safe_title_js}')"
                class="px-3.5 py-2 rounded-xl text-xs font-semibold border transition shrink-0 {btn_cls}">
                {btn_label}
              </button>
            </div>
            """
        )

    mem_cards = []
    seen_nurse_mems: set[str] = set()
    for m in patient_memories:
        if m["content"] in seen_nurse_mems:
            continue
        seen_nurse_mems.add(m["content"])
        clean_shift = _shift_label_from_num(int(m.get("shift_number", 20)))
        mem_cards.append(
            f"""
            <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
              <div class="flex items-center justify-between text-xs mb-1">
                <span class="font-semibold text-teal-800">{_esc(clean_shift)}</span>
                <span class="text-slate-400">{_esc(m['category'])}</span>
              </div>
              <p class="text-xs text-slate-600 leading-relaxed">{_esc(m['content'])}</p>
              <div class="text-[10px] text-slate-400 mt-1">Updated by: {_esc(m['author_name'])}</div>
            </div>
            """
        )
        if len(mem_cards) >= 5:
            break

    body = f"""
    <!-- Nurse Header + Nurse & Assigned Patient Selector -->
    <div class="mb-6 space-y-4">
      <div>
        <span class="text-xs font-bold uppercase tracking-wider text-teal-700">Step 3 • Nurse Station</span>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight mt-0.5">
          Give Prescribed Medicine & Update Patient History
        </h1>
        <p class="text-sm text-slate-500 mt-0.5">
          <strong>{_esc(sp['bed_number'])}: {_esc(sp['name'])} ({sp['age']}{_esc(sp['gender'])})</strong>
          • Assigned Nurse: <span class="text-teal-700 font-semibold">{_esc(selected_nurse)}</span>
          • Prescribing Doctor: <span class="text-slate-800 font-semibold">{_esc(sp['attending_md'])}</span>
        </p>
      </div>

      <!-- Nurse Selector & Assigned Patients Box -->
      <div class="clean-card rounded-2xl p-4 space-y-3">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider mr-1">Select Nurse:</span>
          <div class="flex flex-wrap items-center gap-1.5 p-1 bg-slate-50 rounded-xl border border-slate-200/70">
            {"".join(nurse_tabs)}
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2 pt-2.5 border-t border-slate-100">
          <span class="text-xs font-semibold text-slate-500 mr-1">
            Assigned Patients for {_esc(selected_nurse.replace(', RN', ''))}:
          </span>
          <div class="flex flex-wrap items-center gap-2">
            {"".join(assigned_patient_pills)}
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

      <!-- Left 6 Cols: Step 1 — Doctor's Prescribed Medicines to Give -->
      <div class="lg:col-span-6 space-y-6">
        <div class="clean-card rounded-2xl p-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-base font-bold text-slate-900">1. Doctor's Prescribed Medicines</h2>
              <p class="text-xs text-slate-500">Click "Give Medicine Now" after administering to the patient</p>
            </div>
            <span class="text-xs font-semibold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-full">
              From {_esc(sp['attending_md'])}
            </span>
          </div>

          <div class="space-y-3">
            {"".join(task_cards)}
          </div>
        </div>

        <div class="clean-card rounded-2xl p-6">
          <h3 class="text-sm font-bold text-slate-900 mb-3">Recent Patient History Log</h3>
          <div class="space-y-2.5">
            {"".join(mem_cards)}
          </div>
        </div>
      </div>

      <!-- Right 6 Cols: Step 2 — Update Patient History (Saved to Hindsight Memory) -->
      <div class="lg:col-span-6">
        <div class="clean-card rounded-2xl p-6">
          <div class="mb-4">
            <h2 class="text-base font-bold text-slate-900">2. Update Patient History & Response</h2>
            <p class="text-xs text-slate-500 mt-0.5">
              Record how the patient responded after medicine. Hindsight saves this for the next shift's Doctor.
            </p>
          </div>

          <div class="flex flex-wrap gap-2 mb-4">
            <button type="button"
              onclick="fillNursePreset('Medicine Given & Response', 'INFO', 'Administered prescribed continuous Bumetanide 0.5mg/hr IV after 40mEq KCl. Urine output improved to 180mL/hr, Heart Rate stable at 84 bpm, no arrhythmia observed.')"
              class="px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 text-xs font-semibold transition">
              + Fill: Medicine Given Safely
            </button>
            <button type="button"
              onclick="fillNursePreset('Adverse Drug Reaction', 'CRITICAL', '04:15 IST Bedside Alert: Patient developed acute bradycardia (HR dropped to 44 bpm) and BP dropped to 86/52 mmHg 12 minutes after IV Metoprolol 5mg push. Hold all beta-blockers on next shift.')"
              class="px-3 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-800 border border-rose-200 text-xs font-semibold transition">
              + Fill: Drug Reaction Alert
            </button>
          </div>

          <div id="retain-result-banner" class="hidden mb-4 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900"></div>

          <form id="nurse-retain-form" class="space-y-4 text-xs">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-slate-600 font-semibold mb-1.5">History Update Type</label>
                <select id="obs_category" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900">
                  <option value="Medicine Given & Response">Medicine Given & Response</option>
                  <option value="Adverse Drug Reaction">Adverse Drug Reaction / Side Effect</option>
                  <option value="Electrolyte & Arrhythmia Alert">Vitals / Lab Update</option>
                  <option value="Shift Handoff Directive">Shift Handover Note for Doctor</option>
                </select>
              </div>
              <div>
                <label class="block text-slate-600 font-semibold mb-1.5">Patient Condition Status</label>
                <select id="obs_severity" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900">
                  <option value="CRITICAL">Critical Alert (Warn Next Doctor)</option>
                  <option value="WARNING">Needs Watch</option>
                  <option value="INFO">Stable / Normal Response</option>
                </select>
                <input type="hidden" id="obs_shift" value="{sp['current_shift'] + 1}" />
              </div>
            </div>

            <div>
              <label class="block text-slate-600 font-semibold mb-1.5">What happened after giving medicine? (History Note)</label>
              <textarea id="obs_content" rows="4" required
                class="w-full p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-sm leading-relaxed focus:bg-white focus:outline-none focus:border-teal-600">04:15 IST Bedside Alert: Patient developed acute bradycardia (HR dropped to 44 bpm) and hypotension (86/52 mmHg) 12 minutes after IV Metoprolol 5mg push. Hold all beta-blockers on morning rounds.</textarea>
            </div>

            <div class="flex items-center justify-between pt-2">
              <a href="/doctor?patient_id={_esc(sp['patient_id'])}" class="text-teal-700 hover:underline font-semibold">
                ← Check in Doctor Portal
              </a>
              <button type="submit" id="retain-submit-btn"
                class="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs transition shadow-xs">
                Update Patient History →
              </button>
            </div>
          </form>
        </div>
      </div>

    </div>

    <script>
      const nursePatientId = "{_esc(sp['patient_id'])}";

      function fillNursePreset(category, severity, content) {{
        document.getElementById('obs_category').value = category;
        document.getElementById('obs_severity').value = severity;
        document.getElementById('obs_content').value = content;
      }}

      async function giveMedicineAndPrepareLog(taskId, medTitle) {{
        await fetch(`/api/tasks/${{taskId}}/toggle`, {{ method: 'POST' }});
        window.location.reload();
      }}

      document.getElementById('nurse-retain-form').addEventListener('submit', async (e) => {{
        e.preventDefault();
        const btn = document.getElementById('retain-submit-btn');
        const banner = document.getElementById('retain-result-banner');
        btn.textContent = 'Updating History...';

        const res = await fetch('/api/memories/retain', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            patient_id: nursePatientId,
            shift_number: parseInt(document.getElementById('obs_shift').value || '21', 10),
            category: document.getElementById('obs_category').value,
            severity: document.getElementById('obs_severity').value,
            content: document.getElementById('obs_content').value,
          }})
        }});
        const data = await res.json();
        btn.textContent = 'Update Patient History →';

        if (data.success) {{
          banner.innerHTML = `<strong>✓ Patient History Updated!</strong> Next shift Doctor will see this automatically. <a href="/doctor?patient_id=${{nursePatientId}}" class="underline font-bold ml-1">View in Doctor Portal →</a>`;
          banner.classList.remove('hidden');
          setTimeout(() => window.location.reload(), 1200);
        }}
      }});
    </script>
    """
    return _render_shell(
        title="Nurse Station • WardSense Health",
        active_page="nurse",
        user=ctx["user"],
        patients=patients,
        selected_patient_id=sp["patient_id"],
        hindsight_status=ctx["hindsight_status"],
        config=ctx["config"],
        body_html=body,
    )
