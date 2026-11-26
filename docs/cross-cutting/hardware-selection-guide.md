# Hardware Selection Guide

## Radio Module Selection Matrix

### Sub-GHz (Long Range)

| Module | Freq | Max Power | Sensitivity | Data Rate | Interface | Voltage | Best For |
|--------|------|-----------|-------------|-----------|-----------|---------|----------|
| **SX1262** | 868/915 MHz | +22 dBm | -148 dBm | 0.018-62.5 kbps | SPI | 1.8-3.7V | **LoRaMesher, Meshtastic (recommended)** |
| **SX1268** | 433/868 MHz | +22 dBm | -148 dBm | 0.018-62.5 kbps | SPI | 1.8-3.7V | EU 433MHz, CN 470MHz |
| **SX1276** | 868/915 MHz | +20 dBm | -148 dBm | 0.018-37.5 kbps | SPI | 1.8-3.7V | Legacy Meshtastic |
| **SX1278** | 433 MHz | +20 dBm | -148 dBm | 0.018-37.5 kbps | SPI | 1.8-3.7V | 433 MHz Meshtastic |
| **LR1121** | 868/915/2.4 GHz | +22 dBm | -148 dBm | 0.018-62.5 kbps | SPI | 1.8-3.7V | Multi-band + GNSS |
| **SX1280** | 2.4 GHz | +13 dBm | -132 dBm | 0.018-202 kbps | SPI | 1.8-3.7V | Short range, ranging |
| **LLCC68** | 868/915 MHz | +22 dBm | -148 dBm | 0.018-62.5 kbps | SPI | 1.8-3.7V | Cost-optimized SX1262 |

### 2.4 GHz (Short Range, Higher Throughput)

| Module | Standard | Max Rate | Sensitivity | Interface | Best For |
|--------|----------|----------|-------------|-----------|----------|
| **ESP32-S3** | WiFi 4 (802.11n) | 150 Mbps | -97 dBm | Internal | Babel, 802.11s, WireGuard |
| **ESP32-C6** | WiFi 6 (802.11ax) | 287 Mbps | -98 dBm | Internal | WiFi 6 mesh, Thread + WiFi |
| **ESP32-P4** | WiFi 6 + 802.11n | 574 Mbps | -98 dBm | Internal | High-perf mesh, WireGuard |
| **ESP32-H2** | 802.15.4 + BLE 5.3 | 250 kbps / 2 Mbps | -103 dBm | Internal | Thread, Zigbee, BLE Mesh |
| **ESP32-C3** | WiFi 4 + BLE 5.0 | 150 Mbps / 2 Mbps | -97 dBm | Internal | WiFi + BLE Mesh |
| **nRF52840** | 802.15.4 + BLE 5.2 | 250 kbps / 2 Mbps | -103 dBm | External | Thread, Zigbee, BLE Mesh (Nordic) |
| **CC2652P7** | 802.15.4 + BLE 5.2 | 250 kbps / 2 Mbps | -103 dBm | External | Zigbee Coordinator (TI) |
| **EFR32MG21/24** | 802.15.4 + BLE 5.2 | 250 kbps / 2 Mbps | -103 dBm | External | Thread, Zigbee (Silicon Labs) |

## MCU Selection Matrix

### ESP32 Family

| MCU | Cores | Freq | RAM | Flash | Radio | Best For |
|-----|-------|------|-----|-------|-------|----------|
| **ESP32** | 2 | 240 MHz | 520 KB | 4-16 MB | WiFi 4 + BLE 4.2 | Meshtastic, BLE Mesh, basic WiFi |
| **ESP32-S2** | 1 | 240 MHz | 320 KB | 4-16 MB | WiFi 4 | WiFi only (no BLE) |
| **ESP32-S3** | 2 | 240 MHz | 512 KB | 8-16 MB | WiFi 4 + BLE 5.3 | **Babel, 802.11s, WireGuard, BLE Mesh** |
| **ESP32-C3** | 1 | 160 MHz | 400 KB | 4-16 MB | WiFi 4 + BLE 5.0 | WiFi + BLE Mesh, low cost |
| **ESP32-C6** | 1 | 160 MHz | 512 KB | 4-16 MB | WiFi 6 + BLE 5.3 + 802.15.4 | **Thread + WiFi, Zigbee + WiFi** |
| **ESP32-H2** | 1 | 96 MHz | 320 KB | 4-16 MB | 802.15.4 + BLE 5.3 | **Thread, Zigbee, BLE Mesh (no WiFi)** |
| **ESP32-P4** | 2 | 400 MHz | 768 KB | 32 MB | WiFi 6 + 802.11n | **High-perf mesh, WireGuard, video** |

