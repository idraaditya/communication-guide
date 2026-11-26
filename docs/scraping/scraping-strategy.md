# DeepWiki Scraping Strategy

## Overview

This document describes the automated strategy for scraping DeepWiki documentation from key repositories to keep the Communication Protocols Guide current and accurate.

## Target Repositories

| Repository | DeepWiki URL | Category | Priority |
|------------|--------------|----------|----------|
| `meshtastic/firmware` | https://deepwiki.com/meshtastic/firmware | Cat 1 (LoRa) | High |
| `LoRaMesher/LoRaMesher` | https://deepwiki.com/LoRaMesher/LoRaMesher | Cat 1 (LoRa) | High |
| `espressif/esp-idf` | https://deepwiki.com/espressif/esp-idf | Platform (All) | High |
| `openwrt/routing` | https://deepwiki.com/openwrt/routing | Cat 3 (WiFi Mesh) | High |
| `openthread/openthread` | https://deepwiki.com/openthread/openthread | Cat 2 (Thread) | High |

## Scraping Architecture

```
┌─────────────────────────────────────────────────────────────────┐
                    SCRAPING PIPELINE                              
├─────────────────────────────────────────────────────────────────┤
                                                                 
  SCHEDULER (Weekly Cron)                                         
         │                                                        
         ▼                                                        
  ┌─────────────────────────────────────────────────────────┐   
  │ SCRAPER (Python + Playwright)                           │   
  │   • Fetch DeepWiki index pages                          │   
  │   • Extract all page URLs per repo                      │   
  │   • Render JS content (DeepWiki is SPA)                 │   
  │   • Parse HTML → structured data                        │   
  │   • Save as JSON + Markdown                             │   
  └─────────────────────────────────────────────────────────┘   
         │                                                        
         ▼                                                        
  ┌─────────────────────────────────────────────────────────┐   
  │ RULE EXTRACTOR (Python)                                 │   
  │   • Parse headings, code blocks, tables                 │   
  │   • Classify: config, state_machine, message_format,    │   
  │     timing, routing, security, api, constant            │   
  │   • Extract parameters from text/code                   │   
  │   • Save as structured YAML                             │   
  └─────────────────────────────────────────────────────────┘   
         │                                                        
         ▼                                                        
  ┌─────────────────────────────────────────────────────────┐   
  │ COMPARISON GENERATOR (Python)                           │   
  │   • Generate CSV/Markdown comparison matrices           │   
  │   • Update protocol data from extracted rules           │   
  │   • Generate category summary CSV                       │   
  └─────────────────────────────────────────────────────────┘   
         │                                                        
         ▼                                                        
  ┌─────────────────────────────────────────────────────────┐   
  │ GIT COMMIT (Auto-commit)                                │   
  │   • Commit updated scraped content                      │   
  │   • Commit updated rules                                │   
  │   • Commit updated comparison matrices                  │   
  └─────────────────────────────────────────────────────────┘   
         │                                                        
         ▼                                                        
  DOCS SITE REBUILD (VitePress)                                  
                                                                 
└─────────────────────────────────────────────────────────────────┘
```

## Scraper Implementation

### Core Components

```python
# scripts/scrape_deepwiki.py
class DeepWikiScraper:
    """Scrapes DeepWiki documentation from target repositories."""
    
    REPOS = [
        "meshtastic/firmware",
        "LoRaMesher/LoRaMesher", 
        "espressif/esp-idf",
        "openwrt/routing",
        "openthread/openthread",
    ]
    
    async def scrape_repo(self, repo: str, max_pages: int = 30):
        """Scrape all pages for a repository."""
        # 1. Get index page
        index_url = f"https://deepwiki.com/{repo}"
        html = await self.fetch(index_url)
        
        # 2. Extract page URLs from sidebar/navigation
        urls = self.extract_page_urls(html, repo)
        
        # 3. Scrape each page
        for url in urls[:max_pages]:
            page_html = await self.fetch(url)
            page = self.parse_page(page_html, repo, url)
            await self.save_page(page)
            
        # 4. Extract rules
        self.extract_rules()
        self.save_rules()
```

### Page Parsing

```python
def parse_deepwiki_page(self, html: str, repo: str, url: str) -> ScrapedPage:
    """Parse DeepWiki page HTML into structured data."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove navigation, scripts, styles
    for elem in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        elem.decompose()
    
    # Extract main content
    main = soup.find('main') or soup.find('article') or soup.body
    
    # Title
    title_elem = soup.find('h1') or soup.find('title')
    title = title_elem.get_text(strip=True) if title_elem else "Unknown"
    
    # Headings with hierarchy
    headings = []
    for h in main.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        headings.append({
            'level': int(h.name[1]),
            'text': h.get_text(strip=True),
            'id': h.get('id', '')
        })
    
    # Code blocks
    code_blocks = []
    for code in main.find_all('code'):
        text = code.get_text(strip=True)
        if len(text) > 20:
            code_blocks.append(text)
    for pre in main.find_all('pre'):
        text = pre.get_text(strip=True)
        if text and text not in code_blocks:
            code_blocks.append(text)
    
    # Tables
    tables = [str(t) for t in main.find_all('table')]
    
    # Clean text content
    content = main.get_text(separator='\n', strip=True)
    
    return ScrapedPage(
        repo=repo,
        url=url,
        title=title,
        content=content,
        headings=headings,
        code_blocks=code_blocks,
        tables=tables,
        scraped_at=datetime.now().isoformat()
    )
```

## Rule Extraction

### Classification Logic

