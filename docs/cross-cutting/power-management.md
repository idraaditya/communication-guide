# Power Management Guide

## Power Consumption by Category

### Category 1: LoRa (Sub-GHz)

#### LoRaMesher (TDMA - Best for Battery)

| Operation | Current | Duty Cycle | Avg Current | Notes |
|-----------|---------|------------|-------------|-------|
| Deep Sleep | 10 µA | 99.5% | 0.01 mA | ESP32 ULP + LoRa sleep |
| RX Window | 10 mA | 0.3% | 0.03 mA | Scheduled slots |
| TX (14 dBm) | 100 mA | 0.1% | 0.1 mA | SF7, 200ms slot |
| TX (22 dBm) | 120 mA | 0.1% | 0.12 mA | SF7, max power |
| MCU Active | 15 mA | 0.1% | 0.015 mA | Between slots |
| **Total (SF7, 1 msg/min)** | | | **~0.25 mA** | **~1 year on 2000 mAh** |
| **Total (SF10, 1 msg/10min)** | | | **~0.15 mA** | **~1.5 years on 2000 mAh** |

#### Meshtastic (CSMA/CA - Higher Consumption)

| Operation | Current | Duty Cycle | Avg Current | Notes |
|-----------|---------|------------|-------------|-------|
| Light Sleep | 800 µA | 90% | 0.72 mA | WiFi/BLE off |
| RX (LoRa) | 10 mA | 5% | 0.5 mA | Continuous listen |
| TX (17 dBm) | 120 mA | 1% | 1.2 mA | Random backoff |
| MCU Active | 20 mA | 4% | 0.8 mA | Protocol processing |
| **Total (1 msg/min)** | | | **~3.2 mA** | **~26 days on 2000 mAh** |
| **Total (1 msg/10min)** | | | **~1.5 mA** | **~55 days on 2000 mAh** |

#### LoRa Power Optimization

```c
// LoRaMesher TDMA Sleep (Automatic)
// Slot structure:
// [SYNC] [CONTROL] [DATA] [SLEEP] [SYNC] ...
// Node only wakes for its assigned slots

// Configuration for max battery life:
RadioConfig radio(
    RadioType::kSx1262,
    869.9f,      // Lower freq = better propagation
    7,           // SF7 (fastest, lowest airtime)
    125.0f,      // Narrowest BW
    5,           // CR 4/5 (least redundancy)
    10,          // Low power (10 dBm)
    0x12,        // LoRaMesher sync
    true,        // CRC
    8            // Short preamble
);

LoRaMeshProtocolConfig protocol;
protocol.setNodeRole(NodeRole::NODE_ONLY);  // Never NM
protocol.setMaxPacketSize(51);              // Small packets

// Application: Send rarely, use deep sleep between
// LoRaMesher handles TDMA sleep automatically
```

```c
// Meshtastic Power Optimization
// menuconfig → Meshtastic → Power Management
CONFIG_MESHTASTIC_LIGHT_SLEEP=y
CONFIG_MESHTASTIC_DEEP_SLEEP=y
CONFIG_MESHTASTIC_SLEEP_INTERVAL=60000  // 60s between wake

// Reduce LoRa duty cycle:
meshtastic --set lora.tx_power 10
meshtastic --set lora.spreading_factor 7
meshtastic --set lora.bandwidth 125
meshtastic --set device.sleep_interval 300  // 5 min
```

### Category 2: 802.15.4 / BLE (Thread, Zigbee, BLE Mesh)

#### OpenThread (Thread)

| Role | Sleep Mode | Avg Current | Notes |
|------|------------|-------------|-------|
| **Router/Leader** | None (always on) | 15-20 mA | Mains powered |
| **FED** | None (always on) | 15-20 mA | Mains powered |
| **MED** | CSL (Connected Sleep) | 50-200 µA | Configurable |
| **SED** | Deep Sleep + Poll | 10-50 µA | Lowest power |