### Non-ESP32 Options

| MCU | Cores | Freq | RAM | Radio | Best For |
|-----|-------|------|-----|-------|----------|
| **nRF52840** | 1 (Cortex-M4) | 64 MHz | 256 KB | 802.15.4 + BLE 5.2 | Thread, Zigbee, BLE Mesh (Nordic) |
| **nRF5340** | 2 (M4+M33) | 128/64 MHz | 512/256 KB | 802.15.4 + BLE 5.4 | Advanced Thread/Zigbee |
| **CC2652P7** | 1 (Cortex-M4) | 48 MHz | 80 KB | 802.15.4 + BLE 5.2 | Zigbee Coordinator, Router |
| **EFR32MG21** | 1 (Cortex-M33) | 76 MHz | 128 KB | 802.15.4 + BLE 5.2 | Thread, Zigbee (Silicon Labs) |
| **EFR32MG24** | 1 (Cortex-M33) | 76 MHz | 256 KB | 802.15.4 + BLE 5.3 | Matter/Thread, Zigbee |
| **STM32WL** | 1 (Cortex-M4) | 48 MHz | 64 KB | Sub-GHz (LoRa) | LoRaWAN, LoRaMesher |
| **RP2040** | 2 (Cortex-M0+) | 133 MHz | 264 KB | None (external) | Meshtastic (RP2040 port) |

## Board Recommendations by Protocol

### LoRaMesher / Meshtastic (Category 1)

| Priority | Board | MCU | Radio | Price | Notes |
|----------|-------|-----|-------|-------|-------|
| **1st** | Heltec WiFi LoRa 32 V3 | ESP32-S3 | SX1262 | $25-35 | **Best overall**: TCXO, USB-C, good RF |
| **2nd** | LILYGO T3 S3 v1.x | ESP32-S3 | SX1262 | $20-30 | Good alternative, USB-C |
| **3rd** | TTGO T-Beam v1.1 | ESP32 | SX1276 | $25-30 | 18650 holder, legacy but proven |
| **4th** | RAK4631 | nRF52840 | SX1262 | $40-50 | Meshtastic only (nRF52 port) |
| **Custom** | ESP32-S3 + SX1262 module | ESP32-S3 | SX1262 | $15-20 | Production volume |

### OpenThread / Thread (Category 2)

| Priority | Board | MCU | Radio | Price | Notes |
|----------|-------|-----|-------|-------|-------|
| **1st** | ESP32-H2 DevKit | ESP32-H2 | 802.15.4 | $15-20 | **Native Thread**, lowest cost |
| **2nd** | ESP32-C6 DevKit | ESP32-C6 | 802.15.4 + WiFi | $18-25 | Thread + WiFi dual |
| **3rd** | nRF52840 DK | nRF52840 | 802.15.4 | $40-50 | Reference design |
| **4th** | Silicon Labs xG24 DevKit | EFR32MG24 | 802.15.4 | $50-80 | Matter ready |

### Zigbee (Category 2)

| Priority | Board | MCU | Radio | Price | Notes |
|----------|-------|-----|-------|-------|-------|
| **1st** | ESP32-H2 DevKit | ESP32-H2 | 802.15.4 | $15-20 | **Native Zigbee** |
| **2nd** | ESP32-C6 DevKit | ESP32-C6 | 802.15.4 + WiFi | $18-25 | Zigbee + WiFi bridge |
| **3rd** | CC2652P7 USB Stick | CC2652P7 | 802.15.4 | $25-35 | **Best Coordinator** for HA |
| **4th** | EFR32MG21/24 | Silicon Labs | 802.15.4 | $30-60 | Production Zigbee |

### BLE Mesh (Category 2)

