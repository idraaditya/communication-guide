# Protocol Landscape Map

## Visual Protocol Taxonomy

```
MESH NETWORKING PROTOCOLS
├── LAYER 2 (Data Link)
│   ├── BATMAN-ADV (Better Approach To Mobile Adhoc Networking Advanced)
│   │   ├── Kernel module (Linux)
│   │   ├── OGM (Originator Messages) flooding
│   │   ├── Features: BLA, DAT, NC, MCAST, fragmentation
│   │   └── Platforms: OpenWrt, Linux, (ESP32 via Linux host)
│   │
│   ├── 802.11s (IEEE WiFi Mesh)
│   │   ├── HWMP (Hybrid Wireless Mesh Protocol)
│   │   ├── Path Request/Reply (PREP/PREQ)
│   │   ├── Radio metrics: Airtime Link Metric
│   │   └── Platforms: Linux mac80211, ESP32-S3
│   │
│   └── cjdns (Caleb James DeLisle Network Suite)
│       ├── Layer 2.5 / 3 overlay
│       ├── Crypto-authenticated IPv6
│       ├── DHT-based routing (Kademlia-like)
│       └── Platforms: Linux, OpenWrt, (not ESP32 native)
│
├── LAYER 3 (Network)
│   ├── Distance Vector
│   │   ├── Babel (RFC 8966)
│   │   │   ├── ETX (Expected Transmission Count) metric
│   │   │   ├── Dual-stack IPv4/IPv6
│   │   │   ├── Fast convergence (~1s)
│   │   │   └── Platforms: OpenWrt, Linux, BSD, ESP32-S3
│   │   │
│   │   ├── LoRaMesher
│   │   │   ├── TDMA superframe scheduling
│   │   │   ├── Distance vector + ETX cost
│   │   │   ├── Sponsor-based join
│   │   │   ├── Network Manager election
│   │   │   └── Platforms: ESP32 (PlatformIO), Linux sim
│   │   │
│   │   └── AODV (Ad hoc On-Demand Distance Vector)
│   │       ├── Reactive (on-demand route discovery)
│   │       ├── RREQ/RREP/RERR messages
│   │       └── Used in: Zigbee, some MANETs
│   │
│   ├── Link State
│   │   ├── OLSR (Optimized Link State Routing) - RFC 3626
│   │   │   ├── MPR (MultiPoint Relays) for flooding reduction
│   │   │   ├── HELLO + TC (Topology Control) messages
│   │   │   └── Platforms: OpenWrt (olsrd, olsrd2/OONF)
│   │   │
│   │   ├── OSPF (Open Shortest Path First) - RFC 2328
│   │   │   ├── Dijkstra SPF, areas, LSA flooding
│   │   │   └── Platforms: BIRD2, FRR, Quagga (Linux/OpenWrt)
│   │   │
│   │   └── IS-IS (Intermediate System to Intermediate System)
│   │       ├── TLV-based, hierarchical
│   │       └── Platforms: BIRD2, FRR
│   │
│   ├── Path Vector
│   │   └── BGP (Border Gateway Protocol) - RFC 4271
│   │       ├── Policy-based routing
│   │       ├── AS_PATH attribute
│   │       └── Platforms: BIRD2, FRR, GoBGP
│   │
│   └── Hybrid / Specialized
│       ├── RPL (Routing Protocol for Low-Power and Lossy Networks) - RFC 6550
│       │   ├── DODAG (Destination-Oriented DAG)
│       │   ├── OF0 (Objective Function 0) - hop count
│       │   ├── MRHOF (Minimum Rank with Hysteresis OF) - ETX
│       │   ├── Trickle timer for control traffic
│       │   └── Platforms: OpenThread (Thread), Contiki-NG, RIOT
│       │
│       ├── WireGuard (VPN, not routing per se)
│       │   ├── Noise_IK handshake (1-RTT)
│       │   ├── ChaCha20-Poly1305 encryption
│       │   ├── Cryptokey routing (IP = public key)
│       │   └── Platforms: Linux kernel, WireGuard-go, ESP32-S3
│       │
│       └── Yggdrasil
│           ├── DHT + Tree routing
│           ├── End-to-end encrypted IPv6
│           └── Platforms: Linux, OpenWrt, Windows, macOS
│
└── LAYER 3.5 / APPLICATION (Mesh over existing IP)
    ├── Meshtastic
    │   ├── Flooding-based (TTL-limited)
    │   ├── ReliableRouter for directed unicast
    │   ├── Protobuf serialization
    │   ├── MQTT/TCP gateway
    │   └── Platforms: ESP32, nRF52, RP2040, Linux
    │
    ├── BLE Mesh (Bluetooth SIG)
    │   ├── Managed flooding (Friend/Relay/Proxy/LPN)
    │   ├── Provisioning via PB-ADV / PB-GATT
    │   ├── Models: Generic, Sensor, Lighting, Scene
    │   └── Platforms: ESP32/ESP32-S3 (ESP-BLE-Mesh), nRF52, STM32
    │
    └── Thread (Thread Group)
        ├── IPv6/6LoWPAN over 802.15.4
        ├── RPL routing + Mesh Link Establishment (MLE)
        ├── Commissioning (DTLS + PSKc)
        ├── Border Router (NAT64, DNS64, SRP)
        └── Platforms: OpenThread (ESP32-H2/C6, nRF52840, CC2652)

```

