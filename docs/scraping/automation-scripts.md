# Automation Scripts Reference

## Overview

This document describes all automation scripts used in the Communication Protocols Guide for scraping, validation, and generation tasks.

## Script Inventory

| Script | Purpose | Language | Dependencies |
|--------|---------|----------|--------------|
| `scrape_deepwiki.py` | DeepWiki content scraper | Python 3.8+ | httpx, beautifulsoup4, pyyaml, lxml |
| `extract_rules.py` | Rule extraction from scraped content | Python 3.8+ | pyyaml |
| `generate_comparison.py` | Comparison matrix generator | Python 3.8+ | csv, json |
| `generate_pdf_markdown.py` | Combined markdown for PDF export | Python 3.8+ | pathlib |
| `validate_examples.py` | ESP32 example validator | Python 3.8+ | subprocess, pathlib |
| `run_benchmarks.py` | Automated benchmark runner | Python 3.8+ | asyncio, pandas (optional) |
| `compare_benchmarks.py` | Performance regression detector | Python 3.8+ | json |
| `analyze_field_data.py` | Field test data analyzer | Python 3.8+ | pandas, geopy |

---

## scrape_deepwiki.py

### Purpose
Scrapes DeepWiki documentation from target repositories and saves structured content.

### Usage

```bash
# Scrape all repos (30 pages each)
python scripts/scrape_deepwiki.py

# Scrape with custom page limit
python scripts/scrape_deepwiki.py 50

# Scrape specific repos only (modify REPOS list in script)
```

### Configuration

```python
# Target repositories (modify in script)
REPOS = [
    "meshtastic/firmware",
    "LoRaMesher/LoRaMesher",
    "espressif/esp-idf",
    "openwrt/routing",
    "openthread/openthread",
]

# Output directories
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "scraped"
RULES_DIR = Path(__file__).parent.parent / "docs" / "rules"
```

### Key Features

- **Rate limiting**: Exponential backoff for 429 responses
- **JS rendering**: Handles DeepWiki SPA with httpx (static content)
- **Structured output**: JSON + Markdown per page
- **Incremental**: Only new/changed pages (future enhancement)

### Output

```
docs/scraped/
├── meshtastic_firmware/
│   ├── Overview.json
│   ├── Overview.md
│   └── ...
├── LoRaMesher_LoRaMesher/
├── espressif_esp-idf/
├── openwrt_routing/
└── openthread_openthread/
```

---

## extract_rules.py

### Purpose
Extracts structured protocol rules from scraped DeepWiki content.

### Usage

```bash
# Run after scraping
python scripts/extract_rules.py
```

### Rule Classification

| Rule Type | Keywords | Examples |
|-----------|----------|----------|
| `configuration` | config, parameter, setting, option | "LoRa Configuration", "Mesh Parameters" |
| `state_machine` | state, status, mode, phase | "Network State Machine", "Device Modes" |
| `message_format` | message, packet, frame, format, header | "Packet Structure", "Message Types" |
| `timing` | timing, slot, interval, timeout, period | "TDMA Timing", "Slot Duration" |
| `routing` | route, routing, forward, path, hop | "Routing Algorithm", "Path Discovery" |
| `security` | security, encrypt, auth, key, crypto | "Encryption", "Authentication" |
| `api` | api, callback, function, method, command | "CLI Commands", "Callback API" |
| `constant` | define, const, default_, max_, min_, timeout_ | "MAX_HOPS", "DEFAULT_TIMEOUT" |

### Output

```
docs/rules/
├── low-bandwidth-lossy-long-range/
│   ├── rules.yaml
├── low-bandwidth-stable/
│   ├── rules.yaml
├── high-bandwidth-lossy/
│   ├── rules.yaml
├── high-bandwidth-stable/
│   ├── rules.yaml
├── platform/
│   ├── rules.yaml
└── all_rules.yaml
```

### Rule Structure

```yaml
- repo: "meshtastic/firmware"
  category: "low-bandwidth-lossy-long-range"
  rule_type: "configuration"
  name: "LoRa Configuration Parameters"
  description: "Section: LoRa Configuration Parameters"
  parameters:
    region: "US"
    tx_power: "17"
    spreading_factor: "7"
  source_file: "LoRa_Configuration.md"
  source_section: "lora-configuration"
  confidence: 0.8
```

---

## generate_comparison.py

### Purpose
Generates CSV and Markdown comparison matrices for each protocol category.

### Usage

```bash
# Generate all comparison matrices
python scripts/generate_comparison.py
```

### Protocol Data Source

Combines:
1. **Manual curation** (PROTOCOL_DATA dictionary)
2. **Extracted rules** (from extract_rules.py)
3. **Academic papers** (referenced in docs)

### Categories & Protocols

