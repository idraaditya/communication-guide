# Migration Guide

## Overview

This guide covers migration between protocols and protocol versions within the same category, and cross-category migrations for changing requirements.

---

## Category 1: LoRa Protocols

### Meshtastic 1.x → 2.x

**Breaking Changes:**
- Protobuf schema updated (incompatible with 1.x)
- Channel encryption: PSK format changed
- Device configuration: New JSON structure
- Mobile app: Requires 2.x app

**Migration Steps:**
```bash
# 1. Backup configuration
meshtastic --port /dev/ttyUSB0 --export-config backup_v1.json

# 2. Update firmware
meshtastic --port /dev/ttyUSB0 --flash v2.x

# 3. Convert config (manual)
# - Channels: Recreate with new PSK format
# - Device: Re-enter name, owner, GPS settings
# - LoRa: Re-enter region, power, SF

# 4. Test with one node pair
# 5. Roll out to fleet
```

### Meshtastic ↔ LoRaMesher

**Not directly compatible** - Different protocols, different PHY/MAC parameters.

**Coexistence Strategy:**
```
Different frequencies/channels:
- Meshtastic: 906 MHz (US) / 868 MHz (EU), SF7, BW125, Sync 0x3444
- LoRaMesher: 915 MHz (US) / 869.9 MHz (EU), SF7, BW125, Sync 0x12

Same hardware, different firmware:
- Flash Meshtastic for human messaging + MQTT
- Flash LoRaMesher for sensor backbone + deterministic latency

Gateway node (dual-radio):
- Radio 1: Meshtastic (human traffic)
- Radio 2: LoRaMesher (sensor traffic)
- Bridge: Application-layer forwarder
```

### LoRaMesher 0.x → 1.0

