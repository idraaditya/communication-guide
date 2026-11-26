# Category 2: Low Bandwidth, Stable - Protocol Comparison

## Overview

| Property | **OpenThread** | **Zigbee** | **BLE Mesh** |
|----------|----------------|------------|--------------|
| **Standard** | Thread 1.4 (Thread Group) | Zigbee 3.0 (CSA) | Bluetooth Mesh 1.0.1 (Bluetooth SIG) |
| **PHY/MAC** | IEEE 802.15.4 (2.4 GHz) | IEEE 802.15.4 (2.4 GHz) | BLE 4.2+ (2.4 GHz) |
| **Max Data Rate** | 250 kbps | 250 kbps | 1-2 Mbps (PHY) |
| **Network Layer** | IPv6 / 6LoWPAN | Zigbee Network Layer | Managed Flooding |
| **Routing** | RPL (RFC 6550) | AODV + Tree | Friend/Relay/Proxy |
| **Addressing** | IPv6 (ULA/GUA) | 16-bit NWK + 64-bit IEEE | 16-bit Unicast / Virtual |
| **Security** | AES-CCM* + DTLS | AES-128-CCM | AES-CCM + Provisioning |
| **Commissioning** | DTLS + PSKc / QR | Install codes / Touchlink | Provisioner (PB-ADV/GATT) |
| **Border Router** | Required (NAT64/DNS64/SRP) | Coordinator (ZC) | Optional (Proxy) |
| **IP Connectivity** | Native IPv6 | Via Gateway (Zigbee-IP) | Via Proxy (GATT) |
| **Matter Support** | **Native** (Thread is transport) | Via Bridge | Via Bridge |
| **Max Nodes** | 250+ (per Thread network) | 240+ (per network) | 32767 (theoretical) |
| **ESP32 Support** | ESP32-H2, ESP32-C6 (native 802.15.4) | ESP32-H2, ESP32-C6 (native) | ESP32, ESP32-S3 (BLE) |
| **Maturity** | Thread 1.4 certified (2024) | Zigbee 3.0 (2018), mature | Mesh 1.0.1 (2019), growing |
| **License** | BSD-3 (OpenThread) | Proprietary stack / GPL (ZBOSS) | Apache-2.0 (ESP-BLE-Mesh) |

*OpenThread uses AES-CCM at MAC layer, DTLS at commissioning

---

## Detailed Comparison

### 1. OpenThread (Thread Protocol)

**Source**: [DeepWiki:openthread/openthread] [OpenThread.io] [Thread Spec 1.4]

#### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      OpenThread Stack                           │
├─────────────────────────────────────────────────────────────────┤
│  Application Layer                                              │
│  ├── CoAP / DTLS / UDP / TCP                                    │
│  ├── SNTP / DNS-SD / SRP / mDNS                                 │
│  └── Matter / Custom                                            │
├─────────────────────────────────────────────────────────────────┤
│  Network Layer (IPv6 / 6LoWPAN)                                 │
│  ├── RPL (RFC 6550) - Mesh Routing                              │
│  ├── Mesh Link Establishment (MLE)                              │
│  ├── Address Registration / SLAAC                               │
│  └── NAT64 / DNS64 (Border Router)                             │
├─────────────────────────────────────────────────────────────────┤
│  MAC Layer (IEEE 802.15.4)                                      │
│  ├── CSMA/CA + ACK                                              │
│  ├── Frame Security (AES-CCM)                                   │
│  ├── Beacon / Non-beacon mode                                   │
│  └── Channel Diversity (11-26)                                  │
├─────────────────────────────────────────────────────────────────┤
│  PHY Layer (2.4 GHz O-QPSK, 250 kbps)                          │
├─────────────────────────────────────────────────────────────────┤
│  Platform Abstraction (Radio, Alarm, RNG, UART, etc.)          │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Features

| Feature | Description | Spec |
|---------|-------------|------|
| **RPL Routing** | DODAG with OF0 (hop count) or MRHOF (ETX) | RFC 6550 |
| **MLE** | Secure link establishment, neighbor discovery | Thread Spec |
| **Commissioning** | DTLS + PSKc, QR code, on-mesh | Thread Spec |
| **Border Router** | NAT64, DNS64, SRP, Thread Network Data | Thread Spec |
| **Multicast** | MLD + MPL (RFC 7731) | Thread Spec |
| **Time Sync** | CSL (Connected Sleep) / Time Service | Thread Spec |
| **Matter** | Native transport for Matter 1.2+ | Matter Spec |

