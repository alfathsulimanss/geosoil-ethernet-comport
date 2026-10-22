# Getting Started - LabVIEW Test Data Display

## 📋 Overview

This application displays test data from your MySQL database in an interactive GUI with data tables and graphs. It's designed to be called from LabVIEW's System Exec node.

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
Double-click: setup.bat
```
This will install all required Python packages and verify your setup.

### Step 2: Test the Installation
The setup script will automatically test everything. If all checks pass, you're ready!

### Step 3: Call from LabVIEW
In your LabVIEW VI, use System Exec with:
```
C:\laragon\www\labview_display\display.bat 1 "Stage 1"
```

Replace `1` with your file ID and `"Stage 1"` with your stage name.

## 📁 File Structure

```
labview_display/
├── setup.bat                   ← Run this first!
├── display.bat                 ← Called from LabVIEW
├── main.py                     ← Main application
├── config.py                   ← Configuration
├── database_handler.py         ← Database operations
├── test_install.py             ← Verification script
│
├── README.md                   ← Full documentation
├── LABVIEW_GUIDE.md            ← Detailed LabVIEW guide
├── QUICK_REFERENCE.txt         ← Quick command reference
└── GETTING_STARTED.md          ← This file
```

## 🔧 Installation Steps

### Option A: Automated Setup (Recommended)

1. Navigate to the folder:
   ```
   C:\laragon\www\labview_display
   ```

2. Double-click **setup.bat**

3. Wait for installation to complete

4. If all tests pass, you're done!

### Option B: Manual Setup

1. Open Command Prompt

2. Navigate to the folder:
   ```bash
   cd C:\laragon\www\labview_display
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify installation:
   ```bash
   python test_install.py
   ```

5. All checks should pass ✓

## 📝 Using the Application

### From LabVIEW (System Exec Node)

**Basic Format:**
```
C:\laragon\www\labview_display\display.bat <fileid> "<stagename>"
```

**Example:**
```
C:\laragon\www\labview_display\display.bat 1 "Stage 1"
```

### From Command Line (For Testing)

```bash
python C:\laragon\www\labview_display\main.py 1 "Stage 1"
```

## 🎨 User Interface

When you call the application, a window opens with:

1. **Control Bar** (Top)
   - Y-Axis Dropdown: Choose which measurement to plot
   - Refresh Button: Update the graph
   - Status Display: Shows test type and record count

2. **Data Table Tab**
   - Shows all test measurements
   - Scrollable in both directions
   - Includes timestamp and elapsed time

3. **Graph Tab**
   - Line plot with data points
   - X-axis: Elapsed Time (seconds)
   - Y-axis: Selected measurement
   - Interactive and resizable

## 🔄 Multiple Concurrent Displays

The application handles multiple simultaneous calls seamlessly:

```
Time:  Call 1 → Window 1 opens
       Call 2 → Window 2 opens (Call 1 still running)
       Call 3 → Window 3 opens (Call 1 & 2 still running)
       All three windows display independently
```

Each window runs in its own Python process and can be closed independently.

## ⚙️ Configuration

### Database Settings

Edit **config.py** to modify database connection:

```python
DATABASE_CONFIG = {
    'host': 'localhost',      # Your MySQL host
    'user': 'root',           # Your MySQL user
    'password': '',           # Your MySQL password
    'database': 'projectdata' # Your database name
}
```

### Test Types

Test types are automatically detected from the database. Configuration in **config.py**:

```python
TEST_TYPE_COLUMNS = {
    1: {'name': 'Test Name', 'columns': [...]},
    2: {'name': 'Test Name', 'columns': [...]},
    # ... more types
}
```

## 🐛 Troubleshooting

### Problem: "Connection Failed"
**Solution:**
1. Verify MySQL is running
2. Check database credentials in `config.py`
3. Run `python test_install.py`

### Problem: "No Data Found"
**Solution:**
1. Verify file ID exists in database
2. Check stage name matches exactly (case-sensitive)
3. Confirm data exists in the historydata table

### Problem: Y-axis dropdown is empty
**Solution:**
1. Ensure test type is set correctly in database
2. Verify column names match configuration
3. Try the "Refresh Graph" button

### Problem: Window doesn't appear
**Solution:**
1. Check System Exec error output in LabVIEW
2. Verify parameters are passed correctly
3. Run `test_install.py` to diagnose

## 📚 Documentation Files

- **README.md** - Complete feature documentation
- **LABVIEW_GUIDE.md** - Detailed LabVIEW integration guide
- **QUICK_REFERENCE.txt** - Command quick reference
- **GETTING_STARTED.md** - This file

## ✅ Verification Checklist

After installation, verify:

- [ ] Python 3.7+ installed
- [ ] All packages installed (`pip list` should show mysql-connector, pandas, matplotlib)
- [ ] MySQL running on localhost
- [ ] `test_install.py` passes all checks
- [ ] Can call `display.bat 1 "Stage 1"` successfully
- [ ] Data table appears with records
- [ ] Graph displays correctly

## 🎯 Next Steps

1. ✅ Run `setup.bat` to install
2. ✅ Verify with `test_install.py`
3. ✅ Test command: `display.bat 1 "Stage 1"`
4. ✅ Integrate with LabVIEW (see LABVIEW_GUIDE.md)
5. ✅ Set up System Exec node in your VI

## 💡 Tips

### For LabVIEW Integration
- Use absolute paths: `C:\laragon\www\labview_display\display.bat`
- Always quote stage names: `"Stage 1"` not `Stage 1`
- Use System Exec return code for error handling

### For Multiple Displays
- No limit on concurrent windows
- Each has independent database connection
- Close them individually as needed

### For Performance
- Large datasets (1000+ rows) may take a few seconds
- Graph updates are responsive
- Data loads asynchronously

## 📞 Getting Help

1. Check **LABVIEW_GUIDE.md** for LabVIEW-specific issues
2. Run **test_install.py** to diagnose problems
3. Check database credentials in **config.py**
4. Verify data exists in your database

## 🎓 Example LabVIEW Code

```LabVIEW String Formula:
"C:\laragon\www\labview_display\display.bat " + Num2Str(file_id) + " \"" + stage_name + "\""
```

Pass this to System Exec node.

## 📖 Test Type Reference

| ID | Test Type | Measurements |
|----|-----------|--------------|
| 1 | Triaxial Compression (Drained) | 12 |
| 2 | Triaxial Compression (Undrained) | 9 |
| 3 | Direct Shear | 9 |
| 4 | Permeability | 12 |
| 5 | Consolidation | 5 |
| 6 | B-Value | 7 |
| 7 | Hollow Cylinder | 10 |
| 8 | Unconfined Compression | 7 |
| 9 | Pore Pressure Dissipation | 7 |
| 10 | Direct Tension | 2 |

## ⚡ Requirements

- **Python**: 3.7 or higher
- **MySQL**: Running on localhost
- **Disk Space**: ~200MB for dependencies
- **RAM**: Minimal (< 100MB per window)
- **OS**: Windows 7+ (with Python)

## 📋 What's Included

```
✓ Python application with GUI
✓ Data table display
✓ Interactive graph
✓ Y-axis selector dropdown
✓ Database connectivity
✓ Multiple concurrent window support
✓ LabVIEW integration (System Exec)
✓ Full documentation
✓ Installation helper
✓ Test/verification script
```

---

**Ready to start?** Double-click `setup.bat` and follow the on-screen instructions!

Last Updated: 2026
