# Hardware Recommendations - Category 1 (LoRa Long Range)

## Radio Module Selection Guide

### Semtech SX1262 (Recommended)
| Parameter | Value |
|-----------|-------|
| **Frequency** | 150-960 MHz (multi-band) |
| **Max Power** | +22 dBm |
| **Sensitivity** | -148 dBm @ SF12, BW125 |
| **Interface** | SPI (up to 10 MHz) |
| **TCXO** | Built-in 32 MHz ±1 ppm |
| **DCDC** | Integrated buck/boost |
| **Current (TX 22dBm)** | 120 mA |
| **Current (RX)** | 4.6 mA |
| **Sleep Current** | 0.6 µA |
| **Package** | 4×4 mm QFN28 |
| **Best For** | New designs, best performance |

**Boards with SX1262:**
- Heltec WiFi LoRa 32 V3 (ESP32-S3)
- LILYGO T3 S3 v1.x (ESP32-S3)
- RAKwireless RAK4631 (nRF52840)
- Seeed Studio Wio-WM1110 (STM32WL)
- Custom: SX1262 module + ESP32

### Semtech SX1268
| Parameter | Value |
|-----------|-------|
| **Frequency** | 150-510 MHz (433/470 MHz bands) |
| **Max Power** | +22 dBm |
| **Sensitivity** | -148 dBm @ SF12, BW125 |
| **Other** | Same as SX1262 but lower frequency |

**Best For:** EU 433 MHz, China 470 MHz

### Semtech SX1276 (Legacy)
| Parameter | Value |
|-----------|-------|
| **Frequency** | 137-1020 MHz |
| **Max Power** | +20 dBm |
| **Sensitivity** | -148 dBm @ SF12, BW125 |
| **Interface** | SPI |
| **TCXO** | External required |
| **Current (TX 20dBm)** | 120 mA |
| **Current (RX)** | 10 mA |
| **Sleep Current** | 1.5 µA |
| **Package** | 4×4 mm QFN28 |

**Boards with SX1276:**
- TTGO T-Beam v1.1/v1.2
- Heltec WiFi LoRa 32 V1/V2
- M5Stack CoreLoRa
- RAK811 (module)

### Semtech SX1278 (433 MHz)
| Parameter | Value |
|-----------|-------|
| **Frequency** | 137-525 MHz |
| **Other** | Same as SX1276, optimized for 433 MHz |

### Semtech SX1280 (2.4 GHz)
| Parameter | Value |
|-----------|-------|
| **Frequency** | 2400-2500 MHz |
| **Max Power** | +13 dBm |
| **Sensitivity** | -132 dBm @ SF12, BW1600 |
| **Data Rate** | Up to 2.6 Mbps (FLRC) |
| **Range** | ~1-2 km (LoRa), ~500m (FLRC) |
| **Interface** | SPI |
| **Current (TX 13dBm)** | 35 mA |
| **Sleep Current** | 0.6 µA |

**Best For:** Short range, high throughput, ranging

### Semtech LR1121 (Multi-band + GNSS)
| Parameter | Value |
|-----------|-------|
| **Frequency** | 150-960 MHz + 2.4 GHz |
| **GNSS** | GPS/BeiDou/Galileo |
| **Max Power** | +22 dBm (sub-GHz), +13 dBm (2.4 GHz) |
| **Interface** | SPI + I2C (GNSS) |
| **Best For** | Asset tracking, geolocation |

---

## ESP32 Board Comparison

