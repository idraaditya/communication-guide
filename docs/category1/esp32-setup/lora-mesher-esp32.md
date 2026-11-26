# LoRaMesher on ESP32 - Complete Setup Guide

## Prerequisites

### Hardware
- **ESP32 DevKitC** or **ESP32-S3 DevKitC-1** (ESP32 classic or S3)
- **LoRa Radio Module**:
  - SX1262 (recommended, TCXO, better sensitivity)
  - SX1268 (433/868 MHz)
  - SX1276 (legacy, compatible)
  - SX1278 (433 MHz)
- **Antenna** matched to frequency (868/915 MHz or 433 MHz)
- **Connections**: SPI + GPIO for CS, RST, DIO0, DIO1

### Software
- **VS Code** + **PlatformIO** extension (recommended)
- **Git** for cloning
- **Python 3.8+** (for PlatformIO)

### Board Pinouts

#### TTGO T-Beam v1.1 (SX1276)
| Signal | ESP32 GPIO | Notes |
|--------|------------|-------|
| NSS/CS | GPIO 18 | SPI CS |
| RST | GPIO 23 | Reset |
| DIO0 | GPIO 26 | Interrupt |
| DIO1 | GPIO 33 | Interrupt |
| SPI MOSI | GPIO 27 | Shared |
| SPI MISO | GPIO 19 | Shared |
| SPI SCK | GPIO 5 | Shared |
| 3.3V | 3.3V | Radio VCC |
| GND | GND | Ground |

#### Heltec WiFi LoRa 32 V3 (SX1262)
| Signal | ESP32-S3 GPIO | Notes |
|--------|---------------|-------|
| NSS/CS | GPIO 8 | SPI CS |
| RST | GPIO 12 | Reset |
| DIO1 | GPIO 13 | Interrupt (SX1262 uses DIO1) |
| BUSY | GPIO 9 | Busy indicator |
| TXEN | GPIO 14 | TX enable (RF switch) |
| RXEN | GPIO 10 | RX enable (RF switch) |
| SPI MOSI | GPIO 11 | Shared |
| SPI MISO | GPIO 13 | Shared |
| SPI SCK | GPIO 9 | Shared |
| TCXO | 1.8V | Enable via `setTcxoVoltage(1.8)` |

#### LILYGO T3 S3 v1.x (SX1262)
| Signal | ESP32-S3 GPIO | Notes |
|--------|---------------|-------|
| NSS/CS | GPIO 7 | SPI CS |
| RST | GPIO 8 | Reset |
| DIO1 | GPIO 9 | Interrupt |
| BUSY | GPIO 33 | Busy indicator |
| SPI MOSI | GPIO 11 | Shared |
| SPI MISO | GPIO 13 | Shared |
| SPI SCK | GPIO 12 | Shared |

---

## PlatformIO Project Setup

### 1. Create Project

```bash
# Option A: PlatformIO CLI
pio project init --board esp32dev --project-option="framework=arduino"

# Option B: VS Code
# PlatformIO Home → New Project → Board: ESP32 DevKit → Framework: Arduino
```

### 2. platformio.ini Configuration

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
upload_speed = 921600

; LoRaMesher library
lib_deps =
    ; RadioLib (required dependency)
    jgromes/RadioLib@^7.1.0
    ; LoRaMesher (from GitHub)
    https://github.com/LoRaMesher/LoRaMesher.git

; Build flags for LoRaMesher
build_flags =
    -D LORAMESHER_LOG_LEVEL=1        ; INFO level (0=DEBUG, 4=NO_LOG)
    -D LOGGER_BUFFER_SIZE=256        ; Log buffer size
    ; -D DEBUG                       ; Enable extra debug logs
    ; -D LOGGER_DISABLE_COLORS       ; Disable ANSI colors

; Partition table (need space for LoRaMesher + app)
board_build.partitions = default_16MB.csv

; Optional: Custom partition for OTA
; board_build.partitions = partitions.csv

[env:esp32s3dev]
platform = espressif32
board = esp32s3dev
framework = arduino
monitor_speed = 115200
upload_speed = 921600

lib_deps =
    jgromes/RadioLib@^7.1.0
    https://github.com/LoRaMesher/LoRaMesher.git

build_flags =
    -D LORAMESHER_LOG_LEVEL=1
    -D LOGGER_BUFFER_SIZE=256

