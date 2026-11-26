# Rule Extraction from DeepWiki

## Overview

This document describes the automated rule extraction process that transforms scraped DeepWiki content into structured protocol rules for the Communication Protocols Guide.

## Extraction Pipeline

```
Scraped Content (JSON/Markdown)
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RULE EXTRACTOR                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. HEADING ANALYSIS                                            │
│     • Extract all h1-h6 headings                                │
│     • Classify by keywords → rule_type                          │
│     • Extract parameters from heading text                      │
│                                                                  │
│  2. CODE BLOCK ANALYSIS                                         │
│     • Identify: structs, enums, constants, functions           │
│     • Extract key parameters and values                         │
│     • Classify: data_structure, enumeration, constant, function │
│                                                                  │
│  3. TABLE ANALYSIS                                              │
│     • Detect configuration tables                               │
│     • Extract parameter/value/default/range                     │
│     • Classify: configuration_table                             │
│                                                                  │
│  4. RULE AGGREGATION                                            │
│     • Deduplicate similar rules                                 │
│     • Assign confidence scores                                  │
│     • Group by category                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
    Structured Rules (YAML)
```

## Rule Classification Taxonomy

### Primary Rule Types

| Rule Type | Description | Source Patterns |
|-----------|-------------|-----------------|
| `configuration` | Configurable parameters | "Configuration", "Parameters", "Settings", "Options" |
| `state_machine` | Protocol states & transitions | "State Machine", "States", "Modes", "Phases" |
| `message_format` | Packet/frame structures | "Message Format", "Packet Structure", "Frame Format" |
| `timing` | Time-related parameters | "Timing", "Slots", "Intervals", "Timeouts" |
| `routing` | Routing algorithms & metrics | "Routing", "Forwarding", "Path", "Hops" |
| `security` | Crypto, auth, keys | "Security", "Encryption", "Authentication", "Keys" |
| `api` | Programming interfaces | "API", "Callbacks", "Commands", "Functions" |
| `constant` | Fixed values, limits | "DEFINES", "Constants", "Limits", "Defaults" |
| `data_structure` | Struct/class definitions | `struct`, `class`, `typedef struct` |
| `enumeration` | Enum definitions | `enum`, `enum class` |
| `function` | Function signatures | `void func()`, `int func()` |
| `configuration_table` | Parameter tables | HTML `<table>` with config data |

### Classification Keywords

```python
CLASSIFICATION_KEYWORDS = {
    'configuration': [
        'config', 'parameter', 'setting', 'option', 'setup', 'configure'
    ],
    'state_machine': [
        'state', 'status', 'mode', 'phase', 'transition', 'fsm'
    ],
    'message_format': [
        'message', 'packet', 'frame', 'format', 'header', 'payload'
    ],
    'timing': [
        'timing', 'slot', 'interval', 'timeout', 'period', 'schedule',
        'latency', 'delay', 'duration', 'frequency'
    ],
    'routing': [
        'route', 'routing', 'forward', 'path', 'hop', 'metric',
        'distance', 'vector', 'dijkstra', 'bellman', 'ford'
    ],
    'security': [
        'security', 'encrypt', 'auth', 'key', 'crypto', 'cipher',
        'aes', 'chacha', 'poly', 'hmac', 'signature', 'certificate'
    ],
    'api': [
        'api', 'callback', 'function', 'method', 'command', 'cli',
        'interface', 'handler', 'hook', 'event'
    ],
    'constant': [
        'define', 'const', 'default_', 'max_', 'min_', 'timeout_',
        'limit_', 'size_', 'count_', 'default'
    ],
}
```

## Parameter Extraction

### From Headings

```python
def extract_params_from_text(text: str) -> Dict[str, Any]:
    params = {}
    
    # key=value patterns
    for match in re.finditer(r'(\w+)\s*[=:]\s*([^\s,;]+)', text):
        params[match.group(1)] = match.group(2)
    
    # Numbers with units
    for match in re.finditer(r'(\d+(?:\.\d+)?)\s*(ms|s|khz|mhz|dbm|db|kbps|mbps)', text, re.IGNORECASE):
        params[f'value_{len(params)}'] = f"{match.group(1)} {match.group(2)}"
    
    # Hex values
    for match in re.finditer(r'0x[0-9a-fA-F]+', text):
        params[f'hex_{len(params)}'] = match.group(0)
    
    # Version numbers
    for match in re.finditer(r'v?(\d+\.\d+\.\d+)', text):
        params['version'] = match.group(1)
    
    return params
```

