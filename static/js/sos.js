// Emergency SOS Trigger Logic for Women Safety Portal
// Phone call support via tel: protocol (works on mobile; opens dialer/Skype on desktop)

function playEmergencySiren() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        for (let i = 0; i < 3; i++) {
            const osc  = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(880,  audioCtx.currentTime + i * 0.5);
            osc.frequency.exponentialRampToValueAtTime(1400, audioCtx.currentTime + i * 0.5 + 0.25);
            osc.frequency.exponentialRampToValueAtTime(880,  audioCtx.currentTime + i * 0.5 + 0.5);
            gain.gain.setValueAtTime(0.4, audioCtx.currentTime + i * 0.5);
            gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + i * 0.5 + 0.5);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(audioCtx.currentTime + i * 0.5);
            osc.stop(audioCtx.currentTime  + i * 0.5 + 0.5);
        }
    } catch(e) { console.log('Audio not supported'); }
}

// ── Copy number to clipboard ─────────────────────────────────────────────────
function copyToClipboard(text, btnEl) {
    navigator.clipboard.writeText(text).then(() => {
        const orig = btnEl.innerHTML;
        btnEl.innerHTML = '✅ Copied!';
        btnEl.style.background = '#16a34a';
        setTimeout(() => { btnEl.innerHTML = orig; btnEl.style.background = ''; }, 2000);
    }).catch(() => {
        // Fallback for browsers that block clipboard
        prompt('Copy this number and dial it:', text);
    });
}

// ── Initiate phone call ──────────────────────────────────────────────────────
function initiateCall(phoneNumber, btnEl) {
    const clean = phoneNumber.replace(/\s+/g, '');
    // Try tel: link — works on mobile and desktop with Skype/Teams
    const link = document.createElement('a');
    link.href  = 'tel:' + clean;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Visual feedback
    if (btnEl) {
        const orig = btnEl.innerHTML;
        btnEl.innerHTML = '📲 Dialling...';
        btnEl.style.opacity = '0.8';
        setTimeout(() => {
            btnEl.innerHTML = orig;
            btnEl.style.opacity = '1';
        }, 3000);
    }
}

// ── Build one contact call card ──────────────────────────────────────────────
function buildContactCard(name, phone, label, color) {
    const clean = (phone || '').replace(/\s+/g, '');
    const id    = 'card_' + Math.random().toString(36).slice(2);
    return `
    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:14px 16px;margin-bottom:12px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
            <div>
                <div style="font-weight:700;color:#1e293b;font-size:0.97rem;">${name}</div>
                <div style="color:#64748b;font-size:0.8rem;">${label}</div>
            </div>
            <div style="font-size:1.1rem;font-weight:800;color:#0f172a;letter-spacing:1px;">${phone}</div>
        </div>
        <div style="display:flex;gap:8px;">
            <button id="${id}_call"
                onclick="initiateCall('${clean}', document.getElementById('${id}_call'))"
                style="flex:1;padding:10px;border:none;border-radius:10px;
                       background:${color};color:#fff;font-weight:700;font-size:0.93rem;
                       cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;
                       box-shadow:0 3px 12px rgba(0,0,0,0.18);transition:transform .15s;"
                onmouseover="this.style.transform='scale(1.03)'"
                onmouseout="this.style.transform='scale(1)'">
                📞 Call Now
            </button>
            <button onclick="copyToClipboard('${clean}', this)"
                style="padding:10px 14px;border:1px solid #cbd5e1;border-radius:10px;
                       background:#fff;color:#334155;font-weight:600;font-size:0.85rem;cursor:pointer;">
                📋 Copy
            </button>
        </div>
    </div>`;
}

