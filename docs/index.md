---
layout: home

hero:
  name: Communication Protocols Guide
  text: Embedded Device Communication Protocols
  tagline: Comprehensive reference for selecting, configuring, and deploying protocols on ESP32/ESP32-S3 across four bandwidth/stability categories
  actions:
    - theme: brand
      text: Get Started
      link: /introduction/overview
    - theme: alt
      text: Protocol Comparison
      link: /category1/protocol-comparison

features:
  - title: Four Protocol Categories
    details: Organized by bandwidth and link stability - Low BW Lossy Long Range, Low BW Stable, High BW Lossy, High BW Stable
  - title: ESP32/ESP32-S3 Focus
    details: Complete setup guides for PlatformIO and ESP-IDF with hardware recommendations
  - title: DeepWiki Powered
    details: Auto-updated from Meshtastic, LoRaMesher, ESP-IDF, OpenWrt Routing, OpenThread
  - title: Ready-to-Use Examples
    details: 6 complete ESP32 projects for PlatformIO and ESP-IDF
  - title: Comparison Matrices
    details: Detailed CSV/Markdown comparisons with decision guides
  - title: MIT Licensed
    details: Open source, community driven, auto-updated weekly
---

# Communication Protocols Guide for Embedded Devices

A comprehensive reference for selecting, configuring, and deploying communication protocols on embedded devices (ESP32, ESP32-S3) across four bandwidth/stability categories.

## Quick Navigation

| Category | Bandwidth | Stability | Range | Protocols |
|----------|-----------|-----------|-------|-----------|
| **1. Low BW, Lossy, Long Range** | < 5 kbps | High loss | 1-50+ km | LoRaMesher, Meshtastic, BATMAN-ADV |
| **2. Low BW, Stable** | 250 kbps - 1 Mbps | Low loss | 10-100 m | OpenThread, Zigbee 3.0, BLE Mesh |
| **3. High BW, Lossy** | 1-50 Mbps | Medium loss | 100m-1km | BATMAN-ADV, Babel, 802.11s |
| **4. High BW, Stable** | 100 Mbps - 1 Gbps | Very low loss | LAN/WAN | WireGuard, BIRD2, cjdns, Yggdrasil |

## Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/communication-guide
cd communication-guide

# Install dependencies
npm install
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Scrape latest DeepWiki content
python scripts/scrape_deepwiki.py 30
python scripts/extract_rules.py
python scripts/generate_comparison.py

# Start development server
npm run dev

# Build for production
npm run build
```

## Protocol Selection Guide

```
START: What are your PRIMARY constraints?
│
├─► RANGE > 1 km AND battery-powered?
│   ├─► YES → Category 1 (LoRa)
│   │   ├─► Deterministic latency needed? → LoRaMesher (TDMA)
│   │   ├─► Mobile app + MQTT needed? → Meshtastic
│   │   └─► L2 transparency needed? → BATMAN-ADV (Linux host)
│   │
│   └─► NO → Continue
│
├─► RANGE < 100m AND stable links?
│   ├─► YES → Category 2 (802.15.4/BLE)
│   │   ├─► Building Matter/Thread device? → OpenThread (ESP32-H2/C6)
│   │   ├─► Need Zigbee ecosystem? → Zigbee 3.0 (ESP32-H2/C6)
│   │   └─► Phone provisioning, no border router? → BLE Mesh (ESP32/S3)
│   │
│   └─► NO → Continue
│
├─► HIGH THROUGHPUT (>1 Mbps) over LOSSY wireless?
│   ├─► YES → Category 3 (WiFi Mesh)
│   │   ├─► L2 transparency (bridging)? → BATMAN-ADV (OpenWrt)
│   │   ├─► Fast convergence + dual-stack? → Babel (ESP32-S3/Linux)
│   │   └─► Standard WiFi mesh? → 802.11s (ESP32-S3)
│   │
│   └─► NO → Continue
│
└─► HIGH THROUGHPUT over STABLE links?
    ├─► YES → Category 4
    │   ├─► Simple VPN, point-to-point? → WireGuard (ESP32-S3/Linux)
    │   ├─► Enterprise routing? → BIRD2 OSPF/BGP (Linux)
    │   └─► Encrypted overlay, no PKI? → cjdns / Yggdrasil (Linux)
```

## Key Resources

| Resource | Link |
|----------|------|
| **Live Documentation** | https://yourusername.github.io/communication-guide/ |
| **GitHub Repository** | https://github.com/yourusername/communication-guide |
| **DeepWiki Sources** | Meshtastic, LoRaMesher, ESP-IDF, OpenWrt Routing, OpenThread |
| **ESP32 Examples** | 6 complete PlatformIO/ESP-IDF projects |
| **Comparison Matrices** | CSV + Markdown in `/data/` |

## Automation

| Script | Purpose |
|--------|---------|
| `scrape_deepwiki.py` | Weekly DeepWiki content scraping |
| `extract_rules.py` | Structured rule extraction (12 types) |
| `generate_comparison.py` | CSV/Markdown comparison matrices |
| `validate_examples.py` | ESP32 build verification |
| `generate_pdf_markdown.py` | PDF export via Pandoc |

## License

MIT License - see [LICENSE](https://github.com/yourusername/communication-guide/blob/main/LICENSE) for details.

---

*Last updated: 2024-11-20 | Auto-updated weekly from DeepWiki*