```c
// Thread Sleep Modes (OpenThread)
// CSL (Connected Sleep) - Thread 1.2+
// Parent buffers frames, child wakes periodically

otLinkSetCslPeriod(instance, 1000);      // 1 second CSL period
otLinkSetCslTimeout(instance, 300);      // 300s timeout
otLinkSetChildTimeout(instance, 300);    // Parent child timeout

// Deep Sleep End Device (SED)
otLinkSetPollPeriod(instance, 5000);     // 5 second poll
otLinkSetChildTimeout(instance, 300);    // 5 min timeout

// Power estimates (ESP32-H2):
// SED, Poll 1s: ~100 µA
// SED, Poll 5s: ~30 µA
// SED, Poll 30s: ~15 µA
// Deep sleep (no radio): ~5 µA
```

#### Zigbee

| Device Type | Sleep Mode | Avg Current | Notes |
|-------------|------------|-------------|-------|
| **Coordinator** | None | 15-20 mA | Mains |
| **Router** | None | 15-20 mA | Mains |
| **End Device** | Poll + Deep Sleep | 10-100 µA | Battery |

```c
// Zigbee End Device Sleep
// Poll Rate determines power vs responsiveness
// 100ms: ~200 µA (responsive)
// 1000ms: ~50 µA (balanced)
// 5000ms: ~20 µA (long life)
// 15000ms: ~10 µA (maximum life)

// ESP-Zigbee SDK Configuration:
esp_zb_end_device_config_t ed_config = {
    .poll_rate_ms = 5000,        // 5 second poll
    .idle_timeout_s = 30,        // Sleep after 30s inactivity
    .keep_alive_s = 300,         // Keep-alive every 5 min
    .rx_on_when_idle = false,    // Sleep between polls
};

// Keep-alive interval:
// 300s (5 min): Standard
// 600s (10 min): Longer life
// 1800s (30 min): Maximum life
```

#### BLE Mesh

| Role | Sleep Mode | Avg Current | Notes |
|------|------------|-------------|-------|
| **Relay/Friend/Proxy** | None | 15-20 mA | Mains |
| **LPN (Low Power Node)** | Friendship + Poll | 10-50 µA | Battery |

```c
// BLE Mesh LPN Configuration
// Friendship: LPN ↔ Friend (mains powered)
// LPN polls Friend for messages

CONFIG_BLE_MESH_LPN_POLL_INTERVAL=5000      // 5 second poll
CONFIG_BLE_MESH_LPN_POLL_RETRY=3
CONFIG_BLE_MESH_LPN_RECV_WINDOW=200         // 200ms receive window
CONFIG_BLE_MESH_LPN_SUB_LIST_SIZE=8         // Group subscriptions
CONFIG_BLE_MESH_LPN_POLL_TIMEOUT=300        // 5 min timeout

// Power estimates (ESP32-S3):
// Poll 100ms: ~200 µA
// Poll 1000ms: ~50 µA
// Poll 5000ms: ~20 µA
// Poll 10000ms: ~15 µA
```

### Category 3: WiFi Mesh (Babel, BATMAN-ADV, 802.11s)

| Mode | Avg Current | Notes |
|------|-------------|-------|
| **Active (TX/RX)** | 150-250 mA | High throughput |
| **Light Sleep** | 10-20 mA | WiFi connected, CPU sleep |
| **Modem Sleep** | 15-30 mA | DTIM wake |
| **Deep Sleep** | 5-10 µA | WiFi off |

```c
// WiFi Power Save Modes (ESP32-S3)
// Power Save Mode: Station only
wifi_ps_type_t ps_type = WIFI_PS_MIN_MODEM;  // Modem sleep (DTIM)
// or WIFI_PS_MAX_MODEM: Max modem sleep

// Light Sleep (CPU + Modem):
esp_sleep_enable_timer_wakeup(interval_us);
esp_light_sleep_start();

// Deep Sleep (WiFi off):
esp_sleep_enable_timer_wakeup(interval_us);
esp_deep_sleep_start();

// For mesh nodes: Light sleep between beacons
// Mesh protocols (Babel, BATMAN-ADV) need periodic wake

// Typical mesh node power (ESP32-S3):
// Light sleep 90%, Active 10%: ~25 mA avg
// 5000 mAh battery: ~8 days
// Mains power recommended for mesh infrastructure
```

### Category 4: High Bandwidth Stable (WireGuard, BIRD2)

