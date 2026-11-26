# Testing & Benchmarking Guide

## Test Methodology

### Test Categories

| Category | Purpose | Tools | Duration |
|----------|---------|-------|----------|
| **Unit Testing** | Protocol logic, packet parsing | GCC/Clang, GoogleTest | CI/CD |
| **Integration Testing** | Multi-node communication | Hardware testbed | Hours |
| **Performance Benchmarking** | Throughput, latency, PDR | Automated scripts | Days |
| **Stress Testing** | Max nodes, traffic, failures | Chaos engineering | Days |
| **Field Testing** | Real-world propagation | Mobile test nodes | Weeks |
| **Interop Testing** | Multi-vendor compatibility | Reference implementations | Ongoing |

---

## Testbed Setup

### Hardware Testbed

```
┌─────────────────────────────────────────────────────────────────┐
│                    TESTBED ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CONTROL NODE (Linux)                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Test Orchestrator (Python/Rust)                         │   │
│  │ - Deploy firmware                                       │   │
│  │ - Configure nodes                                       │   │
│  │ - Start/stop traffic generators                         │   │
│  │ - Collect metrics (serial, SSH, MQTT)                   │   │
│  │ - Analyze results                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ POWER MONITORING (Nordic PPK2 / Joulescope)             │   │
│  │ - Per-node current/voltage logging                      │   │
│  │ - Synchronized with test events                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ RF ENVIRONMENT                                          │   │
│  │ - Faraday cage (controlled)                             │   │
│  │ - Attenuators (simulate distance)                       │   │
│  │ - Interference generator (WiFi, BLE, microwave)         │   │
│  │ - Spectrum analyzer (verify channels)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  TEST NODES (5-50 nodes)                                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Node 1  │  │ Node 2  │  │ Node 3  │  │ ...     │           │
│  │ (DUT)   │  │ (Ref)   │  │ (Ref)   │  │         │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Software Test Framework

```python
# test_framework.py
import asyncio
import serial
import json
import time
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

@dataclass
class TestConfig:
    protocol: str
    node_count: int
    topology: str  # "line", "star", "mesh", "random"
    traffic_profile: str  # "periodic", "burst", "poisson"
    packet_size: int
    interval_ms: int
    duration_s: int
    metrics: List[str]

@dataclass
class NodeResult:
    node_id: str
    packets_sent: int
    packets_received: int
    packets_lost: int
    latency_ms: List[float]
    rssi_dbm: List[int]
    snr_db: List[float]
    current_ma: List[float]
    errors: List[str]

