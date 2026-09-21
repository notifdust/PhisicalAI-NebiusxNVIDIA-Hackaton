# Apprentice

A physical-AI **skill compiler** for the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) (Physical AI track).

A person demonstrates a tabletop job once. Apprentice turns that demonstration into a robot skill that still works when lighting, layout, or object pose change — and that can recover when the first attempt fails.

The product is the compiler (demo → skill). The arm is the proof.

## Status

Roadmap is the build contract. Implementation follows it phase by phase.

**→ [ROADMAP.md](./ROADMAP.md)**

- **Deadline:** October 30, 2026, 10:00 am PDT
- **Current phase:** 0 — Foundations (accounts, repo skeleton, Token Factory hello-world)
- **First skill:** pick a visible object and place it in the correct bowl or bin
- **Intended body:** Hugging Face SO-101 leader/follower arm

## Stack (planned)

| Layer | Platform |
| --- | --- |
| Agent runtime | NVIDIA Nemotron on [Nebius Token Factory](https://tokenfactory.nebius.com/) |
| Physical critic | NVIDIA Cosmos 3 Super Reasoner on Token Factory |
| Synthetic data | NVIDIA Cosmos Predict/Transfer on Nebius Serverless Jobs / [Physical AI Workbench](https://github.com/nebius/nebius-physical-ai) |
| Simulation | NVIDIA Isaac Lab on Nebius AI Cloud |
| Motor skill | NVIDIA Isaac GR00T N1.7, SO-101 as `NEW_EMBODIMENT` |
| Procedure/safety facts | [Tavily](https://www.tavily.com/) at skill-compilation time |

Do not add a dependency that does not sit on the diagram in the roadmap.

## Repo

This repository is starting from the roadmap. Phase 0 lands the package layout, license, and hello-world inference scripts. Until then, treat [ROADMAP.md](./ROADMAP.md) as the spec.

## License

MIT license will be added in Phase 0 so GitHub can detect an OSI license for judging.