#### Device Roles
| Role | Description | Power |
|------|-------------|-------|
| **Leader** | Manages network data, assigns router IDs | Mains |
| **Router** | Forwards packets, can become Leader | Mains |
| **REED** | Router Eligible End Device | Mains/Battery |
| **FED** | Full End Device (always on) | Mains |
| **MED** | Minimal End Device (sleepy) | Battery |
| **SED** | Sleepy End Device (deep sleep) | Battery |
| **Border Router** | Connects Thread to IP network | Mains |

#### Network Data (Distributed)
```json
{
  "network_name": "MyThreadNetwork",
  "xpanid": "0x1234567890abcdef",
  "panid": 0x1234,
  "channel": 15,
  "pskc": "0x1a2b3c4d5e6f78901a2b3c4d5e6f7890",
  "network_key": "0x00112233445566778899aabbccddeeff",
  "router_id_assignments": {...},
  "border_router_config": [...],
  "service_data": [...]
}
```

### 2. Zigbee (Zigbee 3.0)

**Source**: Zigbee Alliance (CSA) specs, ESP-Zigbee SDK

#### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      Zigbee Stack                               │
├─────────────────────────────────────────────────────────────────┤
│  Application Layer (ZCL - Zigbee Cluster Library)              │
│  ├── Lighting, Closures, HVAC, Sensors, etc.                   │
│  ├── Green Power (battery-less switches)                       │
│  └── Touchlink (commissioning)                                 │
├─────────────────────────────────────────────────────────────────┤
│  Network Layer (NWK)                                            │
│  ├── AODV Mesh Routing (RREQ/RREP/RERR)                        │
│  ├── Tree Routing (fallback)                                   │
│  ├── Address Assignment (Distributed)                          │
│  └── Frame Security (AES-128-CCM)                              │
├─────────────────────────────────────────────────────────────────┤
│  MAC Layer (IEEE 802.15.4)                                      │
│  ├── CSMA/CA, Beacon/Non-beacon                                │
│  ├── GTS (Guaranteed Time Slots)                               │
│  └── Channel 11-26                                             │
├─────────────────────────────────────────────────────────────────┤
│  PHY Layer (2.4 GHz O-QPSK, 250 kbps)                          │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Features

| Feature | Description |
|---------|-------------|
| **AODV Routing** | On-demand route discovery, route cache |
| **Cluster Library** | Standardized device profiles (Lighting, HA, SE) |
| **Green Power** | Battery-less switches, energy harvesting |
| **Touchlink** | Commissioning without coordinator |
| **Install Codes** | Secure join with pre-shared keys |
| **OTA Updates** | Zigbee OTA cluster |

#### Device Types
| Type | Description | Power |
|------|-------------|-------|
| **Coordinator (ZC)** | Forms network, assigns addresses | Mains |
| **Router (ZR)** | Extends network, routes packets | Mains |
| **End Device (ZED)** | Sleepy, no routing | Battery |

### 3. BLE Mesh (Bluetooth Mesh 1.0.1)

**Source**: Bluetooth SIG Mesh Spec, ESP-BLE-Mesh

#### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      BLE Mesh Stack                             │
├─────────────────────────────────────────────────────────────────┤
│  Models Layer                                                   │
│  ├── Generic (OnOff, Level, Power, Battery, etc.)              │
│  ├── Sensor, Time, Scene, Scheduler                            │
│  ├── Lighting (Light Lightness, CTL, HSL, xyL)                 │
│  └── Vendor Models                                              │
├─────────────────────────────────────────────────────────────────┤
│  Access Layer                                                   │
│  ├── Addressing (Unicast, Group, Virtual)                      │
│  ├── Message Dispatch                                           │
│  └── Replay Protection (IV Index + Seq)                        │
├─────────────────────────────────────────────────────────────────┤
│  Upper Transport / Lower Transport                              │
│  ├── Segmentation & Reassembly (SAR)                           │
│  ├── Encryption (AES-CCM, AppKey/NetKey/DevKey)                │
│  └── Friendship / Proxy / Relay                                │
├─────────────────────────────────────────────────────────────────┤
│  Network Layer                                                  │
│  ├── Managed Flooding (TTL, Seq, IV Index)                     │
│  ├── Subnet / NetKey Management                                │
│  └── IV Update Procedure                                       │
├─────────────────────────────────────────────────────────────────┤
│  Bearer Layer (Advertising / GATT)                             │
│  ├── PB-ADV (Provisioning Bearer - Advertising)                │
│  ├── PB-GATT (Provisioning Bearer - GATT)                      │
│  └── Mesh Profile (Mesh Message / Mesh Beacon)                 │
├─────────────────────────────────────────────────────────────────┤
│  BLE Controller (LL) - 2.4 GHz, 1M/2M PHY                      │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Features

