from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from process_water_model.model import run_model


def make_plots(rows):
    import matplotlib.pyplot as plt

    assets = ROOT / "docs" / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    worst = [r for r in rows if r["scenario_id"] == "WORST"]

    # One residual trace per system. Duplicate organism rows are collapsed by cycle.
    fig, ax = plt.subplots(figsize=(9, 5))
    for system_id in sorted({r["system_id"] for r in worst}):
        system_rows = [r for r in worst if r["system_id"] == system_id]
        by_cycle = {}
        for r in system_rows:
            by_cycle[r["cycle"]] = r
        points = [by_cycle[k] for k in sorted(by_cycle)]
        ax.plot(
            [r["elapsed_time_h"] for r in points],
            [r["pre_redose_residual_ppm"] for r in points],
            marker="o",
            markersize=2,
            label=points[0]["system_name"],
        )
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("Pre-redose residual (ppm)")
    ax.set_title("Synthetic example: disinfectant residual dynamics")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(assets / "example_residual.png", dpi=180)
    plt.close(fig)

    # Organism A only, to keep the figure readable.
    fig, ax = plt.subplots(figsize=(9, 5))
    subset = [r for r in worst if r["organism_id"] == "IND_A"]
    for system_id in sorted({r["system_id"] for r in subset}):
        system_rows = [r for r in subset if r["system_id"] == system_id]
        ax.plot(
            [r["elapsed_time_h"] for r in system_rows],
            [r["cfu_ml"] for r in system_rows],
            label=system_rows[0]["system_name"],
        )
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("Indicator concentration (CFU/mL)")
    ax.set_title("Synthetic example: microbial concentration")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(assets / "example_microbes.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    rows, summary = run_model(ROOT / "config", ROOT / "outputs")
    make_plots(rows)
    print(f"Generated {len(rows)} detailed rows.")
    for row in summary:
        print(row)