class TestOrchestrator:
    def __init__(self, config: TestConfig):
        self.config = config
        self.nodes: List[TestNode] = []
        self.results: Dict[str, NodeResult] = {}
    
    async def setup_nodes(self):
        """Flash firmware, configure network parameters"""
        for i in range(self.config.node_count):
            node = TestNode(f"node_{i}", f"/dev/ttyUSB{i}")
            await node.flash_firmware(self.config.protocol)
            await node.configure(self.get_node_config(i))
            self.nodes.append(node)
    
    async def run_test(self):
        """Execute test scenario"""
        # Start traffic generators
        tasks = [node.start_traffic(self.config) for node in self.nodes]
        await asyncio.gather(*tasks)
        
        # Wait for test duration
        await asyncio.sleep(self.config.duration_s)
        
        # Stop and collect results
        for node in self.nodes:
            await node.stop_traffic()
            self.results[node.node_id] = await node.get_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Compute aggregate metrics"""
        total_sent = sum(r.packets_sent for r in self.results.values())
        total_received = sum(r.packets_received for r in self.results.values())
        total_lost = sum(r.packets_lost for r in self.results.values())
        
        all_latencies = []
        all_rssi = []
        all_snr = []
        for r in self.results.values():
            all_latencies.extend(r.latency_ms)
            all_rssi.extend(r.rssi_dbm)
            all_snr.extend(r.snr_db)
        
        return {
            "pdr": total_received / total_sent if total_sent > 0 else 0,
            "throughput_kbps": (total_received * self.config.packet_size * 8) / 
                               (self.config.duration_s * 1000),
            "avg_latency_ms": sum(all_latencies) / len(all_latencies) if all_latencies else 0,
            "p99_latency_ms": sorted(all_latencies)[int(len(all_latencies) * 0.99)] if all_latencies else 0,
            "avg_rssi_dbm": sum(all_rssi) / len(all_rssi) if all_rssi else 0,
            "avg_snr_db": sum(all_snr) / len(all_snr) if all_snr else 0,
            "node_results": {k: vars(v) for k, v in self.results.items()}
        }

class TestNode:
    def __init__(self, node_id: str, port: str):
        self.node_id = node_id
        self.port = port
        self.serial = None
    
    async def flash_firmware(self, protocol: str):
        # Use esptool.py or platformio
        pass
    
    async def configure(self, config: dict):
        # Send config via serial/CLI
        pass
    
    async def start_traffic(self, test_config: TestConfig):
        # Send "start" command with parameters
        pass
    
    async def stop_traffic(self):
        # Send "stop" command
        pass
    
    async def get_results(self) -> NodeResult:
        # Query node for statistics
        pass
```

---

## Key Metrics

### Protocol Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| **PDR (Packet Delivery Ratio)** | Received / Sent | > 95% | End-to-end |
| **Throughput** | Application data rate | Protocol-dependent | kbps |
| **Latency (Avg/P50/P99)** | Time from send to receive | < 100ms (LoRa), < 10ms (WiFi) | ms |
| **Jitter** | Latency variation | < 20% of avg | ms |
| **RSSI** | Received Signal Strength | > -100 dBm (LoRa), > -70 dBm (WiFi) | dBm |
| **SNR** | Signal-to-Noise Ratio | > 5 dB (LoRa), > 20 dB (WiFi) | dB |
| **Convergence Time** | Route establishment | < 30s (LoRa), < 5s (WiFi) | s |
| **Route Stability** | Route changes per hour | < 1/hour | count/h |
| **Power Consumption** | Average current | Budget-dependent | mA |
| **Battery Life** | Time to cutoff | Target-dependent | days |

### Network Metrics

| Metric | Definition | Measurement |
|--------|------------|-------------|
| **Node Count** | Active nodes in network | Periodic census |
| **Hop Count Distribution** | Histogram of path lengths | Route table analysis |
| **Route Changes** | Route table modifications | Log monitoring |
| **Partition Events** | Network splits/merges | Heartbeat loss |
| **Control Overhead** | Management traffic % | Packet capture |
| **Collision Rate** | MAC layer collisions | Radio stats |

---

## Benchmark Scenarios

### Scenario 1: Static Line Topology (Range Test)

```
NODE_1 ─── NODE_2 ─── NODE_3 ─── NODE_4 ─── NODE_5
  (GW)     (1 hop)    (2 hops)    (3 hops)    (4 hops)

Parameters:
- Distance: 500m between nodes
- Traffic: 1 packet/min, 50 bytes, unicast to gateway
- Duration: 24 hours
- Metrics: PDR per hop, latency, battery drain
```

### Scenario 2: Grid Topology (Density Test)

```
NODE_1 ── NODE_2 ── NODE_3
  │        │        │
NODE_4 ── NODE_5 ── NODE_6
  │        │        │
NODE_7 ── NODE_8 ── NODE_9

Parameters:
- Distance: 300m between adjacent
- Traffic: 1 packet/30s, broadcast
- Duration: 12 hours
- Metrics: PDR, latency, route distribution, collisions
```

### Scenario 3: Mobile Node (Roaming Test)

```
MOBILE ──► AP_1 ── AP_2 ── AP_3 ── GW
   (walking/driving through coverage)

Parameters:
- Speed: 1 m/s (walk), 5 m/s (bike), 15 m/s (car)
- Handover: Between APs
- Traffic: Continuous 10 packets/s, 100 bytes
- Duration: 30 min per speed
- Metrics: Handover latency, packet loss during handover, reconnection time
```

### Scenario 4: Stress Test (Max Load)

```
50 NODES in 200m radius
- Traffic: 10 packets/s/node, 100 bytes
- Pattern: 50% unicast to GW, 30% broadcast, 20% random unicast
- Duration: 4 hours
- Metrics: PDR, latency distribution, queue drops, CPU/memory, crashes
```

### Scenario 5: Failure Recovery

```
10 NODES stable
- Fail: Power off 3 random nodes
- Observe: Route recovery, partition handling
- Restore: Power on nodes
- Observe: Rejoin time, route stabilization
- Metrics: Recovery time, PDR during recovery, route flaps
```

---

## Automated Test Scripts

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Protocol Tests

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * 0'  # Weekly

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: |
          cd protocols/loramesher
          pio test -e test_native -v
  
  integration-tests:
    runs-on: self-hosted  # Requires hardware
    steps:
      - uses: actions/checkout@v4
      - name: Setup testbed
        run: python scripts/setup_testbed.py
      - name: Run integration tests
        run: |
          python scripts/run_benchmarks.py \
            --protocol loramesher \
            --topology line \
            --nodes 5 \
            --duration 3600
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: results/

  performance-regression:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Run benchmarks
        run: python scripts/run_benchmarks.py --full-suite
      - name: Compare with baseline
        run: python scripts/compare_benchmarks.py
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            // Post benchmark comparison as PR comment
```

### Benchmark Runner

```python
# scripts/run_benchmarks.py
#!/usr/bin/env python3
import argparse
import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path

async def run_benchmark(protocol: str, config: dict) -> dict:
    """Run single benchmark configuration"""
    from test_framework import TestOrchestrator, TestConfig
    
    test_config = TestConfig(
        protocol=protocol,
        node_count=config['nodes'],
        topology=config['topology'],
        traffic_profile=config['traffic'],
        packet_size=config['packet_size'],
        interval_ms=config['interval_ms'],
        duration_s=config['duration'],
        metrics=['pdr', 'latency', 'throughput', 'rssi', 'snr', 'power']
    )
    
    orchestrator = TestOrchestrator(test_config)
    await orchestrator.setup_nodes()
    await orchestrator.run_test()
    results = orchestrator.analyze_results()
    
    # Add metadata
    results['config'] = config
    results['timestamp'] = datetime.now().isoformat()
    results['protocol'] = protocol
    
    return results

def save_results(results: dict, output_dir: Path):
    """Save results as JSON and CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON (full)
    json_file = output_dir / f"benchmark_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # CSV (summary)
    csv_file = output_dir / f"benchmark_{timestamp}.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'protocol', 'topology', 'nodes', 'packet_size', 'interval_ms',
            'pdr', 'throughput_kbps', 'avg_latency_ms', 'p99_latency_ms',
            'avg_rssi_dbm', 'avg_snr_db'
        ])
        writer.writerow([
            results['protocol'], results['config']['topology'],
            results['config']['nodes'], results['config']['packet_size'],
            results['config']['interval_ms'],
            results['pdr'], results['throughput_kbps'],
            results['avg_latency_ms'], results['p99_latency_ms'],
            results['avg_rssi_dbm'], results['avg_snr_db']
        ])

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocol', choices=['loramesher', 'meshtastic', 'babel', 'thread', 'zigbee', 'ble-mesh', 'wireguard'], required=True)
    parser.add_argument('--topology', choices=['line', 'grid', 'star', 'random'], default='line')
    parser.add_argument('--nodes', type=int, default=5)
    parser.add_argument('--traffic', choices=['periodic', 'burst', 'poisson'], default='periodic')
    parser.add_argument('--packet-size', type=int, default=50)
    parser.add_argument('--interval-ms', type=int, default=60000)
    parser.add_argument('--duration', type=int, default=3600)
    parser.add_argument('--output', type=Path, default=Path('results'))
    parser.add_argument('--full-suite', action='store_true')
    args = parser.parse_args()
    
    args.output.mkdir(parents=True, exist_ok=True)
    
    if args.full_suite:
        # Run full matrix
        configs = [
            {'topology': 'line', 'nodes': 5, 'traffic': 'periodic', 'packet_size': 50, 'interval_ms': 60000, 'duration': 3600},
            {'topology': 'line', 'nodes': 10, 'traffic': 'periodic', 'packet_size': 50, 'interval_ms': 60000, 'duration': 3600},
            {'topology': 'grid', 'nodes': 9, 'traffic': 'broadcast', 'packet_size': 50, 'interval_ms': 30000, 'duration': 7200},
            {'topology': 'random', 'nodes': 20, 'traffic': 'burst', 'packet_size': 100, 'interval_ms': 1000, 'duration': 14400},
        ]
    else:
        configs = [{
            'topology': args.topology,
            'nodes': args.nodes,
            'traffic': args.traffic,
            'packet_size': args.packet_size,
            'interval_ms': args.interval_ms,
            'duration': args.duration
        }]
    
    for config in configs:
        print(f"Running: {args.protocol} {config}")
        results = await run_benchmark(args.protocol, config)
        save_results(results, args.output)
        print(f"  PDR: {results['pdr']:.2%}, Latency: {results['avg_latency_ms']:.1f}ms, Throughput: {results['throughput_kbps']:.2f} kbps")

