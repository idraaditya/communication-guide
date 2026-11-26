# Category 4: High Bandwidth, Stable - Protocol Comparison

## Overview

| Property | **WireGuard** | **BIRD2 (OSPF/BGP)** | **cjdns** | **Yggdrasil** |
|----------|---------------|----------------------|-----------|---------------|
| **Type** | L3 VPN (Kernel) | Routing Daemon | Overlay Network | Overlay Network |
| **Layer** | Layer 3 | Layer 3 (Control Plane) | Layer 2.5/3 | Layer 3 |
| **Encryption** | ChaCha20-Poly1305 | None (IPsec separate) | Curve25519/ChaCha20 | Curve25519/ChaCha20 |
| **Authentication** | Noise_IK (1-RTT) | OSPF Auth / BGP TCP-AO | CryptoKey (self-cert) | CryptoKey (self-cert) |
| **Key Management** | Static keys + PSK | Manual / Keychain | Self-certifying | Self-certifying |
| **Routing** | Cryptokey routing | OSPF/BGP/RIP/Babel | DHT + Switch labels | DHT + Tree |
| **IPv6 Support** | Yes (native) | Yes (native) | **Native (only)** | **Native (only)** |
| **NAT Traversal** | Built-in (keepalive) | No (needs STUN/ICE) | Built-in (DHT) | Built-in (DHT) |
| **Roaming** | Seamless (1-RTT) | Protocol-dependent | DHT-based | DHT-based |
| **Performance** | ~1-10 Gbps (kernel) | Control plane only | ~100-500 Mbps | ~100-500 Mbps |
| **Platform** | Linux, Windows, macOS, BSD, ESP32-S3 | Linux (OpenWrt, FRR) | Linux, OpenWrt, macOS, Windows | Linux, OpenWrt, macOS, Windows, iOS, Android |
| **License** | GPL-2.0 | GPL-2.0 | GPL-3.0 | GPL-3.0 |
| **Maturity** | Very high (Linux kernel 5.6+) | Very high (production ISP) | Beta | Beta |

---

## Detailed Comparison

### 1. WireGuard

**Source**: https://www.wireguard.com/ | WireGuard Paper (NDSS 2020)

#### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    WireGuard Stack                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Application (IP packets)                                       │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ wg0 Interface (Virtual)                                 │   │
│  │   ├── IP routing (allowed-ips = cryptokey routing)     │   │
│  │   ├── Keepalive (persistent keepalive for NAT)         │   │
│  │   └── MTU = 1420 (IPv6) / 1440 (IPv4)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ WireGuard Kernel Module / WireGuard-Go                  │   │
│  │   ├── Noise_IK Handshake (1-RTT)                       │   │
│  │   ├── ChaCha20-Poly1305 AEAD Encryption               │   │
│  │   ├── Replay Protection (64-bit counter)              │   │
│  │   ├── Cryptokey Routing Table                          │   │
│  │   │   Peer Public Key → Allowed IPs                    │   │
│  │   │   Destination IP → Peer Public Key                 │   │
│  │   ├── Cookie Reply (DoS protection)                   │   │
│  │   └── Timer Wheels (handshake, keepalive, rekey)      │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  UDP Socket (Port configurable, default 51820)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Core Protocol: Noise_IK Handshake

