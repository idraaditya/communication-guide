# cjdns & Yggdrasil on Linux - Encrypted Overlay Networks

## Overview

Both cjdns and Yggdrasil are **encrypted IPv6 overlay networks** that provide:
- **End-to-end encryption** (Curve25519 + ChaCha20-Poly1305)
- **Self-certifying addresses** (public key = address)
- **Decentralized** - no central authority
- **NAT traversal** built-in
- **Cross-platform** (Linux, macOS, Windows, OpenWrt)

---

## cjdns

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         cjdns Architecture                      │
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
│  │   ├── TUN Interface (tun0)                             │   │
│  │   ├── Peer Connections (UDP/TCP/TLS/WebSocket)         │   │
│  │   └── Admin API (JSON-RPC over UNIX socket)            │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  IPv6 Network (fc00::/8 - ULA)                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **CryptoKey** | Public key = IPv6 address (fc00::/8 + hash of pubkey) |
| **DHT** | Kademlia-style for key/node discovery |
| **Switch Labels** | Source routing with 32-bit labels (MPLS-like) |
| **Path Discovery** | BFS with pruning, link quality metric |
| **Peer Protocol** | UDP (default), TCP, TLS, WebSocket |

---

## cjdns Installation

### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update
sudo apt install git build-essential cmake nodejs npm libuv1-dev libssl-dev

# Clone and build
git clone https://github.com/cjdelisle/cjdns
cd cjdns
./do

# Or install via package manager (older version)
sudo apt install cjdns
```

### OpenWrt

```bash
opkg update
opkg install cjdns

# Configure
# /etc/config/cjdns
```

### macOS

```bash
brew install cjdns
```

### Windows

```bash
# Use WSL2 or compile with MSYS2
# Or use pre-built binaries from releases
```

---

## cjdns Configuration

### 1. Generate Configuration

```bash
./cjdroute --genconf > cjdroute.conf
```

### 2. Edit Configuration

```json
{
  // Your IPv6 address (auto-generated from public key)
  "ipv6": "fc00:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx/8",
  
  // Public key (auto-generated)
  "publicKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxx",
  
  // Private key (KEEP SECRET!)
  "privateKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  
  // Authorized peers (password-based peering)
  "authorizedPasswords": [
    {"password": "unique-password-for-peer-1", "peerName": "peer1"},
    {"password": "unique-password-for-peer-2", "peerName": "peer2"}
  ],
  
  // Network interfaces
  "interfaces": {
    "udp": {
      "bind": "0.0.0.0:53123",
      "connect": [
        "peer1.example.com:53123",
        "peer2.example.com:53123"
      ]
    },
    "tcp": {
      "bind": "0.0.0.0:53124",
      "connect": [
        "peer1.example.com:53124"
      ]
    }
  },
  
  // Router settings
  "router": {
    "maxConnections": 100,
    "maxPendingConnections": 10
  },
  
  // Security
  "security": {
    "noIncomingConnections": false
  }
}
```

### 3. Start cjdns

```bash
# Foreground
./cjdroute < cjdroute.conf

# Background (systemd)
sudo systemctl start cjdns
sudo systemctl enable cjdns

# Check status
./cjdroute --status
```

---

## cjdns Administration

### Admin API (UNIX Socket)

```bash
# Default socket: /var/run/cjdns.sock
# Or configure in config: "admin": {"bind": "127.0.0.1:11234"}

# Ping a node
echo '{"cmd":"ping","target":"fc00:..."}' | socat - UNIX-CONNECT:/var/run/cjdns.sock

# Dump routing table
echo '{"cmd":"dumpTable"}' | socat - UNIX-CONNECT:/var/run/cjdns.sock

# Peer statistics
echo '{"cmd":"peerStats"}' | socat - UNIX-CONNECT:/var/run/cjdns.sock

# Dump DHT
echo '{"cmd":"dumpDHT"}' | socat - UNIX-CONNECT:/var/run/cjdns.sock

# Add peer dynamically
echo '{"cmd":"addPeer","password":"peer-password","peerName":"new-peer"}' | socat - UNIX-CONNECT:/var/run/cjdns.sock

# Remove peer
echo '{"cmd":"removePeer","publicKey":"..."}' | socat - UNIX-CONNECT:/var/run/cjdns.sock
```

### JSON-RPC Examples

```bash
# Using curl (if HTTP admin enabled)
curl -X POST http://127.0.0.1:11234 \
  -H "Content-Type: application/json" \
  -d '{"cmd":"ping","target":"fc00:..."}'

# Python script for automation
#!/usr/bin/env python3
import socket, json, sys

def cjdns_rpc(cmd, **params):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect("/var/run/cjdns.sock")
    request = {"cmd": cmd, **params}
    sock.send(json.dumps(request).encode() + b'\n')
    response = sock.recv(65536).decode()
    sock.close()
    return json.loads(response)

