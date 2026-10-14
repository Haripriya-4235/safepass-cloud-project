/**
 * SafePass Women Safety & Safe Route Finder
 * Interactive Features: Dynamic Theming, Custom Moving Cursor Halo, 3D Card Tilt,
 * Live Safety Vigilance Clock, Sound FX, & Scroll Progress Indicator.
 */

(function () {
    'use strict';

    // ─── 1. Theme Switcher (Light / Dark / Night-Safety) ──────────────────────
    const THEME_KEY = 'safepass_theme';
    const SOUND_KEY = 'safepass_sound_fx';
    const CURSOR_KEY = 'safepass_cursor_fx';

    window.setTheme = function (theme) {
        if (!['light', 'dark', 'night-safety'].includes(theme)) theme = 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);
        updateThemeUI(theme);
        playTone(theme === 'night-safety' ? 520 : theme === 'dark' ? 440 : 660, 0.08);
    };

    function updateThemeUI(theme) {
        const iconEl = document.getElementById('themeCurrentIcon');
        const textEl = document.getElementById('themeCurrentText');
        if (!iconEl || !textEl) return;

        if (theme === 'dark') {
            iconEl.innerHTML = '<i class="fa-solid fa-moon text-primary"></i>';
            textEl.textContent = 'Midnight';
        } else if (theme === 'night-safety') {
            iconEl.innerHTML = '<i class="fa-solid fa-shield-halved text-success"></i>';
            textEl.textContent = 'Night Safe';
        } else {
            iconEl.innerHTML = '<i class="fa-solid fa-sun text-warning"></i>';
            textEl.textContent = 'Day Mode';
        }
    }

    function initTheme() {
        const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeUI(savedTheme);
    }

    // ─── 2. Web Audio Sound Feedback (Zero external assets needed) ────────────
    let audioCtx = null;
    let soundEnabled = localStorage.getItem(SOUND_KEY) !== 'false';

    window.toggleSoundFX = function () {
        soundEnabled = !soundEnabled;
        localStorage.setItem(SOUND_KEY, soundEnabled);
        const badge = document.getElementById('soundFxBadge');
        if (badge) badge.textContent = soundEnabled ? 'On' : 'Off';
        if (soundEnabled) playTone(880, 0.1);
    };

    function playTone(freq, duration) {
        if (!soundEnabled) return;
        try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        } catch (e) { }
    }

    // ─── 3. Smooth Moving Glowing Halo Cursor ─────────────────────────────────
    let cursorEnabled = localStorage.getItem(CURSOR_KEY) !== 'false';
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let haloX = mouseX;
    let haloY = mouseY;
    let cursorDot = null;
    let cursorHalo = null;

    window.toggleCustomCursor = function () {
        cursorEnabled = !cursorEnabled;
        localStorage.setItem(CURSOR_KEY, cursorEnabled);
        const badge = document.getElementById('cursorFxBadge');
        if (badge) badge.textContent = cursorEnabled ? 'On' : 'Off';
        if (cursorDot && cursorHalo) {
            cursorDot.style.display = cursorEnabled ? 'block' : 'none';
            cursorHalo.style.display = cursorEnabled ? 'block' : 'none';
        }
        playTone(soundEnabled ? 700 : 0, 0.08);
    };

    function initCustomCursor() {
        // Only initialize on desktop with fine mouse pointer
        if (!window.matchMedia('(pointer: fine)').matches) return;

        cursorDot = document.createElement('div');
        cursorDot.id = 'cursor-dot';
        cursorHalo = document.createElement('div');
        cursorHalo.id = 'cursor-halo';

        if (!cursorEnabled) {
            cursorDot.style.display = 'none';
            cursorHalo.style.display = 'none';
        }

        document.body.appendChild(cursorDot);
        document.body.appendChild(cursorHalo);

        const cursorBadge = document.getElementById('cursorFxBadge');
        if (cursorBadge) cursorBadge.textContent = cursorEnabled ? 'On' : 'Off';
        const soundBadge = document.getElementById('soundFxBadge');
        if (soundBadge) soundBadge.textContent = soundEnabled ? 'On' : 'Off';

        window.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            if (cursorDot) {
                cursorDot.style.left = mouseX + 'px';
                cursorDot.style.top = mouseY + 'px';
            }
        });

        // Hover scale & magnetic glow on interactive elements
        const hoverSelector = 'a, button, input, select, textarea, .card, .report-card, .filter-pill, .badge, .doc-pill';
        document.addEventListener('mouseover', (e) => {
            if (e.target.closest(hoverSelector) && cursorHalo) {
                cursorHalo.classList.add('hovering');
            }
        });
        document.addEventListener('mouseout', (e) => {
            if (e.target.closest(hoverSelector) && cursorHalo) {
                cursorHalo.classList.remove('hovering');
            }
        });

        // Mouse click ripple spark
        window.addEventListener('mousedown', (e) => {
            if (cursorHalo) cursorHalo.classList.add('clicking');
            if (cursorEnabled) {
                const ripple = document.createElement('div');
                ripple.className = 'click-ripple';
                ripple.style.left = e.clientX + 'px';
                ripple.style.top = e.clientY + 'px';
                document.body.appendChild(ripple);
                setTimeout(() => ripple.remove(), 600);
            }
        });

        window.addEventListener('mouseup', () => {
            if (cursorHalo) cursorHalo.classList.remove('clicking');
        });

        // Smooth physics-based trailing ring (lerp loop)
        function renderLoop() {
            if (cursorEnabled && cursorHalo) {
                haloX += (mouseX - haloX) * 0.18;
                haloY += (mouseY - haloY) * 0.18;
                cursorHalo.style.left = haloX + 'px';
                cursorHalo.style.top = haloY + 'px';
            }
            requestAnimationFrame(renderLoop);
        }
        renderLoop();
    }

    // ─── 4. 3D Card Interactive Perspective Tilt ───────────────────────────────
    function initCardTilt() {
        if (!window.matchMedia('(pointer: fine)').matches) return;

        document.addEventListener('mousemove', (e) => {
            const card = e.target.closest('.report-card, .hover-lift');
            if (!card) return;

            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            const tiltX = (y / rect.height) * -8;
            const tiltY = (x / rect.width) * 8;

            card.style.transform = `perspective(1000px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) translateY(-4px)`;
        });

        document.addEventListener('mouseout', (e) => {
            const card = e.target.closest('.report-card, .hover-lift');
            if (card) {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
            }
        });
    }

    // ─── 5. Live Commuter Vigilance Clock ─────────────────────────────────────
    function initSafetyClock() {
        function updateClock() {
            const now = new Date();
            const timeStr = now.toLocaleTimeString([], { hour12: false });
            const clockEl = document.getElementById('liveClock');
            const badgeEl = document.getElementById('vigilanceBadge');
            const dotEl   = document.getElementById('vigilanceDot');
            if (clockEl) clockEl.textContent = timeStr;

            const hour = now.getHours();
            if (badgeEl && dotEl) {
                if (hour >= 22 || hour < 5) {
                    badgeEl.className = 'badge bg-danger text-white border border-danger-subtle px-2 py-0';
                    badgeEl.textContent = 'Night Watch 🔴';
                    dotEl.style.backgroundColor = '#ef4444';
                } else if (hour >= 18) {
                    badgeEl.className = 'badge bg-warning text-dark border border-warning-subtle px-2 py-0';
                    badgeEl.textContent = 'Evening Watch 🟡';
                    dotEl.style.backgroundColor = '#f59e0b';
                } else {
                    badgeEl.className = 'badge bg-success text-white border border-success-subtle px-2 py-0';
                    badgeEl.textContent = 'Day Watch 🟢';
                    dotEl.style.backgroundColor = '#10b981';
                }
            }
        }
        setInterval(updateClock, 1000);
        updateClock();
    }

    // ─── 6. Floating Scroll to Top with Circular Progress ─────────────────────
    function initScrollProgress() {
        const btn = document.getElementById('scrollToTopBtn');
        const circle = document.getElementById('scrollProgressCircle');
        if (!btn || !circle) return;

        const radius = circle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = circumference;

        window.addEventListener('scroll', () => {
            const scrollTop = window.scrollY || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const progress = scrollHeight > 0 ? scrollTop / scrollHeight : 0;
            const offset = circumference - (progress * circumference);
            circle.style.strokeDashoffset = offset;

            if (scrollTop > 220) {
                btn.classList.add('visible');
            } else {
                btn.classList.remove('visible');
            }
        });
    }

    // ─── Document Ready ───────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        initTheme();
        initCustomCursor();
        initCardTilt();
        initSafetyClock();
        initScrollProgress();
    });
})();
