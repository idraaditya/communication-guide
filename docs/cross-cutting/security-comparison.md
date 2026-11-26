# Security Comparison Across Protocols

## Security Properties Matrix

| Protocol | Encryption | Authentication | Key Management | Forward Secrecy | Replay Protection | DoS Protection |
|----------|------------|----------------|----------------|-----------------|-------------------|----------------|
| **LoRaMesher** | AES-128-CTR | AES-CMAC | PSK / AppKey | ❌ | Frame counter | ❌ |
| **Meshtastic** | AES-256-CTR | AES-CMAC | PSK / QR code | ❌ | Packet ID + counter | ❌ |
| **BATMAN-ADV** | ❌ (L2) | ❌ | N/A | N/A | N/A | ❌ |
| **802.11s** | AES-CCMP | SAE/PSK | 4-way handshake | ✅ (per session) | Sequence counter | SAE |
| **Babel** | ❌ | ❌ | N/A | N/A | Sequence number | ❌ |
| **OpenThread** | AES-CCM* | DTLS/PSKc | Commissioner | ✅ (session) | Frame counter | DTLS |
| **Zigbee** | AES-128-CCM | Link/Net keys | Trust Center | ✅ (session) | Frame counter | ❌ |
| **BLE Mesh** | AES-CCM | NetKey/AppKey | Provisioner | ✅ (session) | Seq + IV Index | ❌ |
| **WireGuard** | ChaCha20-Poly1305 | Noise_IK | Static keys + PSK | ✅ (1-RTT) | 64-bit counter | Cookie reply |
| **BIRD2** | ❌ (IPsec) | OSPF Auth/BGP TCP-AO | Manual/Keychain | IPsec | IPsec | ❌ |
| **cjdns** | Curve25519/ChaCha20 | CryptoKey | Self-certifying | ✅ | Seq + IV Index | DHT rate limit |
| **Yggdrasil** | Curve25519/ChaCha20 | CryptoKey | Self-certifying | ✅ | Seq + IV Index | DHT rate limit |

*OpenThread uses AES-CCM at MAC layer, DTLS at commissioning

---

## Detailed Security Analysis

### Category 1: LoRa (LoRaMesher, Meshtastic)

#### LoRaMesher Security

```c
// Security Architecture (PROTOCOL_SPEC.md §5.5)
// - AES-128-CTR for payload encryption
// - AES-CMAC for message integrity (MIC)
// - Keys: AppKey (application), NwkKey (network)
// - Key derivation: AES-CMAC based

// Frame Structure with Security:
struct SecureFrame {
    // Unencrypted header
    uint8_t  version;           // 1
    uint8_t  type;              // Message type
    uint16_t src_addr;          // Source
    uint16_t dst_addr;          // Destination
    uint8_t  flags;             // Security enabled, etc.
    
    // Encrypted payload (AES-128-CTR)
    uint8_t  payload[max_payload];
    
    // MIC (AES-CMAC, 4 bytes)
    uint32_t mic;
};

// Key Hierarchy:
MasterKey (128-bit)
    │
    ├── AppKey = CMAC(MasterKey, "app" + DevEUI)
    ├── NwkKey = CMAC(MasterKey, "nwk" + DevEUI)
    └── JoinKey = CMAC(MasterKey, "join" + DevEUI)  // For sponsor join

// Frame Counter (replay protection):
// - 32-bit counter per session
// - Incremented per frame
// - Verified on receive
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ✅ | AES-128-CTR |
| Integrity | ✅ | AES-CMAC (4 bytes) |
| Authentication | ✅ | Symmetric keys |
| Forward Secrecy | ❌ | Static keys |
| Key Rotation | Manual | No automatic rotation |
| Replay Protection | ✅ | 32-bit frame counter |
| DoS Resistance | ❌ | No cookie mechanism |

#### Meshtastic Security

```c
// Security (Channels.cpp, CryptoEngine.cpp)
// - AES-256-CTR for payload encryption
// - AES-CMAC for message integrity
// - Per-channel keys (up to 8 channels)
// - PSK or QR code sharing