```python
CATEGORY_PROTOCOLS = {
    'low-bandwidth-lossy-long-range': [
        'LoRaMesher', 'Meshtastic', 'BATMAN-ADV (LoRa)'
    ],
    'low-bandwidth-stable': [
        'OpenThread', 'Zigbee 3.0', 'BLE Mesh'
    ],
    'high-bandwidth-lossy': [
        'BATMAN-ADV', 'Babel', '802.11s (HWMP)'
    ],
    'high-bandwidth-stable': [
        'WireGuard', 'BIRD2 (OSPF/BGP)', 'cjdns', 'Yggdrasil'
    ],
}
```

### Attributes Compared

```python
ATTRIBUTES = [
    'Architecture', 'Layer', 'Routing Algorithm', 'Metric',
    'Max Data Rate', 'Typical Range', 'Encryption', 'Authentication',
    'Key Management', 'Forward Secrecy', 'NAT Traversal',
    'Roaming Support', 'Multicast', 'Fragmentation',
    'Security Level', 'Maturity', 'License', 'ESP32 Support', 'Best For'
]
```

### Output Files

```
data/
├── low-bandwidth-lossy-long-range_comparison.csv
├── low-bandwidth-lossy-long-range_comparison.md
├── low-bandwidth-stable_comparison.csv
├── low-bandwidth-stable_comparison.md
├── high-bandwidth-lossy_comparison.csv
├── high-bandwidth-lossy_comparison.md
├── high-bandwidth-stable_comparison.csv
├── high-bandwidth-stable_comparison.md
└── category_summary.csv
```

---

## generate_pdf_markdown.py

### Purpose
Creates combined markdown file for PDF export via pandoc/weasyprint.

### Usage

```bash
# Generate combined markdown (piped to pandoc)
python scripts/generate_pdf_markdown.py > combined.md

# Or use in CI
pandoc combined.md -o guide.pdf --pdf-engine=weasyprint --toc
```

### Features

- **Ordered sections** following guide structure
- **Fixed relative links** converted to anchors
- **Page breaks** before major sections
- **Title page** with metadata
- **Appendices** (glossary, references)

### File Order

```python
PDF_FILES = [
    "introduction/overview.md",
    "introduction/device-categories.md",
    "introduction/protocol-landscape.md",
    "category1/protocol-comparison.md",
    "category1/top-algorithms.md",
    "category1/esp32-setup/loramesher-esp32.md",
    # ... all files in logical order
]
```

---

## validate_examples.py

### Purpose
Validates that all ESP32 examples compile successfully.

### Usage

```bash
# Validate all examples
python scripts/validate_examples.py

# Validate only PlatformIO examples
python scripts/validate_examples.py --only platformio

# Validate only ESP-IDF examples
python scripts/validate_examples.py --only espidf
```

### Build System Detection

```python
def detect_build_system(self, example_dir: Path) -> str:
    if (example_dir / "platformio.ini").exists():
        return "platformio"
    elif (example_dir / "CMakeLists.txt").exists() and (example_dir / "main").exists():
        return "espidf"
    return "unknown"
```

### Validation Commands

| Build System | Commands |
|--------------|----------|
| PlatformIO | `pio check`, `pio run` |
| ESP-IDF | `idf.py build` (with export.sh sourced) |

### Output

```
VALIDATION SUMMARY
============================================================
Total: 8 | Passed: 7 | Failed: 1

PLATFORMIO: 4/4 passed
  ✓ esp32-loramesher (12.3s)
  ✓ esp32-meshtastic (45.2s)
  ✓ esp32-ble-mesh (8.1s)
  ✓ esp32s3-wifi-mesh-babel (15.7s)

ESPIDF: 3/4 passed
  ✓ esp32s3-wireguard (22.3s)
  ✓ esp32s3-openthread-rcp (18.9s)
  ✗ esp32s3-bird2-linux (FAIL: ESP-IDF not found)
```

---

## run_benchmarks.py

### Purpose
Automated benchmark execution for protocol performance testing.

### Usage

```bash
# Single benchmark
python scripts/run_benchmarks.py --protocol loramesher --topology line --nodes 5

# Full suite
python scripts/run_benchmarks.py --full-suite
```

### Configuration

```python
configs = [
    {'topology': 'line', 'nodes': 5, 'traffic': 'periodic', 'packet_size': 50, 'interval_ms': 60000, 'duration': 3600},
    {'topology': 'line', 'nodes': 10, 'traffic': 'periodic', 'packet_size': 50, 'interval_ms': 60000, 'duration': 3600},
    {'topology': 'grid', 'nodes': 9, 'traffic': 'broadcast', 'packet_size': 50, 'interval_ms': 30000, 'duration': 7200},
    {'topology': 'random', 'nodes': 20, 'traffic': 'burst', 'packet_size': 100, 'interval_ms': 1000, 'duration': 14400},
]
```

