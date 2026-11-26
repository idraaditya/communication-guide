# Category 2: Top Algorithms - Low Bandwidth, Stable

## Executive Summary

For **low bandwidth (250 kbps - 1 Mbps), stable (<1% loss), short range (10-100m)** scenarios, the top-performing algorithms are:

| Rank | Algorithm | Protocol | Key Innovation | Best For |
|------|-----------|----------|----------------|----------|
| **1** | **RPL (RFC 6550) + MLE** | OpenThread/Thread | DODAG + Trickle + DTLS Commissioning | Matter, IPv6, standardization |
| **2** | **AODV + ZCL** | Zigbee 3.0 | On-demand routing + Standard clusters | Legacy interop, Green Power |
| **3** | **Managed Flooding + Friendship** | BLE Mesh | TTL flood + LPN/Friend/Proxy | Phone provisioning, no border router |
| **4** | **CSL (Connected Sleep)** | Thread 1.2+ | Scheduled RX windows for sleepy nodes | Battery-powered Thread devices |
| **5** | **MPLF (MPL Forwarding)** | Thread | Multicast to sleepy nodes | Group communication |

---

## 1. RPL + MLE (OpenThread/Thread)

**Source**: [DeepWiki:openthread/openthread] [RFC 6550] [Thread Spec 1.4]

### Algorithm Overview

Thread combines **RPL (Routing Protocol for LLNs)** for mesh routing with **MLE (Mesh Link Establishment)** for secure neighbor discovery and link management.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Thread Network Stack                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  APPLICATION (Matter, CoAP, UDP, TCP)                          │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 6LoWPAN (RFC 4944/6282) - IPv6 Compression              │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ RPL (RFC 6550) - Distance Vector DODAG                  │   │
│  │ ├── DODAG Root (Border Router)                          │   │
│  │ ├── Objective Function: OF0 (hops) / MRHOF (ETX)       │   │
│  │ ├── Trickle Timer (DIO suppression)                     │   │
│  │ ├── DAO (Destination Advertisement Object)              │   │
│  │ └── DIS (DODAG Information Solicitation)               │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ MLE (Mesh Link Establishment)                           │   │
│  ├── Link Request/Response (neighbor discovery)           │   │
│  ├── Link Accept/Reject (link management)                 │   │
│  ├── Link Accept and Request (bidirectional)              │   │
│  ├── Advertisement (periodic, Trickle)                    │   │
│  ├── Update (parameter change)                            │   │
│  └── Security: AES-CCM, Frame Counter                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  IEEE 802.15.4 MAC (CSMA/CA, AES-CCM, ACK)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Algorithm Components

#### A. RPL DODAG Construction

```c
// DODAG Root (Border Router) initiates
// DIO (DODAG Information Object) broadcast with Trickle timer

struct DIO {
    uint8_t  instance_id;        // RPL Instance
    uint8_t  version;            // DODAG Version
    uint16_t rank;               // Rank of sender
    uint8_t  flags;              // Grounded, DODAG ID present
    uint8_t  dag_id[8];          // DODAG ID (64-bit)
    uint8_t  prefix_info[...];   // IPv6 prefixes
    // ... RPL options
};

// Rank calculation (OF0 - hop count based)
uint16_t CalculateRank(uint16_t parent_rank, uint8_t link_quality) {
    // OF0: Rank increases by MinHopRankIncrease (default 256) per hop
    // MRHOF: Rank = parent_rank + ETX(parent) * MinHopRankIncrease
    return parent_rank + MIN_HOP_RANK_INCREASE;
}

// Trickle Timer (RFC 6206) - suppresses redundant DIOs
void TrickleTimer(uint16_t Imin, uint16_t Imax, uint8_t k) {
    // Imin: minimum interval (log2 ms, default 12 = 4s)
    // Imax: maximum interval doublings (default 20 = 1h)
    // k: redundancy constant (default 1)
    
    // On consistent DIO: double interval (up to Imax)
    // On inconsistent DIO: reset to Imin
    // Transmit at random time in [I/2, I]
}
```

#### B. MLE (Mesh Link Establishment)