| Board | MCU | Radio | Antenna | Battery | USB | Best For |
|-------|-----|-------|---------|---------|-----|----------|
| **Heltec V3** | ESP32-S3 | SX1262 | IPEX | 2-pin JST | USB-C | LoRaMesher, Meshtastic |
| **LILYGO T3 S3** | ESP32-S3 | SX1262 | IPEX | 2-pin JST | USB-C | LoRaMesher, Meshtastic |
| **TTGO T-Beam v1.1** | ESP32 | SX1276 | SMA | 18650 holder | Micro-USB | Meshtastic, legacy |
| **Heltec V2** | ESP32 | SX1276 | IPEX | 2-pin JST | Micro-USB | Meshtastic |
| **M5Stack CoreLoRa** | ESP32 | SX1276 | Built-in | Internal | USB-C | Prototyping |
| **RAK4631** | nRF52840 | SX1262 | IPEX | 2-pin JST | USB-C | Meshtastic (nRF52) |
| **Custom SX1262** | ESP32/ESP32-S3 | SX1262 | Your choice | Your choice | Your choice | Production |

---

## Antenna Selection

### 868/915 MHz (Sub-GHz)

| Type | Gain | Pattern | Connector | Price | Use Case |
|------|------|---------|-----------|-------|----------|
| **1/4 Wave Whip** | 2-3 dBi | Omni | SMA | $3-8 | General, mobile |
| **1/2 Wave Dipole** | 5-6 dBi | Omni | SMA | $10-20 | Fixed base station |
| **Collinear (3dB)** | 5-6 dBi | Omni | N/SMA | $20-40 | Base station |
| **Yagi (3-el)** | 7-9 dBi | Directional | N/SMA | $25-50 | Point-to-point |
| **Yagi (6-el)** | 10-12 dBi | Directional | N | $40-80 | Long distance PtP |
| **Panel/Patch** | 8-10 dBi | Directional | N/SMA | $30-60 | Sector coverage |
| **Helical** | 2-3 dBi | Omni | SMA | $5-15 | Compact, mobile |

### 433 MHz
| Type | Gain | Pattern | Connector | Use Case |
|------|------|---------|-----------|----------|
| **1/4 Wave Whip** | 2 dBi | Omni | SMA | General |
| **1/2 Wave Dipole** | 5 dBi | Omni | SMA | Base station |
| **Yagi** | 8-10 dBi | Directional | N | PtP links |

### 2.4 GHz (SX1280)
| Type | Gain | Pattern | Connector | Use Case |
|------|------|---------|-----------|----------|
| **PCB Antenna** | 0-2 dBi | Omni | U.FL/IPEX | Built-in |
| **Patch** | 6-8 dBi | Directional | U.FL/IPEX | Short PtP |
| **Yagi** | 10-15 dBi | Directional | SMA/N | Long PtP |

---

## Antenna Connection Guide

### IPEX/U.FL to SMA
```
Radio Module (IPEX) ──► IPEX-to-SMA pigtail ──► Antenna (SMA)
```
- Use **low-loss cable** (RG316, RG178, or better)
- Keep cable **short** (<30 cm) for sub-GHz
- **Impedance match**: 50Ω throughout

### Direct PCB Antenna
```
Radio Module ──► π-network ──► PCB trace ──► Antenna
```
- Requires **tuning** (network analyzer)
- Follow vendor reference design
- SX1262: Semtech AN1200.48 reference design

### Ground Plane Requirements
- **Minimum**: λ/4 radius (8.6 cm @ 868 MHz, 8.2 cm @ 915 MHz)
- **Ideal**: λ/2 radius or larger
- **Mobile**: Use device body as ground (limited)
- **Base station**: Radials or large metal surface

---

## Power Supply Design

### Battery Options

| Battery | Voltage | Capacity | Pros | Cons |
|---------|---------|----------|------|------|
| **18650 Li-ion** | 3.7V | 2000-3500 mAh | High capacity, rechargeable | Needs holder, protection |
| **21700 Li-ion** | 3.7V | 4000-5000 mAh | Higher capacity | Larger |
| **LiFePO4 14500** | 3.2V | 600-800 mAh | Safe, long life | Lower voltage, capacity |
| **LiPo Pouch** | 3.7V | 500-5000 mAh | Flexible form factor | Needs protection PCB |
| **AA Li-FeS2** | 1.5V×2=3V | 3000 mAh | Long shelf life | Non-rechargeable |
| **Supercapacitor** | 2.7-5.5V | 0.1-10 F | Fast charge, long life | Low energy density |

