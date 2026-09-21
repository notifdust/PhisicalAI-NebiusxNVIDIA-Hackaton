# Architecture

Apprentice is a skill compiler. The SO-101 is the body that proves the compiler works.

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

Three NVIDIA families, three jobs:

| Role | Model | Platform | Code |
| --- | --- | --- | --- |
| Think | Nemotron | Token Factory | `apprentice.agent` |
| See | Cosmos 3 Super Reasoner | Token Factory | `apprentice.critic` |
| Do | GR00T N1.7 (Phase 3) | AI Cloud Endpoint or local GPU | `apprentice.policy` |
| Multiply data | Cosmos Predict/Transfer (Phase 2) | Serverless Jobs / Workbench | `apprentice.factory` |
| Body | SO-101 | LeRobot | `apprentice.robot` |

The **skill card** (`apprentice.skill.SkillSpec`) is the contract between those layers. Do not change the schema without updating factory and runtime together.

## What exists now (Phase 0 + metal bring-up)

- Token Factory client and hello-world CLIs
- Skill card schema + Nemotron compiler
- Cosmos Reasoner scene describe / critique (needs a still image)
- SO-101 command printer, motor ID map, waypoint replay that refuses dummy zeros

## What does not exist yet

- Serverless Jobs / Workbench YAML (Phase 2)
- GR00T fine-tune and action client (Phase 3)
- Teach UI, Tavily in the loop, recovery product (Phase 4)

See [ROADMAP.md](../ROADMAP.md) and [HARDWARE.md](HARDWARE.md).
