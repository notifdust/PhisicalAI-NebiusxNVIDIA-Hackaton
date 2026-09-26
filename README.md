# Apprentice

A physical-AI **skill compiler** for the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) (Physical AI track).

A person demonstrates a tabletop job once. Apprentice turns that demonstration into a robot skill that still works when lighting, layout, or object pose change — and that can recover when the first attempt fails.

The product is the compiler (demo → skill). The arm is the proof — **after** the loop works in simulation.

**First skill:** `put the block in the blue bowl`  
**Body now:** CPU tabletop sim (`apprentice sim`)  
**Body later:** Hugging Face SO-101  
**Deadline:** October 30, 2026, 10:00 am PDT

## Status

**Sim-first.** Hardware is parked. Run the compiler loop on the CPU simulator; plug in the SO-101 when that loop is green.

| Doc | What it is |
| --- | --- |
| [ROADMAP.md](./ROADMAP.md) | Build contract |
| [docs/SIMULATION.md](./docs/SIMULATION.md) | CPU sim: demo, eval, factory, loop |
| [docs/HARDWARE.md](./docs/HARDWARE.md) | Deferred SO-101 bring-up |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Teach / factory / run |
| [docs/HACKATHON.md](./docs/HACKATHON.md) | NVIDIA / Nebius call-site log |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

## Simulation (no robot)

```bash
apprentice sim demo --episodes 5
apprentice sim eval --episodes 20
apprentice sim factory --episodes 20
apprentice sim loop --episodes 5
```

`sim loop` writes a skill-card report plus front/wrist frames. Add `--cosmos` when `NEBIUS_API_KEY` is set to send frames to Cosmos 3 Super Reasoner.

Details: [docs/SIMULATION.md](./docs/SIMULATION.md).

## Token Factory (optional for sim)

```bash
apprentice hello-nemotron
apprentice hello-reasoner
apprentice compile-skill --text "pick the red block into the blue bowl"
apprentice sim loop --episodes 3 --cosmos
```

## SO-101 (later)

Do not assemble the bus yet. When we come back: unique motor IDs **one servo at a time**, then [docs/HARDWARE.md](./docs/HARDWARE.md).

```bash
apprentice robot print
```

## Stack

| Layer | Platform | In repo now |
| --- | --- | --- |
| Body (dev) | CPU tabletop sim | `apprentice sim` |
| Agent runtime | NVIDIA Nemotron on [Token Factory](https://tokenfactory.nebius.com/) | yes |
| Physical critic | Geometric (always) + Cosmos Reasoner (optional) | yes |
| Factory stand-in | Domain-randomized sim eval | `apprentice sim factory` |
| Photoreal factory | Cosmos Predict/Transfer + Isaac Lab on Nebius | next |
| Motor skill | Scripted expert now; GR00T N1.7 later | expert yes |
| Real body | SO-101 + LeRobot | CLI parked |
| Procedure facts | [Tavily](https://www.tavily.com/) | Phase 4 |

## Tests

```bash
pytest -q
```

## License

MIT. Required so GitHub detects an OSI license for judging.