### From Code Blocks

```python
def extract_from_code(self, code: str) -> Dict[str, Any]:
    params = {}
    
    # #define CONSTANT VALUE
    for match in re.finditer(r'#define\s+(\w+)\s+([^\s\n]+)', code):
        params[match.group(1)] = match.group(2)
    
    # const TYPE NAME = VALUE
    for match in re.finditer(r'const\s+\w+\s+(\w+)\s*=\s*([^;\n]+)', code):
        params[match.group(1)] = match.group(2).strip()
    
    # static const TYPE NAME = VALUE
    for match in re.finditer(r'static\s+const\s+\w+\s+(\w+)\s*=\s*([^;\n]+)', code):
        params[match.group(1)] = match.group(2).strip()
    
    # enum VALUES
    for match in re.finditer(r'enum\s+\w*\s*\{([^}]+)\}', code, re.DOTALL):
        enum_content = match.group(1)
        for enum_match in re.finditer(r'(\w+)\s*=\s*([^,\n]+)', enum_content):
            params[enum_match.group(1)] = enum_match.group(2).strip()
    
    # Struct field defaults
    for match in re.finditer(r'(\w+)\s*[:=]\s*([^,\n;]+)', code):
        if not match.group(1).startswith('//'):  # Skip comments
            params[match.group(1)] = match.group(2).strip()
    
    return params
```

### From Tables

```python
def extract_from_table(self, table_html: str) -> List[Dict[str, Any]]:
    """Extract configuration parameters from HTML tables."""
    soup = BeautifulSoup(table_html, 'html.parser')
    rows = soup.find_all('tr')
    
    params = []
    headers = []
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        
        if not headers:
            headers = cell_texts
        else:
            row_data = dict(zip(headers, cell_texts))
            params.append(row_data)
    
    return params
```

## Confidence Scoring

### Confidence Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| **Source Type** | 0.3 | Heading (0.7) > Code (0.6) > Table (0.8) |
| **Keyword Match** | 0.3 | Exact keyword match in heading |
| **Parameter Density** | 0.2 | Number of extracted parameters |
| **Context Relevance** | 0.2 | Category alignment |

### Confidence Calculation

```python
def calculate_confidence(rule: ProtocolRule) -> float:
    base = 0.5
    
    # Source type bonus
    source_bonus = {
        'heading': 0.2,
        'code_block': 0.1,
        'table': 0.3,
    }.get(rule.source_section.split('_')[0], 0)
    
    # Keyword match bonus
    keyword_bonus = 0.2 if rule.parameters else 0
    
    # Parameter count bonus (capped at 0.2)
    param_bonus = min(len(rule.parameters) * 0.05, 0.2)
    
    confidence = base + base * source_bonus + keyword_bonus + param_bonus
    return min(confidence, 1.0)
```

## Output Format

### YAML Structure

```yaml
# docs/rules/category_name/rules.yaml
- repo: "meshtastic/firmware"
  category: "low-bandwidth-lossy-long-range"
  rule_type: "configuration"
  name: "LoRa Configuration Parameters"
  description: "Section: LoRa Configuration Parameters"
  parameters:
    region: "US"
    tx_power: "17"
    spreading_factor: "7"
    bandwidth: "125"
    coding_rate: "5"
  source_file: "LoRa_Configuration.md"
  source_section: "lora-configuration"
  confidence: 0.85
  extracted_at: "2024-11-20T10:30:00Z"
```

### All Rules Index

```yaml
# docs/rules/all_rules.yaml
- repo: "meshtastic/firmware"
  category: "low-bandwidth-lossy-long-range"
  rule_type: "configuration"
  # ... (same as above)
- repo: "LoRaMesher/LoRaMesher"
  category: "low-bandwidth-lossy-long-range"
  rule_type: "state_machine"
  # ...
```

