# Apprentice — Project Roadmap

**Hackathon:** [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) — Physical AI Track  
**Submission deadline:** Friday, October 30, 2026, 10:00 am PDT  
**Judging:** December 1–15, 2026  
**This document is the build contract.** Work proceeds phase by phase. Do not start a later phase until the current phase’s exit criteria are met, unless a listed exception applies.

---

## 1. What we are building

**Apprentice** is a physical-AI skill compiler.

A person demonstrates a tabletop job once (teleop or narrated demo). The system turns that demonstration into a robot skill that still works when lighting, layout, or object pose change — and that can recover when the first attempt fails.

The product is the compiler (demo → skill). The arm is the proof.

### Core problem

Useful robot skills still cost more data and engineering than the job is worth. A pharmacy bench, small kitchen, university lab, or repair shop can show a task in two minutes. They cannot collect thousands of episodes or keep a GPU cluster. The work stays human. Apprentice closes that gap: **one human demonstration versus a reliable physical skill.**

### First skill (locked unless hardware forces a change)

**Clear a table: pick a visible object and place it in the correct bowl or bin.**

This skill is visually obvious on camera, easy to judge as success/fail, and hard enough to show generalization (new lighting, object shifted). A second domain object (vial, sandwich, PCB) is optional stretch only after Skill 1 is reliable.

### Non-goals

- Warehouse humanoids or Unitree G1 as the judged body
- CCTV-only “vision agents” with no actuator
- An LLM that emits `move_to(x,y,z)` into a scripted arm
- Training Cosmos or GR00T from scratch
- Five flaky skills instead of one bulletproof skill

---

## 2. How this satisfies the rules

Every phase must preserve this compliance matrix. If a task does not map to a row, it is out of scope.

| Rule / criterion | How Apprentice complies |
| --- | --- |
| Working app on **Nebius Token Factory** and/or **Nebius AI Cloud** | Live Token Factory `chat.completions` for Nemotron + Cosmos Reasoner; Serverless Jobs (and Endpoints if needed) for synthetic data, sim eval, and policy serving |
| ≥1 **NVIDIA open-source model** | Nemotron, Cosmos 3 Super Reasoner, Cosmos Predict/Transfer, Isaac GR00T N1.7 |
| **Physical AI track** | Cameras + proprioception in; joint commands out; object actually moves |
| Sense **and** act (Stage 1 filter) | Not a chatbot with a robot sticker. The arm changes the physical world |
| Serverless Jobs | Cosmos augmentation, Isaac Lab rollouts, GR00T fine-tune, episode curation |
| Serverless Endpoints | Serve the fine-tuned GR00T policy when no local GPU can hold it |
| Demo video ≤ 3 min | Script in Phase 5; judges need not run the code |
| ≥ 1 min **real hardware** | SO-101 follower arm, continuous take, no jump cuts |
| Public repo + OSI license | MIT (or Apache-2.0); license visible on GitHub About |
| README names NVIDIA + Nebius usage | Call sites listed as they land in code |
| Feedback form | Phase 5, required even for a $100 swag prize |
| Tavily runtime call | Skill-spec compilation looks up handling/safety facts |
| SONIC | Optional sim/retargeting only. Not the judged body. Do not fake a G1 |
| Pre-existing project clause | This repo starts during the submission window; no “what changed” essay needed unless we later import a prior codebase |

**Prize target:** Grand Prize ($20,000), not the track Jetson. Same four judging criteria apply overall. Tavily is a real tool in the skill compiler, which also qualifies for Best Use of Tavily ($3,000). Track prize is acceptable fallback.

**Judging weights (equal):** Technological Implementation, Design, Potential Impact, Quality of the Idea.

---

## 3. Platform map — who does what

Each platform has a job the others cannot do. Do not add a logo that does not sit on this diagram.

```
TEACH (minutes)                         FACTORY (hours)                         RUN (seconds)
────────────────                        ────────────────                        ─────────────
SO-101 + cameras                        Nebius Object Storage                   SO-101 follower
LeRobot episode                         Physical AI Workbench (npa)             GR00T policy (Endpoint or local)
        │                                       │                                       │
        ▼                                       ▼                                       ▼
Token Factory                           Serverless Jobs                         Token Factory
  Nemotron  → skill spec                  Cosmos Predict/Transfer                 Cosmos Reasoner → success/fail
  Tavily    → safety / procedure          Isaac Lab evals                         Nemotron → continue / retry / stop
  Cosmos Reasoner → scene parse           GR00T N1.7 fine-tune                    Tavily if object identity is uncertain
        │                                       │                                       │
        └──────────── skill card ───────────────┴────────── checkpoint ─────────────────┘
```