| Device | Avg Power | Notes |
|--------|-----------|-------|
| **ESP32-S3 WireGuard** | 100-200 mA | Userspace crypto |
| **RPi CM4 WireGuard** | 2-3 W | Kernel crypto |
| **x86 WireGuard/BIRD2** | 10-20 W | High performance |

```c
// WireGuard on ESP32-S3 (WireGuard-Go)
// Userspace crypto = higher power
// Keepalive interval affects power

// Config for lower power:
PersistentKeepalive = 60  // 60 seconds (vs default 25)
// Less frequent handshakes = less CPU

// ESP32-S3 power:
// Active crypto: ~150 mA @ 3.3V = 500 mW
// Idle (keepalive only): ~50 mA
// 5000 mAh battery: ~33 hours continuous
// Mains power recommended
```

---

## Battery Life Calculation

### Formula

```
Battery Life (hours) = Battery Capacity (mAh) / Average Current (mA)

Average Current = Σ (Current_i × Duty_Cycle_i)

Daily Energy (mAh) = Average Current (mA) × 24

Solar Panel Sizing:
Panel Current (mA) = Daily Energy (mAh) × 1.5 / Peak Sun Hours
```

### Example Calculations

#### LoRaMesher Node (SF7, 1 msg/min, 2000 mAh 18650)
```
Deep Sleep: 0.01 mA × 99.5% = 0.01 mA
RX Window:  10 mA × 0.3% = 0.03 mA
TX:         100 mA × 0.1% = 0.1 mA
MCU:        15 mA × 0.1% = 0.015 mA
------------------------------
Average:    0.255 mA

Battery Life = 2000 mAh / 0.255 mA = 7,843 hours = 327 days ≈ 10.7 months
```

#### Meshtastic Node (1 msg/10min, 2000 mAh)
```
Light Sleep:  0.8 mA × 90% = 0.72 mA
RX:          10 mA × 5% = 0.5 mA
TX:         120 mA × 0.5% = 0.6 mA
MCU:        20 mA × 4.5% = 0.9 mA
------------------------------
Average:     2.72 mA

Battery Life = 2000 mAh / 2.72 mA = 735 hours = 30.6 days
```

#### Thread SED (Poll 5s, 2000 mAh)
```
Deep Sleep:  5 µA × 99.9% = 0.005 mA
Poll RX:    15 mA × 0.01% = 0.0015 mA
Poll TX:    20 mA × 0.005% = 0.001 mA
------------------------------
Average:     0.0075 mA

Battery Life = 2000 mAh / 0.0075 mA = 266,666 hours = 30 years!
(Limited by battery self-discharge ~1-2% per year → 2-5 years practical)
```

#### WiFi Mesh Node (Light sleep 90%, 5000 mAh)
```
Light Sleep: 15 mA × 90% = 13.5 mA
Active:     200 mA × 10% = 20 mA
------------------------------
Average:     33.5 mA

Battery Life = 5000 mAh / 33.5 mA = 149 hours = 6.2 days
```

---

## Power Optimization Techniques

### 1. Radio Optimization

```c
// LoRa: Minimize airtime
- Use SF7 (fastest) when range allows
- Use BW 125 kHz (narrowest)
- Use CR 4/5 (least redundancy)
- Minimize preamble (8 symbols)
- Minimize packet size
- Use TDMA (LoRaMesher) vs CSMA (Meshtastic)

// WiFi: Minimize active time
- Increase beacon interval (100→300 TU)
- Disable unnecessary scans
- Use power save mode (WIFI_PS_MIN_MODEM)
- Disable 802.11n/ac if not needed (802.11g only)

// BLE: Minimize advertising/connection
- Increase advertising interval (100→1000ms)
- Use PHY coded (125kbps) for range, not speed
- Minimize connection events
- Use slave latency
```

### 2. MCU Optimization

```c
// ESP32-S3 Power Management
// Light Sleep (automatic with FreeRTOS tickless)
CONFIG_FREERTOS_USE_TICKLESS_IDLE=y
CONFIG_PM_ENABLE=y

// Deep Sleep (manual)
esp_sleep_enable_timer_wakeup(60 * 1000000);  // 60 seconds
esp_deep_sleep_start();

// ULP Coprocessor (for sensor monitoring during sleep)
// ULP runs while main CPU in deep sleep
ulp_riscv_init();
ulp_riscv_load_binary(ulp_main_bin_start, ulp_main_bin_end);
ulp_riscv_run();

// RTC Memory (survives deep sleep)
RTC_DATA_ATTR int boot_count = 0;
RTC_DATA_ATTR float last_temperature = 0;

// GPIO Hold (maintain pin state during sleep)
gpio_hold_en(GPIO_NUM_X);
gpio_deep_sleep_hold_en();
```

