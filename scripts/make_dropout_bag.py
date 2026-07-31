import rosbag
import numpy as np
import sys
from sensor_msgs.point_cloud2 import read_points, create_cloud

def dropout_bag(input_bag, output_bag, drop_pct, lidar_topic='/os_cloud_node/points'):
    seed = 42
    rng = np.random.default_rng(seed)
    with rosbag.Bag(input_bag) as inbag, rosbag.Bag(output_bag, 'w') as outbag:
        count = 0
        for topic, msg, t in inbag.read_messages():
            if topic == lidar_topic:
                points = list(read_points(msg, skip_nans=True))
                n = len(points)
                keep_n = int(n * (1 - drop_pct / 100.0))
                if keep_n < 1:
                    keep_n = 1
                idx = rng.choice(n, size=keep_n, replace=False)
                kept_points = [points[i] for i in idx]
                new_msg = create_cloud(msg.header, msg.fields, kept_points)
                outbag.write(topic, new_msg, t)
                count += 1
                if count % 200 == 0:
                    print(f"Processed {count} scans...")
            else:
                outbag.write(topic, msg, t)
    print(f"Done: {output_bag} (drop={drop_pct}%)")

if __name__ == '__main__':
    drop_pct = float(sys.argv[1])
    output = f"/home/hannan/mulran_ws/KAIST01_dropout{int(drop_pct)}.bag"
    dropout_bag("/home/hannan/mulran_ws/KAIST01.bag", output, drop_pct)