```python
def classify_heading(self, text: str) -> Optional[str]:
    """Classify heading into rule type."""
    text_lower = text.lower()
    
    rules = {
        'configuration': ['config', 'parameter', 'setting', 'option'],
        'state_machine': ['state', 'status', 'mode', 'phase'],
        'message_format': ['message', 'packet', 'frame', 'format', 'header'],
        'timing': ['timing', 'slot', 'interval', 'timeout', 'period', 'schedule'],
        'routing': ['route', 'routing', 'forward', 'path', 'hop'],
        'security': ['security', 'encrypt', 'auth', 'key', 'crypto'],
        'api': ['api', 'callback', 'function', 'method', 'command'],
        'constant': ['define', 'const', 'default_', 'max_', 'min_', 'timeout_'],
    }
    
    for rule_type, keywords in rules.items():
        if any(kw in text_lower for kw in keywords):
            return rule_type
    return None
```

### Parameter Extraction

```python
def extract_params_from_text(self, text: str) -> Dict[str, Any]:
    """Extract parameters from text."""
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
    
    return params
```

## Output Formats

### Scraped Content (JSON + Markdown)

```
docs/scraped/
├── meshtastic_firmware/
│   ├── Overview.json
│   ├── Overview.md
│   ├── Router_Architecture.json
│   ├── Router_Architecture.md
│   └── ...
├── LoRaMesher_LoRaMesher/
│   ├── Overview.json
│   ├── Protocol_Specification.json
│   └── ...
├── espressif_esp-idf/
├── openwrt_routing/
└── openthread_openthread/
```

### Extracted Rules (YAML)

```
docs/rules/
├── low-bandwidth-lossy-long-range/
│   ├── rules.yaml
├── low-bandwidth-stable/
│   ├── rules.yaml
├── high-bandwidth-lossy/
│   ├── rules.yaml
├── high-bandwidth-stable/
│   ├── rules.yaml
├── platform/
│   ├── rules.yaml
└── all_rules.yaml
```

### Rule Structure

```yaml
- repo: "meshtastic/firmware"
  category: "low-bandwidth-lossy-long-range"
  rule_type: "configuration"
  name: "Mesh Configuration Options"
  description: "Section: Mesh Configuration Options"
  parameters:
    lora_region: "US"
    tx_power: "17"
    channel_name: "Primary"
  source_file: "Mesh_Configuration_Options.md"
  source_section: "mesh-configuration"
  confidence: 0.7
```

## Comparison Matrix Generation

### Protocol Data Integration

```python
# Manual curation + extracted rules
PROTOCOL_DATA = {
    'LoRaMesher': {
        'Architecture': 'TDMA + Distance Vector',
        'Layer': 'L3 (Application)',
        'Routing Algorithm': 'Distance Vector + ETX',
        'Metric': 'ETX Cost (hop_count × 65536/quality)',
        # ... from extracted rules + manual curation
    },
    'Meshtastic': { ... },
    # ... all protocols
}
```

### Output Formats

```bash
# CSV for data analysis
data/category1_comparison.csv
data/category2_comparison.csv
data/category3_comparison.csv
data/category4_comparison.csv

# Markdown for documentation
data/category1_comparison.md
data/category2_comparison.md
# ...

# Category summary
data/category_summary.csv
```

## GitHub Actions Workflow

### Weekly Scraping

```yaml
# .github/workflows/scrape-deepwiki.yml
name: Scrape DeepWiki

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly Sunday 2 AM UTC
  workflow_dispatch:
    inputs:
      max_pages:
        description: 'Max pages per repository'
        required: false
        default: '30'

permissions:
  contents: write

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - run: pip install -r requirements.txt
      
      - name: Scrape DeepWiki
        run: python scripts/scrape_deepwiki.py ${{ github.event.inputs.max_pages || 30 }}
      
      - name: Extract rules
        run: python scripts/extract_rules.py
      
      - name: Generate comparisons
        run: python scripts/generate_comparison.py
      
      - name: Commit changes
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: update scraped content and extracted rules [skip ci]"
          file_pattern: docs/scraped/** docs/rules/** data/*.csv
```

## Rate Limiting & Ethics

### DeepWiki Rate Limits

- **429 Too Many Requests** handling with exponential backoff
- **Max 30 pages per repo** per run
- **2 second delay** between requests
- **Respect robots.txt**

### Implementation

```python
async def fetch(self, url: str) -> Optional[str]:
    for attempt in range(5):
        try:
            resp = await self.client.get(url)
            if resp.status_code == 429:
                wait = 2 ** attempt * 5
                print(f"Rate limited, waiting {wait}s...")
                await asyncio.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            if attempt == 4:
                print(f"Failed to fetch {url}: {e}")
                return None
            await asyncio.sleep(2 ** attempt)
    return None
```

## Monitoring & Alerting

### Success Metrics

- Pages scraped per repo
- Rules extracted per category
- Comparison matrix freshness
- Git commit success

### Failure Handling

```yaml
notify:
  needs: scrape
  if: failure()
  runs-on: ubuntu-latest
  steps:
    - name: Alert on failure
      run: |
        echo "DeepWiki scraping failed" | \
        mail -s "Communication Guide Scraping Failed" maintainer@example.com
```

## Future Enhancements

1. **Incremental scraping** - Only changed pages
2. **GitHub webhook triggers** - Scrape on repo releases
3. **Multi-language support** - Chinese docs for espressif
4. **PDF export** - Include in weekly PDF builds
5. **Slack/Discord notifications** - Real-time alerts