| Priority | Board | MCU | Radio | Price | Notes |
|----------|-------|-----|-------|-------|-------|
| **1st** | ESP32-S3 DevKitC-1 | ESP32-S3 | BLE 5.3 | $12-18 | **Best BLE 5.3**, long range |
| **2nd** | ESP32-C3 DevKit | ESP32-C3 | BLE 5.0 | $8-12 | Low cost |
| **3rd** | ESP32 DevKitC | ESP32 | BLE 4.2 | $10-15 | Basic BLE Mesh |
| **4th** | nRF52840 DK | nRF52840 | BLE 5.2 | $40-50 | Reference |

### Babel / 802.11s / WireGuard (Category 3/4)

| Priority | Board | MCU | Radio | Price | Notes |
|----------|-------|-----|-------|-------|-------|
| **1st** | ESP32-S3 DevKitC-1 | ESP32-S3 | WiFi 4 + BLE 5.3 | $12-18 | **Best WiFi mesh** |
| **2nd** | ESP32-C6 DevKit | ESP32-C6 | WiFi 6 + BLE 5.3 | $18-25 | WiFi 6 mesh |
| **3rd** | ESP32-P4 DevKit | ESP32-P4 | WiFi 6 + 802.11n | $30-50 | High performance |
| **4th** | Raspberry Pi CM4 | BCM2711 | WiFi 5/6 + GbE | $40-80 | **Best for BIRD2, WireGuard kernel** |

### BIRD2 / WireGuard Kernel (Category 4)

| Priority | Board | MCU/CPU | Interfaces | Price | Notes |
|----------|-------|---------|------------|-------|-------|
| **1st** | Raspberry Pi CM4 | BCM2711 (4x A72) | GbE, WiFi 5, PCIe | $40-80 | **Full Linux, BIRD2, WireGuard kernel** |
| **2nd** | OpenWrt Router (MT7986) | MediaTek Filogic 820 | 2.5GbE x2, WiFi 6 | $80-150 | **Production router** |
| **3rd** | OpenWrt Router (QCA IPQ807x) | Qualcomm | 10GbE, WiFi 6E | $200-400 | High-end |
| **4th** | x86 Mini PC | Intel N100/12th Gen | 2.5GbE x2+ | $150-300 | **Best for BIRD2, FRR, WireGuard** |

## Antenna Selection

### Sub-GHz (868/915 MHz)

| Type | Gain | Pattern | Connector | Price | Use Case |
|------|------|---------|-----------|-------|----------|
| **1/4 Wave Whip** | 2-3 dBi | Omnidirectional | SMA | $3-8 | Mobile, general |
| **1/2 Wave Dipole** | 5-6 dBi | Omnidirectional | SMA | $10-20 | Fixed base |
| **Collinear (3dB)** | 5-6 dBi | Omnidirectional | N/SMA | $20-40 | Base station |
| **Yagi (3-el)** | 7-9 dBi | Directional | N/SMA | $25-50 | Point-to-point |
| **Yagi (6-el)** | 10-12 dBi | Directional | N | $40-80 | Long PtP |
| **Patch** | 8-10 dBi | Directional | SMA | $30-60 | Sector |
| **Helical** | 2-3 dBi | Omnidirectional | SMA | $5-15 | Compact |

### 2.4 GHz (WiFi/BLE/Thread/Zigbee)

| Type | Gain | Pattern | Connector | Price | Use Case |
|------|------|---------|-----------|-------|----------|
| **PCB Antenna** | 0-2 dBi | Omnidirectional | U.FL/IPEX | Included | Built-in |
| **1/2 Wave Dipole** | 2-3 dBi | Omnidirectional | SMA/U.FL | $5-15 | External |
| **Patch** | 6-8 dBi | Directional | U.FL/IPEX | $10-25 | PtP, sector |
| **Yagi** | 10-15 dBi | Directional | SMA/N | $30-80 | Long PtP |
| **Sector Panel** | 12-15 dBi | 60-120° | N | $50-150 | Sector coverage |

### Antenna Cables (Critical for Sub-GHz)