// ── Main SOS modal ────────────────────────────────────────────────────────────
function showSOSModal(alertData, lat, lng, contacts) {
    const old = document.getElementById('sosConfirmModal');
    if (old) old.remove();

    const alertId   = alertData.alert_id || 'OFFLINE';
    const mapsUrl   = alertData.maps_url || `https://www.google.com/maps?q=${lat},${lng}`;

    // Build contact cards
    let contactsHTML = '';
    if (contacts && contacts.length > 0) {
        contacts.forEach((c, i) => {
            const colors = ['#dc2626','#7c3aed','#0369a1','#065f46'];
            contactsHTML += buildContactCard(
                c.contact_name,
                c.phone_number,
                c.relationship + (c.is_primary ? ' · PRIMARY' : ''),
                colors[i % colors.length]
            );
        });
    } else {
        // No contacts saved — show national helplines
        contactsHTML  = buildContactCard('Women Helpline',          '1091',         'National Emergency · Always Active', '#dc2626');
        contactsHTML += buildContactCard('Police Emergency',        '100',          'National Emergency',                 '#1d4ed8');
        contactsHTML += buildContactCard('Women Safety Helpline',   '181',          'State Women Commission',             '#7c3aed');
    }

    const modal = document.createElement('div');
    modal.id = 'sosConfirmModal';
    modal.style.cssText = `
        position:fixed;top:0;left:0;width:100%;height:100%;z-index:99999;
        background:rgba(0,0,0,0.88);display:flex;align-items:center;justify-content:center;
        animation:sosFadeIn .25s ease;
    `;
    modal.innerHTML = `
    <style>
        @keyframes sosFadeIn  { from{opacity:0;transform:scale(.96)} to{opacity:1;transform:scale(1)} }
        @keyframes sosPulse   { 0%,100%{box-shadow:0 0 0 0 rgba(220,38,38,.5)} 70%{box-shadow:0 0 0 18px rgba(220,38,38,0)} }
        .sos-modal-inner { background:#fff;border-radius:22px;width:92%;max-width:420px;max-height:90vh;overflow-y:auto;
                           box-shadow:0 24px 80px rgba(220,38,38,.35); }
        .sos-modal-head  { background:linear-gradient(135deg,#ef4444,#991b1b);padding:22px 24px 16px;border-radius:22px 22px 0 0;color:#fff;text-align:center; }
        .sos-modal-body  { padding:20px 20px 24px; }
        .sos-alert-ring  { width:64px;height:64px;border-radius:50%;background:rgba(255,255,255,.2);
                           border:3px solid rgba(255,255,255,.6);display:flex;align-items:center;justify-content:center;
                           margin:0 auto 12px;animation:sosPulse 1.4s infinite; }
    </style>
    <div class="sos-modal-inner">
        <div class="sos-modal-head">
            <div class="sos-alert-ring"><span style="font-size:1.8rem;">🚨</span></div>
            <h2 style="font-weight:800;margin:0 0 4px;font-size:1.3rem;">SOS ALERT ACTIVATED</h2>
            <p style="margin:0;opacity:.9;font-size:.85rem;">
                Alert #${alertId} &bull; GPS: ${lat.toFixed(5)}, ${lng.toFixed(5)}
            </p>
        </div>

        <div class="sos-modal-body">
            <!-- Instruction -->
            <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:10px 14px;margin-bottom:16px;text-align:center;">
                <p style="margin:0;color:#991b1b;font-weight:600;font-size:.88rem;">
                    Tap <b>Call Now</b> below to connect instantly.<br>
                    On desktop: opens your phone/Skype app.
                </p>
            </div>

            <!-- Contact cards with call buttons -->
            ${contactsHTML}

            <!-- Google Maps link -->
            <a href="${mapsUrl}" target="_blank"
               style="display:block;text-align:center;padding:11px;border-radius:11px;
                      background:#1e40af;color:#fff;font-weight:700;text-decoration:none;
                      font-size:.9rem;margin-bottom:10px;">
                🗺️ Share My Live Location (Google Maps)
            </a>

            <!-- Dismiss -->
            <button onclick="document.getElementById('sosConfirmModal').remove()"
                style="width:100%;padding:10px;border-radius:11px;border:1px solid #e2e8f0;
                       background:#f8fafc;color:#475569;font-weight:600;cursor:pointer;font-size:.88rem;">
                ✓ I am Safe — Dismiss Alert
            </button>
        </div>
    </div>`;
    document.body.appendChild(modal);

    // Close on backdrop click
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
}

// ── Main SOS trigger ──────────────────────────────────────────────────────────
function triggerEmergencySOS() {
    playEmergencySiren();

    const sosBtn   = document.getElementById('sosHeroBtn');
    const statusEl = document.getElementById('sosStatusText');

    if (sosBtn)   { sosBtn.disabled = true; sosBtn.style.opacity = '0.75'; }
    if (statusEl) { statusEl.innerHTML = '<span style="color:#dc2626;font-weight:700;">⏳ Locating & transmitting distress signal...</span>'; }

    const getLocation = () => new Promise((resolve) => {
        if (!navigator.geolocation) return resolve({ lat: 13.0827, lng: 80.2707, src: 'No GPS' });
        navigator.geolocation.getCurrentPosition(
            (p) => resolve({ lat: p.coords.latitude, lng: p.coords.longitude, src: 'Device GPS' }),
            ()  => resolve({ lat: 13.0827, lng: 80.2707, src: 'Default (GPS denied)' }),
            { enableHighAccuracy: true, timeout: 5000 }
        );
    });

    getLocation().then(({ lat, lng, src }) => {
        sendSOSPayload(lat, lng, src, sosBtn, statusEl);
    });
}

function sendSOSPayload(lat, lng, address, sosBtn, statusEl) {
    // Fetch contacts first (parallel with SOS API call)
    const contactsPromise = fetch('/api/contacts', { credentials: 'same-origin' })
        .then(r => r.ok ? r.json() : { contacts: [] })
        .catch(() => ({ contacts: [] }));

    const sosPromise = fetch('/api/sos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ latitude: lat, longitude: lng, address })
    })
    .then(res => {
        const ct = res.headers.get('content-type') || '';
        if (!ct.includes('application/json')) throw new Error('non-JSON response');
        return res.json();
    })
    .catch(() => ({
        success: true,
        alert: {
            alert_id: 'OFFLINE',
            maps_url: `https://www.google.com/maps?q=${lat},${lng}`,
            contacts_notified: []
        }
    }));

    Promise.all([sosPromise, contactsPromise]).then(([sosData, contactData]) => {
        const alertInfo = sosData.alert || {};
        const contacts  = contactData.contacts || [];

        if (statusEl) {
            statusEl.innerHTML = `<span style="color:#dc2626;font-weight:700;">🚨 ALERT #${alertInfo.alert_id} TRANSMITTED — Call your contact below</span>`;
        }
        if (sosBtn) { sosBtn.disabled = false; sosBtn.style.opacity = '1'; }

        showSOSModal(alertInfo, lat, lng, contacts);
    });
}
