#!/usr/bin/env python3
"""
DeepWiki Scraper for Communication Guide
Scrapes protocol documentation from DeepWiki and GitHub repositories.
"""

import argparse
import asyncio
import json
import random
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import yaml

# DeepWiki repositories to scrape
REPOS = [
    "meshtastic/firmware",
    "LoRaMesher/LoRaMesher",
    "espressif/esp-idf",
    "openwrt/routing",
    "openthread/openthread",
]

DEEPWIKI_BASE = "https://deepwiki.com"
GITHUB_BASE = "https://github.com"
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "scraped"
RULES_DIR = Path(__file__).parent.parent / "docs" / "rules"

# Scraping configuration - very conservative to avoid rate limits
MAX_PAGES_PER_REPO = 5  # Very low to avoid rate limits
BASE_DELAY = 30  # Base delay between requests (seconds) - increased significantly
MAX_DELAY = 300  # Maximum delay for retries (5 minutes)
REQUEST_TIMEOUT = 120  # Seconds


@dataclass
class ScrapedPage:
    repo: str
    url: str
    title: str
    content: str
    headings: List[Dict[str, Any]]
    code_blocks: List[str]
    tables: List[str]
    scraped_at: str


@dataclass
class ProtocolRule:
    repo: str
    category: str
    name: str
    description: str
    parameters: Dict[str, Any]
    source_url: str
    source_section: str