// Channel Key Derivation:
ChannelKey = PBKDF2-HMAC-SHA256(PSK, "Meshtastic" + ChannelName, 10000, 32)

// Frame Encryption:
Nonce = PacketID (32-bit) || ChannelIndex (8-bit) || Flags
Ciphertext = AES-256-CTR(ChannelKey, Nonce, Plaintext)
MIC = AES-CMAC(ChannelKey, Ciphertext || Header)

// QR Code Sharing:
// - Encodes: Channel Name + PSK (base64)
// - Format: "meshtastic://<channel_name>?key=<base64_psk>"
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ✅ | AES-256-CTR |
| Integrity | ✅ | AES-CMAC |
| Authentication | ✅ | Symmetric PSK |
| Forward Secrecy | ❌ | Static PSK |
| Key Rotation | Manual | Channel key change |
| Replay Protection | ✅ | Packet ID + dedup cache |
| DoS Resistance | ❌ | No rate limiting |

### Category 2: 802.15.4 / BLE (Thread, Zigbee, BLE Mesh)

#### OpenThread/Thread Security

```c
// Thread Security (Thread Spec §5, §8)
// MAC Layer: AES-CCM (IEEE 802.15.4)
// Commissioning: DTLS 1.2 + PSKc
// Key Hierarchy:
//   Master Key → Key Derivation →
//   ├── Network Key (rotated)
//   ├── Key Encryption Key (KEK)
//   ├── MAC Key (per frame counter)
//   ├── MLE Key
//   └── Application Keys

// MAC Frame Security (IEEE 802.15.4):
// Security Control: Security Level (ENC-MIC-32/64/128), Key ID Mode
// Frame Counter: 32-bit (per key)
// Key Source: 8 bytes (Key ID Mode 2/3)
// MIC: 4/8/16 bytes

// DTLS Commissioning:
// PSKc = PBKDF2-HMAC-SHA256(Passphrase, "Thread" + ExtPANID, 10000, 16)
// DTLS 1.2 with PSK cipher suites
// Commissioner authenticates Joiner
// Joiner receives: Network Key, Key Rotation Schedule, Network Parameters
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ✅ | AES-CCM (MAC) + DTLS (commissioning) |
| Integrity | ✅ | AES-CCM MIC |
| Authentication | ✅ | DTLS + PSKc / Commissioner |
| Forward Secrecy | ✅ | Session keys (DTLS) |
| Key Rotation | ✅ | Periodic (configurable) |
| Replay Protection | ✅ | Frame counter (32-bit) |
| DoS Resistance | ✅ | DTLS cookies, rate limiting |

#### Zigbee Security

```c
// Zigbee Security (Zigbee Spec, ZCL)
// Key Types:
// - Master Key (pre-shared or derived)
// - Link Key (pairwise, derived from Master)
// - Network Key (broadcast, rotated)
// - Trust Center Link Key (with TC)
// - Install Code (for secure join)

// Key Hierarchy:
Master Key (per device)
    │
    ├── Trust Center Link Key = AES-CMAC(Master, "TC" + IEEE)
    ├── Link Key (pairwise) = SKKE (Symmetric Key Key Establishment)
    ├── Network Key (broadcast) = Generated by TC, rotated
    └── Application Keys (per cluster/profile)

// Security Levels:
// 0x00: None
// 0x01: MIC-32
// 0x02: MIC-64
// 0x03: MIC-128
// 0x04: ENC
// 0x05: ENC-MIC-32
// 0x06: ENC-MIC-64
// 0x07: ENC-MIC-128 (DEFAULT for Zigbee 3.0)

// Frame Counter: 32-bit per key
// Replay Protection: Frame counter + duplicate detection
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ✅ | AES-128-CCM (ENC-MIC-128) |
| Integrity | ✅ | AES-CCM MIC-128 |
| Authentication | ✅ | Link Keys, Install Codes |
| Forward Secrecy | ✅ | Session keys (SKKE) |
| Key Rotation | ✅ | Network Key rotation |
| Replay Protection | ✅ | Frame counter + dup detection |
| DoS Resistance | ❌ | Limited |

#### BLE Mesh Security

