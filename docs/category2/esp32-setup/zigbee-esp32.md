# Zigbee on ESP32-H2/C6 - Complete Setup Guide

## Prerequisites

### Hardware Requirements
- **ESP32-H2** (IEEE 802.15.4 + BLE 5.3) - **Native Zigbee**
- **ESP32-C6** (IEEE 802.15.4 + BLE 5.3 + WiFi 6) - **Dual-protocol**
- **External Zigbee radio** (if using ESP32/ESP32-S3): CC2652P7, EFR32MG21, nRF52840 as coordinator

### Supported Boards
| Board | MCU | Zigbee Role | Notes |
|-------|-----|-------------|-------|
| **ESP32-H2 DevKit** | ESP32-H2 | Coordinator/Router/End Device | Native 802.15.4 |
| **ESP32-C6 DevKit** | ESP32-C6 | Coordinator/Router/End Device | Native 802.15.4 + WiFi |
| **Custom ESP32-H2** | ESP32-H2 | Any | Production |
| **ESP32 + CC2652P7** | ESP32 (Host) + CC2652P7 (Coordinator) | Host + Coord | Z-Stack 3.x |

### Software Requirements
- **ESP-IDF v5.1+** (v5.2 recommended)
- **ESP-Zigbee SDK** (included in ESP-IDF as component)
- **Python 3.8+**
- **Git**

---

## Installation

### 1. Install ESP-IDF

```bash
mkdir -p ~/esp
cd ~/esp
git clone -b v5.2 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32h2 esp32c6
source ./export.sh

# Verify
idf.py --version
```

### 2. Get ESP-Zigbee Examples

```bash
cd ~/esp/esp-idf
ls examples/zigbee/
# Output:
# zigbee_coordinator      - Coordinator (forms network)
# zigbee_router           - Router (extends network)
# zigbee_end_device       - End Device (sleepy)
# zigbee_green_power      - Green Power (battery-less)
# zigbee_touchlink        - Touchlink commissioning
# zigbee_ota_client       - OTA update client
# zigbee_ota_server       - OTA update server
# zigbee_light            - Light device (OnOff, Level, Color)
# zigbee_switch           - Switch device
# zigbee_sensor           - Sensor device (Temp, Humidity)
# zigbee_thermostat       - Thermostat
# zigbee_door_lock        - Door lock
# zigbee_gateway          - Zigbee Gateway (TCP/IP bridge)
```

---

## Building Examples

### 1. Coordinator (Network Former)

```bash
cd ~/esp/esp-idf/examples/zigbee/zigbee_coordinator

# Set target
idf.py set-target esp32h2
# or
idf.py set-target esp32c6

# Configure
idf.py menuconfig
# Key configs:
# Component config → ESP Zigbee SDK →
#   - Zigbee Device Type: [Coordinator]
#   - Zigbee Network Parameters:
#     * PAN ID: 0x1234 (0 = random)
#     * Extended PAN ID: 0x1234567890abcdef (0 = random)
#     * Channel Mask: 0x07fff800 (channels 11-26)
#     * Install Code: (optional, for secure join)
#   - Zigbee Security:
#     * Trust Center Mode: [Standard / High]
#     * Network Key: auto-generate or set
#   - Zigbee Stack:
#     * Max Children: 20
#     * Max Routers: 10
#     * Max Depth: 5
#   - Zigbee Log Level: INFO

# Build
idf.py build

# Flash
idf.py -p /dev/ttyUSB0 flash

# Monitor
idf.py -p /dev/ttyUSB0 monitor
```

### 2. Router (Network Extender)

```bash
cd ~/esp/esp-idf/examples/zigbee/zigbee_router
idf.py set-target esp32h2
idf.py menuconfig
# Zigbee Device Type: [Router]
# Same network params as coordinator
idf.py build flash monitor
```

### 3. End Device (Sleepy)

