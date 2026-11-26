# DeepWiki Source Inventory

## Indexed Repositories

This document catalogs all DeepWiki-indexed repositories used as sources for the Communication Protocols Guide.

## Primary Sources

### 1. Meshtastic Firmware
- **Repository**: `meshtastic/firmware`
- **DeepWiki URL**: https://deepwiki.com/meshtastic/firmware
- **GitHub**: https://github.com/meshtastic/firmware
- **Category**: Low Bandwidth, Lossy, Long Range (Cat 1)
- **Last Indexed**: 2026-06-27 (ec5d230)
- **Stars**: 8.6k
- **Key Sections**:
  - Overview & Architecture
  - Device Initialization & Startup
  - Mesh Networking Core (Router, MeshService)
  - Radio Hardware Interfaces (SX1262, SX1276, etc.)
  - Protocol Buffer System
  - External Communication Interfaces (BLE, WiFi, Serial, MQTT)
  - Module Implementations (Telemetry, Position, UI)
  - Platform Ports (ESP32, nRF52, RP2040, Linux)

### 2. LoRaMesher
- **Repository**: `LoRaMesher/LoRaMesher`
- **DeepWiki URL**: https://deepwiki.com/LoRaMesher/LoRaMesher
- **GitHub**: https://github.com/LoRaMesher/LoRaMesher
- **Category**: Low Bandwidth, Lossy, Long Range (Cat 1)
- **Last Indexed**: 2025-05-21 (ae18690)
- **Stars**: 319
- **Key Sections**:
  - Overview & Architecture
  - Getting Started & Configuration
  - Core Architecture (LoraMesher Class, Task Management)
  - Packet System (Types, Factory, Queues)
  - Routing System (Distance Vector + ETX)
  - Hardware Abstraction (SX1262, SX1276, SX1280)
  - Reliable Messaging
  - Examples (Counter, Display, Large Payload)
  - Advanced Features (Simulation, WiFi Integration)

### 3. ESP-IDF (Espressif IoT Development Framework)
- **Repository**: `espressif/esp-idf`
- **DeepWiki URL**: https://deepwiki.com/espressif/esp-idf
- **GitHub**: https://github.com/espressif/esp-idf
- **Category**: Platform (All Categories)
- **Last Indexed**: 2026-09-29 (4d59230)
- **Stars**: 19.6k
- **Key Sections**:
  - ESP-IDF Overview & Architecture
  - Getting Started & Environment Setup
  - Connectivity (WiFi, Bluetooth, Thread, Zigbee, 802.15.4)
  - System Features (Power Management, FreeRTOS, Memory)
  - Peripheral Drivers (UART, SPI, I2C, ADC, etc.)
  - Storage (NVS, FAT, SPIFFS)
  - Security (TLS, Secure Boot, Flash Encryption)
  - Build System (CMake, idf.py)
  - SoC Capability Mapping

### 4. OpenWrt Routing
- **Repository**: `openwrt/routing`
- **DeepWiki URL**: https://deepwiki.com/openwrt/routing
- **GitHub**: https://github.com/openwrt/routing
- **Category**: High Bandwidth, Lossy (Cat 3)
- **Last Indexed**: 2025-10-10 (45221cf)
- **Stars**: 401
- **Key Sections**:
  - B.A.T.M.A.N. Advanced (batman-adv, batctl, alfred)
  - OLSR Family (olsrd, olsrd2/OONF, DLEP)
  - Modern Mesh Protocols (Babel, BMX7, cjdns)
  - BIRD Internet Routing Daemon
  - Captive Portal Solutions
  - Network Services (UPnP, mesh11sd, pimbd)
  - Build System & CI

### 5. OpenThread
- **Repository**: `openthread/openthread`
- **DeepWiki URL**: https://deepwiki.com/openthread/openthread
- **GitHub**: https://github.com/openthread/openthread
- **Category**: Low Bandwidth, Stable (Cat 2)
- **Last Indexed**: Loading...
- **Stars**: 4.1k
- **Key Sections**:
  - OpenThread Overview
  - Thread Stack Architecture
  - Commissioning & Security
  - Border Router
  - CLI Reference
  - Platform Ports (ESP32-H2/C6, nRF52840, etc.)
  - Matter Integration

## Secondary Sources (GitHub Direct)

### 6. OpenWrt Main Repository
- **Repository**: `openwrt/openwrt`
- **DeepWiki URL**: https://deepwiki.com/openwrt/openwrt
- **GitHub**: https://github.com/openwrt/openwrt
- **Category**: Platform (Cat 3, 4)
- **Last Indexed**: 2026-10-15 (6ca4da2)
- **Stars**: 29.3k
- **Key Areas**:
  - Build System Architecture
  - Kernel Subsystem
  - Network Configuration (netifd, wifi-scripts)
  - Wireless Subsystem (mac80211, mt76, ath10k)
  - Hardware Platforms (MediaTek, Qualcomm, Realtek, etc.)

### 7. OpenWrt Packages (Routing-related)
- **Repository**: `openwrt/packages`
- **GitHub**: https://github.com/openwrt/packages
- **Relevant Packages**:
  - `net/babeld` - Babel routing daemon
  - `net/bird2` - BIRD2 routing daemon
  - `net/wireguard-tools` - WireGuard userspace tools
  - `kernel/kmod-wireguard` - WireGuard kernel module

