# BIRD2 (OSPF/BGP) on Linux - Complete Setup Guide

## Prerequisites

### Hardware
- **Linux host** (x86, ARM, MIPS) - Raspberry Pi, x86 server, OpenWrt router
- **Multiple interfaces** for routing
- **Not for ESP32 directly** - BIRD2 is a Linux userspace daemon

### Software
- **Linux kernel 4.0+**
- **BIRD2 (v2.0+)**
- **IP forwarding enabled**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BIRD2 Architecture                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BIRD2 Daemon (User Space)                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Protocol Modules                                         │   │
│  │   ├── OSPFv2 (RFC 2328) - IPv4 Link State               │   │
│  │   ├── OSPFv3 (RFC 5340) - IPv6 Link State               │   │
│  │   ├── BGP (RFC 4271) - Path Vector                      │   │
│  │   ├── Babel (RFC 8966) - Distance Vector                │   │
│  │   ├── RIP (RFC 2453) - Distance Vector                  │   │
│  │   ├── Static Routes                                      │   │
│  │   ├── Kernel (netlink) - Route Installation             │   │
│  │   ├── Device - Interface Monitoring                     │   │
│  │   └── Pipe - Inter-table Communication                  │   │
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

---

## Installation

### Ubuntu/Debian

```bash
# Install BIRD2
apt update
apt install bird2

# Or install from source for latest version
git clone https://github.com/bird-net/bird
cd bird
./configure --prefix=/usr --sysconfdir=/etc
make
sudo make install
```

### OpenWrt

```bash
opkg update
opkg install bird2

# For specific protocols
opkg install bird2-ospf
opkg install bird2-bgp
opkg install bird2-babel
```

### From Source (Latest)

```bash
# Dependencies
apt install build-essential libncurses-dev libreadline-dev \
    libssl-dev flex bison pkg-config

# Build
git clone https://github.com/bird-net/bird
cd bird
autoreconf -i
./configure --prefix=/usr --sysconfdir=/etc/bird
make -j$(nproc)
sudo make install
```

---

## Configuration

### Basic Structure

```bird
# /etc/bird/bird.conf

# Router ID
router id 192.168.1.1;

# Logging
log "/var/log/bird.log" all;
log syslog all;

# Protocol: Device (interface monitoring)
protocol device {
    scan time 10;  # Scan interfaces every 10 seconds
}

# Protocol: Kernel (route installation)
protocol kernel {
    ipv4 {
        export all;      # Export all routes to kernel
        import none;     # Don't import from kernel
    };
    
    ipv6 {
        export all;
        import none;
    };
}

# Protocol: Static routes
protocol static {
    ipv4;
    route 10.0.0.0/24 via 192.168.1.2;
    route 192.168.2.0/24 via 192.168.1.3;
    
    ipv6;
    route fd00::/64 via fd00::1;
}
```

### OSPFv2 Configuration

```bird
protocol ospf v2 {
    ipv4 {
        import filter {
            # Accept only specific prefixes
            if net ~ [ 10.0.0.0/8+, 192.168.0.0/16+ ] then accept;
            reject;
        };
        export filter {
            # Export static and connected routes
            if source = RTS_STATIC then accept;
            if source = RTS_CONNECTED then accept;
            reject;
        };
    };
    
    # OSPF Area 0 (Backbone)
    area 0.0.0.0 {
        interface "eth0" {
            cost 10;
            type broadcast;
            hello 10;
            dead 40;
            retransmit 5;
            priority 1;
            authentication none;  # Options: none, simple "password", md5 "keyid" "key"
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
    
    # Area 1 (Remote site)
    area 0.0.0.1 {
        interface "eth1" {
            cost 50;
        };
        
        # Virtual link to backbone
        virtual_link 192.168.1.2 {
            hello 10;
            dead 40;
        };
    };
}

# OSPFv3 for IPv6
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
```

