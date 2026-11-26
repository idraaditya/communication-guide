# Meshtastic on ESP32 - Complete Setup Guide

## Prerequisites

### Hardware
- **Supported Boards** (officially supported by Meshtastic firmware):
  - TTGO T-Beam v1.1 / v1.2 (ESP32 + SX1276)
  - Heltec WiFi LoRa 32 V1 / V2 / V3 (ESP32/ESP32-S3 + SX1276/SX1262)
  - LILYGO T3 S3 (ESP32-S3 + SX1262)
  - RAK4631 (nRF52840 + SX1262) - *not ESP32*
  - M5Stack CoreLoRa (ESP32 + SX1276)
  - Custom ESP32 + SX1276/SX1262 boards

### Software
- **Option A: Pre-built Firmware** (easiest)
  - Web Flasher: https://flasher.meshtastic.org/
  - Python CLI: `meshtastic --flash`
- **Option B: Build from Source** (ESP-IDF)
  - ESP-IDF v5.x
  - Python 3.8+
  - Git

---

## Option A: Quick Start - Web Flasher

### 1. Connect Device
- Connect ESP32 via USB
- Put in bootloader mode (hold BOOT, press RST, release BOOT)

### 2. Flash Firmware
1. Open https://flasher.meshtastic.org/ in Chrome/Edge
2. Click "Connect" → Select device
3. Choose board variant (auto-detected or manual)
4. Click "Flash" → Wait for completion
5. Device reboots into Meshtastic

### 3. Configure via Mobile App
- Install Meshtastic app (iOS/Android)
- Pair via Bluetooth
- Configure: Region, Channel, Name, etc.

---

## Option B: Build from Source (ESP-IDF)

### 1. Install ESP-IDF

```bash
# Linux/macOS
mkdir -p ~/esp
cd ~/esp
git clone -b v5.2 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32
source ./export.sh

# Verify
idf.py --version
```

### 2. Clone Meshtastic Firmware

```bash
git clone --recursive https://github.com/meshtastic/firmware.git
cd firmware
git submodule update --init --recursive
```

### 3. Configure Build Target

```bash
# List supported targets
idf.py set-target --help

# For TTGO T-Beam v1.1 (ESP32 + SX1276)
idf.py set-target esp32

# For Heltec V3 / LILYGO T3 S3 (ESP32-S3 + SX1262)
idf.py set-target esp32s3
```

### 4. Configure Board Variant

```bash
# Interactive menuconfig
idf.py menuconfig

# Navigate to:
# Meshtastic Configuration → Board Selection
# Select your board:
#  - TTGO T-Beam v1.1
#  - Heltec WiFi LoRa 32 V3
#  - LILYGO T3 S3 v1.0
#  - etc.
```

**Or set via command line:**

```bash
# TTGO T-Beam v1.1
idf.py -DMESHTASTIC_BOARD=TTGO_TBEAM_V11 build

# Heltec V3
idf.py -DMESHTASTIC_BOARD=HELTEC_WIFI_LORA_32_V3 build

# LILYGO T3 S3
idf.py -DMESHTASTIC_BOARD=LILYGO_T3_S3_V10 build
```

### 5. Build Firmware

```bash
# Full build
idf.py build

# Build output
ls -la build/*.bin
# meshtastic.bin (main firmware)
# bootloader.bin
# partition-table.bin
```

### 6. Flash Firmware

```bash
# Auto-detect port
idf.py flash

# Specific port
idf.py -p /dev/ttyUSB0 flash

# Erase flash first (recommended for first flash)
idf.py erase-flash flash

# Monitor serial output
idf.py monitor

# Build + flash + monitor
idf.py flash monitor
```

---

## Board Configurations (from firmware source)

### TTGO T-Beam v1.1
```kconfig
# boards/ttgo-tbeam-v11.json (simplified)
CONFIG_MESHTASTIC_BOARD_TTGO_TBEAM_V11=y
CONFIG_LORA_CS_GPIO=18
CONFIG_LORA_RESET_GPIO=23
CONFIG_LORA_DIO0_GPIO=26
CONFIG_LORA_DIO1_GPIO=33
CONFIG_LORA_SPI_MOSI=27
CONFIG_LORA_SPI_MISO=19
CONFIG_LORA_SPI_SCLK=5
CONFIG_LORA_MODULE_SX1276=y
CONFIG_LORA_FREQUENCY=915000000
```

