# Device Categories & Hardware Selection

## Four-Quadrant Classification

This guide classifies communication scenarios by two primary axes: **Bandwidth** and **Link Stability**.

### Category Definitions

| Category | Bandwidth | Packet Loss | Latency | Range | Power Budget |
|----------|-----------|-------------|---------|-------|--------------|
| **1. Low BW, Lossy, Long Range** | 0.1-5 kbps | 10-50% | 100ms-5s | 1-50+ km | Battery (years) |
| **2. Low BW, Stable** | 250kbps-1Mbps | <1% | 10-100ms | 10-100m | Battery (months) |
| **3. High BW, Lossy** | 1-50 Mbps | 1-10% | 10-100ms | 100m-1km | Mains/large battery |
| **4. High BW, Stable** | 100Mbps-1Gbps | <0.1% | <10ms | LAN/WAN | Mains |

## Hardware Selection by Category

### Category 1: Long Range LoRa

#### Radio Modules
| Module | Frequency | Max Power | Sensitivity | Interface | Best For |
|--------|-----------|-----------|-------------|-----------|----------|
| **SX1262** | 868/915 MHz | +22 dBm | -148 dBm | SPI | LoRaMesher, Meshtastic |
| **SX1268** | 433/868 MHz | +22 dBm | -148 dBm | SPI | EU 433MHz, LoRaMesher |
| **SX1276** | 868/915 MHz | +20 dBm | -148 dBm | SPI | Meshtastic (legacy) |
| **SX1278** | 433 MHz | +20 dBm | -148 dBm | SPI | Meshtastic (433MHz) |
| **LR1121** | 868/915/2.4GHz | +22 dBm | -148 dBm | SPI | Multi-band, GNSS |
| **SX1280** | 2.4 GHz | +13 dBm | -132 dBm | SPI | Short-range, high throughput |

#### Recommended Boards
| Board | MCU | Radio | Antenna | Battery | Best Protocol |
|-------|-----|-------|---------|---------|---------------|
| **TTGO T-Beam v1.1** | ESP32 | SX1276 | SMA | 18650 | Meshtastic, LoRaMesher |
| **Heltec WiFi LoRa 32 V3** | ESP32-S3 | SX1262 | IPEX | 2-pin JST | LoRaMesher, Meshtastic |
| **LILYGO T3 S3 v1.x** | ESP32-S3 | SX1262 | IPEX | 2-pin JST | LoRaMesher |
| **RAKwireless RAK4631** | nRF52840 | SX1262 | IPEX | 2-pin JST | Meshtastic (nRF52) |
| **M5Stack CoreLoRa** | ESP32 | SX1276 | Built-in | Internal | Prototyping |

#### Antenna Selection
| Type | Gain | Pattern | Mount | Use Case |
|------|------|---------|-------|----------|
| **1/4 wave whip** | 2-3 dBi | Omnidirectional | SMA | General purpose |
| **1/2 wave dipole** | 5-6 dBi | Omnidirectional | SMA | Fixed base stations |
| **Yagi (directional)** | 10-15 dBi | Directional | Pole | Point-to-point links |
| **Patch (2.4 GHz)** | 6-8 dBi | Directional | PCB | SX1280 short range |

### Category 2: Short Range Stable (802.15.4 / BLE)

#### Radio Modules
| Module | Standard | Max Rate | Sensitivity | Interface | ESP32 Support |
|--------|----------|----------|-------------|-----------|---------------|
| **ESP32-H2** | 802.15.4 + BLE 5.3 | 250 kbps / 2 Mbps | -103 dBm | Internal | Native |
| **ESP32-C6** | 802.15.4 + BLE 5.3 + WiFi 6 | 250 kbps / 2 Mbps | -103 dBm | Internal | Native |
| **nRF52840** | 802.15.4 + BLE 5.2 | 250 kbps / 2 Mbps | -103 dBm | External | Via co-proc |
| **CC2652P7** | 802.15.4 + BLE 5.2 | 250 kbps / 2 Mbps | -103 dBm | External | Via co-proc |

