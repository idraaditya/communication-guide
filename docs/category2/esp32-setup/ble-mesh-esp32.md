# BLE Mesh on ESP32/ESP32-S3 - Complete Setup Guide

## Prerequisites

### Hardware Requirements
- **ESP32** (BLE 4.2) - Basic BLE Mesh
- **ESP32-S3** (BLE 5.3) - **Recommended** (longer range, 2M PHY, better coexistence)
- **ESP32-C3/H2** (BLE 5.3) - Also supported

### Supported Boards
| Board | MCU | BLE Version | Notes |
|-------|-----|-------------|-------|
| **ESP32 DevKitC** | ESP32 | 4.2 | Basic support |
| **ESP32-S3 DevKitC-1** | ESP32-S3 | 5.3 | **Recommended** |
| **ESP32-C3 DevKit** | ESP32-C3 | 5.3 | Low cost |
| **M5Stack CoreS3** | ESP32-S3 | 5.3 | With display |
| **Custom ESP32-S3** | ESP32-S3 | 5.3 | Production |

### Software Requirements
- **ESP-IDF v5.0+** (v5.2 recommended)
- **ESP-BLE-Mesh** (included in ESP-IDF)
- **Python 3.8+**
- **Git**
- **Smartphone** with nRF Mesh / ESP-BLE-Mesh app for provisioning

---

## Installation

### 1. Install ESP-IDF

```bash
mkdir -p ~/esp
cd ~/esp
git clone -b v5.2 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32s3 esp32 esp32c3
source ./export.sh

# Verify
idf.py --version
```

### 2. Get ESP-BLE-Mesh Examples

```bash
cd ~/esp/esp-idf
ls examples/bluetooth/ble_mesh/
# Output:
# ble_mesh_node          - Basic node (Generic OnOff Server)
# ble_mesh_provisioner   - Provisioner (configures network)
# ble_mesh_client_model  - Client model (controls servers)
# ble_mesh_sensor        - Sensor Server
# ble_mesh_light         - Light Lightness/CTL/HSL Server
# ble_mesh_time_scene    - Time/Scene Server
# ble_mesh_fast_prov     - Fast Provisioning
# ble_mesh_gatt_proxy    - GATT Proxy (phone connectivity)
# ble_mesh_friend        - Friend Node (for LPN)
# ble_mesh_lpn           - Low Power Node
# ble_mesh_ota           - OTA Update
# ble_mesh_multi_net     - Multiple Networks
# ble_mesh_prov_own      - Provisioning with static OOB
```

---

## Building Examples

### 1. Basic Node (Generic OnOff Server)

```bash
cd ~/esp/esp-idf/examples/bluetooth/ble_mesh/ble_mesh_node

# Set target
idf.py set-target esp32s3
# or
idf.py set-target esp32
# or
idf.py set-target esp32c3

# Configure
idf.py menuconfig
# Key configs:
# Component config → ESP BLE Mesh →
#   - BLE Mesh Node Features:
#     * Enable Relay: YES (relays messages)
#     * Enable Friend: NO (unless mains powered)
#     * Enable Low Power: NO (unless battery)
#     * Enable GATT Proxy: YES (phone connectivity)
#   - BLE Mesh Provisioning:
#     * Provisioning Bearer: [PB-ADV / PB-GATT / Both]
#     * Static OOB: NO (or YES for production)
#     * Output OOB: [Blink / Beep / Number / None]
#     * Input OOB: [Push / Twist / Number / None]
#   - BLE Mesh Network:
#     * Network Transmit Count: 2
#     * Network Transmit Interval: 20ms
#     * Relay Retransmit Count: 2
#     * Relay Retransmit Interval: 20ms
#   - BLE Mesh Models:
#     * Generic OnOff Server: YES
#     * Generic Level Server: YES
#     * Configuration Server: YES (required)
#     * Health Server: YES (required)
#   - BLE Mesh Log Level: INFO

# Build
idf.py build

# Flash
idf.py -p /dev/ttyUSB0 flash

# Monitor
idf.py -p /dev/ttyUSB0 monitor
```