```c
// Noise_IK Pattern (WireGuard Whitepaper)
// Initiator (I) knows Responder's static public key (rs)
// Responder (R) knows Initiator's static public key (is)

// Message 1 (Initiator → Responder):
//   e (ephemeral public)
//   es (DH(e, rs)) → encrypts initiator static (is) + timestamp
//   Payload: {is, timestamp} encrypted with k = KDF(es)

// Message 2 (Responder → Initiator):
//   e (ephemeral public)
//   ee (DH(e, re)) 
//   se (DH(s, re))
//   Payload: {responder_static, timestamp} encrypted with k

// Message 3 (Initiator → Responder):
//   Payload: {empty} encrypted with k (confirmation)
//   Transport keys derived: TAI, TAR (initiator→responder, responder→initiator)

// Transport Data Packet:
//   counter (64-bit, little-endian)
//   encrypted_payload (ChaCha20-Poly1305)
//   auth_tag (16 bytes)

// Cryptokey Routing Table (per peer):
struct wireguard_peer {
    uint8_t public_key[32];           // Peer static public key
    uint8_t preshared_key[32];        // Optional PSK
    struct {
        uint8_t ip[16];               // Allowed IP (IPv4/IPv6)
        uint8_t cidr;                 // Prefix length
    } allowed_ips[MAX_ALLOWED_IPS];
    uint64_t last_handshake;          // Timestamp
    uint64_t rx_bytes, tx_bytes;      // Statistics
    bool keepalive_enabled;
    uint16_t keepalive_interval;      // Seconds (0 = disabled)
    struct sockaddr endpoint;         // Learned endpoint (UDP/IP)
};
```

#### Configuration

```bash
# Linux (wg-quick)
# /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <base64_private_key>
Address = 10.0.0.1/24, fd00:1::1/64
ListenPort = 51820
MTU = 1420

# Peer 1 (Site B)
[Peer]
PublicKey = <base64_public_key>
AllowedIPs = 10.0.0.2/32, fd00:1::2/128, 192.168.2.0/24
Endpoint = site-b.example.com:51820
PersistentKeepalive = 25

# Peer 2 (Road Warrior)
[Peer]
PublicKey = <base64_public_key>
AllowedIPs = 10.0.0.10/32, fd00:1::10/128
PersistentKeepalive = 25

# Start
wg-quick up wg0

# Monitor
wg show
wg show wg0 transfer
wg show wg0 endpoints
```

#### ESP32-S3 Configuration

```c
// ESP-IDF: WireGuard-Go or native port
// Recommended: WireGuard-Go (userspace, easier)

// 1. Build WireGuard-Go for ESP32-S3
git clone https://github.com/wireguard/wireguard-go
cd wireguard-go
GOOS=linux GOARCH=xtensa GOXTENSA=esp32s3 go build -ldflags="-s -w"

// 2. Cross-compile for ESP32-S3 (requires ESP-IDF toolchain)
// Use ESP-IDF component wrapper

// 3. Native ESP32 port (experimental)
// https://github.com/espressif/esp-idf/tree/master/examples/protocols/wireguard

// Configuration (wireguard-go config)
config := &wireguard.Config{
    PrivateKey: privateKey,
    ListenPort: 51820,
    Peers: []wireguard.PeerConfig{
        {
            PublicKey: peerPublicKey,
            AllowedIPs: []net.IPNet{
                {IP: net.ParseIP("10.0.0.0").To4(), Mask: net.CIDRMask(24, 32)},
            },
            Endpoint: &net.UDPAddr{IP: net.ParseIP("1.2.3.4"), Port: 51820},
            PersistentKeepalive: 25 * time.Second,
        },
    },
    ReplaceAllowedIPs: true,
}

// 4. Run as userspace process on ESP32-S3
// Requires: LwIP raw socket support, sufficient RAM (512KB+)
```

#### Performance

| Metric | Value |
|--------|-------|
| **Throughput (Linux kernel)** | 1-10 Gbps (AES-NI/ChaCha20) |
| **Throughput (WireGuard-Go)** | 100-500 Mbps |
| **Latency (handshake)** | 1-RTT (~50-200ms) |
| **Rekey interval** | 2 minutes (configurable) |
| **Keepalive** | 10-60s (NAT traversal) |
| **MTU** | 1420 (IPv6) / 1440 (IPv4) |
| **RAM (WireGuard-Go)** | ~2-5 MB |
| **Flash** | ~2-3 MB |

### 2. BIRD2 (OSPF/BGP/RIP/Babel)

**Source**: https://bird.network.cz/ | OpenWrt BIRD2 package

#### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    BIRD2 Architecture                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BIRD2 Daemon (User Space)                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Protocol Modules                                         │   │
│  │   ├── OSPF (RFC 2328/5340) - Link State                  │   │
│  │   │   ├── SPF (Dijkstra)                                 │   │
│  │   │   ├── LSA Flooding                                   │   │
│  │   │   ├── Areas / Virtual Links                          │   │
│  │   │   └── Authentication (Simple/MD5/SHA)                │   │
│  │   ├── BGP (RFC 4271) - Path Vector                       │   │
│  │   │   ├── AS_PATH, Communities, MED                      │   │
│  │   │   ├── Route Reflection / Confederations              │   │
│  │   │   └── TCP-AO / MD5 Authentication                    │   │
│  │   ├── Babel (RFC 8966) - Distance Vector                 │   │
│  │   ├── RIP (RFC 2453) - Distance Vector                   │   │
│  │   ├── Static Routes                                       │   │
│  │   ├── Kernel (netlink) - Route Installation              │   │
│  │   ├── Device - Interface Monitoring                      │   │
│  │   └── Pipe - Inter-table Communication                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Filtering Engine                                         │   │
│  │   ├── Import Filters (per protocol)                     │   │
│  │   ├── Export Filters (per protocol)                     │   │
│  │   ├── Route Attributes (pref, metric, community, etc.)  │   │
│  │   └── Route Maps / Prefix Lists                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  Routing Tables (Multiple)                                      │
│  ├── master (IPv4)                                             │
│  ├── master6 (IPv6)                                            │
│  └── Custom tables                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### OSPF Configuration

```bird
# /etc/bird/bird.conf
router id 192.168.1.1;

protocol device {
    scan time 10;
}

protocol kernel {
    ipv4 {
        export all;
        import none;
    };
}

protocol static {
    ipv4;
    route 10.0.0.0/24 via 192.168.1.2;
    route 192.168.2.0/24 via 192.168.1.3;
}

protocol ospf v2 {
    ipv4 {
        import filter {
            # Accept only specific prefixes
            if net ~ [ 10.0.0.0/8+, 192.168.0.0/16+ ] then accept;
            reject;
        };
        export filter {
            if source = RTS_STATIC then accept;
            reject;
        };
    };
    
    area 0.0.0.0 {
        interface "eth0" {
            cost 10;
            type broadcast;
            hello 10;
            dead 40;
            retransmit 5;
            priority 1;
            authentication none;  # or simple "password" / md5 "keyid" "key"
        };
        
        interface "wlan0" {
            cost 100;
            type broadcast;
            hello 10;
            dead 40;
        };
        
        # Stub area for remote sites
        stub yes;
    };
}

# IPv6 OSPFv3
protocol ospf v3 {
    ipv6 {
        import filter {
            if net ~ [ fd00::/8+ ] then accept;
            reject;
        };
        export all;
    };
    
    area 0.0.0.0 {
        interface "eth0" {
            cost 10;
        };
        interface "wlan0" {
            cost 100;
        };
    };
}

# Logging
log "/var/log/bird.log" all;
log syslog all;
```

#### BGP Configuration

```bird
protocol bgp {
    local as 65001;
    neighbor 192.168.1.2 as 65002;
    
    ipv4 {
        import filter {
            # Accept customer routes
            if (source = RTS_BGP) && (net ~ [ 10.0.0.0/8+ ]) then {
                bgp_community.add((65001, 100));
                accept;
            }
            reject;
        };
        export filter {
            if source = RTS_STATIC then accept;
            if source = RTS_OSPF then {
                bgp_community.add((65001, 200));
                accept;
            }
            reject;
        };
    };
    
    # Authentication
    password "bgp-secret";
    # Or TCP-AO
    # tcp_ao "keyid" "key";
    
    # Graceful restart
    graceful_restart on;
    graceful_restart_time 120;
}
```

#### BIRD2 CLI