if __name__ == '__main__':
    asyncio.run(main())
```

---

## Field Testing Guide

### Preparation Checklist

- [ ] **Firmware**: Latest stable on all nodes
- [ ] **Configuration**: Identical network params (keys, channels, IDs)
- [ ] **Power**: Fresh batteries / charged power banks
- [ ] **Logging**: Enable debug logs, timestamp sync (NTP/GPS)
- [ ] **Labeling**: Physical labels on nodes (ID, role)
- [ ] **GPS**: Record positions for propagation analysis
- [ ] **Weather**: Note conditions (temp, humidity, rain)
- [ ] **Interference**: Spectrum scan before/after

### Data Collection Template

```csv
# field_log.csv
timestamp,node_id,event_type,peer_id,packet_id,rssi,snr,hop_count,latency_ms,lat,lon,alt,temp_c,humidity,battery_v,notes
2024-01-15T10:00:00Z,node_1,tx,node_2,pkt_001,,,1,,,40.7128,-74.0060,10,15,60,3.7,
2024-01-15T10:00:01Z,node_2,rx,node_1,pkt_001,-85,8,1,120,40.7130,-74.0058,12,15,60,3.6,
2024-01-15T10:00:02Z,node_2,tx,node_3,pkt_001,,,2,,,40.7130,-74.0058,12,15,60,3.6,
```

### Post-Processing

```python
# scripts/analyze_field_data.py
import pandas as pd
import numpy as np