### 2. Provisioner (Network Configurator)

```bash
cd ~/esp/esp-idf/examples/bluetooth/ble_mesh/ble_mesh_provisioner
idf.py set-target esp32s3
idf.py menuconfig
# Enable: Provisioner role, GATT Proxy, PB-GATT
# Provisioner can provision up to 32767 nodes
idf.py build flash monitor
```

### 3. Light Device (Light Lightness/CTL/HSL)

```bash
cd ~/esp/esp-idf/examples/bluetooth/ble_mesh/ble_mesh_light
idf.py set-target esp32s3
idf.py menuconfig
# Models:
#   - Light Lightness Server: YES
#   - Light CTL Server: YES (color temperature)
#   - Light HSL Server: YES (hue/saturation/lightness)
#   - Light xyL Server: YES (CIE 1931)
#   - Light LC Server: YES (light control)
# PWM GPIO: Configure for your LED driver
idf.py build flash monitor
```

### 4. Sensor Node

```bash
cd ~/esp/esp-idf/examples/bluetooth/ble_mesh/ble_mesh_sensor
idf.py set-target esp32s3
idf.py menuconfig
# Sensor Types:
#   - Temperature: YES
#   - Humidity: YES
#   - Pressure: YES
#   - Ambient Light: YES
#   - Motion: YES
#   - CO2: YES
# Reporting: Configure cadence (periodic) or trigger (threshold)
idf.py build flash monitor
```

### 5. Low Power Node (LPN)

```bash
cd ~/esp/esp-idf/examples/bluetooth/ble_mesh/ble_mesh_lpn
idf.py set-target esp32s3
idf.py menuconfig
# Low Power Features:
#   - Enable Low Power: YES
#   - Friend Required: YES (needs Friend node)
#   - Poll Interval: 1000ms (1 second)
#   - Poll Retry: 3
#   - Receive Window: 200ms
#   - Subscription List: Add group addresses
# Power: ~10-50 µA average (with 1s poll)
idf.py build flash monitor
```

### 6. Friend Node (for LPN)

```bash
cd ~/esp/esp-idf/examples/bluetooth/ble_mesh/ble_mesh_friend
idf.py set-target esp32s3
idf.py menuconfig
# Friend Features:
#   - Enable Friend: YES
#   - Friend Queue Size: 16 (messages cached)
#   - Subscription List Size: 8 (group addresses)
#   - Receive Window: 200ms
#   - Poll Timeout: 300s
# Must be mains powered
idf.py build flash monitor
```

### 7. GATT Proxy (Phone Connectivity)

```bash
cd ~/esp/esp-idf/examples/bluetooth/ble_mesh/ble_mesh_gatt_proxy
idf.py set-target esp32s3
idf.py menuconfig
# Proxy Features:
#   - Enable GATT Proxy: YES
#   - Proxy Filter Type: [Whitelist / Blacklist]
#   - Proxy Filter Entries: 16
# Allows phone apps (nRF Mesh) to connect via GATT
idf.py build flash monitor
```

---

## Configuration Guide

### Network Provisioning

```c
// Provisioning creates:
// 1. NetKey (Network Key) - encrypts network layer
// 2. AppKey (Application Key) - encrypts upper transport
// 3. IV Index - replay protection
// 4. Unicast Address - assigned to each element
// 5. Group Addresses - for multicast
// 6. Virtual Addresses - for label-based addressing

// Provisioning Methods:
// 1. PB-ADV (Provisioning Bearer - Advertising)
//    - No GATT connection needed
//    - Works with unprovisioned device beacon
// 2. PB-GATT (Provisioning Bearer - GATT)
//    - Requires GATT connection
//    - Faster, more reliable

// Provisioning Authentication:
// - No OOB: No authentication (development only)
// - Static OOB: Pre-shared 128-bit key (production)
// - Output OOB: Device outputs (blink, beep, number)
// - Input OOB: User inputs (push, twist, number)
```

### Node Composition Data