```bash
# Start
bird -c /etc/bird/bird.conf
birdc  # CLI

# CLI Commands
birdc> show protocols
birdc> show route
birdc> show route for 10.0.0.5
birdc> show route table master
birdc> show ospf topology
birdc> show ospf neighbors
birdc> show ospf lsadb
birdc> show bgp summary
birdc> show bgp neighbors
birdc> show bgp routes
birdc> configure
birdc> disable ospf
birdc> enable ospf
birdc> reload
birdc> debug all
birdc> debug { events, states, packets } on
```

### 3. cjdns (Caleb James DeLisle Network Suite)

**Source**: https://github.com/cjdelisle/cjdns

#### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    cjdns Architecture                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Application (IPv6)                                             │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ cjdns Daemon (User Space)                               │   │
│  │   ├── CryptoAuth (Curve25519 + ChaCha20-Poly1305)      │   │
│  │   ├── DHT (Kademlia-like) for Key/Node Discovery       │   │
│  │   ├── Switch Labels (Source Routing)                    │   │
│  │   │   ├── Label Switching (MPLS-like)                  │   │
│  │   │   ├── Path Discovery (BFS with pruning)            │   │
│  │   │   └── Link Quality Metric (latency/loss)           │   │
│  │   ├── Router Module (IPv6 forwarding)                  │   │
│  │   ├── Switch Module (Label forwarding)                 │   │
│  │   ├── TUN Interface (cjdns0)                           │   │
│  │   ├── Peer Connections (UDP/TCP/TLS)                   │   │
│  │   └── Admin API (JSON-RPC over UNIX socket)            │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  IPv6 Network (fc00::/8 - ULA)                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Concepts

| Concept | Description |
|---------|-------------|
| **CryptoKey** | Public key = IPv6 address (fc00::/8 + hash of pubkey) |
| **DHT** | Kademlia-style for node/key discovery |
| **Switch Labels** | Source routing with 32-bit labels (MPLS-like) |
| **Path Discovery** | BFS with pruning, link quality metric |
| **Peer Protocol** | UDP (default), TCP, TLS, WebSocket |
| **Admin API** | JSON-RPC over UNIX socket |

#### Configuration

```bash
# Install
git clone https://github.com/cjdelisle/cjdns
cd cjdns
./do
# Or package manager: opkg install cjdns (OpenWrt)

# Generate config
./cjdroute --genconf > cjdroute.conf

# Edit cjdroute.conf
{
  "ipv6": "fc00:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx/8",
  "publicKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxx",
  "privateKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  
  "authorizedPasswords": [
    {"password": "unique-password-for-peer-1", "peerName": "peer1"},
    {"password": "unique-password-for-peer-2", "peerName": "peer2"}
  ],
  
  "interfaces": {
    "udp": {
      "bind": "0.0.0.0:53123",
      "connect": [
        "peer1.example.com:53123",
        "peer2.example.com:53123"
      ]
    }
  },
  
  "router": {
    "maxConnections": 100,
    "maxPendingConnections": 10
  },
  
  "security": {
    "noIncomingConnections": false
  }
}

# Start
./cjdroute < cjdroute.conf

# Admin
echo '{"cmd":"ping","target":"fc00:...}"}' | socat - UNIX-CONNECT:/var/run/cjdns.sock
echo '{"cmd":"dumpTable"}' | socat - UNIX-CONNECT:/var/run/cjdns.sock
echo '{"cmd":"peerStats"}' | socat - UNIX-CONNECT:/var/run/cjdns.sock
```

### 4. Yggdrasil

**Source**: https://github.com/yggdrasil-network/yggdrasil

#### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Yggdrasil Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Application (IPv6)                                             │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Yggdrasil Daemon (User Space)                           │   │
│  │   ├── DHT (Kademlia) for Node Discovery                │   │
│  │   ├── Tree Routing (Spanning Tree + Shortcuts)         │   │
│  │   │   ├── Root Selection (stable nodes)                │   │
│  │   │   ├── Parent/Child Relationships                   │   │
│  │   │   └── Shortcut Edges (low-latency paths)           │   │
│  │   ├── Crypto (Curve25519 + ChaCha20-Poly1305)          │   │
│  │   ├── TUN Interface (ygg0)                             │   │
│  │   ├── Peer Connections (TCP/TLS/QUIC/WebSocket)        │   │
│  │   └── Admin API (HTTP/JSON)                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  IPv6 Network (200::/7 - ULA)                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Concepts

