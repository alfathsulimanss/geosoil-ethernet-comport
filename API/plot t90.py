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

def process_file(input_excel_path):
    base_dir = os.path.dirname(input_excel_path)
    file_name = os.path.basename(input_excel_path)
    file_prefix = os.path.splitext(file_name)[0]
    output_excel = os.path.join(base_dir, f"{file_prefix} - Consolidation report.xlsx")

    all_sheets = pd.read_excel(input_excel_path, sheet_name=None)
    # Added engine_kwargs to handle NaN gracefully in Excel if they occur
    writer = pd.ExcelWriter(output_excel, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}})
    workbook = writer.book
    
    for sheet_name, df in all_sheets.items():
        if '.gs' not in sheet_name.lower(): continue
            
        df.columns = df.columns.str.strip()
        
        target_col = 'Height Settlement'
        if target_col not in df.columns:
            print(f"⚠️ Skipping {sheet_name}: '{target_col}' not found.")
            continue

        df['Minutes'] = df['Elapse Time (HH:MM:SS)'].apply(time_to_minutes)
        df['SqrtMinutes'] = np.sqrt(df['Minutes'])
        
        df = df.drop_duplicates(subset=['SqrtMinutes'], keep='first').copy()
        df = df.sort_values('SqrtMinutes').dropna(subset=[target_col, 'SqrtMinutes'])

        # --- T90 & d0 CALCULATIONS ---
        if len(df) < 5:
            print(f"Skipping {sheet_name}: Insufficient data points.")
            continue

        init_df = df.head(4)
        slope, d0_intercept, _, _, _ = linregress(init_df['SqrtMinutes'], init_df[target_col])
        
        # VALIDATION: Ensure regression didn't fail (NaN check)
        if np.isnan(slope) or np.isnan(d0_intercept):
            print(f"Skipping {sheet_name}: Math error (NaN) in regression.")
            continue
        
        f_data = interp1d(df['SqrtMinutes'], df[target_col], kind='linear', fill_value="extrapolate")
        x_search = np.linspace(0, df['SqrtMinutes'].max(), 1000)
        line_115 = d0_intercept + (slope * 1.15) * x_search
        data_interp = f_data(x_search)
        
        idx = np.argmin(np.abs(line_115[10:] - data_interp[10:])) + 10
        sqrt_t90, t90, d90 = x_search[idx], x_search[idx]**2, data_interp[idx]

        # --- PLOTTING ---
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 1. Plot Measured Data
        ax.plot(df['SqrtMinutes'], df[target_col], 'bo-', label='Measured Data', markersize=4, zorder=3)

        # 4. Plot Tangent Construction Lines
        end_idx = min(7, len(df) - 1)
        x_limit = df['SqrtMinutes'].iloc[end_idx]
        x_line_range = np.array([0, x_limit])
        
        ax.plot(x_line_range, d0_intercept + slope * x_line_range, 'r--', label='Initial Tangent', alpha=0.7)
        ax.plot(x_line_range, d0_intercept + (slope * 1.15) * x_line_range, 'g--', label='1.15 Line', alpha=0.7)
        
        # 3. FIX: Capture the top limit BEFORE inversion to ensure line touches X-axis
        # In Matplotlib inverted axes, index [1] is the visual top.
        top_limit_frame = ax.get_ylim()[1]
        
        # 5. Mark t90 and Draw Projection Lines
        ax.plot(sqrt_t90, d90, 'ro', markersize=10, zorder=5)
        
        # Vertical line: Using the dynamic frame top to prevent floating
        ax.vlines(x=sqrt_t90, ymin=top_limit_frame, ymax=d90, colors='black', linestyles=':', linewidth=1.2)
        # Horizontal line: To the Y-axis
        ax.hlines(y=d90, xmin=0, xmax=sqrt_t90, colors='black', linestyles=':', linewidth=1.2)  
        
        # 2. Set Limits and Invert
        ax.set_xlim(left=0) 
        ax.invert_yaxis() # Important: Invert before capturing limits
        
        # 6. Markers and Labels
        ax.plot(0, d0_intercept, 'rs', markersize=6) 
        ax.annotate(f' d0 = {d0_intercept:.3f}', (0, d0_intercept), xytext=(8, 0), textcoords="offset points", color='red', fontweight='bold', va='center')
        ax.annotate(f' t90 = {t90:.2f} min', (sqrt_t90, d90), xytext=(10, 10), textcoords="offset points", color='red', fontweight='bold')

        # --- FORMATTING ---
        ax.set_title(f'Taylor Root-Time Consolidation: {sheet_name}')
        ax.set_xlabel(r'Square Root of Time ($\sqrt{min}$)')
        ax.set_ylabel('Settlement (mm)')
        
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        ax.yaxis.set_minor_locator(MultipleLocator(0.010))
        ax.yaxis.set_major_locator(MultipleLocator(0.050))
        ax.grid(True, which='both', linestyle=':', alpha=0.5)
        
        plt.legend(loc='lower right')
        plt.tight_layout()

        # Save to buffer
        imgdata = io.BytesIO()
        plt.savefig(imgdata, format='png', dpi=150)
        plt.close()

        # --- EXCEL EXPORT ---
        df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        worksheet = writer.sheets[sheet_name[:31]]
        worksheet.insert_image(f'A{len(df) + 4}', f'{sheet_name}.png', {'image_data': imgdata})
        
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9EAD3', 'border': 1})
        val_fmt = workbook.add_format({'border': 1, 'num_format': '0.000'})
        
        worksheet.write('K2', 'Parameter', header_fmt); worksheet.write('L2', 'Value', header_fmt)
        worksheet.write('K3', 'd0 (Intercept mm)', val_fmt); worksheet.write('L3', d0_intercept, val_fmt)
        worksheet.write('K4', 't90 (min)', val_fmt); worksheet.write('L4', t90, val_fmt)
        worksheet.write('K5', 'd90 (mm)', val_fmt); worksheet.write('L5', d90, val_fmt)

    writer.close()
    print(f"SUCCESS:{output_excel}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        print("ERROR: No file path provided.")