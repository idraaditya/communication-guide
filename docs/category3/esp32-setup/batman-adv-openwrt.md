# BATMAN-ADV on OpenWrt - Complete Setup Guide

## Prerequisites

### Hardware
- **OpenWrt-supported router** (any with WiFi)
- **Recommended**: MediaTek Filogic (MT7986), Qualcomm IPQ807x, or x86
- **Multiple devices** for mesh (minimum 3)

### Software
- **OpenWrt 22.03+** or **23.05+**
- **batman-adv kernel module**
- **batctl userspace tool**

---

## Installation

### 1. Install Packages

```bash
opkg update
opkg install kmod-batman-adv batctl

# Optional: for advanced features
opkg install kmod-batman-adv-dat    # Distributed ARP Table
opkg install kmod-batman-adv-bla    # Bridge Loop Avoidance
opkg install kmod-batman-adv-nc     # Network Coding
opkg install kmod-batman-adv-mcast  # Multicast optimization
```

### 2. Verify Installation

```bash
# Check kernel module
lsmod | grep batman

# Check batctl
batctl --version

# Check available mesh interfaces
batctl if
```

---

## Configuration

### 1. Basic Mesh Setup

```bash
# /etc/config/network
config interface 'mesh'
    option type 'bridge'
    option proto 'batadv'
    option mesh 'bat0'

# Add WiFi interfaces to mesh
config wifi-iface 'mesh0'
    option device 'radio0'
    option ifname 'mesh0'
    option network 'mesh'
    option mode 'mesh'
    option mesh_id 'mymesh'
    option mesh_fwding '1'
    option encryption 'psk2+ccmp'
    option key 'your_mesh_password'
    option mesh_rssi_threshold '-80'
```

### 2. Advanced Configuration

```bash
# /etc/config/network - Full example
config interface 'mesh'
    option type 'bridge'
    option proto 'batadv'
    option mesh 'bat0'
    option batadv_mesh 'bat0'
    
    # BATMAN-ADV specific options
    option batadv_aggregated_ogms '1'
    option batadv_ap_isolation '0'
    option batadv_bonding '0'
    option batadv_fragmentation '1'
    option batadv_gw_mode 'off'
    option batadv_gw_bandwidth '0 0'
    option batadv_log_level '0'
    option batadv_nc '1'
    option batadv_orig_interval '1000'
    option batadv_bridge_loop_avoidance '1'
    option batadv_distributed_arp_table '1'
    option batadv_multicast_mode '1'
    option batadv_network_coding '1'
    option batadv_hop_penalty '10'
    option batadv_isolation_mark '0x00000000/0x00000000'

# WiFi mesh interface
config wifi-iface 'mesh0'
    option device 'radio0'
    option ifname 'mesh0'
    option network 'mesh'
    option mode 'mesh'
    option mesh_id 'mymesh'
    option mesh_fwding '1'
    option mesh_rssi_threshold '-80'
    option encryption 'psk2+ccmp'
    option key 'your_secure_password'
    option disabled '0'
```

### 3. Multiple Radio Mesh

```bash
# Dual-band mesh (2.4 + 5 GHz)
config wifi-iface 'mesh_2g'
    option device 'radio0'
    option ifname 'mesh0'
    option network 'mesh'
    option mode 'mesh'
    option mesh_id 'mymesh-2g'
    option mesh_fwding '1'
    option encryption 'psk2+ccmp'
    option key 'mesh_password_2g'

config wifi-iface 'mesh_5g'
    option device 'radio1'
    option ifname 'mesh1'
    option network 'mesh'
    option mode 'mesh'
    option mesh_id 'mymesh-5g'
    option mesh_fwding '1'
    option encryption 'psk2+ccmp'
    option key 'mesh_password_5g'
```

---

## batctl Usage

### Basic Commands