### Heltec WiFi LoRa 32 V3
```kconfig
CONFIG_MESHTASTIC_BOARD_HELTEC_WIFI_LORA_32_V3=y
CONFIG_LORA_CS_GPIO=8
CONFIG_LORA_RESET_GPIO=12
CONFIG_LORA_DIO1_GPIO=13
CONFIG_LORA_BUSY_GPIO=9
CONFIG_LORA_TXEN_GPIO=14
CONFIG_LORA_RXEN_GPIO=10
CONFIG_LORA_SPI_MOSI=11
CONFIG_LORA_SPI_MISO=13
CONFIG_LORA_SPI_SCLK=9
CONFIG_LORA_MODULE_SX1262=y
CONFIG_LORA_FREQUENCY=868000000
CONFIG_LORA_TCXO_VOLTAGE=1.8
```

### LILYGO T3 S3 v1.0
```kconfig
CONFIG_MESHTASTIC_BOARD_LILYGO_T3_S3_V10=y
CONFIG_LORA_CS_GPIO=7
CONFIG_LORA_RESET_GPIO=8
CONFIG_LORA_DIO1_GPIO=9
CONFIG_LORA_BUSY_GPIO=33
CONFIG_LORA_SPI_MOSI=11
CONFIG_LORA_SPI_MISO=13
CONFIG_LORA_SPI_SCLK=12
CONFIG_LORA_MODULE_SX1262=y
CONFIG_LORA_FREQUENCY=868000000
```

---

## Configuration (Post-Flash)

### Via Mobile App (Bluetooth)
1. Open Meshtastic app
2. Tap "Add Device" → Select your device
3. Configure:
   - **Region**: US / EU_868 / EU_433 / CN / JP / ANZ / KR / TW / RU / IN / NZ
   - **Channel**: Primary (default) or custom
   - **Device Name**: Your node name
   - **Owner**: Your name
   - **GPS**: Enable/disable, interval
   - **Bluetooth**: Enable/disable, PIN
   - **WiFi**: Enable/disable, credentials (for MQTT)
   - **LoRa**: TX power, spreading factor (advanced)

### Via Serial Console
```bash
idf.py monitor
# Or
meshtastic --port /dev/ttyUSB0 --get-config
meshtastic --port /dev/ttyUSB0 --set lora.region US
meshtastic --port /dev/ttyUSB0 --set lora.tx_power 17
meshtastic --port /dev/ttyUSB0 --set device.name "MyNode"
```

### Via Python CLI
```bash
pip install meshtastic

# Get config
meshtastic --get lora
meshtastic --get device

# Set config
meshtastic --set lora.region US
meshtastic --set lora.tx_power 17
meshtastic --set lora.spreading_factor 7
meshtastic --set device.name "MyNode"
meshtastic --set channel.name "Primary"
meshtastic --set channel.psk "0x1a2b3c4d..."  # 256-bit hex

# Send test message
meshtastic --sendtext "Hello Mesh!" --dest 0xffff  # Broadcast
meshtastic --sendtext "Hello Node!" --dest 0x1234  # Unicast
```

---

## Key Configuration Options

### LoRa Settings (Region-Dependent)

| Region | Frequency | Max Power | SF Range | BW | Notes |
|--------|-----------|-----------|----------|-----|-------|
| **US** | 902-928 MHz | 30 dBm | 7-11 | 125/500 | FHSS or fixed |
| **EU_868** | 868-870 MHz | 14 dBm | 7-12 | 125 | 1% duty cycle |
| **EU_433** | 433-434 MHz | 10 dBm | 7-12 | 125 | 10% duty cycle |
| **CN** | 470-510 MHz | 20 dBm | 7-12 | 125 | 12 channels |
| **JP** | 920-928 MHz | 14 dBm | 7-12 | 125 | 13 channels |
| **AU** | 915-928 MHz | 30 dBm | 7-11 | 125/500 | Similar to US |

### Channel Settings
```json
{
  "name": "Primary",
  "psk": "0x1a2b3c4d5e6f7890...",  // 256-bit AES key (64 hex chars)
  "data_rate": "SF7_BW125",       // Or SF7_BW500, SF12_BW125, etc.
  "uplink_enabled": true,
  "downlink_enabled": true
}
```

**Generate PSK:**
```bash
# Python
python -c "import secrets; print('0x' + secrets.token_hex(32))"

# Or use Meshtastic app: Channel → Generate QR Code
```

