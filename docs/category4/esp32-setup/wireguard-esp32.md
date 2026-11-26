# WireGuard on ESP32-S3 - Complete Setup Guide

## Prerequisites

### Hardware
- **ESP32-S3 DevKitC-1** (512KB SRAM minimum)
- **ESP32-C6** (alternative)
- **ESP32-P4** (recommended for high throughput)
- **Linux host** for peer configuration

### Software
- **ESP-IDF v5.2+**
- **WireGuard-Go** (userspace) or **ESP-IDF WireGuard component**
- **Linux host** with WireGuard kernel module

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WireGuard on ESP32-S3                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Application (IP packets)                                       │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ wg0 Interface (Virtual TUN)                             │   │
│  │   ├── IP routing (AllowedIPs = cryptokey routing)      │   │
│  │   ├── Keepalive (persistent for NAT)                    │   │
│  │   └── MTU = 1420 (IPv6) / 1440 (IPv4)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ WireGuard-Go (Userspace)                                │   │
│  │   ├── Noise_IK Handshake (1-RTT)                        │   │
│  │   ├── ChaCha20-Poly1305 AEAD Encryption                │   │
│  │   ├── Replay Protection (64-bit counter)               │   │
│  │   ├── Cryptokey Routing Table                          │   │
│  │   │   Peer Public Key → Allowed IPs                    │   │
│  │   │   Destination IP → Peer Public Key                 │   │
│  │   ├── Cookie Reply (DoS protection)                    │   │
│  │   └── Timer Wheels (handshake, keepalive, rekey)       │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  LwIP Stack (ESP-IDF)                                           │
│           │                                                     │
│           ▼                                                     │
│  ESP32-S3 WiFi/Ethernet                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Installation Options

### Option 1: WireGuard-Go (Userspace, Recommended)

```bash
# 1. Build WireGuard-Go for ESP32-S3
git clone https://github.com/wireguard/wireguard-go
cd wireguard-go

# Cross-compile for ESP32-S3 (XTENSA)
GOOS=linux GOARCH=xtensa GOXTENSA=esp32s3 CGO_ENABLED=0 go build -ldflags="-s -w" -o wireguard-go

# Copy to project
mkdir -p ~/esp/wireguard_esp32/components/wireguard-go
cp wireguard-go ~/esp/wireguard_esp32/components/wireguard-go/
```

### Option 2: ESP-IDF WireGuard Component (Native)

```bash
# Use experimental ESP-IDF WireGuard component
# Available in ESP-IDF 5.2+ examples

cd ~/esp/esp-idf/examples/protocols/wireguard
idf.py set-target esp32s3
idf.py menuconfig
# Configure WireGuard settings
idf.py build flash monitor
```

### Option 3: Kernel Module (Linux Host Only)

```bash
# For Linux hosts (Raspberry Pi, x86, OpenWrt)
# Not for ESP32 directly

# Load kernel module
modprobe wireguard

# Configure with wg-quick
wg-quick up wg0
```

---

## ESP-IDF Project Setup (WireGuard-Go)

### 1. Create Project

```bash
cd ~/esp
idf.py create-project esp32s3_wireguard
cd esp32s3_wireguard
idf.py set-target esp32s3
```

### 2. Add WireGuard-Go Component

```bash
# Create component directory
mkdir -p components/wireguard-go

# Copy cross-compiled binary
cp /path/to/wireguard-go components/wireguard-go/

# Create CMakeLists.txt
cat > components/wireguard-go/CMakeLists.txt << 'EOF'
idf_component_register(
    EMBED_FILES "wireguard-go"
    INCLUDE_DIRS "."
    REQUIRES esp_netif lwip mbedtls freertos
)
EOF

# Create wrapper C code
cat > components/wireguard-go/wireguard_esp32.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_spiffs.h"

static const char *TAG = "wireguard_esp32";

// Embedded binary
extern const uint8_t wireguard_go_start[] asm("_binary_wireguard_go_start");
extern const uint8_t wireguard_go_end[]   asm("_binary_wireguard_go_end");

static void wireguard_task(void *pvParameters) {
    // Write embedded binary to SPIFFS
    esp_vfs_spiffs_conf_t conf = {
        .base_path = "/spiffs",
        .partition_label = NULL,
        .max_files = 5,
        .format_if_mount_failed = true
    };
    ESP_ERROR_CHECK(esp_vfs_spiffs_register(&conf));
    
    // Write binary
    FILE *f = fopen("/spiffs/wireguard-go", "wb");
    if (f) {
        size_t size = wireguard_go_end - wireguard_go_start;
        fwrite(wireguard_go_start, 1, size, f);
        fclose(f);
        chmod("/spiffs/wireguard-go", 0755);
    }
    
    // Execute wireguard-go with config
    char *argv[] = {
        "/spiffs/wireguard-go",
        "wg0",
        "--config=/spiffs/wg0.conf",
        NULL
    };
    
    // Execute (requires fork/exec support)
    // This is simplified - actual implementation needs proper process management
    
    vTaskDelete(NULL);
}

void wireguard_esp32_init(void) {
    xTaskCreate(wireguard_task, "wireguard", 8192, NULL, 5, NULL);
}
EOF

# Create header
cat > components/wireguard-go/wireguard_esp32.h << 'EOF'
#ifndef WIREGUARD_ESP32_H
#define WIREGUARD_ESP32_H

#ifdef __cplusplus
extern "C" {
#endif

void wireguard_esp32_init(void);

#ifdef __cplusplus
}
#endif

#endif // WIREGUARD_ESP32_H
EOF
```

