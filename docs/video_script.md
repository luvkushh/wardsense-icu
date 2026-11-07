# 3-Minute Video Demo Script: SiteSense RFI

**Video Goal:** Show how persistent agent memory via Vectorize Hindsight prevents a $185,000 structural disaster on a construction site.  
**Style:** Screen recording (1080p) + voiceover / webcam.

---

## 5 High-Performing YouTube Titles

1. **How Persistent Agent Memory Stopped a $185,000 Construction Disaster**
2. **I Replaced Blueprints with an AI Agent That Never Forgets Structural Changes**
3. **Why Stateless AI Destroys Job Sites (And How Hindsight Fixes It)**
4. **Building an Autonomous Construction Safety Agent with Vectorize Hindsight**
5. **The $185k Mistake That Only AI With Memory Can Catch**

---

## Script & Screen Cues

### Part 1: Quick Intro (0:00 - 0:30)
* **What to show on screen:**  
  Start with the webcam / title screen, then switch over to the **SiteSense RFI Web Dashboard** (`http://localhost:8000`).
* **Speaker Narration:**  
  "Hey everyone, I'm [Your Name]. In mega-construction projects, the single most expensive mistake a subcontractor can make is drilling into a wall or slab without knowing about an engineering change made months ago.
  
  Stateless chatbots and static blueprint RAG cannot solve this because they only read the original base drawings.
  
  To solve this, I built **SiteSense RFI**—an autonomous site agent powered by **Vectorize Hindsight** that gives agents long-term persistent memory to retain historical RFIs and prevent catastrophic field rework before a drill ever touches concrete."

---

### Part 2: The Problem - What Goes Wrong Without Memory (0:30 - 1:00)
* **What to show on screen:**  
  Toggle to the **Stateless vs Hindsight Battle Mode** on the dashboard, highlighting the red card: *Without Hindsight (Failure)*.
* **Speaker Narration:**  
  "Let me show you why standard AI fails here. Imagine a plumber on Level 3 needs to drill a 4-inch core hole at Grid B-4. He asks a standard LLM agent: *'Can I core drill through the floor at Level 3, Grid B-4?'*
  
  The stateless model reads the Rev-0 architectural plans. It says: *'Yes, standard 8-inch reinforced concrete, no chases. Go ahead.'*
  
  What the model didn't know is that three months ago, structural engineering issued RFI-104 adding 33,000-pound post-tension cables right through that coordinate.
  
  The worker drills, severs the tendon, the atrium cantilever sags, and the project incurs an emergency repair bill of **$185,000**."

---

### Part 3: Live Demo - Hindsight Retain & Recall in Action (1:00 - 2:30)
* **What to show on screen:**  
  1. Open terminal and run: `python3 run.py demo`. Show the rich tables displaying the Hindsight memory bank (`project_omega_tower`) retaining RFI-104, RFI-112, and RFI-145 with `client.retain()`.
  2. Switch to the Web Dashboard at `http://localhost:8000`. Click on **Level 3**, then click on **Grid B-4** on the 2D interactive radar map.
  3. Show the question populate in the query box: *"Can I core-drill a 4-inch sleeve through the slab at Level 3, Grid B-4 to run a plumbing waste drain?"*
  4. Click **Verify Against Memory**.
  5. Point to the glowing red alert: **🚨 CRITICAL STRUCTURAL HAZARD: STOP WORK IMMEDIATELY**.
  6. Highlight the Recalled Hindsight section: RFI-104 (approved March 12), risk $185,000, and the approved safe alternative: *Divert conduit to designated MEP Chase sleeve at Grid B-6*.
  7. Show dynamic learning: Click **Ingest New RFI**, submit an emergency change order for Grid D-8, and watch the agent instantly recall it on the next query.
* **Speaker Narration:**  
  "Now look what happens when we give the agent memory with Hindsight.
  
  In the backend, every RFI is stored into a dedicated Hindsight memory bank with `client.retain()`. Hindsight extracts spatial coordinates like 'Grid B-4', temporal dates, and structural directives into a temporal knowledge graph.
  
  When our worker submits the question from the field, SiteSense calls `client.recall()`. In just 12 milliseconds, Hindsight pulls up RFI-104 from 4 months ago.
  
  Instead of saying 'go ahead', SiteSense triggers a full stop-work alert: *'STOP WORK! 4x post-tension cables embedded at 110mm depth.'* 
  
  And notice this: it doesn't just block the worker—it recalls RFI-108 and guides him to an approved alternative sleeve at Grid B-6 only 10 feet away. Zero rework, zero downtime."

---

### Part 4: One Key Takeaway & Wrap Up (2:30 - 3:00)
* **What to show on screen:**  
  Switch back to the code view in `src/agent.py` or the metrics banner showing **$322,000 Rework Prevented**.
* **Speaker Narration:**  
  "The biggest insight building this was realizing that vector embeddings alone are not enough for real-world agents. In the physical world, temporal precedence and entity relationships are everything. An RFI from yesterday must override a blueprint from last year.
  
  Vectorize Hindsight made managing temporal memory effortless with simple retain and recall calls.
  
  Check out the GitHub repo below to run the dashboard and CLI yourself. Thanks for watching!"
