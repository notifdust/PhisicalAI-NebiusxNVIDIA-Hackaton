# Simulation (do this first)

Hardware is deferred. The same skill, skill card, cameras, and joint names run in a CPU tabletop simulator so we can finish teach → factory → run before touching the SO-101 bus.

**Backend today:** `apprentice.sim.TabletopSim` (analytic IK + contact grasp + PIL cameras).  
**Backend later:** real SO-101 via LeRobot, then Isaac Lab on Nebius for photoreal eval. Swap the body, keep the skill card.

Skill 1 is unchanged: `put the block in the blue bowl`.

## Why a dev sim, not Isaac Lab, right now

Isaac Lab / Isaac Sim need RT-core GPUs and a long bring-up. The compiler loop does not. This simulator exists so we can:

- record demonstrations
- score success automatically
- domain-randomize layout and lighting (factory stand-in)
- feed front/wrist frames to Cosmos Reasoner when a Token Factory key exists
- keep GR00T’s joint names (`shoulder_pan` … `gripper`)

Photoreal Cosmos / Isaac jobs come after this loop is green.

## Commands

No robot, no API key:

```bash
pip install -e ".[dev]"

apprentice sim demo --episodes 5
apprentice sim eval --episodes 20
apprentice sim factory --episodes 20
apprentice sim loop --episodes 5
```

Outputs land under `data/sim/` (gitignored). `loop` writes `report.json` plus key frames (`front_*.jpg`, `wrist_*.jpg`) per episode.

Optional, with `NEBIUS_API_KEY`:

```bash
apprentice sim loop --episodes 3 --cosmos
```

That sends the last front frame of each episode to **Cosmos 3 Super Reasoner** on Token Factory. Geometric success is still the ground-truth label.

`--miss-every N` injects a too-high grasp so the critic has a failure class (`grasp_missed`). Use it to test recovery logic without waiting for a flaky policy.

## What “success” means

The block’s XY is inside the bowl radius, the gripper is open, the block is on the table. That is the same criterion the geometric critic reports and the same one Skill 1’s `success` list is about.

The scripted expert is a stand-in for GR00T. It is not the product. It exists so the rest of the stack has a reliable body.

## Mapping onto the three timescales

| Stage | In sim now | Later on metal / Nebius |
| --- | --- | --- |
| Teach | `sim demo` records expert episodes | LeRobot teleop on SO-101 |
| Factory | `sim factory` randomizes pose/lighting | Cosmos Predict/Transfer + Isaac Lab Jobs |
| Run | `sim loop` + scripted expert + geometric critic | GR00T + Cosmos Reasoner + Nemotron |

## Hardware is not cancelled

When the sim loop is stable: motor IDs, calibrate, teleop, 60-second clip. See [HARDWARE.md](HARDWARE.md). Do not daisy-chain servos until IDs are unique.
