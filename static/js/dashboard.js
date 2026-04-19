let map = L.map('attackMap').setView([20.5937, 78.9629], 4); // Center on India
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CyGuard Intelligence'
}).addTo(map);

let markers = {};

function fetchStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            // Update Top Stats
            document.getElementById('total-attacks').innerText = data.attacks.length;
            document.getElementById('blocked-count').innerText = data.total_blocked;
            const uniqueIPs = new Set(data.attacks.map(a => a.ip));
            document.getElementById('unique-ips').innerText = uniqueIPs.size;
            
            if(data.attacks.length > 0) {
                document.getElementById('last-seen').innerText = data.attacks[data.attacks.length-1].timestamp;
            }

            // Update Table
            const tbody = document.getElementById('logsBody');
            tbody.innerHTML = '';
            
            // Reverse loop to show latest first
            data.attacks.slice().reverse().forEach(attack => {
                // Add Map Marker
                if (!markers[attack.ip] && attack.geo.lat) {
                    let color = attack.blocked ? 'red' : '#00ff00';
                    let marker = L.circleMarker([attack.geo.lat, attack.geo.lon], {
                        radius: 8,
                        fillColor: color,
                        color: "#fff",
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(map);
                    
                    marker.bindPopup(`<b>IP:</b> ${attack.ip}<br><b>Pass:</b> ${attack.password}`);
                    markers[attack.ip] = marker;
                }

                // Add Table Row
                let row = `<tr>
                    <td>${attack.timestamp}</td>
                    <td><span class="badge ${attack.blocked ? 'bg-danger' : 'bg-secondary'}">${attack.ip}</span></td>
                    <td>${attack.geo.city}, ${attack.geo.country}</td>
                    <td>${attack.username}</td>
                    <td>${attack.password}</td>
                    <td>${attack.blocked ? '🚫 BLOCKED' : '🟢 Active'}</td>
                    <td>${attack.blocked ? `<button class="btn btn-xs btn-success" onclick="unblockIP('${attack.ip}')">Unblock</button>` : ''}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        });
}

function unblockIP(ip) {
    fetch(`/api/unblock/${ip}`).then(res => res.json()).then(data => {
        alert(data.message);
        fetchStats();
    });
}

function exportPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    doc.setFontSize(18);
    doc.text("CYGUARD THREAT INTELLIGENCE REPORT", 14, 20);
    doc.setFontSize(11);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);
    doc.text("Confidential Forensic Data", 14, 35);
    
    doc.autoTable({
        html: '#logsTable',
        startY: 40,
        theme: 'grid',
        headStyles: { fillColor: [0, 128, 0] }
    });
    
    doc.save('CyGuard_Forensic_Report.pdf');
}

// Auto-refresh every 5 seconds
setInterval(fetchStats, 5000);
fetchStats();