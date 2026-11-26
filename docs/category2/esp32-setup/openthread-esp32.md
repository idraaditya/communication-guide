# OpenThread on ESP32-H2/C6 - Complete Setup Guide

## Prerequisites

### Hardware Requirements
- **ESP32-H2** (IEEE 802.15.4 + BLE 5.3) - **Recommended for Thread**
- **ESP32-C6** (IEEE 802.15.4 + BLE 5.3 + WiFi 6) - **Dual-protocol**
- **External 802.15.4 radio** (if using ESP32/ESP32-S3): nRF52840, CC2652P7, EFR32MG21 as RCP

### Supported Boards
| Board | MCU | Thread Role | Notes |
|-------|-----|-------------|-------|
| **ESP32-H2 DevKit** | ESP32-H2 | FED/MED/SED/Router | Native 802.15.4 |
| **ESP32-C6 DevKit** | ESP32-C6 | FED/MED/SED/Router | Native 802.15.4 + WiFi |
| **Custom ESP32-H2** | ESP32-H2 | Any | Production |
| **ESP32 + nRF52840** | ESP32 (Host) + nRF52840 (RCP) | Any | RCP mode |
| **Raspberry Pi + nRF52840** | Linux + nRF52840 (RCP) | Border Router | OpenThread Border Router |

### Software Requirements
- **ESP-IDF v5.1+** (v5.2 recommended)
- **OpenThread** (included as ESP-IDF component)
- **Python 3.8+**
- **Git**

---

## Installation

### 1. Install ESP-IDF

```bash
# Linux/macOS
mkdir -p ~/esp
cd ~/esp
git clone -b v5.2 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32h2 esp32c6  # Or just: ./install.sh
source ./export.sh

# Verify
idf.py --version
# Should show ESP-IDF v5.2.x
```

### 2. Get OpenThread Examples

```bash
# OpenThread is included in ESP-IDF as component
# Examples are in ESP-IDF
cd ~/esp/esp-idf
ls examples/openthread/
# Output:
# ot_cli          - OpenThread CLI (minimal)
# ot_br           - Border Router (requires Linux host)
# ot_rcp          - Radio Co-Processor (for ESP32 host)
# ot_multicast    - Multicast example
# ot_srp_client   - SRP client example
# ot_coap         - CoAP example
```

---

## Building Examples

### 1. OpenThread CLI (Minimal End Device)

```bash
cd ~/esp/esp-idf/examples/openthread/ot_cli

# Set target (ESP32-H2 or ESP32-C6)
idf.py set-target esp32h2
# or
idf.py set-target esp32c6

# Configure
idf.py menuconfig
# Key configs:
# Component config → OpenThread → 
#   - Thread Device Role: [Full End Device / Minimal End Device / Sleepy End Device]
#   - Thread Network Name: "MyThreadNetwork"
#   - Thread Channel: 15 (11-26)
#   - Thread Pan ID: 0x1234
#   - Thread Extended PAN ID: 0x1234567890abcdef
#   - Thread Network Key: auto-generate or set
#   - Thread PSKc: auto-generate from passphrase
#   - Enable Thread Commissioning: YES
#   - Enable SRP Client: YES (for service registration)
#   - Enable CoAP: YES
#   - Log Level: INFO (or DEBUG for development)

# Build
idf.py build

# Flash
idf.py -p /dev/ttyUSB0 flash

# Monitor
idf.py -p /dev/ttyUSB0 monitor
```

### 2. OpenThread Border Router (ot-br-posix)

**Requires Linux host (Raspberry Pi, x86) + ESP32-H2/C6 as RCP**

