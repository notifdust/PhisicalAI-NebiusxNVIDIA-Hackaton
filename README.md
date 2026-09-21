# Apprentice

A physical-AI **skill compiler** for the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) (Physical AI track).

A person demonstrates a tabletop job once. Apprentice turns that demonstration into a robot skill that still works when lighting, layout, or object pose change — and that can recover when the first attempt fails.

The product is the compiler (demo → skill). The arm is the proof.

**First skill:** `put the block in the blue bowl`  
**Body:** Hugging Face SO-101 leader / follower  
**Deadline:** October 30, 2026, 10:00 am PDT

## Status

Phase 0 software is in this repo. Printed SO-101 parts and motors are in hand — start with motor IDs **before** daisy-chaining.

| Doc | What it is |
| --- | --- |
| [ROADMAP.md](./ROADMAP.md) | Build contract |
| [docs/HARDWARE.md](./docs/HARDWARE.md) | Assemble, ID, calibrate, teleop, record |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Teach / factory / run |
| [docs/HACKATHON.md](./docs/HACKATHON.md) | NVIDIA / Nebius call-site log |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

On the laptop that talks to the arm, also install LeRobot:

```bash
pip install -e ".[robot]"
# if extras are incomplete:
pip install 'lerobot[feetech]'
```

## Token Factory (no robot)

Put a Nebius Token Factory key in `.env` as `NEBIUS_API_KEY`.

```bash
apprentice hello-nemotron
apprentice hello-reasoner              # synthetic table image
apprentice hello-reasoner --image shot.jpg
apprentice compile-skill --text "pick the red block into the blue bowl"
```

Equivalent scripts (ROADMAP names): `scripts/hello_token_factory.py`, `scripts/hello_cosmos_reasoner.py`.

These are the first runtime calls to **Nebius Token Factory** using **NVIDIA Nemotron** and **NVIDIA Cosmos 3 Super Reasoner**.

## SO-101 (robot laptop)

**Do this first:** new motors share id `1`. Set unique IDs with only one motor on the bus.

```bash
apprentice robot ids                 # assignment order
apprentice robot find-port
# write ports into .env
apprentice robot setup-motors --arm follower
apprentice robot setup-motors --arm leader
apprentice robot calibrate --arm follower
apprentice robot calibrate --arm leader
apprentice robot cameras
apprentice robot teleop
apprentice robot record --episodes 5
```

Print every command with current `.env` values:

```bash
apprentice robot print
```

Scripted baseline (for the 60-second hardware clip, no GR00T yet):

```bash
apprentice robot capture-pose --name hover_object
# paste JSON into configs/skill1_waypoints.json
apprentice robot replay --dry-run
apprentice robot replay
```

Replay refuses the all-zero example file on purpose.

Full sequence and safety: [docs/HARDWARE.md](./docs/HARDWARE.md).

## Stack

| Layer | Platform | In repo now |
| --- | --- | --- |
| Agent runtime | NVIDIA Nemotron on [Token Factory](https://tokenfactory.nebius.com/) | yes |
| Physical critic | NVIDIA Cosmos 3 Super Reasoner on Token Factory | yes |
| Body / data | SO-101 + LeRobot | bring-up CLI |
| Synthetic data | Cosmos Predict/Transfer on Serverless Jobs / [Workbench](https://github.com/nebius/nebius-physical-ai) | Phase 2 |
| Simulation | NVIDIA Isaac Lab | Phase 2 |
| Motor skill | NVIDIA Isaac GR00T N1.7 | Phase 3 |
| Procedure facts | [Tavily](https://www.tavily.com/) | Phase 4 |

## Tests

```bash
pytest -q
```

## License

MIT. Required so GitHub detects an OSI license for judging.