board_build.partitions = default_16MB.csv
```

### 3. Install Dependencies

```bash
pio lib install
# Or in VS Code: PlatformIO → Libraries → Add from registry → RadioLib
# Then add LoRaMesher from GitHub URL
```

---

## Basic Example: Minimal Node

### main.cpp

```cpp
#include <Arduino.h>
#include <loramesher.hpp>

using namespace loramesher;

// ============================================================
// HARDWARE CONFIGURATION - MODIFY FOR YOUR BOARD
// ============================================================

// TTGO T-Beam v1.1 (SX1276)
PinConfig pins(18, 23, 26, 33);  // CS, RST, DIO0, DIO1

// Heltec WiFi LoRa 32 V3 (SX1262) - uncomment and comment above
// PinConfig pins(8, 12, 13, -1);  // CS, RST, DIO1, (DIO0 not used on SX1262)

// LILYGO T3 S3 (SX1262) - uncomment for T3 S3
// PinConfig pins(7, 8, 9, -1);

// ============================================================
// RADIO CONFIGURATION - MODIFY FOR YOUR REGION
// ============================================================

// EU 868 MHz (CEPT)
RadioConfig radio(
    RadioType::kSx1276,    // Radio type: kSx1262, kSx1268, kSx1276, kSx1278, kSx1280
    869.9f,                // Frequency MHz (EU: 869.9, US: 915.0, AU: 915.0)
    7,                     // Spreading Factor (7-12, default 7)
    125.0f,                // Bandwidth kHz (125, 250, 500)
    7,                     // Coding Rate (5-8, 4/5 to 4/8)
    14,                    // TX Power dBm (2-22, EU max 14)
    0x12,                  // Sync Word (LoRaMesher default 0x12)
    true,                  // CRC enabled
    8                      // Preamble length
);

// US 915 MHz (FCC) - uncomment for US
// RadioConfig radio(
//     RadioType::kSx1276,
//     915.0f,
//     7,
//     125.0f,
//     7,
//     17,                   // US allows up to 30 dBm, but 17 is safe
//     0x12,
//     true,
//     8
// );

// For SX1262 (Heltec V3, T3 S3) - uncomment and configure
// RadioConfig radio(
//     RadioType::kSx1262,
//     869.9f,              // or 915.0f
//     7,
//     125.0f,
//     7,
//     14,
//     0x12,
//     true,
//     8
// );
// radio.setTcxoVoltage(1.8f);  // REQUIRED for SX1262 with TCXO

// ============================================================
// PROTOCOL CONFIGURATION
// ============================================================

LoRaMeshProtocolConfig protocol;
// protocol.setNodeRole(NodeRole::NETWORK_MANAGER);  // Pre-designate NM (one node only)
// protocol.setNodeRole(NodeRole::NODE_ONLY);        // Never become NM
// protocol.setMaxPacketSize(200);                   // Override SF default
// protocol.setDiscoveryTimeoutMs(30000);            // Discovery timeout

// ============================================================
// GLOBAL INSTANCE
// ============================================================

std::unique_ptr<LoraMesher> mesher;
uint32_t last_send = 0;
uint32_t send_interval = 60000;  // 1 minute

// ============================================================
// CALLBACKS
// ============================================================

void OnDataReceived(AddressType source, const std::vector<uint8_t>& data) {
    Serial.printf("[RX] From 0x%04X (%d bytes): ", source, data.size());
    for (auto b : data) Serial.printf("%02X ", b);
    Serial.println();
    
    // Echo back (demo)
    std::vector<uint8_t> reply = {0x01, 0x02, 0x03, 0x04};
    Result r = mesher->Send(source, reply);
    if (!r) Serial.printf("[TX] Reply failed: %s\n", r.GetErrorMessage().c_str());
}

void OnLog(LogLevel level, const char* message) {
    // Optional: custom log handling
    const char* level_str[] = {"DEBUG", "INFO", "WARN", "ERROR", "NONE"};
    Serial.printf("[%s] %s\n", level_str[(int)level], message);
}

// ============================================================
// SETUP & LOOP
// ============================================================

void setup() {
    Serial.begin(115200);
    delay(2000);
    Serial.println("\n=== LoRaMesher ESP32 Demo ===");

    // Initialize LoRaMesher
    mesher = LoraMesher::Builder()
        .withPinConfig(pins)
        .withRadioConfig(radio)
        .withLoRaMeshProtocol(protocol)
        .Build();

    if (!mesher) {
        Serial.println("ERROR: Failed to create LoRaMesher instance");
        while (1) delay(1000);
    }

    // Set callbacks
    mesher->SetDataCallback(OnDataReceived);
    // mesher->SetLogCallback(OnLog);  // Optional custom logger

    // Start the mesh
    Result r = mesher->Start();
    if (!r) {
        Serial.printf("ERROR: Failed to start: %s\n", r.GetErrorMessage().c_str());
        while (1) delay(1000);
    }

    Serial.printf("Node Address: 0x%04X\n", mesher->GetNodeAddress());
    Serial.printf("Node Role: %d\n", (int)mesher->GetNodeRole());
    Serial.println("Waiting for network...");
}