```bash
cd ~/esp/esp-idf/examples/zigbee/zigbee_end_device
idf.py set-target esp32h2
idf.py menuconfig
# Zigbee Device Type: [End Device]
# Sleep Configuration:
#   - Poll Rate: 1000ms (1 second)
#   - Idle Timeout: 30s
#   - Keep Alive: 300s
idf.py build flash monitor
```

### 4. Light Device (HA Profile)

```bash
cd ~/esp/esp-idf/examples/zigbee/zigbee_light
idf.py set-target esp32h2
idf.py menuconfig
# Zigbee Device Type: [Router]
# Light Configuration:
#   - Device Type: [On/Off / Dimmable / Color Temperature / Full Color]
#   - GPIO for PWM: (configure for your hardware)
#   - Startup Behavior: [Previous / On / Off]
idf.py build flash monitor
```

### 5. Switch Device

```bash
cd ~/esp/esp-idf/examples/zigbee/zigbee_switch
idf.py set-target esp32h2
idf.py menuconfig
# Zigbee Device Type: [End Device]
# Switch Configuration:
#   - Switch Type: [Toggle / Momentary / Multi-function]
#   - GPIO for Button: (configure for your hardware)
#   - Binding: Enable/Disable
idf.py build flash monitor
```

### 6. Sensor Device

```bash
cd ~/esp/esp-idf/examples/zigbee/zigbee_sensor
idf.py set-target esp32h2
idf.py menuconfig
# Zigbee Device Type: [End Device]
# Sensor Configuration:
#   - Sensor Type: [Temperature / Humidity / Pressure / Multi]
#   - Reporting Interval: 300s
#   - Min/Max Report Interval: 10s / 3600s
#   - Reportable Change: 0.5°C / 1% RH
idf.py build flash monitor
```

### 7. Zigbee Gateway (TCP/IP Bridge)

```bash
cd ~/esp/esp-idf/examples/zigbee/zigbee_gateway
idf.py set-target esp32c6  # ESP32-C6 for WiFi + Zigbee
idf.py menuconfig
# Zigbee Device Type: [Coordinator]
# Gateway Configuration:
#   - TCP Server Port: 17754 (default)
#   - WebSocket Port: 17755
#   - WiFi SSID/Password: (configure)
#   - Enable mDNS: YES
idf.py build flash monitor
```

---

## Configuration Guide

### Network Parameters

```c
// In menuconfig: Component config → ESP Zigbee SDK → Zigbee Network Parameters

// PAN ID (0 = random)
#define ZIGBEE_PAN_ID 0x1234

// Extended PAN ID (0 = random)
#define ZIGBEE_EXTENDED_PAN_ID {0x12, 0x34, 0x56, 0x78, 0x90, 0xab, 0xcd, 0xef}

// Channel Mask (channels 11-26)
// 0x07fff800 = all channels
// 0x00000800 = channel 11 only
// 0x00001000 = channel 12 only
// ... 0x04000000 = channel 26 only
#define ZIGBEE_CHANNEL_MASK 0x07fff800

// Install Code (for secure join, 0 = disabled)
// 18 bytes: 16-byte install code + 2-byte CRC
#define ZIGBEE_INSTALL_CODE {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                             0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
                             0x12, 0x34}

// Network Key (16 bytes, 0 = auto-generate)
#define ZIGBEE_NETWORK_KEY {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                            0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff}

// Trust Center Link Key (16 bytes, 0 = default)
#define ZIGBEE_TC_LINK_KEY {0x5a, 0x69, 0x67, 0x42, 0x65, 0x65, 0x41, 0x6c,
                            0x6c, 0x69, 0x61, 0x6e, 0x63, 0x65, 0x30, 0x39}
```

### Device Type Configuration

