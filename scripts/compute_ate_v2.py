import csv
import math
import numpy as np

def rot_to_quat(R):
    trace = R[0][0] + R[1][1] + R[2][2]
    if trace > 0:
        s = 0.5 / math.sqrt(trace + 1.0)
        w = 0.25 / s
        x = (R[2][1] - R[1][2]) * s
        y = (R[0][2] - R[2][0]) * s
        z = (R[1][0] - R[0][1]) * s
    elif R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = 2.0 * math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2])
        w = (R[2][1] - R[1][2]) / s
        x = 0.25 * s
        y = (R[0][1] + R[1][0]) / s
        z = (R[0][2] + R[2][0]) / s
    elif R[1][1] > R[2][2]:
        s = 2.0 * math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2])
        w = (R[0][2] - R[2][0]) / s
        x = (R[0][1] + R[1][0]) / s
        y = 0.25 * s
        z = (R[1][2] + R[2][1]) / s
    else:
        s = 2.0 * math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1])
        w = (R[1][0] - R[0][1]) / s
        x = (R[0][2] + R[2][0]) / s
        y = (R[1][2] + R[2][1]) / s
        z = 0.25 * s
    return x, y, z, w

# ── Load ground truth ──────────────────────────────────────────────────────
print("Loading ground truth...")
gt_rows = []
with open('/home/hannan/mulran_ws/global_pose.csv', 'r') as f:
    for line in f:
        cols = line.strip().split(',')
        if len(cols) < 13:
            continue
        ts_ns = int(cols[0])
        ts_s  = ts_ns / 1e9
        R = [
            [float(cols[1]), float(cols[2]),  float(cols[3])],
            [float(cols[5]), float(cols[6]),  float(cols[7])],
            [float(cols[9]), float(cols[10]), float(cols[11])]
        ]
        tx, ty, tz = float(cols[4]), float(cols[8]), float(cols[12])
        qx, qy, qz, qw = rot_to_quat(R)
        gt_rows.append([ts_s, tx, ty, tz, qx, qy, qz, qw])

# Subtract origin so GT starts near zero
origin_x = gt_rows[0][1]
origin_y = gt_rows[0][2]
origin_z = gt_rows[0][3]
print(f"GT UTM origin: ({origin_x:.2f}, {origin_y:.2f}, {origin_z:.2f})")

for r in gt_rows:
    r[1] -= origin_x
    r[2] -= origin_y
    r[3] -= origin_z

# Filter GT to overlap window only
est_start_ts = 1561000467.096
est_end_ts   = 1561000981.088
gt_filtered = [r for r in gt_rows if est_start_ts <= r[0] <= est_end_ts]
print(f"GT poses in overlap window: {len(gt_filtered)}")

with open('/home/hannan/mulran_ws/gt_tum_v2.txt', 'w') as f:
    for r in gt_filtered:
        f.write(f"{r[0]:.9f} {r[1]:.6f} {r[2]:.6f} {r[3]:.6f} {r[4]:.9f} {r[5]:.9f} {r[6]:.9f} {r[7]:.9f}\n")

print(f"GT written to gt_tum_v2.txt")

# ── Load estimated trajectory ──────────────────────────────────────────────
print("Loading estimated trajectory...")
est_rows = []
with open('/home/hannan/mulran_ws/fastlio_traj.txt', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 12:
            continue
        ts_ns = float(row[0])
        ts_s  = ts_ns / 1e9
        tx, ty, tz = float(row[5]), float(row[6]), float(row[7])
        qx, qy, qz, qw = float(row[8]), float(row[9]), float(row[10]), float(row[11])
        est_rows.append((ts_s, tx, ty, tz, qx, qy, qz, qw))

with open('/home/hannan/mulran_ws/est_tum_v2.txt', 'w') as f:
    for r in est_rows:
        f.write(f"{r[0]:.9f} {r[1]:.6f} {r[2]:.6f} {r[3]:.6f} {r[4]:.9f} {r[5]:.9f} {r[6]:.9f} {r[7]:.9f}\n")

print(f"Est written to est_tum_v2.txt ({len(est_rows)} poses)")
print("\nNow run evo with v2 files.")