```c
// Device composition (sent during provisioning)
typedef struct {
    uint16_t cid;           // Company ID (0x02E5 for Espressif)
    uint16_t pid;           // Product ID
    uint16_t vid;           // Version ID
    uint16_t crpl;          // CRPL
    uint16_t features;      // Relay, Friend, Proxy, LPN
    uint8_t  element_count; // Number of elements
    struct {
        uint16_t loc;       // Location descriptor
        uint16_t model_count;
        uint16_t models[];  // Model IDs (SIG + Vendor)
    } elements[];
} esp_ble_mesh_comp_t;

// Example: Light with 3 elements (Lightness, CTL, HSL)
esp_ble_mesh_comp_t comp = {
    .cid = 0x02E5,
    .pid = 0x0001,
    .vid = 0x0001,
    .features = ESP_BLE_MESH_FEAT_RELAY | ESP_BLE_MESH_FEAT_PROXY,
    .element_count = 3,
    .elements = {
        // Element 0: Main light
        {.loc = 0, .model_count = 3, .models = {ESP_BLE_MESH_MODEL_ID_GEN_ONOFF_SRV,
                                                ESP_BLE_MESH_MODEL_ID_LIGHT_LIGHTNESS_SRV,
                                                ESP_BLE_MESH_MODEL_ID_LIGHT_CTL_SRV}},
        // Element 1: Secondary light
        {.loc = 0, .model_count = 1, .models = {ESP_BLE_MESH_MODEL_ID_GEN_ONOFF_SRV}},
        // Element 2: Sensor
        {.loc = 0, .model_count = 1, .models = {ESP_BLE_MESH_MODEL_ID_SENSOR_SRV}},
    },
};
```

### Generic OnOff Server Model

```c
#include "esp_ble_mesh_defs.h"
#include "esp_ble_mesh_generic_model_api.h"

// OnOff State
typedef struct {
    uint8_t onoff;          // 0=Off, 1=On
    uint8_t target_onoff;   // Target (for transitions)
    uint8_t transition_time; // Transition time (0-63, 0=none)
    uint8_t delay;          // Delay (0-63, 5ms steps)
} esp_ble_mesh_gen_onoff_state_t;

// OnOff Server Callback
static void gen_onoff_server_cb(esp_ble_mesh_generic_server_cb_event_t event,
                                esp_ble_mesh_generic_server_cb_param_t* param) {
    switch (event) {
        case ESP_BLE_MESH_GENERIC_SERVER_STATE_CHANGE_EVT:
            if (param->state_change.model_id == ESP_BLE_MESH_MODEL_ID_GEN_ONOFF_SRV) {
                uint8_t new_state = param->state_change.state.onoff.onoff;
                ESP_LOGI(TAG, "OnOff changed: %d", new_state);
                // Control GPIO/LED
                gpio_set_level(LED_GPIO, new_state);
            }
            break;
        case ESP_BLE_MESH_GENERIC_SERVER_RECV_GET_MSG_EVT:
            // Client requested state
            break;
        case ESP_BLE_MESH_GENERIC_SERVER_RECV_SET_MSG_EVT:
            // Client sent Set command
            break;
    }
}

// Register Model
esp_ble_mesh_model_t models[] = {
    ESP_BLE_MESH_MODEL_GEN_ONOFF_SRV(&onoff_server_cb, &onoff_state),
    ESP_BLE_MESH_MODEL_GEN_LEVEL_SRV(&level_server_cb, &level_state),
    ESP_BLE_MESH_MODEL_CFG_SRV(&config_server_cb),
    ESP_BLE_MESH_MODEL_HEALTH_SRV(&health_server_cb, &health_state),
};
```

### Client Model (Control Other Nodes)