### 3. Peripheral Optimization

```c
// Disable unused peripherals
periph_module_disable(PERIPH_UART1_MODULE);
periph_module_disable(PERIPH_SPI2_MODULE);
periph_module_disable(PERIPH_I2C0_MODULE);

// Reduce CPU frequency
rtc_clk_cpu_freq_set(RTC_CPU_FREQ_80M);  // 240→80 MHz

// Voltage scaling (if supported)
// ESP32-S3: VDD_SPI can be 1.8V for flash/PSRAM
```

### 4. Application-Level Optimization

```c
// Sensor Sampling
// Bad: Sample every second, transmit every sample
// Good: Sample every minute, transmit average every 10 min

// Data Aggregation
// Combine multiple sensors in one packet
struct SensorPacket {
    uint32_t timestamp;
    float temperature;
    float humidity;
    float pressure;
    float battery;
} __attribute__((packed));

// Event-Driven vs Polling
// Bad: Poll sensor every 100ms
// Good: Sensor interrupt → wake MCU → read → sleep

// Batch Transmissions
// Queue messages, send in burst during TX window
// LoRaMesher: Automatic (TDMA slots)
// Meshtastic: Manual (queue in application)
```

---

## Solar Power Design

### Panel Sizing

```
Daily Consumption (mAh) = Average Current (mA) × 24

Required Panel Current (mA) = Daily Consumption × 1.5 / Peak Sun Hours

Panel Power (W) = Panel Current (mA) × Panel Voltage (V) / 1000
```

### Example: LoRaMesher Node (0.25 mA avg, 4h sun)
```
Daily = 0.25 mA × 24 = 6 mAh
Panel Current = 6 × 1.5 / 4 = 2.25 mA @ 5V
Panel Power = 2.25 × 5 / 1000 = 0.011 W = 11 mW

Practical: 0.5W panel (provides margin for clouds, winter)
```

### Example: WiFi Mesh Node (33 mA avg, 4h sun)
```
Daily = 33 mA × 24 = 792 mAh
Panel Current = 792 × 1.5 / 4 = 297 mA @ 5V
Panel Power = 297 × 5 / 1000 = 1.5 W

Practical: 2-3W panel with 5000 mAh battery buffer
```

### Charge Controller Selection

| Controller | Type | Max Panel | Max Battery | Efficiency | Best For |
|------------|------|-----------|-------------|------------|----------|
| **TP4056** | Linear | 5-6V | 3.7V Li-ion | ~80% | < 1W panel, simple |
| **LTC3105** | MPPT | 0.2-5V | 1-5V | ~90% | Small panel, low light |
| **LTC3108** | MPPT | 20mV-1V | 2.2-5.25V | ~85% | Energy harvesting |
| **CN3791** | MPPT | 5-28V | 3.7V Li-ion | ~95% | 1-10W panel |
| **BQ24074** | MPPT | 4.5-28V | 3.7V Li-ion | ~95% | I2C control, 1-5W |
| **BQ25570** | MPPT | 100mV-5V | 2-5V | ~90% | Nano-power harvesting |

### Battery + Solar System Design

```c
// Complete system for LoRaMesher (1 year battery life target)
struct PowerSystem {
    // Battery
    BatteryType: LiFePO4_14500;  // 3.2V, 600mAh, safe
    // or Li-ion 18650: 3.7V, 3000mAh
    
    // Solar Panel
    PanelPower: 0.5W;  // 5V, 100mA
    PanelVoltage: 5V;
    
    // Charge Controller
    Controller: LTC3105;  // MPPT, works in low light
    
    // Power Path
    // Solar → LTC3105 → Battery + System
    // System draws from battery when solar insufficient
    
    // Monitoring
    BatteryADC: GPIO1;  // Voltage divider
    SolarADC: GPIO2;    // Voltage divider
    ChargeStatus: GPIO3; // CHG pin from controller
};

// Monitoring
float ReadBatteryVoltage() {
    int raw = adc1_get_raw(ADC1_CHANNEL_1);
    return raw * 3.3 / 4095.0 * DIVIDER_RATIO;
}

float ReadSolarVoltage() {
    int raw = adc1_get_raw(ADC1_CHANNEL_2);
    return raw * 3.3 / 4095.0 * DIVIDER_RATIO;
}

bool IsCharging() {
    return gpio_get_level(CHG_PIN) == 0;  // Active low
}
```