def analyze_field_data(csv_file: str):
    df = pd.read_csv(csv_file)
    
    # PDR by distance
    tx = df[df['event_type'] == 'tx']
    rx = df[df['event_type'] == 'rx']
    
    # Match TX/RX by packet_id
    merged = pd.merge(tx[['packet_id','node_id','timestamp']], 
                      rx[['packet_id','node_id','rssi','snr','latency_ms']], 
                      on='packet_id', suffixes=('_tx','_rx'))
    
    # Calculate distance from GPS
    from geopy.distance import geodesic
    merged['distance_m'] = merged.apply(
        lambda r: geodesic((r['lat_tx'],r['lon_tx']), (r['lat_rx'],r['lon_rx'])).meters, axis=1)
    
    # PDR by distance bins
    merged['dist_bin'] = pd.cut(merged['distance_m'], bins=[0,500,1000,2000,5000,10000])
    pdr_by_dist = merged.groupby('dist_bin')['packet_id'].count().reset_index(name='received')
    
    # Link budget analysis
    merged['path_loss_db'] = 20*np.log10(merged['distance_m']) + 20*np.log10(915) - 147.55  # Free space
    merged['rx_expected_dbm'] = 14 - merged['path_loss_db']  # 14 dBm TX
    merged['margin_db'] = merged['rssi'] - merged['rx_expected_dbm']
    
    return {
        'pdr_overall': len(merged) / len(tx),
        'pdr_by_distance': pdr_by_dist.to_dict('records'),
        'avg_latency_ms': merged['latency_ms'].mean(),
        'avg_rssi_dbm': merged['rssi'].mean(),
        'avg_snr_db': merged['snr'].mean(),
        'margin_stats': {
            'mean': merged['margin_db'].mean(),
            'min': merged['margin_db'].min(),
            'std': merged['margin_db'].std()
        }
    }
```

---

## Interoperability Testing

### Multi-Vendor Matrix

| Test | Device A | Device B | Expected |
|------|----------|----------|----------|
| **Thread** | ESP32-H2 (OpenThread) | nRF52840 (OpenThread) | Full connectivity |
| **Thread** | ESP32-H2 | Silicon Labs xG24 | Full connectivity |
| **Thread** | ESP32-H2 | Thread Border Router (ot-br-posix) | Commissioning + routing |
| **Zigbee** | ESP32-H2 (ESP-Zigbee) | CC2652P7 (Z-Stack) | HA profile |
| **Zigbee** | ESP32-H2 | Silicon Labs EFR32MG21 | HA profile |
| **BLE Mesh** | ESP32-S3 (ESP-BLE-Mesh) | nRF52840 (Zephyr) | Generic OnOff |
| **BLE Mesh** | ESP32-S3 | Silicon Labs EFR32MG24 | Lighting models |
| **802.11s** | ESP32-S3 (mac80211) | OpenWrt router | Mesh peering |
| **Babel** | ESP32-S3 (babeld) | OpenWrt router (babeld) | Route exchange |
| **WireGuard** | ESP32-S3 (WireGuard-Go) | Linux (kernel WireGuard) | Tunnel + routing |

### Conformance Test Suites

- **Thread**: Thread Test Harness (TTH) - https://github.com/openthread/ot-th
- **Zigbee**: Zigbee Cluster Library Test Suite - CSA members only
- **BLE Mesh**: Bluetooth Mesh PTS - Bluetooth SIG members
- **WiFi**: Wi-Fi Alliance CTT - Wi-Fi Alliance members

---

## Reporting Template

```markdown
# Benchmark Report: {PROTOCOL} v{VERSION}

