import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# RMSE results collected from each dropout test
dropout_pct = [0, 10, 30, 50, 70]
rmse = [30.19, 27.72, 33.89, 30.81, 32.90]

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(dropout_pct, rmse, marker='o', color='#1F4E79', linewidth=2, markersize=8)
for x, y in zip(dropout_pct, rmse):
    ax.annotate(f"{y:.2f} m", (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10)

ax.set_xlabel("Point Cloud Dropout (%)")
ax.set_ylabel("ATE RMSE (m)")
ax.set_title("FAST-LIO2 Trajectory Accuracy vs. Point Cloud Dropout\n(MulRan KAIST01)")
ax.set_xticks(dropout_pct)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("/home/hannan/mulran_ws/plot_dropout_summary.png", dpi=150)
print("Saved summary plot.")
