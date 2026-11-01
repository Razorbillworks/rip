<div align="center">

<!-- Animated Spooky Typewriter Header -->
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=24&pause=1000&color=E06C75&center=true&vCenter=true&width=500&lines=rip%3A+a+graveyard+for+dead+code;channeling+spirits+via+gemma-2;remembering+the+abandoned." alt="rip banner" />

<p align="center">
  A local CLI tool and digital cemetery built for <strong>Hacktoberfest 2026: Ghost in the Machine</strong>.<br />
  Channels the spirits of forgotten scripts and abandoned repositories using local <strong>Google Gemma 2 (2B)</strong>.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Model-Google_Gemma_2_(2B)-8A2BE2?style=flat-square" alt="Model" />
  <img src="https://img.shields.io/badge/Inference-Ollama_(Local)-black?style=flat-square" alt="Inference" />
  <img src="https://img.shields.io/badge/Privacy-100%25_Air--Gapped-success?style=flat-square" alt="Air Gapped" />
  <img src="https://img.shields.io/badge/Hacktoberfest-Week_4-orange?style=flat-square" alt="Hacktoberfest" />
</p>

</div>

---

### Overview

Every developer's drive hosts a quiet graveyard: incomplete prototypes, late-night experiments, and uncommitted scripts.

`rip` acts as a respectful gravekeeper. It traverses your workspaces to locate dormant projects, passing **strictly metadata** (modification age, sizes, and Git commit logs) to an air-gapped Gemma 2 instance. It produces witty obituaries and constructive **Ofrenda** sparks to resurrect your code, rendered both as ANSI terminal tombstones and a self-contained HTML gallery.

---

### The Graveyard Gallery

<div align="center">
  <img src="assets/graveyard-demo.png" alt="Generated Code Cemetery Web View" width="100%" />
</div>

---

### Architecture & Open Innovation

- **Absolute Zero-Content Telemetry**: Proprietary APIs require uploading data off your machine. `rip` runs an open-weight foundation model locally; source code and file contents never touch the inference pipeline.
- **Offline & Air-Gapped**: Runs entirely on local compute through Ollama. No network latency, rate quotas, or vendor lock-in.
- **Zero Compute Costs**: Eliminates token billing for scanning hundreds of local directories.

---

### Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Model** | Google Gemma 2 (2B) | Open-weight foundation LLM for obituaries & revival logic |
| **Engine** | Ollama | Local model orchestration & GPU inference |
| **CLI Runtime** | Python 3.10+ | Filesystem traversals & git metadata extraction |
| **Terminal UI** | Rich | Structured ANSI panels & tombstone formatting |
| **Export** | Vanilla HTML / CSS Grid | Standalone dark-mode cemetery visualizer |

---

### Installation & Setup

**1. Pull the model weights**

```bash
ollama pull gemma2:2b
```

**2. Clone & prepare the environment**

```bash
git clone https://github.com/Razorbillworks/rip.git
cd rip
python -m venv venv
```

Activate the environment:

- Windows: `.\venv\Scripts\Activate.ps1`
- Linux/macOS: `source venv/bin/activate`

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

### Usage

Scan a directory for items untouched for more than 30 days:

```bash
python rip.py "C:\path\to\projects" --days 30
```

Enable the Día de los Muertos Ofrenda mode for resurrection hints:

```bash
python rip.py "C:\path\to\projects" --days 15 --ofrenda --out cemetery.html
```

---

### CLI Reference

```text
positional arguments:
  path              Target directory to scan (default: current working dir)

options:
  --days INT        Dormancy threshold in days (default: 30)
  --model STR       Ollama model tag (default: gemma2:2b)
  --ofrenda         Generate constructive resurrection hints
  --out STR         HTML cemetery output path (default: cemetery.html)
```