## Protocol-to-Category Mapping

| Protocol | Primary Category | Secondary | Layer | Maturity | ESP32 Native |
|----------|------------------|-----------|-------|----------|--------------|
| LoRaMesher | Cat 1 | - | L3 | Beta (1.0) | ✅ PlatformIO |
| Meshtastic | Cat 1 | - | L3.5 | Stable (2.x) | ✅ ESP-IDF |
| BATMAN-ADV | Cat 3 | Cat 1* | L2 | Stable | ⚠️ Linux host |
| 802.11s | Cat 3 | - | L2 | Standard | ✅ ESP32-S3 |
| Babel | Cat 3 | Cat 4* | L3 | Stable (RFC) | ✅ ESP32-S3 |
| OpenThread | Cat 2 | - | L3.5 | Stable (1.4) | ✅ ESP32-H2/C6 |
| Zigbee | Cat 2 | - | L3.5 | Stable | ✅ ESP32-H2/C6 |
| BLE Mesh | Cat 2 | - | L3.5 | Stable | ✅ ESP32/S3 |
| WireGuard | Cat 4 | Cat 3* | L3 | Stable | ✅ ESP32-S3 |
| BIRD2 (OSPF/BGP) | Cat 4 | - | L3 | Stable | ⚠️ Linux host |
| cjdns | Cat 4 | Cat 3* | L2.5 | Beta | ❌ |
| OLSR/OLSRv2 | Cat 3 | - | L3 | Stable | ⚠️ OpenWrt |
| Yggdrasil | Cat 4 | Cat 3* | L3 | Beta | ❌ |

*With appropriate radio (e.g., BATMAN-ADV over LoRa for Cat 1)

## Key Protocol Properties Comparison

### Routing Algorithm Type

| Type | Protocols | Convergence | Overhead | Best For |
|------|-----------|-------------|----------|----------|
| **Proactive (Table-driven)** | OLSR, Babel, RPL, OSPF | Fast | Continuous | Stable topologies |
| **Reactive (On-demand)** | AODV, DSR | Slow (first packet) | Low | Mobile, sparse traffic |
| **Hybrid** | BATMAN-ADV (L2), Meshtastic (flood+unicast) | Medium | Medium | Mixed |
| **Flooding-based** | Meshtastic (broadcast), BLE Mesh | N/A | High | Small networks, low duty |
| **TDMA-scheduled** | LoRaMesher | Deterministic | Predictable | Battery, long range |

