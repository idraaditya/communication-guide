#!/usr/bin/env python3
"""
Generate Comparison Matrices from Extracted Rules
Creates CSV and Markdown comparison tables for each category.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

RULES_DIR = Path(__file__).parent.parent / "docs" / "rules"
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Protocol definitions per category
CATEGORY_PROTOCOLS = {
    'low-bandwidth-lossy-long-range': [
        'LoRaMesher',
        'Meshtastic',
        'BATMAN-ADV (LoRa)',
    ],
    'low-bandwidth-stable': [
        'OpenThread',
        'Zigbee 3.0',
        'BLE Mesh',
    ],
    'high-bandwidth-lossy': [
        'BATMAN-ADV',
        'Babel',
        '802.11s (HWMP)',
    ],
    'high-bandwidth-stable': [
        'WireGuard',
        'BIRD2 (OSPF/BGP)',
        'cjdns',
        'Yggdrasil',
    ],
}

# Comparison attributes
ATTRIBUTES = [
    'Architecture',
    'Layer',
    'Routing Algorithm',
    'Metric',
    'Max Data Rate',
    'Typical Range',
    'Encryption',
    'Authentication',
    'Key Management',
    'Forward Secrecy',
    'NAT Traversal',
    'Roaming Support',
    'Multicast',
    'Fragmentation',
    'Security Level',
    'Maturity',
    'License',
    'ESP32 Support',
    'Best For',
]

# Protocol data (manually curated from research)
PROTOCOL_DATA = {
    'LoRaMesher': {
        'Architecture': 'TDMA + Distance Vector',
        'Layer': 'L3 (Application)',
        'Routing Algorithm': 'Distance Vector + ETX',
        'Metric': 'ETX Cost (hop_count × 65536/quality)',
        'Max Data Rate': '0.018-62.5 kbps',
        'Typical Range': '1-50+ km',
        'Encryption': 'AES-128-CTR',
        'Authentication': 'AES-CMAC',
        'Key Management': 'PSK / AppKey',
        'Forward Secrecy': 'No',
        'NAT Traversal': 'N/A',
        'Roaming Support': 'Limited',
        'Multicast': 'Capability-based discovery',
        'Fragmentation': 'Application layer',
        'Security Level': 'Medium',
        'Maturity': 'v1.0 (2024)',
        'License': 'MIT',
        'ESP32 Support': '✅ PlatformIO',
        'Best For': 'Battery, deterministic latency, long range',
    },
    'Meshtastic': {
        'Architecture': 'Flooding + ReliableRouter',
        'Layer': 'L3.5 (Mesh over LoRa)',
        'Routing Algorithm': 'Hybrid (Flood + On-demand)',
        'Metric': 'Hop count + SNR/RSSI',
        'Max Data Rate': '0.018-37.5 kbps',
        'Typical Range': '1-10+ km',
        'Encryption': 'AES-256-CTR',
        'Authentication': 'AES-CMAC',
        'Key Management': 'PSK / QR code',
        'Forward Secrecy': 'No',
        'NAT Traversal': 'N/A',
        'Roaming Support': 'Limited',
        'Multicast': 'TTL flood broadcast',
        'Fragmentation': 'Application layer',
        'Security Level': 'Medium-High',
        'Maturity': 'v2.x (2024)',
        'License': 'GPL-3.0',
        'ESP32 Support': '✅ ESP-IDF',
        'Best For': 'Human messaging, MQTT gateway, community',
    },
    'BATMAN-ADV (LoRa)': {
        'Architecture': 'L2 Mesh (Kernel)',
        'Layer': 'L2',
        'Routing Algorithm': 'OGM Flooding',
        'Metric': 'TQ (Transmission Quality)',
        'Max Data Rate': '0.018-62.5 kbps',
        'Typical Range': '1-50+ km',
        'Encryption': 'None (L2)',
        'Authentication': 'None',
        'Key Management': 'N/A',
        'Forward Secrecy': 'N/A',
        'NAT Traversal': 'N/A',
        'Roaming Support': 'Excellent (L2)',
        'Multicast': 'MCAST optimization',
        'Fragmentation': 'Built-in',
        'Security Level': 'Low (needs IPsec)',
        'Maturity': 'Stable (mainline kernel)',
        'License': 'GPL-2.0',
        'ESP32 Support': '❌ Linux host',
        'Best For': 'L2 transparency, roaming, wired backhaul',
    },
    'OpenThread': {
        'Architecture': 'IPv6/6LoWPAN + RPL',
        'Layer': 'L3.5 (Thread)',
        'Routing Algorithm': 'RPL (DODAG)',
        'Metric': 'OF0 (hops) / MRHOF (ETX)',
        'Max Data Rate': '250 kbps',
        'Typical Range': '10-100m',
        'Encryption': 'AES-CCM (MAC) + DTLS',
        'Authentication': 'DTLS + PSKc',
        'Key Management': 'Commissioner',
        'Forward Secrecy': 'Yes (session)',
        'NAT Traversal': 'Border Router (NAT64/DNS64)',
        'Roaming Support': 'Good (Thread 1.2+)',
        'Multicast': 'MPL (RFC 7731)',
        'Fragmentation': '6LoWPAN',
        'Security Level': 'High',
        'Maturity': 'Thread 1.4 Certified',
        'License': 'BSD-3',
        'ESP32 Support': '✅ ESP32-H2/C6',
        'Best For': 'Matter, IPv6, border router',
    },
    'Zigbee 3.0': {
        'Architecture': 'AODV + ZCL',
        'Layer': 'L3.5 (Zigbee)',
        'Routing Algorithm': 'AODV + Tree',
        'Metric': 'Path cost',
        'Max Data Rate': '250 kbps',
        'Typical Range': '10-100m',
        'Encryption': 'AES-128-CCM',
        'Authentication': 'Link/Net keys',
        'Key Management': 'Trust Center',
        'Forward Secrecy': 'Yes (session)',
        'NAT Traversal': 'Gateway needed',
        'Roaming Support': 'Limited',
        'Multicast': 'Group addressing',
        'Fragmentation': 'APS',
        'Security Level': 'High',
        'Maturity': 'Zigbee 3.0 (2018)',
        'License': 'Proprietary/GPL',
        'ESP32 Support': '✅ ESP32-H2/C6',
        'Best For': 'HA ecosystem, Green Power',
    },
    'BLE Mesh': {
        'Architecture': 'Managed Flood + Friendship',
        'Layer': 'L3.5 (BLE Mesh)',
        'Routing Algorithm': 'Managed Flooding',
        'Metric': 'TTL + Relay count',
        'Max Data Rate': '1-2 Mbps (PHY)',
        'Typical Range': '10-100m',
        'Encryption': 'AES-CCM',
        'Authentication': 'ECDH Provisioning',
        'Key Management': 'Provisioner',
        'Forward Secrecy': 'Yes (session)',
        'NAT Traversal': 'Proxy (GATT)',
        'Roaming Support': 'Limited',
        'Multicast': 'Group/Virtual addresses',
        'Fragmentation': 'SAR',
        'Security Level': 'High',
        'Maturity': 'Mesh 1.0.1 (2019)',
        'License': 'Apache-2.0',
        'ESP32 Support': '✅ ESP32/ESP32-S3',
        'Best For': 'Phone provisioning, lighting, no border router',
    },
    'BATMAN-ADV': {
        'Architecture': 'L2 Mesh (Kernel)',
        'Layer': 'L2',
        'Routing Algorithm': 'OGM Flooding',
        'Metric': 'TQ (Transmission Quality)',
        'Max Data Rate': '100+ Mbps (WiFi)',
        'Typical Range': '100m-1km (WiFi)',
        'Encryption': 'None (L2)',
        'Authentication': 'None',
        'Key Management': 'N/A',
        'Forward Secrecy': 'N/A',
        'NAT Traversal': 'N/A',
        'Roaming Support': 'Excellent (L2)',
        'Multicast': 'MCAST optimization',
        'Fragmentation': 'Built-in',
        'Security Level': 'Low (needs IPsec)',
        'Maturity': 'Stable (mainline kernel)',
        'License': 'GPL-2.0',
        'ESP32 Support': '❌ Linux host (OpenWrt)',
        'Best For': 'L2 transparency, roaming, VLAN',
    },
    'Babel': {
        'Architecture': 'Distance Vector (L3)',
        'Layer': 'L3',
        'Routing Algorithm': 'DV + ETX',
        'Metric': 'ETX (Expected TX Count)',
        'Max Data Rate': '100+ Mbps (WiFi)',
        'Typical Range': '100m-1km (WiFi)',
        'Encryption': 'None',
        'Authentication': 'None',
        'Key Management': 'N/A',
        'Forward Secrecy': 'N/A',
        'NAT Traversal': 'N/A',
        'Roaming Support': 'Good',
        'Multicast': 'Native (MPL-like)',
        'Fragmentation': 'IP',
        'Security Level': 'Low (needs IPsec)',
        'Maturity': 'RFC 8966',
        'License': 'MIT/ISC',
        'ESP32 Support': '✅ ESP32-S3 (babeld)',
        'Best For': 'Fast convergence, dual-stack, policy routing',
    },
    '802.11s (HWMP)': {
        'Architecture': 'L2 Mesh (MAC)',
        'Layer': 'L2',
        'Routing Algorithm': 'HWMP (Reactive)',
        'Metric': 'Airtime Link Metric',
        'Max Data Rate': '100+ Mbps (WiFi)',
        'Typical Range': '100m-1km (WiFi)',
        'Encryption': 'AES-CCMP/GCMP-256',
        'Authentication': 'SAE (WPA3) / PSK',
        'Key Management': '4-way handshake',
        'Forward Secrecy': 'Yes (session)',
        'NAT Traversal': 'N/A',
        'Roaming Support': 'Standard (802.11r/k/v)',
        'Multicast': 'IGMP/MLD Snooping',
        'Fragmentation': '802.11',
        'Security Level': 'High (WPA3)',
        'Maturity': 'IEEE 802.11s-2011',
        'License': 'GPL-2.0 (Linux)',
        'ESP32 Support': '✅ ESP32-S3 (mac80211)',
        'Best For': 'Standard WiFi mesh, WPA3',
    },
    'WireGuard': {
        'Architecture': 'L3 VPN (Kernel/Userspace)',
        'Layer': 'L3',
        'Routing Algorithm': 'Cryptokey Routing',
        'Metric': 'Static (AllowedIPs)',
        'Max Data Rate': '1-10 Gbps',
        'Typical Range': 'Internet/WAN',
        'Encryption': 'ChaCha20-Poly1305',
        'Authentication': 'Noise_IK (1-RTT)',
        'Key Management': 'Static keys + PSK',
        'Forward Secrecy': 'Yes (1-RTT)',
        'NAT Traversal': 'Built-in (keepalive)',
        'Roaming Support': 'Seamless',
        'Multicast': 'No',
        'Fragmentation': 'IP',
        'Security Level': 'Very High',
        'Maturity': 'Stable (Linux 5.6+)',
        'License': 'GPL-2.0',
        'ESP32 Support': '✅ ESP32-S3 (WireGuard-Go)',
        'Best For': 'Site-to-site, road warrior, simple config',
    },
    'BIRD2 (OSPF/BGP)': {
        'Architecture': 'Routing Daemon (L3)',
        'Layer': 'L3 (Control Plane)',
        'Routing Algorithm': 'OSPF (SPF) / BGP (Path Vector)',
        'Metric': 'OSPF Cost / BGP Attributes',
        'Max Data Rate': 'Control plane only',
        'Typical Range': 'Internet/Enterprise',
        'Encryption': 'IPsec (separate)',
        'Authentication': 'MD5/SHA/TCP-AO',
        'Key Management': 'Manual/Keychain',
        'Forward Secrecy': 'IPsec only',
        'NAT Traversal': 'No',
        'Roaming Support': 'Protocol-dependent',
        'Multicast': 'OSPF: Yes, BGP: No',
        'Fragmentation': 'IP',
        'Security Level': 'Medium (needs IPsec)',
        'Maturity': 'Production ISP grade',
        'License': 'GPL-2.0',
        'ESP32 Support': '❌ Linux host',
        'Best For': 'Enterprise/ISP routing, policy',
    },
    'cjdns': {
        'Architecture': 'Overlay (L2.5/L3)',
        'Layer': 'L2.5/L3',
        'Routing Algorithm': 'DHT + Switch Labels',
        'Metric': 'Latency/Loss (DHT)',
        'Max Data Rate': '100-500 Mbps',
        'Typical Range': 'Internet/Overlay',
        'Encryption': 'Curve25519/ChaCha20',
        'Authentication': 'CryptoKey (self-cert)',
        'Key Management': 'Self-certifying',
        'Forward Secrecy': 'Yes (ephemeral DH)',
        'NAT Traversal': 'Built-in (DHT)',
        'Roaming Support': 'DHT-based',
        'Multicast': 'No',
        'Fragmentation': 'Built-in',
        'Security Level': 'High',
        'Maturity': 'Beta',
        'License': 'GPL-3.0',
        'ESP32 Support': '❌ Linux host',
        'Best For': 'Encrypted overlay, no PKI',
    },
    'Yggdrasil': {
        'Architecture': 'Overlay (L3)',
        'Layer': 'L3',
        'Routing Algorithm': 'DHT + Tree + Shortcuts',
        'Metric': 'Latency (Tree + Shortcuts)',
        'Max Data Rate': '100-500 Mbps',
        'Typical Range': 'Internet/Overlay',
        'Encryption': 'Curve25519/ChaCha20',
        'Authentication': 'CryptoKey (self-cert)',
        'Key Management': 'Self-certifying',
        'Forward Secrecy': 'Yes (ephemeral DH)',
        'NAT Traversal': 'Built-in (DHT)',
        'Roaming Support': 'DHT-based',
        'Multicast': 'No',
        'Fragmentation': 'IP',
        'Security Level': 'High',
        'Maturity': 'Beta',
        'License': 'GPL-3.0',
        'ESP32 Support': '❌ (cross-platform)',
        'Best For': 'Encrypted overlay, cross-platform',
    },
}

def generate_csv(category: str, protocols: List[str]):
    """Generate CSV comparison matrix."""
    output_file = DATA_DIR / f"{category}_comparison.csv"
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Attribute'] + protocols)
        
        for attr in ATTRIBUTES:
            row = [attr]
            for proto in protocols:
                data = PROTOCOL_DATA.get(proto, {})
                row.append(data.get(attr, 'N/A'))
            writer.writerow(row)
    
    print(f"Generated {output_file}")

def generate_markdown(category: str, protocols: List[str]):
    """Generate Markdown comparison table."""
    output_file = DATA_DIR / f"{category}_comparison.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# {category.replace('-', ' ').title()} Protocol Comparison\n\n")
        
        # Full table
        f.write("| Attribute | " + " | ".join(protocols) + " |\n")
        f.write("|" + "---|" * (len(protocols) + 1) + "\n")
        
        for attr in ATTRIBUTES:
            row = [attr]
            for proto in protocols:
                data = PROTOCOL_DATA.get(proto, {})
                val = data.get(attr, 'N/A')
                # Escape pipes in values
                val = str(val).replace('|', '\\|')
                row.append(val)
            f.write("| " + " | ".join(row) + " |\n")
        
        f.write("\n\n## Quick Selection Guide\n\n")
        f.write("| Requirement | Recommended Protocol |\n")
        f.write("|-------------|---------------------|\n")
        
        # Add selection guide based on category
        guides = {
            'low-bandwidth-lossy-long-range': [
                ('Battery + deterministic latency', 'LoRaMesher'),
                ('Human messaging + MQTT + community', 'Meshtastic'),
                ('L2 transparency + roaming', 'BATMAN-ADV (Linux host)'),
            ],
            'low-bandwidth-stable': [
                ('Matter + IPv6 + border router', 'OpenThread'),
                ('HA ecosystem + Green Power', 'Zigbee 3.0'),
                ('Phone provisioning + no border router', 'BLE Mesh'),
            ],
            'high-bandwidth-lossy': [
                ('L2 transparency + roaming', 'BATMAN-ADV (Linux)'),
                ('Fast convergence + dual-stack + policy', 'Babel'),
                ('Standard WiFi mesh + WPA3', '802.11s'),
            ],
            'high-bandwidth-stable': [
                ('Site-to-site VPN + road warrior', 'WireGuard'),
                ('Enterprise/ISP routing + policy', 'BIRD2 (OSPF/BGP)'),
                ('Encrypted overlay + no PKI', 'cjdns / Yggdrasil'),
            ],
        }
        
        for req, proto in guides.get(category, []):
            f.write(f"| {req} | {proto} |\n")
    
    print(f"Generated {output_file}")

def generate_category_summary():
    """Generate overall category summary CSV."""
    output_file = DATA_DIR / "category_summary.csv"
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Category', 'Bandwidth', 'Stability', 'Range', 'Protocols', 'Best For'
        ])
        
        categories = [
            ('Low BW, Lossy, Long Range', '< 5 kbps', 'High loss (10-50%)', '1-50+ km', 
             'LoRaMesher, Meshtastic, BATMAN-ADV', 'Sensor networks, off-grid comms'),
            ('Low BW, Stable', '250 kbps - 1 Mbps', 'Low loss (<1%)', '10-100m', 
             'OpenThread, Zigbee, BLE Mesh', 'Home automation, Matter'),
            ('High BW, Lossy', '1-50 Mbps', 'Medium loss (1-10%)', '100m-1km', 
             'BATMAN-ADV, Babel, 802.11s', 'WiFi mesh, mobile ad-hoc'),
            ('High BW, Stable', '100 Mbps - 1 Gbps', 'Very low loss (<0.1%)', 'LAN/WAN', 
             'WireGuard, BIRD2, cjdns, Yggdrasil', 'VPN, enterprise routing, overlays'),
        ]
        
        for row in categories:
            writer.writerow(row)
    
    print(f"Generated {output_file}")

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Generating comparison matrices...")
    
    for category, protocols in CATEGORY_PROTOCOLS.items():
        print(f"\nProcessing {category}...")
        generate_csv(category, protocols)
        generate_markdown(category, protocols)
    
    generate_category_summary()
    
    print("\nAll comparison matrices generated in data/")

if __name__ == '__main__':
    main()