```c
// MLE Message Types (Thread Spec §4.12)
enum MLE_Type {
    LINK_REQUEST      = 0,
    LINK_ACCEPT       = 1,
    LINK_ACCEPT_REQ   = 2,
    LINK_REJECT       = 3,
    ADVERTISEMENT     = 4,
    UPDATE            = 5,
    // ... Thread 1.2+
    DATA_REQUEST      = 6,  // For sleepy nodes
    PARENT_REQUEST    = 7,
    PARENT_RESPONSE   = 8,
    CHILD_ID_REQUEST  = 9,
    CHILD_ID_RESPONSE = 10,
};

// Link Request (discovery)
struct LinkRequest {
    uint16_t challenge;           // Random challenge
    uint8_t  version;             // Thread version
    TLV*     tlvs;                // Source Address, Mode, Timeout, etc.
};

// Link Accept (response)
struct LinkAccept {
    uint16_t response;            // Challenge response
    uint8_t  version;
    TLV*     tlvs;                // Link Frame Counter, MLE Frame Counter, etc.
};

// Security: All MLE messages encrypted with AES-CCM
// Key: Link Key (derived from Master Key)
```

#### C. Commissioning (DTLS + PSKc)

```c
// Thread Commissioning (Thread Spec §8)
// 1. Commissioner discovers Border Router (SRP/DNS-SD)
// 2. DTLS session with Border Router (PSKc)
// 3. Commissioner sends MGMT_COMMISSIONER_SET
// 4. Joiner connects via PASE (Thread 1.1) or DTLS (1.2+)
// 5. Network parameters delivered via MGMT_ACTIVE_SET

// PSKc derivation (Thread Spec §8.10.2)
void ComputePSKc(const char* passphrase, const uint8_t* salt, uint16_t iter,
                 uint8_t* pskc) {
    // PBKDF2-HMAC-SHA256(passphrase, salt, iter, 16)
    // salt = "Thread" + Extended PAN ID
    // iter = 10000 (minimum)
}
```

#### D. Border Router Services

```c
// Border Router provides:
// 1. NAT64/DNS64 (RFC 6146/6147) - IPv6 ↔ IPv4 translation
// 2. SRP (Service Registration Protocol) - RFC 8980
// 3. Thread Network Data distribution
// 4. External Route propagation (default route)

struct NetworkData {
    // Stable (Leader managed)
    uint8_t  border_router_config[...];  // Border Router RLOC16, PIO
    uint8_t  external_route[...];        // Prefix + preference
    uint8_t  service_data[...];          // Enterprise services
    uint8_t  leader_data[...];           // Partition ID, weighting
    
    // Temporary (any router)
    uint8_t  prefix[...];                // On-mesh prefixes
    uint8_t  has_route[...];             // Has route to prefix
    uint8_t  router_id[...];             // Router ID assignments
};
```

### Performance Characteristics (Thread 1.4)

| Metric | Value | Conditions |
|--------|-------|------------|
| **Join Time** | 2-10s | DTLS commissioning |
| **Route Convergence** | <5s | Trickle timer, 4s min interval |
| **Max Hops** | 16 | Rank limit (65535 / 256) |
| **Multicast Latency** | <1s | MPL forwarding |
| **Sleepy Node (CSL)** | 100ms-2s latency | Configurable CSL period |
| **Throughput** | ~200 kbps | 250 kbps PHY, overhead |
| **Memory (OpenThread)** | ~60KB RAM, ~400KB Flash | Minimal config |
| **Power (Sleepy)** | ~20 µA avg | CSL 1s, 250kbps |

### OpenThread Implementation (Key Files)

```
openthread/src/
├── core/
│   ├── net/
│   │   ├── rpl/           # RPL implementation
│   │   ├── ip6/           # IPv6 stack
│   │   ├── lowpan/        # 6LoWPAN
│   │   └── nat64/         # NAT64
│   ├── mesh/
│   │   ├── mle/           # Mesh Link Establishment
│   │   ├── routing/       # RPL integration
│   │   └── commissioner/  # Commissioning
│   ├── radio/             # Radio abstraction
│   └── utils/             # Heap, timers, etc.
├── platform/
│   ├── esp32/             # ESP32-H2/C6 platform
│   ├── nrf52840/          # Nordic platform
│   └── posix/             # Linux simulation
└── examples/
    ├── cli/               # OpenThread CLI
    ├── border-router/     # Border router (ot-br-posix)
    └── minimal/           # Minimal end device
```

### OpenThread CLI Commands