### Device Settings
```json
{
  "name": "MyNode",
  "owner": "MyName",
  "owner_short": "MN",
  "is_licensed": false,
  "gps_enabled": true,
  "gps_interval": 300,           // seconds
  "fixed_position": false,
  "position_precision": 2,       // 0-3 (higher = less precise)
  "bluetooth_enabled": true,
  "bluetooth_pin": "1234",
  "wifi_enabled": false,
  "wifi_ap_enabled": false,
  "wifi_ssid": "",
  "wifi_password": ""
}
```

### MQTT Gateway (WiFi Required)
```json
{
  "mqtt_enabled": true,
  "mqtt_server": "mqtt.example.com",
  "mqtt_port": 8883,
  "mqtt_username": "user",
  "mqtt_password": "pass",
  "mqtt_root_topic": "msh",
  "mqtt_tls_enabled": true,
  "mqtt_ca_cert": "-----BEGIN CERTIFICATE-----...",
  "mqtt_client_cert": "-----BEGIN CERTIFICATE-----...",
  "mqtt_client_key": "-----BEGIN PRIVATE KEY-----...",
  "mqtt_map_reporting_enabled": true,
  "mqtt_nodeinfo_enabled": true
}
```

---

## Module Configuration (menuconfig)

### Enable/Disable Modules
```bash
idf.py menuconfig
# Meshtastic Configuration → Module Configuration
```

| Module | Default | Description |
|--------|---------|-------------|
| `CONFIG_MESHTASTIC_MODULE_TEXT_MESSAGES` | Y | Text messaging |
| `CONFIG_MESHTASTIC_MODULE_POSITION` | Y | GPS position sharing |
| `CONFIG_MESHTASTIC_MODULE_TELEMETRY` | Y | Battery, env sensors |
| `CONFIG_MESHTASTIC_MODULE_NEIGHBOR_INFO` | Y | Neighbor discovery |
| `CONFIG_MESHTASTIC_MODULE_WAYPOINT` | Y | Waypoint sharing |
| `CONFIG_MESHTASTIC_MODULE_ROUTING` | Y | Routing info |
| `CONFIG_MESHTASTIC_MODULE_STORE_FORWARD` | N | Store & forward (experimental) |
| `CONFIG_MESHTASTIC_MODULE_REMOTE_HARDWARE` | N | Remote GPIO control |
| `CONFIG_MESHTASTIC_MODULE_SERIAL` | Y | Serial API |
| `CONFIG_MESHTASTIC_MODULE_ADMIN` | Y | Admin commands |
| `CONFIG_MESHTASTIC_MODULE_DETECTION` | Y | Hardware detection |
| `CONFIG_MESHTASTIC_MODULE_AUDIO` | N | Audio (experimental) |

### Security Settings
```bash
# Meshtastic Configuration → Security
CONFIG_MESHTASTIC_ENCRYPTED_STORAGE=y        # Encrypt config in flash
CONFIG_MESHTASTIC_PHONEAPI_ACCESS_CONTROL=y  # Require auth for phone API
CONFIG_MESHTASTIC_ADMIN_PASSWORD="..."       # Admin password hash
```

---

## Advanced: Custom Board Definition

### 1. Create Board JSON
```json
// boards/my_custom_board.json
{
  "name": "My Custom Board",
  "inherit": "esp32_base",
  "lora": {
    "module": "SX1262",
    "frequency": 868000000,
    "pins": {
      "cs": 7,
      "reset": 8,
      "dio1": 9,
      "busy": 33,
      "spi_mosi": 11,
      "spi_miso": 13,
      "spi_sclk": 12
    },
    "tcxo_voltage": 1.8
  },
  "bluetooth": {
    "enabled": true,
    "pin": "1234"
  },
  "battery": {
    "adc_pin": 35,
    "divider": 2.0
  }
}
```

### 2. Add to CMakeLists.txt
```cmake
# In firmware/CMakeLists.txt or component CMakeLists.txt
set(MESHTASTIC_BOARDS
    ${MESHTASTIC_BOARDS}
    "boards/my_custom_board.json"
)
```

### 3. Build
```bash
idf.py -DMESHTASTIC_BOARD=MY_CUSTOM_BOARD build
```

---

## Debugging & Monitoring

### Serial Monitor
```bash
idf.py monitor
# Exit: Ctrl+]
```