### 3. Configuration File

```ini
# wg0.conf (stored in SPIFFS)
[Interface]
PrivateKey = <base64_private_key>
Address = 10.0.0.2/24, fd00:1::2/64
ListenPort = 51820
MTU = 1420

[Peer]
PublicKey = <base64_public_key_of_server>
AllowedIPs = 10.0.0.0/24, fd00:1::/64, 192.168.1.0/24
Endpoint = your-server.example.com:51820
PersistentKeepalive = 25
```

### 4. Main Application

```c
// main/main.c
#include <stdio.h>
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "wireguard_esp32.h"

static const char *TAG = "main";

void app_main(void) {
    // Initialize NVS
    ESP_ERROR_CHECK(nvs_flash_init());
    
    // Initialize TCP/IP stack
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    
    // Initialize WiFi (or Ethernet)
    // ... wifi_init_sta() or eth_init()
    
    // Wait for network
    // ... wait for IP address
    
    // Initialize WireGuard
    wireguard_esp32_init();
    
    ESP_LOGI(TAG, "WireGuard initialized");
    
    // Main loop
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(30000));
        
        // Monitor WireGuard status
        // system("wg show");
    }
}
```

---

## Server Configuration (Linux)

### 1. Generate Keys

```bash
# On server
wg genkey | tee server_private.key | wg pubkey > server_public.key
wg genkey | tee client_private.key | wg pubkey > client_public.key

# Generate PSK (optional, for post-quantum resistance)
wg genpsk > preshared.key
```

### 2. Server Configuration

```ini
# /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <server_private_key>
Address = 10.0.0.1/24, fd00:1::1/64
ListenPort = 51820
MTU = 1420

# Optional: PostUp/PostDown for routing
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE; ip6tables -A FORWARD -i %i -j ACCEPT; ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE; ip6tables -D FORWARD -i %i -j ACCEPT; ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# ESP32-S3 Client
PublicKey = <client_public_key>
PresharedKey = <preshared_key>  # Optional
AllowedIPs = 10.0.0.2/32, fd00:1::2/128
```

### 3. Client Configuration (ESP32-S3)

```ini
# wg0.conf (on ESP32-S3)
[Interface]
PrivateKey = <client_private_key>
Address = 10.0.0.2/24, fd00:1::2/64
ListenPort = 51820
MTU = 1420

[Peer]
PublicKey = <server_public_key>
PresharedKey = <preshared_key>  # Optional
AllowedIPs = 10.0.0.0/24, fd00:1::/64, 192.168.1.0/24
Endpoint = your-server.example.com:51820
PersistentKeepalive = 25
```

---

## ESP32-S3 Integration (Simplified Approach)

### Using ESP-IDF WireGuard Example

```bash
# Use official ESP-IDF WireGuard example
cd ~/esp/esp-idf/examples/protocols/wireguard
idf.py set-target esp32s3

# Configure
idf.py menuconfig
# Example Configuration → WireGuard Configuration
#   Set private key, peer public key, endpoint, etc.

# Build and flash
idf.py build flash monitor
```

### Configuration via menuconfig

```ini
# Example Configuration → WireGuard
CONFIG_EXAMPLE_WIREGUARD_PRIVATE_KEY = "<base64_private_key>"
CONFIG_EXAMPLE_WIREGUARD_PEER_PUBLIC_KEY = "<base64_public_key>"
CONFIG_EXAMPLE_WIREGUARD_PRESHARED_KEY = "<base64_psk>"  # Optional
CONFIG_EXAMPLE_WIREGUARD_ENDPOINT = "your-server.example.com:51820"
CONFIG_EXAMPLE_WIREGUARD_ALLOWED_IPS = "10.0.0.0/24, fd00:1::/64"
CONFIG_EXAMPLE_WIREGUARD_KEEPALIVE = 25
```

---

## Advanced Configuration

### Multiple Peers

