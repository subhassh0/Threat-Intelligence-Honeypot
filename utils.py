import requests
import os
from datetime import datetime

# Yahan apna Discord Webhook URL paste karein
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "https://discord.com/api/webhooks/1495401074897715391/0zjJL2FsHPgXmmHbVTWjCGhMYPd7T8GpGaaPOWlgX5g1KXut10gWwAS7XwZfvQDzttKJ")

# --- MITRE ATT&CK MAPPING ---
MITRE_TAGS = {
    "brute_force": {"id": "T1110", "name": "Brute Force", "tactic": "Credential Access"},
    "sqli": {"id": "T1190", "name": "Exploit Public-Facing App", "tactic": "Initial Access"}
}

def get_ip_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon,isp", timeout=2).json()
        if response['status'] == 'success': 
            return response
    except: 
        pass
    # Fake Data for Localhost Demo
    return {"status": "success", "country": "India", "city": "New Delhi (Trace)", "lat": 28.6139, "lon": 77.2090, "isp": "Private Network"}

def format_siem_log(ip, username, password, attack_type, blocked):
    mitre = MITRE_TAGS.get(attack_type, {"id": "Unknown", "name": "Unknown", "tactic": "Unknown"})
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": "security_alert",
        "severity": "CRITICAL" if blocked else "WARNING",
        "src_ip": ip,
        "action": "blocked" if blocked else "allowed",
        "mitre_tactic": mitre["tactic"],
        "mitre_technique_id": mitre["id"],
        "payload": {"username_attempted": username, "password_attempted": password}
    }

def capture_pcap(ip):
    pcap_dir = "logs/pcaps"
    if not os.path.exists(pcap_dir): os.makedirs(pcap_dir)
    filename = f"{pcap_dir}/capture_{ip.replace('.','_')}_{datetime.now().strftime('%H%M%S')}.pcap"
    with open(filename, 'w') as f:
        f.write(f"PCAP CAPTURE MOCK FILE\nTarget IP: {ip}\nStatus: Ready for Analysis\nTrigger: MITRE Auto-Defense")

def send_discord_alert(siem_log, geo_info):
    if not DISCORD_WEBHOOK or "YOUR_WEBHOOK" in DISCORD_WEBHOOK: return
    technique_name = MITRE_TAGS.get('brute_force' if 'password_attempted' in siem_log['payload'] else 'sqli').get('name')
    embed = {
        "title": f"🚨 SIEM ALERT: {siem_log['mitre_technique_id']} Detected",
        "color": 16711680 if siem_log['severity'] == "CRITICAL" else 16753920,
        "fields": [
            {"name": "🛡️ MITRE Tactic", "value": f"`{siem_log['mitre_tactic']}`", "inline": False},
            {"name": "📡 Source IP", "value": f"`{siem_log['src_ip']}`", "inline": True},
            {"name": "🌍 Location", "value": f"{geo_info.get('city', 'Unknown')}", "inline": True},
            {"name": "🔑 Payload Data", "value": f"User: `{siem_log['payload'].get('username_attempted','')}`\nPass: `{siem_log['payload'].get('password_attempted','')}`", "inline": False},
            {"name": "🛑 Action Taken", "value": f"**{siem_log['action'].upper()}**", "inline": True}
        ],
        "footer": {"text": f"CyGuard SOC • {siem_log['timestamp']}"}
    }
    try: requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})
    except: pass