---

## Power Budget Template

```
PROJECT: ________________
PROTOCOL: ________________
HARDWARE: ________________

CURRENT BUDGET:
┌──────────────────┬──────────┬────────────┬────────────┐
│ Operation        │ Current  │ Duty Cycle │ Avg Current│
├──────────────────┼──────────┼────────────┼────────────┤
│ Deep Sleep       │ ____ µA  │ ____ %     │ ____ µA    │
│ Light Sleep      │ ____ mA  │ ____ %     │ ____ mA    │
│ RX (Radio)       │ ____ mA  │ ____ %     │ ____ mA    │
│ TX (Radio)       │ ____ mA  │ ____ %     │ ____ mA    │
│ MCU Active       │ ____ mA  │ ____ %     │ ____ mA    │
│ Sensors          │ ____ mA  │ ____ %     │ ____ mA    │
│ Peripherals      │ ____ mA  │ ____ %     │ ____ mA    │
├──────────────────┼──────────┼────────────┼────────────┤
│ TOTAL AVERAGE    │          │            │ ____ mA    │
└──────────────────┴──────────┴────────────┴────────────┘

BATTERY: ____ mAh (__ V, chemistry: ______)
BATTERY LIFE: ____ hours = ____ days = ____ months

SOLAR: ____ W panel, ____ V, ____ h peak sun
CHARGE CONTROLLER: ________________
EXPECTED SOLAR HARVEST: ____ mAh/day
NET DAILY: ____ mAh (positive = sustainable)

MARGIN: ____ % (target > 50%)
```

---

## Testing Power Consumption

### Equipment

| Tool | Purpose | Budget |
|------|---------|--------|
| **Multimeter** | Basic current measurement | $15 |
| **USB Power Meter** | USB current/voltage/power | $10 |
| **Nordic Power Profiler Kit II** | µA accuracy, profiling | $80 |
| **Joulescope** | High precision, visualization | $300 |
| **Oscilloscope + Current Probe** | Dynamic analysis | $200+ |

### Measurement Procedure

```bash
# 1. Baseline (deep sleep)
# Measure: Should be 5-20 µA for ESP32-S3

# 2. Active TX
# Measure peak: 100-250 mA for LoRa/WiFi

# 3. Average over time
# Use Power Profiler Kit II: 24h capture
# Export CSV → calculate average

# 4. Battery drain test
# Full charge → run until cutoff → measure time
# Compare with calculated

# 5. Solar test
# Measure: Panel V/I, Battery V/I, Charge controller efficiency
# Vary: Sun angle, clouds, temperature
```

---

## Troubleshooting High Power

| Symptom | Cause | Fix |
|---------|-------|-----|
| High deep sleep (>100 µA) | GPIO not held, peripheral enabled | `gpio_hold_en()`, `periph_module_disable()` |
| High light sleep (>5 mA) | WiFi/BLE not disabled | `esp_wifi_stop()`, `esp_bt_controller_disable()` |
| Frequent wakeups | Timer too short, sensor interrupt | Increase intervals, use ULP |
| High TX current | Max power, long packets | Reduce power, minimize packets |
| Battery drains fast | No sleep, constant RX | Implement TDMA/polling, disable radio |

---

## Resources

- **ESP32 Power Management**: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/power_management.html
- **Nordic Power Profiler**: https://www.nordicsemi.com/Products/Development-tools/nrf-power-profiler-kit-ii
- **Joulescope**: https://www.joulescope.com/
- **LoRa Power**: https://www.semtech.com/products/wireless-rf/lora-transceivers
- **Thread Power**: https://www.threadgroup.org/
- **BLE Mesh Power**: https://www.bluetooth.com/specifications/mesh/