### BGP Configuration

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
    
    # IPv6 BGP
    ipv6 {
        import all;
        export filter {
            if source = RTS_STATIC then accept;
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
    
    # Route reflection (if RR)
    # route_reflector on;
    # cluster_id 1.2.3.4;
}
```

### Babel Configuration

```bird
protocol babel {
    ipv4 {
        import filter {
            if net ~ [ 10.0.0.0/8+, 192.168.0.0/16+ ] then accept;
            reject;
        };
        export filter {
            if source = RTS_STATIC then accept;
            if source = RTS_CONNECTED then accept;
            reject;
        };
    };
    
    ipv6 {
        import filter {
            if net ~ [ fd00::/8+ ] then accept;
            reject;
        };
        export all;
    };
    
    interface "eth0" {
        type wired;
        hello-interval 200;      # 2 seconds
        update-interval 6000;    # 60 seconds
    };
    
    interface "wlan0" {
        type wireless;
        hello-interval 200;
        update-interval 6000;
        rxcost-limit 9600;       # Max ETX ~37.5
    };
}
```

### Route Filtering

```bird
# Filter functions
filter customer_routes {
    # Accept customer prefixes
    if net ~ [ 10.0.0.0/8+, 192.168.0.0/16+ ] then accept;
    reject;
}

filter transit_routes {
    # Don't transit customer routes to other transit
    if net ~ [ 10.0.0.0/8+ ] then reject;
    accept;
}

filter bogon_filter {
    # Filter bogons
    if net ~ [ 0.0.0.0/8+, 10.0.0.0/8+, 127.0.0.0/8+, 
               169.254.0.0/16+, 172.16.0.0/12+, 192.168.0.0/16+,
               224.0.0.0/4+, 240.0.0.0/4+ ] then reject;
    accept;
}

# Apply filters
protocol bgp {
    ipv4 {
        import filter {
            bogon_filter;
            customer_routes;
        };
        export filter {
            bogon_filter;
            transit_routes;
        };
    };
}
```

---

## Advanced Features

### Route Maps

```bird
# Route map for policy routing
route_map SET_LOCAL_PREF {
    sequence 10 {
        match {
            community (65001:100);
        }
        action {
            local_pref = 200;
            accept;
        }
    }
    sequence 20 {
        match {
            community (65001:200);
        }
        action {
            local_pref = 100;
            accept;
        }
    }
    default {
        reject;
    }
}

protocol bgp {
    ipv4 {
        import filter {
            route_map SET_LOCAL_PREF;
        };
    };
}
```

### Multiple Routing Tables

```bird
# Define additional tables
table t_customer1;
table t_customer2;

protocol kernel {
    ipv4 {
        table t_customer1;
        export filter { if net ~ [ 10.1.0.0/16+ ] then accept; reject; };
    };
}

protocol kernel {
    ipv4 {
        table t_customer2;
        export filter { if net ~ [ 10.2.0.0/16+ ] then accept; reject; };
    };
}

# Policy routing in Linux
# ip rule add from 10.1.0.0/16 table 101
# ip route add default via 192.168.1.1 table 101
```

### Graceful Restart

```bird
protocol ospf {
    graceful_restart on;
    graceful_restart_time 120;
    
    # Helper mode (default on)
    # graceful_restart_helper on;
}

protocol bgp {
    graceful_restart on;
    graceful_restart_time 120;
    
    # For route reflector
    # graceful_restart_helper on;
}

protocol babel {
    # Babel has built-in graceful restart via sequence numbers
}
```

### RPKI/ROA Validation (BGP)

```bird
# Requires rpki-client or routinator running locally
protocol rpki {
    remote "127.0.0.1" port 3323;
    
    # Or use local cache
    # cache_dir "/var/lib/rpki";
}

protocol bgp {
    ipv4 {
        import filter {
            # Validate RPKI
            if roa_check(net, bgp_path.last) = ROA_INVALID then reject;
            if roa_check(net, bgp_path.last) = ROA_UNKNOWN then {
                # Accept but log
                accept;
            }
            accept;
        };
    };
}
```

---

## CLI Usage

```bash
# Start/stop
systemctl start bird
systemctl stop bird
systemctl restart bird

# CLI
birdc                    # IPv4 CLI
birdc6                   # IPv6 CLI

# Commands
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
birdc> show babel neighbors
birdc> configure
birdc> disable ospf
birdc> enable ospf
birdc> reload
birdc> debug all
birdc> debug { events, states, packets } on
```

### Monitoring Scripts

```bash
#!/bin/bash
# monitor_bird.sh

# Check protocol status
birdc show protocols | grep -E "(ospf|bgp|babel)" | while read line; do
    proto=$(echo $line | awk '{print $1}')
    state=$(echo $line | awk '{print $2}')
    if [ "$state" != "Up" ]; then
        echo "ALERT: $proto is $state"
    fi
done

# Check route count
routes=$(birdc show route | grep -c "^[0-9]")
echo "Routes: $routes"

# Check specific route
birdc show route for 10.0.0.5
```

---

## Integration with WireGuard

### BIRD over WireGuard

```bird
# WireGuard interface
protocol device {
    scan time 10;
}

protocol kernel {
    ipv4 {
        export all;
    };
}

# OSPF over WireGuard
protocol ospf {
    ipv4 {
        export filter {
            if source = RTS_STATIC then accept;
            reject;
        };
    };
    
    area 0.0.0.0 {
        interface "wg0" {
            cost 10;
            type point_to_point;  # WireGuard is PtP
            hello 10;
            dead 40;
            authentication none;
        };
    };
}

# BGP over WireGuard
protocol bgp {
    local as 65001;
    neighbor 10.0.0.1 as 65002;  # WireGuard peer IP
    
    ipv4 {
        import filter {
            if net ~ [ 10.0.0.0/8+ ] then accept;
            reject;
        };
        export filter {
            if source = RTS_STATIC then accept;
            reject;
        };
    };
    
    password "bgp-secret";
}
```

---

## Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| Protocol not Up | Interface down, config error | Check interface, config syntax |
| Routes not exported | Filter rejecting | Check export filters |
| Flapping routes | Link flapping, timer mismatch | Adjust hello/dead timers |
| BGP session down | AS number mismatch, auth | Verify AS numbers, passwords |
| OSPF not converging | Area mismatch, auth | Match area IDs, authentication |
| High CPU | Too many routes/peers | Filter routes, reduce peers |

### Debug Commands

```bash
# Enable debug
birdc debug all
birdc debug { events, states, packets } on

# Check specific protocol
birdc show protocols ospf1
birdc show ospf topology
birdc show ospf lsadb
birdc show bgp neighbors

# Packet capture
tcpdump -i any -n proto ospf
tcpdump -i any -n port 179
```

---

## Integration with OpenWrt

### OpenWrt BIRD2 Package

```bash
opkg update
opkg install bird2 bird2-ospf bird2-bgp bird2-babel

# Configuration in /etc/bird/bird.conf
# Start service
/etc/init.d/bird start
/etc/init.d/bird enable
```

### UCI Integration

```bash
# /etc/config/bird (OpenWrt UCI config)
config bird 'global'
    option router_id '192.168.1.1'
    option log_file '/var/log/bird.log'

config protocol 'kernel'
    option protocol 'kernel'
    option ipv4_export 'all'

config protocol 'device'
    option protocol 'device'

config protocol 'ospf'
    option protocol 'ospf'
    option router_id '192.168.1.1'
    list area '0.0.0.0'

config interface 'ospf_eth0'
    option protocol 'ospf'
    option area '0.0.0.0'
    option interface 'eth0'
    option cost '10'
```

---

## Resources

- **BIRD2**: https://bird.network.cz/
- **BIRD2 GitHub**: https://github.com/bird-net/bird
- **BIRD2 Documentation**: https://bird.network.cz/?get_doc
- **OSPF RFC**: RFC 2328, RFC 5340
- **BGP RFC**: RFC 4271
- **Babel RFC**: RFC 8966
- **OpenWrt BIRD2**: https://openwrt.org/docs/guide-user/network/bird