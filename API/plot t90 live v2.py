import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, AutoMinorLocator, FormatStrFormatter
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

def parse_series_arg(raw):
    """
    Parse a numeric series from:
    1) comma-separated string (existing behavior), or
    2) file reference using '@path' to avoid command-line length limits.

    File content can be either:
    - comma-separated values, or
    - JSON array, e.g. [0, 1.2, 3.4]
    """
    if raw is None:
        return np.array([], dtype=float)

    s = str(raw).strip()

    if s.startswith('@'):
        file_path = s[1:].strip().strip('"')
        if not os.path.isfile(file_path):
            raise ValueError(f"Data file not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            s = f.read().strip()

    if not s:
        return np.array([], dtype=float)

    if s.startswith('[') and s.endswith(']'):
        values = json.loads(s)
    else:
        values = [v for v in s.split(',') if v.strip() != '']

    return np.asarray(values, dtype=float)

def parse_payload_arg(raw):
    """
    Parse a combined payload that contains both x and y arrays.

    Supported forms:
    1) @path_to_json_file
    2) inline JSON text

    Supported keys:
    - sqrt_minutes / x / time_array
    - settlement / y / deformation_array
    """
    if raw is None:
        raise ValueError("Payload argument is empty")

    s = str(raw).strip()
    if s.startswith('@'):
        file_path = s[1:].strip().strip('"')
        if not os.path.isfile(file_path):
            raise ValueError(f"Payload file not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            s = f.read().strip()

    if not s:
        raise ValueError("Payload content is empty")

    payload = json.loads(s)
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a JSON object")

    x_values = (
        payload.get('sqrt_minutes')
        or payload.get('x')
        or payload.get('time_array')
    )
    y_values = (
        payload.get('settlement')
        or payload.get('y')
        or payload.get('deformation_array')
    )

    if x_values is None or y_values is None:
        raise ValueError("Payload must include x/sqrt_minutes/time_array and y/settlement/deformation_array")

    return np.asarray(x_values, dtype=float), np.asarray(y_values, dtype=float)

def is_payload_arg(raw):
    """Return True when argument looks like a combined JSON payload input."""
    if raw is None:
        return False

    s = str(raw).strip()
    if not s:
        return False

    if s.startswith('@'):
        file_path = s[1:].strip().strip('"')
        lower_name = file_path.lower()
        return lower_name.endswith('.json')

    return s.startswith('{')

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

        if len(x) != len(y):
            print(f"ERROR|Length mismatch: sqrt_minutes={len(x)} settlement={len(y)}")
            return

        if len(x) < 5:
            print("ERROR|Insufficient data points.")
            return

        # Sort and de-duplicate x values for stable interpolation/regression.
        order = np.argsort(x)
        x = x[order]
        y = y[order]
        x_unique, unique_idx = np.unique(x, return_index=True)
        y_unique = y[unique_idx]
        x = x_unique
        y = y_unique

        if len(x) < 5:
            print("ERROR|Insufficient unique x points after cleaning.")
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

        # Set x-range explicitly from data to avoid clipping when autoscale is disabled.
        x_max = float(np.max(x)) if len(x) > 0 else 1.0
        ax.set_xlim(0, max(1.0, x_max * 1.05))
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
        ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
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
    #   Large-data mode (recommended for LabVIEW):
    #     python "plot t90 live v2.py" "@C:\\temp\\sqrt_t.txt" "@C:\\temp\\settle.txt" "path/save.png"
    #   (txt can be CSV text or JSON array)
    #
    #   Single payload mode (one argument for both arrays):
    #     python "plot t90 live v2.py" "@C:\\temp\\t90_payload.json" "path/save.png"
    #   JSON example:
    #     {"sqrt_minutes":[...],"settlement":[...]}
    #
    if len(sys.argv) >= 3 and is_payload_arg(sys.argv[1]):
        try:
            arg_sqrt_t, arg_settle = parse_payload_arg(sys.argv[1])
            arg_path = sys.argv[2]
            raw_tangent = sys.argv[3] if len(sys.argv) > 3 else None
            t_indices = parse_tangent_indices(raw_tangent)
            generate_plot(arg_sqrt_t, arg_settle, arg_path, tangent_indices=t_indices)
        except Exception as e:
            print(f"ERROR|{str(e)}")
    elif len(sys.argv) > 3:
        arg_sqrt_t    = parse_series_arg(sys.argv[1])
        arg_settle    = parse_series_arg(sys.argv[2])
        arg_path      = sys.argv[3]
        raw_tangent   = sys.argv[4] if len(sys.argv) > 4 else None
        t_indices     = parse_tangent_indices(raw_tangent)
        generate_plot(arg_sqrt_t, arg_settle, arg_path, tangent_indices=t_indices)
    else:
        print("ERROR|Missing arguments.")
