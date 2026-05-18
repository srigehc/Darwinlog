# 🆘 Troubleshooting Guide - Darwin Log Compare

## Common Issues & Solutions

### 🔴 Error: "'C:\Program' is not recognized as an internal or external command"

**What this means:**
Python is installed in a directory with spaces in the path (like `C:\Program Files\Python\...`), and the batch file isn't handling it correctly.

**Quick Fixes (try these first):**

#### Option A: Use PowerShell Instead ⭐ EASIEST
```
1. Right-click RUN.ps1
2. Select "Run with PowerShell"
3. Click "Yes" if prompted about execution policy
```
PowerShell handles paths with spaces automatically.

#### Option B: Install Python to a Path Without Spaces
```
1. Go to Control Panel → Programs → Uninstall a Program
2. Find "Python" and click "Uninstall"
3. Download Python from https://www.python.org/
4. During installation:
   - Click "Customize Installation"
   - For install location, choose: C:\Python311
   - ✓ Check "Add Python to PATH"
5. Click "Install"
6. Restart your computer
7. Try RUN.bat again
```

#### Option C: Run from Command Line
```
1. Press Windows key + R
2. Type: cmd
3. Press Enter
4. Type: cd /d "C:\Users\YOUR_USERNAME\Downloads\Darwin log compare"
5. Type: python setup_and_run.py
6. Press Enter
```

#### Option D: Use Administrator Privileges
```
1. Right-click Command Prompt (cmd.exe)
2. Select "Run as Administrator"
3. Navigate to the folder
4. Run: python setup_and_run.py
```

---

### 🔴 Error: "Python is not installed or not in PATH"

**What this means:**
Python isn't installed, or the system can't find it.

**Solutions:**

1. **Check if Python is installed:**
   - Press Windows key + R
   - Type: `python --version`
   - Press Enter
   - If it shows a version (e.g., "Python 3.11.5"), Python is installed

2. **Install Python:**
   - Go to https://www.python.org/downloads/
   - Download Python 3.8 or newer
   - **IMPORTANT:** During installation, check ✓ "Add Python to PATH"
   - Click "Install Now"
   - Wait for completion
   - **Restart your computer**

3. **Verify installation:**
   - Close and reopen Command Prompt
   - Type: `python --version`
   - Should show a version number

4. **Still not working?**
   ```
   1. Uninstall Python
   2. Install to C:\Python311 (avoid Program Files)
   3. During install, manually add to PATH:
      - Check "Add Python to PATH" 
      - Or manually add C:\Python311 to system PATH
   4. Restart computer
   ```

---

### 🔴 Error: "ModuleNotFoundError: No module named 'pandas'"

**What this means:**
The required pandas library didn't install correctly.

**Solutions:**

1. **Try automatic fix:**
   ```
   Press Windows key + R
   Type: cmd
   Press Enter
   Type: pip install pandas
   Press Enter
   ```

2. **Use specific Python version:**
   ```
   Press Windows key + R
   Type: cmd
   Press Enter
   Type: python -m pip install --upgrade pip
   Press Enter
   Type: python -m pip install pandas
   Press Enter
   ```

3. **Check pip is installed:**
   ```
   Type: pip --version
   Should show a version like "pip 23.1..."
   ```

4. **If pip is missing:**
   ```
   1. Uninstall Python
   2. Reinstall with "pip" checked during installation
   ```

---

### 🔴 Error: "Log files not found" or Empty outputs

**What this means:**
The program can't find the input log files.

**Check these files exist in the project root:**
- ✓ SystemLog.csv
- ✓ hl7Log.txt
- ✓ sbxLog.xml
- ✓ DoComLog.txt

**Solutions:**

1. **Verify files are in the right place:**
   - Navigate to the project folder
   - You should see these 4 files in the root directory
   - If they're in a subfolder, move them to the root

2. **Check file names exactly match:**
   - File names are case-sensitive on some systems
   - Exact names: `SystemLog.csv`, `hl7Log.txt`, `sbxLog.xml`, `DoComLog.txt`
   - No extra spaces or special characters

3. **File permissions:**
   ```
   1. Right-click the file
   2. Select "Properties"
   3. Check if "Read-only" is NOT checked
   4. Click "OK"
   ```

4. **Files too large?**
   - If files are > 1GB, processing will be slow
   - This is normal - can take 5-15 minutes

---

### 🟡 Error: "Pipeline execution failed" (Timeout or Crash)

**What this means:**
The program ran but encountered an error during processing.

**Solutions:**

1. **Run main.py directly for detailed error:**
   ```
   1. Press Windows key + R
   2. Type: cmd
   3. Press Enter
   4. cd to your project folder
   5. Type: python main.py
   6. Look at the error message
   ```