void loop() {
    // Periodic status
    static uint32_t last_status = 0;
    if (millis() - last_status > 10000) {
        last_status = millis();
        
        NetworkStatus status = mesher->GetNetworkStatus();
        Serial.printf("\n[STATUS] State: %d, NM: 0x%04X, Slot: %d, Nodes: %d, Sync: %s\n",
            (int)status.current_state,
            status.network_manager,
            status.current_slot,
            status.connected_nodes,
            status.is_synchronized ? "YES" : "NO");

        // Routing table
        auto routes = mesher->GetRoutingTable();
        Serial.printf("Routes: %d\n", routes.size());
        for (auto& rt : routes) {
            Serial.printf("  0x%04X -> 0x%04X (%d hops, qual=%d)\n",
                rt.destination, rt.next_hop, rt.hop_count, rt.link_quality);
        }

        // Send readiness
        if (Result r = mesher->IsReadyToSend(); r) {
            Serial.println("Ready to send: YES");
        } else {
            Serial.printf("Ready to send: NO (%s)\n", r.GetErrorMessage().c_str());
        }
    }

    // Periodic data send
    if (millis() - last_send > send_interval) {
        last_send = millis();

        // Wait for next TX slot (TDMA-aware)
        uint32_t wait_ms = mesher->GetTimeUntilNextDataSlot(200);  // 200ms guard
        if (wait_ms > 0 && wait_ms < 5000) {
            Serial.printf("Waiting %d ms for TX slot...\n", wait_ms);
            delay(wait_ms);
        }

        // Send broadcast
        std::vector<uint8_t> payload = {0xAA, 0xBB, 0xCC, 0xDD};
        Result r = mesher->SendBroadcast(payload);
        if (!r) {
            Serial.printf("[TX] Broadcast failed: %s\n", r.GetErrorMessage().c_str());
        } else {
            Serial.println("[TX] Broadcast sent");
        }
    }

    // Small delay to prevent watchdog
    delay(10);
}
```

---

## Advanced Example: Battery-Optimized Node

### battery_optimized_main.cpp

```cpp
#include <Arduino.h>
#include <loramesher.hpp>
#include <driver/rtc_io.h>
#include <esp_sleep.h>

using namespace loramesher;

// ============================================================
// HARDWARE CONFIG (TTGO T-Beam v1.1 with 18650)
// ============================================================

PinConfig pins(18, 23, 26, 33);

RadioConfig radio(
    RadioType::kSx1276,
    869.9f,      // EU
    10,          // SF10 for max range
    125.0f,
    7,
    14,          // 14 dBm (EU limit)
    0x12,
    true,
    8
);

LoRaMeshProtocolConfig protocol;
protocol.setNodeRole(NodeRole::NODE_ONLY);        // Never NM
protocol.setMaxPacketSize(51);                    // SF10 default

std::unique_ptr<LoraMesher> mesher;
RTC_DATA_ATTR uint32_t boot_count = 0;
RTC_DATA_ATTR uint32_t last_seq = 0;

// Battery monitoring (TTGO T-Beam: GPIO 35 = ADC1_CH7)
const int BAT_PIN = 35;
const float BAT_DIVIDER = 2.0;  // Voltage divider ratio

float ReadBatteryVoltage() {
    int raw = analogRead(BAT_PIN);
    float voltage = raw * 3.3 / 4095.0 * BAT_DIVIDER;
    return voltage;
}

uint8_t BatteryPercent() {
    float v = ReadBatteryVoltage();
    // 18650: 3.0V=0%, 4.2V=100%
    if (v >= 4.2) return 100;
    if (v <= 3.0) return 0;
    return (uint8_t)((v - 3.0) / 1.2 * 100);
}

void OnDataReceived(AddressType source, const std::vector<uint8_t>& data) {
    // Store for next wake cycle
    Serial.printf("[RX] 0x%04X: %d bytes\n", source, data.size());
}

