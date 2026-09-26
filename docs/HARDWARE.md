# Hardware bring-up — SO-101

**Deferred.** Finish the CPU sim loop in [SIMULATION.md](SIMULATION.md) before assembling the bus. Printed parts and motors can wait on the shelf. When we come back here: **set unique motor IDs before daisy-chaining.**


Official assembly reference: [LeRobot SO-101](https://huggingface.co/docs/lerobot/en/so101). This file is the Apprentice-specific checklist: Skill 1, ports, cameras, safety, and the commands this repo prints for you.

## What you should have on the table

| Item | Notes |
| --- | --- |
| 3D-printed SO-101 parts, support material removed | Follower gripper **and** leader handle if you printed both |
| 12× Feetech STS3215 (leader + follower) | See gearing table. **Do not mix 7.4 V and 12 V on the wrong supply** |
| 2× bus servo adapter (Waveshare / BusLinker) | USB + separate DC power. USB does **not** power the motors |
| 3-pin servo cables | One per motor, plus daisy-chain jumpers |
| 5 V supply for 7.4 V motors, 12 V supply for 12 V motors | Leader is usually 7.4 V. Wrong voltage burns servos |
| 2× USB cameras | Front (table) + wrist. 640×480 @ 30 fps is the baseline |
| Laptop with Linux or macOS | `pip install -e '.[robot]'` after the Python package |
| Two bowls / bins + a distinct block | Skill 1: `put the block in the blue bowl` |
| Clamp or heavy base | The arm will walk the table if the base is free |

Fill `docs/HARDWARE.md` (this file) with **your** ports after `apprentice robot find-port`. Record them in `.env` as well.

### Local log (fill in)

```
Follower port:
Follower id: apprentice_follower
Leader port:
Leader id: apprentice_leader
Front camera index:
Wrist camera index:
Power: follower ___ V / leader ___ V
Calibration date:
```

## Motor map

LeRobot and GR00T both expect this ID map. `apprentice robot ids` prints it.

| Joint | ID | Follower gear | Leader gear |
| --- | --- | --- | --- |
| shoulder_pan | 1 | 1/345 | 1/191 |
| shoulder_lift | 2 | 1/345 | 1/345 |
| elbow_flex | 3 | 1/345 | 1/191 |
| wrist_flex | 4 | 1/345 | 1/147 |
| wrist_roll | 5 | 1/345 | 1/147 |
| gripper | 6 | 1/345 | 1/147 |

Label each motor **before** you lose them in a pile: `F1`…`F6`, `L1`…`L6`.

## 0. Software on the robot laptop

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[robot,dev]"
cp .env.example .env
# put Token Factory key in .env when you have it; robot bring-up does not need it
```

LeRobot also wants the Feetech extra from its own tree if `pip install lerobot` is not enough:

```bash
pip install 'lerobot[feetech]'
```

## 1. Find the USB port (one bus at a time)

Power the adapter **and** plug USB. Then:

```bash
apprentice robot find-port
```

Unplug the adapter when asked. Write the path into `.env`:

```
SO101_FOLLOWER_PORT=/dev/ttyACM0   # Linux; macOS looks like /dev/tty.usbmodem…
SO101_LEADER_PORT=/dev/ttyACM1
```

On Linux, your user must be in `dialout` (then log out/in):

```bash
sudo usermod -aG dialout "$USER"
```

Waveshare boards: USB jumpers on the **B** channel.

## 2. Set motor IDs — one motor on the board

This is the step people skip. Do it **before** assembly daisy-chains.

```bash
apprentice robot setup-motors --arm follower
```

The script asks you to connect **only** the motor it names, starting at **gripper (id 6)** and ending at **shoulder_pan (id 1)**. The motor must not be chained to any other motor.

Then the leader:

```bash
apprentice robot setup-motors --arm leader
```

If a write fails: power, USB, 3-pin polarity, and “only one motor on the bus.”

After IDs are set, daisy-chain **shoulder_pan → … → gripper** and plug shoulder_pan into the adapter. Mount the adapter on the base.

## 3. Assemble

Follow the official joint-by-joint steps (horns, M2 motor screws, M3 structure screws). Summary:

1. Joint 1 (base pan) in the base, horns, shoulder.
2. Joint 2 (shoulder lift) from the top, upper arm.
3. Joint 3 (elbow), forearm.
4. Joint 4 (wrist flex).
5. Joint 5 (wrist roll) — **one** horn on this motor.
6. Gripper (follower) or handle (leader).

Route cables through the printed guides so motion cannot yank a connector. Leave enough slack at wrist roll.

## 4. Calibrate

Put every joint roughly in the **middle of its range**. Then:

```bash
apprentice robot calibrate --arm follower
apprentice robot calibrate --arm leader
```

Sweep each joint through its full range when the script asks. Use the **same** `--robot.id` / `--teleop.id` forever (`apprentice_follower` / `apprentice_leader` in `.env`). That is how LeRobot finds the calibration files.

## 5. Cameras

```bash
apprentice robot cameras
```

Set `SO101_FRONT_CAM` and `SO101_WRIST_CAM` in `.env`. Front should see the whole table + both bowls. Wrist should see the gripper fingers and the object in the last 10 cm of a grasp.

## 6. Teleop (this is “the robot is alive”)

Clear the sweep volume. Keep a hand on the DC plug — that is the e-stop.

```bash
apprentice robot teleop
```

Leader motion should match the follower. If the follower fights you, recalibrate or check a motor ID collision.

## 7. Record Skill 1

Canonical language, do not improvise per episode:

```
put the block in the blue bowl
```

```bash
apprentice robot record --episodes 5
```

Roadmap minimum is 5 clean episodes; 20 is better. Hold out 2 for eval — never train on them.

Keys (LeRobot): save episode, retry, Esc to stop. Log which episode IDs are gold vs junk.

## 8. Scripted baseline (60-second video is not blocked on GR00T)

Replay of a **learned** policy is Phase 3. For Phase 1 we want metal moving on camera even if learning is not ready.

1. Teleop to a pose, then:
   ```bash
   apprentice robot capture-pose --name hover_object
   ```
2. Paste the JSON into `configs/skill1_waypoints.json` (gitignored). Start from `configs/skill1_waypoints.example.json`.
3. Capture `home`, `hover_object`, `grasp`, `hover_bowl`, `release`.
4. Dry-run, then live:
   ```bash
   apprentice robot replay --dry-run
   apprentice robot replay
   ```

`replay` **refuses** the all-zero example file so we cannot command a parked arm with dummy numbers.

Shoot a **continuous 70–90 s** take of teleop or waypoint replay. No jump cuts, no copyrighted music. Archive the raw file under `data/` (gitignored).

## Safety

- No people in the sweep during policy or replay.
- Power-plug e-stop. Do not rely on Ctrl+C.
- Table edge / monitor / coffee are out of reach, or the arm will find them.
- If a servo is hot or buzzing at rest, power down and check calibration / ID clash.

## Print the whole command list

```bash
apprentice robot print
```

Uses whatever ports and camera indices are in `.env`.