### Log Levels
```bash
# In menuconfig: Meshtastic Configuration → Logging
CONFIG_LOG_DEFAULT_LEVEL_INFO=y      # Default
CONFIG_LOG_DEFAULT_LEVEL_DEBUG=y     # Verbose
CONFIG_LOG_DEFAULT_LEVEL_WARN=y      # Warnings only
CONFIG_LOG_DEFAULT_LEVEL_ERROR=y     # Errors only
```

### Common Serial Commands
```bash
# In monitor, type:
help                    # Show commands
info                    # Device info
config                  # Show config
nodes                   # List known nodes
routes                  # Show routing table
scan                    # Scan channels
gps                     # GPS status
battery                 # Battery status
reboot                  # Reboot device
factory_reset           # Factory reset
```

### Python CLI Debug
```bash
meshtastic --port /dev/ttyUSB0 --info
meshtastic --port /dev/ttyUSB0 --nodes
meshtastic --port /dev/ttyUSB0 --routes
meshtastic --port /dev/ttyUSB0 --get lora
meshtastic --port /dev/ttyUSB0 --get channel
```

---

## Troubleshooting

### Build Issues

| Error | Solution |
|-------|----------|
| `idf.py: command not found` | `source ~/esp/esp-idf/export.sh` |
| `Kconfig: not found` | Run in firmware directory |
| `Submodule not found` | `git submodule update --init --recursive` |
| `Partition table too small` | Use `default_16MB.csv` or custom partition |
| `SX1262 TCXO error` | Set `CONFIG_LORA_TCXO_VOLTAGE=1.8` |

### Runtime Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| No LoRa packets | Wrong frequency/region | Match all nodes to same region |
| Bluetooth not pairing | PIN mismatch | Check `bluetooth_pin` config |
| GPS no fix | Antenna/indoors | Move outdoors, check GPS module |
| High packet loss | Interference/collision | Change channel, reduce TX power |
| Device reboots | Brownout / watchdog | Check power supply, increase `CONFIG_ESP_TASK_WDT_TIMEOUT_S` |
| MQTT not connecting | TLS certs / network | Check certs, WiFi credentials |

### Debugging Radio
```bash
# Enable radio debug
# menuconfig → Meshtastic Configuration → Radio → Debug
CONFIG_MESHTASTIC_RADIO_DEBUG=y

# Check radio registers
meshtastic --port /dev/ttyUSB0 --radio-debug
```

---

## Firmware Update (OTA)

### Via Mobile App
1. Connect via Bluetooth
2. Settings → Firmware Update
3. Select release or custom file
4. Update

### Via Serial (DFU)
```bash
# Build OTA image
idf.py build

# Flash OTA partition
idf.py -p /dev/ttyUSB0 flash

# Or use meshtastic CLI
meshtastic --port /dev/ttyUSB0 --flash-firmware build/meshtastic.bin
```

---

## Performance Tuning

### For Maximum Range
```bash
# menuconfig or CLI
meshtastic --set lora.spreading_factor 11
meshtastic --set lora.bandwidth 125
meshtastic --set lora.tx_power 17    # Max for region
meshtastic --set lora.coding_rate 8  # 4/8
```

### For Maximum Battery Life
```bash
# Reduce GPS interval
meshtastic --set device.gps_interval 3600  # 1 hour

# Disable unused modules
# menuconfig: disable MODULE_AUDIO, MODULE_STORE_FORWARD, etc.

# Reduce Bluetooth advertising
meshtastic --set bluetooth.enabled false  # If not using phone app
```

### For Maximum Throughput
```bash
meshtastic --set lora.spreading_factor 7
meshtastic --set lora.bandwidth 500
meshtastic --set lora.coding_rate 5
meshtastic --set channel.data_rate "SF7_BW500"
```

---

## Resources

- **Meshtastic Website**: https://meshtastic.org/
- **Documentation**: https://meshtastic.org/docs/
- **GitHub Firmware**: https://github.com/meshtastic/firmware
- **DeepWiki**: https://deepwiki.com/meshtastic/firmware
- **Discord**: https://discord.gg/mWmKpuQx
- **Python CLI**: https://github.com/meshtastic/python
- **Mobile Apps**: iOS App Store / Google Play Store
- **Web Flasher**: https://flasher.meshtastic.org/
- **Supported Hardware**: https://meshtastic.org/docs/hardware/device-recommendations/