```c
// BLE Mesh Security (Bluetooth Mesh Spec 1.0.1)
// Key Hierarchy:
// - Device Key (per device, derived from Provisioning)
// - NetKey (per subnet, 128-bit)
// - AppKey (per application, 128-bit)
// - Device Key = K1(ECDH Secret, "prdk", DeviceUUID)
// - NetKey = K1(ECDH Secret, "netk", ProvisioningSalt)
// - AppKey = K2(NetKey, "appk", AppKeyIndex)

// Provisioning (ECDH P-256):
// 1. Device generates static ECDH keypair
// 2. Provisioner generates static ECDH keypair
// 3. ECDH shared secret = d_device * Q_provisioner = d_provisioner * Q_device
// 4. Confirmation = AES-CMAC(ConfirmationKey, ...)
// 5. Provisioning Data encrypted with SessionKey

// Message Security:
// - Network Layer: NetKey (AES-CCM, 64-bit MIC)
// - Upper Transport: AppKey (AES-CCM, 64-bit MIC)
// - Sequence Number: 24-bit (per NetKey)
// - IV Index: 32-bit (incremented every 96 hours)
// - Replay Protection: Seq + IV Index + Source Address

// Friendship Security:
// - Friend Credential = K3(NetKey, "frnd", FriendAddr)
// - LPN encrypts with Friend Credential
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ✅ | AES-CCM (NetKey/AppKey) |
| Integrity | ✅ | AES-CCM MIC-64 |
| Authentication | ✅ | ECDH Provisioning |
| Forward Secrecy | ✅ | Session keys (Provisioning) |
| Key Rotation | ✅ | IV Update (96h), Key Refresh |
| Replay Protection | ✅ | Seq (24-bit) + IV Index (32-bit) |
| DoS Resistance | ❌ | Limited |

### Category 3: WiFi Mesh (BATMAN-ADV, Babel, 802.11s)

#### 802.11s Security

```c
// 802.11s Mesh Security (IEEE 802.11-2020)
// - SAE (Simultaneous Authentication of Equals) - WPA3
// - Or PSK (WPA2-Personal)
// - Mesh Peering: Open Authentication → SAE → Confirm
// - Pairwise Master Key (PMK) from SAE
// - Pairwise Transient Key (PTK) from PMK
// - Group Temporal Key (GTK) for broadcast
// - AES-CCMP for encryption (or GCMP-256 for WPA3)

// SAE Handshake:
// 1. Commit: scalar + element (password-derived)
// 2. Confirm: HMAC-SHA256(PMK, peer_commit || own_commit)
// 3. PMK = SAE_KDF(password, own_scalar, peer_scalar, own_element, peer_element)
// 4. PTK = KDF(PMK, "SAE KCK", ...)
// 5. GTK = GMK (group) distributed via Group Key Handshake

// Mesh Peering States:
// IDLE → OPEN → CONFIRM → ESTABLISHED
// Each peer has separate PTK/GTK
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ✅ | AES-CCMP / GCMP-256 |
| Integrity | ✅ | CCMP/GCMP MIC |
| Authentication | ✅ | SAE (WPA3) / PSK (WPA2) |
| Forward Secrecy | ✅ | Per-session PTK |
| Key Rotation | ✅ | GTK rotation, SAE re-auth |
| Replay Protection | ✅ | Packet Number (48-bit) |
| DoS Resistance | ✅ | SAE anti-clogging (cookie) |

#### BATMAN-ADV Security

```c
// BATMAN-ADV: NO built-in security (Layer 2)
// - OGMs sent in clear
// - No encryption, no authentication
// - Relies on upper layers (IPsec, WireGuard, TLS)
// - Vulnerable to: OGM injection, route hijacking, MITM

// Mitigation:
// 1. Run WireGuard/IPsec OVER bat0 interface
// 2. Use VLAN isolation
// 3. Physical security (private spectrum)
// 4. Monitor for anomalies (batctl)
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ❌ | None (L2) |
| Integrity | ❌ | None |
| Authentication | ❌ | None |
| Forward Secrecy | N/A | - |
| Key Rotation | N/A | - |
| Replay Protection | ❌ | None |
| DoS Resistance | ❌ | OGM flooding |

#### Babel Security

```c
// Babel: NO built-in security (RFC 8966)
// - Messages sent in clear
// - No encryption, no authentication
// - Relies on IPsec or WireGuard at L3
// - Vulnerable to: Route injection, spoofing

