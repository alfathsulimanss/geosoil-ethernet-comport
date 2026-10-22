# LabVIEW Test Data Display Application

A Python-based GUI application for displaying test data and graphs from your MySQL database, designed to be called from LabVIEW.

## Features

- **Data Table Display**: Shows all test data in a scrollable table format
- **Dynamic Graph**: Displays data with selected Y-axis and time-based X-axis
- **Y-Axis Selector**: Dropdown to choose which measurement to plot
- **Automatic Column Mapping**: Columns are automatically mapped based on test type
- **Multiple Concurrent Displays**: Can handle multiple simultaneous data displays
- **Native Windows Integration**: Uses tkinter for native Windows appearance

## Installation

### Prerequisites
- Python 3.7 or higher
- MySQL database (localhost, no password required by default)

### Setup Steps

1. **Install Python Dependencies**
   ```bash
   cd f:\laragon\www\labview_display
   pip install -r requirements.txt
   ```

2. **Verify Database Connection**
   - Ensure MySQL is running on localhost
   - Database name: `projectdata`
   - User: `root`
   - Password: (empty)

## Usage

### From LabVIEW (System Exec)

#### Basic Syntax
```
display.bat <fileid> <stage_name>
```

#### Examples

1. **Single Display**
   ```
   display.bat 1 "Stage 1"
   ```

2. **Multiple Concurrent Displays**
   - Call 1: `display.bat 1 "Stage 1"`
   - Call 2: `display.bat 1 "Stage 2"` (while first is running)
   - Call 3: `display.bat 2 "Stage 1"` (while previous are running)

### From Command Line (Direct)

```bash
python main.py 1 "Stage 1"
```

## Application Interface

### Window Layout

1. **Control Bar** (Top)
   - Y-Axis Dropdown: Select which measurement to display on the graph
   - Refresh Button: Update the graph with new data
   - Status Display: Shows test type name and record count

2. **Data Table Tab**
   - Shows all records in a scrollable table
   - Columns: timestamp, elapsetime, and all test-specific measurements
   - Sortable and scrollable in both directions

3. **Graph Tab**
   - Line plot with markers
   - X-axis: Elapsed Time (seconds)
   - Y-axis: Selected measurement
   - Grid enabled for easy reading

## Supported Test Types

| Type | Name | Columns |
|------|------|---------|
| 1 | Triaxial Compression (Drained) | 12 columns |
| 2 | Triaxial Compression (Undrained) | 9 columns |
| 3 | Direct Shear Test | 9 columns |
| 4 | Permeability Test | 12 columns |
| 5 | Consolidation Test | 5 columns |
| 6 | B-Value Test | 7 columns |
| 7 | Hollow Cylinder Test | 10 columns |
| 8 | Unconfined Compression | 7 columns |
| 9 | Pore Pressure Dissipation | 7 columns |
| 10 | Direct Tension Test | 2 columns |

## Database Schema Requirements

### Tables Used
- **historydata**: Contains test measurements
  - Fields: timestamp, elapsetime, fileid, testname, testtype, and measurement columns
- **stage**: Contains stage information
  - Fields: filename, stage, testplan, status, station, delete flag

## Configuration

Edit `config.py` to modify:
- Database connection settings (host, user, password, database)
- Test type column definitions
- Add new test types if needed

## Troubleshooting

### "Connection Failed" Error
- Check if MySQL is running
- Verify database credentials in `config.py`
- Check if database name is `projectdata`

### "No Data Found" Error
- Verify fileid exists in the database
- Verify stage name matches exactly (case-sensitive)
- Check if records exist in historydata table

### Missing Dropdown Values
- Ensure test type is correctly set in the database
- Verify column names match exactly with database

### Graph Not Displaying
- Check if Y-axis column exists in the data
- Verify data contains valid numeric values
- Click "Refresh Graph" button

## Command Line Arguments

| Parameter | Type | Description |
|-----------|------|-------------|
| fileid | Integer | The file ID to display |
| stage_name | String | The stage name (must match database exactly) |

## Notes for LabVIEW Integration

1. **Batch File Path**: Use full path or add folder to system PATH
   ```
   C:\laragon\www\labview_display\display.bat 1 "Stage 1"
   ```

2. **Stage Name with Spaces**: Always wrap in quotes
   ```
   display.bat 1 "Stage Name With Spaces"
   ```

3. **Multiple Windows**: Each call creates a separate window - they don't interfere with each other

4. **Error Handling**: Check the return code (exit code) in LabVIEW:
   - 0 = Success
   - 1 = Missing parameters

## Performance Notes

- Data tables with 1000+ rows may take a few seconds to display
- Graph updates are responsive even with large datasets
- Each display runs in its own Python process (isolated)

## File Structure

```
labview_display/
├── main.py                 # Main application
├── config.py               # Configuration and test type mappings
├── database_handler.py      # Database operations
├── display.bat             # LabVIEW launcher script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Contact & Support

For issues or feature requests, check the database schema and verify data integrity first.

---
Created: 2026
Last Updated: 2026
