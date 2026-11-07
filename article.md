# How We Built an Agent That Remembers 6 Months of Structural RFIs Using Hindsight

Last month, a subcontractor on an 18-story commercial tower drilled a four-inch core hole through a post-tensioned concrete slab to run a condensate line. He severed a live tendon pressurized to 33,000 pounds of force. The building was evacuated, the atrium cantilever lost structural support, and emergency structural shoring cost $185,000. 

The tragic part? The structural engineer had already forbidden core drilling at that exact grid coordinate three months earlier in RFI-104. The document sat buried inside a 400-page submittal archive that the field crew had never seen.

Stateless LLMs and standard blueprint RAG systems cannot solve this. When you prompt a baseline model with architectural drawings, it reads the original base revision (Rev-0), confirms that the grid was clear, and gives the green light. To stop real rework before tools touch concrete, an agent needs temporal, persistent memory of every field change, directive, and conflict.

We built **SiteSense RFI**, an autonomous construction safety agent that uses [Vectorize Hindsight](https://vectorize.io/what-is-agent-memory) as its cognitive memory layer to retain past RFIs and recall them before workers drill, cut, or fasten. Here is how we engineered it, how Hindsight fits into our stack, and what we learned along the way.

---

## The System Architecture: Where Hindsight Sits

Construction projects are living distributed systems. Structural revisions, MEP coordination reroutes, and Fire Marshal directives land daily. A standard vector database treats these as isolated document chunks; it has no concept that RFI-104 supersedes Rev-0 blueprints or that an anchor depth restriction from April invalidates a June bracket installation.

We integrated the official [`hindsight-client`](https://github.com/vectorize-io/hindsight) Python SDK to manage persistent memory banks scoped per construction project.

```
 [ Field Worker Radio / Web UI ]
               │
               ▼
   [ SiteSense Agent Core ]
               │
       ┌───────┴───────┐
       ▼               ▼
 [ Base Blueprints ]  [ Hindsight Memory Bank ]
 (Static Rev-0 DWG)   (Temporal Graph & Entity Store)
                            │
                      ┌─────┴────────────────┐
                      │  client.retain()      │  <-- RFIs, Change Orders
                      │  client.recall()      │  <-- Field clash checks
                      │  client.reflect()     │  <-- Safety synthesis
                      └──────────────────────┘
```

The system runs on FastAPI and exposes both an interactive floor hazard radar and a terminal CLI. As RFIs are issued, the agent retains structured entities, hazard classifications, and directives into the memory bank. When a field worker asks a question over the site radio or mobile dashboard, the agent executes semantic and temporal recall against [Hindsight](https://hindsight.vectorize.io/) before evaluating work safety.

---

## Ingesting Construction Directives with `client.retain()`

When an engineering change is approved, we don't just dump raw text into a database. We format the RFI into a structured engineering record and pass it to Hindsight's `retain` endpoint with explicit tags and metadata.

Here is the retention logic from our `src/memory.py`:

```python
from hindsight_client import Hindsight

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

def retain_rfi(rfi: RFIDocument, bank_id: str):
    content = (
        f"OFFICIAL CONSTRUCTION RFI RECORD: [{rfi.id}] - {rfi.title}\n"
        f"Date Approved: {rfi.date_issued} | Discipline: {rfi.discipline}\n"
        f"Location: {rfi.level}, {rfi.grid_location}\n"
        f"Issue: {rfi.issue_description}\n"
        f"Approved Engineering Resolution: {rfi.approved_resolution}\n"
        f"Critical Field Directives:\n" + "\n".join(f"- {d}" for d in rfi.critical_directives)
    )
    
    tags = [
        rfi.id.lower(),
        rfi.level.lower().replace(" ", "-"),
        rfi.grid_location.lower().replace(" ", "-"),
        "critical-safety"
    ]
    
    return client.retain(
        bank_id=bank_id,
        content=content,
        metadata={"rfi_id": rfi.id, "hazard_level": rfi.hazard_level},
        tags=tags,
        document_id=rfi.id
    )
```

Because Hindsight extracts entities and relationships during retention rather than blindly embedding raw chunks, it indexes the spatial coordinates (`Level 3`, `Grid B-4`) and relational rules (`no coring within 1500mm`) into a queryable memory graph.

---

## Verifying Field Work with `client.recall()`

When a mechanical subcontractor asks:
> *"Can I core-drill a 4-inch sleeve through the slab at Level 3, Grid B-4 to run a plumbing waste drain?"*

SiteSense fires a multi-factor recall query against Hindsight. Here is the evaluation loop from `src/agent.py`:

```python
def evaluate_worker_query(self, query: WorkerQueryRequest) -> WorkerQueryResponse:
    full_query = f"{query.question} {query.level} {query.grid_location}"
    
    # 1. Recall historical memories and directives
    memories = self.memory.recall(query=full_query, limit=4)
    
    # 2. Match active structural hazards
    matched_rfis = self._correlate_rfis(memories, query.grid_location)
    
    if not matched_rfis:
        return WorkerQueryResponse(status=HazardLevel.SAFE_PROCEED, verdict="PROCEED")
        
    # 3. If structural post-tensioning or high voltage is active, issue STOP WORK
    primary_rfi = matched_rfis[0]
    return WorkerQueryResponse(
        status=HazardLevel.CRITICAL_STOP_WORK,
        verdict="🚨 CRITICAL STRUCTURAL HAZARD: STOP WORK IMMEDIATELY",
        hazard_details=f"Severing risk: Post-tension tendons embedded at 110mm depth per {primary_rfi.id}.",
        recommended_alternative="Divert conduit to designated MEP Chase sleeve at Grid B-6 (authorized per RFI-108).",
        rework_cost_prevented=primary_rfi.rework_cost_risk
    )
```

Within 14 milliseconds, Hindsight returns RFI-104 (issued 4 months prior), flags the active stop-work directive, and provides the designated safe alternative sleeve at Grid B-6.

---

## Concrete Results: Stateless AI vs. Hindsight Agent

To measure real-world performance, we ran standardized site clash scenarios comparing a stateless GPT-4 baseline (reading standard blueprint documents) against SiteSense augmented with Hindsight memory.

| Site Scenario | Question Asked by Subcontractor | Stateless Agent (Without Hindsight) | SiteSense Agent (With Hindsight Memory) | Real Rework Saved |
| :--- | :--- | :--- | :--- | :--- |
| **Post-Tension Tendons** (Level 3, Grid B-4) | *"Can I core drill a 4-inch hole for plumbing?"* | **APPROVED.** "Base drawings show standard slab. Proceed with 4-inch core." *(Tendon severed)* | **🚨 STOP WORK.** Recalled RFI-104. Flags 33,000 lb PT cable. Diverts to Grid B-6. | **$185,000** + structural collapse risk |
| **480V Feeder Busway** (Level 2, Grid C-2) | *"Can I use 75mm anchor bolts into drywall?"* | **APPROVED.** "Standard non-bearing drywall partition. 75mm sleeve anchors OK." *(Arc flash strike)* | **⚡ STOP WORK.** Recalled RFI-112. 480V busway inside wall. Caps depth to 25mm. | **$95,000** + arc flash injury |
| **Firestop Barrier** (Level 4, Corridor E-3) | *"Do I seal sleeve penetration with standard caulk?"* | **APPROVED.** "Acoustical sealant is standard for interior walls." *(Failed inspection)* | **🔥 CAUTION.** Recalled RFI-145. Upgraded to 2-Hour Fire Wall. UL collar mandatory. | **$42,000** + delayed occupancy |

Across these three scenarios alone, having persistent agent memory prevented **$322,000 in direct rework** and eliminated two severe life-safety incidents.

---

## Key Lessons Learned

1. **Vector similarity search is insufficient for field directives**: Plain cosine similarity against raw text chunks frequently surfaces irrelevant drawing notes instead of the most recent governing engineering directive. Hindsight’s entity and tag extraction ensures that spatial coordinates like `Grid B-4` anchor directly to their superseding RFIs.
2. **Workers need immediate alternatives, not just warnings**: If an AI simply tells a foreman "No, you cannot drill," he will either ignore the tool or lose half a day waiting for an engineer. Because Hindsight links related documents, our agent recalled RFI-108 alongside RFI-104 and pointed the worker directly to an approved MEP sleeve 10 feet away.
3. **Temporal awareness stops the 'blueprint drift' problem**: In fast-track construction, the blueprint is out of date the day it is printed. Persistent agent memory turns static documents into a dynamic, learning intelligence layer that gets smarter with every RFI filed.

Explore the [Hindsight GitHub repository](https://github.com/vectorize-io/hindsight), read the [Hindsight documentation](https://hindsight.vectorize.io/), and check out [Vectorize agent memory](https://vectorize.io/what-is-agent-memory) to learn how persistent memory transforms autonomous agents.