### 8. Linux Kernel (Wireless)
- **Repository**: `torvalds/linux`
- **GitHub**: https://github.com/torvalds/linux
- **Relevant Subsystems**:
  - `net/mac80211/` - 802.11 stack (802.11s, HWMP)
  - `net/batman-adv/` - BATMAN-ADV kernel module
  - `drivers/net/wireless/` - WiFi drivers

## Academic & Standards References

### Key Papers (from LoRaMesher DeepWiki)

1. **Solé et al.** "Implementation of a LoRa Mesh Library" — IEEE Access, 2022
   - DOI: 10.1109/ACCESS.2022.3217215
   - Describes LoRaMesher TDMA + Distance Vector design

2. **Solé et al.** "Large and reliable data transfer service for LoRa mesh network applications" — Computer Communications, 2026
   - DOI: 10.1016/j.comcom.2025.108404
   - Large payload transfer over LoRa mesh

### RFCs & Standards

| Protocol | RFC/Standard | Title |
|----------|--------------|-------|
| **Babel** | RFC 8966 | The Babel Routing Protocol |
| **OLSR** | RFC 3626 | Optimized Link State Routing |
| **OLSRv2** | RFC 7181 | OLSRv2 |
| **RPL** | RFC 6550 | Routing Protocol for LLNs |
| **RPL Metrics** | RFC 6551 | RPL Metrics |
| **RPL OF** | RFC 6552 | RPL Objective Functions |
| **6LoWPAN** | RFC 4944/6282 | IPv6 over LoWPAN |
| **Thread** | Thread Spec 1.4 | Thread Group Specification |
| **Babel** | RFC 8966 | The Babel Routing Protocol |
| **WireGuard** | Noise_IK | WireGuard Protocol |
| **802.11s** | IEEE 802.11s-2011 | Mesh Networking |
| **Thread** | Thread Spec 1.4 | Thread Group Specification |
| **Zigbee** | Zigbee 3.0 | CSA Specification |
| **BLE Mesh** | Mesh 1.0.1 | Bluetooth SIG |

## Source Quality Assessment

### Reliability Scores

| Source | Completeness | Accuracy | Freshness | Overall |
|--------|--------------|----------|-----------|---------|
| Meshtastic DeepWiki | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★★ |
| LoRaMesher DeepWiki | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★★ |
| ESP-IDF DeepWiki | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ |
| OpenWrt Routing DeepWiki | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| OpenThread DeepWiki | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| OpenWrt Main DeepWiki | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★☆ |

### Update Frequency

| Source | DeepWiki Index | GitHub Commits | Release Cycle |
|--------|----------------|----------------|---------------|
| Meshtastic | Weekly | Daily | Monthly |
| LoRaMesher | Weekly | Weekly | Quarterly |
| ESP-IDF | Weekly | Daily | Quarterly |
| OpenWrt Routing | Monthly | Daily | 6 months |
| OpenThread | Monthly | Weekly | Quarterly |

## Access Patterns

### DeepWiki API Usage

```bash
# Index page (lists all pages)
curl https://deepwiki.com/meshtastic/firmware

# Specific page
curl https://deepwiki.com/meshtastic/firmware/5-mesh-networking-core

# Search (if available)
curl "https://deepwiki.com/search?q=mesh+routing"
```

### Rate Limits

- **DeepWiki**: ~30 req/min per IP
- **GitHub API**: 5000 req/hr (authenticated)
- **Respect**: 429 responses, implement backoff

## Citation Format

When citing DeepWiki sources in the guide:

```markdown
[DeepWiki:meshtastic/firmware] 
→ https://deepwiki.com/meshtastic/firmware

[DeepWiki:LoRaMesher/LoRaMesher] 
→ https://deepwiki.com/LoRaMesher/LoRaMesher

[DeepWiki:espressif/esp-idf] 
→ https://deepwiki.com/espressif/esp-idf

[DeepWiki:openwrt/routing] 
→ https://deepwiki.com/openwrt/routing

[DeepWiki:openthread/openthread] 
→ https://deepwiki.com/openthread/openthread
```

## Maintenance

### Weekly Updates

- Automated scraping via GitHub Actions
- Rule extraction from new content
- Comparison matrix regeneration
- Documentation rebuild

### Manual Updates Needed

- Academic paper citations (quarterly)
- RFC updates (as published)
- Major version releases (manual review)
- Breaking changes in protocols

## Access Links Summary

| Repository | DeepWiki | GitHub | Raw Docs |
|------------|----------|--------|----------|
| Meshtastic | [link](https://deepwiki.com/meshtastic/firmware) | [link](https://github.com/meshtastic/firmware) | [link](https://meshtastic.org/docs/) |
| LoRaMesher | [link](https://deepwiki.com/LoRaMesher/LoRaMesher) | [link](https://github.com/LoRaMesher/LoRaMesher) | [link](https://github.com/LoRaMesher/LoRaMesher/tree/main/docs) |
| ESP-IDF | [link](https://deepwiki.com/espressif/esp-idf) | [link](https://github.com/espressif/esp-idf) | [link](https://docs.espressif.com/) |
| OpenWrt Routing | [link](https://deepwiki.com/openwrt/routing) | [link](https://github.com/openwrt/routing) | [link](https://openwrt.org/docs/guide-user/network/) |
| OpenThread | [link](https://deepwiki.com/openthread/openthread) | [link](https://github.com/openthread/openthread) | [link](https://openthread.io/) |