### Power Management

#### TTGO T-Beam (AXP192 PMU)
```cpp
// Battery voltage reading
float getBatteryVoltage() {
    // AXP192 ADC: BAT voltage register
    // Via I2C: 0x34, reg 0x78-0x79
    return axp.getBattVoltage();  // mV
}

// Charge current setting
axp.setChgCur(AXP202_CHG_CUR_500MA);  // 100-1000mA

// Power path management
axp.setPowerOutPut(AXP192_LDO2, true);  // LoRa power
axp.setPowerOutPut(AXP192_LDO3, true);  // GPS power
```

#### Heltec V3 / LILYGO T3 S3 (No PMU)
```cpp
// Direct battery to ESP32-S3 (with protection circuit)
// ADC reading on GPIO 1-5 (ADC1)
float getBatteryVoltage() {
    int raw = analogRead(BAT_PIN);
    return raw * 3.3 / 4095.0 * DIVIDER_RATIO;
}

// External charging IC recommended (TP4056, BQ24074, etc.)
```

### Solar Charging
```cpp
// Solar panel sizing (for 24/7 operation)
// Panel = (Daily consumption × 1.5) / Peak sun hours
// Example: 10 mAh/day, 4h sun → 3.75 mA panel @ 5V = 19 mW
// Practical: 0.5W-1W panel (5V) with TP4056/LTC3105

// LTC3105 (MPPT, works with small panels)
// TP4056 (simple, needs ~5V panel)
```

---

## Enclosure & Environmental

### IP Rating Selection
| Environment | Min IP Rating | Recommendation |
|-------------|---------------|----------------|
| Indoor | IP20 | Open frame / project box |
| Outdoor covered | IP54 | Junction box with gland |
| Outdoor exposed | IP67 | Waterproof enclosure |
| Buried/Submerged | IP68 | Potted / specialized |

### Recommended Enclosures
| Type | IP | Size | Mounting | Price |
|------|----|------|----------|-------|
| **Polycarbonate junction box** | IP66 | 100×100×50mm | Wall/pole | $8-15 |
| **ABS project box** | IP54 | 120×80×55mm | Wall | $5-10 |
| **Aluminum die-cast** | IP67 | 100×100×60mm | Wall/pole | $15-30 |
| **PVC electrical box** | IP65 | 86×86×50mm | Surface | $3-8 |
| **Pelican case (small)** | IP67 | 190×125×85mm | Portable | $30-50 |

### Antenna Mounting
- **Through enclosure**: N/SMA bulkhead connector
- **External**: N/SMA cable gland + pigtail
- **Internal**: PCB antenna (if plastic enclosure)
- **Pole mount**: U-bolt + antenna bracket

### Thermal Management
- **TX heat**: 120mA @ 3.3V = 400mW during TX
- **Solar load**: White enclosure, shade
- **Ventilation**: Gortex vent (IP67 breathable)

---

## PCB Design Guidelines (Custom Boards)

### SX1262 Layout (Critical)
```
Reference: Semtech AN1200.48 SX1261/62/68 Layout Guidelines
```

**Key Rules:**
1. **RF Trace**: 50Ω controlled impedance (CPWG or microstrip)
2. **Ground**: Solid pour under RF, stitching vias every λ/20
3. **Decoupling**: 100nF + 10µF at each VDD pin (close!)
4. **TCXO**: Keep away from switching regulators
5. **Crystal**: 32 MHz TCXO, 1.8V or 3.3V per module
6. **RF Switch**: If needed (TX/RX), use low-loss (PE4259, SKY13351)
7. **Matching Network**: π-network at antenna (tune with VNA)