### Scalability Limits (Typical)

| Protocol | Max Nodes | Max Hops | Network Diameter | Control Traffic |
|----------|-----------|----------|------------------|-----------------|
| LoRaMesher | ~100 | 10 | 10 | Low (TDMA slots) |
| Meshtastic | ~100 | 7 | 7 | Medium (flooding) |
| BATMAN-ADV | ~500 | 20 | 20 | Medium (OGM) |
| Babel | ~1000 | 30 | 30 | Low (triggered) |
| OpenThread | ~250 | 15 | 15 | Low (Trickle) |
| OSPF (BIRD) | ~10000 | Unlimited | Large | High (LSA) |
| BGP (BIRD) | Internet-scale | AS hops | Global | Policy-based |
| WireGuard | Point-to-point | 1 | N/A | Minimal (keepalive) |
| cjdns | ~10000 | DHT hops | Log(N) | DHT maintenance |

### Security Properties

| Protocol | Encryption | Authentication | Key Management | Forward Secrecy |
|----------|------------|----------------|----------------|-----------------|
| LoRaMesher | AES-128-CTR | AES-CMAC | PSK / AppKey | ❌ |
| Meshtastic | AES-256-CTR | AES-CMAC | PSK / QR code | ❌ |
| BATMAN-ADV | ❌ (L2) | ❌ | N/A | N/A |
| 802.11s | AES-CCMP | SAE/PSK | 4-way handshake | ✅ |
| Babel | ❌ (plain) | ❌ | N/A | N/A |
| OpenThread | AES-CCM* | DTLS/PSKc | Commissioner | ✅ (session) |
| Zigbee | AES-128-CCM | Link/Network keys | Trust Center | ✅ (session) |
| BLE Mesh | AES-CCM | NetKey/AppKey | Provisioner | ✅ (session) |
| WireGuard | ChaCha20-Poly1305 | Noise_IK | Static keys | ✅ (1-RTT) |
| cjdns | Curve25519/ChaCha20 | CryptoKey | Self-certifying | ✅ |
| Yggdrasil | Curve25519/ChaCha20 | CryptoKey | Self-certifying | ✅ |

*OpenThread uses AES-CCM at MAC layer, DTLS at commissioning

## Decision Flowchart

```
START: What is your PRIMARY constraint?
│
├─► RANGE > 1 km AND battery-powered?
│   │
│   ├─► YES → Category 1 (LoRa)
│   │   ├─► Need deterministic latency? → LoRaMesher (TDMA)
│   │   ├─► Want mobile app + cloud? → Meshtastic
│   │   └─► Need L2 transparency? → BATMAN-ADV over LoRa (experimental)
│   │
│   └─► NO → Continue
│
├─► RANGE < 100m AND stable links?
│   │
│   ├─► YES → Category 2 (802.15.4/BLE)
│   │   ├─► Building Matter/Thread device? → OpenThread (ESP32-H2/C6)
│   │   ├─► Need Zigbee ecosystem? → Zigbee (ESP32-H2/C6)
│   │   ├─► Phone provisioning, no border router? → BLE Mesh (ESP32/S3)
│   │   └─► IPv6 end-to-end required? → OpenThread
│   │
│   └─► NO → Continue
│
├─► HIGH THROUGHPUT (>1 Mbps) over LOSSY wireless?
│   │
│   ├─► YES → Category 3 (WiFi Mesh)
│   │   ├─► Need L2 transparency (bridging)? → BATMAN-ADV (OpenWrt)
│   │   ├─► Need L3 routing, fast convergence? → Babel (ESP32-S3/Linux)
│   │   ├─► Standard WiFi mesh? → 802.11s (ESP32-S3)
│   │   └─► Mobile nodes, roaming? → Babel or BATMAN-ADV
│   │
│   └─► NO → Continue
│
├─► HIGH THROUGHPUT over STABLE links?
│   │
│   ├─► YES → Category 4
│   │   ├─► Simple VPN, point-to-point? → WireGuard (ESP32-S3/Linux)
│   │   ├─► Dynamic routing, multi-site? → BIRD2 OSPF/BGP (Linux)
│   │   ├─► Encrypted overlay, no PKI? → cjdns / Yggdrasil (Linux)
│   │   └─► Enterprise routing? → BIRD2 / FRR
│   │
│   └─► NO → Re-evaluate requirements
│
END: Select protocol → Follow ESP32 setup guide for your category
```

