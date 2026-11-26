#!/usr/bin/env python3
"""
Generate Combined Markdown for PDF Export
Orders all documentation files in logical sequence for PDF generation.
"""

import os
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"

# Ordered list of all markdown files for PDF
PDF_FILES = [
    # Introduction
    "introduction/overview.md",
    "introduction/device-categories.md",
    "introduction/protocol-landscape.md",
    
    # Category 1: Low Bandwidth, Lossy, Long Range
    "category1/protocol-comparison.md",
    "category1/top-algorithms.md",
    "category1/esp32-setup/loramesher-esp32.md",
    "category1/esp32-setup/meshtastic-esp32.md",
    "category1/esp32-setup/hardware-recommendations.md",
    
    # Category 2: Low Bandwidth, Stable
    "category2/protocol-comparison.md",
    "category2/top-algorithms.md",
    "category2/esp32-setup/openthread-esp32.md",
    "category2/esp32-setup/zigbee-esp32.md",
    "category2/esp32-setup/ble-mesh-esp32.md",
    
    # Category 3: High Bandwidth, Lossy
    "category3/protocol-comparison.md",
    "category3/top-algorithms.md",
    "category3/esp32-setup/babel-wifi-esp32.md",
    "category3/esp32-setup/batman-adv-openwrt.md",
    "category3/esp32-setup/80211s-esp32.md",
    
    # Category 4: High Bandwidth, Stable
    "category4/protocol-comparison.md",
    "category4/top-algorithms.md",
    "category4/esp32-setup/wireguard-esp32.md",
    "category4/esp32-setup/bird2-linux.md",
    "category4/esp32-setup/cjdns-yggdrasil-linux.md",
    
    # Cross-Cutting
    "cross-cutting/hardware-selection-guide.md",
    "cross-cutting/security-comparison.md",
    "cross-cutting/power-management.md",
    "cross-cutting/testing-benchmarking.md",
    "cross-cutting/migration-guide.md",
    
    # DeepWiki Scraping
    "scraping/scraping-strategy.md",
    "scraping/source-inventory.md",
    "scraping/automation-scripts.md",
    "scraping/rule-extraction.md",
]

def read_md_file(filepath: Path) -> str:
    """Read markdown file with error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"<!-- FILE NOT FOUND: {filepath} -->\n\n"
    except Exception as e:
        return f"<!-- ERROR READING {filepath}: {e} -->\n\n"

def fix_relative_links(content: str, base_path: str) -> str:
    """Fix relative links in markdown for combined document."""
    import re
    
    # Fix relative links to other markdown files
    def replace_link(match):
        text = match.group(1)
        url = match.group(2)
        if url.endswith('.md') or url.endswith('.md)'):
            # Convert to anchor link
            anchor = url.replace('.md', '').replace('./', '').replace('../', '')
            anchor = anchor.replace('/', '-').replace('.', '')
            return f"[{text}](#{anchor.lower()})"
        return match.group(0)
    
    # Pattern: [text](path/file.md) or [text](./path/file.md)
    content = re.sub(r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)', replace_link, content)
    return content

def add_page_breaks(content: str) -> str:
    """Add page breaks before major sections."""
    import re
    
    # Add page break before h1 (but not first one)
    content = re.sub(r'\n(# [^\n]+)', r'\n\\newpage\n\1', content)
    return content

def generate_combined_markdown():
    """Generate combined markdown for PDF."""
    output = []
    
    # Title page
    output.append("""# Communication Protocols Guide for Embedded Devices

## Comprehensive Reference for Protocol Selection, Configuration, and Deployment

**Version:** 1.0  
**Date:** 2024-11-20  
**License:** MIT  
**Repository:** https://github.com/yourusername/communication-guide  
**Live Docs:** https://yourusername.github.io/communication-guide/

---

*This guide provides a comprehensive reference for selecting, configuring, and deploying communication protocols on embedded devices (ESP32, ESP32-S3) across four bandwidth/stability categories.*

---

\\newpage

# Table of Contents