// Mitigation:
// 1. Run IPsec (ESP/AH) for Babel traffic
// 2. Run WireGuard tunnel for Babel
// 3. Use Babel authentication extension (experimental)
// 4. Filter at kernel (iptables/nftables)
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ❌ | None |
| Integrity | ❌ | None |
| Authentication | ❌ | None |
| Forward Secrecy | N/A | - |
| Key Rotation | N/A | - |
| Replay Protection | Sequence number only | No crypto |
| DoS Resistance | ❌ | Route injection |

### Category 4: VPN / Overlay (WireGuard, BIRD2, cjdns, Yggdrasil)

#### WireGuard Security

```c
// WireGuard Security (WireGuard Whitepaper, NDSS 2020)
// Protocol: Noise_IK
// - Initiator knows Responder static public key
// - Responder knows Initiator static public key

// Handshake (1-RTT):
// Message 1 (I→R): e, es, {is, timestamp}_k1
// Message 2 (R→I): e, ee, se, {rs, timestamp}_k2
// Message 3 (I→R): {}_k3 (confirmation)

// Crypto:
// - KDF: HKDF-HMAC-BLAKE2s
// - AEAD: ChaCha20-Poly1305
// - DH: Curve25519 (X25519)
// - Hash: BLAKE2s
// - Timestamp: TAI64N (replay protection)

// Transport:
// - Counter: 64-bit (little-endian)
// - Nonce: counter || 0x00000000
// - Encrypted payload + 16-byte auth tag

// Cryptokey Routing:
// - Peer Public Key → Allowed IPs
// - Destination IP → Peer Public Key (longest prefix match)

// DoS Protection:
// - Cookie Reply: Responder sends cookie under load
// - Initiator must include cookie in Message 1
// - Rate limiting per peer
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ✅ | ChaCha20-Poly1305 |
| Integrity | ✅ | Poly1305 auth tag |
| Authentication | ✅ | Noise_IK (static keys) |
| Forward Secrecy | ✅ | Ephemeral DH per session |
| Key Rotation | ✅ | Rekey every 2 min (configurable) |
| Replay Protection | ✅ | 64-bit counter + timestamp |
| DoS Resistance | ✅ | Cookie reply, rate limiting |

#### BIRD2 Security

```c
// BIRD2: NO built-in security for routing protocols
// - OSPF: Simple password / MD5 / SHA (RFC 5709)
// - BGP: TCP MD5 Signature Option (RFC 2385) / TCP-AO (RFC 5925)
// - RIP: Simple password / MD5
// - Babel: No auth (use IPsec)

// IPsec for BIRD2:
// - Kernel IPsec (XFRM) for OSPF/BGP/Babel packets
// - ESP for encryption, AH for integrity
// - IKEv2 for key management (strongSwan, libreswan)

// OSPF Authentication:
protocol ospf {
    interface "eth0" {
        authentication md5;
        password "ospf-secret";
        # or simple "password"
        # or sha "keyid" "key"
    };
}

// BGP Authentication:
protocol bgp {
    password "bgp-secret";
    # or tcp_ao "keyid" "key";
}
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | IPsec only | ESP |
| Integrity | IPsec / MD5 / TCP-AO | AH / TCP-AO |
| Authentication | MD5 / TCP-AO / Simple | Protocol-dependent |
| Forward Secrecy | IPsec only | IKEv2 |
| Key Rotation | Manual / IKEv2 | Config-dependent |
| Replay Protection | IPsec / Sequence | ESP/AH |
| DoS Resistance | Limited | TCP-AO helps BGP |

#### cjdns Security

