# End-to-End Self-Driving Agent (CARLA)

An end-to-end learning pipeline that drives a vehicle in the [CARLA](https://carla.org/) simulator from raw camera input alone — no explicit lane detection, sign detection, or rule-based planning. A CNN maps a single front-facing camera frame directly to **throttle**, **steer**, and **brake** commands, trained via behavioral cloning on an autopilot "expert" driver.

**AIM:** Given a destination, get there without collisions, learning the driving policy purely from pixels.

> Demo video: https://youtu.be/qu6lK62JuP4

## Highlights

- **Behavioral cloning at scale** — collected 500k+ image/control samples by driving CARLA's built-in autopilot across multiple towns and weather conditions.
- **Custom expert agent** ([carla_route_finder](carla_route_finder)) — a modified autopilot that ignores traffic *signals* but correctly reacts to stop and speed-limit *signs*, with randomized routing at intersections so the dataset isn't biased toward one path.
- **Emergent sign-following behavior** — the trained network was never given sign labels, yet learned to slow/stop at stop signs and adjust speed at speed-limit signs, purely from correlating visual cues in the image with the expert's control outputs.
- **Inception-based CNN** — a simplified GoogLeNet-style architecture (stacked Inception blocks + standard conv blocks, batch norm, and dropout) chosen specifically because multi-scale filters are better at picking up small, localized visual cues like signage.
- **Reusable data-collection module** — sensor and waypoint capture is decoupled enough to plug in additional sensors (RGB, semantic segmentation, waypoints already supported) for future experiments.

## Pipeline

```
Carla Autopilot  →  Data Collection  →  Preprocessing/Balancing  →  CNN Training  →  Closed-loop Inference
   (expert)          (image+control)      (flip/augment)            (Inception)        (live control)
```

### 1. Collecting Data
[`auto_pilot.py`](auto_pilot.py) / [`autopilot_data_collect.py`](autopilot_data_collect.py) spawn the ego vehicle, attach RGB (and optionally semantic segmentation) cameras, hand control to CARLA's autopilot/traffic manager, and log `(image, controls)` pairs — optionally with the next 5 route waypoints for future trajectory-following work.

### 2. Preprocessing
Raw driving is heavily imbalanced — most frames are "go straight." [`preprocess.py`](preprocess.py) rebalances the dataset by downsampling the center/straight class and synthesizing extra left/right turn samples by horizontally flipping images and negating the steer label, then shuffles and splits into train/test sets (85/15).

### 3. Network Architecture
[`model_architecture.py`](model_architecture.py) implements the CNN:

| Stage | Detail |
|---|---|
| Stem | Conv 7x7 (64) → BN → MaxPool, Conv 3x3 (192) → BN → MaxPool → Dropout 0.2 |
| Inception Block 1–3 | Parallel 1x1 / 3x3 / 5x5 / pooling branches, BN per branch → MaxPool → Dropout 0.3 each |
| Head | Flatten → Dense(256, elu) → Dropout 0.5 → Dense(32, elu) → Dropout 0.5 → Dense(3, linear) |

Output: `[throttle (0,1), steer (-1,1), brake (0,1)]`, regressed directly with MSE loss.

### 4. Training
[`train.py`](train.py) trains with `tf.GradientTape` and Adam, logging batch/epoch train and test loss to TensorBoard ([`tensorlogs`](config.py)). Trained on an i7-10th-gen / RTX 2070 (8GB) / 16GB RAM box for 35 epochs (~4 hours). Batch and epoch loss curves on both train and test sets show steady convergence with no overfitting, attributable to batch norm + dropout regularization across every layer.

### 5. Inference / Closed-loop Control
[`auto_run.py`](auto_run.py) and [`test.py`](test.py) feed live camera frames from the simulator through the trained model and apply the predicted controls back to the vehicle in real time.

## Results

- Smooth, stable straight-line driving with minimal oscillation.
- Reacts to stop signs and speed-limit signs despite never being explicitly trained to detect them — an emergent property credited to the Inception modules' multi-scale receptive fields.
- Occasionally stalls fully at a stop sign without resuming, and can hesitate at intersections when no clear route is implied by the image alone — both require a manual nudge in the demo video.

## Repo Layout

```
config.py                     # central config: image size, CARLA port/town, paths, hyperparams
auto_pilot.py                 # data collection driver (autopilot + waypoint capture)
autopilot_data_collect.py     # data collection driver (autopilot + RGB/semantic capture)
auto_run.py                   # closed-loop driving with the trained model
preprocess.py                 # dataset balancing, flip-augmentation, train/test split
model_architecture.py         # Inception-based CNN (TensorFlow/Keras)
train.py                      # training loop, TensorBoard logging, checkpointing
test.py                       # model evaluation / inference
load.py / utils.py            # data loading utilities, batch dispatch
lane_detection.py / cvstuff.py # classical CV experiments
view_sample.py                 # quick visualization of collected samples
carla_route_finder/            # global route planner, local planner, basic agent (CARLA navigation)
```

## Tech Stack

- **Simulator:** CARLA 0.9.9.4
- **ML:** TensorFlow / Keras, NumPy
- **CV:** OpenCV
- **Language:** Python 3.7

## Setup

### CARLA
1. Download CARLA for Windows from the [0.9.9 release](https://github.com/carla-simulator/carla/releases/tag/0.9.9) (0.9.9.4) and extract it.
2. Install the Python API globally: copy the egg from `CARLA_0.9.9.4\WindowsNoEditor\PythonAPI\carla\dist` into `C:\Users\%username%\AppData\Local\Programs\Python\Python37\Lib\site-packages` and extract it there (use `easy_install` on the egg if a plain extract doesn't register it).
3. Start the CARLA server:
   ```
   CarlaUE4.exe -ResX=320 -ResY=240 -carla-server -fps=10 -carla-world-port=7878 -quality-level=Low
   ```
   The port is configurable in [`config.py`](config.py) (`CARLA_PORT`) — change it on both ends if `7878` is unavailable.
4. More info: [CARLA docs](https://carla.readthedocs.io/en/latest/start_introduction/).

### Running remotely
A Colab-based CARLA setup is available here: [carla-colab](https://colab.research.google.com/github/MichaelBosello/carla-colab/blob/master/carla-simulator.ipynb).

### Usage
```bash
python autopilot_data_collect.py   # collect driving data via CARLA autopilot
python preprocess.py               # balance + split the dataset
python train.py                    # train the model
python auto_run.py                 # run the trained model in closed-loop control
```

## Next Steps

- Move beyond random intersection decisions toward true destination-conditioned navigation using the waypoint data already being collected.
- Add collision avoidance for other vehicles/pedestrians as a precursor to full waypoint-following.
- Resolve the "stuck at stop sign" and intersection-hesitation failure modes seen in closed-loop testing.

*Code for the next development phase is being developed privately while the project continues; this repo reflects the current milestone.*

## References

- Szegedy et al., 2014 — [Going Deeper with Convolutions](https://arxiv.org/abs/1409.4842) (Inception)
- Bojarski et al., 2016 — [End to End Learning for Self-Driving Cars](https://medium.com/swlh/behavioural-cloning-end-to-end-learning-for-self-driving-cars-50b959708e59)
- Chen, Li & Tomizuka, 2020 — Interpretable End-to-end Urban Autonomous Driving with Latent Deep Reinforcement Learning
- Chen, Zhou, Koltun & Krähenbühl, 2019 — Learning by Cheating