void setup() {
    Serial.begin(115200);
    delay(100);
    
    boot_count++;
    Serial.printf("\n=== Boot #%d ===\n", boot_count);
    Serial.printf("Battery: %.2fV (%d%%)\n", ReadBatteryVoltage(), BatteryPercent());

    // Initialize LoRaMesher
    mesher = LoraMesher::Builder()
        .withPinConfig(pins)
        .withRadioConfig(radio)
        .withLoRaMeshProtocol(protocol)
        .Build();

    mesher->SetDataCallback(OnDataReceived);

    Result r = mesher->Start();
    if (!r) {
        Serial.printf("Start failed: %s\n", r.GetErrorMessage().c_str());
        EnterDeepSleep(60);  // Retry in 1 min
    }

    // Wait for network join (max 60 seconds)
    uint32_t join_start = millis();
    while (millis() - join_start < 60000) {
        NetworkStatus status = mesher->GetNetworkStatus();
        if (status.is_synchronized) {
            Serial.println("Network joined!");
            break;
        }
        delay(1000);
    }

    // Send sensor data
    SendSensorData();

    // Enter deep sleep
    EnterDeepSleep(300);  // 5 minutes
}

void loop() {
    // Never reached - deep sleep
}

void SendSensorData() {
    // Wait for TX slot
    uint32_t wait_ms = mesher->GetTimeUntilNextDataSlot(200);
    if (wait_ms > 0 && wait_ms < 10000) {
        delay(wait_ms);
    }

    // Prepare payload: [seq(2), temp(2), humidity(2), battery(1), voltage(2)]
    uint16_t seq = last_seq++;
    int16_t temp = 2500;      // 25.00°C * 100
    uint16_t hum = 6000;      // 60.00% * 100
    uint8_t bat = BatteryPercent();
    uint16_t volt = (uint16_t)(ReadBatteryVoltage() * 1000);  // mV

    std::vector<uint8_t> payload;
    payload.push_back(seq >> 8);
    payload.push_back(seq & 0xFF);
    payload.push_back(temp >> 8);
    payload.push_back(temp & 0xFF);
    payload.push_back(hum >> 8);
    payload.push_back(hum & 0xFF);
    payload.push_back(bat);
    payload.push_back(volt >> 8);
    payload.push_back(volt & 0xFF);

    // Send to Network Manager (or broadcast if no route)
    AddressType dest = mesher->GetNetworkStatus().network_manager;
    if (dest == 0 || dest == 0xFFFF) dest = 0xFFFF;  // Broadcast

    Result r = mesher->Send(dest, payload);
    if (!r) {
        Serial.printf("Send failed: %s\n", r.GetErrorMessage().c_str());
    } else {
        Serial.printf("Sent: seq=%d, bat=%d%%, %.2fV\n", seq, bat, ReadBatteryVoltage());
    }

    // Give time for TX
    delay(500);
    mesher->Stop();
}

void EnterDeepSleep(uint32_t seconds) {
    Serial.printf("Deep sleep for %d seconds...\n", seconds);
    
    // Configure wake timer
    esp_sleep_enable_timer_wakeup(seconds * 1000000ULL);
    
    // Power down peripherals
    rtc_gpio_isolate(GPIO_NUM_12);  // Example: isolate unused pins
    
    // Enter deep sleep
    esp_deep_sleep_start();
}
```

---

## Configuration Reference

### RadioConfig Parameters

```cpp
RadioConfig(
    RadioType type,        // kSx1262, kSx1268, kSx1276, kSx1278, kSx1280
    float frequency_mhz,   // 433.0, 868.0, 869.9, 915.0, 923.0, 2400.0
    uint8_t spreading_factor,  // 7-12 (SX1280: 5-12)
    float bandwidth_khz,   // 125.0, 250.0, 500.0 (SX1280: 200, 400, 800, 1600)
    uint8_t coding_rate,   // 5-8 (4/5 to 4/8), SX1280: 5-7
    int8_t tx_power_dbm,   // 2-22 (SX1262), 2-20 (SX1276), -5 to 13 (SX1280)
    uint8_t sync_word,     // 0x12 (LoRaMesher), 0x3444 (Meshtastic)
    bool crc_enabled,      // true/false
    uint8_t preamble_length // 6-65535 (default 8)
)

// SX1262-specific
radio.setTcxoVoltage(1.8f);  // 1.6, 1.7, 1.8, 2.2, 2.4, 2.7, 3.0, 3.3V
radio.setDio2AsRfSwitch(true);  // Use DIO2 for RF switch control
```

### LoRaMeshProtocolConfig Parameters

```cpp
LoRaMeshProtocolConfig protocol;