```bash
# Network management
dataset init new                    # Create new network dataset
dataset networkname "MyThread"
dataset extpanid 0x1234567890abcdef
dataset panid 0x1234
dataset channel 15
dataset pskc "1a2b3c4d5e6f78901a2b3c4d5e6f7890"
dataset commit active
ifconfig up
thread start

# Commissioner
commissioner start
commissioner joiner add * "J01NME" 180  # PSKd for joiner

# Border Router
srpl enable
nat64 enable
dns64 enable

# Diagnostics
state                              # Node state
router table                       # Router table
child table                        # Child table
neighbor table                     # Neighbor table
route table                        # RPL route table
ping <address>                     # ICMPv6 ping
```

---

## 2. AODV + ZCL (Zigbee 3.0)

**Source**: Zigbee Cluster Library, ESP-Zigbee SDK

### Algorithm Overview

Zigbee uses **AODV (Ad hoc On-Demand Distance Vector)** for mesh routing with **Tree Routing** as fallback, layered with the **Zigbee Cluster Library (ZCL)** for standardized application profiles.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Zigbee Network Stack                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  APPLICATION (ZCL Clusters)                                     │
│  ├── HA: Lighting, Switches, Sensors, Locks, Thermostats       │
│  ├── SE: Smart Energy, Price, DRLC, Metering                   │
│  ├── GP: Green Power (battery-less)                            │
│  └── Touchlink: Commissioning                                   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ APS (Application Support Sublayer)                      │   │
│  ├── APSDE (Data Entity) - Fragmentation, ACK, Retry       │   │
│  ├── APSME (Management Entity) - Binding, Groups           │   │
│  └── Security: AES-128-CCM (Link/Network keys)             │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ NWK (Network Layer)                                     │   │
│  ├── AODV Mesh Routing (RREQ/RREP/RERR)                    │   │
│  ├── Tree Routing (Hierarchical, fallback)                 │   │
│  ├── Address Assignment (Distributed, stochastic)          │   │
│  ├── Route Discovery / Repair / Maintenance                │   │
│  └── Security: AES-128-CCM (Network Key)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  IEEE 802.15.4 MAC (CSMA/CA, Beacon/Non-beacon, GTS)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Algorithm Components

#### A. AODV Route Discovery

```c
// Route Request (RREQ)
struct RREQ {
    uint8_t  flags;              // Gratuitous, Destination only, etc.
    uint8_t  hop_count;          // Current hop count
    uint32_t broadcast_id;       // Unique per originator
    uint16_t dst_addr;           // Destination NWK address
    uint16_t src_addr;           // Originator NWK address
    uint8_t  dst_seq_num;        // Destination sequence number
    uint8_t  src_seq_num;        // Originator sequence number
};

// Route Reply (RREP)
struct RREP {
    uint8_t  flags;              // Acknowledgment required
    uint8_t  hop_count;
    uint16_t dst_addr;
    uint16_t src_addr;
    uint8_t  dst_seq_num;
    uint16_t lifetime;           // Route lifetime (seconds)
};

// Route Error (RERR)
struct RERR {
    uint8_t  dst_count;          // Number of unreachable destinations
    struct {
        uint16_t dst_addr;
        uint8_t  dst_seq_num;
    } destinations[MAX_DEST];
};

// Route Discovery Process:
// 1. Originator broadcasts RREQ (hop_count=0, broadcast_id++)
// 2. Each intermediate node:
//    - Checks if seen this (src_addr, broadcast_id)
//    - Creates reverse route to originator
//    - Increments hop_count, rebroadcasts
// 3. Destination (or node with fresh enough route):
//    - Creates forward route to originator
//    - Unicasts RREP back along reverse route
// 4. Originator receives RREP, confirms route
```

#### B. Tree Routing (Fallback)

```c
// Hierarchical addressing (Zigbee 3.0)
// Coordinator: depth=0, parent=0x0000
// Router: assigned address block by parent
// End Device: address from parent

// Address Assignment (Distributed)
uint16_t AssignAddress(uint16_t parent_addr, uint8_t depth, uint8_t index) {
    // Cskip algorithm (Zigbee Spec §3.6.3)
    // Calculates address block size based on:
    // - Lm: Max depth
    // - Rm: Max children
    // - Cm: Max router children
    // - Cskip(d) = (1 + Cm*(Lm-d-1)) if d < Lm-1, else 1
}

// Tree Routing:
// If destination in my subtree: forward to child
// Else: forward to parent
// No route discovery needed if addresses known
```