## Protocol Interoperability Matrix

| From \ To | LoRaMesher | Meshtastic | BATMAN-ADV | Babel | OpenThread | WireGuard |
|-----------|------------|------------|------------|-------|------------|-----------|
| **LoRaMesher** | Native | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Meshtastic** | ❌ | Native | ❌ | ❌ | ❌ | ❌ |
| **BATMAN-ADV** | ❌ | ❌ | Native | ✅ (L3) | ❌ | ✅ (tunnel) |
| **Babel** | ❌ | ❌ | ✅ (L2) | Native | ❌ | ✅ (tunnel) |
| **OpenThread** | ❌ | ❌ | ❌ | ❌ | Native | ✅ (border router) |
| **WireGuard** | ❌ | ❌ | ✅ (tunnel) | ✅ (tunnel) | ✅ (tunnel) | Native |

**Bridging Strategies:**
- **LoRa ↔ IP**: MQTT gateway (Meshtastic), custom bridge (LoRaMesher)
- **Thread ↔ WiFi**: Border Router (NAT64/DNS64/SRP)
- **BLE Mesh ↔ IP**: Proxy node (GATT/ADV)
- **WiFi Mesh ↔ Wired**: Standard Linux bridging (brctl/ip link)

## Academic & Standards References

| Protocol | Key Paper / RFC | Year | DOI/Link |
|----------|-----------------|------|----------|
| LoRaMesher | "Implementation of a LoRa Mesh Library" | 2022 | 10.1109/ACCESS.2022.3217215 |
| LoRaMesher | "Large and reliable data transfer for LoRa mesh" | 2026 | 10.1016/j.comcom.2025.108404 |
| Meshtastic | Meshtastic Protocol Spec | 2024 | github.com/meshtastic/protobufs |
| BATMAN-ADV | "BATMAN-ADV: A Linux Kernel Module" | 2011 | batman-adv.org |
| Babel | RFC 8966 | 2021 | https://datatracker.ietf.org/doc/rfc8966/ |
| OLSR | RFC 3626 | 2003 | https://datatracker.ietf.org/doc/rfc3626/ |
| OLSRv2 | RFC 7181 | 2014 | https://datatracker.ietf.org/doc/rfc7181/ |
| RPL | RFC 6550 | 2012 | https://datatracker.ietf.org/doc/rfc6550/ |
| OpenThread | Thread Specification 1.4 | 2024 | threadgroup.org |
| WireGuard | "WireGuard: Next Generation Kernel Network Tunnel" | 2020 | wireguard.com/papers/ |
| cjdns | "cjdns: Routing in a Cryptographically Authenticated Network" | 2013 | github.com/cjdelisle/cjdns |
| 802.11s | IEEE 802.11s-2011 | 2011 | ieeexplore.ieee.org/document/6005317 |
| BLE Mesh | Bluetooth Mesh Profile 1.0.1 | 2019 | bluetooth.com/specifications/mesh/ |

## Maintenance & Updates

This landscape is updated quarterly. Last update: 2026-11-20.

Sources monitored:
- DeepWiki for each repo (auto-scraped weekly)
- GitHub releases for protocol implementations
- IETF RFC updates
- Thread Group / Bluetooth SIG / LoRa Alliance specs
- Academic publications (IEEE Access, Computer Communications, Ad Hoc Networks)