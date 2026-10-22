import pandas as pd
import numpy as np
import os
import io
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from scipy.stats import linregress
from scipy.interpolate import interp1d

def time_to_minutes(t_str):
    try:
        parts = list(map(float, str(t_str).split(':')))
        return parts[0] * 60 + parts[1] + parts[2] / 60 if len(parts) == 3 else 0.0
    except:
        return 0.0

def _parse_index_pair(s):
    """
    Parse a single "pt1,pt2" string into a 0-based (idx_a, idx_b) tuple.
    Returns None if invalid.
    """
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

def parse_tangent_map(raw):
    """
    Parse tangent input from LabVIEW. Supports two formats:

    1. Global (same indices for all sheets):
         "3,4"

    2. Per-sheet (different indices per sheet, separated by ";"):
         "LOAD 24N.gs=3,4;LOAD 48N.gs=5,6;LOAD 96N.gs=nan"

    Returns a dict mapping sheet name (lower) -> (idx_a, idx_b) or None (auto).
    If global format, returns a single-entry dict with key "*" (wildcard).
    Returns None entirely if raw is empty/nan.
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if s.lower() in ('', 'nan', 'null', 'none'):
        return None

    # Per-sheet format contains '='
    if '=' in s:
        result = {}
        for entry in s.split(';'):
            entry = entry.strip()
            if not entry:
                continue
            if '=' not in entry:
                continue
            sheet_part, idx_part = entry.split('=', 1)
            key = sheet_part.strip().lower()
            idx_str = idx_part.strip().lower()
            if idx_str == 'skip':
                val = 'skip'
            elif idx_str in ('nan', 'null', 'none', ''):
                val = None
            else:
                val = _parse_index_pair(idx_part)
            result[key] = val
        return result if result else None

    # Global format: just "3,4"
    indices = _parse_index_pair(s)
    if indices is None:
        return None
    return {'*': indices}

def compute_tangent_from_indices(df, target_col, idx_a, idx_b):
    """
    Compute slope and d0 intercept using two actual measured data points
    identified by their 0-based row indices.
    Extrapolates the line back to x=0 to get d0.
    """
    if idx_a >= len(df) or idx_b >= len(df):
        return None, None

    x1 = df['SqrtMinutes'].iloc[idx_a]
    y1 = df[target_col].iloc[idx_a]
    x2 = df['SqrtMinutes'].iloc[idx_b]
    y2 = df[target_col].iloc[idx_b]

    if abs(x2 - x1) < 1e-9:
        return None, None

    slope = (y2 - y1) / (x2 - x1)
    d0_intercept = y1 - slope * x1  # extrapolate back to x=0

    if np.isnan(slope) or np.isnan(d0_intercept):
        return None, None
    return slope, d0_intercept

def make_sheet_name(sheet_name, suffix):
    """Build an Excel-safe sheet name with a suffix, capped at 31 characters."""
    base = str(sheet_name).strip()
    max_base_len = max(1, 31 - len(suffix))
    return f"{base[:max_base_len]}{suffix}"

def estimate_t100(df, target_col):
    """
    Estimate T100 from the late-time plateau.

    This is a practical approximation for consolidation reporting:
    - Estimate the final primary consolidation settlement from the last 20% of points
      (minimum 5 points).
    - Find the first time where the settlement reaches 99% of that estimated final value.

    Returns a dict with the estimated settlement, threshold, and T100 time in minutes.
    """
    work = df[['Minutes', target_col]].copy()
    work = work.dropna(subset=['Minutes', target_col])
    work = work[work['Minutes'] > 0].sort_values('Minutes')

    if len(work) < 5:
        return None

    tail_count = max(5, int(np.ceil(len(work) * 0.2)))
    final_settlement = float(work[target_col].tail(tail_count).mean())
    initial_settlement = float(work[target_col].iloc[0])
    threshold_settlement = initial_settlement + (0.99 * (final_settlement - initial_settlement))

    minutes = work['Minutes'].to_numpy(dtype=float)
    settlement = work[target_col].to_numpy(dtype=float)

    t100_minutes = float(minutes[-1])
    for idx in range(1, len(work)):
        y0 = settlement[idx - 1]
        y1 = settlement[idx]
        x0 = minutes[idx - 1]
        x1 = minutes[idx]

        crossed = (y0 <= threshold_settlement <= y1) or (y0 >= threshold_settlement >= y1)
        if not crossed:
            continue

        if abs(y1 - y0) < 1e-9:
            t100_minutes = float(x1)
        else:
            fraction = (threshold_settlement - y0) / (y1 - y0)
            t100_minutes = float(x0 + (fraction * (x1 - x0)))
        break

    return {
        'final_settlement': final_settlement,
        'threshold_settlement': threshold_settlement,
        't100_minutes': t100_minutes,
        'log_t100': float(np.log10(t100_minutes)) if t100_minutes > 0 else None,
        'tail_count': tail_count,
        'method': f'Late plateau estimate ({tail_count} pts, 99% threshold)'
    }

def create_t100_figure(df, target_col, sheet_name):
    """Create a log-time T100 estimate figure for consolidation reporting."""
    estimate = estimate_t100(df, target_col)
    if estimate is None:
        return None, None

    work = df[['Minutes', target_col]].copy()
    work = work.dropna(subset=['Minutes', target_col])
    work = work[work['Minutes'] > 0].sort_values('Minutes')
    if len(work) < 5:
        return None, None

    log_minutes = np.log10(work['Minutes'].to_numpy(dtype=float))
    settlement = work[target_col].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(left=min(0, float(np.nanmin(log_minutes))))
    ax.invert_yaxis()
    ax.plot(log_minutes, settlement, 'bo-', label='Measured Data', markersize=4, zorder=3)

    ax.axhline(estimate['threshold_settlement'], color='orange', linestyle='--', linewidth=1.2,
               label='Estimated 99% of d100')

    if estimate['log_t100'] is not None:
        ax.vlines(x=estimate['log_t100'], ymin=ax.get_ylim()[0], ymax=estimate['threshold_settlement'],
                  colors='black', linestyles=':', linewidth=1.2, label='Estimated T100')
        ax.plot(estimate['log_t100'], estimate['threshold_settlement'], 'ro', markersize=8, zorder=5)
        ax.annotate(f" T100 = {estimate['t100_minutes']:.2f} min",
                    (estimate['log_t100'], estimate['threshold_settlement']),
                    xytext=(10, 10), textcoords="offset points",
                    color='red', fontweight='bold')

    ax.annotate(f" d100 = {estimate['final_settlement']:.3f}",
                (log_minutes[-1], estimate['final_settlement']),
                xytext=(10, -15), textcoords="offset points",
                color='orange', fontweight='bold')

    ax.set_title(f'Log-Time Consolidation: {sheet_name}  [T100 estimate]')
    ax.set_xlabel(r'Log$_{10}$(Time, min)')
    ax.set_ylabel('Settlement (mm)')

    ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    ax.yaxis.set_minor_locator(MultipleLocator(0.010))
    ax.yaxis.set_major_locator(MultipleLocator(0.050))
    ax.grid(True, which='both', linestyle=':', alpha=0.5)
    ax.legend(loc='lower right')

    plt.tight_layout()
    return fig, estimate

def process_file(input_excel_path, tangent_map=None):
    """
    Parameters
    ----------
    input_excel_path : str
    tangent_map : dict or None
        Maps sheet name (lowercase) -> (idx_a, idx_b) 0-based tuple, or None for auto.
        Use key '*' for a global setting that applies to all sheets.
        If tangent_map is None entirely, all sheets run in auto mode.
    """

    try:
        base_dir = os.path.dirname(input_excel_path)
        file_name = os.path.basename(input_excel_path)
        file_prefix = os.path.splitext(file_name)[0]
        output_excel = os.path.join(base_dir, f"{file_prefix} - Consolidation report.xlsx")
        all_sheets = pd.read_excel(input_excel_path, sheet_name=None)
    except Exception as e:
        print(f"ERROR: Failed to open file - {e}")
        return

    writer = pd.ExcelWriter(output_excel, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}})
    workbook = writer.book
    sheets_written = 0

    try:
        for sheet_name, df in all_sheets.items():
            if '.gs' not in sheet_name.lower():
                continue

            try:
                df.columns = df.columns.str.strip()

                target_col = 'Height Settlement'
                if target_col not in df.columns:
                    print(f"Skipping {sheet_name}: '{target_col}' not found.")
                    continue

                df['Minutes'] = df['Elapse Time (HH:MM:SS)'].apply(time_to_minutes)
                df['SqrtMinutes'] = np.sqrt(df['Minutes'])

                df = df.drop_duplicates(subset=['SqrtMinutes'], keep='first').copy()
                df = df.sort_values('SqrtMinutes').dropna(subset=[target_col, 'SqrtMinutes'])

                if len(df) < 5:
                    print(f"Skipping {sheet_name}: Insufficient data points.")
                    continue

                # --- Resolve tangent indices for this sheet ---
                sheet_indices = None
                if tangent_map is not None:
                    # Exact sheet name match first, then wildcard
                    sheet_indices = tangent_map.get(sheet_name.strip().lower(),
                                    tangent_map.get('*', None))

                if sheet_indices == 'skip':
                    print(f"Skipping {sheet_name}: marked as skip.")
                    continue

                # --- TANGENT LINE: slope & d0 ---
                if sheet_indices is not None:
                    idx_a, idx_b = sheet_indices
                    slope, d0_intercept = compute_tangent_from_indices(df, target_col, idx_a, idx_b)
                    if slope is None:
                        print(f"Sheet '{sheet_name}': Could not compute tangent from indices {idx_a+1},{idx_b+1}. Falling back to auto.")
                        init_df = df.head(4)
                        slope, d0_intercept, _, _, _ = linregress(init_df['SqrtMinutes'], init_df[target_col])
                        effective_label = 'Auto fallback (4 pts)'
                        pt_a_x = pt_a_y = pt_b_x = pt_b_y = None
                    else:
                        effective_label = f'Manual (pts {idx_a+1} & {idx_b+1})'
                        pt_a_x = df['SqrtMinutes'].iloc[idx_a]
                        pt_a_y = df[target_col].iloc[idx_a]
                        pt_b_x = df['SqrtMinutes'].iloc[idx_b]
                        pt_b_y = df[target_col].iloc[idx_b]
                else:
                    init_df = df.head(4)
                    slope, d0_intercept, _, _, _ = linregress(init_df['SqrtMinutes'], init_df[target_col])
                    effective_label = 'Auto (first 4 pts)'
                    pt_a_x = pt_a_y = pt_b_x = pt_b_y = None
                    idx_a = idx_b = None

                if np.isnan(slope) or np.isnan(d0_intercept):
                    print(f"Skipping {sheet_name}: NaN in regression.")
                    continue

                # --- T90 CALCULATION ---
                f_data = interp1d(df['SqrtMinutes'], df[target_col], kind='linear', fill_value="extrapolate")
                x_search = np.linspace(0, df['SqrtMinutes'].max(), 1000)
                line_115 = d0_intercept + (slope / 1.15) * x_search
                data_interp = f_data(x_search)

                idx = np.argmin(np.abs(line_115[10:] - data_interp[10:])) + 10
                sqrt_t90, t90, d90 = x_search[idx], x_search[idx]**2, data_interp[idx]

                # --- PLOTTING ---
                fig, ax = plt.subplots(figsize=(10, 6))

                # 1. Invert y-axis FIRST
                ax.set_xlim(left=0)
                ax.invert_yaxis()

                # 2. Measured Data
                ax.plot(df['SqrtMinutes'], df[target_col], 'bo-', label='Measured Data', markersize=4, zorder=3)

                # 3. Mark the two tangent points if manual
                if pt_a_x is not None:
                    ax.plot([pt_a_x, pt_b_x], [pt_a_y, pt_b_y], 'y^', markersize=10,
                            label=f'Tangent pts ({idx_a+1} & {idx_b+1})',
                            zorder=6)

                # 4. Tangent Construction Lines
                end_idx = min(7, len(df) - 1)
                x_limit = df['SqrtMinutes'].iloc[end_idx]
                x_line_range = np.array([0, x_limit])

                ax.plot(x_line_range, d0_intercept + slope * x_line_range, 'r--', label='Initial Tangent', alpha=0.7)
                ax.plot(x_line_range, d0_intercept + (slope / 1.15) * x_line_range, 'g--', label='1.15 Line', alpha=0.7)

                # 5. Capture top limit AFTER inversion and data
                top_limit_frame = ax.get_ylim()[1]

                # 6. Mark t90 Projection Lines
                ax.plot(sqrt_t90, d90, 'ro', markersize=10, zorder=5)
                ax.vlines(x=sqrt_t90, ymin=top_limit_frame, ymax=d90, colors='black', linestyles=':', linewidth=1.2)
                ax.hlines(y=d90, xmin=0, xmax=sqrt_t90, colors='black', linestyles=':', linewidth=1.2)

                # 7. Labels
                ax.plot(0, d0_intercept, 'rs', markersize=6)
                ax.annotate(f' d0 = {d0_intercept:.3f}', (0, d0_intercept), xytext=(8, 0), textcoords="offset points", color='red', fontweight='bold', va='center')
                ax.annotate(f' t90 = {t90:.2f} min', (sqrt_t90, d90), xytext=(10, 10), textcoords="offset points", color='red', fontweight='bold')

                # --- FORMATTING ---
                ax.set_title(f'Taylor Root-Time Consolidation: {sheet_name}  [{effective_label}]')
                ax.set_xlabel(r'Square Root of Time ($\sqrt{min}$)')
                ax.set_ylabel('Settlement (mm)')

                ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
                ax.yaxis.set_minor_locator(MultipleLocator(0.010))
                ax.yaxis.set_major_locator(MultipleLocator(0.050))
                ax.grid(True, which='both', linestyle=':', alpha=0.5)

                plt.legend(loc='lower right')
                plt.tight_layout()

                imgdata = io.BytesIO()
                plt.savefig(imgdata, format='png', dpi=150)
                plt.close()

                # --- EXCEL EXPORT ---
                t90_sheet_name = make_sheet_name(sheet_name, '_T90')
                df.to_excel(writer, sheet_name=t90_sheet_name, index=False)
                worksheet = writer.sheets[t90_sheet_name]
                worksheet.insert_image(f'A{len(df) + 4}', f'{sheet_name}.png', {'image_data': imgdata})

                header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9EAD3', 'border': 1})
                val_fmt = workbook.add_format({'border': 1, 'num_format': '0.000'})
                str_fmt = workbook.add_format({'border': 1})

                worksheet.write('K2', 'Parameter', header_fmt); worksheet.write('L2', 'Value', header_fmt)
                worksheet.write('K3', 'd0 (Intercept mm)', val_fmt); worksheet.write('L3', d0_intercept, val_fmt)
                worksheet.write('K4', 't90 (min)', val_fmt); worksheet.write('L4', t90, val_fmt)
                worksheet.write('K5', 'd90 (mm)', val_fmt); worksheet.write('L5', d90, val_fmt)
                worksheet.write('K6', 'Tangent Mode', str_fmt); worksheet.write('L6', effective_label, str_fmt)
                if pt_a_x is not None:
                    worksheet.write('K7', f'Pt {idx_a+1} sqrt_t', val_fmt); worksheet.write('L7', pt_a_x, val_fmt)
                    worksheet.write('K8', f'Pt {idx_a+1} Settlement', val_fmt); worksheet.write('L8', pt_a_y, val_fmt)
                    worksheet.write('K9', f'Pt {idx_b+1} sqrt_t', val_fmt); worksheet.write('L9', pt_b_x, val_fmt)
                    worksheet.write('K10', f'Pt {idx_b+1} Settlement', val_fmt); worksheet.write('L10', pt_b_y, val_fmt)

                # --- T100 EXPORT ---
                t100_fig, t100_info = create_t100_figure(df, target_col, sheet_name)
                if t100_fig is not None and t100_info is not None:
                    t100_sheet_name = make_sheet_name(sheet_name, '_T100')
                    t100_imgdata = io.BytesIO()
                    t100_fig.savefig(t100_imgdata, format='png', dpi=150)
                    plt.close(t100_fig)

                    df.to_excel(writer, sheet_name=t100_sheet_name, index=False)
                    t100_worksheet = writer.sheets[t100_sheet_name]
                    t100_worksheet.insert_image(f'A{len(df) + 4}', f'{sheet_name}_T100.png', {'image_data': t100_imgdata})

                    t100_worksheet.write('K2', 'Parameter', header_fmt); t100_worksheet.write('L2', 'Value', header_fmt)
                    t100_worksheet.write('K3', 'Estimated d100 (mm)', val_fmt); t100_worksheet.write('L3', t100_info['final_settlement'], val_fmt)
                    t100_worksheet.write('K4', 'T100 (min)', val_fmt); t100_worksheet.write('L4', t100_info['t100_minutes'], val_fmt)
                    t100_worksheet.write('K5', '99% Threshold (mm)', val_fmt); t100_worksheet.write('L5', t100_info['threshold_settlement'], val_fmt)
                    t100_worksheet.write('K6', 'Method', str_fmt); t100_worksheet.write('L6', t100_info['method'], str_fmt)

                sheets_written += 1

            except Exception as e:
                print(f"ERROR: Sheet '{sheet_name}' failed - {e}")
                plt.close('all')
                continue

    finally:
        if sheets_written == 0:
            print("ERROR: No valid .gs sheets were processed. Output file not saved.")
            writer.close()
        else:
            writer.close()
            print(f"SUCCESS:{output_excel}")

if __name__ == "__main__":
    # Usage from LabVIEW:
    #
    #   Auto mode (all sheets use regression on first 4 pts):
    #     python "plot t90 v2.py" "C:\path\to\file.xlsx"
    #     python "plot t90 v2.py" "C:\path\to\file.xlsx" "nan"
    #
    #   Global manual mode (same 2 points for ALL sheets):
    #     python "plot t90 v2.py" "C:\path\to\file.xlsx" "3,4"
    #
    #   Per-sheet manual mode (different points per sheet, separated by ";"):
    #     python "plot t90 v2.py" "C:\path\to\file.xlsx" "LOAD 24N.gs=3,4;LOAD 48N.gs=5,6"
    #
    #   Mixed (some sheets manual, others auto — use nan for auto sheets):
    #     python "plot t90 v2.py" "C:\path\to\file.xlsx" "LOAD 24N.gs=3,4;LOAD 48N.gs=nan"
    #
    #   Skip a sheet entirely (not a t90 test):
    #     python "plot t90 v2.py" "C:\path\to\file.xlsx" "LOAD 24N.gs=3,4;LOAD 48N.gs=skip"
    #
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
        raw_tangent = sys.argv[2] if len(sys.argv) > 2 else None
        tangent_map = parse_tangent_map(raw_tangent)
        process_file(excel_path, tangent_map=tangent_map)
    else:
        print("ERROR: No file path provided.")