#### Boards
| Board | MCU | Protocols | Antenna | Best For |
|-------|-----|-----------|---------|----------|
| **ESP32-H2 DevKit** | ESP32-H2 | Thread, Zigbee, BLE | PCB/External | Matter development |
| **ESP32-C6 DevKit** | ESP32-C6 | Thread, Zigbee, BLE, WiFi | PCB/External | Dual-protocol |
| **Nordic nRF52840 DK** | nRF52840 | Thread, Zigbee, BLE | PCB | Reference design |
| **Silicon Labs xG24** | EFR32MG24 | Thread, Zigbee, BLE | RF module | Production |

### Category 3: High Bandwidth Lossy (WiFi Mesh)

#### Radio Modules
| Module | Standard | Max Rate | Bands | MIMO | ESP32 Support |
|--------|----------|----------|-------|------|---------------|
| **ESP32-S3** | WiFi 4 (802.11n) | 150 Mbps | 2.4 GHz | 1x1 | Native |
| **ESP32-C6** | WiFi 6 (802.11ax) | 287 Mbps | 2.4 GHz | 1x1 | Native |
| **ESP32-P4** | WiFi 6 + 802.11n | 574 Mbps | 2.4/5 GHz | 2x2 | Native |

#### Boards
| Board | MCU | WiFi | RAM | Flash | Best For |
|-------|-----|------|-----|-------|----------|
| **ESP32-S3 DevKitC-1** | ESP32-S3 | 802.11n | 512KB SRAM | 16MB | Babel, BATMAN-ADV |
| **ESP32-C6 DevKit** | ESP32-C6 | 802.11ax | 512KB SRAM | 16MB | WiFi 6 mesh |
| **ESP32-P4 DevKit** | ESP32-P4 | 802.11ax/n | 768KB SRAM | 32MB | High-perf mesh |
| **M5Stack CoreS3** | ESP32-S3 | 802.11n | 512KB SRAM | 16MB | Prototyping |

### Category 4: High Bandwidth Stable

#### Hardware
| Board | MCU | Ethernet | WiFi | Crypto | Best For |
|-------|-----|----------|------|--------|----------|
| **ESP32-P4** | ESP32-P4 | 10/100/1000 | 802.11ax | AES/SHA/RSA | WireGuard, cjdns |
| **ESP32-S3 + ETH** | ESP32-S3 | 10/100 (RMII) | 802.11n | AES/SHA | WireGuard |
| **Raspberry Pi CM4** | BCM2711 | 10/100/1000 | 802.11ac | ARM Crypto | BIRD, cjdns, WireGuard |
| **OpenWrt Router** | MediaTek/Qualcomm | Multi-GbE | 802.11ax | HW Crypto | All Cat 4 protocols |

## Power Budget Estimates

### Category 1 (LoRa)
| Operation | Current | Duration | Energy (per hour) |
|-----------|---------|----------|-------------------|
| Deep sleep | 10 µA | 99.9% | 0.036 mAh |
| RX (LoRa) | 10 mA | 0.05% | 0.5 mAh |
| TX (22 dBm) | 120 mA | 0.05% | 6 mAh |
| **Total (1 msg/min)** | | | **~6.5 mAh/h** |
| **18650 (3000 mAh)** | | | **~19 days** |

With TDMA (LoRaMesher): ~1 msg/10 min → **~190 days**

### Category 2 (Thread/Zigbee/BLE)
| Operation | Current | Duty Cycle | Energy (per hour) |
|-----------|---------|------------|-------------------|
| Deep sleep | 5 µA | 90% | 0.018 mAh |
| RX | 15 mA | 5% | 0.75 mAh |
| TX (0 dBm) | 20 mA | 5% | 1 mAh |
| **Total** | | | **~1.8 mAh/h** |
| **2000 mAh battery** | | | **~46 days** |

### Category 3 (WiFi Mesh)
| Operation | Current | Duty Cycle | Energy (per hour) |
|-----------|---------|------------|-------------------|
| Light sleep | 800 µA | 50% | 0.4 mAh |
| RX (WiFi) | 80 mA | 25% | 20 mAh |
| TX (17 dBm) | 240 mA | 25% | 60 mAh |
| **Total** | | | **~80 mAh/h** |
| **5000 mAh battery** | | | **~2.6 days** |