```bash
# On Linux host (Raspberry Pi OS, Ubuntu, Debian)
git clone https://github.com/openthread/ot-br-posix
cd ot-br-posix

# Build with ESP32-H2/C6 RCP support
./script/setup
# Select: ESP32-H2 or ESP32-C6 as RCP

# Or manual:
mkdir build && cd build
cmake -DOTBR_OPTIONS="-DOT_RCP=ON -DOT_RCP_VENDOR=ESP32_H2" ..
make

# Flash RCP firmware to ESP32-H2/C6
# (Use pre-built or build from esp-idf/examples/openthread/ot_rcp)
cd ~/esp/esp-idf/examples/openthread/ot_rcp
idf.py set-target esp32h2
idf.py build
idf.py -p /dev/ttyUSB0 flash

# Start Border Router
cd ~/ot-br-posix/build
sudo ./otbr-agent -I wpan0 -d7 'spinel+hdlc+uart:///dev/ttyUSB0?uart-baudrate=460800'
sudo ./otbr-web -I wpan0 -p 80

# Access web UI: http://<pi-ip>:80
```

### 3. Thread Multicast Example

```bash
cd ~/esp/esp-idf/examples/openthread/ot_multicast
idf.py set-target esp32h2
idf.py menuconfig
# Enable: Multicast forwarding, MPL
idf.py build flash monitor
```

---

## Configuration Guide

### Network Dataset (Thread Network Parameters)

```c
// In menuconfig: Component config → OpenThread → Thread Network Data
// Or programmatically:

#include "openthread/dataset.h"

void SetNetworkDataset(otInstance* instance) {
    otOperationalDataset dataset;
    memset(&dataset, 0, sizeof(dataset));
    
    // Active Timestamp
    dataset.mComponents.mIsActiveTimestampPresent = true;
    dataset.mActiveTimestamp = 1234567890;  // Unix timestamp
    
    // Network Name (UTF-8, max 16 chars)
    dataset.mComponents.mIsNetworkNamePresent = true;
    strncpy(dataset.mNetworkName.m8, "MyThreadNet", OT_NETWORK_NAME_MAX_SIZE);
    
    // Extended PAN ID (8 bytes)
    dataset.mComponents.mIsExtendedPanIdPresent = true;
    uint8_t extpanid[8] = {0x12, 0x34, 0x56, 0x78, 0x90, 0xab, 0xcd, 0xef};
    memcpy(dataset.mExtendedPanId.m8, extpanid, 8);
    
    // PAN ID (2 bytes)
    dataset.mComponents.mIsPanIdPresent = true;
    dataset.mPanId = 0x1234;
    
    // Channel (11-26 for 2.4 GHz)
    dataset.mComponents.mIsChannelPresent = true;
    dataset.mChannel = 15;
    
    // Network Key (16 bytes)
    dataset.mComponents.mIsNetworkKeyPresent = true;
    uint8_t netkey[16] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                          0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff};
    memcpy(dataset.mNetworkKey.m8, netkey, 16);
    
    // PSKc (16 bytes) - derived from passphrase
    dataset.mComponents.mIsPskcPresent = true;
    uint8_t pskc[16] = {...};  // Compute from passphrase + salt
    memcpy(dataset.mPskc.m8, pskc, 16);
    
    // Security Policy
    dataset.mComponents.mIsSecurityPolicyPresent = true;
    dataset.mSecurityPolicy.mRotationTime = 3600;  // 1 hour
    dataset.mSecurityPolicy.mFlags = OT_SECURITY_POLICY_OBTAIN_NETWORK_KEY |
                                     OT_SECURITY_POLICY_NATIVE_COMMISSIONING |
                                     OT_SECURITY_POLICY_ROUTERS;
    
    // Set as active dataset
    otDatasetSetActive(instance, &dataset);
    
    // Commit to non-volatile storage
    otDatasetCommitActive(instance);
}
```

### Device Role Configuration

```c
// In menuconfig: Component config → OpenThread → Thread Device Role
// Options:
typedef enum {
    OT_DEVICE_ROLE_DISABLED     = 0,
    OT_DEVICE_ROLE_DETACHED     = 1,
    OT_DEVICE_ROLE_CHILD        = 2,   // SED/MED
    OT_DEVICE_ROLE_ROUTER       = 3,   // Router
    OT_DEVICE_ROLE_LEADER       = 4,   // Leader
} otDeviceRole;

// Programmatic role setting:
void SetDeviceRole(otInstance* instance, otDeviceRole role) {
    otThreadSetDeviceRole(instance, role);
    
    // For sleepy devices, configure poll period
    if (role == OT_DEVICE_ROLE_CHILD) {
        otLinkSetChildTimeout(instance, 300);  // 300s timeout
        otLinkSetPollPeriod(instance, 1000);   // 1 second poll
        // For CSL (Thread 1.2+):
        otLinkSetCslPeriod(instance, 1000);    // 1 second CSL period
    }
}
```

