# Category 1: Low Bandwidth, Lossy, Long Range - Protocol Comparison

## Overview

| Property | LoRaMesher | Meshtastic |
|----------|------------|------------|
| **Architecture** | TDMA + Distance Vector | Flooding + ReliableRouter |
| **Routing Metric** | ETX cost (hop_count × 65536/quality) | Hop count + SNR/RSSI |
| **MAC Layer** | TDMA superframe (scheduled) | CSMA/CA + random backoff |
| **Join Mechanism** | Sponsor-based (NM election) | Flooding discovery |
| **Max Packet Size** | SF-dependent (51-242 bytes) | 240 bytes (configurable) |
| **Encryption** | AES-128-CTR + CMAC | AES-256-CTR + CMAC |
| **Key Management** | PSK / AppKey | PSK / QR code sharing |
| **Gateway Support** | Capability-based discovery | MQTT/TCP gateway |
| **Mobile App** | None (custom) | iOS/Android (official) |
| **Maturity** | v1.0 (2024), academic papers | v2.x (2024), 8.6k★ GitHub |
| **License** | MIT | GPL-3.0 |

## Detailed Comparison

### 1. LoRaMesher (Distance Vector + TDMA)

**Source**: [DeepWiki:LoRaMesher/LoRaMesher] [PROTOCOL_SPEC.md]

#### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    LoRaMesher Stack                         │
├─────────────────────────────────────────────────────────────┤
│  Application Layer (User callbacks)                         │
├─────────────────────────────────────────────────────────────┤
│  Mesh Protocol (Distance Vector + TDMA)                     │
│  ├── Network Service (State machine: 6 states)             │
│  ├── Routing Service (ETX cost, loop prevention)           │
│  ├── Synchronization Service (TDMA superframe)             │
│   │   ├── SYNC_BEACON (multi-hop, 20 bytes)                │
│   │   ├── Slot allocation (CONTROL + DATA slots)           │
│   │   └── Power-aware slot duration                        │
│  └── Radio Service (RadioLib abstraction)                  │
├─────────────────────────────────────────────────────────────┤
│  Radio Hardware (SX1262/SX1276/SX1280 via RadioLib)        │
└─────────────────────────────────────────────────────────────┘
```

#### Key Features

| Feature | Description | Spec Reference |
|---------|-------------|----------------|
| **TDMA Superframe** | Deterministic slots, nodes sleep between slots | §5.1-5.4 |
| **Sponsor-based Join** | Node beyond NM range joins via sponsor | §6.4 |
| **NM Election** | Priority + battery + node count | §5.9 |
| **ETX Cost Metric** | cost = hop_count × 65536 / max(quality,1) | §4.1.3 |
| **Loop Prevention** | Split horizon (next_hop field) + route poisoning | §4.2 |
| **Unidirectional Link Detection** | 3 missed beacons → quality=0 (cost=65535) | §4.3 |
| **Power-aware Slots** | Slot duration = ceil_50(ToA + guard + 50ms) | §5.8 |
| **Capability Discovery** | GATEWAY, SENSOR propagated via next-hop trust | §3.2.3 |

#### State Machine (6 States)

```
[INITIALIZING] → [DISCOVERY] → [JOINING] → [NORMAL_OPERATION]
                     ↓              ↓
                [NETWORK_MANAGER]  [FAULT_RECOVERY] → [DISCOVERY]
                     ↓
                [NM_ELECTION] → [NETWORK_MANAGER]
