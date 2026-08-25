# Quick Start Guide

Get the Credit File Web App running in **2 minutes**.

## ⚡ Quick Setup

### **Windows**
```bash
# Double-click setup.bat
# OR run in PowerShell:
.\setup.bat
```

### **macOS/Linux**
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

## 🚀 Run the App

```bash
streamlit run app.py
```

✅ The app will open automatically at `http://localhost:8501`

## 📤 Upload a Credit Report

1. Click the upload area
2. Select an Excel file (.xlsx)
3. Wait for processing
4. View your credit score and detailed analysis

## 🐳 Docker Option (No Python Install Needed)

```bash
docker build -t creditfile .
docker run -p 8501:8501 creditfile
```

Then visit `http://localhost:8501`

## 📊 What You'll Get

- ✅ Credit score (1-100)
- ✅ Personal data analysis
- ✅ Income breakdown
- ✅ Data validation report
- ✅ Export results (JSON/CSV)

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| `Python not found` | Install Python 3.8+ from python.org |
| `Module not found` | Run `pip install -r requirements-web.txt` |
| `Port 8501 in use` | Run `streamlit run app.py --server.port 8502` |
| `Slow upload` | Check file size (max 500MB) |

## 📚 Full Documentation

See [README_WEB.md](README_WEB.md) for complete documentation.

---

**Questions?** Check the troubleshooting section in the full README or ensure all dependencies are installed correctly.