```c
// cjdns Security (cjdns Whitepaper)
// - Address = Hash(PublicKey) → fc00::/8 + hash
// - CryptoAuth: Curve25519 + ChaCha20-Poly1305
// - Session: Ephemeral DH per connection
// - Switch Labels: Source routing with 32-bit labels

// Key Hierarchy:
// - Permanent Key: Curve25519 (identity)
// - Session Key: ECDH(ephemeral, permanent) per peer
// - Switch Keys: Derived per path

// Path Discovery:
// - BFS with pruning
// - Link Quality Metric (latency, loss)
// - Cryptographic verification of path

// DHT:
// - Kademlia for key/node discovery
// - Signed records (Ed25519)
// - Rate limiting for DoS
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ✅ | ChaCha20-Poly1305 |
| Integrity | ✅ | Poly1305 |
| Authentication | ✅ | Curve25519 (self-cert) |
| Forward Secrecy | ✅ | Ephemeral DH per session |
| Key Rotation | Per session | Automatic |
| Replay Protection | ✅ | Seq + IV Index |
| DoS Resistance | ✅ | DHT rate limiting |

#### Yggdrasil Security

```c
// Yggdrasil Security (Yggdrasil Spec)
// - Address = 200::/7 + Curve25519 public key hash
// - Crypto: Curve25519 + ChaCha20-Poly1305
// - Tree Routing + Shortcuts
// - Session: Noise-like handshake

// Key Hierarchy:
// - Permanent Key: Curve25519 (identity, address derivation)
// - Session Key: ECDH per connection
// - Peer Authentication: Mutual Curve25519 verification

// Peering:
// 1. TCP/TLS/QUIC/WebSocket connection
// 2. Curve25519 key exchange
// 3. Mutual authentication (verify peer public key = address)
// 4. Session keys derived

// DHT:
// - Kademlia for node discovery
// - Rate limiting
// - No persistent DHT state (ephemeral)
```

**Security Properties:**
| Property | Status | Notes |
|----------|--------|-------|
| Confidentiality | ✅ | ChaCha20-Poly1305 |
| Integrity | ✅ | Poly1305 |
| Authentication | ✅ | Curve25519 (self-cert) |
| Forward Secrecy | ✅ | Ephemeral DH per session |
| Key Rotation | Per session | Automatic |
| Replay Protection | ✅ | Seq + IV Index |
| DoS Resistance | ✅ | Connection limits, rate limiting |

---

## Security Best Practices by Category

### Category 1 (LoRa)
```yaml
# LoRaMesher
- Use unique AppKey per device (not shared)
- Enable frame counter verification
- Rotate keys periodically (manual process)
- Use SF7/SF8 for shorter airtime (less exposure)
- Monitor for replay attacks (frame counter gaps)

# Meshtastic
- Use unique PSK per channel
- Share via QR code (not plaintext)
- Enable "Encrypted Storage" on device
- Use "Phone API Access Control" for admin
- Rotate channel keys periodically
```

### Category 2 (802.15.4/BLE)
```yaml
# OpenThread/Thread
- Use DTLS commissioning with strong passphrase
- Enable "Native Commissioning" (Thread 1.2+)
- Configure key rotation interval (default 30 days)
- Use Commissioner with proper authentication
- Monitor for orphaned nodes

# Zigbee
- Use Install Codes for secure join (not default TC Link Key)
- Enable "High Security" mode (Zigbee 3.0)
- Rotate Network Key periodically
- Use unique Link Keys per device pair
- Monitor Trust Center for anomalies

# BLE Mesh
- Use Static OOB for provisioning (not "No OOB")
- Enable IV Update (automatic every 96h)
- Use unique AppKeys per application
- Monitor for replay attacks (Seq/IV Index)
- Limit Friendship to trusted nodes
```

### Category 3 (WiFi Mesh)
```yaml
# 802.11s
- Use WPA3-SAE (not WPA2-PSK)
- Enable "Mesh Peering" with SAE
- Use unique PMK per mesh (not shared PSK)
- Enable GTK rotation
- Monitor for rogue peers

# BATMAN-ADV
- ALWAYS run WireGuard/IPsec OVER bat0
- Use VLAN isolation for mesh traffic
- Monitor batctl for anomalies
- Physical security for mesh links