| Concept | Description |
|---------|-------------|
| **Address** | 200::/7 + Curve25519 public key hash |
| **Tree Routing** | Spanning tree with root selection |
| **Shortcuts** | Direct links bypassing tree |
| **DHT** | Kademlia for node discovery |
| **Peering** | TCP, TLS, QUIC, WebSocket |
| **Admin** | HTTP/JSON API |

#### Configuration

```yaml
# /etc/yggdrasil.conf
# Network
NodeName: "my-node"
Peers:
  - "tcp://peer1.example.com:12345"
  - "tls://peer2.example.com:12345"
  - "quic://peer3.example.com:12345"

# Listen
Listen:
  - "tcp://0.0.0.0:12345"
  - "tls://0.0.0.0:12345"
  - "quic://0.0.0.0:12345"

# Tree routing
Tree:
  Enabled: true
  RootSelection: "stable"  # or "manual"
  # Manual root: Root: "200:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx"

# DHT
DHT:
  Enabled: true
  Port: 12345

# Admin API
Admin:
  Listen: "127.0.0.1:9001"
  # API: http://127.0.0.1:9001

# Logging
LogLevel: "info"
LogFile: "/var/log/yggdrasil.log"

# Start
yggdrasil -useconffile /etc/yggdrasil.conf

# Admin API
curl http://127.0.0.1:9001/peers
curl http://127.0.0.1:9001/nodes
curl http://127.0.0.1:9001/dht
curl http://127.0.0.1:9001/routing
```

---

## Comparison Matrix

| Aspect | WireGuard | BIRD2 | cjdns | Yggdrasil |
|--------|-----------|-------|-------|-----------|
| **Primary Use** | Site-to-site VPN, Road warrior | ISP/Enterprise routing | Encrypted overlay | Encrypted overlay |
| **Encryption** | ChaCha20-Poly1305 | None (IPsec) | Curve25519/ChaCha20 | Curve25519/ChaCha20 |
| **Key Mgmt** | Static + PSK | Manual/Keychain | Self-certifying | Self-certifying |
| **Routing** | Cryptokey (static) | OSPF/BGP/Babel/RIP | DHT + Switch labels | DHT + Tree |
| **IPv6** | Yes | Yes | **Native only** | **Native only** |
| **NAT Traversal** | Built-in | No | Built-in | Built-in |
| **Roaming** | Seamless | Protocol-dependent | DHT-based | DHT-based |
| **Performance** | 1-10 Gbps (kernel) | Control plane | ~100-500 Mbps | ~100-500 Mbps |
| **Platform** | All (kernel/userspace) | Linux/OpenWrt | Linux/OpenWrt | All |
| **Config Complexity** | Low | High | Medium | Low |
| **Audit/Formal Verif** | Yes (Noise) | No | No | No |

---

## When to Choose Which

### Choose **WireGuard** if:
- ✅ **Site-to-site VPN** or **road warrior** access
- ✅ **Simple configuration** (static keys, allowed-ips)
- ✅ **High performance** (kernel, 1-10 Gbps)
- ✅ **NAT traversal** built-in (keepalive)
- ✅ **Seamless roaming** (1-RTT handshake)
- ✅ Running on **ESP32-S3** (WireGuard-Go) or Linux
- ✅ Need **IPv4 + IPv6** dual-stack

### Choose **BIRD2** if:
- ✅ **Production routing** (OSPF/BGP)
- ✅ **Multi-homed** networks, route redistribution
- ✅ **Policy-based routing** (filters, communities)
- ✅ **ISP/Enterprise** grade
- ✅ Running on **Linux/OpenWrt** (not ESP32)
- ✅ Need **BGP** for internet routing