#### C. ZCL (Zigbee Cluster Library)

```c
// Key Clusters (Zigbee 3.0)
// General (0x0000-0x000F)
CLUSTER_BASIC              = 0x0000
CLUSTER_POWER_CONFIG       = 0x0001
CLUSTER_DEVICE_TEMP        = 0x0002
CLUSTER_IDENTIFY           = 0x0003
CLUSTER_GROUPS             = 0x0004
CLUSTER_SCENES             = 0x0005
CLUSTER_ON_OFF             = 0x0006
CLUSTER_LEVEL_CONTROL      = 0x0008
CLUSTER_ALARMS             = 0x0009
CLUSTER_TIME               = 0x000A
CLUSTER_OTA                = 0x0019

// Lighting (0x0010-0x001F)
CLUSTER_COLOR_CONTROL      = 0x0300
CLUSTER_BALLAST            = 0x0301

// Measurement (0x0400-0x04FF)
CLUSTER_TEMP_MEAS          = 0x0402
CLUSTER_PRESSURE_MEAS      = 0x0403
CLUSTER_FLOW_MEAS          = 0x0404
CLUSTER_HUMIDITY_MEAS      = 0x0405
CLUSTER_OCCUPANCY          = 0x0406

// Example: On/Off Cluster
struct OnOffCluster {
    // Attributes
    bool onOff;              // 0x0000
    uint8_t globalSceneControl; // 0x4000
    uint16_t onTime;         // 0x4001
    uint16_t offWaitTime;    // 0x4002
    
    // Commands
    void Off() { onOff = false; }
    void On() { onOff = true; }
    void Toggle() { onOff = !onOff; }
    void OnWithTimedOff(uint16_t onTime, uint16_t offWaitTime);
}

// Binding (Source → Destination)
struct BindingEntry {
    uint64_t src_ieee;
    uint8_t  src_endpoint;
    uint16_t cluster_id;
    uint64_t dst_ieee;       // or group address
    uint8_t  dst_endpoint;
};
```

### Performance Characteristics (Zigbee 3.0)

| Metric | Value | Conditions |
|--------|-------|------------|
| **Join Time** | 1-5s | Install code / Touchlink |
| **Route Discovery** | 100ms-2s | RREQ flood, network size |
| **Max Hops** | 15-20 | NWK layer limit |
| **Route Repair** | ~1s | RERR + rediscovery |
| **Throughput** | ~20 kbps app | 250 kbps PHY, APS overhead |
| **Memory** | ~40KB RAM, ~300KB Flash | ZBOSS/Ember stack |
| **Power (End Device)** | ~50 µA avg | Poll interval 100ms |
| **Green Power** | ~0 µA | Energy harvesting switch |

---

## 3. Managed Flooding + Friendship (BLE Mesh)

**Source**: Bluetooth Mesh Spec 1.0.1, ESP-BLE-Mesh

### Algorithm Overview

BLE Mesh uses **Managed Flooding** with **Friendship** for low-power nodes and **Proxy** for phone connectivity.

```
┌─────────────────────────────────────────────────────────────────┐
│                    BLE Mesh Network Stack                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MODELS (Generic, Sensor, Lighting, Vendor)                    │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ACCESS LAYER                                           │   │
│  ├── Addressing: Unicast (16-bit), Group (16-bit), Virtual (128-bit)
│  ├── Message Dispatch, Replay Protection (Seq + IV Index)│   │
│  └── Model Publication / Subscription                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ TRANSPORT LAYER                                        │   │
│  ├── Segmentation & Reassembly (SAR)                     │   │
│  ├── Encryption: AppKey / NetKey / DevKey (AES-CCM)      │   │
│  ├── Friendship (LPN ↔ Friend)                           │   │
│  └── Heartbeat (IV Index, TTL)                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ NETWORK LAYER                                          │   │
│  ├── Managed Flooding (TTL, Seq, Features)               │   │
│  ├── Subnet Management (NetKey per subnet)               │   │
│  ├── IV Update Procedure (96 hours)                      │   │
│  └── Key Refresh (NetKey/AppKey)                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ BEARER LAYER                                           │   │
│  ├── Advertising Bearer (Mesh Message, Mesh Beacon)       │   │
│  ├── GATT Bearer (Proxy, Provisioning PB-GATT)           │   │
│  └── Provisioning Bearer (PB-ADV, PB-GATT)               │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  BLE CONTROLLER (LL) - 2.4 GHz, 1M/2M PHY                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Algorithm Components

#### A. Managed Flooding

```c
// Network PDU (Bluetooth Mesh Spec §3.4)
struct NetworkPDU {
    uint8_t  ivi_nid;        // IV Index (1 bit) + NID (7 bits)
    uint8_t  ctl_ttl;        // CTL (1 bit) + TTL (7 bits)
    uint16_t src;            // Source address (unicast)
    uint16_t dst;            // Destination address
    uint8_t  seq[3];         // Sequence number (24 bits)
    uint8_t  payload[];      // Transport PDU (max 11 bytes)
    uint8_t  mic[4/8];       // MIC (32/64 bits)
};