### ESP32 + SX1262 Schematic (Minimal)
```
ESP32-S3                          SX1262
┌─────────────┐                  ┌─────────────┐
│ GPIO 7   ───┼──► NSS          │
│ GPIO 8   ───┼──► RST          │
│ GPIO 9   ───┼──► DIO1 (IRQ)   │
│ GPIO 33  ◄──┼──◄ BUSY         │
│ GPIO 11  ───┼──► MOSI         │
│ GPIO 13  ◄──┼──◄ MISO         │
│ GPIO 12  ───┼──► SCK          │
│            │                  │
│ 3.3V  ──────┼──► VDD, VDDIO   │
│ GND   ──────┼──► GND          │
└─────────────┘                  └─────────────┘
```

### BOM (Bill of Materials) - Minimal
| Qty | Part | Value | Package | Notes |
|-----|------|-------|---------|-------|
| 1 | ESP32-S3-WROOM-1 | - | Module | 16MB flash, 8MB PSRAM |
| 1 | SX1262 | - | QFN28 | LoRa transceiver |
| 1 | TCXO | 32 MHz, 1.8V | 2.5×2.0mm | ±1 ppm, clipped sine |
| 1 | Inductor | 4.7 µH | 0603 | DCDC (SX1262) |
| 2 | Capacitor | 10 µF | 0603 | VDD decoupling |
| 4 | Capacitor | 100 nF | 0402 | VDD pin decoupling |
| 1 | Capacitor | 1 µF | 0402 | TCXO supply |
| 1 | Crystal | 32.768 kHz | 2×6mm | ESP32 RTC |
| 1 | USB-C | - | - | Power/programming |
| 1 | LDO | 3.3V, 500mA | SOT-23 | ESP32 supply |
| 1 | Battery connector | JST-PH 2pin | - | LiPo/Li-ion |
| 1 | Protection IC | DW01+FS8205 | - | Battery protection |

---

## Testing & Validation Equipment

### Essential
| Tool | Purpose | Budget Option |
|------|---------|---------------|
| **SDR (RTL-SDR)** | Spectrum monitoring | $25 |
| **LoRa Sniffer** | Packet capture | Meshtastic device + serial |
| **Multimeter** | Voltage/current | $15 |
| **USB Power Meter** | USB current/voltage | $10 |

### Recommended
| Tool | Purpose | Budget Option |
|------|---------|---------------|
| **VNA (NanoVNA)** | Antenna tuning | $50 |
| **Spectrum Analyzer** | Regulatory compliance | $300+ (TinySA) |
| **Oscilloscope** | Signal integrity | $100+ |
| **Current Probe** | Sleep current measurement | $50+ |

### Test Procedures

#### 1. Link Budget Verification
```bash
# Measure RSSI/SNR at various distances
# Expected: -148 dBm sensitivity (SF12)
# Link budget = TX_power + TX_antenna + RX_antenna - Path_loss - Margin
# Path loss (free space) = 20log(d) + 20log(f) - 147.55
# d=km, f=MHz
```

#### 2. Range Test
```bash
# Two nodes: one fixed (gateway), one mobile
# Record: distance, RSSI, SNR, PDR, latency
# Test: urban, suburban, rural, line-of-sight
```

#### 3. Battery Life Test
```bash
# Configure: SF7, 1 msg/10min, deep sleep
# Measure: average current over 24h
# Calculate: battery_mAh / avg_mA = hours
```

#### 4. Regulatory Compliance
```bash
# Measure: EIRP, duty cycle, bandwidth, spurious emissions
# Tools: Spectrum analyzer + calibrated antenna
# Limits: ETSI EN 300 220 (EU), FCC 15.247 (US)
```

---

## Procurement Links (Reference)

### Modules
- **SX1262**: DigiKey, Mouser, LCSC (~$3-5)
- **SX1268**: DigiKey, Mouser, LCSC (~$3-5)
- **SX1276**: DigiKey, Mouser, LCSC (~$2-4)
- **LR1121**: DigiKey, Mouser (~$8-12)

### Boards
- **Heltec V3**: Heltec store, AliExpress, Amazon (~$25-35)
- **LILYGO T3 S3**: LILYGO store, AliExpress (~$20-30)
- **TTGO T-Beam**: TTGO store, AliExpress, Amazon (~$25-35)
- **RAK4631**: RAKwireless store, DigiKey (~$40-50)
- **M5Stack CoreLoRa**: M5Stack store, DigiKey (~$40)