### Metrics Collected

- PDR (Packet Delivery Ratio)
- Throughput (kbps)
- Latency (avg, p50, p95, p99)
- RSSI/SNR
- Power consumption
- Convergence time

### CI Integration

```yaml
# .github/workflows/benchmark.yml
- name: Run benchmarks
  run: python scripts/run_benchmarks.py --full-suite
- name: Compare with baseline
  run: python scripts/compare_benchmarks.py
```

---

## compare_benchmarks.py

### Purpose
Detects performance regressions by comparing current benchmarks with baseline.

### Usage

```bash
# Compare current results with baseline
python scripts/compare_benchmarks.py --current results.json --baseline baseline.json
```

### Regression Detection

```python
def compare_with_baseline(current: dict, baseline_file: Path):
    metrics = ['pdr', 'throughput_kbps', 'avg_latency_ms', 'p99_latency_ms']
    for metric in metrics:
        curr = current.get(metric, 0)
        base = baseline.get(metric, 0)
        if base > 0:
            change_pct = (curr - base) / base * 100
            regression = change_pct < -5  # 5% threshold
```

### CI Integration

```bash
# Fail build on regression
if any(v['regression'] for v in comparison.values()):
    print("::error::Performance regression detected!")
    exit(1)
```

---

## analyze_field_data.py

### Purpose
Analyzes field test data from CSV logs.

### Usage

```bash
python scripts/analyze_field_data.py field_log.csv
```

### Analysis Features

- PDR by distance
- Link budget analysis
- Path loss vs RSSI
- Latency distribution
- Battery drain correlation

### Dependencies

```bash
pip install pandas geopy
```

### Output

```json
{
  "pdr_overall": 0.942,
  "pdr_by_distance": [...],
  "avg_latency_ms": 145.2,
  "avg_rssi_dbm": -87.3,
  "avg_snr_db": 7.8,
  "margin_stats": {
    "mean": 3.2,
    "min": -2.1,
    "std": 4.5
  }
}
```

---

## CI/CD Integration

### Complete Pipeline

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install -r requirements.txt
      - run: python scripts/validate_examples.py

  benchmark:
    needs: validate
    runs-on: self-hosted  # Requires hardware
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/run_benchmarks.py --full-suite
      - run: python scripts/compare_benchmarks.py

  scrape:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install -r requirements.txt
      - run: python scripts/scrape_deepwiki.py
      - run: python scripts/extract_rules.py
      - run: python scripts/generate_comparison.py
      - uses: stefanzweifel/git-auto-commit-action@v5

  deploy:
    needs: [validate, benchmark]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: '20', cache: 'npm'}
      - run: npm ci && npm run build
      - uses: actions/upload-pages-artifact@v3
        with: {path: docs/.vitepress/dist}
      - uses: actions/deploy-pages@v4
```

---

## Requirements

### Python Dependencies

```txt
# requirements.txt
httpx>=0.27.0
beautifulsoup4>=4.12.0
pyyaml>=6.0
lxml>=4.9.0
pandas>=2.0.0
geopy>=2.3.0
```

### System Dependencies

```bash
# Ubuntu/Debian
apt update && apt install -y \
    pandoc weasyprint \
    python3-venv python3-dev \
    gcc g++ make cmake \
    libssl-dev libffi-dev

# ESP-IDF (for ESP-IDF examples)
# Follow: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/

# PlatformIO (for PlatformIO examples)
pip install platformio
```

---

## Troubleshooting

| Script | Common Issue | Solution |
|--------|--------------|----------|
| `scrape_deepwiki.py` | 429 Too Many Requests | Increase delays, reduce max_pages |
| `extract_rules.py` | No rules extracted | Check scraped JSON structure |
| `generate_comparison.py` | Missing protocol data | Check PROTOCOL_DATA dict |
| `validate_examples.py` | ESP-IDF not found | Source export.sh, check PATH |
| `run_benchmarks.py` | Hardware not found | Use self-hosted runner |
| `generate_pdf_markdown.py` | Missing files | Check PDF_FILES list |

---

## Extending Scripts

### Adding New Protocol to Comparisons

1. Add to `CATEGORY_PROTOCOLS` in `generate_comparison.py`
2. Add protocol data to `PROTOCOL_DATA` dict
3. Add ESP32 setup guide in appropriate category
3. Run `python scripts/generate_comparison.py`

### Adding New Scraping Target

1. Add repo to `REPOS` list in `scrape_deepwiki.py`
2. Add category mapping in `categorize_repo()`
3. Run scraper and extractor
4. Update `source-inventory.md`

### Custom Rule Types

```python
# In extract_rules.py
rules = {
    'new_type': ['keyword1', 'keyword2'],
    # ...
}
```