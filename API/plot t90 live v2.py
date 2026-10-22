import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from scipy.stats import linregress
from scipy.interpolate import interp1d

def _parse_index_pair(s):
    """Parse 'a,b' into 0-based (idx_a, idx_b). Returns None if invalid."""
    try:
        parts = s.strip().split(',')
        if len(parts) != 2:
            return None
        a = int(float(parts[0].strip()))
        b = int(float(parts[1].strip()))
        if a < 1 or b < 1 or a == b:
            return None
        return (min(a, b) - 1, max(a, b) - 1)
    except (ValueError, TypeError):
        return None

def parse_tangent_indices(raw):
    """
    Parse tangent indices from LabVIEW.
    Accepts "3,4" (1-based point indices) or "nan"/"" for auto mode.
    Returns (idx_a, idx_b) 0-based, or None for auto.
    """
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if s in ('', 'nan', 'null', 'none'):
        return None
    return _parse_index_pair(s)

def compute_tangent_from_indices(x, y, idx_a, idx_b):
    """
    Compute slope and d0 from two specific measured data points (0-based indices).
    Returns (slope, d0_intercept) or (None, None) if invalid.
    """
    if idx_a >= len(x) or idx_b >= len(x):
        return None, None
    x1, y1 = x[idx_a], y[idx_a]
    x2, y2 = x[idx_b], y[idx_b]
    if abs(x2 - x1) < 1e-9:
        return None, None
    slope = (y2 - y1) / (x2 - x1)
    d0_intercept = y1 - slope * x1   # extrapolate back to x=0
    if np.isnan(slope) or np.isnan(d0_intercept):
        return None, None
    return slope, d0_intercept

