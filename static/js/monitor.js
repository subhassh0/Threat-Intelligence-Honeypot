// Fingerprinting Script
document.getElementById('trapForm').onsubmit = function() {
    const data = {
        screen: `${window.screen.width}x${window.screen.height}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language,
        cores: navigator.hardwareConcurrency,
        platform: navigator.platform
    };
    document.getElementById('fingerprint_data').value = JSON.stringify(data);
};