```

**Timing** (SF7/BW125kHz, 10-slot superframe):
- Discovery timeout: 30s ± 5s jitter
- Superframe duration: ~10s
- Slot duration: ~200ms (SF7) to ~550ms (SF10)
- Join: 1-3 superframes after beacon

#### Message Types (Bit-field: 4-bit category + 4-bit subtype)

| Category | Type | Value | Description |
|----------|------|-------|-------------|
| DATA (0x1x) | DATA | 0x11 | Unicast data |
| | DATA_BROADCAST | 0x12 | TTL flood broadcast |
| CONTROL (0x2x) | ACK | 0x21 | Acknowledgment (reserved) |
| | PING | 0x23 | Ping request |
| | PONG | 0x24 | Ping response |
| ROUTING (0x3x) | HELLO | 0x31 | Neighbor discovery (planned) |
| | ROUTE_TABLE | 0x32 | Distance vector exchange |
| SYSTEM (0x4x) | SYNC | 0x41 | Sync packet |
| | JOIN_REQUEST | 0x42 | Join with sponsor |
| | JOIN_RESPONSE | 0x43 | Response with routing |
| | SLOT_REQUEST | 0x44 | Request slot allocation |
| | SLOT_ALLOCATION | 0x45 | Slot allocation response |
| | SYNC_BEACON | 0x46 | Multi-hop sync (20 bytes) |
| | NM_CLAIM | 0x47 | NM election claim |

#### Routing Table Entry (10 bytes)

```c
struct RoutingTableEntry {
    uint16_t destination;      // Destination address
    uint8_t  hop_count;        // Hops to destination
    uint8_t  link_quality;     // Combined route quality (0-255)
    uint8_t  allocated_data_slots;
    uint8_t  capabilities;     // Node capability bitmap
    uint8_t  control_slot_index; // 0xFF = unassigned
    uint8_t  reception_quality;  // Raw EWMA quality (0-255)
    uint16_t next_hop;         // Next hop for loop prevention
};
```

**Link Quality Calculation** (bidirectional):
```
bottleneck = min(local_quality, remote_quality)
average    = (local_quality + remote_quality) / 2
quality    = (bottleneck * 7 + average * 3) / 10
```
If unidirectional confirmed (3+ missed): quality = 1 (cost = 65535)

#### Configuration Parameters (from PROTOCOL_SPEC.md)

```cpp
// RadioConfig
RadioType::kSx1262 / kSx1276 / kSx1278 / kSx1280
Frequency: 869.9 MHz (EU) / 915 MHz (US)
Spreading Factor: 7-12 (default SF7)
Bandwidth: 125 / 250 / 500 kHz
Coding Rate: 5-8 (4/5 to 4/8)
TX Power: 2-22 dBm
Sync Word: 0x12 (LoRaMesher) / 0x34 (Meshtastic)

// LoRaMeshProtocolConfig
max_packet_size: SF-dependent default (see table)
node_role: AUTO / NODE_ONLY / NETWORK_MANAGER
discovery_timeout_ms: 30000 (default)
route_timeout_ms: 180000 (3 min)
node_timeout_ms: configurable
link_quality_ewma_alpha: 0.30 (default)
```

### 2. Meshtastic (Flooding + ReliableRouter)

**Source**: [DeepWiki:meshtastic/firmware] [GitHub:meshtastic/firmware/src/mesh]

#### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Meshtastic Stack                         │
├─────────────────────────────────────────────────────────────┤
│  Application Modules (Text, Position, Telemetry, etc.)     │
├─────────────────────────────────────────────────────────────┤
│  Mesh Networking Core                                       │
│  ├── MeshService (Packet processing, module dispatch)      │
│  ├── ReliableRouter (Directed unicast with ACK/retry)      │
│  ├── FloodingRouter (Broadcast TTL flood)                  │
│  ├── NextHopRouter (Simple next-hop)                       │
│  ├── Router (Abstract base)                                │
│  ├── PacketHistory (Deduplication, 32-entry cache)         │
│  ├── NodeDB (Node database, persistent)                    │
│  └── Channels (Channel settings, encryption)               │
├─────────────────────────────────────────────────────────────┤
│  Radio Interfaces (RadioLib abstraction)                   │
│  ├── SX1262/SX1268/SX1276/SX1278/SX1280/LR11xx           │
│  └── Hardware abstraction (SPI, GPIO, interrupts)          │
├─────────────────────────────────────────────────────────────┤
│  External Interfaces                                        │
│  ├── Phone API (Bluetooth/NimBLE, WiFi, Serial)            │
│  ├── MQTT Gateway (TCP/TLS)                                │
│   └── Admin Interface (Serial, encrypted)                  │
└─────────────────────────────────────────────────────────────┘
```

#### Key Features