2. **Check disk space:**
   - Press Windows key + E (File Explorer)
   - Right-click your C: drive
   - Select "Properties"
   - Need at least 500MB free space

3. **Close other programs:**
   - Close browser, email, other apps
   - These consume memory/CPU
   - Try running again

4. **Try running individual steps:**
   ```
   # Just normalization
   python main.py
   
   # Just correlation
   python analysis/correlation_engine.py
   
   # Just coverage
   python analysis/Rule_engine/coverage_summary.py
   ```

5. **Check memory & CPU:**
   - Press Ctrl + Shift + Esc (Task Manager)
   - Look for memory usage
   - If > 80%, close some programs and retry

---

### 🟡 Program Runs Very Slowly

**What this means:**
This is often NORMAL for large log files.

**Typical timings:**
- Small logs (< 10K events): 30 seconds
- Medium logs (10K-100K events): 1-3 minutes
- Large logs (> 100K events): 5-15 minutes
- First run (includes dependency install): +1-2 minutes

**Ways to speed up:**
1. Close other programs
2. Move project to local drive (not network drive)
3. Restart computer
4. Run at different time when system is less busy

---

### 🟡 Error: "UnicodeDecodeError" or Encoding Issues

**What this means:**
Log files have special characters the program can't read.

**Solutions:**

1. **Convert files to UTF-8:**
   - Open log file in Notepad++
   - Encoding menu → Encode in UTF-8
   - Save file
   - Try again

2. **Or use PowerShell (handles encoding better):**
   - Right-click `RUN.ps1`
   - Select "Run with PowerShell"

3. **Or open with Python directly:**
   ```
   python setup_and_run.py
   ```

---

### 🟡 Output Files Empty or Corrupted

**What this means:**
The program ran but didn't produce valid data.

**Check:**

1. **Verify outputs/ folder has files:**
   - Look in: Project folder → outputs →
   - Should see: CSV and JSON files

2. **Open CSV files in Excel:**
   - Right-click .csv file → Open with → Excel
   - Should show data in columns
   - If empty, rerun the program

3. **File size:**
   ```
   Right-click file → Properties → Size
   Should NOT be 0 bytes
   ```

4. **Try running just normalization:**
   ```
   python main.py
   This creates normalized_logs.json
   Check the file size (should be > 100KB for non-empty logs)
   ```

---

### ❓ General Debugging Steps

**If nothing else works, try:**

```
1. Delete outputs/ folder
   (Right-click → Delete)

2. Delete frequency_validations.* files in Freqency_check/
   (Clean up old results)

3. Run from Administrator Command Prompt:
   Press Windows key, type "cmd"
   Right-click Command Prompt → Run as Administrator
   Navigate to project folder
   Type: python setup_and_run.py

4. Watch the console output carefully
   Note any error messages
   These tell you what went wrong

5. If error mentions a specific file:
   - Check that file exists
   - Check file is readable (not corrupted)
   - Check file format matches expected
```

---

## Getting Help

### Before asking for help, provide:

1. **Exact error message** (copy-paste from console)
2. **Which method you used:**
   - [ ] RUN.bat
   - [ ] RUN.ps1
   - [ ] Command line: `python setup_and_run.py`
3. **Your Python version:**
   ```
   python --version
   (Tell us the output)
   ```
4. **File sizes:**
   ```
   Right-click each log file → Properties → Size
   SystemLog.csv size: _____ MB
   hl7Log.txt size: _____ MB
   sbxLog.xml size: _____ MB
   DoComLog.txt size: _____ MB
   ```
5. **Computer specs:**
   - Windows 7 / 10 / 11 / Server?
   - Disk space available: ____ GB
   - RAM: ____ GB

---

## 💡 Pro Tips

### Speed up future runs:
```
1. Keep outputs/ folder between runs
2. Dependencies install once, reuse after
3. Smaller log files process faster
```

### Debug mode:
```
Edit main.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)

This shows detailed debug messages
```

### Manual Python PATH fix:
```
If Python not in PATH:
1. Find Python.exe location
2. Press Windows key + X → System
3. Advanced system settings → Environment Variables
4. Add Python path to PATH variable
5. Restart computer
```

---

## 📞 Contact Support

If you've tried all above steps and still have issues:

1. **Check INSTALLATION.md** for basic setup
2. **Run from Administrator Command Prompt** with detailed output
3. **Provide the exact error message** from console
4. **Include your Python version** (`python --version`)
5. **Include your Windows version** (Start → Settings → System → About)

---

**Good luck! You've got this! 🚀**