// Flooding Logic (Spec §3.4.5):
void ProcessNetworkPDU(const NetworkPDU* pdu) {
    // 1. Check replay protection (Seq + IV Index + Source)
    if (IsReplay(pdu->src, pdu->seq, pdu->ivi_nid)) return;
    
    // 2. Check TTL
    if (pdu->ctl_ttl & 0x7F == 0) {
        // TTL=0: deliver locally, don't relay
        DeliverLocally(pdu);
        return;
    }
    
    // 3. Decrement TTL
    NetworkPDU relay = *pdu;
    relay.ctl_ttl = (relay.ctl_ttl & 0x80) | ((relay.ctl_ttl & 0x7F) - 1);
    
    // 4. Relay if Relay feature enabled
    if (HasFeature(FEATURE_RELAY)) {
        Transmit(&relay);
    }
    
    // 5. Deliver locally
    DeliverLocally(pdu);
}

// TTL Guidelines:
// - Unicast: TTL = 2-7 (network diameter)
// - Multicast: TTL = 3-7
// - Known good path: TTL = path_length + 1
```

#### B. Friendship (LPN ↔ Friend)

```c
// Low Power Node (LPN) - Battery powered
// Friend - Mains powered, caches messages

// Friendship Establishment (Spec §3.6)
struct FriendOffer {
    uint8_t  recv_win;           // Receive window (ms)
    uint8_t  queue_size;         // Max messages cached
    uint8_t  sub_list_size;      // Subscription list size
    int8_t   rssi;               // RSSI threshold
};

struct FriendPoll {
    uint8_t  fsn;                // Frame Sequence Number
};

// Friendship State Machine (LPN side):
enum LPN_State {
    LPN_DISABLED,
    LPN_CLEAR,           // Clear previous friendship
    LPN_REQUEST,         // Send Friend Request
    LPN_OFFER,           // Wait for Friend Offer
    LPN_ESTABLISHED,     // Friendship active
    LPN_TERMINATE        // Terminating
};

// Friend Cache Management:
struct FriendCache {
    struct Message {
        NetworkPDU pdu;
        uint32_t   timestamp;
    } queue[MAX_QUEUE_SIZE];
    
    uint16_t subscription_list[MAX_SUB_LIST];
    
    void AddMessage(const NetworkPDU* pdu) {
        if (queue_full) RemoveOldest();
        queue[head++] = {*pdu, now()};
    }
    
    void Poll(uint8_t fsn) {
        // Return messages with seq > fsn
        // Update fsn
    }
};
```

#### C. Provisioning (PB-ADV / PB-GATT)

```c
// Provisioning Protocol (Spec §5)
// 1. Beacon (PB-ADV) / Link Open (PB-GATT)
// 2. Invite / Capabilities
// 3. Start (Algorithm, Public Key, Auth Method)
// 4. Public Key Exchange (ECDH P-256)
// 5. Authentication (Static OOB, Output OOB, Input OOB, None)
// 6. Confirmation (ECDH shared secret)
// 7. Provisioning Data (NetKey, Key Index, Flags, IV Index, Unicast Addr)
// 8. Complete

// PB-ADV (Advertising Bearer):
// - Unprovisioned device broadcasts Mesh Beacon
// - Provisioner scans, sends Link Open via ADV
// - Link established over advertising channels