### Commissioning (DTLS + PSKc)

```c
// 1. Generate PSKc from passphrase
// PSKc = PBKDF2-HMAC-SHA256(passphrase, "Thread" + extpanid, 10000, 16)

// Example passphrase: "J01N-ME-NOW"
// PSKc (hex): 1a2b3c4d5e6f78901a2b3c4d5e6f7890

// 2. Commissioner (phone/app) uses PSKd (passphrase) to authenticate
// 3. Device receives network parameters via MGMT_ACTIVE_SET

// Enable commissioning in menuconfig:
CONFIG_OPENTHREAD_COMMISSIONER=y
CONFIG_OPENTHREAD_JOINER=y
CONFIG_OPENTHREAD_NATIVE_COMMISSIONING=y

// CLI commands:
/* 
commissioner start
commissioner joiner add * "J01N-ME-NOW" 180
// * = any joiner, 180s timeout
*/
```

### Border Router Configuration

```c
// For ESP32-C6 (WiFi + Thread) as Border Router
// Requires: ot-br-posix on Linux host OR ESP32-C6 with WiFi

// On Linux host (ot-br-posix):
// 1. Connect ESP32-H2/C6 as RCP via USB
// 2. otbr-agent creates wpan0 interface
// 3. otbr-web provides web UI

// Services provided:
// - NAT64/DNS64 (RFC 6146/6147)
// - SRP (Service Registration Protocol) - RFC 8980
// - DNS-SD / mDNS
// - Thread Network Data distribution

// Web UI: http://<border-router-ip>:80
// - Form new network
// - Join existing network
// - Commissioner UI
// - Network diagnostics
```

---

## OpenThread CLI Reference

### Basic Commands
```bash
# Network state
state                           # detached, child, router, leader
dataset                         # Show active dataset
dataset active                  # Show active dataset (detailed)
dataset pending                 # Show pending dataset

# Network management
dataset init new                # Create new network
dataset networkname "MyNet"     # Set network name
dataset extpanid 0011223344556677
dataset panid 0x1234
dataset channel 15
dataset pskc "1a2b3c4d5e6f78901a2b3c4d5e6f7890"
dataset commit active           # Commit to active
ifconfig up                     # Bring up interface
thread start                    # Start Thread stack

# Commissioner
commissioner start
commissioner joiner add * "PASSPHRASE" 180
commissioner joiner remove *

# Diagnostics
router table                    # Router table (leader only)
child table                     # Child table (router/leader)
child ipaddrs                   # Child IPv6 addresses
neighbor table                  # Neighbor table
route table                     # Route table (RPL)
ping <ipv6>                     # ICMPv6 ping
ping 2001:db8::1                # Example

# IPv6 addresses
ipaddr                          # Show all IPv6 addresses
ipaddr add <prefix> <iid>       # Add address manually

# SRP (Service Registration)
srp client enable
srp client host add "my-device"  # Register hostname
srp client service add "my-srv" "_http._tcp" 80

# CoAP
coap start
coap resource "test"            # Create resource
coap put "coap://[ff03::1]/test" "hello"  # Multicast

# Factory reset
factoryreset                    # Erase all config
```

### Advanced Commands
```bash
# Channel management
channel manager                 # Show channel manager state
channel page 0                  # Channel page 0 (2.4 GHz)
channel 15                      # Set channel

# MAC/Link
macfilter                       # MAC filter table
macfilter add <extaddr>         # Add to allowlist
macfilter enable

# Crypto
keysequence                     # Key sequence counter
keysequence rotate              # Rotate keys

# Debug
log level debug                 # Set log level
log output debug                # Output to debug
diag                            # Diagnostic mode
diag send <extaddr> <payload>   # Send raw 802.15.4
```

