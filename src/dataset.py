"""Pre-loaded realistic construction RFIs for Omega Tower Project.
Demonstrates temporal modifications, structural safety changes, and MEP revisions.
"""
from typing import List
from src.models import RFIDocument, HazardLevel, Discipline, ComparisonItem

INITIAL_RFIS: List[RFIDocument] = [
    RFIDocument(
        id="RFI-104",
        title="Level 3 Post-Tensioning Cable Addition at Grid B-4",
        date_issued="2024-03-12",
        discipline=Discipline.STRUCTURAL,
        level="Level 3",
        grid_location="Grid B-4",
        issue_description=(
            "Structural engineer added supplemental post-tensioning (PT) tendons to mitigate deflection "
            "around the atrium cantilever. Blueprints (Rev 0) showed solid concrete slab without tendons."
        ),
        approved_resolution=(
            "Approved: 4x 0.5-inch 270ksi unbonded monostrand post-tension tendons embedded at 110mm depth "
            "running diagonally across Grid B-4 through Grid B-5. No core drilling or slab penetrations allowed."
        ),
        hazard_level=HazardLevel.CRITICAL_STOP_WORK,
        critical_directives=[
            "STRICTLY FORBIDDEN: Any core drilling or slab cutting within a 1500mm radius of Grid B-4.",
            "Tension tendons are pressurized to 33,000 lbs force. Severing risks catastrophic slab failure and personal injury.",
            "All mechanical penetrations must divert to designated MEP Chase at Grid B-6 as authorized in RFI-108."
        ],
        tags=["structural", "post-tension", "level-3", "grid-b4", "critical-safety", "no-coring"],
        rework_cost_risk=185000.00
    ),
    RFIDocument(
        id="RFI-112",
        title="Relocation of 480V High-Voltage Busway above Ceiling",
        date_issued="2024-04-05",
        discipline=Discipline.ELECTRICAL,
        level="Level 2",
        grid_location="Grid C-2",
        issue_description=(
            "Interference between primary ductwork and high-voltage feeder busway at Grid C-2 plenum space. "
            "Original electrical design routed busway along Column C-1."
        ),
        approved_resolution=(
            "Approved: 480V/800A bus duct rerouted directly behind the drywall partition at Grid C-2 at height 2.8m. "
            "Fastener penetrations deeper than 25mm into the wall studs are hazardous."
        ),
        hazard_level=HazardLevel.CRITICAL_STOP_WORK,
        critical_directives=[
            "CAUTION: 480V live energized bus duct runs horizontally at +2800mm AFF along Grid C-2 drywall.",
            "Drywall anchors or mechanical hangers must NOT exceed 25mm penetration depth.",
            "De-energization and Lockout/Tagout (LOTO) mandatory before any heavy bracket drilling."
        ],
        tags=["electrical", "high-voltage", "level-2", "grid-c2", "loto", "fire-hazard"],
        rework_cost_risk=95000.00
    ),
    RFIDocument(
        id="RFI-128",
        title="Medical Gas Vacuum Pipe Isolation Zone",
        date_issued="2024-05-18",
        discipline=Discipline.MEP,
        level="Level 3",
        grid_location="Grid D-1",
        issue_description=(
            "Surgical suite vacuum and nitrous lines rerouted to clear shear wall reinforcement at Grid D-1. "
            "Copper piping is uninsulated."
        ),
        approved_resolution=(
            "Approved: Maintain a minimum 500mm thermal isolation clearance. No steam or hot water heating lines "
            "may run parallel within this zone. Hot work / torch cutting requires hot-work permit and copper shielding."
        ),
        hazard_level=HazardLevel.CAUTION_VERIFY,
        critical_directives=[
            "Hot-work permit required for any brazing or grinding within Grid D-1 zone.",
            "Strict 500mm physical separation must be maintained between med-gas lines and steam pipes.",
            "Verify with Hospital Clinical Engineer prior to closing partition walls."
        ],
        tags=["medgas", "mep", "level-3", "grid-d1", "hot-work", "isolation"],
        rework_cost_risk=65000.00
    ),
    RFIDocument(
        id="RFI-145",
        title="2-Hour Fire Barrier Upgrade at Corridor E-3",
        date_issued="2024-06-22",
        discipline=Discipline.FIRE_PROTECTION,
        level="Level 4",
        grid_location="Grid E-3",
        issue_description=(
            "City Fire Marshal rejected 1-hour smoke partition between corridor and egress stairwell. "
            "Partition upgraded to 2-hour structural fire barrier."
        ),
        approved_resolution=(
            "Approved: 2 layers of 5/8-inch Type X gypsum installed. All pipe or cable penetrations must utilize "
            "UL System W-L-1054 intumescent firestop collars. Unsealed penetrations will fail occupancy inspection."
        ),
        hazard_level=HazardLevel.CAUTION_VERIFY,
        critical_directives=[
            "Corridor partition at Grid E-3 is now a certified 2-Hour Fire Wall.",
            "No uncollared penetrations permitted. Must log every sleeve in the Firestop Submittal Log.",
            "Field inspector must verify intumescent caulking thickness before dry lining."
        ],
        tags=["fire-safety", "ul-collar", "level-4", "grid-e3", "code-compliance"],
        rework_cost_risk=42000.00
    ),
    RFIDocument(
        id="RFI-159",
        title="Chilled Water Supply Line Rerouting around Elevator Shaft",
        date_issued="2024-07-10",
        discipline=Discipline.MEP,
        level="Level 1",
        grid_location="Grid A-6",
        issue_description=(
            "Hydraulic elevator piston casing clashed with 6-inch chilled water riser on base drawing M-201."
        ),
        approved_resolution=(
            "Approved: 6-inch chilled water riser offset 900mm east toward Grid A-7. Slab sleeve cast at A-7."
        ),
        hazard_level=HazardLevel.SAFE_PROCEED,
        critical_directives=[
            "Verify sleeve position at Grid A-7 before pipe delivery.",
            "Do not drill at old coordinate A-6 (sleeves have been grouted solid with non-shrink grout)."
        ],
        tags=["chilled-water", "hvac", "level-1", "grid-a6", "reroute"],
        rework_cost_risk=38000.00
    ),
    RFIDocument(
        id="RFI-166",
        title="Emergency Seismic Tieback Retrofit on Lower Shear Wall",
        date_issued="2024-08-01",
        discipline=Discipline.STRUCTURAL,
        level="Level 2",
        grid_location="Grid B-4",
        issue_description=(
            "Peer review mandated additional seismic drag struts directly below Level 3 Grid B-4 core location."
        ),
        approved_resolution=(
            "Approved: High-strength epoxy rebar dowels installed into beam underside at Grid B-4. "
            "Zero vibration or percussion drilling within 2m during concrete cure cycle."
        ),
        hazard_level=HazardLevel.CRITICAL_STOP_WORK,
        critical_directives=[
            "CRITICAL: Structural anchor epoxy curing until Aug 20. Absolutely zero hammer-drilling within 2m.",
            "Load transfer in progress. Any tampering or vibration can compromise anchor pullout strength."
        ],
        tags=["structural", "seismic", "level-2", "grid-b4", "vibration-restriction", "curing"],
        rework_cost_risk=120000.00
    ),
]


