import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from scipy.stats import linregress
from scipy.interpolate import interp1d

def generate_plot(sqrt_minutes, settlement, save_path):
    try:
        x = np.array(sqrt_minutes, dtype=float)
        y = np.array(settlement, dtype=float)

        if len(x) < 5:
            print("ERROR: Insufficient data points.")
            return

        # --- T90 & d0 CALCULATIONS ---
        init_df_x = x[:4]
        init_df_y = y[:4]
        slope, d0_intercept, _, _, _ = linregress(init_df_x, init_df_y)
        
        f_data = interp1d(x, y, kind='linear', fill_value="extrapolate")
        x_search = np.linspace(0, x.max(), 1000)
        
        # Taylor's 1.15 construction: Abscissa increases by 1.15 -> slope / 1.15
        line_115 = d0_intercept + (slope / 1.15) * x_search
        data_interp = f_data(x_search)
        
        idx = np.argmin(np.abs(line_115[10:] - data_interp[10:])) + 10
        sqrt_t90, t90, d90 = x_search[idx], x_search[idx]**2, data_interp[idx]

        # --- PLOTTING (Optimized for 5x3) ---
        fig, ax = plt.subplots(figsize=(5.5, 3), layout='constrained')
        
        # 3. Axis Configuration FIRST so all subsequent coordinates are in inverted space
        ax.set_xlim(left=0)
        ax.invert_yaxis()

        # 1. Measured Data
        ax.plot(x, y, 'bo-', label='Measured', markersize=3, linewidth=1, zorder=3)

        # 2. Construction Lines
        x_limit = x[min(7, len(x) - 1)]
        x_line_range = np.array([0, x_limit * 1.2])
        ax.plot(x_line_range, d0_intercept + slope * x_line_range, 'r--', label='Tangent', alpha=0.7, linewidth=1)
        ax.plot(x_line_range, d0_intercept + (slope / 1.15) * x_line_range, 'g--', label='1.15 Line', alpha=0.7, linewidth=1)

        # Capture top limit AFTER inversion and data: [1] is now the visual top (min data value)
        top_limit_frame = ax.get_ylim()[1]

        # 4. T90 Mark & Projections
        ax.plot(sqrt_t90, d90, 'ro', markersize=4, zorder=5)
        ax.vlines(x=sqrt_t90, ymin=top_limit_frame, ymax=d90, colors='black', linestyles=':', linewidth=0.8)
        ax.hlines(y=d90, xmin=0, xmax=sqrt_t90, colors='black', linestyles=':', linewidth=0.8)  
        
        # --- 5. Labels and Annotations (Fix for overlapping) ---
        ax.plot(0, d0_intercept, 'rs', markersize=4) 
        
        # d0: Place it ABOVE the point, aligned to the LEFT
        ax.annotate(f'd0={d0_intercept:.3f}', 
                    (0, d0_intercept), 
                    xytext=(50, -1), # Shift left and up
                    textcoords="offset points", 
                    color='red', fontweight='bold', fontsize=6,
                    ha='right', va='center')
        
        # t90: Place it BELOW the point, aligned to the RIGHT
        ax.annotate(f't90={t90:.2f}min', 
                    (sqrt_t90, d90), 
                    xytext=(10, 0), # Shift right and down
                    textcoords="offset points", 
                    color='red', fontweight='bold', fontsize=6,
                    ha='left', va='center')

        # Formatting (Smaller Fonts)
        ax.set_title('Taylor Root-Time Consolidation', fontsize=8)
        ax.set_xlabel(r'$\sqrt{Time}$ ($\sqrt{min}$)', fontsize=7)
        ax.set_ylabel('Settlement (mm)', fontsize=7)
        
        ax.tick_params(axis='both', labelsize=7) # Smaller axis numbers
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        ax.yaxis.set_minor_locator(MultipleLocator(0.010))
        ax.grid(True, which='both', linestyle=':', alpha=0.5)
        
        # Smaller legend
        ax.legend(loc='lower right', fontsize=7, framealpha=0.8)
        
        plt.savefig(save_path, dpi=150)
        plt.close()
        
        # Return result for LabVIEW
        print(f"SUCCESS|{t90:.4f}|{d0_intercept:.4f}|{save_path}")

    except Exception as e:
        print(f"ERROR|{str(e)}")

if __name__ == "__main__":
    # LabVIEW calls this as: python script.py "0,1,2" "0.1,0.2,0.3" "path/to/save.png"
    if len(sys.argv) > 3:
        arg_sqrt_t = sys.argv[1].split(',')
        arg_settle = sys.argv[2].split(',')
        arg_path = sys.argv[3]
        generate_plot(arg_sqrt_t, arg_settle, arg_path)
    else:
        print("ERROR: Missing arguments.")