| Cable Type | Loss @ 900 MHz (dB/m) | Max Length | Connector | Price/m |
|------------|----------------------|------------|-----------|---------|
| **RG178** | 1.2 | < 1m | IPEX/U.FL | $2-5 |
| **RG316** | 0.8 | < 2m | IPEX/SMA | $3-8 |
| **RG58** | 0.5 | < 5m | SMA/N | $2-5 |
| **LMR-195** | 0.3 | < 10m | SMA/N | $5-10 |
| **LMR-400** | 0.15 | < 30m | N | $10-20 |

**Rule**: Keep cables **as short as possible**. Every 1 dB loss = ~20% range reduction.

## Power Supply Design

### Battery Selection

| Battery | Voltage | Capacity | Chemistry | Best For |
|---------|---------|----------|-----------|----------|
| **18650 Li-ion** | 3.7V | 2000-3500 mAh | Li-ion | LoRaMesher, Meshtastic (1+ year) |
| **21700 Li-ion** | 3.7V | 4000-5000 mAh | Li-ion | Extended LoRa |
| **LiFePO4 14500** | 3.2V | 600-800 mAh | LiFePO4 | Safe, long cycle life |
| **LiPo Pouch** | 3.7V | 500-5000 mAh | LiPo | Custom form factor |
| **AA Li-FeS2** | 1.5V×2=3V | 3000 mAh | Li-FeS2 | Non-rechargeable, 10yr shelf |
| **Supercapacitor** | 2.7-5.5V | 0.1-10 F | EDLC | Energy harvesting |

### Solar Charging

```c
// Panel sizing formula:
// Panel_Current = (Daily_mAh × 1.5) / Peak_Sun_Hours

// Example: 10 mAh/day, 4h sun → 3.75 mA @ 5V = 19 mW panel
// Practical: 0.5W-1W panel (5V) with MPPT

// Charge Controllers:
// - TP4056: Simple, ~5V panel, no MPPT
// - LTC3105/LTC3108: MPPT, works with small panels
// - CN3791: MPPT, 5-28V panel
// - BQ24074: MPPT, I2C control

// Panel Recommendations:
// - 0.5W 5V: TP4056, indoor/low light
// - 1W 5V: TP4056/LTC3105, general outdoor
// - 2W 6V: LTC3105/CN3791, reliable outdoor
// - 5W 6V: CN3791/BQ24074, high power
```

## Enclosure & Environmental

### IP Rating Selection

| Environment | Min IP | Recommendation |
|-------------|--------|----------------|
| Indoor | IP20 | Open frame / project box |
| Outdoor covered | IP54 | Junction box with gland |
| Outdoor exposed | IP67 | Waterproof enclosure |
| Buried/Submerged | IP68 | Potted / specialized |

### Recommended Enclosures

| Type | IP | Size | Mounting | Price |
|------|----|------|----------|-------|
| Polycarbonate junction box | IP66 | 100×100×50mm | Wall/pole | $8-15 |
| ABS project box | IP54 | 120×80×55mm | Wall | $5-10 |
| Aluminum die-cast | IP67 | 100×100×60mm | Wall/pole | $15-30 |
| PVC electrical box | IP65 | 86×86×50mm | Surface | $3-8 |
| Pelican case (small) | IP67 | 190×125×85mm | Portable | $30-50 |

### Thermal Management

- **TX heat**: 120mA @ 3.3V = 400mW during TX
- **Solar load**: White enclosure, shade
- **Ventilation**: Gortex vent (IP67 breathable)

## Cost Comparison (Per Node)

| Configuration | Radio | Board | Antenna | Battery | Enclosure | Total |
|---------------|-------|-------|---------|---------|-----------|-------|
| **Minimal LoRaMesher** | SX1262 module | Custom PCB | Whip | 18650 | Junction box | **$25-35** |
| **Meshtastic Ready** | On-board | Heltec V3 | Whip | LiPo | Included | **$30-40** |
| **Long Range Base** | SX1262 | Custom | Yagi 9dBi | 21700 | Aluminum | **$60-100** |
| **Solar Gateway** | SX1262 | Custom | Dipole | LiFePO4 + 1W solar | IP67 box | **$80-150** |
| **Thread/Zigbee Node** | Internal | ESP32-H2 DevKit | PCB | LiPo | 3D printed | **$20-30** |
| **BLE Mesh Node** | Internal | ESP32-S3 DevKit | PCB | LiPo | 3D printed | **$15-25** |
| **WiFi Mesh Node** | Internal | ESP32-S3 DevKit | PCB | USB power | 3D printed | **$15-25** |
| **WireGuard Gateway** | Internal | RPi CM4 + Carrier | Ethernet | Mains | DIN rail | **$80-150** |
| **BIRD2 Router** | Internal | x86 Mini PC | GbE x2+ | Mains | Rack/desktop | **$200-400** |