class DeepWikiScraper:
    def __init__(self, output_dir: Path = OUTPUT_DIR, rules_dir: Path = RULES_DIR):
        self.output_dir = output_dir
        self.rules_dir = rules_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
            }
        )
        self.pages: List[ScrapedPage] = []
        self.rules: List[ProtocolRule] = []
        self._last_request_time = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _throttle_request(self):
        """Throttle requests to avoid rate limiting."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < BASE_DELAY:
            wait = BASE_DELAY - elapsed + random.uniform(0, 2)
            await asyncio.sleep(wait)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch a URL with retries, throttling, and rate limit handling."""
        for attempt in range(6):  # More attempts
            try:
                await self._throttle_request()
                resp = await self.client.get(url)
                
                if resp.status_code == 429:
                    # Exponential backoff with jitter
                    wait = min(BASE_DELAY * (2 ** attempt) + random.uniform(0, 5), MAX_DELAY)
                    print(f"  Rate limited (429), waiting {wait:.1f}s... (attempt {attempt + 1}/6)")
                    await asyncio.sleep(wait)
                    continue
                    
                resp.raise_for_status()
                return resp.text
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < 5:
                    wait = min(BASE_DELAY * (2 ** attempt) + random.uniform(0, 5), MAX_DELAY)
                    print(f"  Rate limited (429), waiting {wait:.1f}s... (attempt {attempt + 1}/6)")
                    await asyncio.sleep(wait)
                    continue
                if e.response.status_code >= 500 and attempt < 5:
                    wait = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
                    print(f"  Server error ({e.response.status_code}), waiting {wait}s...")
                    await asyncio.sleep(wait)
                    continue
                if attempt == 5:
                    print(f"  Failed to fetch {url}: {e}")
                    return None
                    
            except asyncio.TimeoutError:
                if attempt == 5:
                    print(f"  Timeout fetching {url}")
                    return None
                wait = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
                print(f"  Timeout, waiting {wait}s... (attempt {attempt + 1}/6)")
                await asyncio.sleep(wait)
                
            except Exception as e:
                if attempt == 5:
                    print(f"  Failed to fetch {url}: {type(e).__name__}: {e}")
                    return None
                wait = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
                print(f"  Error ({type(e).__name__}), waiting {wait}s... (attempt {attempt + 1}/6)")
                await asyncio.sleep(wait)
                
        return None

    def parse_deepwiki_page(self, html: str, repo: str, url: str) -> ScrapedPage:
        """Parse DeepWiki page HTML into structured data."""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove navigation, scripts, styles
        for elem in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            elem.decompose()

        # Get main content
        main = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main'))
        if not main:
            main = soup.body

        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        title = title_elem.get_text(strip=True) if title_elem else "Unknown"

        # Extract headings with hierarchy
        headings = []
        for h in main.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': int(h.name[1]),
                'text': h.get_text(strip=True),
                'id': h.get('id', '')
            })

        # Extract code blocks
        code_blocks = []
        for code in main.find_all('code'):
            text = code.get_text(strip=True)
            if len(text) > 20:  # Skip inline code
                code_blocks.append(text)

        for pre in main.find_all('pre'):
            text = pre.get_text(strip=True)
            if text and text not in code_blocks:
                code_blocks.append(text)

        # Extract tables
        tables = []
        for table in main.find_all('table'):
            tables.append(str(table))

        # Get clean text content
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

    async def scrape_repo_index(self, repo: str) -> List[str]:
        """Get all page URLs from a DeepWiki repo index."""
        url = f"{DEEPWIKI_BASE}/{repo}"
        html = await self.fetch(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        urls = []

        # Find all links to wiki pages
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith(f'/{repo}/') and not href.endswith('/'):
                full_url = f"{DEEPWIKI_BASE}{href}"
                if full_url not in urls:
                    urls.append(full_url)

        # Also check for sidebar navigation
        for nav in soup.find_all('nav'):
            for link in nav.find_all('a', href=True):
                href = link['href']
                if href.startswith(f'/{repo}/'):
                    full_url = f"{DEEPWIKI_BASE}{href}"
                    if full_url not in urls:
                        urls.append(full_url)

        print(f"  Found {len(urls)} pages for {repo}")
        return urls

    async def scrape_repo(self, repo: str, max_pages: int = MAX_PAGES_PER_REPO):
        """Scrape all pages for a repository."""
        print(f"\nScraping {repo} (max {max_pages} pages)...")
        urls = await self.scrape_repo_index(repo)

        # Limit pages for initial run
        urls = urls[:max_pages]

        for i, url in enumerate(urls):
            print(f"  [{i+1}/{len(urls)}] {url}")
            html = await self.fetch(url)
            if html:
                page = self.parse_deepwiki_page(html, repo, url)
                self.pages.append(page)
                await self.save_page(page)
            # Longer delay between requests to avoid rate limiting
            await asyncio.sleep(BASE_DELAY + random.uniform(0, 3))

    async def save_page(self, page: ScrapedPage):
        """Save scraped page as markdown and JSON."""
        repo_dir = self.output_dir / page.repo.replace('/', '_')
        repo_dir.mkdir(parents=True, exist_ok=True)

        # Save as JSON (full data)
        json_file = repo_dir / f"{page.title[:100].replace('/', '_')}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(page), f, indent=2)

        # Save as Markdown (readable)
        md_file = repo_dir / f"{page.title[:100].replace('/', '_')}.md"
        with open(md_file, 'w') as f:
            f.write(f"# {page.title}\n\n")
            f.write(f"**Source:** {page.url}\n")
            f.write(f"**Repo:** {page.repo}\n")
            f.write(f"**Scraped:** {page.scraped_at}\n\n")
            f.write("## Headings\n\n")
            for h in page.headings:
                f.write(f"{'#' * h['level']} {h['text']}\n")
            f.write("\n## Content\n\n")
            f.write(page.content[:50000])  # Limit size
            if page.code_blocks:
                f.write("\n## Code Blocks\n\n")
                for i, code in enumerate(page.code_blocks[:10]):
                    f.write(f"### Code Block {i+1}\n```\n{code[:5000]}\n```\n\n")
            if page.tables:
                f.write("\n## Tables\n\n")
                for i, table in enumerate(page.tables[:5]):
                    f.write(f"### Table {i+1}\n{table}\n\n")

    def extract_rules(self):
        """Extract protocol rules from scraped pages."""
        print("\nExtracting protocol rules...")

        rule_patterns = {
            'config_parameter': re.compile(r'(set|get|enable|disable|config)\w*\s*[=:]\s*\w+', re.IGNORECASE),
            'constant': re.compile(r'(DEFAULT_|MAX_|MIN_|TIMEOUT_)\w+\s*=\s*[\d.]+', re.IGNORECASE),
            'state': re.compile(r'(STATE_|STATUS_|MODE_)\w+', re.IGNORECASE),
            'message_type': re.compile(r'(MSG_|TYPE_|MESSAGE_)\w+', re.IGNORECASE),
            'timing': re.compile(r'(\d+)\s*(ms|s|sec|min|hr)', re.IGNORECASE),
        }

        for page in self.pages:
            repo = page.repo
            category = self.categorize_repo(repo)

            # Extract from headings
            for heading in page.headings:
                text = heading['text']
                if any(kw in text.lower() for kw in ['config', 'parameter', 'setting', 'option', 'state', 'message', 'protocol', 'timing', 'routing']):
                    self.rules.append(ProtocolRule(
                        repo=repo,
                        category=category,
                        name=text,
                        description=f"Section: {text}",
                        parameters={},
                        source_url=page.url,
                        source_section=heading.get('id', '')
                    ))

            # Extract from code blocks
            for code in page.code_blocks:
                # Look for config structures, enums, constants
                lines = code.split('\n')
                for line in lines:
                    line = line.strip()
                    if any(kw in line for kw in ['struct', 'enum', '#define', 'const', 'config', 'parameter', 'timeout', 'interval', 'slot', 'hop']):
                        if len(line) > 10 and len(line) < 200:
                            self.rules.append(ProtocolRule(
                                repo=repo,
                                category=category,
                                name=line[:80],
                                description=f"Code: {line[:200]}",
                                parameters={'raw_line': line},
                                source_url=page.url,
                                source_section='code_block'
                            ))

            # Extract from tables (configuration tables)
            for table in page.tables:
                if any(kw in table.lower() for kw in ['parameter', 'value', 'default', 'range', 'config', 'setting']):
                    self.rules.append(ProtocolRule(
                        repo=repo,
                        category=category,
                        name="Configuration Table",
                        description=f"Table with {table.count('<tr>')} rows",
                        parameters={'table_html': table[:5000]},
                        source_url=page.url,
                        source_section='table'
                    ))

        print(f"  Extracted {len(self.rules)} rules")

    def categorize_repo(self, repo: str) -> str:
        """Categorize repository by protocol type."""
        categories = {
            'meshtastic/firmware': 'low-bandwidth-lossy-long-range',
            'LoRaMesher/LoRaMesher': 'low-bandwidth-lossy-long-range',
            'espressif/esp-idf': 'platform',
            'openwrt/routing': 'high-bandwidth-lossy',
            'openthread/openthread': 'low-bandwidth-stable',
        }
        return categories.get(repo, 'unknown')

    def save_rules(self):
        """Save extracted rules as YAML."""
        # Group by category
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

        # Also save all rules
        with open(self.rules_dir / 'all_rules.yaml', 'w') as f:
            yaml.dump([asdict(r) for r in self.rules], f, default_flow_style=False, sort_keys=False)

        print(f"Saved rules to {self.rules_dir}")

    async def run(self, max_pages_per_repo: int = 30):
        """Run full scraping pipeline."""
        print("Starting DeepWiki scraping...")

        for repo in REPOS:
            await self.scrape_repo(repo, max_pages_per_repo)

        self.extract_rules()
        self.save_rules()

        # Save summary
        summary = {
            'scraped_at': datetime.now().isoformat(),
            'repos': REPOS,
            'total_pages': len(self.pages),
            'total_rules': len(self.rules),
            'pages_per_repo': {repo: sum(1 for p in self.pages if p.repo == repo) for repo in REPOS}
        }
        with open(self.output_dir / 'scrape_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\nDone! Scraped {len(self.pages)} pages, extracted {len(self.rules)} rules")
        return summary


async def main():
    import argparse
    parser = argparse.ArgumentParser(description='Scrape DeepWiki for protocol documentation')
    parser.add_argument('--max-pages', type=int, default=MAX_PAGES_PER_REPO,
                        help=f'Max pages per repository (default: {MAX_PAGES_PER_REPO})')
    parser.add_argument('--repos', nargs='*', default=REPOS,
                        help='Repositories to scrape (default: all)')
    parser.add_argument('--delay', type=int, default=BASE_DELAY,
                        help=f'Base delay between requests in seconds (default: {BASE_DELAY})')
    args = parser.parse_args()
    
    # Update global config if provided
    import sys
    this_module = sys.modules[__name__]
    this_module.BASE_DELAY = args.delay
    
    async with DeepWikiScraper() as scraper:
        await scraper.run(max_pages_per_repo=args.max_pages)


if __name__ == '__main__':
    asyncio.run(main())