def generate_plot(sqrt_minutes, settlement, save_path, tangent_indices=None):
    try:
        x = np.array(sqrt_minutes, dtype=float)
        y = np.array(settlement, dtype=float)

        if len(x) < 5:
            print("ERROR|Insufficient data points.")
            return

        # --- T90 & d0 CALCULATIONS ---
        # Invert y for calculations so settlement increases positively,
        # ensuring slope is positive and 1.15 line intersection is found correctly.
        y_calc = -y

        if tangent_indices is not None:
            idx_a, idx_b = tangent_indices
            slope_calc, d0_calc = compute_tangent_from_indices(x, y_calc, idx_a, idx_b)
            if slope_calc is None:
                # Fallback to auto if indices are out of range or degenerate
                slope_calc, d0_calc, _, _, _ = linregress(x[:4], y_calc[:4])
                effective_label = 'Auto fallback (4 pts)'
                tangent_indices = None  # clear so plot doesn't try to mark them
            else:
                effective_label = f'Manual (pts {idx_a+1} & {idx_b+1})'
        else:
            slope_calc, d0_calc, _, _, _ = linregress(x[:4], y_calc[:4])
            effective_label = 'Auto (first 4 pts)'

        # Convert back to original space: d0 = -d0_calc, slope sign flipped
        d0_intercept = -d0_calc
        slope        = -slope_calc

        # Find t90: work in calc (positive) space for reliable intersection search
        f_data_calc = interp1d(x, y_calc, kind='linear', fill_value="extrapolate")
        x_search = np.linspace(0, x.max(), 1000)
        line_115_calc = d0_calc + (slope_calc / 1.15) * x_search
        data_interp_calc = f_data_calc(x_search)

        idx = np.argmin(np.abs(line_115_calc[10:] - data_interp_calc[10:])) + 10
        sqrt_t90 = x_search[idx]
        t90       = sqrt_t90 ** 2
        d90       = -data_interp_calc[idx]   # back to original (display) space

        # --- PLOTTING ---
        fig, ax = plt.subplots(figsize=(5.5, 3), layout='constrained')

        # Invert y-axis FIRST so all data and lines are drawn in visual space
        ax.set_xlim(left=0)
        ax.invert_yaxis()

        # Measured Data
        ax.plot(x, y, 'bo-', label='Measured', markersize=3, linewidth=1, zorder=3)

        # Mark the two tangent points if manual
        if tangent_indices is not None:
            idx_a, idx_b = tangent_indices
            ax.plot([x[idx_a], x[idx_b]], [y[idx_a], y[idx_b]], 'y^',
                    markersize=7, label=f'Tangent pts ({idx_a+1} & {idx_b+1})',
                    zorder=6)

        # Construction Lines (drawn in original y space, same slope sign)
        x_limit = x[min(7, len(x) - 1)]
        x_line_range = np.array([0, x_limit * 1.2])
        ax.plot(x_line_range, d0_intercept + slope * x_line_range,
                'r--', label='Tangent', alpha=0.7, linewidth=1)
        ax.plot(x_line_range, d0_intercept + (slope / 1.15) * x_line_range,
                'g--', label='1.15 Line', alpha=0.7, linewidth=1)

        # Capture top limit AFTER inversion and data plotting
        top_limit_frame = ax.get_ylim()[1]

        # T90 Mark & Projections
        ax.plot(sqrt_t90, d90, 'ro', markersize=4, zorder=5)
        ax.vlines(x=sqrt_t90, ymin=top_limit_frame, ymax=d90,
                  colors='black', linestyles=':', linewidth=0.8)
        ax.hlines(y=d90, xmin=0, xmax=sqrt_t90,
                  colors='black', linestyles=':', linewidth=0.8)

        # Labels and Annotations
        ax.plot(0, d0_intercept, 'rs', markersize=4)
        ax.annotate(f'd0={d0_intercept:.3f}',
                    (0, d0_intercept),
                    xytext=(50, -1),
                    textcoords="offset points",
                    color='red', fontweight='bold', fontsize=6,
                    ha='right', va='center')
        ax.annotate(f't90={t90:.2f}min',
                    (sqrt_t90, d90),
                    xytext=(10, 0),
                    textcoords="offset points",
                    color='red', fontweight='bold', fontsize=6,
                    ha='left', va='center')

        # Formatting
        ax.set_title(f'Taylor Root-Time [{effective_label}]', fontsize=8)
        ax.set_xlabel(r'$\sqrt{Time}$ ($\sqrt{min}$)', fontsize=7)
        ax.set_ylabel('Settlement (mm)', fontsize=7)
        ax.tick_params(axis='both', labelsize=7)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        ax.yaxis.set_minor_locator(MultipleLocator(0.010))
        ax.grid(True, which='both', linestyle=':', alpha=0.5)
        ax.legend(loc='lower right', fontsize=6, framealpha=0.8)

        plt.savefig(save_path, dpi=150)
        plt.close()

        # Return result for LabVIEW (same format as original)
        print(f"SUCCESS|{t90:.4f}|{d0_intercept:.4f}|{save_path}")

    except Exception as e:
        print(f"ERROR|{str(e)}")

if __name__ == "__main__":
    # LabVIEW call formats:
    #
    #   Auto mode (default - regression on first 4 pts):
    #     python "plot t90 live v2.py" "0,1,2,..." "0.1,0.2,..." "path/save.png"
    #     python "plot t90 live v2.py" "0,1,2,..." "0.1,0.2,..." "path/save.png" "nan"
    #
    #   Manual mode (tangent through data point 3 and point 4):
    #     python "plot t90 live v2.py" "0,1,2,..." "0.1,0.2,..." "path/save.png" "3,4"
    #
    if len(sys.argv) > 3:
        arg_sqrt_t    = sys.argv[1].split(',')
        arg_settle    = sys.argv[2].split(',')
        arg_path      = sys.argv[3]
        raw_tangent   = sys.argv[4] if len(sys.argv) > 4 else None
        t_indices     = parse_tangent_indices(raw_tangent)
        generate_plot(arg_sqrt_t, arg_settle, arg_path, tangent_indices=t_indices)
    else:
        print("ERROR|Missing arguments.")