| Feature | Description | Source |
|---------|-------------|--------|
| **Flooding Routing** | TTL-based broadcast, deduplication cache | MeshModule.cpp |
| **ReliableRouter** | Unicast with ACK, retry, route discovery | ReliableRouter.cpp |
| **Channel Encryption** | Per-channel AES-256, PSK or QR sharing | Channels.cpp |
| **MQTT Gateway** | JSON/Protobuf over TLS, topic per channel | MqttClient.cpp |
| **Position Sharing** | Periodic beacon, precision configurable | PositionPrecision.cpp |
| **Telemetry** | Battery, env sensors, device metrics | TelemetryModule.cpp |
| **Canned Messages** | Pre-defined text messages | CannedMessageModule.cpp |

#### Message Format (Protocol Buffers)

```protobuf
// mesh.proto (simplified)
message MeshPacket {
  uint32 id = 1;              // Packet ID
  uint32 from = 2;            // Source node ID
  uint32 to = 3;              // Destination (0 = broadcast)
  uint32 next_hop = 4;        // Next hop (for routing)
  uint32 relay_node = 5;      // Relay node ID
  uint32 hop_limit = 6;       // TTL (default 3)
  uint32 hop_start = 7;       // Original hop limit
  uint32 priority = 8;        // Priority level
  bool   want_ack = 9;        // Request ACK
  bool   want_response = 10;  // Request response
  Data   decoded = 11;        // Decoded payload
  bytes  encrypted = 12;      // Encrypted payload
  uint32 channel = 13;        // Channel index
}

// Data payload types
message Data {
  oneof payload {
    Position position = 1;
    TextMessage text = 2;
    Telemetry telemetry = 3;
    // ... more types
  }
}
```

#### Routing Behavior

**FloodingRouter** (Broadcast):
- TTL default: 3 hops
- Deduplication: PacketHistory (32-entry LRU cache)
- Each node rebroadcasts with TTL-1
- No ACK for broadcasts

**ReliableRouter** (Unicast):
- Route discovery via route request flood
- Route reply establishes path
- ACK with retry (exponential backoff)
- Route timeout: 30 min default
- Max retries: 3

#### Configuration (from firmware)

```cpp
// Key config options (configuration.h / Config.proto)
struct Config {
  // LoRa settings
  struct LoRaConfig {
    uint32 frequency = 906000000;  // Hz
    uint8_t spreading_factor = 7;   // 7-12
    uint8_t bandwidth = 125;        // kHz (125/250/500)
    uint8_t coding_rate = 5;        // 5-8 (4/5 to 4/8)
    int8_t tx_power = 17;           // dBm
    uint16_t sync_word = 0x3444;    // Meshtastic sync
  } lora;

  // Mesh settings
  struct MeshConfig {
    uint8_t hop_limit = 3;          // TTL
    uint32_t route_timeout = 1800;  // seconds
    bool use_mqtt = false;
    // ...
  } mesh;

  // Security
  struct SecurityConfig {
    bytes psk = "";                 // Pre-shared key (AES-256)
    // ...
  } security;
}
```

## Performance Comparison

| Metric | LoRaMesher | Meshtastic |
|--------|------------|------------|
| **Join Time (NM pre-set)** | 10-30s | 30-60s |
| **Join Time (all AUTO)** | 40-60s | 60-120s |
| **Unicast Latency (1 hop)** | ~200ms (slot aligned) | ~500ms (CSMA) |
| **Unicast Latency (3 hops)** | ~600ms | ~2-3s |
| **Broadcast Latency** | N/A (no broadcast) | ~1-2s (TTL=3) |
| **Throughput (SF7)** | ~0.5 kbps sustained | ~0.3 kbps burst |
| **Throughput (SF10)** | ~0.1 kbps | ~0.05 kbps |
| **Battery Life (1 msg/10min)** | ~6 months | ~3 months |
| **Max Nodes (practical)** | 50-100 | 50-100 |
| **Route Convergence** | ~1 superframe (10s) | ~30-60s |
| **Memory (ESP32)** | ~80KB RAM | ~120KB RAM |
| **Flash (ESP32)** | ~500KB | ~1MB |

## When to Choose Which

