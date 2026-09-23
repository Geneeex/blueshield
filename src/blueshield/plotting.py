"""Optional scientific figures using matplotlib; original assets are untouched."""
from __future__ import annotations

from pathlib import Path


def create_plots(output_dir: Path, inputs: dict, engineering: dict, survey: dict,
                 cycle_rows: list[dict], membrane_rows: list[dict]) -> dict:
    try:
        import matplotlib
    except ImportError:
        return {"status": "skipped", "reason": "Optional matplotlib is not installed.", "files": []}
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    flow_L_h = inputs["cycle"]["discharge_flow"]["value"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.8), layout="constrained")
    axes[0].plot([r["assumed_flux_LMH"] for r in membrane_rows],
                 [r["calculated_active_area_m2"] for r in membrane_rows], color="#17638b")
    for row in engineering["membrane"]["area_scenarios"]:
        x, y = row["assumed_flux_LMH"], row["active_area_m2"]
        axes[0].plot(x, y, "o", color="#c56a23")
        axes[0].annotate(f"{y:.2f} m²", (x, y), xytext=(5, 6), textcoords="offset points", fontsize=8)
    axes[0].set(xlabel="Assumed operating flux (L m⁻² h⁻¹)", ylabel="Required active area (m²)",
                title=f"(a) Membrane sizing at assumed {flow_L_h:g} L/h")
    flows = [r["assumed_discharge_L_h"] for r in cycle_rows]
    axes[1].plot(flows, flows, "--", color="#869198", label="Discharge flow")
    axes[1].plot(flows, [r["calculated_cycle_average_L_h"] for r in cycle_rows], color="#17638b", label="Cycle-average delivery")
    axes[1].plot(flow_L_h, engineering["cycle"]["cycle_average_L_h"], "o", color="#c56a23")
    axes[1].set(xlabel="Assumed discharge flow (L/h)", ylabel="Flow (L/h)", title="(b) Sequential batch timing")
    axes[1].legend(frameon=False, fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.18)
    fig.suptitle("Illustrative engineering calculations — no experimental performance data", fontsize=10)
    fig.savefig(output_dir / "design_sensitivity.png", dpi=250)
    plt.close(fig)

    rows = survey["perceptions"]
    labels = ["Technical feasibility", "Anticipated effectiveness", "Monitoring benefit"]
    fig, ax = plt.subplots(figsize=(8.5, 3.9))
    fig.subplots_adjust(left=0.27, right=0.98, top=0.86, bottom=0.28)
    very = [r["very_pct"] for r in rows]
    somewhat = [r["somewhat_pct"] for r in rows]
    ax.barh(labels, very, color="#175d82", label="Very")
    ax.barh(labels, somewhat, left=very, color="#67a9bf", label="Somewhat")
    for index, row in enumerate(rows):
        ax.text(very[index] / 2, index, f"{very[index]:.1f}%", ha="center", va="center", color="white")
        ax.text(very[index] + somewhat[index] / 2, index, f"{somewhat[index]:.1f}%", ha="center", va="center")
        ax.text(row["favorable_pct"] + 1, index, f"{row['favorable_pct']:.1f}%", va="center")
    ax.set(xlim=(0, 104), xlabel="Reported percentage (%)",
           title="Reported survey aggregates (stated sample n = 125)")
    ax.invert_yaxis()
    fig.legend(*ax.get_legend_handles_labels(), frameon=False, loc="lower center", bbox_to_anchor=(0.62, 0.07), ncol=2)
    ax.grid(axis="x", alpha=0.15)
    ax.set_axisbelow(True)
    fig.text(0.5, 0.02, "Very/somewhat feasible, effective, or beneficial respectively. No inferential intervals.", ha="center", fontsize=8)
    fig.savefig(output_dir / "perception_aggregates.png", dpi=250, bbox_inches="tight")
    plt.close(fig)
    return {"status": "produced", "matplotlib_version": matplotlib.__version__,
            "files": ["design_sensitivity.png", "perception_aggregates.png"]}
