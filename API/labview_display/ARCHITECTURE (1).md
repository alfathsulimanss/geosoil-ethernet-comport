# Architecture & Flow Diagrams

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       LabVIEW                                   │
│                                                                 │
│  [File ID] ──────┐                                             │
│                  ├──→ [System Exec Node] ──→ display.bat      │
│  [Stage Name] ───┘                                             │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Command line call:
                             │ display.bat 1 "Stage 1"
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Windows System                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │             display.bat (Batch Script)              │       │
│  │                                                     │       │
│  │  - Receives fileid and stage_name                  │       │
│  │  - Launches Python process                         │       │
│  │  - Passes arguments to main.py                     │       │
│  └──────────────────────────┬──────────────────────────┘       │
│                             │                                   │
│                             ↓                                   │
│  ┌─────────────────────────────────────────────────────┐       │
│  │         main.py (Python Application)               │       │
│  │                                                     │       │
│  │  - Initializes GUI (tkinter)                       │       │
│  │  - Calls database_handler                          │       │
│  │  - Loads config                                    │       │
│  │  - Creates display window                          │       │
│  └──────────────┬──────────────────────────────────────┘       │
│                 │                                               │
│                 ↓                                               │
│  ┌─────────────────────────────────────────────────────┐       │
│  │     database_handler.py (Database Layer)            │       │
│  │                                                     │       │
│  │  - Connects to MySQL                              │       │
│  │  - Queries historydata table                       │       │
│  │  - Returns formatted data                          │       │
│  │  - Closes connection                               │       │
│  └──────────────┬──────────────────────────────────────┘       │
│                 │                                               │
│                 ↓                                               │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MySQL Database                               │
│                  (projectdata)                                  │
│                                                                 │
│  ┌──────────────────────────────┐                              │
│  │  historydata table           │                              │
│  │  - timestamp                 │                              │
│  │  - elapsetime                │                              │
│  │  - fileid                    │                              │
│  │  - testname (stage name)     │                              │
│  │  - testtype                  │                              │
│  │  - [measurement columns]     │                              │
│  └──────────────────────────────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Application Data Flow

```
START
  │
  ├─→ Parse command line arguments
  │   ├─ fileid (e.g., "1")
  │   └─ stage_name (e.g., "Stage 1")
  │
  ├─→ Load config.py
  │   ├─ Database settings
  │   └─ Test type definitions
  │
  ├─→ Initialize GUI window (tkinter)
  │   ├─ Create main frame
  │   ├─ Add control bar
  │   └─ Create tabs (Table, Graph)
  │
  ├─→ Start async data loading thread
  │   │
  │   ├─→ Connect to MySQL database
  │   │   └─ Check connection success
  │   │
  │   ├─→ Query database
  │   │   ├─ Get testtype from fileid
  │   │   ├─ Get columns for testtype
  │   │   └─ Execute SELECT query
  │   │
  │   └─→ Return data to main thread
  │       ├─ Convert to DataFrame
  │       └─ Populate table
  │
  ├─→ Display data table
  │   ├─ Set column headers
  │   ├─ Insert rows
  │   └─ Enable scrolling
  │
  ├─→ Update Y-axis dropdown
  │   ├─ Get available columns
  │   ├─ Populate dropdown
  │   └─ Select first column
  │
  ├─→ Display initial graph
  │   ├─ Create matplotlib figure
  │   ├─ Plot X: elapsed time
  │   ├─ Plot Y: first column
  │   └─ Embed in tkinter
  │
  ├─→ Wait for user interaction
  │   │
  │   ├─ Y-axis changed?
  │   │  └─→ Redraw graph with new Y-axis
  │   │
  │   ├─ Refresh button clicked?
  │   │  └─→ Redraw graph
  │   │
  │   └─ Window closed?
  │       └─→ Go to END
  │
  └─→ END
```

## 🪟 GUI Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│  Test Data Viewer - File ID: 1 | Stage: Stage 1             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Controls                                               │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Select Y-Axis: [Dropdown ▼] [Refresh] Status: ...     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────┬──────────────────────────────────────┐ │
│  │ Data Table  │   │ Graph                                │ │
│  │             │   │                                      │ │
│  │ ┌─────────┐ │   │ ┌──────────────────────────────────┐│ │
│  │ │timestamp│ │   │ │  [Graph Plot]                    ││ │
│  │ │elapstime│ │   │ │                                  ││ │
│  │ │Column 1 │ │   │ │                                  ││ │
│  │ │Column 2 │ │   │ │                                  ││ │
│  │ │Column 3 │ │   │ │  Y: Selected Column              ││ │
│  │ │   ...   │ │   │ │  X: Elapsed Time                 ││ │
│  │ │         │ │   │ │                                  ││ │
│  │ │[Scroll] │ │   │ │                                  ││ │
│  │ └─────────┘ │   │ └──────────────────────────────────┘│ │
│  │             │   │                                      │ │
│  └─────────────┴──────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 🗄️ Database Query Flow