# Usage
print(cjdns_rpc("ping", target="fc00:..."))
print(cjdns_rpc("dumpTable"))
print(cjdns_rpc("peerStats"))
```

---

## cjdns Peering

### Password-Based Peering

```bash
# On Node A: Generate password
# Share with Node B securely

# Node B config:
"authorizedPasswords": [
    {"password": "shared-secret-password", "peerName": "node-a"}
]

# Node B connects to Node A:
"interfaces": {
    "udp": {
        "connect": ["node-a.example.com:53123"]
    }
}
```

### Static Peer Configuration

```json
"interfaces": {
    "udp": {
      "bind": "0.0.0.0:53123",
      "connect": [
        "peer1.example.com:53123",
        "peer2.example.com:53123"
      ]
    },
    "tcp": {
      "bind": "0.0.0.0:53124",
      "connect": [
        "peer1.example.com:53124"
      ]
    },
    "tls": {
      "bind": "0.0.0.0:53125",
      "connect": [
        "peer1.example.com:53125"
      ]
    }
}
```

### Peer Discovery (DHT)

```json
"router": {
  "maxConnections": 100,
  "maxPendingConnections": 10,
  "dht": {
    "enabled": true,
    "bootstrap": [
      "fc00:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx"
    ]
  }
}
```

---

## Yggdrasil

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Yggdrasil Architecture                     │
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

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Address** | 200::/7 + Curve25519 public key hash |
| **Tree Routing** | Spanning tree with root selection |
| **Shortcuts** | Direct links bypassing tree |
| **DHT** | Kademlia for node discovery |
| **Peering** | TCP, TLS, QUIC, WebSocket |
| **Admin** | HTTP/JSON API |

---

## Yggdrasil Installation

### Linux

```bash
# Install from package
sudo apt install yggdrasil

# Or build from source
git clone https://github.com/yggdrasil-network/yggdrasil
cd yggdrasil
./build

# Install
sudo cp ./yggdrasil /usr/local/bin/
sudo cp ./yggdrasilctl /usr/local/bin/
```

### OpenWrt

```bash
opkg update
opkg install yggdrasil
```

### macOS

```bash
brew install yggdrasil
```

### Windows

```bash
# Download from GitHub releases
# Or use scoop: scoop install yggdrasil
```

---

## Yggdrasil Configuration

### 1. Generate Config

```bash
yggdrasil -genconf > yggdrasil.conf
```

### 2. Edit Configuration

```yaml
# /etc/yggdrasil.conf

# Network
NodeName: "my-node"

# Peers (replace with actual peers)
Peers:
  - "tcp://peer1.example.com:12345"
  - "tls://peer2.example.com:12345"
  - "quic://peer3.example.com:12345"

# Listen addresses
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
```

### 3. Start Yggdrasil

```bash
# Foreground
yggdrasil -useconffile yggdrasil.conf

# Background (systemd)
sudo systemctl start yggdrasil
sudo systemctl enable yggdrasil

# Check status
yggdrasilctl getPeers
yggdrasilctl getNodes
yggdrasilctl getSelf
```

---

## Yggdrasil Administration

### Admin API (HTTP/JSON)

```bash
# Peers
curl http://127.0.0.1:9001/peers

# Nodes
curl http://127.0.0.1:9001/nodes

# DHT
curl http://127.0.0.1:9001/dht

# Routing table
curl http://127.0.0.1:9001/routing

# Self info
curl http://127.0.0.1:9001/self

# Add peer dynamically
curl -X POST http://127.0.0.1:9001/peers \
  -H "Content-Type: application/json" \
  -d '{"peer": "tcp://newnode.example.com:12345"}'

# Remove peer
curl -X DELETE http://127.0.0.1:9001/peers/peer-id
```

### CLI Tool

```bash
# Get peers
yggdrasilctl getPeers

# Get nodes
yggdrasilctl getNodes

# Get self info
yggdrasilctl getSelf

# Ping node
yggdrasilctl ping 200:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx

# Traceroute
yggdrasilctl trace 200:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx

# Dump DHT
yggdrasilctl dumpDHT
```

---

## Yggdrasil Peering

### Static Peers

```yaml
Peers:
  - "tcp://peer1.example.com:12345"
  - "tls://peer2.example.com:12345"
  - "quic://peer3.example.com:12345"
  - "ws://peer4.example.com:12345"
  - "wss://peer5.example.com:12345"
```

### Peer Types

| Protocol | Use Case |
|----------|----------|
| `tcp://` | Basic, no encryption |
| `tls://` | TLS encrypted (recommended) |
| `quic://` | QUIC (low latency, multiplexed) |
| `ws://` | WebSocket (firewall traversal) |
| `wss://` | Secure WebSocket |

### Dynamic Peering

```bash
# Add peer via API
curl -X POST http://127.0.0.1:9001/peers \
  -H "Content-Type: application/json" \
  -d '{"peer": "tls://newnode.example.com:12345"}'

# Remove peer
curl -X DELETE http://127.0.0.1:9001/peers/peer-id
```

---