```c
// Generic OnOff Client
static void gen_onoff_client_cb(esp_ble_mesh_generic_client_cb_event_t event,
                                esp_ble_mesh_generic_client_cb_param_t* param) {
    switch (event) {
        case ESP_BLE_MESH_GENERIC_CLIENT_GET_STATE_EVT:
            ESP_LOGI(TAG, "OnOff Get: src=0x%04x, onoff=%d", 
                     param->params->status.addr, param->status.onoff);
            break;
        case ESP_BLE_MESH_GENERIC_CLIENT_SET_STATE_EVT:
            ESP_LOGI(TAG, "OnOff Set: src=0x%04x, status=%d", 
                     param->params->status.addr, param->status.status);
            break;
        case ESP_BLE_MESH_GENERIC_CLIENT_PUBLISH_EVT:
            ESP_LOGI(TAG, "OnOff Publish received");
            break;
    }
}

// Send OnOff Set (Turn On)
void TurnOnLight(uint16_t dst_addr) {
    esp_ble_mesh_generic_client_set_state_t set = {
        .model_id = ESP_BLE_MESH_MODEL_ID_GEN_ONOFF_CLI,
        .opcode = ESP_BLE_MESH_MODEL_OP_GEN_ONOFF_SET,
        .ctx = {
            .addr = dst_addr,
            .app_idx = 0,  // AppKey index
            .send_ttl = 3,
            .send_relay = true,
        },
        .onoff = {
            .onoff = 1,
            .tid = 0,
            .trans_time = 0,
            .delay = 0,
        },
    };
    esp_ble_mesh_generic_client_set_state(&set);
}

// Send OnOff Get
void GetLightState(uint16_t dst_addr) {
    esp_ble_mesh_generic_client_get_state_t get = {
        .model_id = ESP_BLE_MESH_MODEL_ID_GEN_ONOFF_CLI,
        .opcode = ESP_BLE_MESH_MODEL_OP_GEN_ONOFF_GET,
        .ctx = {
            .addr = dst_addr,
            .app_idx = 0,
            .send_ttl = 3,
            .send_relay = true,
        },
    };
    esp_ble_mesh_generic_client_get_state(&get);
}
```

### Group Addressing (Multicast)

```c
// Group addresses: 0xC000 - 0xFEFF (16-bit)
// Virtual addresses: 128-bit label UUID

// Add node to group
esp_ble_mesh_cfg_client_add_group_addr(0xC000, node_addr, element_addr);

// Send to group
void TurnOnGroup(uint16_t group_addr) {
    esp_ble_mesh_generic_client_set_state_t set = {
        .model_id = ESP_BLE_MESH_MODEL_ID_GEN_ONOFF_CLI,
        .opcode = ESP_BLE_MESH_MODEL_OP_GEN_ONOFF_SET,
        .ctx = {
            .addr = group_addr,        // Group address
            .app_idx = 0,
            .send_ttl = 3,
            .send_relay = true,
        },
        .onoff = {.onoff = 1, .tid = 0, .trans_time = 0, .delay = 0},
    };
    esp_ble_mesh_generic_client_set_state(&set);
}

// Virtual address (Label UUID)
esp_ble_mesh_virtual_addr_t virtual_addr;
esp_ble_mesh_gen_virtual_addr(label_uuid, 16, &virtual_addr);
// Use virtual_addr.addr as destination
```

### Provisioning (Programmatic)

```c
// Provisioner: Provision unprovisioned device
void ProvisionDevice(const uint8_t uuid[16], uint16_t unicast_addr) {
    esp_ble_mesh_prov_params_t prov = {
        .uuid = uuid,
        .unicast_addr = unicast_addr,
        .attention_duration = 10,
        .provisioning_data = {
            .net_key = net_key,           // 16 bytes
            .net_idx = 0,
            .flags = 0,
            .iv_index = 0,
            .unicast_addr = unicast_addr,
            .dev_key = dev_key,           // 16 bytes (per device)
        },
    };
    esp_ble_mesh_provisioner_provision_device(&prov);
}

// Unprovisioned device: Wait for provisioning
void WaitForProvisioning() {
    // Device automatically enters unprovisioned beacon state
    // Advertises: Mesh Beacon (PB-ADV) or connects via GATT (PB-GATT)
    
    // Callback when provisioned:
    static void prov_cb(esp_ble_mesh_prov_cb_event_t event, 
                        esp_ble_mesh_prov_cb_param_t* param) {
        if (event == ESP_BLE_MESH_PROVISIONER_PROV_COMPLETE_EVT) {
            ESP_LOGI(TAG, "Provisioned: unicast=0x%04x", 
                     param->prov_complete.unicast_addr);
        }
    }
}
```