### Antennas
- **Sub-GHz whip**: AliExpress, Amazon, DigiKey ($3-15)
- **Yagi**: Amazon, specialty RF ($25-80)
- **IPEX pigtails**: AliExpress, DigiKey ($1-3)

### Enclosures
- **Junction box**: Home Depot, Amazon, electrical supply ($8-20)
- **Project box**: Amazon, AliExpress ($5-15)

---

## Cost Comparison (Per Node)

| Configuration | Radio | Board | Antenna | Battery | Enclosure | Total |
|---------------|-------|-------|---------|---------|-----------|-------|
| **Minimal (LoRaMesher)** | SX1262 module | Custom PCB | Whip | 18650 | Junction box | **$25-35** |
| **Meshtastic Ready** | On-board | Heltec V3 | Whip | LiPo | Included | **$30-40** |
| **Long Range Base** | SX1262 | Custom | Yagi 9dBi | 21700 | Aluminum | **$60-100** |
| **Solar Gateway** | SX1262 | Custom | Dipole | LiFePO4 + 1W solar | IP67 box | **$80-150** |
| **Asset Tracker** | LR1121 | Custom | Patch | LiPo pouch | Potted | **$50-80** |

---

## Decision Matrix

| Requirement | Recommended Hardware |
|-------------|---------------------|
| **Lowest cost** | Custom ESP32 + SX1262 module ($15-20) |
| **Easiest start** | Heltec V3 or LILYGO T3 S3 ($25-35) |
| **Meshtastic community** | TTGO T-Beam v1.1 ($25-30) |
| **Maximum range** | SX1262 + Yagi + 22dBm + SF12 |
| **Battery 1+ year** | ESP32 + SX1262 + 18650 + deep sleep + SF7 |
| **Gateway (Mains)** | ESP32-S3 + SX1262 + Ethernet + Dipole |
| **Mobile/Portable** | LILYGO T3 S3 + LiPo + Whip |
| **Asset Tracking** | RAK4631 (nRF52) + LR1121 + GNSS |
| **Production (1000+)** | Custom PCB with ESP32-S3 + SX1262 |
| **EU 433 MHz** | SX1268 module + 433 MHz antenna |
| **US 915 MHz** | SX1262 + 915 MHz antenna (same HW) |
| **2.4 GHz Short Range** | SX1280 module + Patch antenna |

---

## Regulatory Checklist by Region

### EU (CE Mark)
- [ ] ETSI EN 300 220-1/2 (LoRa)
- [ ] ETSI EN 301 489-1/3 (EMC)
- [ ] EN 62368-1 (Safety)
- [ ] Duty cycle ≤ 1% (868 MHz) or 10% (433 MHz)
- [ ] EIRP ≤ 14 dBm (868) / 10 dBm (433)
- [ ] Declaration of Conformity
- [ ] User manual with restrictions

### US (FCC)
- [ ] FCC 15.247 (DSSS/FHSS)
- [ ] FCC 15.209 (Spurious emissions)
- [ ] EIRP ≤ 30 dBm (1W)
- [ ] 20 dB bandwidth ≤ 500 kHz or FHSS
- [ ] FCC ID application (if selling)
- [ ] Manual with FCC statement

### Canada (ISED)
- [ ] RSS-247 (DTS)
- [ ] RSS-Gen (General)
- [ ] IC certification

### Australia/NZ (RCM)
- [ ] AS/NZS 4268 (Radio)
- [ ] RCM mark

### Japan (MIC)
- [ ] ARIB STD-T108
- [ ] MIC certification

---

## Next Steps

1. **Prototype**: Start with Heltec V3 or LILYGO T3 S3
2. **Validate**: Range test with 2 nodes
3. **Optimize**: Antenna, power, firmware config
4. **Scale**: Design custom PCB for production
5. **Certify**: Regulatory testing for target markets