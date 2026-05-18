# Distribution Package Guide

## For Team Distribution

### Option 1: Simple Folder Distribution (Recommended)

1. **Zip the entire folder:**
   ```
   Darwin log compare/
   ├── RUN.bat                    (⭐ Give to team - double-click to run)
   ├── setup_and_run.py          (auto-downloaded via git)
   ├── requirements.txt
   ├── main.py
   ├── config.py
   ├── normalizers/
   ├── analysis/
   ├── Freqency_check/
   ├── outputs/                  (auto-created)
   ├── inputs/                   (place log files here)
   ├── INSTALLATION.md           (read this first)
   └── ... other files
   ```

2. **Share with team:**
   - Upload entire folder to shared drive/cloud
   - Team downloads and extracts
   - Team double-clicks `RUN.bat`
   - Done!

**Advantages:**
- ✅ Zero setup required
- ✅ Single file to double-click
- ✅ Works on Windows immediately
- ✅ Automatic dependency installation
- ✅ Clear progress messages

---

### Option 2: Python Package Installation

For distribution via package repository (PyPI, company repository, etc.):

```bash
# Create distribution package
python setup.py sdist bdist_wheel

# Install on user's machine
pip install darwin-log-compare-1.0.0-py3-none-any.whl

# Run from anywhere
darwin-log-compare
```

**Advantages:**
- ✅ Cleaner for IT deployment
- ✅ Versioning and updates
- ✅ Works on Linux/Mac too

**Setup required:**
- Team must have Python 3.8+ installed
- One-time pip install

---

### Option 3: Docker Container (Advanced)

For maximum portability and zero setup:

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["python", "main.py"]
   ```

2. **Build and run:**
   ```bash
   docker build -t darwin-log-compare .
   docker run -v /path/to/logs:/app/data darwin-log-compare
   ```

**Advantages:**
- ✅ Works on any OS with Docker
- ✅ No Python installation needed
- ✅ Isolated environment

**Setup required:**
- Install Docker Desktop

---

### Option 4: Standalone Executable (Advanced)

For users without Python:

```bash
pip install pyinstaller

# Create single EXE file
pyinstaller --onefile --distpath ./dist setup_and_run.py

# Result: dist/setup_and_run.exe (can be run without Python!)
```

**Advantages:**
- ✅ Zero dependencies
- ✅ Works on any Windows PC
- ✅ Single executable file
- ✅ Fastest startup

**Disadvantages:**
- ❌ Larger file size (~50-100MB)
- ❌ Longer first build time
- ❌ No source code visibility

---

## Recommended Approach

**For your team: Use Option 1 (Folder Distribution)**

### Step-by-Step:

1. **Ensure your folder has these files:**
   ```
   ✓ RUN.bat
   ✓ setup_and_run.py
   ✓ requirements.txt
   ✓ main.py
   ✓ INSTALLATION.md
   ✓ All code files (analysis/, normalizers/, etc.)
   ✓ Input log files (SystemLog.csv, hl7Log.txt, etc.)
   ```

2. **Create a README for team:**
   ```
   QUICK START GUIDE
   =================
   1. Extract the zip file
   2. Double-click RUN.bat
   3. Wait for completion
   4. Find results in outputs/ folder
   
   For help, see INSTALLATION.md
   ```

3. **Share on:**
   - Shared network drive
   - Cloud storage (OneDrive, Google Drive)
   - Email (if < 50MB)
   - Git repository

4. **Team experience:**
   - Download zip
   - Extract
   - Double-click RUN.bat
   - See console output with progress
   - Results appear in outputs/

---

## Testing Before Distribution

Before giving to team, test:

```bash
# Test on clean machine (or VM)
1. Download the folder
2. Double-click RUN.bat
3. Verify outputs/ has all expected files
4. Check console for any errors
5. Verify CSV/JSON files are readable
```

---

## Maintenance & Updates

### If you make changes:

1. **Update version in setup.py:**
   ```python
   version="1.1.0"  # Change this
   ```

2. **Update CHANGELOG:**
   ```
   v1.1.0 - Added frequency validation
   v1.0.0 - Initial release
   ```

3. **Redistribute:**
   - Upload new zip with all changes
   - Team downloads and re-runs RUN.bat

---

## Troubleshooting Distribution

| Problem | Solution |
|---------|----------|
| "RUN.bat not working" | Right-click → "Run as Administrator" |
| "Python not found" | Team must install Python 3.8+ from python.org |
| "Large download" | Compress with 7-Zip to reduce size |
| "Need updates" | Create new version folder (v1.1, v1.2, etc.) |
| "Share with many users" | Use shared drive instead of email |

---

## Distribution Checklist

Before sharing:

- [ ] All code files included
- [ ] requirements.txt present and updated
- [ ] RUN.bat works (tested locally)
- [ ] INSTALLATION.md present
- [ ] Input log files included (or separate folder)
- [ ] outputs/ folder created and empty
- [ ] README.md updated with team info
- [ ] Tested on another PC/VM

---

## Support

For team members needing help:
1. Run INSTALLATION.md troubleshooting section
2. Check console output for error messages
3. Verify Python 3.8+ installed
4. Try running main.py directly for more details