```c
// In menuconfig: Component config → ESP Zigbee SDK → Zigbee Device Type

// Coordinator (forms network, assigns addresses)
typedef enum {
    ESP_ZB_DEVICE_TYPE_COORDINATOR = 0,
    ESP_ZB_DEVICE_TYPE_ROUTER      = 1,
    ESP_ZB_DEVICE_TYPE_END_DEVICE  = 2,
} esp_zb_device_type_t;

// Coordinator config
esp_zb_cfg_t zb_cfg = {
    .device_type = ESP_ZB_DEVICE_TYPE_COORDINATOR,
    .install_code_policy = INSTALL_CODE_POLICY_ALLOW,  // or REQUIRE
    .nwk_config = {
        .pan_id = 0x1234,
        .extended_pan_id = {0x12, 0x34, 0x56, 0x78, 0x90, 0xab, 0xcd, 0xef},
        .channel_mask = 0x07fff800,
    },
    .security_config = {
        .network_key = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                        0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff},
        .tc_link_key = {0x5a, 0x69, 0x67, 0x42, 0x65, 0x65, 0x41, 0x6c,
                        0x6c, 0x69, 0x61, 0x6e, 0x63, 0x65, 0x30, 0x39},
    },
};
```

### End Device Sleep Configuration

```c
// For battery-powered end devices
esp_zb_end_device_config_t ed_config = {
    .poll_rate_ms = 1000,        // Poll every 1 second
    .idle_timeout_s = 30,        // Sleep after 30s inactivity
    .keep_alive_s = 300,         // Send keep-alive every 5 min
    .rx_on_when_idle = false,    // Sleep between polls
};

// Power consumption estimates:
// - Poll rate 100ms: ~200 µA avg
// - Poll rate 1000ms: ~50 µA avg
// - Poll rate 5000ms: ~20 µA avg
// - Deep sleep (no poll): ~5 µA
```

---

## Zigbee Cluster Library (ZCL) Usage

### Basic Cluster Implementation

```c
#include "esp_zb_core.h"
#include "esp_zb_zcl_attr.h"

// On/Off Cluster (0x0006)
static esp_zb_attribute_list_t* CreateOnOffCluster() {
    esp_zb_on_off_cluster_cfg_t cfg = {
        .on_off = false,              // Initial state
        .global_scene_control = true, // Allow scenes
        .on_time = 0,                 // On time (for timed off)
        .off_wait_time = 0,           // Off wait time
    };
    return esp_zb_on_off_cluster_create(&cfg);
}

// Level Control Cluster (0x0008)
static esp_zb_attribute_list_t* CreateLevelCluster() {
    esp_zb_level_cluster_cfg_t cfg = {
        .current_level = 128,         // 0-254 (0xFE = max)
        .remaining_time = 0,          // Transition time
        .on_off_transition_time = 10, // Default transition
        .on_level = 0xFE,             // Level when turned on
    };
    return esp_zb_level_cluster_create(&cfg);
}

// Temperature Measurement (0x0402)
static esp_zb_attribute_list_t* CreateTempSensor() {
    esp_zb_temperature_sensor_cfg_t cfg = {
        .measured_value = 2500,       // 25.00°C * 100
        .min_measured_value = -2000,  // -20.00°C
        .max_measured_value = 5000,   // 50.00°C
        .tolerance = 50,              // ±0.5°C
    };
    return esp_zb_temperature_sensor_create(&cfg);
}

// Humidity Measurement (0x0405)
static esp_zb_attribute_list_t* CreateHumiditySensor() {
    esp_zb_humidity_sensor_cfg_t cfg = {
        .measured_value = 5000,       // 50.00% * 100
        .min_measured_value = 0,
        .max_measured_value = 10000,  // 100.00%
        .tolerance = 100,             // ±1%
    };
    return esp_zb_humidity_sensor_create(&cfg);
}
```

### Creating a Complete Device

