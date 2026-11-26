# Communication Protocols Guide for Embedded Devices

[![Build](https://github.com/idraaditya/communication-guide/actions/workflows/build.yml/badge.svg)](https://github.com/idraaditya/communication-guide/actions/workflows/build.yml)
[![Scrape](https://github.com/idraaditya/communication-guide/actions/workflows/scrape.yml/badge.svg)](https://github.com/idraaditya/communication-guide/actions/workflows/scrape.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, automatically updated guide for selecting, configuring, and deploying communication protocols on embedded devices (ESP32, ESP32-S3) across four bandwidth/stability categories.

## 📖 Live Documentation

**🌐 [https://idraaditya.github.io/communication-guide/](https://idraaditya.github.io/communication-guide/)**

## 🎯 Quick Start

### 1. Identify Your Category

```
                    ┌─────────────────────────────────────────┐
                    │         BANDWIDTH REQUIREMENT           │
                    │      Low (<1 Mbps)      High (>1 Mbps)  │
    ┌───────────────┼─────────────────────┼───────────────────┤
    │  Stable       │  Thread, Zigbee,    │  WireGuard,       │
    │  (Low Loss)   │  BLE Mesh           │  OSPF/BGP, cjdns  │
    │               │  ─────────────────  │  ───────────────  │
    │               │  Category 2         │  Category 4       │
    ├───────────────┼─────────────────────┼───────────────────┤
    │  Lossy        │  LoRaMesher,        │  BATMAN-ADV,      │
    │  (High Loss)  │  Meshtastic         │  Babel, 802.11s   │
    │               │  ─────────────────  │  ───────────────  │
    │               │  Category 1         │  Category 3       │
    └───────────────┴─────────────────────┴───────────────────┘
                         RANGE: Short  ←─────→  Long
```

### 2. Follow ESP32 Setup Guides

| Category | Protocols | ESP32 Variant | Guide |
|----------|-----------|---------------|-------|
| **Cat 1: LoRa** | LoRaMesher, Meshtastic | ESP32 / ESP32-S3 | [Setup Guide](docs/category1/esp32-setup/) |
| **Cat 2: 802.15.4/BLE** | OpenThread, Zigbee, BLE Mesh | ESP32-H2/C6, ESP32-S3 | [Setup Guide](docs/category2/esp32-setup/) |
| **Cat 3: WiFi Mesh** | Babel, BATMAN-ADV, 802.11s | ESP32-S3 | [Setup Guide](docs/category3/esp32-setup/) |
| **Cat 4: VPN/Routing** | WireGuard, BIRD2, cjdns | ESP32-S3 / Linux | [Setup Guide](docs/category4/esp32-setup/) |

## 🔬 Features

- **📊 Protocol Comparisons** - Detailed matrices for each category
- **🏆 Top Algorithms** - Research-backed recommendations per category
- **🛠 ESP32 Setup Guides** - Complete PlatformIO/ESP-IDF instructions
- **🔒 Security Analysis** - Encryption, auth, key management comparison
- **🔋 Power Management** - Battery life calculations, optimization
- **🧪 Testing Framework** - Automated benchmarks, CI/CD integration
- **🔄 Migration Guides** - Protocol version and cross-category migrations
- **🤖 Auto-Updated** - Weekly DeepWiki scraping keeps content current

## 🤖 Automated DeepWiki Scraping

This guide stays current by automatically scraping documentation from:

| Repository | DeepWiki | Protocol |
|------------|----------|----------|
| `meshtastic/firmware` | ✅ | Meshtastic (Cat 1) |
| `LoRaMesher/LoRaMesher` | ✅ | LoRaMesher (Cat 1) |
| `espressif/esp-idf` | ✅ | ESP32 Platform (All) |
| `openwrt/routing` | ✅ | BATMAN-ADV, Babel, OLSR (Cat 3) |
| `openthread/openthread` | ✅ | OpenThread (Cat 2) |

**Weekly GitHub Action** scrapes DeepWiki, extracts structured rules, and regenerates documentation.

## 🚀 Local Development

### Prerequisites

- Node.js 18+ (for VitePress)
- Python 3.8+ (for scraping)
- ESP-IDF 5.2+ (for ESP32 examples)
- PlatformIO (for LoRaMesher examples)

### Install

```bash
# Clone
git clone https://github.com/idraaditya/communication-guide.git
cd communication-guide

# Install Node dependencies
npm install

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install VitePress
npm install -D vitepress

# Start dev server
npm run dev
```

### Run Scraping

```bash
# Scrape DeepWiki (takes 5-10 minutes)
python scripts/scrape_deepwiki.py 20

# Extract structured rules
python scripts/extract_rules.py

# Generate comparison matrices
python scripts/generate_comparison.py
```

### Build Documentation

```bash
# Build static site
npm run build

# Preview production build
npm run preview

# Export PDF (requires pandoc + weasyprint)
npm run pdf
```

## 📁 Project Structure

```
communication-guide/
├── docs/                    # VitePress documentation
│   ├── .vitepress/         # VitePress config
│   ├── introduction/       # Overview & classification
│   ├── category1/          # Low BW, Lossy, Long Range (LoRa)
│   ├── category2/          # Low BW, Stable (Thread/Zigbee/BLE)
│   ├── category3/          # High BW, Lossy (WiFi Mesh)
│   ├── category4/          # High BW, Stable (VPN/Routing)
│   ├── cross-cutting/      # Security, Power, Testing, Migration
│   ├── scraping/           # DeepWiki scraping docs
│   ├── scraped/            # Raw scraped content (auto-generated)
│   └── rules/              # Extracted protocol rules (auto-generated)
├── scripts/                # Automation scripts
│   ├── scrape_deepwiki.py  # DeepWiki scraper
│   ├── extract_rules.py    # Rule extractor
│   ├── generate_comparison.py
│   └── validate_examples.py
├── examples/               # ESP32/PlatformIO examples
│   ├── esp32-loramesher/
│   ├── esp32-meshtastic/
│   ├── esp32-ble-mesh/
│   ├── esp32s3-wifi-mesh-babel/
│   ├── esp32s3-wireguard/
│   └── esp32s3-openthread-rcp/
├── data/                   # Comparison matrices (CSV)
├── .github/workflows/      # CI/CD pipelines
└── package.json            # Node dependencies
```

## 🧪 Testing Examples

```bash
# Validate all ESP32 examples compile
python scripts/validate_examples.py

# Run specific protocol benchmark
python scripts/run_benchmarks.py --protocol loramesher --topology line --nodes 5
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python scripts/validate_examples.py`
5. Submit a Pull Request

### Adding New Protocols

1. Add protocol to appropriate category in `docs/`
2. Add DeepWiki source to `scripts/scrape_deepwiki.py`
3. Add ESP32 setup guide
4. Add comparison matrix entries
5. Update navigation in `.vitepress/config.ts`

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **LoRaMesher** team for TDMA LoRa mesh research
- **Meshtastic** community for battle-tested LoRa messaging
- **OpenThread** team for Thread 1.4 implementation
- **ESP-IDF** team for excellent ESP32 platform support
- **OpenWrt Routing** for BATMAN-ADV, Babel, OLSR packages
- **DeepWiki** for making codebases queryable

## 📚 References

- [LoRaMesher Protocol Spec](https://github.com/LoRaMesher/LoRaMesher/blob/main/PROTOCOL_SPEC.md)
- [Meshtastic Documentation](https://meshtastic.org/docs/)
- [OpenThread Guides](https://openthread.io/guides/)
- [Thread Specification 1.4](https://www.threadgroup.org/)
- [Zigbee 3.0 Specification](https://csa-iot.org/all-solutions/zigbee/)
- [Bluetooth Mesh 1.0.1](https://www.bluetooth.com/specifications/mesh/)
- [WireGuard Protocol](https://www.wireguard.com/protocol/)
- [BIRD2 Documentation](https://bird.network.cz/)
- [RFC 8966 (Babel)](https://datatracker.ietf.org/doc/rfc8966/)
- [RFC 6550 (RPL)](https://datatracker.ietf.org/doc/rfc6550/)

---

**Built with ❤️ for the embedded community**