## Yggdrasil Tree Routing

### Root Selection

```yaml
Tree:
  Enabled: true
  RootSelection: "stable"  # or "manual"
  # Manual: Root: "200:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx"
```

### Shortcuts

```yaml
Tree:
  Enabled: true
  # Shortcuts automatically created for low-latency paths
  # No manual configuration needed
```

---

## Comparison: cjdns vs Yggdrasil

| Feature | cjdns | Yggdrasil |
|---------|-------|-----------|
| **Address Space** | fc00::/8 | 200::/7 |
| **Routing** | DHT + Switch Labels | DHT + Tree + Shortcuts |
| **Admin API** | JSON-RPC (UNIX socket) | HTTP/JSON |
| **Peering** | Password + DHT | Static + Dynamic |
| **Transports** | UDP, TCP, TLS, WebSocket | TCP, TLS, QUIC, WebSocket |
| **Maturity** | Older, more tested | Newer, active development |
| **Cross-platform** | Linux, macOS, Windows | Linux, macOS, Windows, OpenWrt, iOS, Android |
| **License** | GPL-3.0 | GPL-3.0 |

---

## Hybrid Deployment

### cjdns + Yggdrasil

```bash
# Run both on same node
# Different TUN interfaces: tun0 (cjdns), ygg0 (Yggdrasil)
# Different address spaces: fc00::/8 and 200::/7

# Route between them via Linux kernel
ip route add fc00::/8 dev tun0
ip route add 200::/7 dev ygg0
```

### Integration with WireGuard

```bash
# Overlay over WireGuard for additional security
# WireGuard provides L3 tunnel
# cjdns/Yggdrasil runs inside tunnel

# WireGuard config
[Interface]
PrivateKey = ...
Address = 10.0.0.1/24

[Peer]
PublicKey = ...
AllowedIPs = 10.0.0.0/24
Endpoint = peer.example.com:51820

# cjdns/Yggdrasil binds to WireGuard interface
# cjdns.conf:
"interfaces": {
  "udp": {
    "bind": "10.0.0.1:53123",
    "connect": ["10.0.0.2:53123"]
  }
}
```

---

## Monitoring & Metrics

### cjdns

```bash
# Health check
./cjdroute --status

# Metrics via admin API
echo '{"cmd":"peerStats"}' | socat - UNIX-CONNECT:/var/run/cjdns.sock

# Prometheus exporter (community)
# https://github.com/cjdelisle/cjdns-exporter
```

### Yggdrasil

```bash
# Health check
yggdrasilctl getSelf

# Metrics via admin API
curl http://127.0.0.1:9001/peers
curl http://127.0.0.1:9001/nodes

# Prometheus exporter
# https://github.com/yggdrasil-network/yggdrasil-exporter
```

---

## Troubleshooting

### cjdns

| Issue | Fix |
|-------|-----|
| Can't connect to peers | Check firewall (UDP 53123), verify passwords |
| High latency | Check DHT, add more peers, check link quality |
| No routes | Check DHT bootstrap, add manual peers |
| High CPU | Reduce max connections, check for loops |

```bash
# Debug
./cjdroute --debug < cjdroute.conf

# Logs
journalctl -u cjdns -f

# Admin API debug
echo '{"cmd":"dumpDHT"}' | socat - UNIX-CONNECT:/var/run/cjdns.sock
```

### Yggdrasil

| Issue | Fix |
|-------|-----|
| Can't connect | Check firewall (TCP 12345), verify peer configs |
| No routes | Check tree root, add more peers |
| High latency | Enable shortcuts, add more peers |
| Disconnections | Check TLS certs, increase timeouts |

```bash
# Debug
yggdrasil -useconffile yggdrasil.conf -logLevel debug

# Logs
journalctl -u yggdrasil -f

# Admin API
curl http://127.0.0.1:9001/peers
curl http://127.0.0.1:9001/dht
```

---

## Resources

### cjdns
- **GitHub**: https://github.com/cjdelisle/cjdns
- **Whitepaper**: https://github.com/cjdelisle/cjdns/blob/master/doc/Whitepaper.md
- **Protocol Spec**: https://github.com/cjdelisle/cjdns/blob/master/doc/ProtocolSpec.md
- **Admin API**: https://github.com/cjdelisle/cjdns/blob/master/doc/AdminAPI.md

### Yggdrasil
- **GitHub**: https://github.com/yggdrasil-network/yggdrasil
- **Documentation**: https://github.com/yggdrasil-network/yggdrasil/blob/master/README.md
- **Protocol Spec**: https://github.com/yggdrasil-network/yggdrasil/blob/master/doc/ProtocolSpec.md
- **Admin API**: https://github.com/yggdrasil-network/yggdrasil/blob/master/doc/AdminAPI.md

### Community
- **cjdns IRC**: #cjdns on Libera.Chat
- **Yggdrasil Matrix**: #yggdrasil:matrix.org
- **Reddit**: r/cjdns, r/yggdrasil