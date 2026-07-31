# FAST-LIO2 Reproduction on MulRan KAIST01

Reproduction and extension of **FAST-LIO2** (Xu et al., 2022) on the **MulRan KAIST01** sequence, done as a Mobile Robotics semester project. This repo contains our modified configuration, data-processing/evaluation scripts, and results. It is built on top of the official [FAST-LIO2 repository](https://github.com/hku-mars/FAST_LIO) — see setup instructions below.

## Original Paper
Xu, W., Cai, Y., He, D., Lin, J., & Zhang, F. (2022). *FAST-LIO2: Fast Direct LiDAR-Inertial Odometry.* IEEE Transactions on Robotics.
Original implementation: https://github.com/hku-mars/FAST_LIO

## Dataset
MulRan KAIST01 sequence (Ouster OS1-64 LiDAR + Xsens IMU + GPS + global pose ground truth).
Official dataset: https://sites.google.com/view/mulran-dataset
Raw sequence files + demo video for this project: [Google Drive](https://drive.google.com/drive/u/2/folders/1LsI10ViQvEp_rg95Bd9y8yeNyG7NBVK3)

## Repository Structure
```
config/       Modified FAST-LIO2 config for the Ouster sensor on KAIST01
launch/       ROS launch file for running FAST-LIO2 on KAIST01
scripts/      Data conversion, dropout-robustness bag generation, trajectory extraction, ATE evaluation, plotting
results/
  trajectories/     Estimated and ground-truth trajectories (TUM format)
  ate_evaluation/   evo ATE results (clean run + 10/30/50/70% LiDAR dropout robustness tests)
  figures/          Dropout robustness plots
docs/         Final IEEE paper (added on submission)
```

## Installation

1. **Install ROS Noetic** (Ubuntu 20.04) and standard FAST-LIO2 dependencies: PCL, Eigen, Ceres Solver, livox_ros_driver. See the [original FAST-LIO2 README](https://github.com/hku-mars/FAST_LIO#1-prerequisites) for exact versions.

2. **Clone FAST-LIO2 upstream** into a catkin workspace:
   ```bash
   mkdir -p ~/catkin_ws/src && cd ~/catkin_ws/src
   git clone https://github.com/hku-mars/FAST_LIO.git
   cd FAST_LIO && git submodule update --init
   ```

3. **Clone this repo** and copy our modified config/launch files over:
   ```bash
   git clone https://github.com/Hannan7-5/fast-lio2-mulran-kaist01.git
   cp fast-lio2-mulran-kaist01/config/kaist01.yaml ~/catkin_ws/src/FAST_LIO/config/
   cp fast-lio2-mulran-kaist01/launch/mapping_kaist01.launch ~/catkin_ws/src/FAST_LIO/launch/
   ```

4. **Build**:
   ```bash
   cd ~/catkin_ws && catkin_make
   source devel/setup.bash
   ```

## Data Preparation

1. Download the KAIST01 sequence from the [Drive link above](https://drive.google.com/drive/u/2/folders/1LsI10ViQvEp_rg95Bd9y8yeNyG7NBVK3) (or the official MulRan site) — you need `data_stamp.csv`, `global_pose.csv`, `xsens_imu.csv`, and the Ouster point cloud archive.
2. Extract everything into a working folder, e.g. `~/mulran_ws/`.
3. Convert the raw data into a ROS bag:
   ```bash
   python3 scripts/convert_to_bag_v3.py
   ```
   This reads timestamps/IMU/LiDAR data and writes a `.bag` file playable by FAST-LIO2.

## Running FAST-LIO2

```bash
roslaunch fast_lio mapping_kaist01.launch
```
In a separate terminal, play the converted bag:
```bash
rosbag play ~/mulran_ws/KAIST01.bag
```

## Extracting and Evaluating Trajectories

```bash
python3 scripts/extract_traj_v6.py      # extracts estimated trajectory in TUM format
python3 scripts/compute_ate_v2.py       # aligns with ground truth, writes TUM files for evo
```
Then run `evo` (https://github.com/MichaelGrupp/evo) on the resulting ground-truth/estimate TUM files for ATE metrics, or use:
```bash
python3 scripts/plot_evo_results.py
```

## Extension: LiDAR Dropout Robustness

To test robustness under degraded sensing, we simulate LiDAR point dropout (10/30/50/70%) and re-run the pipeline:
```bash
python3 scripts/make_dropout_bag.py
```
Results per dropout level are in `results/ate_evaluation/dropout{10,30,50,70}/`, with summary plots in `results/figures/`.

## Configuration Changes from Stock FAST-LIO2

We enabled online IMU-LiDAR extrinsic estimation (`extrinsic_est_en: true`) rather than using stock fixed extrinsics, since precise IMU-LiDAR calibration for the KAIST01 rig was not directly available to us.

## Known Limitations

The current ATE evaluation shows a large error magnitude relative to expectations, likely due to a scale/alignment issue in the trajectory-to-ground-truth registration that we are still refining. Numbers in `results/ate_evaluation/` should be treated as preliminary pending further validation. This is documented as an open item in the accompanying paper.

## Demo Video

See the [Google Drive folder](https://drive.google.com/drive/u/2/folders/1LsI10ViQvEp_rg95Bd9y8yeNyG7NBVK3) for the recorded demonstration (pipeline walkthrough, execution, and results).

## Authors

Hannan — MS Mechatronics Engineering, UET Lahore. Mobile Robotics semester project.
