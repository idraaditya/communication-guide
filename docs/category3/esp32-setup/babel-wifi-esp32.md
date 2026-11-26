# Babel on ESP32-S3 WiFi - Complete Setup Guide

## Prerequisites

### Hardware
- **ESP32-S3 DevKitC-1** (or any ESP32-S3 with WiFi)
- **External antenna** (recommended for mesh)

### Software
- **ESP-IDF v5.2+** 
- **babeld** (compiled for ESP32-S3)
- **Python 3.8+**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESP32-S3 Babel Stack                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Application (IPv4/IPv6)                                        │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ babeld Daemon (User Space)                              │   │
│  │   ├── Route Table (IPv4 + IPv6)                         │   │
│  │   ├── Neighbor Table (ETX measurement)                  │   │
│  │   ├── Interface State Machine                           │   │
│  │   └── ubus Integration (OpenWrt) / CLI (ESP32)         │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ESP-IDF Network Stack (LwIP)                                   │
│           │                                                     │
│           ▼                                                     │
│  ESP32-S3 WiFi MAC (802.11n)                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Build Options

### Option 1: Pre-built babeld for ESP32-S3 (Recommended)

```bash
# Use pre-compiled babeld from OpenWrt SDK
# Or compile from source using OpenWrt toolchain

# 1. Setup OpenWrt SDK for ESP32
git clone https://github.com/openwrt/openwrt.git
cd openwrt
./scripts/feeds update -a
./scripts/feeds install -a -p routing

# 2. Configure for ESP32-S3
make menuconfig
# Target: ESP32-S3
# Target Profile: ESP32-S3 DevKitC-1
# Kernel modules: kmod-babel
# Packages: babeld

# 3. Build
make -j$(nproc)

# 4. Extract babeld binary
# Find in: bin/targets/esp32/s3/packages/babeld_*.ipk
```

### Option 2: Compile babeld with ESP-IDF (Experimental)

```bash
# 1. Add babeld as ESP-IDF component
mkdir -p components/babeld
cd components/babeld

# 2. Clone babeld source
git clone https://github.com/jech/babeld.git src

# 3. Create CMakeLists.txt
cat > CMakeLists.txt << 'EOF'
idf_component_register(
    SRCS "src/babeld.c" "src/kernel.c" "src/interface.c" "src/neighbour.c" 
         "src/message.c" "src/resend.c" "src/source.c" "src/route.c" 
         "src/configuration.c" "src/local.c" "src/util.c"
    INCLUDE_DIRS "src"
    REQUIRES esp_netif esp_wifi lwip
    PRIV_REQUIRES mbedtls
)
EOF

# 4. Modify babeld for ESP-IDF (remove Linux-specific code)
# - Replace Linux socket APIs with LwIP sockets
# - Remove Linux-specific ioctls
# - Use ESP-IDF logging
```

---

## ESP-IDF Project Setup

### 1. Create Project

```bash
cd ~/esp
idf.py create-project esp32s3_babel_mesh
cd esp32s3_babel_mesh
idf.py set-target esp32s3
```

### 2. Add babeld Component

```bash
# Copy babeld component to project
mkdir -p components
cp -r /path/to/babeld/component components/babeld
```

### 3. Configure WiFi Mesh

```c
// main/wifi_mesh.c
#include "esp_wifi.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "nvs_flash.h"

#define MESH_SSID "babel-mesh"
#define MESH_PASS "meshpassword123"
#define MESH_CHANNEL 6

static void wifi_init_mesh(void) {
    // Initialize NVS
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    // Create WiFi interface
    esp_netif_t *sta_netif = esp_netif_create_default_wifi_sta();
    esp_netif_t *ap_netif = esp_netif_create_default_wifi_ap();

    // Configure WiFi as mesh (STA + AP simultaneously)
    wifi_config_t wifi_config = {
        .sta = {
            .ssid = MESH_SSID,
            .password = MESH_PASS,
            .channel = MESH_CHANNEL,
        },
        .ap = {
            .ssid = MESH_SSID,
            .password = MESH_PASS,
            .channel = MESH_CHANNEL,
            .authmode = WIFI_AUTH_WPA2_PSK,
            .max_connection = 10,
        },
    };

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_APSTA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    
    // Enable mesh mode
    ESP_ERROR_CHECK(esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_11B | WIFI_PROTOCOL_11G | WIFI_PROTOCOL_11N));
    ESP_ERROR_CHECK(esp_wifi_set_protocol(WIFI_IF_AP, WIFI_PROTOCOL_11B | WIFI_PROTOCOL_11G | WIFI_PROTOCOL_11N));

    ESP_ERROR_CHECK(esp_wifi_start());
    
    // Wait for connection
    ESP_LOGI(TAG, "WiFi mesh started: %s", MESH_SSID);
}
```

### 4. Launch babeld

```c
// main/babel_launcher.c
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

static void start_babeld(void) {
    // Wait for IP address
    while (1) {
        esp_netif_ip_info_t ip_info;
        if (esp_netif_get_ip_info(esp_netif_get_handle_from_ifkey("WIFI_STA_DEF"), &ip_info) == ESP_OK) {
            if (ip_info.ip.addr != 0) break;
        }
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    // Launch babeld as subprocess (if compiled as binary)
    // Or integrate babeld main loop directly
    
    // Option 1: Run babeld binary
    char *argv[] = {
        "babeld",
        "-I", "wlan0",           // Interface
        "-d", "1",               // Debug level
        "-L", "/var/log/babeld.log", // Log file
        "-r", "10",              // Retransmission interval
        "-g", "5000",            // Port
        NULL
    };
    
    // Execute babeld (requires filesystem with babeld binary)
    // execv("/usr/sbin/babeld", argv);
    
    // Option 2: Integrate babeld event loop directly
    // babel_main(argc, argv);  // If babeld is linked as library
}

void app_main(void) {
    // Initialize NVS
    ESP_ERROR_CHECK(nvs_flash_init());
    
    // Initialize WiFi mesh
    wifi_init_mesh();
    
    // Start babeld
    start_babeld();
    
    // Monitor loop
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(30000));
        
        // Print babeld status via CLI or ubus
        // system("babeld -d 0 -I wlan0 -c show");
    }
}
```