### Summary Statistics

```json
// docs/rules/extraction_summary.json
{
  "total_rules": 247,
  "by_category": {
    "low-bandwidth-lossy-long-range": 68,
    "low-bandwidth-stable": 52,
    "high-bandwidth-lossy": 41,
    "high-bandwidth-stable": 38,
    "platform": 48
  },
  "by_type": {
    "configuration": 89,
    "state_machine": 23,
    "message_format": 18,
    "timing": 27,
    "routing": 31,
    "security": 15,
    "api": 22,
    "constant": 12,
    "data_structure": 5,
    "configuration_table": 4
  },
  "avg_confidence": 0.72,
  "extraction_date": "2024-11-20T10:30:00Z"
}
```

## Quality Assurance

### Validation Rules

1. **No duplicate rules** - Same repo + rule_type + name
2. **Minimum confidence** - 0.5 threshold
3. **Required fields** - repo, category, rule_type, name
4. **Parameter format** - Key-value pairs, no nested objects

### Post-Processing

```python
def post_process_rules(rules: List[ProtocolRule]) -> List[ProtocolRule]:
    # 1. Deduplicate
    seen = set()
    unique = []
    for rule in rules:
        key = (rule.repo, rule.rule_type, rule.name)
        if key not in seen:
            seen.add(key)
            unique.append(rule)
    
    # 2. Filter by confidence
    filtered = [r for r in unique if r.confidence >= 0.5]
    
    # 3. Sort by category, then confidence
    filtered.sort(key=lambda r: (r.category, -r.confidence))
    
    return filtered
```

## Integration with Guide Generation

### Comparison Matrix Updates

```python
def update_protocol_data_from_rules(rules: List[ProtocolRule]):
    """Update PROTOCOL_DATA dict with extracted rules."""
    for rule in rules:
        proto_name = infer_protocol_name(rule.repo)
        if proto_name not in PROTOCOL_DATA:
            PROTOCOL_DATA[proto_name] = {}
        
        # Map rule types to attributes
        mapping = {
            'configuration': 'Configuration Parameters',
            'timing': 'Timing Parameters',
            'routing': 'Routing Algorithm',
            'security': 'Security Features',
            # ...
        }
        
        attr = mapping.get(rule.rule_type)
        if attr and rule.parameters:
            PROTOCOL_DATA[proto_name][attr] = rule.parameters
```

### Documentation Updates

```python
def update_documentation_from_rules(rules: List[ProtocolRule]):
    """Generate documentation snippets from rules."""
    for category, cat_rules in groupby(rules, lambda r: r.category):
        # Generate parameter tables
        # Update configuration guides
        # Refresh comparison matrices
        pass
```

## Testing Extraction Quality

### Golden Set Evaluation

```python
def evaluate_extraction(golden_rules: List[ProtocolRule], extracted_rules: List[ProtocolRule]):
    """Evaluate extraction against golden standard."""
    # Match rules by repo + type + name similarity
    matches = 0
    false_positives = 0
    false_negatives = 0
    
    for golden in golden_rules:
        match = find_best_match(golden, extracted_rules)
        if match and match.confidence > 0.7:
            matches += 1
        else:
            false_negatives += 1
    
    for extracted in extracted_rules:
        if not any(golden.name == extracted.name and golden.repo == extracted.repo 
                   for golden in golden_rules):
            false_positives += 1
    
    precision = matches / (matches + false_positives) if (matches + false_positives) > 0 else 0
    recall = matches / (matches + false_negatives) if (matches + false_negatives) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'matches': matches,
        'false_positives': false_positives,
        'false_negatives': false_negatives
    }
```

## Continuous Improvement

### Feedback Loop

1. **Manual review** of extracted rules weekly
2. **Update classification keywords** based on missed rules
3. **Adjust confidence thresholds** based on manual review
4. **Add new rule types** as patterns emerge

### Versioning

```yaml
# docs/rules/version.yaml
version: "1.2.0"
extractor_version: "2.1.0"
last_updated: "2024-11-20"
schema_version: "1.0"
```