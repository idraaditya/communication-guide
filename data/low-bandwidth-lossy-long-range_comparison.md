# Low Bandwidth Lossy Long Range Protocol Comparison

| Attribute | LoRaMesher | Meshtastic | BATMAN-ADV (LoRa) |
|---|---|---|---|
| Architecture | TDMA + Distance Vector | Flooding + ReliableRouter | L2 Mesh (Kernel) |
| Layer | L3 (Application) | L3.5 (Mesh over LoRa) | L2 |
| Routing Algorithm | Distance Vector + ETX | Hybrid (Flood + On-demand) | OGM Flooding |
| Metric | ETX Cost (hop_count × 65536/quality) | Hop count + SNR/RSSI | TQ (Transmission Quality) |
| Max Data Rate | 0.018-62.5 kbps | 0.018-37.5 kbps | 0.018-62.5 kbps |
| Typical Range | 1-50+ km | 1-10+ km | 1-50+ km |
| Encryption | AES-128-CTR | AES-256-CTR | None (L2) |
| Authentication | AES-CMAC | AES-CMAC | None |
| Key Management | PSK / AppKey | PSK / QR code | N/A |
| Forward Secrecy | No | No | N/A |
| NAT Traversal | N/A | N/A | N/A |
| Roaming Support | Limited | Limited | Excellent (L2) |
| Multicast | Capability-based discovery | TTL flood broadcast | MCAST optimization |
| Fragmentation | Application layer | Application layer | Built-in |
| Security Level | Medium | Medium-High | Low (needs IPsec) |
| Maturity | v1.0 (2024) | v2.x (2024) | Stable (mainline kernel) |
| License | MIT | GPL-3.0 | GPL-2.0 |
| ESP32 Support | ✅ PlatformIO | ✅ ESP-IDF | ❌ Linux host |
| Best For | Battery, deterministic latency, long range | Human messaging, MQTT gateway, community | L2 transparency, roaming, wired backhaul |


## Quick Selection Guide

| Requirement | Recommended Protocol |
|-------------|---------------------|
| Battery + deterministic latency | LoRaMesher |
| Human messaging + MQTT + community | Meshtastic |
| L2 transparency + roaming | BATMAN-ADV (Linux host) |
