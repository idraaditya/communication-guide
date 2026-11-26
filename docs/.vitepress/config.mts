import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Communication Protocols Guide',
  description: 'Comprehensive guide for embedded device communication protocols across bandwidth/stability categories',
  lang: 'en-US',
  lastUpdated: true,
  cleanUrls: true,
  
  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'Comm Guide',
    
    nav: [
      { text: 'Introduction', link: '/introduction/overview' },
      { text: 'Categories', items: [
        { text: 'Low BW, Lossy, Long Range', link: '/category1/protocol-comparison' },
        { text: 'Low BW, Stable', link: '/category2/protocol-comparison' },
        { text: 'High BW, Lossy', link: '/category3/protocol-comparison' },
        { text: 'High BW, Stable', link: '/category4/protocol-comparison' },
      ]},
      { text: 'ESP32 Setup', items: [
        { text: 'LoRaMesher', link: '/category1/esp32-setup/loramesher-esp32' },
        { text: 'Meshtastic', link: '/category1/esp32-setup/meshtastic-esp32' },
        { text: 'OpenThread', link: '/category2/esp32-setup/openthread-esp32' },
        { text: 'Zigbee', link: '/category2/esp32-setup/zigbee-esp32' },
        { text: 'BLE Mesh', link: '/category2/esp32-setup/ble-mesh-esp32' },
        { text: 'Babel/WiFi Mesh', link: '/category3/esp32-setup/babel-wifi-esp32' },
        { text: 'WireGuard', link: '/category4/esp32-setup/wireguard-esp32' },
      ]},
      { text: 'Cross-Cutting', items: [
        { text: 'Hardware Selection', link: '/cross-cutting/hardware-selection-guide' },
        { text: 'Security Comparison', link: '/cross-cutting/security-comparison' },
        { text: 'Power Management', link: '/cross-cutting/power-management' },
        { text: 'Testing & Benchmarking', link: '/cross-cutting/testing-benchmarking' },
        { text: 'Migration Guide', link: '/cross-cutting/migration-guide' },
      ]},
      { text: 'DeepWiki Scraping', link: '/scraping/scraping-strategy' },
    ],
    
    sidebar: {
      '/introduction/': [
        { text: 'Overview', link: '/introduction/overview' },
        { text: 'Device Categories', link: '/introduction/device-categories' },
        { text: 'Protocol Landscape', link: '/introduction/protocol-landscape' },
      ],
      '/category1/': [
        { text: 'Protocol Comparison', link: '/category1/protocol-comparison' },
        { text: 'Top Algorithms', link: '/category1/top-algorithms' },
        { text: 'ESP32 Setup', items: [
          { text: 'LoRaMesher on ESP32', link: '/category1/esp32-setup/loramesher-esp32' },
          { text: 'Meshtastic on ESP32', link: '/category1/esp32-setup/meshtastic-esp32' },
          { text: 'Hardware Recommendations', link: '/category1/esp32-setup/hardware-recommendations' },
        ]},
      ],
      '/category2/': [
        { text: 'Protocol Comparison', link: '/category2/protocol-comparison' },
        { text: 'Top Algorithms', link: '/category2/top-algorithms' },
        { text: 'ESP32 Setup', items: [
          { text: 'OpenThread on ESP32-H2/C6', link: '/category2/esp32-setup/openthread-esp32' },
          { text: 'Zigbee on ESP32-H2/C6', link: '/category2/esp32-setup/zigbee-esp32' },
          { text: 'BLE Mesh on ESP32/S3', link: '/category2/esp32-setup/ble-mesh-esp32' },
        ]},
      ],
      '/category3/': [
        { text: 'Protocol Comparison', link: '/category3/protocol-comparison' },
        { text: 'Top Algorithms', link: '/category3/top-algorithms' },
        { text: 'ESP32 Setup', items: [
          { text: 'Babel/WiFi Mesh on ESP32-S3', link: '/category3/esp32-setup/babel-wifi-esp32' },
          { text: 'BATMAN-ADV (OpenWrt)', link: '/category3/esp32-setup/batman-adv-openwrt' },
          { text: '802.11s on ESP32-S3', link: '/category3/esp32-setup/80211s-esp32' },
        ]},
      ],
      '/category4/': [
        { text: 'Protocol Comparison', link: '/category4/protocol-comparison' },
        { text: 'Top Algorithms', link: '/category4/top-algorithms' },
        { text: 'ESP32 Setup', items: [
          { text: 'WireGuard on ESP32-S3', link: '/category4/esp32-setup/wireguard-esp32' },
          { text: 'BIRD2 (Linux)', link: '/category4/esp32-setup/bird2-linux' },
          { text: 'cjdns/Yggdrasil (Linux)', link: '/category4/esp32-setup/cjdns-yggdrasil-linux' },
        ]},
      ],
      '/cross-cutting/': [
        { text: 'Hardware Selection Guide', link: '/cross-cutting/hardware-selection-guide' },
        { text: 'Security Comparison', link: '/cross-cutting/security-comparison' },
        { text: 'Power Management', link: '/cross-cutting/power-management' },
        { text: 'Testing & Benchmarking', link: '/cross-cutting/testing-benchmarking' },
        { text: 'Migration Guide', link: '/cross-cutting/migration-guide' },
      ],
      '/scraping/': [
        { text: 'Scraping Strategy', link: '/scraping/scraping-strategy' },
        { text: 'Source Inventory', link: '/scraping/source-inventory' },
        { text: 'Automation Scripts', link: '/scraping/automation-scripts' },
        { text: 'Rule Extraction', link: '/scraping/rule-extraction' },
      ],
    },
    
    socialLinks: [
      { icon: 'github', link: 'https://github.com/yourusername/communication-guide' },
    ],
    
    footer: {
      message: 'Released under MIT License.',
      copyright: 'Copyright © 2024 Communication Guide Contributors',
    },
    
    search: {
      provider: 'local',
    },
    
    editLink: {
      pattern: 'https://github.com/yourusername/communication-guide/edit/main/docs/:path',
      text: 'Edit this page on GitHub',
    },
  },
  
  markdown: {
    theme: 'github-light',
    lineNumbers: true,
    toc: { level: [2, 3] },
  },
  
  vite: {
    optimizeDeps: {
      include: ['vue'],
    },
  },
})