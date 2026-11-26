# Communication Protocols Guide for Embedded Devices

## Purpose

This guide provides a comprehensive reference for selecting, configuring, and deploying communication protocols on embedded devices (ESP32, ESP32-S3) across four bandwidth/stability categories:

| Category | Bandwidth | Stability | Range | Typical Use Cases |
|----------|-----------|-----------|-------|-------------------|
| **Low BW, Lossy, Long Range** | < 1 kbps | High loss | 1-50+ km | LoRa mesh, sensor networks, off-grid comms |
| **Low BW, Stable** | 250 kbps - 1 Mbps | Low loss | 10-100 m | Thread, Zigbee, BLE Mesh, home automation |
| **High BW, Lossy** | 1-50 Mbps | Medium loss | 100 m - 1 km | WiFi mesh (BATMAN-ADV, Babel), mobile ad-hoc |
| **High BW, Stable** | 100 Mbps - 1 Gbps | Very low loss | LAN/WAN | WireGuard, BIRD (OSPF/BGP), cjdns |

## How to Use This Guide

1. **Identify your category** - Match your bandwidth, stability, and range requirements
2. **Compare protocols** - Use the comparison matrices in each section
3. **Follow ESP32 setup** - Step-by-step PlatformIO/ESP-IDF instructions
4. **Tune performance** - Apply category-specific optimization guidelines

## Device Classification Matrix

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

## Protocol Landscape Overview

### Category 1: Low Bandwidth, Lossy, Long Range
| Protocol | Architecture | Routing | Key Feature | ESP32 Support |
|----------|--------------|---------|-------------|---------------|
| **LoRaMesher** | TDMA + Distance Vector | ETX cost metric | Sponsor-based join, power-aware slots | ✅ PlatformIO |
| **Meshtastic** | Flooding + ReliableRouter | Hop-limited flood | Battle-tested, MQTT gateway, 8.6k★ | ✅ ESP-IDF |
| **BATMAN-ADV (LoRa)** | Layer 2 mesh | OGM flooding | Kernel fast-path, transparent bridging | ⚠️ Linux host |

### Category 2: Low Bandwidth, Stable
| Protocol | Architecture | Routing | Key Feature | ESP32 Support |
|----------|--------------|---------|-------------|---------------|
| **OpenThread** | IPv6/6LoWPAN | RPL (RFC 6550) | Thread 1.4 certified, Matter ready | ✅ ESP32-H2/C6 |
| **Zigbee** | IEEE 802.15.4 | AODV + Clusters | Mature ecosystem, Green Power | ✅ ESP32-H2/C6 |
| **BLE Mesh** | Managed Flood | Friend/Relay/Proxy | Phone provisioning, no border router | ✅ ESP32/ESP32-S3 |

### Category 3: High Bandwidth, Lossy
| Protocol | Architecture | Routing | Key Feature | ESP32 Support |
|----------|--------------|---------|-------------|---------------|
| **BATMAN-ADV** | Layer 2 (kernel) | OGM + ETX | Transparent L2, roaming, VLAN | ⚠️ OpenWrt |
| **Babel** | Layer 3 (user) | Distance Vector + ETX | RFC 8966, fast convergence, ubus | ✅ ESP32-S3 |
| **802.11s** | Layer 2 (HWMP) | Path Request/Reply | Native WiFi, standard | ✅ ESP32-S3 |

### Category 4: High Bandwidth, Stable
| Protocol | Architecture | Routing | Key Feature | ESP32 Support |
|----------|--------------|---------|-------------|---------------|
| **WireGuard** | L3 VPN (kernel) | Static/CryptoKey | 1 RTT handshake, roaming | ✅ ESP32-S3 |
| **BIRD2** | User daemon | OSPF/BGP/RIP | Production-grade, filters | ⚠️ Linux host |
| **cjdns** | Overlay (user) | DHT + Crypto | E2E encrypted, IPv6, self-organizing | ⚠️ Linux host |

## Quick Selection Guide

### Choose **LoRaMesher** if:
- Need 1-50 km range with <1 kbps
- Battery-powered nodes (TDMA sleep)
- Deterministic latency required
- Can use SX1262/SX1276 hardware

### Choose **Meshtastic** if:
- Want plug-and-play with mobile app
- Need MQTT/cloud integration
- Community support important
- OK with flooding-based routing

### Choose **OpenThread** if:
- Building Matter/Thread devices
- Need IPv6 end-to-end
- Have 802.15.4 radio (ESP32-H2/C6)
- Border router for internet access

### Choose **Babel** if:
- WiFi mesh with mobile nodes
- Need fast convergence (<1s)
- Dual-stack IPv4/IPv6
- OpenWrt/Ubuntu/Debian target

### Choose **WireGuard** if:
- Site-to-site or road-warrior VPN
- High throughput, low latency
- Simple configuration
- Kernel support available

## Source Attribution

This guide aggregates and structures information from:
- **DeepWiki** documentation for each repository
- **GitHub** source code and specifications
- **Academic papers** (IEEE Access 2022, Computer Communications 2026)
- **RFCs** and **IEEE standards**
- **Vendor documentation** (Espressif, Semtech, Silicon Labs)

Each section cites sources inline with `[DeepWiki:repo/section]` or `[GitHub:repo/path]` format.