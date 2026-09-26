# Architecture

Apprentice is a skill compiler. The body is swappable. **Right now the body is a CPU tabletop simulator.** The real SO-101 plugs into the same skill card later.

```
TEACH                                 FACTORY                               RUN
────────────────                      ────────────────                      ─────────────
Sim expert (now)                      Domain-random eval (now)              Scripted expert (now)
SO-101 teleop (later)                 Cosmos + Isaac Jobs (later)           GR00T (later)
        │                                     │                                     │
        ▼                                     ▼                                     ▼
Skill card (Nemotron / default)       Randomized layouts + lighting         Geometric critic (now)
LeRobot-shaped episode                Factory summary.json                  Cosmos Reasoner (optional)
```

Three NVIDIA families, three jobs — the sim loop is where they get wired before metal:

| Role | Model | Platform | Code | Sim now |
| --- | --- | --- | --- | --- |
| Think | Nemotron | Token Factory | `apprentice.agent` | optional (`compile-skill`) |
| See | Cosmos 3 Super Reasoner | Token Factory | `apprentice.critic` | optional (`sim loop --cosmos`) |
| Do | GR00T N1.7 later; scripted expert now | AI Cloud later | `apprentice.policy` / `apprentice.sim.expert` | yes |
| Multiply data | Cosmos later; layout RNG now | Serverless Jobs later | `apprentice.factory` | `sim factory` |
| Body | TabletopSim now; SO-101 later | CPU / LeRobot | `apprentice.sim` / `apprentice.robot` | yes |

The **skill card** (`apprentice.skill.SkillSpec`) is the contract. Do not change the schema without updating factory and runtime together.

## What exists now

- Token Factory client and hello-world CLIs
- Skill card schema + Nemotron compiler
- CPU Skill 1 sim: demo, eval, factory, closed loop
- Geometric critic + optional Cosmos on sim frames
- SO-101 bring-up CLI (parked until sim is green)

## What is next, in order

1. Sim loop metrics + optional live Token Factory on sim frames
2. Isaac Lab / Cosmos Jobs on Nebius (photoreal factory)
3. GR00T on sim datasets
4. Hardware: IDs, calibrate, teleop, 60-second clip
5. Teach UI, Tavily, recovery product

See [SIMULATION.md](SIMULATION.md), [ROADMAP.md](../ROADMAP.md), [HARDWARE.md](HARDWARE.md).