Mains power recommended for Category 3.

### Category 4 (Wired/WiFi 6)
| Operation | Power | Notes |
|-----------|-------|-------|
| ESP32-P4 + ETH | 1-2 W | Mains only |
| Raspberry Pi CM4 | 3-5 W | Mains only |
| OpenWrt Router | 5-15 W | Mains only |

## Regulatory Considerations

### LoRa (Category 1)
| Region | Band | Max EIRP | Duty Cycle | Channels |
|--------|------|----------|------------|----------|
| **EU (CEPT)** | 868 MHz | 25 mW (14 dBm) | 1% / 0.1% | 8 channels |
| **US (FCC)** | 915 MHz | 1 W (30 dBm) | None | 64 channels |
| **AU/NZ** | 915 MHz | 1 W (30 dBm) | None | 64 channels |
| **CN** | 470 MHz | 100 mW (20 dBm) | 1% | 12 channels |
| **JP** | 920 MHz | 25 mW (14 dBm) | None | 13 channels |

### WiFi (Categories 3-4)
| Region | 2.4 GHz Channels | 5 GHz Channels | Max EIRP |
|--------|------------------|----------------|----------|
| **US** | 1-11 | 36-165 | 1 W (30 dBm) |
| **EU** | 1-13 | 36-165 | 100 mW (20 dBm) |
| **JP** | 1-14 | 36-165 | 100 mW (20 dBm) |

### 802.15.4 (Category 2)
| Region | Band | Channels | Max EIRP |
|--------|------|----------|----------|
| **Worldwide** | 2.4 GHz | 11-26 | 0 dBm (1 mW) typical |
| **US/EU/JP** | 2.4 GHz | 11-26 | 20 dBm (100 mW) max |

## Selection Checklist

For your project, answer:

1. **Range needed?** → <100m (Cat 2/3/4) / 1-50km (Cat 1)
2. **Bandwidth needed?** → <1kbps (Cat 1) / 250kbps-1Mbps (Cat 2) / 1-50Mbps (Cat 3) / >100Mbps (Cat 4)
3. **Link reliability?** → Lossy (Cat 1/3) / Stable (Cat 2/4)
4. **Power source?** → Battery years (Cat 1) / Battery months (Cat 2) / Mains (Cat 3/4)
5. **Mobility?** → Static (all) / Mobile (Cat 3 Babel, Cat 4 WireGuard)
6. **IP required?** → Yes (Cat 2 Thread, Cat 3/4) / No (Cat 1 LoRaMesher, Cat 2 BLE Mesh)
7. **Internet gateway?** → Border router (Cat 2) / MQTT gateway (Cat 1) / Direct (Cat 3/4)

## Cross-Category Hybrid Deployments

Many real systems combine categories:

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERNET / CLOUD                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │   BORDER GATEWAY        │
              │   (ESP32-S3 + Ethernet) │
              └────────────┬────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────┴────┐       ┌─────┴─────┐      ┌─────┴─────┐
   │ WiFi    │       │ Thread/   │      │ LoRa      │
   │ Mesh    │       │ Zigbee    │      │ Mesh      │
   │(Cat 3)  │       │(Cat 2)    │      │(Cat 1)    │
   └─────────┘       └───────────┘      └───────────┘
   Babel/           OpenThread/        LoRaMesher/
   BATMAN-ADV       Zigbee/            Meshtastic
                    BLE Mesh
```

**Example: Smart Agriculture**
- **Field sensors** (soil moisture, weather) → LoRaMesher (Cat 1, battery 1 year)
- **Greenhouse actuators** (valves, fans) → Thread (Cat 2, mains powered)
- **Camera/ML nodes** → WiFi Mesh Babel (Cat 3, mains/solar)
- **Gateway** → ESP32-S3 with Ethernet + LoRa + WiFi → Cloud (Cat 4)