""")
    
    # Generate TOC
    toc_entries = []
    for i, rel_path in enumerate(PDF_FILES):
        full_path = DOCS_DIR / rel_path
        if full_path.exists():
            # Extract first h1 from file
            content = read_md_file(full_path)
            for line in content.split('\n'):
                if line.startswith('# '):
                    title = line[2:].strip()
                    toc_entries.append(f"{i+1}. [{title}](#{rel_path.replace('/', '-').replace('.md', '').lower()})")
                    break
    
    output.append('\n'.join(toc_entries))
    output.append('\n\\newpage\n')
    
    # Process each file
    first_h1 = True
    for rel_path in PDF_FILES:
        full_path = DOCS_DIR / rel_path
        if not full_path.exists():
            continue
        
        content = read_md_file(full_path)
        
        # Fix relative links
        content = fix_relative_links(content, rel_path)
        
        # Add page break before each major section (except first)
        if not first_h1:
            output.append('\\newpage\n')
        first_h1 = False
        
        # Add file as section
        output.append(f"<!-- {rel_path} -->\n")
        output.append(content)
        output.append('\n')
    
    # Appendices
    output.append('\\newpage\n')
    output.append("""# Appendices

## A. Glossary

| Term | Definition |
|------|------------|
| **BLE** | Bluetooth Low Energy |
| **CAT** | Category (bandwidth/stability classification) |
| **DODAG** | Destination-Oriented Directed Acyclic Graph |
| **DV** | Distance Vector |
| **ETX** | Expected Transmission Count |
| **HWMP** | Hybrid Wireless Mesh Protocol |
| **LoRa** | Long Range (modulation) |
| **LPN** | Low Power Node |
| **LQI** | Link Quality Indicator |
| **MAC** | Medium Access Control |
| **MLE** | Mesh Link Establishment |
| **NAT** | Network Address Translation |
| **NWK** | Network Layer (Zigbee) |
| **OGM** | Originator Message |
| **PDR** | Packet Delivery Ratio |
| **PHY** | Physical Layer |
| **PSK** | Pre-Shared Key |
| **RPL** | Routing Protocol for LLNs |
| **RSSI** | Received Signal Strength Indicator |
| **SAE** | Simultaneous Authentication of Equals |
| **SNR** | Signal-to-Noise Ratio |
| **SRP** | Service Registration Protocol |
| **TDMA** | Time Division Multiple Access |
| **TTL** | Time To Live |
| **UART** | Universal Asynchronous Receiver-Transmitter |

## B. References

### Academic Papers
1. Solé et al. "Implementation of a LoRa Mesh Library" — IEEE Access, 2022. DOI: 10.1109/ACCESS.2022.3217215
2. Solé et al. "Large and reliable data transfer for LoRa mesh" — Computer Communications, 2026. DOI: 10.1016/j.comcom.2025.108404
3. Donnet et al. "WireGuard: Next Generation Kernel Network Tunnel" — NDSS 2020

### RFCs & Standards
- RFC 6550: RPL (Routing Protocol for Low-Power and Lossy Networks)
- RFC 6551: RPL Metrics
- RFC 6552: RPL Objective Functions
- RFC 8966: Babel Routing Protocol
- RFC 3626: OLSR (Optimized Link State Routing)
- RFC 7181: OLSRv2
- RFC 4944/6282: 6LoWPAN
- RFC 8439: ChaCha20-Poly1305
- IEEE 802.15.4: Low-Rate Wireless PAN
- IEEE 802.11s: Mesh Networking
- Thread Specification 1.4
- Zigbee 3.0 Specification
- Bluetooth Mesh 1.0.1

### Key Repositories
- LoRaMesher: https://github.com/LoRaMesher/LoRaMesher
- Meshtastic: https://github.com/meshtastic/firmware
- OpenThread: https://github.com/openthread/openthread
- ESP-IDF: https://github.com/espressif/esp-idf
- OpenWrt Routing: https://github.com/openwrt/routing
- WireGuard: https://www.wireguard.com/
- BIRD2: https://bird.network.cz/
- cjdns: https://github.com/cjdelisle/cjdns
- Yggdrasil: https://github.com/yggdrasil-network/yggdrasil

---

*Generated on: 2024-11-20*  
*Communication Protocols Guide v1.0*  
*MIT License*

""")
    
    return '\n'.join(output)

def main():
    markdown = generate_combined_markdown()
    print(markdown)

if __name__ == '__main__':
    main()