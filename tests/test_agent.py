"""Unit and integration tests for SiteSense Zero-Rework RFI Agent."""
import pytest
from src.agent import SiteSenseRFIAgent
from src.models import WorkerQueryRequest, HazardLevel, RFIDocument, Discipline


def test_agent_initialization_and_rfis():
    agent = SiteSenseRFIAgent()
    rfis = agent.get_all_rfis()
    assert len(rfis) >= 6
    assert any(r.id == "RFI-104" for r in rfis)


def test_critical_post_tension_hazard_detection():
    agent = SiteSenseRFIAgent()
    query = WorkerQueryRequest(
        question="Can I core drill a 4-inch hole at Level 3, Grid B-4?",
        level="Level 3",
        grid_location="Grid B-4",
        action_type="Core Drilling"
    )
    resp = agent.evaluate_worker_query(query)
    
    assert resp.status == HazardLevel.CRITICAL_STOP_WORK
    assert "POST-TENSION" in resp.verdict.upper() or "CRITICAL" in resp.verdict.upper()
    assert resp.rework_cost_prevented >= 180000.00
    assert "B-6" in resp.recommended_alternative  # Guides worker to safe sleeve


def test_high_voltage_busway_hazard_detection():
    agent = SiteSenseRFIAgent()
    query = WorkerQueryRequest(
        question="I need to install 75mm heavy anchor bolts at Level 2, Grid C-2 along the drywall.",
        level="Level 2",
        grid_location="Grid C-2"
    )
    resp = agent.evaluate_worker_query(query)
    
    assert resp.status == HazardLevel.CRITICAL_STOP_WORK
    assert "480V" in resp.hazard_details or "ARC FLASH" in resp.verdict
    assert resp.rework_cost_prevented >= 90000.00


def test_dynamic_learning_new_rfi_ingestion():
    agent = SiteSenseRFIAgent()
    
    # Query an unencumbered grid first
    initial_q = WorkerQueryRequest(
        question="Can I drill anchor holes at Level 1, Grid D-8?",
        level="Level 1",
        grid_location="Grid D-8"
    )
    initial_resp = agent.evaluate_worker_query(initial_q)
    assert initial_resp.status == HazardLevel.SAFE_PROCEED
    
    # Now engineer issues an emergency RFI for Grid D-8
    new_rfi = RFIDocument(
        id="RFI-999",
        title="Emergency Fuel Gas Line Relocation",
        date_issued="2024-09-01",
        discipline=Discipline.MEP,
        level="Level 1",
        grid_location="Grid D-8",
        issue_description="Natural gas high-pressure main routed across Grid D-8 ceiling.",
        approved_resolution="Strict hot-work and drilling prohibition within 3 meters of Grid D-8.",
        hazard_level=HazardLevel.CRITICAL_STOP_WORK,
        critical_directives=["Zero drilling or spark generation within 3m."],
        tags=["natural-gas", "flammable", "grid-d8"],
        rework_cost_risk=250000.00
    )
    agent.add_rfi(new_rfi)
    
    # Query again - Hindsight memory should now immediately catch the hazard!
    subsequent_resp = agent.evaluate_worker_query(initial_q)
    assert subsequent_resp.status == HazardLevel.CRITICAL_STOP_WORK
    assert subsequent_resp.rework_cost_prevented >= 250000.00