```c
// Example: Multi-sensor End Device
void CreateMultiSensorDevice() {
    // Endpoint 1: Temperature + Humidity
    esp_zb_endpoint_config_t ep_config = {
        .endpoint = 1,
        .device_id = ESP_ZB_HA_TEMPERATURE_SENSOR_DEVICE_ID,
        .device_version = 0,
        .profile_id = ESP_ZB_AF_HA_PROFILE_ID,
    };
    
    // Cluster list for endpoint 1
    esp_zb_cluster_list_t* cluster_list = esp_zb_zcl_cluster_list_create();
    esp_zb_cluster_list_add_basic_cluster(cluster_list, CreateBasicCluster(), ESP_ZB_ZCL_CLUSTER_SERVER_ROLE);
    esp_zb_cluster_list_add_identify_cluster(cluster_list, CreateIdentifyCluster(), ESP_ZB_ZCL_CLUSTER_SERVER_ROLE);
    esp_zb_cluster_list_add_temperature_sensor(cluster_list, CreateTempSensor(), ESP_ZB_ZCL_CLUSTER_SERVER_ROLE);
    esp_zb_cluster_list_add_humidity_sensor(cluster_list, CreateHumiditySensor(), ESP_ZB_ZCL_CLUSTER_SERVER_ROLE);
    
    // Create endpoint
    esp_zb_ep_list_t* ep_list = esp_zb_ep_list_create();
    esp_zb_ep_list_add_ep(ep_list, cluster_list, ep_config);
    
    // Register device
    esp_zb_device_register(ep_list);
    
    // Set reporting (attribute reports to bound devices)
    esp_zb_zcl_attr_t* attr = esp_zb_zcl_get_attr(1, ESP_ZB_ZCL_CLUSTER_ID_TEMP_MEAS, ESP_ZB_ZCL_CLUSTER_SERVER_ROLE, ESP_ZB_ZCL_ATTR_TEMP_MEAS_VALUE_ID);
    esp_zb_zcl_set_attr_val(1, ESP_ZB_ZCL_CLUSTER_ID_TEMP_MEAS, ESP_ZB_ZCL_CLUSTER_SERVER_ROLE, ESP_ZB_ZCL_ATTR_TEMP_MEAS_VALUE_ID, &new_value, false);
    
    // Configure reporting: min 10s, max 3600s, change 0.5°C
    esp_zb_zcl_config_reporting(1, ESP_ZB_ZCL_CLUSTER_ID_TEMP_MEAS, ESP_ZB_ZCL_CLUSTER_SERVER_ROLE,
                                ESP_ZB_ZCL_ATTR_TEMP_MEAS_VALUE_ID,
                                10, 3600, 50);  // 50 = 0.5°C * 100
}
```

### Binding (Switch → Light)

```c
// Bind switch (source) to light (destination)
// Done via gateway or commissioner

// Binding table entry
esp_zb_binding_table_entry_t binding = {
    .src_endpoint = 1,              // Switch endpoint
    .cluster_id = ESP_ZB_ZCL_CLUSTER_ID_ON_OFF,  // On/Off cluster
    .dst_addr_mode = ESP_ZB_APS_ADDR_MODE_64_ENDP_PRESENT,
    .dst_addr_64 = 0x0011223344556677,  // Light IEEE address
    .dst_endpoint = 1,              // Light endpoint
};

// Add binding
esp_zb_binding_add(&binding);

// Now switch commands (On/Off/Toggle) automatically sent to light
```

---

## Commissioning Methods

### 1. Install Code (Secure)

```c
// Coordinator: Set install code policy
esp_zb_set_install_code_policy(INSTALL_CODE_POLICY_REQUIRE);

// Device: Set install code (18 bytes: 16 code + 2 CRC)
// Generate install code:
uint8_t install_code[16] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                            0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff};
uint16_t crc = crc16(install_code, 16);
uint8_t full_code[18];
memcpy(full_code, install_code, 16);
full_code[16] = crc & 0xFF;
full_code[17] = crc >> 8;

// Set on device
esp_zb_set_install_code(full_code, 18);
```

### 2. Touchlink (No Coordinator Needed)

```c
// Enable Touchlink in menuconfig
CONFIG_ESP_ZB_TOUCHLINK=y

// Touchlink initiator (e.g., remote control)
// Touchlink target (e.g., light bulb)
// Devices discover and bind directly

// CLI commands (if enabled):
/*
touchlink scan
touchlink identify <ieee_addr>
touchlink bind <ieee_addr> <cluster_id>
*/
```

### 3. Green Power (Battery-less)