---

## Key Models Reference

### SIG Models (Standardized)

| Model ID | Name | Description |
|----------|------|-------------|
| **Generic** |
| 0x1000 | Configuration Server | Network config (required) |
| 0x1001 | Configuration Client | Configures nodes |
| 0x1002 | Health Server | Fault reporting (required) |
| 0x1003 | Health Client | Monitors health |
| 0x1004 | Remote Provisioning Server | Provision via proxy |
| 0x1005 | Remote Provisioning Client | Initiates remote prov |
| 0x1006 | Directed Forwarding Config Server | Path config |
| 0x1007 | Directed Forwarding Config Client | Path config client |
| 0x1008 | Bridge Config Server | Bridge configuration |
| 0x1009 | Bridge Config Client | Bridge configuration client |
| **Generic (User-facing)** |
| 0x1000 | Generic OnOff Server | On/Off state |
| 0x1001 | Generic OnOff Client | Controls OnOff |
| 0x1002 | Generic Level Server | 0-65535 level |
| 0x1003 | Generic Level Client | Controls Level |
| 0x1004 | Generic Default Transition Time Server | Transition time |
| 0x1005 | Generic Default Transition Time Client | Controls transition |
| 0x1006 | Generic OnPowerUp Server | Power-up behavior |
| 0x1007 | Generic OnPowerUp Client | Controls power-up |
| 0x1008 | Generic Power Level Server | Power level |
| 0x1009 | Generic Power Level Client | Controls power level |
| 0x100A | Generic Battery Server | Battery state |
| 0x100B | Generic Battery Client | Reads battery |
| 0x100C | Generic Location Server | Global/local location |
| 0x100D | Generic Location Client | Reads location |
| 0x100E | Generic Admin Property Server | Admin properties |
| 0x100F | Generic Manufacturer Property Server | Mfg properties |
| 0x1010 | Generic User Property Server | User properties |
| 0x1011 | Generic Client Property Client | Reads properties |
| **Lighting** |
| 0x1300 | Light Lightness Server | Lightness (0-65535) |
| 0x1301 | Light Lightness Client | Controls lightness |
| 0x1302 | Light Lightness Setup Server | Lightness config |
| 0x1303 | Light CTL Server | Color temp + lightness |
| 0x1304 | Light CTL Client | Controls CTL |
| 0x1305 | Light CTL Setup Server | CTL config |
| 0x1306 | Light CTL Temperature Server | Temp only |
| 0x1307 | Light CTL Temperature Client | Controls temp |
| 0x1308 | Light HSL Server | Hue/Sat/Lightness |
| 0x1309 | Light HSL Client | Controls HSL |
| 0x130A | Light HSL Setup Server | HSL config |
| 0x130B | Light HSL Hue Server | Hue only |
| 0x130C | Light HSL Hue Client | Controls hue |
| 0x130D | Light HSL Saturation Server | Saturation only |
| 0x130E | Light HSL Saturation Client | Controls saturation |
| 0x130F | Light xyL Server | CIE 1931 xy + Lightness |
| 0x1310 | Light xyL Client | Controls xyL |
| 0x1311 | Light xyL Setup Server | xyL config |
| 0x1312 | Light LC Server | Light control (occupancy, ambient) |
| 0x1313 | Light LC Setup Server | LC config |
| **Sensor** |
| 0x1400 | Sensor Server | Generic sensor |
| 0x1401 | Sensor Client | Reads sensors |
| 0x1402 | Sensor Setup Server | Sensor config |
| **Time & Scene** |
| 0x1200 | Time Server | Current time, zone, TAI |
| 0x1201 | Time Client | Reads time |
| 0x1202 | Time Setup Server | Time config |
| 0x1203 | Scene Server | Scene store/recall |
| 0x1204 | Scene Client | Controls scenes |
| 0x1205 | Scene Setup Server | Scene config |
| 0x1206 | Scheduler Server | Scheduled actions |
| 0x1207 | Scheduler Client | Controls scheduler |
| 0x1208 | Scheduler Setup Server | Scheduler config |