**Full Rewrite** - See [MIGRATION.md](https://github.com/LoRaMesher/LoRaMesher/blob/main/MIGRATION.md)

**Key Changes:**
- API: C++20, fluent Builder pattern
- Config: PinConfig, RadioConfig, LoRaMeshProtocolConfig objects
- Callbacks: SetDataCallback, SetLogCallback
- TDMA: Automatic slot alignment
- Sponsor-based join (new)
- NM Election: Priority + battery based

---

## Category 2: 802.15.4 / BLE Protocols

### OpenThread Version Upgrades

**Thread 1.1 → 1.2 → 1.3 → 1.4**

**Thread 1.2 Key Features:**
- CSL (Connected Sleep) for sleepy end devices
- Multicast improvements (MPL)
- Service Registration Protocol (SRP)

**Thread 1.3 Key Features:**
- Matter support (Device Attestation)
- Improved commissioning
- Enhanced security

**Thread 1.4 Key Features:**
- Matter 1.2 support
- Enhanced multicast
- Operational datasets improvements

**Migration:**
```bash
# OpenThread version is tied to ESP-IDF version
# ESP-IDF 5.1 → Thread 1.2
# ESP-IDF 5.2 → Thread 1.3/1.4

# Update ESP-IDF:
cd ~/esp/esp-idf
git checkout v5.2
git submodule update --init --recursive
./install.sh esp32h2 esp32c6

# Rebuild application
idf.py build flash monitor
```

### OpenThread ↔ Zigbee

**Not interoperable** - Different network layers, different application layers.

**Coexistence:**
```
Same hardware (ESP32-H2/C6), different firmware:
- Flash OpenThread for Thread/Matter
- Flash Zigbee for Zigbee 3.0

Dual-protocol gateway (ESP32-C6):
- Radio: Time-sliced 802.15.4 (Thread + Zigbee)
- Application: Thread ↔ Zigbee bridge
- Use case: Matter device + legacy Zigbee sensors
```

### BLE Mesh → Thread/Zigbee

**Migration Path:**
```
BLE Mesh (phone provisioning) 
    → Thread (Matter, IPv6)
    → Zigbee (HA ecosystem)

Reasons to migrate:
- Thread: Matter support, IPv6, border router
- Zigbee: Mature HA ecosystem, Green Power
- BLE Mesh: Phone provisioning, no border router needed
```

**Data Migration:**
- Device identities: Re-provision (different key hierarchies)
- Group/Scene data: Recreate (different models)
- Automation rules: Rewrite (different platforms)

---

## Category 3: WiFi Mesh Protocols

### BATMAN-ADV ↔ Babel ↔ 802.11s

**Not directly interoperable** - Different layers, different routing.

**Layer 2 vs Layer 3:**
```
BATMAN-ADV (L2): Transparent bridging, VLAN, DHCP relay
Babel (L3): Native IPv4/IPv6 routing, policy
802.11s (L2): Standard WiFi mesh, SAE security
```

**Migration Scenarios:**

| From | To | Effort | Notes |
|------|-----|--------|-------|
| BATMAN-ADV | Babel | Medium | L2→L3, re-IP network |
| BATMAN-ADV | 802.11s | Low | Same L2, different protocol |
| Babel | 802.11s | High | L3→L2, re-architect |
| 802.11s | BATMAN-ADV | Low | L2→L2, similar concepts |

**Coexistence (Hybrid):**
```
BATMAN-ADV (L2 mesh) + Babel (L3 routing)
- bat0 interface runs BATMAN-ADV
- Babel runs on top of bat0 (or separate WiFi)
- Use case: L2 transparency + L3 policy routing
```

### 802.11s Migration (Kernel Versions)

**Linux Kernel 802.11s:**
- Kernel 4.0+: Basic HWMP
- Kernel 5.0+: Improved metrics, congestion control
- Kernel 6.0+: Better roaming, multi-link

**Migration:**
```bash
# Update kernel on OpenWrt/Ubuntu
opkg update && opkg upgrade kernel
# Or
apt update && apt install linux-generic-hwe-22.04

# Verify 802.11s features
iw phy phy0 info | grep -A 20 "mesh"
```

---

## Category 4: VPN / Overlay Protocols

### WireGuard Version Updates

**WireGuard is stable** - Protocol unchanged since 1.0 (2020).

**Updates are kernel/userspace only:**
```bash
# Linux kernel (auto with distro updates)
apt update && apt upgrade linux-image-generic

# WireGuard-Go (userspace)
cd wireguard-go
git pull
go build
```

### WireGuard ↔ IPsec

**Migration WireGuard → IPsec:**
```bash
# strongSwan IPsec config
# /etc/ipsec.conf
conn site-to-site
    left=%defaultroute
    leftsubnet=10.0.0.0/24
    right=remote.example.com
    rightsubnet=10.1.0.0/24
    authby=secret
    ike=aes256-sha256-modp2048
    esp=aes256-sha256
    keyingtries=0
    auto=start

# Migration steps:
# 1. Deploy IPsec alongside WireGuard
# 2. Test connectivity
# 3. Switch routing
# 4. Decommission WireGuard
```

**Migration IPsec → WireGuard:**
- Simpler config
- Better performance
- Easier NAT traversal
- Modern crypto

### BIRD2 Version Updates

**BIRD 1.x → 2.x** (Major rewrite)

**BIRD 2.x Key Changes:**
- New configuration syntax
- Protocol modules (OSPF, BGP, Babel, RIP)
- Improved filtering language
- Multiple routing tables
- Better IPv6 support

**Migration:**
```bird
# BIRD 1.x config (old)
protocol ospf {
    export all;
    interface "eth0" { cost 10; };
}

# BIRD 2.x config (new)
protocol ospf v2 {
    ipv4 {
        export all;
    };
    area 0 {
        interface "eth0" {
            cost 10;
        };
    };
}
```

### cjdns / Yggdrasil Version Updates

**Both are beta** - Breaking changes possible.

**Update:**
```bash
# cjdns
cd cjdns && git pull && ./do

# Yggdrasil
cd yggdrasil && git pull && make

# Config usually compatible, but check changelog
```

---

## Cross-Category Migrations

### LoRa (Cat 1) → Thread (Cat 2)

**When:** Need IPv6, Matter support, border router

**Migration:**
```
LoRaMesher/Meshtastic (sensor backbone)
    │
    ▼
Gateway Node (ESP32-C6: LoRa + Thread)
    │
    ▼
Thread Network (IPv6, Matter)
    │
    ▼
Border Router → Internet/Cloud
```

**Gateway Implementation:**
```c
// ESP32-C6: LoRa (SPI) + Thread (802.15.4)
// LoRa side: LoRaMesher node (sensor data)
// Thread side: OpenThread border router

// Data flow:
LoRaMesher_Sensor_Data → LoRa Gateway → Thread_Network → Border_Router → MQTT/Cloud
```

### WiFi Mesh (Cat 3) → WireGuard (Cat 4)

**When:** Need secure tunnels over untrusted mesh

**Migration:**
```
Babel/BATMAN-ADV/802.11s (mesh transport)
    │
    ▼
WireGuard Tunnels (encrypted overlay)
    │
    ▼
Secure IPv4/IPv6 routing
```

**Implementation:**
```bash
# On each mesh node:
# 1. Mesh provides L2/L3 connectivity
# 2. WireGuard creates encrypted tunnels
# 3. Routing protocols (Babel/OSPF) run OVER WireGuard

# Example: Babel over WireGuard
# wg0.conf:
[Interface]
PrivateKey = ...
ListenPort = 51820

[Peer]
PublicKey = ...
AllowedIPs = 10.0.0.0/8  # Mesh subnet
Endpoint = peer.mesh.local:51820
PersistentKeepalive = 25

# babeld.conf:
interface wg0
    type wired
    hello-interval 200
```

### Zigbee (Cat 2) → Matter/Thread (Cat 2)

**When:** Want Matter ecosystem, IPv6

**Migration Path:**
```
Zigbee 3.0 devices
    │
    ▼
Matter Bridge (ESP32-H2/C6 + Thread)
    │
    ▼
Thread Network (Matter fabric)
    │
    ▼
Matter Controller (Apple Home, Google Home, HA)
```

**Bridge Implementation:**
```c
// ESP32-H2: Thread + Zigbee co-existence
// Zigbee side: Coordinator (Zigbee 3.0)
// Thread side: OpenThread (Matter device)

// Zigbee clusters → Matter clusters mapping:
// OnOff → OnOff
// LevelControl → LevelControl
// ColorControl → ColorControl
// TemperatureMeasurement → TemperatureSensor
// OccupancySensing → OccupancySensor

// Matter Bridge Device Type: 0x000B (Bridge)
// Exposes Zigbee endpoints as Matter endpoints
```

---

## Data Migration Checklist

### Network Parameters

| Parameter | Action |
|-----------|--------|
| Network ID / PAN ID | Reconfigure (different formats) |
| Channel / Frequency | Reconfigure (different bands) |
| Encryption Keys | Regenerate (different hierarchies) |
| Device Identities | Re-provision (different key derivation) |
| Group/Scene Data | Recreate (different models) |

### Application Data

| Data Type | Migration |
|-----------|-----------|
| Sensor Calibration | Preserve (re-flash) |
| Device Names/Labels | Export/Import JSON |
| Automation Rules | Rewrite (platform-specific) |
| Historical Data | Export CSV → New platform |
| User Accounts | Recreate (different auth) |

### Firmware Update Strategy

```bash
# 1. Canary Deployment (1-5% of fleet)
# 2. Monitor metrics (PDR, latency, crashes)
# 3. Gradual Rollout (25%, 50%, 75%, 100%)
# 4. Rollback Plan (previous firmware OTA)

# OTA Update (Meshtastic):
meshtastic --port /dev/ttyUSB0 --flash-firmware firmware.bin

# OTA Update (OpenThread):
# Requires Border Router with SRP/OTA
# ot-ctl ota <image>

# OTA Update (ESP-IDF apps):
# esp_https_ota component
# Partition: ota_0, ota_1, factory
```

---

## Rollback Procedures

### Firmware Rollback

```bash
# Meshtastic:
meshtastic --port /dev/ttyUSB0 --flash-firmware previous_version.bin

# ESP-IDF (OpenThread, Zigbee, BLE Mesh):
# 1. Factory partition has known-good firmware
# 2. Set boot partition to factory
esptool.py --port /dev/ttyUSB0 --chip esp32h2 \
  --after hard_reset write_flash 0x8000 boot_app0.bin
# 3. Or use OTA rollback API
esp_ota_set_boot_partition(esp_partition_find_first(
    ESP_PARTITION_TYPE_APP, ESP_PARTITION_SUBTYPE_APP_FACTORY, NULL));
esp_restart();

# OpenWrt (BATMAN-ADV, Babel, 802.11s):
sysupgrade -n previous_firmware.bin
```

### Configuration Rollback

```bash
# Meshtastic:
meshtastic --port /dev/ttyUSB0 --import-config backup_v1.json

# OpenThread:
# Dataset stored in flash, restore from backup
# ot-ctl dataset import <backup>

# ESP-Zigbee:
# NVS stores config, erase to defaults
nvs_flash_erase();
nvs_flash_init();

# BATMAN-ADV / Babel / 802.11s:
# /etc/config/network, /etc/config/babeld
# Restore from backup
cp /etc/config/network.backup /etc/config/network
/etc/init.d/network restart
```

---

## Testing Migration

### Pre-Migration Validation

```bash
# 1. Baseline metrics (current protocol)
python scripts/run_benchmarks.py --protocol current --full-suite

# 2. Lab test new protocol (same hardware if possible)
python scripts/run_benchmarks.py --protocol new --topology line --nodes 5

# 3. Compare results
python scripts/compare_benchmarks.py --current current_results.json --new new_results.json

# 4. Interop test (if applicable)
# Test new protocol nodes with existing protocol nodes
```

### Post-Migration Validation

```bash
# 1. Full fleet metrics
# 2. Edge cases (mobile, far nodes, interference)
# 3. Failure scenarios (node loss, partition)
# 4. Battery life verification
# 4. OTA update test
```

---

## Migration Timeline Template

```
WEEK 1-2: Planning
├── Requirements analysis
├── Protocol selection
├── Hardware assessment
├── Risk analysis
└── Rollback plan

WEEK 3-4: Lab Development
├── Prototype (5-10 nodes)
├── Integration testing
├── Performance baseline
└── Documentation

WEEK 5-6: Field Pilot
├── 50-100 nodes
├── Real-world conditions
├── Metrics collection
└── Issue resolution

WEEK 7-8: Gradual Rollout
├── 25% → 50% → 75% → 100%
├── Monitoring dashboard
├── Rollback triggers
└── Support runbook

WEEK 9: Stabilization
├── Final validation
├── Documentation update
├── Training
└── Handover
```

---

## Resources

- **Meshtastic Migration**: https://meshtastic.org/docs/getting-started/upgrading/
- **LoRaMesher Migration**: https://github.com/LoRaMesher/LoRaMesher/blob/main/MIGRATION.md
- **OpenThread Updates**: https://openthread.io/guides/
- **ESP-Zigbee Migration**: https://github.com/espressif/esp-zigbee-sdk
- **BLE Mesh Migration**: https://github.com/espressif/esp-idf/tree/master/examples/bluetooth/ble_mesh
- **BATMAN-ADV**: https://www.open-mesh.org/projects/batman-adv/wiki
- **Babel**: https://www.irif.fr/~jch/software/babel/
- **WireGuard**: https://www.wireguard.com/
- **BIRD2**: https://bird.network.cz/
- **cjdns**: https://github.com/cjdelisle/cjdns
- **Yggdrasil**: https://github.com/yggdrasil-network/yggdrasil