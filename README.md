# CyGuard: Web Based Honeypot 

CyGuard is an advanced **deception-based cybersecurity tool** designed to attract, log, and analyze unauthorized access attempts in real-time. Built for Blue Team operations, it mimics a corporate portal and uses the **MITRE ATT&CK Framework** to classify threats.

## Key Features

- **Deception Portal:** Ultra-realistic corporate login interface with psychological triggers to keep attackers engaged.
- **MITRE ATT&CK Mapping:** Automatically tags attacks with Technique IDs (e.g., **T1110** for Brute Force, **T1190** for SQL Injection).
- **Dual Logging System:** - `siem_logs.json`: JSONL format for professional SIEM ingestion (Splunk/Wazuh).
  - `attack_alerts.json`: Human-readable JSON for manual forensic review.
- **Live Threat Intelligence:** - Real-time **Geo-location Tracking** (City/Country) of attackers.
  - Interactive **Threat Map** to visualize attack origins.
- **Active Defense:** Automated IP blocking after a threshold and background **PCAP (Packet Capture)** generation for deeper analysis.
- **Forensic Reporting:** One-click PDF export feature for security documentation.

## Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Mapping:** Leaflet.js (Open-source mapping library)
- **Forensics:** jsPDF, AutoTable
- **Alerting:** Discord Webhook Integration

## SOC Dashboard Preview

The dashboard provides a high-level overview of security events, including:
1. Total Attack Counts
2. Blocked Hostile IPs
3. Live Location Map
4. Detailed SIEM Event Logs

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/CyGuard-Honeypot.git](https://github.com/YOUR_USERNAME/CyGuard-Honeypot.git)
   cd CyGuard-Honeypot