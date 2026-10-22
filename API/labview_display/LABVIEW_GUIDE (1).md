# LabVIEW Integration Guide

## Quick Start for LabVIEW Users

This guide explains how to call the Test Data Display application from LabVIEW.

## Setup (One-time)

### 1. Install Python Packages
```
Command Prompt:
cd C:\laragon\www\labview_display
pip install -r requirements.txt
```

Or run the setup script:
```
PowerShell (as Administrator):
.\install.ps1
```

### 2. Verify Installation
```
python test_install.py
```

All tests should pass before proceeding.

## Using from LabVIEW

### System Exec Configuration

In LabVIEW, use the **System Exec** node to call the display.

**Node Location**: Functions → Programming → OS Control → System Exec

### Basic Setup

1. **Create String Controls** for parameters:
   - `fileid` (numeric, convert to string)
   - `stage_name` (string)

2. **Set Command** in System Exec:
   ```
   C:\laragon\www\labview_display\display.bat %fileid% "%stage_name%"
   ```

   Or use a formula to build the command:
   ```
   "C:\laragon\www\labview_display\display.bat " + str(fileid) + " \"" + stage_name + "\""
   ```

### Example LabVIEW Code Structure

```
[Test File ID (numeric)] ──→ [Format to String] ──────┐
                                                       ├──→ [System Exec] ──→ [Wait for Completion]
[Stage Name (string)] ─────────────────────────────────┤
                                                       │
[Command String (formula)] ────────────────────────────┘
```

### Complete Command Examples

**Example 1: Single Stage Display**
```
C:\laragon\www\labview_display\display.bat 1 "Stage 1"
```

**Example 2: Multiple Simultaneous Displays**
```
Call 1: display.bat 1 "Stage 1"
Call 2: display.bat 1 "Stage 2"
Call 3: display.bat 2 "Stage 1"
```

All three windows can run simultaneously without interfering.

## Parameters

| Parameter | Type | Example | Notes |
|-----------|------|---------|-------|
| fileid | Integer | 1 | Must exist in database |
| stage_name | String | "Stage 1" | Must match database exactly (case-sensitive) |

## Error Handling in LabVIEW

The System Exec node provides error information:

- **Return Code 0**: Success
- **Return Code 1**: Missing parameters or invalid inputs
- **stderr output**: Database connection errors or data not found

Example handling:
```
if (System Exec Return Code != 0) {
    Display Error Message: System Exec stderr output
} else {
    Display Success Message
}
```

## Multiple Concurrent Windows

The application is designed to handle multiple concurrent calls:

```
[LabVIEW Main Loop]
├─ Call 1: display.bat 1 "Stage 1"
├─ Call 2: display.bat 1 "Stage 2"  (while Call 1 is running)
├─ Call 3: display.bat 2 "Stage 1"  (while Call 1 & 2 are running)
└─ All three windows display independently
```

Each window:
- Runs in its own Python process
- Has its own database connection
- Can be closed independently
- Does not affect other windows

## Tips & Best Practices

### 1. Parameter Construction
```LabVIEW String Formula:
"display.bat " + Num2Str(file_id) + " \"" + stage_name + "\""
```

### 2. Batch File Path
Use either:
- Relative path: `.\display.bat` (if in same directory)
- Absolute path: `C:\laragon\www\labview_display\display.bat`
- Add to PATH and use: `display.bat`

### 3. Stage Names with Special Characters
Always quote the stage name:
```
display.bat 1 "Stage 1"        ✓ Correct
display.bat 1 "Stage-1_Test"   ✓ Correct
display.bat 1 Stage 1          ✗ Wrong
```

### 4. Debugging
Create a test VI that logs commands before execution:
```
Write to File: [Command String] + "\n"
System Exec: [Command String]
```

Then verify the exact command being sent.

### 5. Performance Considerations
- Large datasets (1000+ rows) may take a few seconds
- Database queries run asynchronously
- Window appears once data is loaded

## Troubleshooting

### Display doesn't appear
1. Check System Exec error output
2. Verify file ID and stage name exist in database
3. Run `python test_install.py` to check database connection

### Data looks incomplete
1. Verify stage name matches exactly (case-sensitive)
2. Check if test type is correctly set in database
3. Ensure data exists for that file ID and stage

### "Connection Failed" error
1. Start MySQL service
2. Run `python test_install.py`
3. Verify database credentials in `config.py`

### Y-axis dropdown is empty
1. Ensure test type is set correctly in database
2. Verify data columns match configuration
3. Try refreshing the graph using the button

## Advanced Usage

### Logging System Exec Calls
Create a test VI to log all calls:
```
[System Exec Node] ──→ [Write File Dialog]
 ↓ (stderr)
[String to File]
```

### Handling Long-Running Displays
If you want to monitor while display is open:
```
[System Exec (Timeout = 0)]
├─ Allows display to run independently
└─ LabVIEW continues without waiting
```

## File Locations

- **Main Application**: `C:\laragon\www\labview_display\main.py`
- **Launcher**: `C:\laragon\www\labview_display\display.bat`
- **Database Config**: `C:\laragon\www\labview_display\config.py`
- **Logs**: Check Windows Event Viewer if needed

## Supported Test Types

When you call the display, the test type is automatically detected from the database:

| ID | Test Name | Measurement Columns |
|----|-----------|-------------------|
| 1 | Triaxial Compression (Drained) | 12 |
| 2 | Triaxial Compression (Undrained) | 9 |
| 3 | Direct Shear | 9 |
| 4 | Permeability | 12 |
| 5 | Consolidation | 5 |
| 6 | B-Value Test | 7 |
| 7 | Hollow Cylinder | 10 |
| 8 | Unconfined Compression | 7 |
| 9 | Pore Pressure Dissipation | 7 |
| 10 | Direct Tension | 2 |

## Example LabVIEW VI Structure

```
┌─────────────────────────────────────┐
│   Test Data Display VI              │
├─────────────────────────────────────┤
│ Inputs:                             │
│  - File ID (Number)                 │
│  - Stage Name (String)              │
│                                     │
│ [Build Command String] ─────────┐  │
│                                 │  │
│ [System Exec Node] ◄────────────┘  │
│  ├─ Command: display.bat ...      │
│  ├─ Return Code → 0?              │
│  └─ stderr ──→ Error Handler       │
│                                     │
│ Output:                             │
│  - Display Window (popup)           │
│  - Return Code                      │
│  - Error Message                    │
└─────────────────────────────────────┘
```

## Contact

For issues with the Python application, check `README.md` in the same folder.

---
Last Updated: 2026
