/**
 * Wellsy Frontend — Solar System Multi-Agent Renderer
 * Interactive Solar System canvas visualizer, voice transcript, WebSocket chat, conversation mode.
 */

// === DOM Elements ===
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const stopBtn = document.getElementById('stopBtn');
const liveClock = document.getElementById('liveClock');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const rateBarFill = document.getElementById('rateBarFill');
const rateBarText = document.getElementById('rateBarText');
const welcomeMessage = document.getElementById('welcomeMessage');
const micCanvas = document.getElementById('micCanvas');
const micBtn = document.getElementById('micBtn');
const jarvisCanvas = document.getElementById('jarvisCanvas');
const orbStatusText = document.getElementById('orbStatusText');
const transcriptContent = document.getElementById('transcriptContent');

const pillMedia = document.getElementById('pillMedia');
const pillComms = document.getElementById('pillComms');
const pillOS = document.getElementById('pillOS');
const pillResearch = document.getElementById('pillResearch');

// === State ===
let ws = null;
let isConnected = false;
let isThinking = false;
let isMicActive = false;
let conversationMode = false;
let messageCount = 0;
let orbState = 'idle'; // idle | listening | thinking | speaking
let activeAgent = null; // null | MediaAgent | CommsAgent | OSAgent | ResearchAgent

// === Live Clock ===
function updateClock() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    liveClock.textContent = `${h}:${m}:${s}`;
}
setInterval(updateClock, 1000);
updateClock();

// ============================================================
//  SOLAR SYSTEM CANVAS VISUALIZER
// ============================================================
const ctx = jarvisCanvas.getContext('2d');
const W = jarvisCanvas.width;
const H = jarvisCanvas.height;
const CX = W / 2;
const CY = H / 2;

// Planets Configuration (Sub-Agents)
const PLANETS = [
    // === Main Agent Planets ===
    { id: 'MediaAgent', name: 'MEDIA', icon: '🎵', radius: 75, speed: 0.012, size: 9, color: '#00d4ff', glow: 'rgba(0, 212, 255, 0.7)', angle: 0.5, pill: pillMedia, isAgent: true },
    { id: 'CommsAgent', name: 'COMMS', icon: '💬', radius: 110, speed: -0.008, size: 10, color: '#2ed573', glow: 'rgba(46, 213, 115, 0.7)', angle: 2.1, pill: pillComms, isAgent: true },
    { id: 'OSAgent', name: 'OS/SYS', icon: '🖥️', radius: 145, speed: 0.006, size: 11, color: '#3b8bff', glow: 'rgba(59, 139, 255, 0.7)', angle: 3.8, pill: pillOS, isAgent: true },
    { id: 'ResearchAgent', name: 'RESEARCH', icon: '🔬', radius: 175, speed: -0.004, size: 10, color: '#a855f7', glow: 'rgba(168, 85, 247, 0.7)', angle: 5.2, pill: pillResearch, isAgent: true },

    // === Ambient Orbital Bodies (decorative — no agent routing) ===
    { id: null, name: '', icon: '', radius: 48, speed: 0.022, size: 3.5, color: '#ff6b6b', glow: 'rgba(255, 107, 107, 0.4)', angle: 1.0, pill: null, isAgent: false },
    { id: null, name: '', icon: '', radius: 58, speed: -0.018, size: 2.5, color: '#ffd93d', glow: 'rgba(255, 217, 61, 0.4)', angle: 4.2, pill: null, isAgent: false },
    { id: null, name: '', icon: '', radius: 92, speed: 0.015, size: 4, color: '#6bcfff', glow: 'rgba(107, 207, 255, 0.4)', angle: 0.8, pill: null, isAgent: false },
    { id: null, name: '', icon: '', radius: 128, speed: -0.01, size: 3, color: '#ff9ff3', glow: 'rgba(255, 159, 243, 0.4)', angle: 5.6, pill: null, isAgent: false },
    { id: null, name: '', icon: '', radius: 160, speed: 0.007, size: 3.5, color: '#54a0ff', glow: 'rgba(84, 160, 255, 0.35)', angle: 1.9, pill: null, isAgent: false },
    { id: null, name: '', icon: '', radius: 190, speed: -0.005, size: 2.5, color: '#5f27cd', glow: 'rgba(95, 39, 205, 0.35)', angle: 3.3, pill: null, isAgent: false },
    { id: null, name: '', icon: '', radius: 196, speed: 0.003, size: 4, color: '#01a3a4', glow: 'rgba(1, 163, 164, 0.35)', angle: 0.3, pill: null, isAgent: false },
    { id: null, name: '', icon: '', radius: 55, speed: 0.025, size: 2, color: '#f368e0', glow: 'rgba(243, 104, 224, 0.3)', angle: 2.8, pill: null, isAgent: false },
];