---

## Provisioning with Phone Apps

### nRF Mesh (Nordic)
1. Install **nRF Mesh** (iOS/Android)
2. Open app → "New Network" or "Join Network"
3. Scan for unprovisioned devices
4. Select device → "Provision"
5. Choose authentication (Static OOB recommended)
6. Assign unicast address, NetKey, AppKey
7. Configure models (bind, subscribe, publish)

### ESP-BLE-Mesh App (Espressif)
1. Install **ESP-BLE-Mesh** (iOS/Android)
2. Similar flow to nRF Mesh
3. Supports ESP-specific features

### Static OOB (Production)
```c
// Generate 128-bit Static OOB
uint8_t static_oob[16] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                          0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff};

// Set on device (before provisioning)
esp_ble_mesh_set_static_oob(static_oob);

// In phone app: Enter Static OOB (32 hex chars)
// 00112233445566778899aabbccddeeff
```

---

## Debugging & Monitoring

### Serial Logs
```bash
# In menuconfig: Component config → ESP BLE Mesh → Log Level
CONFIG_BLE_MESH_LOG_LEVEL_DEBUG=y   # Verbose
CONFIG_BLE_MESH_LOG_LEVEL_INFO=y    # Normal

# Monitor
idf.py -p /dev/ttyUSB0 monitor
```

### Key Log Messages
```
I (1234) BLE_MESH: [INFO] Provisioning started
I (1234) BLE_MESH: [INFO] Node provisioned: unicast=0x0001
I (1234) BLE_MESH: [INFO] Config: AppKey added, NetKey added
I (1234) BLE_MESH: [INFO] Model: Generic OnOff Server registered
I (1234) BLE_MESH: [INFO] Relay: Enabled
I (1234) BLE_MESH: [INFO] GATT Proxy: Connected
I (1234) BLE_MESH: [INFO] Friend: Established with LPN 0x0002
I (1234) BLE_MESH: [INFO] Message: src=0x0001, dst=0xC000, opcode=0x8201
```

### nRF Mesh / Wireshark Capture
```bash
# 1. nRF Sniffer (nRF52840 dongle) + Wireshark
# 2. Capture BLE advertising + GATT
# 3. Filter: btmesh
# 4. Decrypt with NetKey/AppKey (if known)
```

### CLI Commands (if enabled)
```bash
# Enable CLI in menuconfig
CONFIG_BLE_MESH_CLI=y

# Commands:
mesh info                      # Network info
mesh node                      # Node state
mesh models                    # Registered models
mesh provision <uuid> <addr>   # Provision device
mesh group add <addr> <group>  # Add to group
mesh bind <model> <group>      # Bind model to group
mesh pub <model> <group>       # Set publish address
mesh sub <model> <group>       # Add subscription
mesh send onoff <addr> on      # Send OnOff
mesh send level <addr> 32767   # Send Level
```

---

## Performance Tuning

### Network Parameters
```c
// menuconfig: Component config → ESP BLE Mesh → BLE Mesh Network
CONFIG_BLE_MESH_NETWORK_TRANSMIT_COUNT=2      // 1-7 (default 2)
CONFIG_BLE_MESH_NETWORK_TRANSMIT_INTERVAL=20  // 10-320ms (default 20ms)
CONFIG_BLE_MESH_RELAY_RETRANSMIT_COUNT=2      // 1-7
CONFIG_BLE_MESH_RELAY_RETRANSMIT_INTERVAL=20  // 10-320ms
CONFIG_BLE_MESH_DEFAULT_TTL=3                 // 1-127 (default 3)

// For large networks: Increase transmit count/interval
// For low latency: Decrease interval, increase TTL
```