---

## Example Application: CoAP Sensor

### main.c
```c
#include <stdio.h>
#include "esp_log.h"
#include "openthread/instance.h"
#include "openthread/coap.h"
#include "openthread/ip6.h"
#include "openthread/thread.h"

static const char* TAG = "coap_sensor";
static otInstance* sInstance = NULL;

// Temperature sensor reading (simulated)
float ReadTemperature() {
    return 25.0 + (rand() % 100) / 100.0;
}

// CoAP Resource Handler
void TemperatureHandler(void* context, otMessage* message, 
                        const otMessageInfo* messageInfo) {
    (void)context;
    (void)messageInfo;
    
    float temp = ReadTemperature();
    char payload[32];
    snprintf(payload, sizeof(payload), "{\"temp\":%.2f}", temp);
    
    otError error = otCoapSendResponse(sInstance, message, 
                                       OT_COAP_RESPONSE_CODE_CONTENT,
                                       payload, strlen(payload));
    if (error != OT_ERROR_NONE) {
        ESP_LOGE(TAG, "CoAP response failed: %s", otThreadErrorToString(error));
    }
}

void SetupCoapServer() {
    static otCoapResource resource = {
        .mUriPath = "temperature",
        .mHandler = TemperatureHandler,
        .mContext = NULL,
        .mNext = NULL,
    };
    
    otCoapStart(sInstance, OT_DEFAULT_COAP_PORT);
    otCoapAddResource(sInstance, &resource);
    ESP_LOGI(TAG, "CoAP server started on /temperature");
}

// Periodic multicast temperature update
void SendTemperatureMulticast() {
    otMessage* message = otCoapNewMessage(sInstance, NULL);
    if (!message) return;
    
    otCoapMessageInit(message, OT_COAP_TYPE_NON_CONFIRMABLE, OT_COAP_CODE_PUT);
    otCoapMessageGenerateToken(message, 2);
    otCoapMessageAppendUriPathOptions(message, "sensors/temperature");
    otCoapMessageSetContentFormat(message, OT_COAP_OPTION_CONTENT_FORMAT_JSON);
    
    float temp = ReadTemperature();
    char payload[32];
    snprintf(payload, sizeof(payload), "{\"temp\":%.2f,\"unit\":\"C\"}", temp);
    otMessageAppend(message, payload, strlen(payload));
    
    otMessageInfo messageInfo = {0};
    messageInfo.mPeerPort = OT_DEFAULT_COAP_PORT;
    // Multicast to all Thread nodes (MPL)
    otIp6AddressFromString("ff03::1", &messageInfo.mPeerAddr);  // All Thread nodes
    
    otError error = otCoapSendRequest(sInstance, message, &messageInfo, NULL, NULL);
    if (error != OT_ERROR_NONE) {
        ESP_LOGE(TAG, "Multicast send failed: %s", otThreadErrorToString(error));
        otMessageFree(message);
    }
}

void app_main() {
    // Initialize ESP-IDF
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    
    // Initialize OpenThread
    esp_openthread_platform_config_t config = {
        .radio_config = ESP_OPENTHREAD_DEFAULT_RADIO_CONFIG(),
        .host_config = ESP_OPENTHREAD_DEFAULT_HOST_CONFIG(),
        .port_config = ESP_OPENTHREAD_DEFAULT_PORT_CONFIG(),
    };
    ESP_ERROR_CHECK(esp_openthread_init(&config));
    
    sInstance = esp_openthread_get_instance();
    
    // Wait for Thread to start (attach to network)
    while (otThreadGetDeviceRole(sInstance) == OT_DEVICE_ROLE_DETACHED) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    ESP_LOGI(TAG, "Thread attached, role: %d", otThreadGetDeviceRole(sInstance));
    
    // Setup CoAP
    SetupCoapServer();
    
    // Main loop
    while (1) {
        SendTemperatureMulticast();
        vTaskDelay(pdMS_TO_TICKS(30000));  // Every 30 seconds
    }
}
```