---

## Configuration

### babeld Configuration File

```ini
# /etc/babeld.conf (or embedded in firmware)

# Interface configuration
interface wlan0
    type wireless
    hello-interval 200        # 2 seconds (centiseconds)
    update-interval 6000      # 60 seconds
    rxcost-limit 9600         # Max ETX ~37.5
    max-rtt-penalty 100

# Redistribute kernel routes
redistribute kernel
    metric 100

# Logging
log-level 2
log-file /var/log/babeld.log

# Security (experimental)
# auth-key 1 mysecretkey
```

### WiFi Configuration for Mesh

```c
// Optimal WiFi settings for mesh
wifi_config_t mesh_wifi_config = {
    .sta = {
        .ssid = "babel-mesh",
        .password = "securepassword123",
        .channel = 6,                    // Channel 1, 6, or 11
        .listen_interval = 3,            // DTIM intervals
    },
    .ap = {
        .ssid = "babel-mesh",
        .password = "securepassword123",
        .channel = 6,
        .authmode = WIFI_AUTH_WPA2_PSK,
        .max_connection = 10,
        .beacon_interval = 100,          // 100 TU = 102.4ms
    },
};

// Power save
esp_wifi_set_ps(WIFI_PS_MIN_MODEM);  // Modem sleep

// TX power (adjust for range vs interference)
esp_wifi_set_max_tx_power(78);  // 78 = 19.5 dBm (max for ESP32-S3)
```

---

## Monitoring & Debugging

### CLI Commands (if babeld supports CLI)

```bash
# Show routes
babeld -I wlan0 -c "show routes"

# Show neighbours
babeld -I wlan0 -c "show neighbours"

# Show interfaces
babeld -I wlan0 -c "show interfaces"

# Dump routes to file
babeld -I wlan0 -c "dump routes" > routes.txt
```

### ubus Integration (OpenWrt style)

```c
// If ubus is available on ESP32
// Call babeld ubus methods

// Get routes
ubus call babel get_routes '{"interface":"wlan0"}'

# Get neighbours
ubus call babel get_neighbours '{"interface":"wlan0"}'

# Get xroutes (external routes)
ubus call babel get_xroutes '{}'
```

### Logging

```c
// Enable ESP-IDF logging for babeld
// menuconfig → Component config → Log output → Default log verbosity → Debug

// babeld log levels:
// -d 0: Fatal only
// -d 1: Errors
// -d 2: Warnings (default)
// -d 3: Info
// -d 4: Debug
```

---

## Performance Tuning

### For Low Latency

```c
// babeld.conf
interface wlan0
    hello-interval 100        # 1 second
    update-interval 3000      # 30 seconds
    rxcost-limit 4800         # Max ETX ~18.75

// WiFi
esp_wifi_set_ps(WIFI_PS_NONE);  // Disable power save
esp_wifi_set_max_tx_power(78);  // Max power
```

### For Battery Life

```c
// babeld.conf
interface wlan0
    hello-interval 500        # 5 seconds
    update-interval 12000     # 2 minutes
    rxcost-limit 9600

// WiFi
esp_wifi_set_ps(WIFI_PS_MIN_MODEM);  // Modem sleep
esp_wifi_set_max_tx_power(50);  // 12.5 dBm
```

### For High Density

```c
// Reduce interference
// Use different channels for adjacent meshes
// Channel 1, 6, 11 for 2.4 GHz

// Limit mesh size
max-connections 20

// Use 5 GHz if available (ESP32-C6/P4)
```

---

## Testing

### Basic Connectivity Test

```bash
# 1. Flash two ESP32-S3 devices
# 2. Power on both
# 3. Check logs for babeld startup

# Expected log:
# babeld: interface wlan0 up
# babeld: neighbour fe80::xxxx:xxxx:xxxx:xxxx reachable
# babeld: route 2001:db8::/64 metric 96 via fe80::xxxx

# 3. Ping test
ping -c 5 <peer_ipv6>
ping -c 5 <peer_ipv4>
```

### Performance Test

```bash
# iperf3 throughput test
# Server: iperf3 -s
# Client: iperf3 -c <server_ip> -t 30 -P 4

# Latency test
ping -c 100 -i 0.1 <peer_ip>

# Jitter test
iperf3 -c <server_ip> -u -b 10M -t 60
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| No neighbours found | WiFi not in mesh mode | Check APSTA mode, same channel/SSID |
| Routes not converging | Hello interval too long | Reduce hello-interval |
| High packet loss | Interference | Change channel, reduce TX power |
| No IPv6 routes | IPv6 disabled | Enable IPv6 in LwIP config |
| babeld crashes | Memory corruption | Enable stack protection, check stack size |

---

## Resources

- **babeld**: https://www.irif.fr/~jch/software/babel/
- **RFC 8966**: https://datatracker.ietf.org/doc/rfc8966/
- **OpenWrt babeld**: https://openwrt.org/docs/guide-user/network/babel
- **ESP-IDF WiFi**: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/network/esp_wifi.html
- **DeepWiki OpenWrt Routing**: https://deepwiki.com/openwrt/routing