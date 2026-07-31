import rosbag

bag = rosbag.Bag('/home/hannan/mulran_ws/odom_recorded_v6.bag')
with open('/home/hannan/mulran_ws/fastlio_clean_v6.txt', 'w') as f:
    for topic, msg, t in bag.read_messages(topics=['/Odometry']):
        stamp = msg.header.stamp.to_sec()
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        f.write(f"{stamp:.9f} {p.x:.6f} {p.y:.6f} {p.z:.6f} {q.x:.9f} {q.y:.9f} {q.z:.9f} {q.w:.9f}\n")
bag.close()