### For Battery Nodes (LPN)
```c
// menuconfig: Component config → ESP BLE Mesh → Low Power
CONFIG_BLE_MESH_LPN_POLL_INTERVAL=1000        // 100-10000ms (default 1000ms)
CONFIG_BLE_MESH_LPN_POLL_RETRY=3              // 1-10
CONFIG_BLE_MESH_LPN_RECV_WINDOW=200           // 10-255 (200ms default)
CONFIG_BLE_MESH_LPN_SUB_LIST_SIZE=8           // 0-16
CONFIG_BLE_MESH_LPN_POLL_TIMEOUT=300          // 10-3600s

// Power estimates (ESP32-S3):
// Poll 100ms: ~200 µA avg
// Poll 1000ms: ~50 µA avg
// Poll 5000ms: ~20 µA avg
// Poll 10000ms: ~15 µA avg
```

### For Friend Nodes
```c
// menuconfig: Component config → ESP BLE Mesh → Friend
CONFIG_BLE_MESH_FRIEND_QUEUE_SIZE=16          // 2-64 messages
CONFIG_BLE_MESH_FRIEND_SUB_LIST_SIZE=8        // 0-16
CONFIG_BLE_MESH_FRIEND_RECV_WINDOW=200        // 10-255
CONFIG_BLE_MESH_FRIEND_POLL_TIMEOUT=300       // 10-3600s

// Must be mains powered!
```

### For GATT Proxy
```c
// menuconfig: Component config → ESP BLE Mesh → GATT Proxy
CONFIG_BLE_MESH_GATT_PROXY_FILTER_TYPE=0      // 0=Whitelist, 1=Blacklist
CONFIG_BLE_MESH_GATT_PROXY_FILTER_ENTRIES=16  // 1-32
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Provisioning fails | Wrong OOB / timeout | Use Static OOB, increase timeout |
| Node not relaying | Relay disabled | Enable Relay feature |
| LPN not connecting | No Friend node | Deploy Friend node |
| GATT Proxy not connecting | Proxy disabled | Enable GATT Proxy |
| Group not working | Wrong group address | Use 0xC000-0xFEFF |
| High packet loss | Network congested | Reduce transmit count, increase interval |
| OTA fails | Partition too small | Increase OTA partition size |
| Provisioner can't find device | Device not beaconing | Check unprovisioned state |

---

## Integration with Home Assistant

### Via ESPHome (Recommended)
```yaml
# esphome.yaml
esphome:
  name: ble-mesh-node
  platform: ESP32
  board: esp32s3_devkitc_1

bluetooth:
  enabled: true

ble_mesh:
  node_id: 1
  # Provision via ESPHome dashboard or nRF Mesh
```

### Via MQTT Bridge
```c
// Implement MQTT bridge on ESP32-S3
// Publish BLE Mesh events to MQTT
// Subscribe to MQTT for BLE Mesh commands

// Example: OnOff state → MQTT
void OnOffStateChange(uint16_t addr, uint8_t onoff) {
    char topic[64], payload[32];
    snprintf(topic, sizeof(topic), "blemesh/node/0x%04x/onoff", addr);
    snprintf(payload, sizeof(payload), "{\"onoff\":%d}", onoff);
    esp_mqtt_client_publish(mqtt_client, topic, payload, 0, 1, 0);
}
```

---

## Resources

- **ESP-BLE-Mesh**: https://github.com/espressif/esp-idf/tree/master/examples/bluetooth/ble_mesh
- **Bluetooth Mesh Spec**: https://www.bluetooth.com/specifications/mesh/
- **nRF Mesh App**: iOS App Store / Google Play Store
- **ESP-BLE-Mesh App**: iOS App Store / Google Play Store
- **nRF Sniffer**: https://www.nordicsemi.com/Products/Development-tools/nrf-sniffer-for-bluetooth-le
- **DeepWiki**: https://deepwiki.com/espressif/esp-idf (BLE Mesh section)