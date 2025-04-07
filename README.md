
# Scanner.py — Automated Enumeration Toolkit

## 🔍 Overview
`Scanner.py` is a powerful Python-based automated recon tool for penetration testers and red teamers. It performs deep enumeration across multiple layers — from open ports to web fuzzing to subdomain discovery — and generates structured HTML, Markdown, and PDF reports.

---

## 🚀 Features

- ✅ Full TCP port scan using Nmap (`-p- --open`)
- ✅ Service enumeration with Nmap `-sCV`
- ✅ Web port detection (80, 443, 8080, etc.)
- ✅ Web directory fuzzing with:
  - nikto
  - dirb
  - gobuster
  - feroxbuster
  - ffuf
- ✅ Subdomain enumeration using:
  - ffuf (DNS mode)
  - dnsx
  - sublist3r
  - subfinder
- ✅ Tool auto-selection or user-defined
- ✅ Wordlist selection (custom or default)
- ✅ Real-time output for all tools
- ✅ Parallel execution (`--parallel`)
- ✅ Modular scanning with flexible flags

---

## 🧾 HTML & Report Output

The script generates:
- `target_report.html`: Full HTML report per target
- `combined_report.html`: Summary across all scanned targets

Each HTML report includes:
- Organized sections for Nmap, web tools, subdomain tools
- 📚 Table of contents
- 🔍 Search bar for fast navigation
- ✅ Exportable to:
  - Markdown (.md)
  - PDF (.pdf)

---

## ⚙️ CLI Usage

### Single Target
```bash
python3 autoscan.py <target>
```

### Multiple Targets
```bash
python3 autoscan.py -f targets.txt
```

---

## 🧩 Command-Line Flags

| Flag | Description |
|------|-------------|
| `--parallel` | Run tools concurrently (faster) |
| `--nmap-only` | Only run full Nmap scans |
| `--web-only` | Only run web fuzzing tools |
| `--subdomain-only` | Only run subdomain enumeration |
| `--no-nmap` | Skip all Nmap scans |
| `--tools` | Choose web tools (comma-separated) |
| `--subtools` | Choose subdomain tools (comma-separated) |
| `--wordlist` | Path to custom wordlist for web fuzzing |
| `--subwordlist` | Path to custom wordlist for subdomain fuzzing |
| `--report` | Generate HTML, Markdown, and PDF reports |
| `-f <file>` | Run against multiple targets listed in a file |

---

## 🗂 Output Files

For each target:
- `target_openPorts.txt`
- `target_sCV_scan.txt`
- `target_port<port>_<tool>.txt`
- `target_subdomains_<tool>.txt`
- `target_report.html`, `.md`, `.pdf` (if `--report`)

And a `combined_report.html` if scanning multiple hosts.

---

## 🧠 Requirements

Ensure the following tools are installed:
- `nmap`, `nikto`, `gobuster`, `dirb`, `feroxbuster`, `ffuf`
- `dnsx`, `subfinder`, `sublist3r`

Install them using `apt`, `snap`, or `pip` as needed.

---

## 🧪 Example
```bash
python3 autoscan.py 192.168.1.10 --tools nikto,gobuster --subtools dnsx,subfinder --report --parallel
```

---

## 💬 Notes
- Default wordlist used: `/usr/share/wordlists/rockyou.txt`
- All results printed in real-time and saved to output files