// Photon particles flowing along beams when an agent is active
class PhotonParticle {
    constructor(targetPlanet) {
        this.targetPlanet = targetPlanet;
        this.progress = Math.random() * 0.3; // 0 (Sun) to 1 (Planet)
        this.speed = 0.02 + Math.random() * 0.03;
        this.size = 1.5 + Math.random() * 2;
    }
    update() {
        this.progress += this.speed;
        if (this.progress > 1) {
            this.progress = 0;
        }
    }
    draw(ctx, sunX, sunY, planetX, planetY, color) {
        const x = sunX + (planetX - sunX) * this.progress;
        const y = sunY + (planetY - sunY) * this.progress;
        ctx.beginPath();
        ctx.arc(x, y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.shadowColor = color;
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0;
    }
}

const photonMap = {};
PLANETS.forEach(p => {
    photonMap[p.id] = [new PhotonParticle(p), new PhotonParticle(p), new PhotonParticle(p)];
});

// Ambient background stardust
class Stardust {
    constructor() {
        this.reset();
    }
    reset() {
        this.x = Math.random() * W;
        this.y = Math.random() * H;
        this.size = Math.random() * 1.2;
        this.alpha = 0.1 + Math.random() * 0.4;
        this.vy = -(0.1 + Math.random() * 0.3);
    }
    update() {
        this.y += this.vy;
        if (this.y < 0) this.reset();
    }
    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 212, 255, ${this.alpha})`;
        ctx.fill();
    }
}
const stardustArray = Array.from({ length: 70 }, () => new Stardust());

// Draw Central Sun (Supervisor Core)
function drawSun(ctx, cx, cy, time, intensity) {
    const sunRadius = 22 + Math.sin(time * 2) * 2 + intensity * 8;
    
    // Outer Corona Glow
    const coronaGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, sunRadius * 2.8);
    coronaGrad.addColorStop(0, `rgba(0, 212, 255, ${0.3 + intensity * 0.3})`);
    coronaGrad.addColorStop(0.5, `rgba(59, 139, 255, ${0.15 + intensity * 0.2})`);
    coronaGrad.addColorStop(1, 'rgba(0, 212, 255, 0)');
    ctx.beginPath();
    ctx.arc(cx, cy, sunRadius * 2.8, 0, Math.PI * 2);
    ctx.fillStyle = coronaGrad;
    ctx.fill();

    // Core Flame
    const coreGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, sunRadius);
    coreGrad.addColorStop(0, '#ffffff');
    coreGrad.addColorStop(0.4, '#00d4ff');
    coreGrad.addColorStop(0.8, '#3b8bff');
    coreGrad.addColorStop(1, 'rgba(59, 139, 255, 0)');
    ctx.beginPath();
    ctx.arc(cx, cy, sunRadius, 0, Math.PI * 2);
    ctx.fillStyle = coreGrad;
    ctx.fill();

    // Center Supervisor Label
    ctx.font = '700 8px Orbitron, sans-serif';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('JARVIS', cx, cy);
}

// Render Loop
function renderSolarSystem() {
    const time = Date.now() / 1000;
    const intensity = getIntensity();
    
    ctx.clearRect(0, 0, W, H);

    // Draw stardust
    stardustArray.forEach(s => {
        s.update();
        s.draw(ctx);
    });

    // Draw Orbits & Planets
    PLANETS.forEach(p => {
        // Update angle
        const speedMult = (p.isAgent && activeAgent === p.id) ? 2.5 : 1;
        p.angle += p.speed * speedMult;

        const px = CX + Math.cos(p.angle) * p.radius;
        const py = CY + Math.sin(p.angle) * p.radius;

        const isActive = p.isAgent && activeAgent === p.id;

        // --- Ambient decorative bodies (no beams, no labels) ---
        if (!p.isAgent) {
            // Faint orbit trail
            ctx.beginPath();
            ctx.arc(CX, CY, p.radius, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
            ctx.lineWidth = 0.5;
            ctx.setLineDash([2, 8]);
            ctx.stroke();
            ctx.setLineDash([]);

            // Tiny atmospheric glow
            const ambientGlow = ctx.createRadialGradient(px, py, 0, px, py, p.size * 2);
            ambientGlow.addColorStop(0, p.glow);
            ambientGlow.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.beginPath();
            ctx.arc(px, py, p.size * 2, 0, Math.PI * 2);
            ctx.fillStyle = ambientGlow;
            ctx.fill();

            // Solid micro-planet core
            ctx.beginPath();
            ctx.arc(px, py, p.size, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 3;
            ctx.fill();
            ctx.shadowBlur = 0;
            return;
        }

        // --- Main Agent Planets (full visuals) ---

        // 1. Draw Orbit Ring
        ctx.beginPath();
        ctx.arc(CX, CY, p.radius, 0, Math.PI * 2);
        ctx.strokeStyle = isActive ? p.glow : 'rgba(0, 212, 255, 0.08)';
        ctx.lineWidth = isActive ? 1.5 : 0.8;
        if (!isActive) ctx.setLineDash([4, 6]);
        else ctx.setLineDash([]);
        ctx.stroke();
        ctx.setLineDash([]);

        // 2. Draw Connection Beam (Sun to Planet)
        ctx.beginPath();
        ctx.moveTo(CX, CY);
        ctx.lineTo(px, py);
        ctx.strokeStyle = isActive ? p.glow : 'rgba(0, 212, 255, 0.06)';
        ctx.lineWidth = isActive ? 2 : 0.6;
        ctx.stroke();

        // 3. Photon particles along beam if active
        if (isActive && photonMap[p.id]) {
            photonMap[p.id].forEach(particle => {
                particle.update();
                particle.draw(ctx, CX, CY, px, py, p.color);
            });
        }

        // 4. Draw Planet Body
        const currentSize = isActive ? p.size * 1.5 + Math.sin(time * 6) * 2 : p.size;
        
        // Planet Atmosphere Glow
        const glowGrad = ctx.createRadialGradient(px, py, 0, px, py, currentSize * 2.2);
        glowGrad.addColorStop(0, p.glow);
        glowGrad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.beginPath();
        ctx.arc(px, py, currentSize * 2.2, 0, Math.PI * 2);
        ctx.fillStyle = glowGrad;
        ctx.fill();

        // Solid Planet Core
        ctx.beginPath();
        ctx.arc(px, py, currentSize, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.shadowColor = p.color;
        ctx.shadowBlur = isActive ? 15 : 4;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Planet Label & Icon
        ctx.font = isActive ? '700 9px Orbitron, sans-serif' : '500 8px Inter, sans-serif';
        ctx.fillStyle = isActive ? p.color : 'rgba(156, 163, 175, 0.8)';
        ctx.textAlign = 'center';
        ctx.fillText(`${p.icon} ${p.name}`, px, py + currentSize + 12);
        
        // Update Legend Pill UI
        if (p.pill) {
            if (isActive) p.pill.classList.add('active');
            else p.pill.classList.remove('active');
        }
    });

    // Draw Central Sun Core
    drawSun(ctx, CX, CY, time, intensity);

    requestAnimationFrame(renderSolarSystem);
}
renderSolarSystem();

// Get animation intensity based on orb state
function getIntensity() {
    switch (orbState) {
        case 'listening': return 0.6 + Math.sin(Date.now() / 400) * 0.15;
        case 'thinking': return 0.5 + Math.sin(Date.now() / 200) * 0.25;
        case 'speaking': return 0.8 + Math.sin(Date.now() / 300) * 0.2;
        default: return 0.15 + Math.sin(Date.now() / 2000) * 0.05;
    }
}

// Update orb state text & agent telemetry
function setOrbState(state, label, agent = null) {
    orbState = state;
    if (agent) activeAgent = agent;
    
    orbStatusText.textContent = label || state.toUpperCase();
    orbStatusText.className = `orb-status-text state-${state}`;
}

// Infer active agent from user text input heuristic
function inferAgentFromText(text) {
    const t = text.lower ? text.lower() : text.toLowerCase();
    if (t.includes('spotify') || t.includes('music') || t.includes('youtube') || t.includes('pause') || t.includes('play')) {
        return 'MediaAgent';
    }
    if (t.includes('whatsapp') || t.includes('chat') || t.includes('email') || t.includes('gmail') || t.includes('outlook') || t.includes('text')) {
        return 'CommsAgent';
    }
    if (t.includes('cpu') || t.includes('ram') || t.includes('battery') || t.includes('file') || t.includes('folder') || t.includes('volume') || t.includes('brightness') || t.includes('app')) {
        return 'OSAgent';
    }
    if (t.includes('search') || t.includes('image') || t.includes('research') || t.includes('rag') || t.includes('overleaf')) {
        return 'ResearchAgent';
    }
    return null;
}

// ============================================================
//  VOICE TRANSCRIPT
// ============================================================
function addTranscriptLine(sender, text) {
    const placeholder = transcriptContent.querySelector('.transcript-placeholder');
    if (placeholder) placeholder.remove();
    
    const line = document.createElement('div');
    line.className = `transcript-line ${sender}`;
    
    const now = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
    });
    
    const label = sender === 'user' ? 'YOU' : 'WELLSY';
    line.innerHTML = `
        <span class="transcript-time">${now}</span>
        <span class="transcript-sender">${label}</span>
        <span class="transcript-text">${text}</span>
    `;
    
    transcriptContent.appendChild(line);
    transcriptContent.scrollTop = transcriptContent.scrollHeight;
    
    while (transcriptContent.children.length > 50) {
        transcriptContent.removeChild(transcriptContent.firstChild);
    }
}

// ============================================================
//  AMBIENT MIC WAVEFORM
// ============================================================
const micCtx = micCanvas.getContext('2d');

function drawMicWaveform() {
    const w = micCanvas.width;
    const h = micCanvas.height;
    micCtx.clearRect(0, 0, w, h);

    const bars = 24;
    const barW = 2.5;
    const gap = (w - bars * barW) / (bars - 1);
    const time = Date.now() / 300;

    for (let i = 0; i < bars; i++) {
        const x = i * (barW + gap);
        const activeMultiplier = isMicActive ? 3 : 1;
        const barH = 2 + Math.sin(time + i * 0.5) * 2 * activeMultiplier + Math.random() * activeMultiplier;
        const y = (h - barH) / 2;

        if (isMicActive) {
            micCtx.fillStyle = `rgba(0, 212, 255, ${0.5 + Math.sin(time + i) * 0.3})`;
        } else if (isConnected) {
            micCtx.fillStyle = `rgba(59, 139, 255, ${0.2 + Math.sin(time + i) * 0.1})`;
        } else {
            micCtx.fillStyle = 'rgba(156, 163, 175, 0.2)';
        }
        micCtx.fillRect(x, y, barW, barH);
    }

    requestAnimationFrame(drawMicWaveform);
}
drawMicWaveform();

// ============================================================
//  WEBSOCKET CONNECTION
// ============================================================
function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8765/ws');

    ws.onopen = () => {
        isConnected = true;
        statusDot.className = 'status-dot online';
        statusText.textContent = 'Online';
        setOrbState('idle', 'SOLAR SYSTEM ONLINE');
        console.log('Connected to Wellsy backend');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };

    ws.onclose = () => {
        isConnected = false;
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Disconnected';
        setOrbState('idle', 'RECONNECTING...');
        console.log('Disconnected. Retrying in 3s...');
        setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Connection error';
    };
}

// ============================================================
//  MESSAGE HANDLING
// ============================================================
function handleMessage(data) {
    switch (data.type) {
        case 'status':
            updateRateLimits(data.data.rate_limits);
            break;

        case 'thinking':
            showThinking();
            const targetAgent = activeAgent || 'SUPERVISOR';
            setOrbState('thinking', `SUPERVISOR -> ${targetAgent.toUpperCase()}`);
            break;

        case 'response':
            hideThinking();
            addMessage('wellsy', data.data.message, data.data.time);
            addTranscriptLine('wellsy', truncateText(data.data.message, 120));
            updateRateLimits(data.data.rate_limits);
            setOrbState('speaking', 'WELLSY RESPONDING');
            
            // Fade active agent back to neutral after 4s
            setTimeout(() => {
                activeAgent = null;
                if (orbState === 'speaking') setOrbState('idle', 'SUPERVISOR ONLINE');
            }, 4000);

            // Conversational turn-taking
            if (conversationMode) {
                const estimatedSpeechMs = Math.max(3000, (data.data.message.length / 12) * 1000 + 1000);
                setTimeout(() => {
                    if (conversationMode && isConnected) {
                        ws.send(JSON.stringify({ type: 'start_mic' }));
                        setOrbState('listening', 'LISTENING');
                    }
                }, estimatedSpeechMs);
            }
            break;

        case 'error':
            hideThinking();
            addMessage('wellsy', data.data.message);
            setOrbState('idle', 'ERROR HANDLED');
            activeAgent = null;
            if (conversationMode) {
                setTimeout(() => {
                    if (conversationMode && isConnected) {
                        ws.send(JSON.stringify({ type: 'start_mic' }));
                        setOrbState('listening', 'LISTENING');
                    }
                }, 2000);
            }
            break;

        case 'mic_status':
            isMicActive = data.data.active;
            if (isMicActive) {
                micBtn.classList.add('recording');
                statusText.textContent = data.data.info || 'Listening...';
                setOrbState('listening', 'LISTENING');
            } else {
                micBtn.classList.remove('recording');
                if (!conversationMode) {
                    statusText.textContent = 'Online';
                    setOrbState('idle', 'SUPERVISOR ONLINE');
                }
            }
            break;

        case 'speech_transcription':
            if (isMicActive) {
                ws.send(JSON.stringify({ type: 'stop_mic' }));
            }
            addTranscriptLine('user', data.data.message);
            messageInput.value = data.data.message;
            sendMessage();
            break;

        case 'pong':
            updateRateLimits(data.data.rate_limits);
            break;
    }
}

// ============================================================
//  CHAT FUNCTIONS
// ============================================================
function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !isConnected || isThinking) return;

    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }

    // Infer sub-agent targeting for immediate visual beam activation
    activeAgent = inferAgentFromText(text);

    addMessage('user', text);
    addTranscriptLine('user', truncateText(text, 120));

    ws.send(JSON.stringify({
        type: 'chat',
        message: text,
    }));

    messageInput.value = '';
    isThinking = true;
}

function addMessage(sender, text, time = null) {
    const now = time || new Date().toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', hour12: false,
    });

    messageCount++;
    const isUser = sender === 'user';

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;

    const waveBars = createWaveform();

    msgDiv.innerHTML = `
        <div class="message-header">
            <div class="msg-dot"></div>
            <span>${isUser ? 'You' : 'Wellsy'}</span>
            ${waveBars}
        </div>
        <div class="message-bubble">${formatMessage(text)}</div>
        <span class="message-time">${now}</span>
    `;

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    setTimeout(() => {
        const waveContainer = msgDiv.querySelector('.waveform-container');
        if (waveContainer) {
            const bars = waveContainer.querySelectorAll('.wave-bar');
            bars.forEach(bar => {
                bar.style.animation = 'none';
                bar.style.height = `${3 + Math.random() * 6}px`;
            });
        }
    }, 2500);
}

function createWaveform() {
    const bars = 14;
    let html = '<div class="waveform-container">';
    for (let i = 0; i < bars; i++) {
        const delay = (i * 0.06).toFixed(2);
        const h = 3 + Math.random() * 12;
        html += `<div class="wave-bar" style="animation-delay:${delay}s; height:${h}px"></div>`;
    }
    html += '</div>';
    return html;
}

function formatMessage(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

function truncateText(text, maxLen) {
    const clean = text.replace(/\n/g, ' ').replace(/\s+/g, ' ').trim();
    return clean.length > maxLen ? clean.substring(0, maxLen) + '...' : clean;
}

// ============================================================
//  THINKING INDICATOR
// ============================================================
let thinkingEl = null;

function showThinking() {
    isThinking = true;
    thinkingEl = document.createElement('div');
    thinkingEl.className = 'status-message';
    thinkingEl.id = 'thinkingIndicator';
    thinkingEl.innerHTML = `
        <div class="thinking-dots">
            <span></span><span></span><span></span>
        </div>
        <span>Supervisor orchestrating agents...</span>
    `;
    chatContainer.appendChild(thinkingEl);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideThinking() {
    isThinking = false;
    const el = document.getElementById('thinkingIndicator');
    if (el) el.remove();
}

// ============================================================
//  RATE LIMITS
// ============================================================
function updateRateLimits(limits) {
    if (!limits) return;
    const pct = limits.budget_percent || 0;
    rateBarFill.style.width = `${pct}%`;
    rateBarText.textContent = `API: ${limits.daily_used} / ${limits.daily_limit}`;
    if (pct > 75) {
        rateBarFill.classList.add('warning');
    } else {
        rateBarFill.classList.remove('warning');
    }
}

// ============================================================
//  EVENT LISTENERS
// ============================================================
sendBtn.addEventListener('click', sendMessage);

micBtn.addEventListener('click', () => {
    if (!isConnected) return;
    
    if (conversationMode) {
        conversationMode = false;
        ws.send(JSON.stringify({ type: 'stop_mic' }));
        micBtn.classList.remove('conversation-active');
        statusText.textContent = 'Online';
        setOrbState('idle', 'SUPERVISOR ONLINE');
        activeAgent = null;
    } else {
        conversationMode = true;
        ws.send(JSON.stringify({ type: 'start_mic' }));
        micBtn.classList.add('conversation-active');
        statusText.textContent = 'Conversation active';
        setOrbState('listening', 'LISTENING');
    }
});

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

stopBtn.addEventListener('click', () => {
    hideThinking();
    isThinking = false;
    conversationMode = false;
    activeAgent = null;
    addMessage('wellsy', 'Standing by, Moksh.');
    if (isMicActive) {
        ws.send(JSON.stringify({ type: 'stop_mic' }));
    }
    micBtn.classList.remove('conversation-active');
    statusText.textContent = 'Online';
    setOrbState('idle', 'SUPERVISOR ONLINE');
});

// Window controls
document.getElementById('btnMinimize')?.addEventListener('click', () => {
    window.electronAPI?.minimize();
});
document.getElementById('btnMaximize')?.addEventListener('click', () => {
    window.electronAPI?.maximize();
});
document.getElementById('btnClose')?.addEventListener('click', () => {
    window.electronAPI?.close();
});

// Ping every 30s
setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
    }
}, 30000);

// === START ===
connectWebSocket();