## Decision Matrix

| Requirement | Recommended Hardware |
|-------------|---------------------|
| **Lowest cost LoRa** | Custom ESP32 + SX1262 module ($15-20) |
| **Easiest LoRa start** | Heltec V3 or LILYGO T3 S3 ($25-35) |
| **Meshtastic community** | TTGO T-Beam v1.1 ($25-30) |
| **Maximum LoRa range** | SX1262 + Yagi 9dBi + 22dBm + SF12 |
| **Battery 1+ year LoRa** | ESP32 + SX1262 + 18650 + deep sleep + SF7 |
| **Thread/Zigbee native** | ESP32-H2 DevKit ($15-20) |
| **Thread + WiFi bridge** | ESP32-C6 DevKit ($18-25) |
| **Best Zigbee Coordinator** | CC2652P7 USB Stick ($25-35) |
| **BLE Mesh + long range** | ESP32-S3 DevKit ($12-18) |
| **WiFi Mesh (Babel/802.11s)** | ESP32-S3 DevKit ($12-18) |
| **WireGuard Gateway** | RPi CM4 + Carrier ($80-150) |
| **BIRD2/OSPF/BGP Router** | x86 Mini PC ($200-400) |
| **Production LoRa (1000+)** | Custom PCB: ESP32-S3 + SX1262 |
| **Production Thread/Zigbee** | Custom PCB: ESP32-H2/C6 |
| **Production WiFi Mesh** | Custom PCB: ESP32-S3/C6/P4 |

## Regulatory Checklist by Region

### LoRa/Sub-GHz

| Region | Band | Max EIRP | Duty Cycle | Channels |
|--------|------|----------|------------|----------|
| **EU (CEPT)** | 868 MHz | 14 dBm (25 mW) | 1% / 0.1% | 8 ch |
| **US (FCC)** | 915 MHz | 30 dBm (1 W) | None | 64 ch |
| **AU/NZ** | 915 MHz | 30 dBm (1 W) | None | 64 ch |
| **CN** | 470 MHz | 20 dBm (100 mW) | 1% | 12 ch |
| **JP** | 920 MHz | 14 dBm (25 mW) | None | 13 ch |
| **IN** | 865 MHz | 30 dBm | None | 10 ch |
| **RU** | 868 MHz | 14 dBm | 1% | 8 ch |

### WiFi/Bluetooth/Thread/Zigbee (2.4 GHz)

| Region | Channels | Max EIRP | Notes |
|--------|----------|----------|-------|
| **US (FCC)** | 1-11 | 30 dBm (1 W) | |
| **EU (ETSI)** | 1-13 | 20 dBm (100 mW) | |
| **JP** | 1-14 | 20 dBm (100 mW) | Ch 14 802.11b only |
| **CN** | 1-13 | 20 dBm | SRRC certification |
| **CA** | 1-11 | 30 dBm | ISED |
| **AU/NZ** | 1-13 | 20 dBm | RCM |

### WiFi 5/6 GHz

| Region | 5 GHz Channels | 6 GHz Channels | Max EIRP |
|--------|----------------|----------------|----------|
| **US** | 36-165 | 1-233 (AFC) | 30 dBm |
| **EU** | 36-165 | 1-193 (LPI) | 23 dBm |
| **JP** | 36-165 | - | 20 dBm |

---

## Next Steps

1. **Prototype**: Start with dev kit for your protocol
2. **Validate**: Range test with 2 nodes
3. **Optimize**: Antenna, power, firmware config
4. **Scale**: Design custom PCB for production
5. **Certify**: Regulatory testing for target markets