// Node role
protocol.setNodeRole(NodeRole::AUTO);           // Default: auto join/elect
protocol.setNodeRole(NodeRole::NODE_ONLY);      // Never NM
protocol.setNodeRole(NodeRole::NETWORK_MANAGER); // Force NM (one per network!)

// Network parameters
protocol.setMaxPacketSize(242);        // Override SF default (SF7/8=242, SF9=115, SF10+=51)
protocol.setDiscoveryTimeoutMs(30000); // Discovery timeout (default 30s)
protocol.setRouteTimeoutMs(180000);    // Route inactive timeout (default 3min)
protocol.setNodeTimeoutMs(3600000);    // Node removal timeout (default 1hr)

// Link quality
protocol.setLinkQualityEwmaAlpha(0.30f);  // EWMA alpha (default 0.30)

// Capabilities (for discovery)
protocol.setNodeCapabilities(NodeCapabilities::GATEWAY);      // This node is gateway
protocol.setNodeCapabilities(NodeCapabilities::SENSOR);       // Sensor node
protocol.setNodeCapabilities(NodeCapabilities::CUSTOM_1);     // Custom flag
```

### NodeCapabilities Enum

```cpp
enum class NodeCapabilities : uint8_t {
    NONE = 0x00,
    GATEWAY = 0x01,        // Internet gateway
    SENSOR = 0x02,         // Sensor node
    ACTUATOR = 0x04,       // Actuator node
    CUSTOM_1 = 0x10,       // Custom application flags
    CUSTOM_2 = 0x20,
    CUSTOM_3 = 0x40,
    CUSTOM_4 = 0x80,
};
```

### Discovery: Find Gateway/Sensor

```cpp
// Find closest gateway
auto gw = mesher->GetClosestGateway();
if (gw.has_value()) {
    Serial.printf("Gateway: 0x%04X (%d hops, qual=%d)\n",
        gw->destination, gw->hop_count, gw->link_quality);
}

// Find closest sensor
auto sensor = mesher->GetClosestNodeByCapability(NodeCapabilities::SENSOR);
if (sensor.has_value()) {
    Serial.printf("Sensor: 0x%04X\n", sensor->destination);
}
```

---

## Debugging & Monitoring

### Serial Log Levels

```cpp
// In platformio.ini build_flags:
-D LORAMESHER_LOG_LEVEL=0   // DEBUG (verbose)
-D LORAMESHER_LOG_LEVEL=1   // INFO (default)
-D LORAMESHER_LOG_LEVEL=2   // WARNING
-D LORAMESHER_LOG_LEVEL=3   // ERROR
-D LORAMESHER_LOG_LEVEL=4   // NO_LOG

// Enable extra debug
-D DEBUG

// Disable colors (for log files)
-D LOGGER_DISABLE_COLORS
```

### Key Debug Commands

```cpp
// Print routing table
auto routes = mesher->GetRoutingTable();
for (auto& r : routes) {
    Serial.printf("0x%04X -> 0x%04X (%d hops, Q=%d, slots=%d, caps=0x%02X)\n",
        r.destination, r.next_hop, r.hop_count, r.link_quality,
        r.allocated_data_slots, r.capabilities);
}

// Print network status
NetworkStatus s = mesher->GetNetworkStatus();
Serial.printf("State: %d, NM: 0x%04X, Slot: %d/%d, Nodes: %d, Sync: %s\n",
    (int)s.current_state, s.network_manager, s.current_slot,
    s.total_slots, s.connected_nodes, s.is_synchronized ? "YES" : "NO");

// Check send readiness
if (Result r = mesher->IsReadyToSend(); r) {
    Serial.println("Ready to send");
} else {
    Serial.printf("Not ready: %s\n", r.GetErrorMessage().c_str());
}

// Time until next TX slot
uint32_t wait = mesher->GetTimeUntilNextDataSlot(200);  // 200ms guard
Serial.printf("Next TX slot in %d ms\n", wait);
```

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `Start()` returns `RADIO_INIT_FAILED` | Wrong pins or SPI conflict | Verify pinout, check SPI wiring |
| `Start()` returns `RADIO_CONFIG_FAILED` | Invalid frequency/SF/BW combo | Check RadioLib docs for valid combos |
| Never synchronizes | No Network Manager in range | Pre-designate one node as NM |
| High packet loss | Wrong sync word or frequency | Match all nodes exactly |
| TX fails with `NO_TX_SLOT` | Not synchronized or no data slots | Wait for sync, check `GetTimeUntilNextDataSlot` |
| Battery drains fast | High SF, frequent TX | Use SF7, increase send interval, enable sleep |
| `GetClosestGateway` returns empty | No node with GATEWAY capability | Set `protocol.setNodeCapabilities(GATEWAY)` on gateway |

---

## Building & Flashing

```bash
# Build
pio run -e esp32dev