### CMakeLists.txt
```cmake
idf_component_register(SRCS "main.c"
                       INCLUDE_DIRS "."
                       REQUIRES openthread esp_openthread)
```

---

## Debugging & Monitoring

### Serial Logs
```bash
# In menuconfig: Component config → OpenThread → Log Level
CONFIG_OPENTHREAD_LOG_LEVEL_DEBUG=y   # Verbose
CONFIG_OPENTHREAD_LOG_LEVEL_INFO=y    # Normal

# Monitor
idf.py -p /dev/ttyUSB0 monitor
```

### Key Log Messages
```
I (1234) ot: [INFO] Thread state: CHILD -> ROUTER
I (1234) ot: [INFO] RPL: DIO sent, rank=256
I (1234) ot: [INFO] MLE: Link established with neighbor 0x1234
I (1234) ot: [INFO] Commissioner: Joiner added
I (1234) ot: [INFO] SRP: Service registered: _http._tcp
```

### Network Diagnostics
```bash
# CLI diagnostics
diag                            # Enter diagnostic mode
diag send <extaddr> "hello"     # Send raw 802.15.4
diag stats                      # Radio stats
diag channel 15                 # Set channel for diag

# Radio stats
> diag stats
Received: 1234
Sent: 567
RX Errors: 2
TX Errors: 0
CCA Failures: 10
```

### Packet Capture (Wireshark)
```bash
# 1. Enable DLT_IEEE802_15_4 in Wireshark
# 2. Capture on Linux host with RCP:
sudo tcpdump -i wpan0 -w thread.pcap
# 3. Or use OpenThread sniffer:
cd ~/ot-br-posix
./script/sniffer /dev/ttyUSB0 15  # Channel 15
```

---

## Performance Tuning

### For Battery-Powered Devices (SED)
```c
// menuconfig:
CONFIG_OPENTHREAD_CHILD_TIMEOUT=300      // 5 min timeout
CONFIG_OPENTHREAD_POLL_PERIOD=1000       // 1s poll interval
CONFIG_OPENTHREAD_CSL_PERIOD=1000        // 1s CSL period (Thread 1.2+)
CONFIG_OPENTHREAD_CSL_TIMEOUT=300        // CSL timeout

// Advanced: Reduce RX window
// otPlatRadioSetCslPeriod(), otPlatRadioSetCslTimeout()
```

### For High Throughput
```c
// Increase buffer sizes
CONFIG_OPENTHREAD_MLE_MAX_CHILDREN=20
CONFIG_OPENTHREAD_IP6_MAX_NEIGHBORS=32
CONFIG_OPENTHREAD_IP6_MAX_ROUTE_ENTRIES=64
CONFIG_OPENTHREAD_COAP_MAX_RESOURCES=10
```

### For Large Networks
```c
// Router capacity
CONFIG_OPENTHREAD_MAX_ROUTER_ID=32
CONFIG_OPENTHREAD_ROUTER_UPGRADE_THRESHOLD=16
CONFIG_OPENTHREAD_ROUTER_DOWNGRADE_THRESHOLD=8
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `state` stuck at `detached` | No network dataset | Set dataset, `dataset commit active` |
| Can't join network | Wrong PSKc/Channel/PANID | Match all parameters exactly |
| No IPv6 address | Not attached | Wait for `thread start` completion |
| Border Router no NAT64 | otbr-agent not running | Start `otbr-agent` with `-d7` |
| SRP not working | SRP client disabled | Enable `CONFIG_OPENTHREAD_SRP_CLIENT` |
| High packet loss | Channel interference | Change channel (11-26), scan first |
| Device not sleeping | Wrong role config | Set `CHILD` role, configure poll/CSL |

---

## Resources

- **OpenThread Docs**: https://openthread.io/guides
- **Thread Spec**: https://www.threadgroup.org/
- **Matter + Thread**: https://csa-iot.org/all-solutions/matter/
- **ESP-Thread**: https://github.com/espressif/esp-thread
- **ot-br-posix**: https://github.com/openthread/ot-br-posix
- **DeepWiki**: https://deepwiki.com/openthread/openthread
- **Discord**: https://discord.gg/openthread