```c
// Enable Green Power in menuconfig
CONFIG_ESP_ZB_GREEN_POWER=y

// Green Power sink (coordinator/router)
// Green Power device (switch, energy harvesting)

// Commission GP device:
// 1. GP device sends GP Commissioning Notification
// 2. Sink adds GP device to GP table
// 3. GP device paired with sink

// GP Device Types:
// - GP Switch (commissioning, on/off, level, hue)
// - GP Sensor (temperature, occupancy)
// - GP Multi-sensor
```

---

## Zigbee Gateway (TCP/IP Bridge)

### Gateway Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Zigbee Gateway (ESP32-C6)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TCP Server (Port 17754)                                        │
│  ├── JSON-RPC 2.0 Protocol                                      │
│  ├── Device Management (Add/Remove/Configure)                  │
│  ├── Cluster Commands (Read/Write/Report)                      │
│  └── Network Management (Permit Join, Channel, etc.)           │
│           │                                                     │
│           ▼                                                     │
│  ESP-Zigbee Stack (Coordinator)                                │
│           │                                                     │
│           ▼                                                     │
│  IEEE 802.15.4 Radio                                           │
│                                                                 │
│  WebSocket (Port 17755) - Real-time events                     │
│  mDNS - Service Discovery (_zigbee._tcp)                       │
└─────────────────────────────────────────────────────────────────┘
```

### Gateway API (JSON-RPC 2.0)

```json
// Request
{"jsonrpc": "2.0", "id": 1, "method": "device.list", "params": {}}

// Response
{"jsonrpc": "2.0", "id": 1, "result": {
    "devices": [
        {"ieee": "0x0011223344556677", "nwk": 0x1234, "type": "Router", "endpoints": [1]},
        {"ieee": "0x0011223344556688", "nwk": 0x5678, "type": "EndDevice", "endpoints": [1, 2]}
    ]
}}

// Read attribute
{"jsonrpc": "2.0", "id": 2, "method": "zcl.read", "params": {
    "ieee": "0x0011223344556677", "endpoint": 1, "cluster": 0x0006, "attr": 0x0000
}}

// Write attribute
{"jsonrpc": "2.0", "id": 3, "method": "zcl.write", "params": {
    "ieee": "0x0011223344556677", "endpoint": 1, "cluster": 0x0006, "attr": 0x0000, "value": true
}}

// Send command
{"jsonrpc": "2.0", "id": 4, "method": "zcl.command", "params": {
    "ieee": "0x0011223344556677", "endpoint": 1, "cluster": 0x0006, "command": 0x01
}}

// Permit join
{"jsonrpc": "2.0", "id": 5, "method": "network.permit_join", "params": {"duration": 60}}

// Event subscription (WebSocket)
{"jsonrpc": "2.0", "method": "events.subscribe", "params": ["device.joined", "attribute.report", "device.left"]}
```

---

## Debugging & Monitoring

### Serial Logs
```bash
# In menuconfig: Component config → ESP Zigbee SDK → Log Level
CONFIG_ESP_ZB_LOG_LEVEL_DEBUG=y   # Verbose
CONFIG_ESP_ZB_LOG_LEVEL_INFO=y    # Normal

# Monitor
idf.py -p /dev/ttyUSB0 monitor
```

### Key Log Messages
```
I (1234) ZB: [INFO] Device started: Coordinator
I (1234) ZB: [INFO] Network formed: PAN=0x1234, Channel=15
I (1234) ZB: [INFO] Device joined: IEEE=0x0011223344556677, NWK=0x5678
I (1234) ZB: [INFO] Attribute report: EP=1, Cluster=0x0402, Attr=0x0000, Val=2500
I (1234) ZB: [INFO] Binding added: Src=0x5678/1 -> Dst=0x1234/1 (Cluster=0x0006)
```

### CLI Commands (if enabled)
```bash
# Enable CLI in menuconfig
CONFIG_ESP_ZB_CLI=y

