import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
from evo.tools import file_interface

def plot_ape_result(zip_path, out_png, title):
    result = file_interface.load_res_file(zip_path, load_trajectories=True)
    ape = result.np_arrays["error_array"]
    timestamps = result.np_arrays["seconds_from_start"]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(timestamps, ape, color="gray", linewidth=1)
    ax.axhline(result.stats["rmse"], color="blue", label=f"rmse ({result.stats['rmse']:.2f} m)")
    ax.axhline(result.stats["mean"], color="red", label=f"mean ({result.stats['mean']:.2f} m)")
    ax.axhline(result.stats["median"], color="green", label=f"median ({result.stats['median']:.2f} m)")
    ax.fill_between(timestamps, result.stats["mean"] - result.stats["std"],
                     result.stats["mean"] + result.stats["std"], alpha=0.2, color="purple", label="std")
    ax.set_xlabel("t (s)")
    ax.set_ylabel("APE (m)")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    print(f"Saved: {out_png}")
    print(f"RMSE={result.stats['rmse']:.3f}  mean={result.stats['mean']:.3f}  median={result.stats['median']:.3f}  max={result.stats['max']:.3f}  std={result.stats['std']:.3f}")

if __name__ == "__main__":
    zip_path = sys.argv[1]
    out_png = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "APE w.r.t. translation part (m)"
    plot_ape_result(zip_path, out_png, title)
