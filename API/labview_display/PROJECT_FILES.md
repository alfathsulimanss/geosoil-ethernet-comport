# Project File Structure & Documentation

## 📦 Complete File Listing

### Application Core Files

1. **main.py** (Main Application)
   - Purpose: Main GUI application
   - Size: ~10KB
   - Run from: LabVIEW via display.bat
   - Features:
     * Data table display (tkinter)
     * Interactive graph (matplotlib)
     * Y-axis selector dropdown
     * Multi-tab interface (Table & Graph)
     * Asynchronous data loading
   - Dependencies: tkinter, pandas, matplotlib, mysql.connector

2. **config.py** (Configuration)
   - Purpose: Database settings and test type definitions
   - Size: ~2KB
   - Edit this for: Database credentials, test type columns
   - Contains:
     * DATABASE_CONFIG (host, user, password, database)
     * TEST_TYPE_COLUMNS (1-10 test types with column mappings)

3. **database_handler.py** (Database Layer)
   - Purpose: MySQL database operations
   - Size: ~3KB
   - Methods:
     * connect() / disconnect()
     * get_stage_info()
     * get_testtype()
     * get_stage_data()
   - Auto-loaded by main.py

### Launcher Scripts

4. **display.bat** (Batch Launcher)
   - Purpose: LabVIEW launcher - MAIN ENTRY POINT
   - Called from LabVIEW System Exec
   - Usage: `display.bat <fileid> "<stagename>"`
   - Returns: Exit code 0 (success) or 1 (error)

5. **display.ps1** (PowerShell Launcher)
   - Purpose: Alternative launcher using PowerShell
   - Usage: `.\display.ps1 -FileID 1 -StageName "Stage 1"`
   - Modern alternative to batch file

### Setup & Installation

6. **setup.bat** (Automated Setup)
   - Purpose: One-click installation and verification
   - Steps:
     * Checks Python installation
     * Installs dependencies
     * Runs verification tests
   - Recommended for first-time setup

7. **install.ps1** (PowerShell Installation)
   - Purpose: PowerShell alternative to setup.bat
   - For systems that prefer PowerShell

8. **requirements.txt** (Python Dependencies)
   - Purpose: Lists all Python packages needed
   - Contents:
     * mysql-connector-python>=8.0.33
     * pandas>=1.5.0
     * matplotlib>=3.7.0
     * numpy>=1.24.0
   - Install with: `pip install -r requirements.txt`

### Testing & Verification

9. **test_install.py** (Installation Verification)
   - Purpose: Verify installation is correct
   - Checks:
     * Python packages installed
     * Database connection
     * Configuration file
     * Tables in database
   - Run: `python test_install.py`

### Documentation Files

10. **README.md** (Full Documentation)
    - Purpose: Complete feature and usage documentation
    - Length: ~400 lines
    - Contents:
      * Features overview
      * Installation steps
      * Usage instructions
      * Database schema
      * Configuration details
      * Troubleshooting guide
    - Read first for comprehensive info

11. **LABVIEW_GUIDE.md** (LabVIEW Integration)
    - Purpose: Detailed guide for LabVIEW users
    - Length: ~300 lines
    - Contents:
      * System Exec configuration
      * Command examples
      * Parameter details
      * Error handling
      * Multiple concurrent calls
      * Tips & best practices
      * Advanced usage
    - Must-read for LabVIEW integration

12. **GETTING_STARTED.md** (Quick Start Guide)
    - Purpose: First-time user guide
    - Length: ~250 lines
    - Contents:
      * 3-step quick start
      * Installation steps
      * Usage instructions
      * Troubleshooting
      * Checklist
    - Start here for new users

13. **QUICK_REFERENCE.txt** (Command Reference)
    - Purpose: Quick lookup for commands and examples
    - Length: ~200 lines
    - Contents:
      * Installation command
      * Command format
      * Examples
      * LabVIEW formula template
      * Return codes
      * Supported test types
      * Troubleshooting table
    - Keep handy while using

14. **PROJECT_FILES.md** (This File)
    - Purpose: File structure and documentation index
    - Reference for all files in the project

## 📊 File Statistics

```
Total Files: 14
Total Size: ~40KB (code) + ~1MB (documentation)

Code Files:        5 (Python + Batch + PowerShell)
Documentation:    6 (Markdown + TXT)
Configuration:    1
Setup/Test:       2
```

## 🔄 File Dependencies