# Commands:
zb info                        # Network info
zb devices                     # List devices
zb device <ieee>               # Device details
zb endpoints <ieee>            # Device endpoints
zb clusters <ieee> <ep>        # Endpoint clusters
zb attr <ieee> <ep> <cluster>  # Read attributes
zb bind <src_ieee> <src_ep> <cluster> <dst_ieee> <dst_ep>
zb permit_join <duration>      # Permit join
zb channel <11-26>             # Change channel (requires restart)
zb factory_reset               # Factory reset
```

---

## Performance Tuning

### For Large Networks
```c
// menuconfig: Component config → ESP Zigbee SDK → Zigbee Stack
CONFIG_ESP_ZB_MAX_CHILDREN=50          // Max children per router
CONFIG_ESP_ZB_MAX_ROUTERS=20           // Max routers
CONFIG_ESP_ZB_MAX_DEPTH=10             // Max network depth
CONFIG_ESP_ZB_NWK_TABLE_SIZE=100       // Network table size
CONFIG_ESP_ZB_APS_BINDING_TABLE_SIZE=64 // Binding table
CONFIG_ESP_ZB_APS_GROUP_TABLE_SIZE=32  // Group table
```

### For Battery End Devices
```c
// Poll rate optimization
// 100ms: ~200 µA (responsive)
// 1000ms: ~50 µA (balanced)
// 5000ms: ~20 µA (long life)
// 15000ms: ~10 µA (maximum life)

// Keep-alive interval
// 300s (5 min): Standard
// 600s (10 min): Longer life
// 1800s (30 min): Maximum life
```

### For High Reliability
```c
// APS Acknowledgment
CONFIG_ESP_ZB_APS_ACK_ENABLED=y

// Route Discovery
CONFIG_ESP_ZB_NWK_ROUTE_DISCOVERY=y
CONFIG_ESP_ZB_NWK_ROUTE_REPAIR=y

// Security
CONFIG_ESP_ZB_SECURITY_STANDARD=y  // Standard security
// CONFIG_ESP_ZB_SECURITY_HIGH=y    // High security (more overhead)
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Device won't join | Wrong PAN ID/Channel/Key | Match all network params |
| Device joins but no communication | Wrong cluster/endpoint | Check ZCL cluster IDs, endpoints |
| Binding not working | Binding table full | Increase binding table size |
| End device sleeps too long | Poll rate too slow | Reduce poll rate |
| Coordinator fails to start | Channel busy | Scan channels, pick clean one |
| OTA fails | Image too large | Check OTA partition size |
| Green Power not working | GP sink not enabled | Enable GP on coordinator/router |

---

## Integration with Home Assistant

### Via Zigbee Gateway (ESP32-C6)
```yaml
# configuration.yaml
mqtt:
  broker: 192.168.1.100
  discovery: true

# Zigbee2MQTT alternative (if using CC2652P7 coordinator)
zigbee2mqtt:
  device: /dev/ttyUSB0
  network_key: [0x00, 0x11, 0x22, ...]
```

### Direct ESP-Zigbee + HA
```c
// Implement MQTT bridge on ESP32-C6
// Publish Zigbee events to MQTT
// Subscribe to MQTT commands for Zigbee control

// Example: Temperature sensor → MQTT
void TempReportCallback(float temp) {
    char payload[64];
    snprintf(payload, sizeof(payload), 
             "{\"temperature\":%.2f,\"unit\":\"C\"}", temp);
    esp_mqtt_client_publish(mqtt_client, "zigbee/sensor/temp", payload, 0, 1, 0);
}
```

---

## Resources

- **ESP-Zigbee SDK**: https://github.com/espressif/esp-zigbee-sdk
- **Zigbee Spec**: https://csa-iot.org/all-solutions/zigbee/
- **ZCL Reference**: Zigbee Cluster Library Specification
- **ESP-IDF Zigbee Examples**: https://github.com/espressif/esp-idf/tree/master/examples/zigbee
- **Zigbee2MQTT**: https://www.zigbee2mqtt.io/
- **DeepWiki**: https://deepwiki.com/espressif/esp-idf (Zigbee section)