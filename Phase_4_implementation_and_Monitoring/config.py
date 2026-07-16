"""
Shared output-path configuration for Phase 4 scripts.

All results are written under Phase_4_implementation_and_Monitoring/Results/.
"""

from pathlib import Path

results_dir = Path(__file__).resolve().parent / "Results"
visualizations_dir = results_dir / "visualizations"
reports_dir = results_dir / "reports"
monitoring_dir = results_dir / "monitoring"
logs_dir = results_dir / "logs"

CONVERGENCE_PLOT_FILE = visualizations_dir / "convergence_plot.png"

for _dir in (results_dir, visualizations_dir, reports_dir, monitoring_dir, logs_dir):
    _dir.mkdir(parents=True, exist_ok=True)


def get_results_path(filename):
    return str(results_dir / filename)


def get_visualization_path(filename):
    return str(visualizations_dir / filename)


def get_report_path(filename):
    return str(reports_dir / filename)


def get_monitoring_path(filename):
    return str(monitoring_dir / filename)