# Flash (auto-detect port)
pio run -e esp32dev -t upload

# Flash specific port
pio run -e esp32dev -t upload --upload-port /dev/ttyUSB0

# Monitor serial
pio device monitor -e esp32dev

# Build + flash + monitor
pio run -e esp32dev -t upload && pio device monitor -e esp32dev

# Clean build
pio run -e esp32dev -t clean
```

### ESP32-S3 Specific

```bash
# Use ESP32-S3 environment
pio run -e esp32s3dev -t upload

# For USB CDC/JTAG (native USB)
pio device monitor -e esp32s3dev --port /dev/ttyACM0
```

---

## Performance Tuning

### For Maximum Range
```cpp
RadioConfig radio(
    RadioType::kSx1262,
    869.9f,      // Lower frequency = better propagation
    10,          // SF10 (max for SX1262 is 12, but 10 is good balance)
    125.0f,      # Narrowest BW = best sensitivity
    7,           # 4/8 coding rate (max redundancy)
    14,          # Max legal power (EU)
    0x12,
    true,
    12           # Longer preamble for weak signals
);
```

### For Maximum Battery Life
```cpp
// Use SF7 (fastest, lowest airtime)
RadioConfig radio(..., 7, 125.0f, 5, 10, ...);  // Low power

// Protocol config
protocol.setNodeRole(NodeRole::NODE_ONLY);  // No NM duties
protocol.setMaxPacketSize(51);              // Small packets

// Application: send rarely, use deep sleep
// LoRaMesher sleeps automatically between TDMA slots
```

### For Maximum Throughput
```cpp
// SF7, BW 500 kHz, CR 4/5
RadioConfig radio(..., 7, 500.0f, 5, 14, ...);

// Larger packets (SF7 default 242 bytes)
protocol.setMaxPacketSize(242);

// Multiple data slots per superframe
// (protocol config - see PROTOCOL_SPEC.md)
```

---

## Regulatory Compliance

### EU (868 MHz)
```cpp
// Frequency: 868.0 - 870.0 MHz
// Max EIRP: 14 dBm (25 mW)
// Duty cycle: 1% (general), 0.1% (specific sub-bands)
// LoRaMesher TDMA inherently limits duty cycle
RadioConfig radio(..., 869.9f, ..., 14, ...);
```

### US (915 MHz)
```cpp
// Frequency: 902 - 928 MHz
// Max EIRP: 30 dBm (1 W) - but 17-20 dBm typical for modules
// No duty cycle limit (but FCC 15.247 requires spreading)
// Use SF7-SF10, BW 125/500
RadioConfig radio(..., 915.0f, ..., 17, ...);
```

### Channel Plans
```cpp
// EU: Single channel 869.9 MHz (or 868.1/868.3/868.5)
// US: Frequency hopping or fixed 915 MHz
// AU: 915-928 MHz, similar to US
// CN: 470-510 MHz (12 channels)
// JP: 920-928 MHz (13 channels)
```

---

## Next Steps

1. **Test with 2 nodes** - One as NM, one as NODE_ONLY
2. **Verify synchronization** - Check `is_synchronized` in status
3. **Test unicast** - Use `Send(dest, payload)` with known address
4. **Test broadcast** - Use `SendBroadcast(payload)`
5. **Add sensors** - Integrate BME280, GPS, etc.
6. **Build gateway** - Set `GATEWAY` capability, add MQTT bridge
7. **Scale up** - Add more nodes, monitor routing table

## Resources

- **LoRaMesher GitHub**: https://github.com/LoRaMesher/LoRaMesher
- **PROTOCOL_SPEC.md**: https://github.com/LoRaMesher/LoRaMesher/blob/main/PROTOCOL_SPEC.md
- **DeepWiki**: https://deepwiki.com/LoRaMesher/LoRaMesher
- **RadioLib**: https://github.com/jgromes/RadioLib
- **Examples**: https://github.com/LoRaMesher/LoRaMesher/tree/main/examples
- **Discord**: https://discord.gg/KCY78MbpUa