## Test Configuration
- **Date**: {DATE}
- **Protocol**: {PROTOCOL} {VERSION}
- **Hardware**: {BOARD} + {RADIO}
- **Firmware**: {GIT_COMMIT}
- **Topology**: {TOPOLOGY}
- **Nodes**: {COUNT}
- **Traffic**: {PROFILE} ({PACKET_SIZE}B every {INTERVAL}ms)
- **Duration**: {DURATION}s
- **Environment**: {LAB/FIELD} - {CONDITIONS}

## Results Summary
| Metric | Value | Target | Pass/Fail |
|--------|-------|--------|-----------|
| PDR | {PDR:.2%} | > 95% | {PASS/FAIL} |
| Throughput | {THROUGHPUT:.2f} kbps | > {TARGET} kbps | {PASS/FAIL} |
| Avg Latency | {LATENCY:.1f} ms | < {TARGET} ms | {PASS/FAIL} |
| P99 Latency | {P99:.1f} ms | < {TARGET} ms | {PASS/FAIL} |
| Avg RSSI | {RSSI:.1f} dBm | > -100 dBm | {PASS/FAIL} |
| Avg SNR | {SNR:.1f} dB | > 5 dB | {PASS/FAIL} |
| Convergence | {CONV:.1f} s | < 30 s | {PASS/FAIL} |

## Detailed Analysis
### PDR by Hop Count
| Hops | Packets | Received | PDR |
|------|---------|----------|-----|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |

### Latency Distribution
- Min: {MIN} ms
- P50: {P50} ms
- P95: {P95} ms
- P99: {P99} ms
- Max: {MAX} ms

### Power Consumption
| Node | Avg Current | Battery Life (est) |
|------|-------------|-------------------|
| ... | ... mA | ... days |

## Issues Found
| ID | Severity | Description | Repro Steps |
|----|----------|-------------|-------------|
| ... | ... | ... | ... |

## Recommendations
1. ...
2. ...

## Raw Data
- [Link to JSON results]
- [Link to CSV summary]
- [Link to PCAP captures]
- [Link to field logs]
```

---

## Continuous Benchmarking

### Baseline Tracking

```python
# scripts/compare_benchmarks.py
import json
from pathlib import Path

def compare_with_baseline(current: dict, baseline_file: Path):
    if not baseline_file.exists():
        return {"status": "no_baseline"}
    
    with open(baseline_file) as f:
        baseline = json.load(f)
    
    metrics = ['pdr', 'throughput_kbps', 'avg_latency_ms', 'p99_latency_ms']
    comparison = {}
    
    for metric in metrics:
        curr = current.get(metric, 0)
        base = baseline.get(metric, 0)
        if base > 0:
            change_pct = (curr - base) / base * 100
            comparison[metric] = {
                'current': curr,
                'baseline': base,
                'change_pct': change_pct,
                'regression': change_pct < -5  # 5% threshold
            }
    
    return comparison

# In CI: fail if regression detected
if any(v['regression'] for v in comparison.values()):
    print("::error::Performance regression detected!")
    exit(1)
```

---

## Resources

- **Nordic Power Profiler Kit II**: https://www.nordicsemi.com/Products/Development-tools/nrf-power-profiler-kit-ii
- **Joulescope**: https://www.joulescope.com/
- **Wireshark**: https://www.wireshark.org/ (with LoRa/BLE/Thread dissectors)
- **Thread Test Harness**: https://github.com/openthread/ot-th
- **Zephyr Test Framework**: https://docs.zephyrproject.org/latest/test/
- **ESP-IDF Unity Tests**: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/unit-tests.html