```bash
# Show originator table (nodes in mesh)
batctl o

# Show neighbours
batctl n

# Show translation table (MAC -> Originator)
batctl t

# Show gateway table
batctl gw

# Show mesh interfaces
batctl if

# Ping another node (by MAC)
batctl p <mac_address>

# Throughput test
batctl tp <mac_address>

# Traceroute
batctl tr <mac_address>

# Show mesh statistics
batctl s

# Debug logging
batctl -d 1 -I bat0
```

### Configuration via batctl

```bash
# Set hop penalty
batctl hp 10

# Set orig interval (ms)
batctl it 1000

# Enable/disable features
batctl bla 1    # Bridge Loop Avoidance
batctl dat 1    # Distributed ARP Table
batctl nc 1     # Network Coding
batctl mcast 1  # Multicast optimization
batctl frag 1   # Fragmentation

# Set gateway mode
batctl gw off   # No gateway
batctl gw server # Gateway server
batctl gw client # Gateway client
```

---

## Advanced Features

### 1. Bridge Loop Avoidance (BLA)

```bash
# Enable in /etc/config/network
option batadv_bridge_loop_avoidance '1'

# Configure BLA parameters
# /etc/config/network
option batadv_bla_own '1'
option batadv_bla_grpm '1'
```

**Use Case**: Prevents loops when mesh nodes have wired backhaul connections.

### 2. Distributed ARP Table (DAT)

```bash
# Enable in /etc/config/network
option batadv_distributed_arp_table '1'

# Reduces ARP broadcast traffic significantly
```

**Benefit**: Reduces ARP traffic by caching ARP entries in mesh.

### 3. Network Coding (NC)

```bash
# Enable in /etc/config/network
option batadv_network_coding '1'

# XORs packets for loss recovery
# Best for lossy links
```

### 4. Multicast Optimization (MCAST)

```bash
# Enable in /etc/config/network
option batadv_multicast_mode '1'

# Modes:
# 0 = disabled
# 1 = enabled (default)
# 2 = forced flooding
```

### 5. Gateway Mode

```bash
# Gateway server (connects mesh to Internet)
option batadv_gw_mode 'server'
option batadv_gw_bandwidth '100000 100000'  # down/up kbit

# Gateway client (uses gateway for Internet)
option batadv_gw_mode 'client'
```

---

## Gateway + Internet Access

### 1. Gateway Node Configuration

```bash
# /etc/config/network - Gateway node
config interface 'mesh'
    option type 'bridge'
    option proto 'batadv'
    option mesh 'bat0'
    option batadv_gw_mode 'server'
    option batadv_gw_bandwidth '100000 100000'

config interface 'wan'
    option proto 'dhcp'
    option ifname 'eth0'

config interface 'lan'
    option proto 'static'
    option ipaddr '192.168.1.1'
    option netmask '255.255.255.0'

# Firewall: allow mesh -> wan
config forwarding
    option src 'mesh'
    option dest 'wan'
```

### 2. Client Node Configuration

```bash
# /etc/config/network - Client node
config interface 'mesh'
    option type 'bridge'
    option proto 'batadv'
    option mesh 'bat0'
    option batadv_gw_mode 'client'

# No WAN interface needed
```

---

## Monitoring & Debugging

### Real-time Monitoring

```bash
# Watch originator table
watch -n 2 'batctl o'

# Watch neighbours
watch -n 2 'batctl n'

# Continuous ping
batctl p <mac> -c 100 -i 0.1

# Throughput test
batctl tp <mac> -t 30
```

### Logging

```bash
# Enable debug logging
# /etc/config/network
option batadv_log_level '4'  # 0=none, 1=errors, 2=warn, 3=info, 4=debug

# View logs
logread -f | grep batman

# Or use batctl debug
batctl -d 4 -I bat0
```

### Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| No neighbours | Same mesh_id, channel, encryption | Verify all nodes identical |
| No gateway | GW mode not set | Set `gw_mode server` on gateway |
| High latency | Too many hops | Optimize topology, add nodes |
| Packet loss | Interference | Change channel, reduce TX power |
| No Internet | Firewall blocking | Check forwarding rules |

---

## Performance Tuning

### For Low Latency

