# AI Legal Contract Auditor - Installation Guide

This guide will help you set up the AI Legal Contract Auditor on **any Windows, Mac, or Linux computer**.

## 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.10 or higher** installed
- **At least 8GB RAM** (16GB recommended for better performance)
- **5GB free disk space** (for Ollama model)
- **Internet connection** (for initial setup only)

---

## 🚀 Step-by-Step Installation

### Step 1: Install Python

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run installer and **CHECK** "Add Python to PATH"
3. Verify: Open Command Prompt and run `python --version`

**Mac:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

---

### Step 2: Install Ollama (Free Local AI)

**Windows:**
1. Download Ollama from https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically

**Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Verify Ollama is running:**
```bash
ollama --version
```

---

### Step 3: Download Llama 3.2 Model

Open a terminal/command prompt and run:

```bash
ollama pull llama3.2
```

This will download ~2GB. Wait for it to complete.

---

### Step 4: Clone/Download the Project

**Option A: Using Git**
```bash
git clone <repo link>
cd ai-legal-contract-auditor
```

**Option B: Manual Download**
1. Download the project ZIP file
2. Extract to a folder (e.g., `C:\ai-legal-contract-auditor` or `~/ai-legal-contract-auditor`)
3. Open terminal in that folder

---

### Step 5: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

### Step 6: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt -c constraints.txt

```
Note: We use constraints.txt to fix version conflicts with LangChain and related packages

This will install:
- LangChain (RAG framework)
- ChromaDB (vector database)
- Sentence Transformers (free embeddings)
- Ollama Python client
- ReportLab (PDF generation)
- PyPDF (PDF parsing)

---

### Step 7: Verify Installation

Run the verification script:

**Windows:**
```powershell
.\venv\Scripts\python.exe -c "import ollama; import chromadb; import reportlab; print('✅ All dependencies installed successfully!')"
```

**Mac/Linux:**
```bash
./venv/bin/python -c "import ollama; import chromadb; import reportlab; print('✅ All dependencies installed successfully!')"
```

---

## 🎯 Running Your First Analysis

### Quick Test

**Windows:**
```powershell
.\venv\Scripts\python.exe analyze_contract.py "path\to\your\contract.pdf" --redline --qa
```

**Mac/Linux:**
```bash
./venv/bin/python analyze_contract.py "path/to/your/contract.pdf" --redline --qa
```

### Example with CUAD Dataset

```bash
# Windows
.\venv\Scripts\python.exe analyze_contract.py "C:\Downloads\contract.pdf" --output "analysis.pdf" --redline --qa

# Mac/Linux
./venv/bin/python analyze_contract.py "~/Downloads/contract.pdf" --output "analysis.pdf" --redline --qa
```

---

## 🔧 Troubleshooting

### Issue 1: "Python not found"
**Solution:** Make sure Python is in your PATH. Reinstall Python and check "Add to PATH" option.

### Issue 2: "Ollama connection refused"
**Solution:** 
```bash
# Start Ollama service
# Windows: Ollama should auto-start, or run "Ollama" from Start Menu
# Mac/Linux:
ollama serve
```

### Issue 3: "Module not found" errors
**Solution:**
```bash
# Make sure virtual environment is activated
# Windows:
.\venv\Scripts\Activate.ps1

# Mac/Linux:
source venv/bin/activate

