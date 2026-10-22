import sys
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MultipleLocator
import threading
from database_handler import DatabaseHandler
from config import TEST_TYPE_COLUMNS

class DataDisplayApp:
    def __init__(self, root, fileid, stage_name):
        self.root = root
        self.fileid = fileid
        self.stage_name = stage_name
        self.db = DatabaseHandler()
        self.data = None
        self.columns_info = None
        self.selected_y_axis = None
        
        # Configure window
        self.root.title(f"Test Data Viewer - File ID: {fileid} | Stage: {stage_name}")
        self.root.geometry("900x600")
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top control frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=5)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Y-axis selection dropdown
        ttk.Label(control_frame, text="Select Y-Axis:").pack(side=tk.LEFT, padx=5)
        self.y_axis_var = tk.StringVar()
        self.y_axis_dropdown = ttk.Combobox(control_frame, textvariable=self.y_axis_var, state='readonly', width=30)
        self.y_axis_dropdown.pack(side=tk.LEFT, padx=5)
        self.y_axis_dropdown.bind('<<ComboboxSelected>>', self.on_y_axis_changed)
        
        # Refresh button
        ttk.Button(control_frame, text="Refresh Graph", command=self.refresh_graph).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Loading data...", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Table tab
        table_frame = ttk.Frame(self.notebook)
        self.notebook.add(table_frame, text="Data Table")
        
        # Create Treeview for table display
        tree_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree = ttk.Treeview(
            table_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Graph tab
        graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(graph_frame, text="Graph")
        self.graph_frame = graph_frame
        
        # Load data asynchronously
        loading_thread = threading.Thread(target=self.load_data, daemon=True)
        loading_thread.start()
    
    def load_data(self):
        """Load data from database"""
        try:
            print(f"Loading data for: fileid={self.fileid}, stage_name={self.stage_name}")
            
            if not self.db.connect():
                self.show_error("Database Connection Failed", 
                              "Could not connect to database.\n\n"
                              "Check:\n"
                              "- MySQL is running\n"
                              "- config.py has correct credentials\n"
                              "- Database 'projectdata' exists")
                return
            
            print("Database connected")
            
            # Get available stages for debugging
            available_stages = self.db.get_available_stages(self.fileid)
            print(f"Available stages: {available_stages}")
            
            if self.stage_name not in available_stages:
                stages_str = "\n".join([f"  - {s}" for s in available_stages]) if available_stages else "  (None found)"
                self.show_error("Stage Not Found", 
                              f"Stage '{self.stage_name}' not found.\n\n"
                              f"Available stages for File ID {self.fileid}:\n{stages_str}\n\n"
                              "Check:\n"
                              "- Stage name spelling (case-sensitive)\n"
                              "- File ID exists\n"
                              "- Data exists in database")
                return
            
            self.data, self.columns_info = self.db.get_stage_data(self.fileid, self.stage_name)
            self.db.disconnect()
            
            if self.data is None:
                self.show_error("Data Not Found", 
                              f"No data found for File ID: {self.fileid}, Stage: {self.stage_name}\n\n"
                              "Check:\n"
                              "- File ID and stage name are correct\n"
                              "- Data exists in historydata table\n"
                              "- Test type is properly configured")
                return
            
            if len(self.data) == 0:
                self.show_error("Empty Result", 
                              f"No records found in the database for this stage.\n\n"
                              "File ID: {self.fileid}\n"
                              "Stage: {self.stage_name}")
                return
            
            print(f"Data loaded successfully: {len(self.data)} records")
            
            # Update UI in main thread
            self.root.after(0, self.display_data)
            
        except Exception as e:
            print(f"Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            self.show_error("Error", f"An error occurred:\n\n{str(e)}")

    
    def display_data(self):
        """Display loaded data in table and update dropdowns"""
        try:
            if not self.data:
                return
            
            # Update status
            self.status_label.config(text=f"Test Type: {self.columns_info['name']} | Records: {len(self.data)}", foreground="green")
            
            # Convert to DataFrame for easier handling
            df = pd.DataFrame(self.data)
            
            # Display table
            self.display_table(df)
            
            # Update Y-axis dropdown with available columns
            available_columns = self.columns_info['columns']
            self.y_axis_dropdown['values'] = available_columns
            if available_columns:
                self.y_axis_dropdown.current(0)
                self.selected_y_axis = available_columns[0]
            
            # Display initial graph
            self.refresh_graph()
            
        except Exception as e:
            self.show_error("Display Error", f"Error displaying data: {str(e)}")
    
    def display_table(self, df):
        """Display data in treeview table"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Set columns
            self.tree['columns'] = list(df.columns)
            self.tree.column('#0', width=0, stretch=tk.NO)
            
            # Configure column headings and widths
            for col in df.columns:
                self.tree.column(col, anchor=tk.W, width=100)
                self.tree.heading(col, text=col, anchor=tk.W)
            
            # Add data rows
            for idx, row in df.iterrows():
                values = [row[col] for col in df.columns]
                self.tree.insert('', tk.END, values=values)
            
        except Exception as e:
            print(f"Table display error: {e}")
    
    def on_y_axis_changed(self, event=None):
        """Handle Y-axis dropdown change"""
        self.selected_y_axis = self.y_axis_var.get()
        self.refresh_graph()
    
    def refresh_graph(self):
        """Refresh the graph with selected Y-axis"""
        try:
            if not self.data or not self.selected_y_axis:
                return
            
            # Clear previous graph
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            # Convert to DataFrame
            df = pd.DataFrame(self.data)
            
            # Create figure
            fig = Figure(figsize=(10, 5), dpi=100)
            ax = fig.add_subplot(111)
            
            # Convert elapsetime from TIME format (HH:MM:SS) to numeric seconds
            def time_to_seconds(time_str):
                """Convert HH:MM:SS to total seconds"""
                if pd.isna(time_str):
                    return None
                try:
                    time_str = str(time_str).strip()
                    parts = time_str.split(':')
                    if len(parts) == 3:
                        hours, minutes, seconds = map(float, parts)
                        return hours * 3600 + minutes * 60 + seconds
                    else:
                        # Try to convert directly if already numeric
                        return float(time_str)
                except:
                    return None
            
            # Apply conversion
            x_data = df['elapsetime'].apply(time_to_seconds)
            y_data = pd.to_numeric(df[self.selected_y_axis], errors='coerce')
            
            # Remove NaN values
            mask = ~(pd.isna(x_data) | pd.isna(y_data))
            x_data = x_data[mask]
            y_data = y_data[mask]
            
            # Debug output
            print(f"\n[GRAPH] Plotting graph:")
            print(f"  X-axis (elapsed time) - min: {x_data.min():.2f}s, max: {x_data.max():.2f}s")
            print(f"  Y-axis ({self.selected_y_axis}) - min: {y_data.min():.4f}, max: {y_data.max():.4f}")
            print(f"  Data points: {len(x_data)}")
            
            if len(x_data) == 0:
                print(f"  [ERROR] No valid data points to plot!")
                error_label = ttk.Label(self.graph_frame, text="No valid data to plot", foreground="red")
                error_label.pack(padx=10, pady=10)
                return
            
            # Plot
            ax.plot(x_data, y_data, 'b-', linewidth=1.5, marker='o', markersize=3)
            
            # Format x-axis to display time as HH:MM:SS (30-minute intervals)
            def seconds_to_time_str(seconds, pos):
                """Convert seconds to HH:MM:SS format"""
                total_seconds = int(seconds)
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                secs = 0  # Always show 00 for seconds on major grid
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            formatter = FuncFormatter(seconds_to_time_str)
            ax.xaxis.set_major_formatter(formatter)
            
            # Auto-determine interval based on total time range
            total_time = x_data.max() - x_data.min()
            if total_time <= 3600:  # <= 1 hour: use 10-minute intervals
                interval = 600  # 10 minutes
            elif total_time <= 10800:  # <= 3 hours: use 30-minute intervals
                interval = 1800  # 30 minutes
            else:  # > 3 hours: use 1-hour intervals
                interval = 3600  # 1 hour
            
            ax.xaxis.set_major_locator(MultipleLocator(interval))
            
            ax.set_xlabel('Elapsed Time (HH:MM:SS)', fontsize=10)
            ax.set_ylabel(self.selected_y_axis, fontsize=10)
            ax.set_title(f"{self.columns_info['name']} - {self.selected_y_axis} vs Time", fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            fig.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add hover tooltip
            self._add_hover_tooltip(canvas, fig, ax, x_data, y_data)
            
            print(f"[OK] Graph rendered successfully")
            
        except Exception as e:
            print(f"[ERROR] Graph error: {e}")
            import traceback
            traceback.print_exc()
            error_label = ttk.Label(self.graph_frame, text=f"Error displaying graph: {str(e)}", foreground="red")
            error_label.pack(padx=10, pady=10)
    
    
    def _add_hover_tooltip(self, canvas, fig, ax, x_data, y_data):
        """Add hover tooltip to graph showing X,Y values"""
        import numpy as np
        
        # Create annotation (initially hidden)
        annot = ax.annotate("", xy=(0, 0), xytext=(10, 10),
                           textcoords="offset points",
                           bbox=dict(boxstyle="round,pad=0.7", facecolor="gray", edgecolor="black", linewidth=1),
                           arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0", color="black"),
                           fontsize=8,
                           color="white")
        annot.set_visible(False)
        
        # Store data as numpy arrays for distance calculation
        x_array = np.array(x_data.values)
        y_array = np.array(y_data.values)
        
        def on_hover(event):
            """Handle mouse hover event"""
            if event.inaxes != ax or event.xdata is None or event.ydata is None:
                annot.set_visible(False)
                fig.canvas.draw_idle()
                return
            
            try:
                # Get axis limits for normalization
                x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
                y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
                
                # Calculate normalized distance to each point
                x_dist = (x_array - event.xdata) / x_range
                y_dist = (y_array - event.ydata) / y_range
                dist = np.sqrt(x_dist**2 + y_dist**2)
                
                # Find nearest point
                closest_idx = np.argmin(dist)
                
                # Threshold for showing tooltip
                if dist[closest_idx] < 0.05:
                    x_val = x_array[closest_idx]
                    y_val = y_array[closest_idx]
                    
                    # Convert seconds back to HH:MM:SS
                    hours = int(x_val) // 3600
                    minutes = (int(x_val) % 3600) // 60
                    seconds = int(x_val) % 60
                    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    
                    # Smart positioning to keep tooltip inside plot area
                    offset_x = 10
                    offset_y = 10
                    
                    # If point is in upper half, move tooltip down (inside)
                    if y_val > (ax.get_ylim()[0] + ax.get_ylim()[1]) / 2:
                        offset_y = -40
                    
                    # If point is in right half, move tooltip left (inside)
                    if x_val > (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2:
                        offset_x = -100
                    
                    annot.xytext = (offset_x, offset_y)
                    
                    # Update annotation
                    annot.xy = (x_val, y_val)
                    annot.set_text(f"Time: {time_str}\n{self.selected_y_axis}: {y_val:.4f}")
                    annot.set_visible(True)
                else:
                    annot.set_visible(False)
            except Exception as e:
                print(f"[ERROR] Hover tooltip error: {e}")
                annot.set_visible(False)
            
            fig.canvas.draw_idle()
        
        # Connect hover event
        canvas.mpl_connect("motion_notify_event", on_hover)
    
    def show_error(self, title, message):
        """Show error message"""
        print(f"[ERROR] {title}: {message}")
        self.root.after(0, lambda: messagebox.showerror(title, message))

def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        messagebox.showerror("Error", "Usage: python main.py <fileid> <stage_name>\n\nExample: python main.py 1 'Stage 1'")
        return
    
    fileid = sys.argv[1]
    stage_name = sys.argv[2]
    
    root = tk.Tk()
    app = DataDisplayApp(root, fileid, stage_name)
    root.mainloop()

if __name__ == '__main__':
    main()