```
┌────────────────────────────────────┐
│  Receive fileid and stage_name     │
│  (from LabVIEW via command line)   │
└────────────────┬───────────────────┘
                 │
                 ↓
┌────────────────────────────────────┐
│  Query 1: Get testtype             │
│  SELECT testtype FROM stage        │
│  WHERE filename = fileid           │
│  LIMIT 1                           │
└────────────────┬───────────────────┘
                 │
                 ├─→ Found? 
                 │   └─→ Yes: Use testtype
                 │   └─→ No: Try historydata
                 │
                 ↓
┌────────────────────────────────────┐
│  Query 2: Get columns for testtype │
│  (from TEST_TYPE_COLUMNS config)   │
│                                    │
│  Test Type 1 → 12 columns          │
│  Test Type 2 → 9 columns           │
│  Test Type 3 → 9 columns           │
│  ... etc                           │
└────────────────┬───────────────────┘
                 │
                 ↓
┌────────────────────────────────────┐
│  Query 3: Get data                 │
│  SELECT timestamp, elapsetime,     │
│         [all columns]              │
│  FROM historydata                  │
│  WHERE fileid = fileid AND         │
│        testname = stage_name       │
│  ORDER BY elapsetime ASC           │
└────────────────┬───────────────────┘
                 │
                 ↓
┌────────────────────────────────────┐
│  Return results to GUI             │
│  - DataFrame with all rows         │
│  - Column info with test type name │
└────────────────────────────────────┘
```

## 🎯 Processing Pipeline

```
INPUT
  │
  ├─→ Argument Validation
  │   ├─ fileid present?
  │   ├─ stage_name present?
  │   └─ Both non-empty?
  │
  ├─→ Configuration Loading
  │   ├─ Load DATABASE_CONFIG
  │   └─ Load TEST_TYPE_COLUMNS
  │
  ├─→ Database Connection
  │   ├─ Connect to localhost
  │   ├─ Authenticate with root / no password
  │   ├─ Select projectdata database
  │   └─ Check for errors
  │
  ├─→ Data Retrieval
  │   ├─ Determine testtype
  │   ├─ Get column mapping
  │   ├─ Execute SELECT query
  │   └─ Return as list of dicts
  │
  ├─→ Data Processing
  │   ├─ Convert to pandas DataFrame
  │   ├─ Handle NULL/NaN values
  │   ├─ Convert numeric columns
  │   └─ Sort by elapsed time
  │
  ├─→ UI Population
  │   ├─ Display table with all columns
  │   ├─ Populate Y-axis dropdown
  │   ├─ Generate initial graph
  │   └─ Show status message
  │
  ├─→ User Interaction
  │   ├─ Listen for dropdown changes
  │   ├─ Listen for refresh clicks
  │   ├─ Listen for window close
  │   └─ Update graph on selection
  │
  └─→ OUTPUT
      ├─ Display window open
      ├─ Data visible in table
      ├─ Graph displayed
      └─ User can interact
```

## 🔌 LabVIEW Integration Flow

```
LabVIEW Program
     │
     ├─→ Build command string
     │   "C:\...\display.bat 1 \"Stage 1\""
     │
     ├─→ System Exec node
     │   ├─ Command: [string from above]
     │   ├─ Return Code output
     │   └─ stderr output
     │
     ├─→ Wait for execution
     │   └─ Window opens (display.bat launches main.py)
     │
     └─→ Get return code
         ├─ 0 = Success
         └─ 1 = Error (check stderr)

Parallel Execution Scenario:
     │
     ├─→ Call 1: display.bat 1 "Stage 1"
     │   └─→ Window 1 opens (Python process 1)
     │
     ├─→ Call 2: display.bat 1 "Stage 2" (while Call 1 running)
     │   └─→ Window 2 opens (Python process 2)
     │
     └─→ Call 3: display.bat 2 "Stage 1" (while Call 1 & 2 running)
         └─→ Window 3 opens (Python process 3)

All three windows run independently without interference!
```

## 📊 Test Type Configuration Structure

```
config.py
│
└─ TEST_TYPE_COLUMNS (dictionary)
   │
   ├─ 1: {
   │      'name': 'Triaxial Compression (Drained)',
   │      'columns': [
   │        'Cell Pressure',
   │        'Back Pressure',
   │        'Volume Change',
   │        ... (12 total)
   │      ]
   │    }
   │
   ├─ 2: { ... }  # 9 columns
   ├─ 3: { ... }  # 9 columns
   ├─ 4: { ... }  # 12 columns
   ├─ 5: { ... }  # 5 columns
   ├─ 6: { ... }  # 7 columns
   ├─ 7: { ... }  # 10 columns
   ├─ 8: { ... }  # 7 columns
   ├─ 9: { ... }  # 7 columns
   └─ 10: { ... } # 2 columns
```

## 🔄 Window Management

```
Operating System
│
├─ Process 1: display.bat 1 "Stage 1"
│  └─ Python process
│     └─ Window 1 (independent, can close anytime)
│
├─ Process 2: display.bat 1 "Stage 2"
│  └─ Python process
│     └─ Window 2 (independent, can close anytime)
│
└─ Process 3: display.bat 2 "Stage 1"
   └─ Python process
      └─ Window 3 (independent, can close anytime)

Each process:
- Has own memory space
- Has own database connection
- Has own GUI state
- Can run indefinitely
- Can be terminated independently
```

## 🎨 Graph Rendering Pipeline

```
Selected Y-Axis Column
         │
         ↓
Get numeric data
         │
         ├─→ Extract elapsetime (X-axis)
         ├─→ Extract column values (Y-axis)
         │
         ↓
Clean data (remove NaN)
         │
         ↓
Create matplotlib Figure
         │
         ├─→ Create subplot
         ├─→ Plot line with markers
         ├─→ Set labels and title
         ├─→ Enable grid
         │
         ↓
Embed in tkinter canvas
         │
         ├─→ Create FigureCanvasTkAgg
         ├─→ Draw on canvas
         ├─→ Pack in frame
         │
         ↓
Display to user
```

---

**Last Updated**: 2026

For detailed information about each component, see:
- README.md - Complete documentation
- LABVIEW_GUIDE.md - LabVIEW integration
- QUICK_REFERENCE.txt - Command reference