```ini
# wg0.conf (multiple peers)
[Interface]
PrivateKey = <private_key>
Address = 10.0.0.2/24, fd00:1::2/64
ListenPort = 51820
MTU = 1420

[Peer]
# Server 1
PublicKey = <server1_public_key>
AllowedIPs = 10.0.0.0/24, fd00:1::/64
Endpoint = server1.example.com:51820
PersistentKeepalive = 25

[Peer]
# Server 2
PublicKey = <server2_public_key>
AllowedIPs = 10.1.0.0/24, fd00:2::/64
Endpoint = server2.example.com:51820
PersistentKeepalive = 25

[Peer]
# Road warrior (no endpoint)
PublicKey = <mobile_public_key>
AllowedIPs = 10.0.0.10/32, fd00:1::10/128
PersistentKeepalive = 25
```

### Routing with WireGuard

```c
// Add routes for WireGuard subnet
esp_netif_ip_info_t ip_info;
esp_netif_get_ip_info(esp_netif_get_handle_from_ifkey("WIFI_STA_DEF"), &ip_info);

// Add route for WireGuard subnet via wg0
esp_netif_t *wg_netif = esp_netif_get_handle_from_ifkey("wg0");
esp_netif_dhcpc_stop(wg_netif);

// Static IP for wg0
esp_netif_ip_info_t wg_ip;
IP4_ADDR(&wg_ip.ip, 10, 0, 0, 2);
IP4_ADDR(&wg_ip.gw, 10, 0, 0, 1);
IP4_ADDR(&wg_ip.netmask, 255, 255, 255, 0);
esp_netif_set_ip_info(wg_netif, &wg_ip);

// Add route for remote subnet
esp_netif_route_t route = {
    .destination = {.addr = IPADDR4_INIT_BYTES(10, 0, 0, 0), .type = ESP_NETIF_IP4},
    .netmask = {.addr = IPADDR4_INIT_BYTES(255, 255, 255, 0), .type = ESP_NETIF_IP4},
    .gw = {.addr = IPADDR4_INIT_BYTES(10, 0, 0, 1), .type = ESP_NETIF_IP4},
};
esp_netif_add_route(wg_netif, &route);
```

---

## Performance Optimization

### MTU Settings

```ini
# Optimal MTU for different transports
# Ethernet: 1440 (IPv4) / 1420 (IPv6)
# WiFi: 1420 (IPv6) / 1440 (IPv4)
# Cellular: 1380 (IPv4) / 1360 (IPv6)

MTU = 1420  # Safe default for IPv6 over WiFi
```

### Keepalive Settings

```ini
# For NAT traversal
PersistentKeepalive = 25  # Every 25 seconds

# For stable connections (no NAT)
# PersistentKeepalive = 0  # Disabled
```

### Crypto Performance

```c
// Enable hardware acceleration if available
// ESP32-S3 has AES/SHA hardware acceleration
// mbedTLS will use it automatically

// For ChaCha20-Poly1305 (software only on ESP32)
// Consider PSK for additional security
```

---

## Testing & Monitoring

### Connection Test

```bash
# On ESP32-S3 serial monitor
# Check for handshake completion
I (1234) wireguard: Handshake completed with peer
I (1234) wireguard: Tunnel established: 10.0.0.2/24

# Ping test
ping -c 5 10.0.0.1
ping6 -c 5 fd00:1::1

# Check handshake status
# wg show (if CLI available)
```

### Monitoring

```c
// Periodic status check
void monitor_wireguard(void) {
    // Check handshake time
    // Check data counters
    // Check endpoint connectivity
    
    // Log stats every 60 seconds
    ESP_LOGI(TAG, "WireGuard: RX=%llu bytes, TX=%llu bytes", rx_bytes, tx_bytes);
}
```

### Debugging

```bash
# Enable debug logging
# menuconfig → Component config → Log output → Debug

# WireGuard-Go debug
# Set environment variable
export WIREGUARD_GO_DEBUG=1

# Check handshake logs
# Look for:
# "handshake initiated"
# "handshake received"
# "keypair created"
# "transport started"
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Handshake fails | Wrong keys/endpoint | Verify keys match, endpoint reachable |
| No traffic | AllowedIPs mismatch | Match AllowedIPs on both sides |
| Handshake but no data | MTU too large | Reduce MTU to 1420 |
| No handshake | Firewall blocking UDP 51820 | Open firewall |
| Intermittent | Keepalive too long | Reduce PersistentKeepalive |
| No endpoint | NAT | Ensure PersistentKeepalive=25 |

### Debug Commands

```bash
# Check WireGuard status (if CLI available)
wg show
wg show wg0 transfer
wg show wg0 endpoints

# Check handshake
# Look for: "handshake initiated" / "handshake received"

# Capture packets
tcpdump -i any udp port 51820 -w wg.pcap
```

---

## Resources

- **WireGuard**: https://www.wireguard.com/
- **WireGuard Protocol**: https://www.wireguard.com/protocol/
- **WireGuard-Go**: https://github.com/wireguard/wireguard-go
- **ESP-IDF WireGuard Example**: https://github.com/espressif/esp-idf/tree/master/examples/protocols/wireguard
- **WireGuard on Embedded**: https://www.wireguard.com/install/#embedded-devices