### Choose **cjdns** if:
- ✅ **Encrypted overlay** without PKI
- ✅ **Self-certifying** addresses (pubkey = address)
- ✅ **DHT-based** discovery
- ✅ **Switch labels** for source routing
- ✅ Running on **Linux/OpenWrt** (not ESP32)
- ✅ Experimental/beta acceptable

### Choose **Yggdrasil** if:
- ✅ **Encrypted overlay** with simpler config
- ✅ **Tree + shortcut** routing
- ✅ **Cross-platform** (Windows, macOS, iOS, Android)
- ✅ **HTTP admin API**
- ✅ Running on **any platform** including mobile
- ✅ Beta acceptable

---

## Hybrid Deployments

```
┌─────────────────────────────────────────────────────────────────┐
│                    HYBRID ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   SITE A (HQ)                              SITE B (BRANCH)     │
│   ┌─────────────────┐                      ┌─────────────────┐ │
│   │ BIRD2 (OSPF)    │◄────── WireGuard ────►│ BIRD2 (OSPF)    │ │
│   │ 10.0.0.0/8      │   Tunnel             │ 10.1.0.0/16     │ │
│   └────────┬────────┘                      └────────┬────────┘ │
│            │                                        │          │
│            ▼                                        ▼          │
│   ┌─────────────────┐                      ┌─────────────────┐ │
│   │ WireGuard Mesh  │◄─────────────────────►│ WireGuard Mesh  │ │
│   │ (Road Warriors) │   Encrypted IPv4/IPv6 │ (Road Warriors) │ │
│   └─────────────────┘                      └─────────────────┘ │
│                                                                 │
│   OVERLAY (Optional):                                           │
│   ┌─────────────────┐                      ┌─────────────────┐ │
│   │ Yggdrasil/cjdns │◄────────────────────►│ Yggdrasil/cjdns │ │
│   │ (Encrypted IPv6)│   Over WireGuard    │ (Encrypted IPv6) │ │
│   └─────────────────┘                      └─────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ESP32-S3 Specific: WireGuard

```c
// ESP-IDF WireGuard Example (WireGuard-Go)
// Requires: ESP32-S3 with 512KB+ RAM, ESP-IDF 5.2+

// 1. Build WireGuard-Go for ESP32-S3
// GOOS=linux GOARCH=xtensa GOXTENSA=esp32s3 CGO_ENABLED=0 go build

// 2. ESP-IDF Component (wg_esp32)
idf_component_register(
    SRCS "wg_esp32.c"
    INCLUDE_DIRS "."
    REQUIRES esp_netif lwip mbedtls
)

// 3. Initialize
esp_err_t wg_esp32_init(wg_config_t* config) {
    // Create TUN interface
    // Initialize WireGuard-Go
    // Set up peer configs
    // Start event loop
}

// 4. Configuration
wg_config_t config = {
    .private_key = "...",  // Base64
    .listen_port = 51820,
    .peers = {
        {
            .public_key = "...",
            .allowed_ips = {"10.0.0.0/24"},
            .endpoint = "1.2.3.4:51820",
            .keepalive = 25,
        }
    }
};

// 5. Monitor
wg_esp32_stats_t stats;
wg_esp32_get_stats(&stats);
// stats.rx_bytes, stats.tx_bytes, stats.last_handshake
```

---

## Resources

- **WireGuard**: https://www.wireguard.com/ | https://www.wireguard.com/papers/
- **BIRD2**: https://bird.network.cz/ | https://github.com/bird-net/bird
- **cjdns**: https://github.com/cjdelisle/cjdns
- **Yggdrasil**: https://github.com/yggdrasil-network/yggdrasil
- **OpenWrt BIRD2**: https://openwrt.org/docs/guide-user/network/bird
- **WireGuard on ESP32**: https://github.com/espressif/esp-idf/tree/master/examples/protocols/wireguard
- **WireGuard-Go**: https://github.com/wireguard/wireguard-go