BENCHMARK_SCENARIOS: List[ComparisonItem] = [
    ComparisonItem(
        scenario_title="The $185,000 Post-Tension Cable Disaster",
        worker_question="Can I core-drill a 4-inch sleeve through the slab at Level 3, Grid B-4 to run a plumbing waste drain?",
        location="Level 3, Grid B-4",
        stateless_behavior={
            "agent_type": "Stateless LLM / Blueprint RAG (Without Hindsight)",
            "verdict": "PROCEED / CLEAR",
            "response": (
                "According to the base architectural drawing Rev-0, the concrete slab at Level 3, Grid B-4 "
                "is standard 8-inch reinforced concrete with no scheduled vertical chases. You may proceed with "
                "a standard 4-inch diamond core drill."
            ),
            "disaster_outcome": (
                "WORKER SEVERS POST-TENSION TENDON #2. Cable bursts from concrete under 33,000 lbs tension. "
                "Immediate evacuation. Atrium cantilever loses structural support. Project halted 4 weeks. "
                "Emergency structural shoring & repair costs: $185,000."
            ),
            "safety_rating": "CATASTROPHIC FAILURE"
        },
        hindsight_behavior={
            "agent_type": "SiteSense RFI Agent (Powered by Hindsight Memory)",
            "verdict": "STOP WORK - CRITICAL HAZARD",
            "response": (
                "🚨 STOP WORK IMMEDIATELY! DO NOT CORE DRILL.\n\n"
                "Recalled from Hindsight Memory Bank (RFI-104, approved March 12):\n"
                "Structural engineering added 4x 0.5-inch 270ksi unbonded post-tension tendons embedded at 110mm depth "
                "running diagonally across Grid B-4. Any coring will sever these cables and cause catastrophic slab failure.\n\n"
                "APPROVED ALTERNATIVE: Route your 4-inch drain line through designated MEP chase sleeve at Grid B-6 "
                "as authorized in RFI-108."
            ),
            "disaster_outcome": "Disaster completely prevented. Zero rework. Worker guided to approved sleeve.",
            "safety_rating": "LIFE SAFETY PRESERVED"
        },
        rework_cost_prevented=185000.00,
        safety_danger_prevented="Explosive post-tension tendon severance & structural cantilever collapse"
    ),
    ComparisonItem(
        scenario_title="The 480V High-Voltage Busway Drill Strike",
        worker_question="I'm mounting heavy equipment struts along the drywall at Level 2, Grid C-2. Can I use 75mm sleeve anchors?",
        location="Level 2, Grid C-2",
        stateless_behavior={
            "agent_type": "Stateless LLM / Blueprint RAG (Without Hindsight)",
            "verdict": "PROCEED",
            "response": (
                "Original architectural specs classify Grid C-2 as an interior non-bearing drywall partition. "
                "75mm heavy-duty anchors into metal studs are standard practice."
            ),
            "disaster_outcome": (
                "75mm drill bit penetrates the 480V/800A bus duct hidden inside wall cavity. Arc flash explosion. "
                "Hospital main breaker trips. Subcontractor suffers second-degree burns. Equipment fried: $95,000."
            ),
            "safety_rating": "LIFE SAFETY INCIDENT"
        },
        hindsight_behavior={
            "agent_type": "SiteSense RFI Agent (Powered by Hindsight Memory)",
            "verdict": "STOP WORK - ELECTRICAL ARC FLASH HAZARD",
            "response": (
                "⚡ CRITICAL SAFETY WARNING: DO NOT USE 75mm ANCHORS.\n\n"
                "Recalled from Hindsight Memory Bank (RFI-112, approved April 5):\n"
                "Due to MEP plenum clash, the 480V/800A electrical bus duct was rerouted horizontally directly behind "
                "the Grid C-2 drywall at +2.8m AFF.\n\n"
                "MANDATORY RESTRICTIONS:\n"
                "1. Fastener penetration depth is strictly capped at 25mm maximum.\n"
                "2. Electrical Lockout/Tagout (LOTO) is required if working within 500mm of the busway."
            ),
            "disaster_outcome": "Worker warned about hidden busway. Anchor depth restricted to 25mm. Arc flash averted.",
            "safety_rating": "ELECTRICAL SHOCK / ARC FLASH PREVENTED"
        },
        rework_cost_prevented=95000.00,
        safety_danger_prevented="480V arc flash explosion and electrical fire"
    ),
    ComparisonItem(
        scenario_title="The Fire Marshal Inspection Lockout",
        worker_question="I cut an 8-inch sleeve through Corridor wall E-3 on Level 4 for telecom cables. Do I just caulk it with standard acoustic sealant?",
        location="Level 4, Corridor E-3",
        stateless_behavior={
            "agent_type": "Stateless LLM / Blueprint RAG (Without Hindsight)",
            "verdict": "PROCEED",
            "response": "Yes, standard acoustical sealant or drywall mud can seal partition wall penetrations on corridor drawings.",
            "disaster_outcome": (
                "City Fire Marshal inspection fails the building 3 days before planned handover. "
                "Certificate of Occupancy denied. Entire corridor partition must be torn down and retrofitted. "
                "Liquidated damages + retrofit: $42,000."
            ),
            "safety_rating": "FAILED OCCUPANCY INSPECTION"
        },
        hindsight_behavior={
            "agent_type": "SiteSense RFI Agent (Powered by Hindsight Memory)",
            "verdict": "CAUTION: CERTIFIED FIRESTOP MANDATORY",
            "response": (
                "🔥 COMPLIANCE ALERT: DO NOT USE STANDARD CAULK.\n\n"
                "Recalled from Hindsight Memory Bank (RFI-145, approved June 22):\n"
                "Wall E-3 was upgraded from 1-hour partition to a certified 2-Hour Fire Barrier per Fire Marshal directive.\n\n"
                "MANDATORY REQUIREMENT:\n"
                "All penetrations MUST install UL System W-L-1054 intumescent firestop collars and be stamped into the "
                "Firestop Submittal Log. Standard acoustic sealant is an immediate code violation."
            ),
            "disaster_outcome": "Proper UL firestop collars installed. Occupancy inspection passed on first attempt.",
            "safety_rating": "REGULATORY COMPLIANCE SECURED"
        },
        rework_cost_prevented=42000.00,
        safety_danger_prevented="Loss of Certificate of Occupancy and failure of 2-hour smoke barrier"
    )
]