| Feature | Description |
|---------|-------------|
| **Managed Flooding** | TTL-based, Relay nodes retransmit |
| **Friendship** | Low Power Nodes (LPN) cache at Friend |
| **Proxy** | GATT connection for non-Mesh devices (phones) |
| **Provisioning** | PB-ADV (beacon) or PB-GATT (GATT) |
| **Models** | Standardized behaviors (Generic, Sensor, Lighting) |
| **Subnets** | Multiple NetKeys for isolation |
| **IV Update** | Key refresh every 96 hours |

#### Node Roles
| Role | Description | Power |
|------|-------------|-------|
| **Relay** | Retransmits mesh messages | Mains |
| **Friend** | Caches messages for LPN | Mains |
| **LPN** | Low Power Node (sleeps, polls Friend) | Battery |
| **Proxy** | GATT interface for phones | Mains |
| **Provisioner** | Adds devices to network | Phone/Hub |

---

## Comparison Matrix

### Network Formation

| Aspect | OpenThread | Zigbee | BLE Mesh |
|--------|------------|--------|----------|
| **Network Creation** | Leader elected automatically | Coordinator forms | Provisioner creates |
| **Join Process** | DTLS commissioning | Install code / Touchlink | PB-ADV / PB-GATT |
| **Address Assignment** | IPv6 SLAAC + DHCPv6 | Distributed (16-bit) | Provisioner assigns |
| **Network Size** | 250+ routers + children | 240 routers + children | 32767 (theoretical) |
| **Partition Handling** | Merge via Leader | Rejoin via Trust Center | Reprovision |

### Routing

| Aspect | OpenThread | Zigbee | BLE Mesh |
|--------|------------|--------|----------|
| **Algorithm** | RPL (DODAG) | AODV + Tree | Managed Flooding |
| **Metric** | OF0 (hops) / MRHOF (ETX) | Path cost | TTL + Relay count |
| **Convergence** | Fast (Trickle timer) | Route discovery | N/A (flooding) |
| **Loop Prevention** | DAG rank | Sequence numbers | TTL + Seq + IV Index |
| **Multicast** | MPL (RFC 7731) | Group addressing | Group / Virtual addr |

### Security

| Aspect | OpenThread | Zigbee | BLE Mesh |
|--------|------------|--------|----------|
| **Link Encryption** | AES-CCM (MAC) | AES-128-CCM | AES-CCM |
| **Key Hierarchy** | Master Key → Keys | Master Key → Keys | NetKey → AppKey → DevKey |
| **Commissioning Auth** | DTLS + PSKc | Install Code / TC | ECDH + OOB |
| **Key Rotation** | Periodic (MLE) | Periodic (TC) | IV Update (96h) |
| **Replay Protection** | Frame counter | Frame counter | Seq + IV Index |

### Power Profiles

| Profile | OpenThread | Zigbee | BLE Mesh |
|---------|------------|--------|----------|
| **Always On (Router)** | ~15 mA RX, ~20 mA TX | Similar | ~15 mA (Relay) |
| **Sleepy (MED/SED)** | CSL: ~100 µA avg | Poll: ~50-100 µA | LPN: ~10-50 µA |
| **Deep Sleep (SED)** | ~5 µA (RTC wake) | ~5 µA | ~5 µA |
| **Wake Interval** | CSL: 100-2000ms | Poll: 100ms-7.5s | LPN poll: 100ms-4h |

### Ecosystem & Interop

