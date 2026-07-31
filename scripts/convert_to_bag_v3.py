import os
import csv
import numpy as np
import rosbag
import rospy
from sensor_msgs.msg import PointCloud2, PointField, Imu
from std_msgs.msg import Header
from tqdm import tqdm

OUSTER_DIR = os.path.expanduser("~/mulran_ws/Ouster")
IMU_CSV    = os.path.expanduser("~/mulran_ws/xsens_imu.csv")
STAMP_CSV  = os.path.expanduser("~/mulran_ws/data_stamp.csv")
OUTPUT_BAG = os.path.expanduser("~/mulran_ws/KAIST01_v3.bag")

LIDAR_TOPIC = "/os_cloud_node/points"
IMU_TOPIC   = "/imu/data"

print("Loading timestamps...")
timestamps = []
with open(STAMP_CSV, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2 and row[1].strip() == "ouster":
            timestamps.append(int(row[0].strip()))
timestamps.sort()
print(f"Found {len(timestamps)} LiDAR timestamps")

print("Loading IMU data...")
imu_rows = []
with open(IMU_CSV, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) > 16:
            imu_rows.append(row)
print(f"Found {len(imu_rows)} IMU rows")

print(f"Writing bag to {OUTPUT_BAG} ...")
bag = rosbag.Bag(OUTPUT_BAG, 'w')

print("Writing IMU messages...")
for row in tqdm(imu_rows):
    try:
        ts_ns = int(float(row[0]))
        ts    = rospy.Time(nsecs=ts_ns)
        msg   = Imu()
        msg.header = Header()
        msg.header.stamp    = ts
        msg.header.frame_id = "imu"
        msg.angular_velocity.x    = float(row[8])
        msg.angular_velocity.y    = float(row[9])
        msg.angular_velocity.z    = float(row[10])
        msg.linear_acceleration.x = float(row[11])
        msg.linear_acceleration.y = float(row[12])
        msg.linear_acceleration.z = float(row[13])
        bag.write(IMU_TOPIC, msg, ts)
    except Exception as e:
        print(f"IMU row error: {e}")
        continue

print("Writing LiDAR point cloud messages (with per-point time, uint32 ns)...")
fields = [
    PointField('x',         0,  PointField.FLOAT32, 1),
    PointField('y',         4,  PointField.FLOAT32, 1),
    PointField('z',         8,  PointField.FLOAT32, 1),
    PointField('intensity', 12, PointField.FLOAT32, 1),
    PointField('t',         16, PointField.UINT32,  1),
]

NUM_CHANNELS = 64
NUM_COLS     = 1024
SCAN_PERIOD_NS = 100_000_000  # 0.1s in nanoseconds, OS1-64 spins at 10Hz

col_time_offset_ns = (np.arange(NUM_COLS, dtype=np.uint32) * (SCAN_PERIOD_NS // NUM_COLS))
per_point_time_ns = np.repeat(col_time_offset_ns, NUM_CHANNELS)

matched = 0
missing = 0
for ts_ns in tqdm(timestamps):
    bin_file = os.path.join(OUSTER_DIR, f"{ts_ns}.bin")
    if not os.path.exists(bin_file):
        missing += 1
        continue
    try:
        raw     = np.fromfile(bin_file, dtype=np.float32)
        points  = raw.reshape(-1, 4)
        num_pts = points.shape[0]

        if num_pts == NUM_CHANNELS * NUM_COLS:
            t_col = per_point_time_ns
        else:
            n_cols_actual = num_pts // NUM_CHANNELS
            if n_cols_actual > 0:
                t_col = np.repeat(
                    (np.arange(n_cols_actual, dtype=np.uint32) * (SCAN_PERIOD_NS // n_cols_actual)),
                    NUM_CHANNELS
                )
                if t_col.shape[0] != num_pts:
                    t_col = np.zeros(num_pts, dtype=np.uint32)
            else:
                t_col = np.zeros(num_pts, dtype=np.uint32)

        # pack xyz+intensity as float32 bytes, t as uint32 bytes, interleaved per point
        xyzi_bytes = points.astype(np.float32).tobytes()  # 16 bytes/point contiguous
        t_bytes    = t_col.astype(np.uint32).tobytes()    # 4 bytes/point contiguous

        # interleave: need per-point 20-byte structure -> build via structured array
        struct_dtype = np.dtype([('x', np.float32), ('y', np.float32), ('z', np.float32),
                                  ('intensity', np.float32), ('t', np.uint32)])
        combined = np.zeros(num_pts, dtype=struct_dtype)
        combined['x'] = points[:, 0]
        combined['y'] = points[:, 1]
        combined['z'] = points[:, 2]
        combined['intensity'] = points[:, 3]
        combined['t'] = t_col

        ts  = rospy.Time(nsecs=ts_ns)
        hdr = Header()
        hdr.stamp    = ts
        hdr.frame_id = "os_sensor"
        cloud_msg = PointCloud2()
        cloud_msg.header       = hdr
        cloud_msg.height       = 1
        cloud_msg.width        = num_pts
        cloud_msg.fields       = fields
        cloud_msg.is_bigendian = False
        cloud_msg.point_step   = 20
        cloud_msg.row_step     = 20 * num_pts
        cloud_msg.is_dense     = True
        cloud_msg.data         = combined.tobytes()
        bag.write(LIDAR_TOPIC, cloud_msg, ts)
        matched += 1
    except Exception as e:
        print(f"LiDAR error at {ts_ns}: {e}")
        continue

bag.close()
print(f"\nDone!")
print(f"LiDAR scans written : {matched}")
print(f"LiDAR scans missing : {missing}")
print(f"Bag saved to        : {OUTPUT_BAG}")