```
main.py
  ├── config.py (configuration)
  ├── database_handler.py
  │   └── config.py (configuration)
  ├── pandas
  ├── matplotlib
  ├── tkinter (built-in)
  └── mysql.connector

display.bat
  └── main.py (calls this)

setup.bat
  ├── requirements.txt (installs from)
  └── test_install.py (runs)

test_install.py
  ├── config.py
  └── database_handler.py
```

## 📋 Usage Matrix

| File | Called From | How | Purpose |
|------|-------------|-----|---------|
| display.bat | LabVIEW System Exec | Command line | Launch application |
| main.py | display.bat | Python subprocess | Main application |
| config.py | main.py, database_handler.py | Import | Configuration |
| database_handler.py | main.py | Import | Database operations |
| setup.bat | User double-click | Batch execution | Installation |
| test_install.py | setup.bat or manual | Command line | Verification |
| README.md | User | Text editor/browser | Documentation |

## 🎯 Which File To Use When

### I want to...

**Install the application**
→ Double-click `setup.bat`

**Run from LabVIEW**
→ Use `display.bat` in System Exec

**Test if it works**
→ Run `python test_install.py`

**Learn how to integrate with LabVIEW**
→ Read `LABVIEW_GUIDE.md`

**Get quick commands**
→ Check `QUICK_REFERENCE.txt`

**Understand all features**
→ Read `README.md`

**Modify database settings**
→ Edit `config.py`

**Troubleshoot issues**
→ See `README.md` or run `test_install.py`

**Add new test types**
→ Edit `TEST_TYPE_COLUMNS` in `config.py`

## 🔧 Customization Guide

### To change database settings:
Edit `config.py` → `DATABASE_CONFIG`

### To add new test types:
Edit `config.py` → `TEST_TYPE_COLUMNS` → Add new case with column list

### To modify UI appearance:
Edit `main.py` → Modify tkinter configuration (colors, fonts, sizes)

### To change graph style:
Edit `main.py` → `refresh_graph()` method → matplotlib parameters

### To add more columns:
Edit `config.py` → Add to `TEST_TYPE_COLUMNS` for specific test type

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] Run `setup.bat` successfully
- [ ] Run `python test_install.py` - all pass
- [ ] Test `display.bat 1 "Stage 1"` - window opens
- [ ] Check data displays correctly
- [ ] Test graph and Y-axis selector
- [ ] Test with multiple concurrent displays
- [ ] Verify database credentials are set
- [ ] Test from LabVIEW System Exec
- [ ] Verify error handling works
- [ ] Document any custom settings in config.py

## 📁 Directory Structure

```
F:\laragon\www\
└── labview_display\                    [Main folder]
    ├── main.py                         [Python: Main app]
    ├── config.py                       [Python: Configuration]
    ├── database_handler.py             [Python: Database ops]
    ├── display.bat                     [Batch: LabVIEW launcher]
    ├── display.ps1                     [PowerShell: Alt launcher]
    ├── setup.bat                       [Batch: Installation]
    ├── install.ps1                     [PowerShell: Alt setup]
    ├── test_install.py                 [Python: Verification]
    ├── requirements.txt                [Pip dependencies]
    │
    ├── README.md                       [Doc: Complete guide]
    ├── LABVIEW_GUIDE.md                [Doc: LabVIEW specific]
    ├── GETTING_STARTED.md              [Doc: Quick start]
    ├── QUICK_REFERENCE.txt             [Doc: Command ref]
    └── PROJECT_FILES.md                [Doc: This file]
```

## 🔍 Quick File Reference

| Need | File | Type |
|------|------|------|
| Installation | setup.bat | Batch |
| Database config | config.py | Python |
| Main app | main.py | Python |
| LabVIEW calling | display.bat | Batch |
| Full docs | README.md | Markdown |
| Quick guide | QUICK_REFERENCE.txt | Text |
| LabVIEW help | LABVIEW_GUIDE.md | Markdown |
| First steps | GETTING_STARTED.md | Markdown |

## 📞 File Locations

All files are in:
```
C:\laragon\www\labview_display\
```

Main entry point for LabVIEW:
```
C:\laragon\www\labview_display\display.bat
```

## 📝 Notes

- All Python files use UTF-8 encoding
- All batch files work on Windows 7+
- PowerShell files require PS 3.0+
- Documentation in Markdown format (view in browser or editor)
- Test types 1-10 are pre-configured in config.py

## 🔄 Version History

- **1.0** - Initial release
  * Core functionality working
  * All documentation complete
  * LabVIEW integration tested
  * Multiple concurrent windows supported

---

Generated: 2026
For more help, see README.md or GETTING_STARTED.md