| Aspect | OpenThread | Zigbee | BLE Mesh |
|--------|------------|--------|----------|
| **Certification** | Thread Certified Component | Zigbee Certified | Bluetooth Mesh Qualified |
| **Matter Support** | **Native transport** | Bridge required | Bridge required |
| **Phone App** | Thread Commissioning app | Vendor apps | nRF Mesh, vendor apps |
| **Gateways** | Border Router (OpenWrt, RPi) | Zigbee Coordinator + HA | Proxy (Phone, Hub) |
| **Cloud** | SRP + DNS-SD | Vendor clouds | Vendor clouds |
| **Vendors** | Google, Apple, Amazon, Nordic, Espressif, etc. | Silicon Labs, NXP, TI, etc. | Nordic, Silicon Labs, Espressiv, etc. |

---

## When to Choose Which

### Choose **OpenThread** if:
- ✅ Building **Matter** devices (Thread is mandatory transport)
- ✅ Need **native IPv6** connectivity
- ✅ Want **standardized** routing (RPL) and commissioning
- ✅ Have **ESP32-H2/C6** or nRF52840/CC2652 hardware
- ✅ Need **border router** for IP integration
- ✅ Prefer **BSD-3** license, open source

### Choose **Zigbee** if:
- ✅ Integrating with **existing Zigbee ecosystem** (hue, SmartThings, HA)
- ✅ Need **Green Power** (battery-less switches)
- ✅ Using **Zigbee Cluster Library** profiles
- ✅ Have **Silicon Labs/NXP/TI** SoCs or ESP32-H2/C6
- ✅ Don't need IPv6 natively

### Choose **BLE Mesh** if:
- ✅ **Phone provisioning** critical (no border router needed)
- ✅ **Bluetooth** already in product (reuse radio)
- ✅ Need **Lighting models** (standardized)
- ✅ Using **ESP32/ESP32-S3** (no 802.15.4 radio)
- ✅ Small networks, simple deployment

### Hardware Decision

| Hardware | OpenThread | Zigbee | BLE Mesh |
|----------|------------|--------|----------|
| **ESP32-H2** | ✅ Native | ✅ Native | ✅ BLE 5.3 |
| **ESP32-C6** | ✅ Native | ✅ Native | ✅ BLE 5.3 + WiFi 6 |
| **ESP32-S3** | ❌ No 802.15.4 | ❌ No 802.15.4 | ✅ Native |
| **ESP32** | ❌ No 802.15.4 | ❌ No 802.15.4 | ✅ Native |
| **nRF52840** | ✅ OpenThread | ✅ Zigbee | ✅ BLE Mesh |
| **CC2652P7** | ✅ OpenThread | ✅ Zigbee | ✅ BLE Mesh |
| **Silicon Labs xG24** | ✅ OpenThread | ✅ Zigbee | ✅ BLE Mesh |

---

## Hybrid Deployments

Many products combine protocols:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART HOME HUB                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Thread     │  │  Zigbee     │  │  BLE Mesh   │             │
│  │  (Matter)   │  │  (Legacy)   │  │  (Phone)    │             │
│  │  ESP32-H2   │  │  EFR32MG21  │  │  ESP32-S3   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│              ┌─────────────────────┐                            │
│              │   Application CPU   │                            │
│              │   (Linux / ESP32-P4)│                            │
│              │   Matter Controller │                            │
│              │   Home Assistant    │                            │
│              └─────────────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Migration Paths

| From | To | Effort | Notes |
|------|-----|--------|-------|
| Zigbee → Thread | Medium | Matter bridge, new hardware |
| BLE Mesh → Thread | Medium | Matter bridge, new hardware |
| Zigbee ↔ BLE Mesh | Low | Dual-radio gateway |
| Thread (OpenThread) → Thread (Silabs) | Low | Same protocol, different stack |

---

## References

- **OpenThread**: https://openthread.io/ | [DeepWiki](https://deepwiki.com/openthread/openthread)
- **Thread Spec 1.4**: https://www.threadgroup.org/
- **Matter Spec**: https://csa-iot.org/all-solutions/matter/
- **Zigbee 3.0**: https://csa-iot.org/all-solutions/zigbee/
- **Bluetooth Mesh**: https://www.bluetooth.com/specifications/mesh/
- **ESP-Thread**: https://github.com/espressif/esp-thread
- **ESP-Zigbee**: https://github.com/espressif/esp-zigbee-sdk
- **ESP-BLE-Mesh**: https://github.com/espressif/esp-idf/tree/master/examples/bluetooth/ble_mesh
- **RPL**: RFC 6550, RFC 6551, RFC 6552
- **6LoWPAN**: RFC 4944, RFC 6282
- **MLE**: Thread Specification