| Platform | Role in Apprentice | When it first appears |
| --- | --- | --- |
| **SO-101 + LeRobot** | Body, teleop, episode format | Phase 1 |
| **NVIDIA Isaac GR00T N1.7** | Vision-language-action motor skill | Phase 3 |
| **NVIDIA Cosmos 3 Super Reasoner** (`nvidia/Cosmos3-Super-Reasoner` on Token Factory) | Physical critic: did the grasp work, what failed | Phase 0 (API), Phase 4 (closed loop) |
| **NVIDIA Cosmos Predict / Transfer** | Multiply one demo into visual/layout variants | Phase 2 |
| **NVIDIA Nemotron** (Nano/Lightning for the loop; Super for skill compilation) | Agent runtime: plan, tools, recovery | Phase 0 (API), Phase 4 (product) |
| **Nebius Token Factory** | Live inference for Nemotron + Reasoner | Phase 0 |
| **Nebius AI Cloud Serverless Jobs** | Burst GPU: SDG, sim, train, eval | Phase 2 |
| **Nebius AI Cloud Serverless Endpoints** | Serve GR00T if the laptop cannot | Phase 3 |
| **Nebius Physical AI Workbench (`npa`)** | Declared YAML/CLI workflow instead of custom glue | Phase 2 |
| **NVIDIA Isaac Lab / Isaac Sim** | Physics test range before metal | Phase 2 |
| **Tavily** | Live procedure/safety facts the cameras do not know | Phase 4 |
| **SONIC** | Optional Workbench retargeting in sim only | Stretch, Phase 4 |

If a piece is dropped, the product breaks in a specific way (no body, no motor skill, no critic, no generalization, no evidence, no product, or a rules fail). That is the test for “logically blended.”

---

## 4. Calendar

Today is **Monday, September 21, 2026**. There are **39 days** to the deadline.

| Phase | Dates | Theme | Hard exit |
| --- | --- | --- | --- |
| **0 — Foundations** | Sep 21 – Sep 27 | Accounts, repo skeleton, Token Factory hello-world | Cloud calls work from this repo |
| **1 — First metal** | Sep 28 – Oct 4 | Hardware + one recorded skill, even if ugly | ≥60 s of the real arm moving on camera |
| **2 — Data factory** | Oct 5 – Oct 11 | Cosmos SDG + Isaac eval on Jobs/Workbench | 1 demo → N variants → eval artifact |
| **3 — Policy** | Oct 12 – Oct 18 | GR00T post-train + deploy | Policy runs the skill in sim and at least once on metal |
| **4 — Product** | Oct 19 – Oct 25 | Agent runtime, Tavily, teach UI, recovery | A person can teach and run without a notebook |
| **5 — Submit** | Oct 26 – Oct 30 | Freeze, video, README, Devpost | Submission form complete **before** 10:00 am PDT Oct 30 |

**Exception:** Phase 1 hardware can overlap Phase 0. If the SO-101 has not arrived by **October 4**, trigger the hardware fallback in §8 the same day. Do not wait.

**Feature freeze:** October 26, 2026. After freeze, only video, docs, reliability fixes, and submission packaging.

---

## 5. Phase 0 — Foundations (Sep 21 – Sep 27)

**Goal:** The repo can talk to Nebius and NVIDIA models. No robot required.

### 5.1 Accounts and credits

