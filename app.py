from flask import Flask, render_template, request, jsonify
import json
import os
import time
from threading import Lock, Thread
from utils import get_ip_info, format_siem_log, capture_pcap, send_discord_alert

app = Flask(__name__)

# --- DONO FILES KA SETUP ---
SIEM_LOG_FILE = 'logs/siem_logs.json'
ALERT_LOG_FILE = 'logs/attack_alerts.json'

MAX_RETRIES = 5
log_lock = Lock()
blocked_ips = set()
attack_counts = {}

# Ensure folders exist
if not os.path.exists('logs'): os.makedirs('logs')
if not os.path.exists('logs/pcaps'): os.makedirs('logs/pcaps')

def save_logs(entry):
    with log_lock:
        # 1. Save in Enterprise SIEM Format (JSON Lines)
        with open(SIEM_LOG_FILE, 'a') as f: 
            f.write(json.dumps(entry) + '\n')
            
        # 2. Save in Normal Readable Format (Beautiful JSON for VS Code)
        try:
            with open(ALERT_LOG_FILE, 'r+') as f:
                try: data = json.load(f)
                except: data = []
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
        except FileNotFoundError:
            with open(ALERT_LOG_FILE, 'w') as f:
                json.dump([entry], f, indent=4)

def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"): return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

@app.route('/')
def index():
    ip = get_client_ip()
    if ip in blocked_ips: return render_template('error.html'), 503
    return render_template('login.html', error=None)

@app.route('/login', methods=['POST'])
def login():
    ip = get_client_ip()
    time.sleep(1.5) 
    
    if ip in blocked_ips: return render_template('error.html'), 503
    
    attack_counts[ip] = attack_counts.get(ip, 0) + 1
    is_blocked = attack_counts[ip] >= MAX_RETRIES
    
    if is_blocked and ip not in blocked_ips:
        blocked_ips.add(ip)
        Thread(target=capture_pcap, args=(ip,)).start()

    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    geo_info = get_ip_info(ip)
    siem_log = format_siem_log(ip, username, password, "brute_force", is_blocked)
    siem_log['geo'] = geo_info 
    
    # Save to BOTH files
    save_logs(siem_log)
    send_discord_alert(siem_log, geo_info)
    
    if is_blocked: return render_template('error.html'), 503
    return render_template('login.html', error="Invalid User ID or Password. Please try again.")

@app.route('/api/v1/users', methods=['GET'])
def fake_api():
    ip = get_client_ip()
    user_id = request.args.get('id', '')
    
    if user_id and ("'" in user_id or "OR" in user_id.upper() or "SELECT" in user_id.upper()):
        is_blocked = True
        blocked_ips.add(ip)
        Thread(target=capture_pcap, args=(ip,)).start()
        
        geo_info = get_ip_info(ip)
        siem_log = format_siem_log(ip, user_id, "SQLi_Payload", "sqli", is_blocked)
        siem_log['geo'] = geo_info
        
        # Save to BOTH files
        save_logs(siem_log)
        send_discord_alert(siem_log, geo_info)
        return jsonify({"error": "SQL syntax error near '" + user_id + "'"}), 500
        
    return jsonify({"status": "Unauthorized access"}), 401

@app.route('/error')
def error_page(): 
    return render_template('error.html')

@app.route('/cyguard-admin')
def admin():
    attacks = []
    with log_lock:
        if os.path.exists(SIEM_LOG_FILE):
            with open(SIEM_LOG_FILE, 'r') as f:
                for line in f:
                    if line.strip(): 
                        try: attacks.append(json.loads(line))
                        except: pass
    return render_template('admin_panel.html', attacks=attacks[::-1], blocked_count=len(blocked_ips))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 80))
    print(f"🚀 CyGuard SOC Running on Port {port}...")
    app.run(host='0.0.0.0', port=port, threaded=True)