### Choose **LoRaMesher** if:
- ✅ Deterministic latency required (TDMA)
- ✅ Battery life critical (scheduled sleep)
- ✅ Building custom application (C++ API)
- ✅ Need capability-based discovery (gateway/sensor)
- ✅ Academic/proven algorithm (published papers)
- ✅ MIT license preferred

### Choose **Meshtastic** if:
- ✅ Want mobile app (iOS/Android) out of box
- ✅ Need MQTT/cloud integration
- ✅ Text messaging primary use case
- ✅ Community support important (large user base)
- ✅ GPL-3.0 acceptable
- ✅ Rapid prototyping with Python CLI

### Choose **Both** (Hybrid):
- LoRaMesher for sensor backbone (deterministic)
- Meshtastic for human messaging (app + MQTT)
- Bridge via gateway node with both stacks

## Hardware Compatibility Matrix

| Board | MCU | LoRaMesher | Meshtastic | Notes |
|-------|-----|------------|------------|-------|
| TTGO T-Beam v1.1 | ESP32 | ✅ | ✅ | SX1276, 18650 |
| Heltec WiFi LoRa 32 V3 | ESP32-S3 | ✅ | ✅ | SX1262, TCXO |
| LILYGO T3 S3 v1.x | ESP32-S3 | ✅ | ✅ | SX1278 |
| RAK4631 | nRF52840 | ❌ | ✅ | Meshtastic only |
| M5Stack CoreLoRa | ESP32 | ✅ | ✅ | Prototyping |
| Custom SX1262 | ESP32 | ✅ | ✅ | Best for LoRaMesher |
| Custom SX1276 | ESP32 | ✅ | ✅ | Legacy Meshtastic |

## Regulatory Compliance

| Parameter | LoRaMesher Default | Meshtastic Default | EU 868 MHz | US 915 MHz |
|-----------|-------------------|-------------------|------------|------------|
| Frequency | 869.9 / 915 MHz | 906 / 868 MHz | 868-870 MHz | 902-928 MHz |
| Max EIRP | 14 dBm (config) | 17 dBm (config) | 14 dBm | 30 dBm |
| Duty Cycle | TDMA (controlled) | CSMA (uncontrolled) | 1% / 0.1% | None |
| Sync Word | 0x12 | 0x3444 | N/A | N/A |
| Listen Before Talk | No (TDMA) | No | Recommended | Not required |

**Recommendation**: Configure both for your region. LoRaMesher's TDMA inherently limits duty cycle.

## Migration Path

| From | To | Effort | Notes |
|------|-----|--------|-------|
| Meshtastic 1.x → 2.x | High | Protobuf changes, config migration |
| LoRaMesher 0.x → 1.0 | High | Full rewrite, see MIGRATION.md |
| Meshtastic → LoRaMesher | Medium | Different API, same hardware |
| LoRaMesher → Meshtastic | Medium | Loss of TDMA, gain app/MQTT |

## Testing & Validation

Both protocols support desktop simulation:
- **LoRaMesher**: `pio test -e test_native` (ASAN/UBSAN/TSAN)
- **Meshtastic**: `pio test -e native` (limited)

Field testing checklist:
- [ ] Link budget verification (RSSI/SNR logging)
- [ ] Battery life measurement (1 week minimum)
- [ ] Route convergence timing
- [ ] Multi-hop reliability (3+ hops)
- [ ] NM election/failover
- [ ] Channel collision (multiple networks)

## References

- LoRaMesher: [PROTOCOL_SPEC.md](https://github.com/LoRaMesher/LoRaMesher/blob/main/PROTOCOL_SPEC.md) v1.6
- LoRaMesher: [DeepWiki](https://deepwiki.com/LoRaMesher/LoRaMesher)
- Meshtastic: [DeepWiki](https://deepwiki.com/meshtastic/firmware)
- Meshtastic: [GitHub firmware/src/mesh](https://github.com/meshtastic/firmware/tree/develop/src/mesh)
- IEEE Access 2022: DOI 10.1109/ACCESS.2022.3217215
- Computer Communications 2026: DOI 10.1016/j.comcom.2025.108404