# Babel
- ALWAYS run IPsec/WireGuard for Babel traffic
- Filter Babel packets at kernel (nftables)
- Monitor for route injection
```

### Category 4 (VPN/Overlay)
```yaml
# WireGuard
- Generate unique key pair per node
- Use PSK for additional security (post-quantum)
- Set AllowedIPs precisely (least privilege)
- Enable PersistentKeepalive for NAT
- Monitor handshake timestamps

# BIRD2
- Use TCP-AO for BGP (not MD5)
- Use MD5/SHA for OSPF (not simple password)
- Run IPsec for protocol traffic
- Filter at kernel (nftables)

# cjdns/Yggdrasil
- Verify peer public keys match addresses
- Use TLS/QUIC for peer connections
- Monitor DHT for anomalies
- Limit connections per peer
```

---

## Threat Model by Category

| Threat | Cat 1 (LoRa) | Cat 2 (802.15.4/BLE) | Cat 3 (WiFi Mesh) | Cat 4 (VPN/Overlay) |
|--------|--------------|----------------------|-------------------|---------------------|
| **Eavesdropping** | AES-CTR/CCM | AES-CCM/CCM | AES-CCMP/GCMP | ChaCha20 |
| **Message Injection** | CMAC/MIC | Frame counter + MIC | CCMP/GCMP MIC | Poly1305 |
| **Replay** | Frame counter | Frame counter / Seq | Packet Number | 64-bit counter |
| **Route Hijacking** | Route validation | Route validation | SAE peer auth | Cryptokey routing |
| **DoS (Flooding)** | Limited | Limited | SAE cookie | Cookie/rate limit |
| **MITM** | Mutual auth | DTLS/ECDH mutual | SAE mutual | Noise_IK mutual |
| **Key Compromise** | Session keys | Session keys + rotation | Session keys + rotation | Ephemeral DH |
| **Side Channel** | Timing (CTR) | Timing (CCM) | Timing (CCMP) | Constant-time |

---

## Compliance & Standards

| Protocol | Standard | Certification | Audit |
|----------|----------|---------------|-------|
| LoRaMesher | Custom (IEEE 802.15.4g based) | LoRa Alliance | Academic papers |
| Meshtastic | Custom | None | Community |
| OpenThread | Thread 1.4 | Thread Certified | Google/Nest |
| Zigbee | Zigbee 3.0 | Zigbee Certified | CSA |
| BLE Mesh | Mesh 1.0.1 | Bluetooth Qualified | Bluetooth SIG |
| 802.11s | IEEE 802.11s-2011 | Wi-Fi Certified | Wi-Fi Alliance |
| BATMAN-ADV | Custom | None | Kernel review |
| Babel | RFC 8966 | None | IETF |
| WireGuard | Noise_IK | Linux kernel | Formal verification |
| BIRD2 | RFC 2328/4271/8966 | None | Production ISP |
| cjdns | Custom | None | Community |
| Yggdrasil | Custom | None | Community |

---

## Recommendations Summary

| Priority | Action |
|----------|--------|
| **1** | Use protocols with **forward secrecy** (WireGuard, Thread, 802.11s) |
| **2** | **Rotate keys** periodically (automatic preferred) |
| **3** | **Authenticate peers** mutually (not just one-way) |
| **4** | **Monitor** for anomalies (replay, route injection, unknown peers) |
| **5** | **Layer security**: WireGuard/IPsec under insecure mesh (BATMAN-ADV, Babel) |
| **6** | **Least privilege**: Precise AllowedIPs, minimal AppKeys/NetKeys |
| **7** | **Update firmware** regularly for crypto patches |
| **8** | **Physical security** for mesh nodes (tamper detection) |

---

## Resources

- **WireGuard**: https://www.wireguard.com/protocol/
- **Thread Security**: https://www.threadgroup.org/
- **Zigbee Security**: https://csa-iot.org/all-solutions/zigbee/
- **Bluetooth Mesh Security**: https://www.bluetooth.com/specifications/mesh/
- **802.11s Security**: IEEE 802.11-2020 §11.24
- **Noise Protocol**: https://noiseprotocol.org/
- **Curve25519**: https://cr.yp.to/ecdh.html
- **ChaCha20-Poly1305**: RFC 8439