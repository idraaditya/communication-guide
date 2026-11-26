#!/usr/bin/env python3
"""
Rule Extraction from Scraped DeepWiki Content
Extracts structured protocol rules from scraped markdown files.
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

SCRAPED_DIR = Path(__file__).parent.parent / "docs" / "scraped"
RULES_DIR = Path(__file__).parent.parent / "docs" / "rules"

@dataclass
class ProtocolRule:
    repo: str
    category: str
    rule_type: str
    name: str
    description: str
    parameters: Dict[str, Any]
    source_file: str
    source_section: str
    confidence: float

class RuleExtractor:
    def __init__(self, scraped_dir: Path = SCRAPED_DIR, rules_dir: Path = RULES_DIR):
        self.scraped_dir = scraped_dir
        self.rules_dir = rules_dir
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        self.rules: List[ProtocolRule] = []
    
    def categorize_repo(self, repo: str) -> str:
        categories = {
            'meshtastic_firmware': 'low-bandwidth-lossy-long-range',
            'LoRaMesher_LoRaMesher': 'low-bandwidth-lossy-long-range',
            'espressif_esp-idf': 'platform',
            'openwrt_routing': 'high-bandwidth-lossy',
            'openthread_openthread': 'low-bandwidth-stable',
        }
        return categories.get(repo, 'unknown')
    
    def extract_from_json(self, json_file: Path) -> List[ProtocolRule]:
        """Extract rules from a scraped JSON file."""
        with open(json_file) as f:
            data = json.load(f)
        
        repo = data['repo']
        category = self.categorize_repo(repo)
        rules = []
        
        # Extract from headings
        for heading in data.get('headings', []):
            rule = self.extract_from_heading(heading, repo, category, json_file.name)
            if rule:
                rules.append(rule)
        
        # Extract from code blocks
        for i, code in enumerate(data.get('code_blocks', [])):
            rule = self.extract_from_code(code, repo, category, json_file.name, f"code_block_{i}")
            if rule:
                rules.append(rule)
        
        # Extract from tables
        for i, table in enumerate(data.get('tables', [])):
            rule = self.extract_from_table(table, repo, category, json_file.name, f"table_{i}")
            if rule:
                rules.append(rule)
        
        return rules
    
    def extract_from_heading(self, heading: dict, repo: str, category: str, source_file: str, source_section: str) -> Optional[ProtocolRule]:
        text = heading['text']
        level = heading['level']
        
        # Classify heading type
        rule_type = self.classify_heading(text)
        if not rule_type:
            return None
        
        # Extract parameters from heading text
        params = self.extract_params_from_text(text)
        
        return ProtocolRule(
            repo=repo,
            category=category,
            rule_type=rule_type,
            name=text[:100],
            description=f"Heading (level {level}): {text}",
            parameters=params,
            source_file=source_file,
            source_section=source_section,
            confidence=0.7
        )
    
    def classify_heading(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        
        # Configuration parameters
        if any(kw in text_lower for kw in ['config', 'parameter', 'setting', 'option', 'parameter']):
            return 'configuration'
        
        # State machines
        if any(kw in text_lower for kw in ['state', 'status', 'mode', 'phase']):
            return 'state_machine'
        
        # Message formats
        if any(kw in text_lower for kw in ['message', 'packet', 'frame', 'format', 'header']):
            return 'message_format'
        
        # Timing
        if any(kw in text_lower for kw in ['timing', 'slot', 'interval', 'timeout', 'period', 'schedule']):
            return 'timing'
        
        # Routing
        if any(kw in text_lower for kw in ['route', 'routing', 'forward', 'path', 'hop']):
            return 'routing'
        
        # Security
        if any(kw in text_lower for kw in ['security', 'encrypt', 'auth', 'key', 'crypto']):
            return 'security'
        
        # API
        if any(kw in text_lower for kw in ['api', 'callback', 'function', 'method', 'command']):
            return 'api'
        
        return None
    
    def extract_params_from_text(self, text: str) -> Dict[str, Any]:
        params = {}
        
        # Key=value patterns
        for match in re.finditer(r'(\w+)\s*[=:]\s*([^\s,;]+)', text):
            params[match.group(1)] = match.group(2)
        
        # Number with units
        for match in re.finditer(r'(\d+(?:\.\d+)?)\s*(ms|s|khz|mhz|dbm|db|khz|kbps|mbps)', text, re.IGNORECASE):
            params[f'value_{len(params)}'] = f"{match.group(1)} {match.group(2)}"
        
        # Hex values
        for match in re.finditer(r'0x[0-9a-fA-F]+', text):
            params[f'hex_{len(params)}'] = match.group(0)
        
        return params
    
    def extract_from_code(self, code: str, repo: str, category: str, source_file: str, source_section: str) -> Optional[ProtocolRule]:
        if len(code) < 50:
            return None
        
        # Classify code type
        rule_type = 'code'
        if 'struct' in code or 'class' in code:
            rule_type = 'data_structure'
        elif 'enum' in code:
            rule_type = 'enumeration'
        elif 'def ' in code or 'void ' in code or 'func ' in code:
            rule_type = 'function'
        elif '#define' in code or 'const ' in code:
            rule_type = 'constant'
        elif 'config' in code.lower():
            rule_type = 'configuration'
        
        # Extract key constants/parameters
        params = {}
        for match in re.finditer(r'(?:#define|const\s+\w+|static\s+const)\s+(\w+)\s*[=:]\s*([^\s;]+)', code):
            params[match.group(1)] = match.group(2)
        
        for match in re.finditer(r'(\w+)\s*[:=]\s*(\d+(?:\.\d+)?)\s*(ms|s|khz|mhz|dbm|db)', code, re.IGNORECASE):
            params[match.group(1)] = f"{match.group(2)} {match.group(3)}"
        
        return ProtocolRule(
            repo=repo,
            category=category,
            rule_type=rule_type,
            name=code[:80].split('\n')[0],
            description=f"Code block: {code[:200]}",
            parameters=params,
            source_file=source_file,
            source_section=source_section,
            confidence=0.6
        )
    
    def extract_from_table(self, table_html: str, repo: str, category: str, source_file: str, source_section: str) -> Optional[ProtocolRule]:
        # Simple table parsing - look for config/parameter tables
        if not any(kw in table_html.lower() for kw in ['parameter', 'value', 'default', 'range', 'config', 'setting']):
            return None
        
        return ProtocolRule(
            repo=repo,
            category=category,
            rule_type='configuration_table',
            name="Configuration Table",
            description=f"Table with configuration parameters: {table_html[:200]}",
            parameters={'table_html': table_html[:5000]},
            source_file=source_file,
            source_section=source_section,
            confidence=0.8
        )
    
    def run_extraction(self):
        """Run extraction on all scraped JSON files."""
        print("Extracting rules from scraped content...")
        
        json_files = list(self.scraped_dir.rglob("*.json"))
        print(f"Found {len(json_files)} JSON files")
        
        for json_file in json_files:
            try:
                rules = self.extract_from_json(json_file)
                self.rules.extend(rules)
                print(f"  {json_file.name}: {len(rules)} rules")
            except Exception as e:
                print(f"  Error processing {json_file}: {e}")
        
        print(f"Total rules extracted: {len(self.rules)}")
        self.save_rules()
    
    def save_rules(self):
        """Save rules as YAML by category."""
        by_category = {}
        for rule in self.rules:
            cat = rule.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(asdict(rule))
        
        for cat, rules in by_category.items():
            cat_dir = self.rules_dir / cat
            cat_dir.mkdir(parents=True, exist_ok=True)
            with open(cat_dir / 'rules.yaml', 'w') as f:
                yaml.dump(rules, f, default_flow_style=False, sort_keys=False)
        
        # All rules
        with open(self.rules_dir / 'all_rules.yaml', 'w') as f:
            yaml.dump([asdict(r) for r in self.rules], f, default_flow_style=False, sort_keys=False)
        
        # Summary
        summary = {
            'total_rules': len(self.rules),
            'by_category': {cat: len(rules) for cat, rules in by_category.items()},
            'by_type': {}
        }
        for rule in self.rules:
            t = rule.rule_type
            summary['by_type'][t] = summary['by_type'].get(t, 0) + 1
        
        with open(self.rules_dir / 'extraction_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Rules saved to {self.rules_dir}")
        print(f"Summary: {summary}")

def main():
    extractor = RuleExtractor()
    extractor.run_extraction()

if __name__ == '__main__':
    main()