- [ ] Register / confirm Devpost entry; pick **Physical AI** as the track
- [ ] Join the [Nebius AI Builder Program](https://nebius.com/blog/posts/introducing-the-nebius-ai-builder-program) and apply credits
- [ ] Create a Nebius Token Factory API key; store it only in env / secret manager, never in git
- [ ] Create a Tavily API key (used in Phase 4; get it now so it is not a scramble)
- [ ] Confirm Nebius AI Cloud access: Object Storage, Serverless Jobs, Serverless Endpoints (or DevPods as bootstrap)
- [ ] Clone / install [Nebius Physical AI Workbench](https://github.com/nebius/nebius-physical-ai) (`npa`); record the exact version we pin
- [ ] Hugging Face account for LeRobot datasets and GR00T weights (`nvidia/GR00T-N1.7-3B`)

### 5.2 Hardware order (do not delay)

- [ ] Order **SO-101 leader + follower pair** plus two cameras (front + wrist). Seeed / WowRobo assembled kits are preferred over DIY if shipping time is tight
- [ ] Confirm delivery ETA. If ETA is after October 4, start fallback hardware sourcing the same day (§8)
- [ ] Reserve a fixed table, clamps, two bowls/bins, and a small set of demo objects (distinct colors)

### 5.3 Repository skeleton

Create the layout the rest of the roadmap will fill. Empty modules may exist as packages with README stubs.

```
apprentice/
  README.md
  ROADMAP.md                 ← this file
  LICENSE                    ← MIT
  pyproject.toml
  .env.example
  docs/
    ARCHITECTURE.md
    HACKATHON.md             ← rules mapping + call-site log
  src/apprentice/
    agent/                   ← Nemotron runtime
    critic/                  ← Cosmos Reasoner
    factory/                 ← Jobs / Workbench wrappers
    policy/                  ← GR00T client
    robot/                   ← LeRobot / SO-101 I/O
    skill/                   ← skill spec schema
  scripts/
    hello_token_factory.py
    hello_cosmos_reasoner.py
  tests/
```

- [ ] OSI license file at repo root so GitHub detects it
- [ ] `.env.example` with `NEBIUS_API_KEY`, `TAVILY_API_KEY`, model IDs, no secrets
- [ ] Python package installable with `uv` or `pip install -e .`

### 5.4 Hello-world inference (compliance starts here)

- [ ] `scripts/hello_token_factory.py` — Nemotron Nano or Lightning chat completion via `https://api.tokenfactory.nebius.com/v1/`
- [ ] `scripts/hello_cosmos_reasoner.py` — send one local image to `nvidia/Cosmos3-Super-Reasoner`; print a structured scene description
- [ ] Log model IDs, region, and request IDs in `docs/HACKATHON.md` so the README can cite real call sites later

**Pinned model IDs (change only with a roadmap note):**

| Job | Model ID |
| --- | --- |
| Fast agent loop | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` or `nvidia/Nemotron-3_5-Lightning` |
| Skill compilation | `nvidia/nemotron-3-super-120b-a12b` |
| Physical critic | `nvidia/Cosmos3-Super-Reasoner` |
| Motor skill | `nvidia/GR00T-N1.7-3B` |

Do **not** call Ultra 550B in Phase 0. Credits are finite.

### 5.5 Skill spec schema (no robot yet)

Define the JSON object that later phases pass around:

```json
{
  "name": "clear_table_to_bin",
  "goal": "Place the visible object into the matching bowl",
  "constraints": [],
  "success": ["object in target bowl", "gripper open", "arm clear of table"],
  "recovery": ["re-detect", "retry grasp once", "stop and ask"],
  "sources": { "demo_episode": null, "tavily": [] }
}
```

- [ ] Pydantic (or equivalent) schema + unit tests for parse/validate
- [ ] Nemotron prompt that drafts a spec from a text description of a demo (image optional)

### Phase 0 exit criteria

1. Token Factory Nemotron call succeeds from CI or a documented local command.
2. Token Factory Cosmos Reasoner call succeeds on a still image.
3. License + `.env.example` + package layout exist.
4. SO-101 is ordered **or** fallback hardware is identified with a ship date.

---

## 6. Phase 1 — First metal (Sep 28 – Oct 4)

**Goal:** One real demonstration on the arm, recorded in LeRobot format, and a 60-second hardware clip in the can. Success rate may be ugly. The clip is not optional.

### 6.1 Bring-up

- [ ] Assemble / unbox, flash/configure Feetech bus, calibrate leader and follower per LeRobot SO-101 docs
- [ ] Confirm camera indices (front, wrist), 640×480 @ 30 fps as a baseline
- [ ] Safety: e-stop or unplug path, workspace walls, no people in the sweep volume during policy runs
- [ ] Record calibration notes in `docs/HARDWARE.md` (ports, IDs, camera indices)

### 6.2 Data collection

- [ ] Teleop **Skill 1** for ≥20 episodes if time allows; **minimum 5** clean episodes to proceed
- [ ] Language instruction on every episode: a single canonical phrase, e.g. `"put the block in the blue bowl"`
- [ ] Save as GR00T-flavored LeRobot v2 (see Isaac GR00T `examples/SO100`)
- [ ] Hold out 2 episodes for evaluation; never train on them

### 6.3 Scripted baseline (honesty check)

- [ ] A non-learning replay or simple scripted motion that can place an object when the scene is identical to the demo
- [ ] This exists so later GR00T results have a baseline, and so the 60-second video is not blocked on training

### 6.4 Capture the judging clip early

- [ ] Shoot a **continuous 70–90 second** take of the follower arm operating (teleop or scripted is allowed for this clip)
- [ ] No jump cuts, no copyrighted music, well-lit table, instruction spoken on camera
- [ ] Archive the raw file. Phase 5 will edit; Phase 1 must not “wait for the perfect policy”

### Phase 1 exit criteria

1. Robot can be teleoperated and recorded end to end.
2. ≥5 LeRobot episodes of Skill 1 on disk.
3. Raw ≥60 s hardware footage stored.
4. `docs/HARDWARE.md` is enough for a teammate to plug in the same arm.

**If the arm has not arrived by October 4:** execute §8 immediately. Phase 2 can still run in sim with a public SO-101 / Isaac dataset, but the hardware clip remains a blocker for submission quality.

---

## 7. Phase 2 — Data factory (Oct 5 – Oct 11)

**Goal:** One real (or public) episode becomes many variants, evaluated in physics, on Nebius compute.

### 7.1 Workbench / Jobs plumbing

- [ ] Object Storage bucket for episodes, MP4s, checkpoints, eval JSON
- [ ] `npa` workflow YAML: ingest → (optional curate) → Cosmos augment → Isaac eval
- [ ] Same pipeline also runnable as Nebius Serverless Jobs from a container in this repo
- [ ] Dockerfile for factory workers; no secrets in the image

### 7.2 Cosmos augmentation

- [ ] Take 1–3 gold episodes; generate **at least 50** visual/layout variants (lighting, table clutter, object color/pose)
- [ ] Keep a side-by-side contact sheet (real vs synthetic) for the video and README
- [ ] Filter obvious physical nonsense with Cosmos Reasoner as a batch critic (Job, not interactive)

### 7.3 Isaac Lab evaluation harness

- [ ] Skill 1 task in Isaac Lab (or the official SO-101 sim stack) with a binary success flag
- [ ] Job that rolls out N episodes and writes `eval/summary.json` (success rate, failure tags)
- [ ] Dashboard artifact: one HTML or markdown report the teach UI will later embed

### 7.4 Cost and credit discipline

- [ ] Log GPU type, hours, and estimated $ for each Job in `docs/HACKATHON.md`
- [ ] Prefer L40S / RTX PRO 6000 for Isaac rendering (RT cores). Do not blindly schedule Isaac Sim on H100
- [ ] Cap a single SDG wave; iterate quality before scale

### Phase 2 exit criteria

1. A documented command starts a factory run on Nebius (Workbench or Serverless Jobs).
2. Artifacts: N synthetic clips + one eval summary from sim.
3. README section “How Nebius AI Cloud is used” can be written from real Job IDs.

---

## 8. Phase 3 — Policy (Oct 12 – Oct 18)

**Goal:** GR00T N1.7 post-trained on real + synthetic data, serving actions, succeeding on Skill 1 at least once on metal.

### 8.1 Fine-tune

- [ ] Convert datasets to the GR00T LeRobot v2 layout; register `NEW_EMBODIMENT` with the SO-101 modality config (upstream `examples/SO100`)
- [ ] Fine-tune `nvidia/GR00T-N1.7-3B` on Nebius (Job or Workbench `groot` path)
- [ ] Start small: a few thousand steps, batch size per official SO-100 example; do not burn the credit pool on a 10k-step first run
- [ ] Save checkpoint to Object Storage; record commit + dataset hash

### 8.2 Serve

- [ ] Policy client in `src/apprentice/policy` matching GR00T action chunks to LeRobot robot I/O
- [ ] If no local GPU: Nebius Serverless Endpoint (or Workbench serve) for the checkpoint
- [ ] Latency budget: action chunk back in time to keep 10–30 Hz control; measure and write the number down

### 8.3 Evaluate

- [ ] Sim: success rate on held-out layouts (factory eval job)
- [ ] Metal: ≥10 trials of Skill 1; log success/fail. **Target for this phase: any consistent >0 success**, not 90%
- [ ] Compare to Phase 1 scripted baseline on the same table

### Phase 3 exit criteria

1. A named GR00T checkpoint exists and is reproducible from the README.
2. Policy produces actions in sim.
3. At least one uncut metal episode where the policy (not teleop) completes Skill 1.
4. Endpoint **or** documented local GPU path is how the robot gets actions.

---

## 9. Phase 4 — Product (Oct 19 – Oct 25)

**Goal:** A complete product experience. This is the Design criterion. Stop looking like a research repo.

### 9.1 Agent runtime

- [ ] Nemotron loop: user goal → skill card → call GR00T → read Reasoner verdict → continue / retry / stop
- [ ] Cosmos Reasoner on wrist+front frames after each action chunk or at subgoal boundaries
- [ ] Structured verdict schema: `{success, failure_mode, next_subgoal}`
- [ ] One retry then stop (safe default). No infinite loops on metal

### 9.2 Tavily (required for bonus, justified in-product)

- [ ] During skill compilation, Nemotron calls Tavily when the object class is named (e.g. “insulin pen”, “solder paste”, “ceramic bowl”)
- [ ] Results become `constraints[]` and `success[]` on the skill card, with source URLs stored
- [ ] For Skill 1’s generic block/bowl, still call Tavily for a handling note (fragile / food-safe / keep upright) so the runtime path is real and logged
- [ ] Never call Tavily in the 30 Hz control loop

### 9.3 Teach UI

Minimum viable product, not a design-award app:

- [ ] Record / upload a demo
- [ ] Show the generated skill card (goal, constraints from Tavily, success checks)
- [ ] “Compile” button that launches or shows status of the factory Job
- [ ] Eval summary (success rate, a few failure clips)
- [ ] “Run on robot” with live camera and Reasoner one-liners (“grasp failed, retrying”)

Local web app (FastAPI + simple frontend) is enough. Hosting a public demo URL is **not required** for Physical AI, but a screen recording of this UI is required for Design.

### 9.4 Recovery demo (video gold)

- [ ] Change lighting **or** shift the object after the demo
- [ ] Policy + Reasoner + Nemotron retry visibly
- [ ] If it still fails, the UI says why and stops. A clean failure with an explanation scores better than a hidden one

### 9.5 SONIC (stretch only)

- [ ] Only if Phases 1–4 core path is green: Workbench SONIC retargeting of the skill in sim
- [ ] Label it “simulation / humanoid retarget,” never as the judged robot

### Phase 4 exit criteria

1. A non-author can teach (or load a saved demo) and run Skill 1 from the UI.
2. Tavily appears in logs as a runtime API call with query + citations on the skill card.
3. Reasoner-triggered retry is recorded on video at least once.
4. Architecture diagram in README matches the running system.

---

## 10. Phase 5 — Freeze, video, submit (Oct 26 – Oct 30)

**Goal:** Judges can score from video + README + public repo. No new features.

### 10.1 Feature freeze (Oct 26)

- [ ] Tag `v1.0.0-hackathon` on the commit that will be judged
- [ ] Open-source license still detected on GitHub
- [ ] Secrets scan; `.env` not in git
- [ ] `README.md` setup: how to run hello-world, factory (if they have Nebius credits), and robot (if they have an SO-101)

### 10.2 README (rules-mandatory content)

Must include:

- What Apprentice is and who it is for
- Architecture diagram
- **NVIDIA models used** (IDs + what they do)
- **Where Token Factory accelerated the workflow** (agent + critic)
- **Other Nebius services** (Jobs, Endpoints, Workbench, Object Storage)
- Tavily’s role
- Hardware bill of materials
- Setup instructions
- Link to this roadmap and to the demo video

### 10.3 Demo video (≤ 3:00, public YouTube, English)

Locked script — do not improvise structure:

| Time | Content |
| --- | --- |
| 0:00–0:20 | Problem: a person repeating a bench task |
| 0:20–0:50 | Architecture; say **Token Factory, Cosmos, GR00T, Serverless Jobs** out loud |
| 0:50–1:50 | **Real arm, continuous, no jump cuts** (use Phase 1 archive + best Phase 3/4 policy take) |
| 1:50–2:20 | Factory: one demo → Cosmos grid + Job eval numbers |
| 2:20–2:50 | Recovery: lights/object change, Reasoner, retry |
| 2:50–3:00 | Who it is for + repo URL |

- [ ] No third-party trademarks or copyrighted music
- [ ] Burn in subtitles if audio is noisy
- [ ] Upload unlisted, then public before submit

### 10.4 Devpost form

- [ ] Track: Physical AI
- [ ] Project description (problem, audience, how it works, stack)
- [ ] Public repo URL
- [ ] Video URL
- [ ] Demo URL: optional for this track; add UI recording if we host nothing
- [ ] Feedback on Token Factory, AI Cloud, and NVIDIA tools (required)
- [ ] Tavily: describe the runtime call so we remain eligible for the bonus
- [ ] Submit **at least 12 hours before** 10:00 am PDT Oct 30; do not use the last hour for first upload

### 10.5 Post-submit (does not block judging)

- [ ] Keep the repo public and the robot available if Sponsor requests physical access
- [ ] Do not silently swap the judged commit; further work goes on a different branch/tag

### Phase 5 exit criteria

Devpost shows a **complete** submission: repo, license, README, video, feedback. Clock is before the deadline.

---

## 11. Repository workstream (parallel to phases)

These are always in progress; they do not get their own week.

| Workstream | Rule |
| --- | --- |
| **Commits** | Small, named after the phase (`feat(factory): cosmos job wrapper`). Main stays releasable |
| **Call-site log** | Every new NVIDIA/Nebius/Tavily integration is a row in `docs/HACKATHON.md` |
| **Tests** | Schema, agent tool routing, and Job payload tests do not need a robot. Hardware tests are manual checklists |
| **Safety** | No policy run without a human in reach of power. Log every metal trial |
| **Credits** | Weekly remaining-credit note in `docs/HACKATHON.md` starting Phase 0 |

---

## 12. Hardware fallback

Trigger on **October 4** if the SO-101 pair is not in hand.

| Priority | Fallback | What we keep | What we lose |
| --- | --- | --- | --- |
| 1 | Any 6-DOF arm we can already borrow + two webcams | GR00T `NEW_EMBODIMENT` story | Official SO-101 example smoothness |
| 2 | Wheeled base + cheap gripper (fetch / bin) | Sense-and-act video, Nemotron + Reasoner | Weak GR00T embodiment story |
| 3 | Camera + relay/estop on a real machine (printer, mill) | Sense-and-act, easy hardware | Weaker “robot,” still valid Physical AI |
| 4 | Isaac-only + public SO-101 datasets | Factory + GR00T in sim | Design/Impact hit; rules allow “modules in action” — last resort |

Fallback 4 still uses Token Factory + Jobs so Stage 1 can pass. It is a worse Grand Prize bet. Decide in writing in this file the day it happens.

---

## 13. Risks and default mitigations

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Arm ships late | High | Order on Day 1; §8 on Oct 4; keep shooting any metal we have |
| GR00T fine-tune does not transfer | High | Scripted/teleop clip already in the can; ship critic + factory + honest success rate; one lucky policy take is enough for the video if logged |
| Cosmos SDG burns credits | Medium | Cap waves; Reasoner filter; prefer Transfer-from-real-video over unlimited text-to-world |
| Isaac Sim GPU mismatch (no RT cores) | Medium | Schedule sim on L40S / RTX PRO; document in Job configs |
| Scope creep (second skill, humanoid, pretty UI) | High | Skill 1 only. SONIC and skill 2 are stretch after Phase 4 exit |
| Token Factory model ID drift | Medium | Pin IDs in `.env.example`; hello scripts in CI |
| Video fails the 60 s hardware rule | High if delayed | Capture in Phase 1 regardless of policy quality |
| Secrets in git | Medium | `.gitignore`, `gitleaks` or `git log -p` scan in Phase 5 |
| Solo bottleneck | Medium | Phase 0–2 can be almost fully software; do not block software on hardware except the clip |

---

## 14. Definition of done for the hackathon

Apprentice is done when all of the following are true:

1. **Problem:** README states the skill-scarcity problem and a named user.
2. **Metal:** ≥60 seconds of the real robot operating in the submitted video.
3. **Nebius:** At least one Token Factory runtime path **and** at least one AI Cloud Job or Endpoint, both evidenced in README.
4. **NVIDIA:** Nemotron, Cosmos Reasoner, and GR00T each have a call site. Cosmos Predict/Transfer used in the factory unless credits make it impossible (then document the miss).
5. **Tavily:** One functional runtime call during skill compilation, logged.
6. **Product:** Teach → compile/eval → run is usable without a Jupyter notebook.
7. **Honesty:** SONIC, if shown, is labeled sim. Failure cases are shown, not hidden.
8. **Submission:** Devpost complete, repo public, license visible, feedback submitted.

---

## 15. Immediate next actions (this week)

1. Order the SO-101 pair and cameras.
2. Create Token Factory, AI Cloud, Tavily, and Hugging Face credentials.
3. Land the Phase 0 repo skeleton and hello-world scripts on this repository.
4. Write `docs/HACKATHON.md` with the first two successful API call IDs.
5. Do not start UI polish, SONIC, or a second skill.

When Phase 0 exit criteria are checked off, move to Phase 1 without replanning.