// PB-GATT (GATT Bearer):
// - Provisioner connects via GATT
// - Uses Mesh Provisioning Service (UUID 0x1827)
// - Data channel: Mesh Provisioning Data In/Out

// Security:
// - ECDH P-256 for key exchange
// - AES-CCM for confirmation/encryption
// - Auth methods: Static OOB, Output OOB (blink/display), Input OOB (push), None
```

### Performance Characteristics (BLE Mesh 1.0.1)

| Metric | Value | Conditions |
|--------|-------|------------|
| **Provisioning Time** | 5-30s | PB-ADV vs PB-GATT, auth method |
| **Message Latency** | 50-500ms | TTL, relay count, network load |
| **Max Nodes** | 32767 | Theoretical (16-bit unicast) |
| **Practical Nodes** | 100-300 | Limited by flooding overhead |
| **Throughput** | ~10-50 kbps | 1M PHY, SAR overhead |
| **Relay Latency** | ~10-50ms/hop | Advertising interval |
| **LPN Poll Interval** | 100ms-4h | Configurable |
| **Friend Cache** | 16-64 messages | Configurable |
| **IV Update** | 96 hours | Automatic |
| **Memory (ESP-BLE-Mesh)** | ~80KB RAM, ~500KB Flash | Full features |

---

## Algorithm Comparison Summary

| Aspect | RPL+MLE (Thread) | AODV+ZCL (Zigbee) | Managed Flood+Friend (BLE Mesh) |
|--------|------------------|-------------------|--------------------------------|
| **Routing Type** | Proactive (DODAG) | Reactive (AODV) + Tree | Flooding (Managed) |
| **Convergence** | Fast (Trickle) | On-demand | N/A (stateless) |
| **Overhead** | Low (periodic DIO) | Route discovery | High (flooding) |
| **Sleepy Support** | CSL (scheduled) | Polling | Friendship (cached) |
| **Multicast** | MPL (efficient) | Groupcast | Group/Virtual addr |
| **Scalability** | 250+ routers | 240 routers | 100-300 practical |
| **Commissioning** | DTLS (standardized) | Install code/Touchlink | PB-ADV/PB-GATT (phone) |
| **IP Connectivity** | Native IPv6 | Gateway needed | Proxy (GATT) needed |
| **Matter Ready** | **Yes** | Bridge | Bridge |
| **License** | BSD-3 | Proprietary/GPL | Apache-2.0 |

---

## Decision Matrix

```
REQUIREMENT                    →  RECOMMENDED
──────────────────────────────────────────────────────
Matter device                  →  OpenThread (Thread)
Native IPv6                    →  OpenThread (Thread)
Existing Zigbee ecosystem      →  Zigbee 3.0
Green Power switches           →  Zigbee 3.0
Phone provisioning (no hub)    →  BLE Mesh
Lighting control (standard)    →  BLE Mesh / Zigbee
ESP32-S3 (no 802.15.4)         →  BLE Mesh
ESP32-H2/C6 available          →  OpenThread (preferred)
Battery, years life            →  Thread (CSL) or BLE Mesh (LPN)
Gateway/Border Router OK       →  OpenThread
No gateway, phone only         →  BLE Mesh
Standardized clusters          →  Zigbee (ZCL)
Open source stack              →  OpenThread (BSD-3)
```

---

## References

- **OpenThread**: https://openthread.io/ | [DeepWiki](https://deepwiki.com/openthread/openthread)
- **Thread Spec 1.4**: https://www.threadgroup.org/
- **RPL**: RFC 6550, RFC 6551, RFC 6552, RFC 6206 (Trickle)
- **6LoWPAN**: RFC 4944, RFC 6282
- **MLE**: Thread Specification §4.12
- **Commissioning**: Thread Specification §8
- **Zigbee 3.0**: https://csa-iot.org/all-solutions/zigbee/
- **AODV**: RFC 3561
- **ZCL**: Zigbee Cluster Library Specification
- **Bluetooth Mesh**: https://www.bluetooth.com/specifications/mesh/
- **Mesh Spec 1.0.1**: Bluetooth SIG
- **ESP-Thread**: https://github.com/espressif/esp-thread
- **ESP-Zigbee**: https://github.com/espressif/esp-zigbee-sdk
- **ESP-BLE-Mesh**: https://github.com/espressif/esp-idf/tree/master/examples/bluetooth/ble_mesh