# Then reinstall:
pip install -r requirements.txt
```

### Issue 4: "Model not found: llama3.2"
**Solution:**
```bash
ollama pull llama3.2
```

### Issue 5: Slow performance
**Solutions:**
- Close other applications to free up RAM
- Use a smaller model: `ollama pull llama3.2:1b` (faster but less accurate)
- Disable Q&A section: remove `--qa` flag

### Issue 6: "Permission denied" on Mac/Linux
**Solution:**
```bash
chmod +x analyze_contract.py
```

---

## 📁 Project Structure

```
AI-Legal-Contract-Auditor/
├── analyze_contract.py          # Main script to run
├── requirements.txt             # Python dependencies
├── constraints.txt              # Fixed version constraints
├── README.md                    # Project documentation
├── CUAD_v1/                     # Subset of CUAD contracts (PDFs)
├── IP.pdf                       # Sample output report
├── src/
│   ├── config.py                # Configuration
│   ├── pdf_parser.py            # PDF extraction and chunking
│   ├── vector_store.py          # Vector database
│   ├── rag_pipeline.py          # RAG implementation
│   ├── clause_analyzer.py       # Clause extraction, risk scoring, summaries
│   ├── pdf_report_generator.py  # PDF report generation
│   └── main.py                  # Pipeline orchestrator
└── chroma_db/                   # Vector DB storage

```

---

## 🌐 System Requirements by OS

### Windows
- **OS:** Windows 10/11 (64-bit)
- **Python:** 3.10+
- **RAM:** 8GB minimum, 16GB recommended
- **Disk:** 5GB free space

### macOS
- **OS:** macOS 11 (Big Sur) or later
- **Python:** 3.10+
- **RAM:** 8GB minimum, 16GB recommended
- **Disk:** 5GB free space
- **Architecture:** Intel or Apple Silicon (M1/M2/M3)

### Linux
- **OS:** Ubuntu 20.04+, Debian 11+, or equivalent
- **Python:** 3.10+
- **RAM:** 8GB minimum, 16GB recommended
- **Disk:** 5GB free space

---

## 💡 Usage Examples

### Basic Analysis (No Redlines, No Q&A)
```bash
python analyze_contract.py contract.pdf
```

### Full Analysis with Redlines
```bash
python analyze_contract.py contract.pdf --redline
```

### Full Analysis with Q&A
```bash
python analyze_contract.py contract.pdf --qa
```

### Complete Analysis (Redlines + Q&A)
```bash
python analyze_contract.py contract.pdf --redline --qa
```

### Custom Output Path
```bash
python analyze_contract.py contract.pdf --output "my_report.pdf" --redline --qa
```

### Rebuild Vector Database (First Time or New Contracts)
```bash
python analyze_contract.py contract.pdf --rebuild --redline --qa
```

---

## 🎓 First Time Setup Checklist

- [ ] Python 3.10+ installed
- [ ] Ollama installed and running
- [ ] Llama 3.2 model downloaded (`ollama pull llama3.2`)
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Verification test passed
- [ ] Test contract analyzed successfully

---

## 📞 Getting Help

If you encounter issues:

1. **Check this guide** - Most common issues are covered above
2. **Verify all prerequisites** - Ensure Python, Ollama, and Llama 3.2 are installed
3. **Check Ollama is running** - Run `ollama list` to see available models
4. **Activate virtual environment** - Make sure `(venv)` appears in your terminal
5. **Check Python version** - Run `python --version` (must be 3.10+)

---

## 🔄 Updating the System

To update to the latest version:

```bash
# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1

# Mac/Linux:
source venv/bin/activate

# Update dependencies
pip install --upgrade -r requirements.txt

# Update Ollama model (if needed)
ollama pull llama3.2
```

---

## ✅ Success!

Once you see this output, you're ready to analyze contracts:

```
================================================================================
ANALYSIS COMPLETE
================================================================================

📊 Summary:
   ✓ Clauses Found: 5/5
   🔴 High Risk: 1
   🟡 Medium Risk: 2
   🟢 Low Risk: 2

✅ Full analysis report saved to: analysis_report.pdf
```

Your PDF report will contain:
- Executive summary
- All 5 clause analyses
- Risk assessments
- Plain English summaries
- Citations (page + section)
- Redline suggestions (if enabled)
- Q&A results (if enabled)

---

## 🎉 You're All Set!

The AI Legal Contract Auditor is now ready to analyze contracts on your computer - **100% free, 100% local, 100% private**.