```bash
# /etc/config/network
option batadv_orig_interval '500'      # 500ms (default 1000ms)
option batadv_hop_penalty '5'          # Lower penalty (default 10)
option batadv_aggregated_ogms '1'
```

### For High Throughput

```bash
# Enable network coding for lossy links
option batadv_network_coding '1'

# Increase orig interval to reduce overhead
option batadv_orig_interval '2000'

# Enable fragmentation for large MTU
option batadv_fragmentation '1'
```

### For Mobile Nodes

```bash
# Faster convergence
option batadv_orig_interval '500'
option batadv_hop_penalty '5'

# Enable BLA for wired backhaul
option batadv_bridge_loop_avoidance '1'
```

---

## Security

### Encryption

```bash
# WiFi encryption (WPA2-PSK minimum, WPA3 preferred)
config wifi-iface 'mesh0'
    option encryption 'psk2+ccmp'
    option key 'your_very_secure_password'
    # For WPA3:
    # option encryption 'sae'
    # option sae_pwe '2'
```

### Isolation

```bash
# AP isolation (prevent client-to-client at AP)
option batadv_ap_isolation '1'

# Mesh isolation (prevent mesh-to-mesh at L2)
# Not directly supported, use VLANs
```

---

## Monitoring with Grafana/Prometheus

### node_exporter + batctl exporter

```bash
# Install prometheus-node-exporter
opkg install prometheus-node-exporter-lua

# Custom batctl exporter (Python)
#!/usr/bin/env python3
import subprocess
import json

def get_batman_metrics():
    # Originators
    out = subprocess.check_output(['batctl', 'o', '-j']).decode()
    originators = json.loads(out)
    
    # Neighbours
    out = subprocess.check_output(['batctl', 'n', '-j']).decode()
    neighbours = json.loads(out)
    
    # Metrics
    metrics = {
        'batman_nodes_total': len(originators),
        'batman_neighbours_total': len(neighbours),
    }
    
    for node in originators:
        metrics[f'batman_node_tq{{mac="{node["orig"]}"}}'] = node['tq']
    
    return metrics

if __name__ == '__main__':
    print(json.dumps(get_batman_metrics()))
```

---

## Troubleshooting

### Common Issues

| Symptom | Diagnosis | Solution |
|---------|-----------|----------|
| `batctl o` empty | No mesh formation | Check mesh_id, channel, encryption match |
| High packet loss | `batctl n` shows low TQ | Reduce hop count, change channel |
| No gateway | `batctl gw` empty | Check `gw_mode server` on gateway |
| High latency | Many hops in `batctl tr` | Add more nodes, optimize topology |
| Memory leaks | `logread | grep oom` | Upgrade OpenWrt, reduce `orig_interval` |

### Debug Commands

```bash
# Kernel messages
dmesg | grep batman

# batctl debug
batctl -d 4 -I bat0

# Interface stats
cat /sys/kernel/debug/batman_adv/bat0/originators

# Network stats
cat /proc/net/dev | grep bat0

# Bridge info
brctl show bat0
```

---

## Integration with Babel/Bird

### Hybrid BATMAN-ADV + Babel

```bash
# BATMAN-ADV handles L2 mesh
# Babel runs on bat0 interface for L3 routing

# /etc/config/network
config interface 'mesh'
    option type 'bridge'
    option proto 'batadv'
    option mesh 'bat0'

# /etc/config/babeld
config interface 'bat0'
    option ifname 'bat0'
    option type 'wired'
    option hello_interval '200'
    option update_interval '6000'
```

---

## Resources

- **BATMAN-ADV Wiki**: https://www.open-mesh.org/projects/batman-adv/wiki
- **OpenWrt BATMAN-ADV**: https://openwrt.org/docs/guide-user/network/batman_adv
- **batctl Manual**: https://manpages.debian.org/testing/batctl/batctl.8.en.html
- **OpenWrt Routing Feed**: https://github.com/openwrt/routing
- **DeepWiki OpenWrt Routing**: https://deepwiki.com/openwrt/routing