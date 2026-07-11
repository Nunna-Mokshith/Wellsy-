/**
 * Wellsy Frontend — Renderer
 * Handles WebSocket connection, chat UI, waveforms, and dynamic effects.
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

// === State ===
let ws = null;
let isConnected = false;
let isThinking = false;
let isMicActive = false;
let messageCount = 0;

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

// === Ambient Mic Waveform (idle animation) ===
const micCtx = micCanvas.getContext('2d');
let micAnimFrame = null;

function drawMicWaveform() {
    const w = micCanvas.width;
    const h = micCanvas.height;
    micCtx.clearRect(0, 0, w, h);

    const bars = 20;
    const barW = 3;
    const gap = (w - bars * barW) / (bars - 1);
    const time = Date.now() / 300;

    for (let i = 0; i < bars; i++) {
        const x = i * (barW + gap);
        const barH = 3 + Math.sin(time + i * 0.5) * 3 + Math.random() * 2;
        const y = (h - barH) / 2;

        micCtx.fillStyle = isConnected
            ? `rgba(59, 139, 255, ${0.3 + Math.sin(time + i) * 0.2})`
            : 'rgba(85, 85, 106, 0.3)';
        micCtx.fillRect(x, y, barW, barH);
    }

    micAnimFrame = requestAnimationFrame(drawMicWaveform);
}
drawMicWaveform();

// === WebSocket Connection ===
function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8765/ws');

    ws.onopen = () => {
        isConnected = true;
        statusDot.className = 'status-dot online';
        statusText.textContent = 'Online';
        console.log('🟢 Connected to Wellsy backend');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };

    ws.onclose = () => {
        isConnected = false;
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Disconnected';
        console.log('🔴 Disconnected. Retrying in 3s...');
        setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Connection error';
    };
}

// === Handle Incoming Messages ===
function handleMessage(data) {
    switch (data.type) {
        case 'status':
            updateRateLimits(data.data.rate_limits);
            break;

        case 'thinking':
            showThinking();
            break;

        case 'response':
            hideThinking();
            addMessage('wellsy', data.data.message, data.data.time);
            updateRateLimits(data.data.rate_limits);
            break;

        case 'error':
            hideThinking();
            addMessage('wellsy', `⚠️ ${data.data.message}`);
            break;

        case 'mic_status':
            isMicActive = data.data.active;
            if (isMicActive) {
                micBtn.classList.add('recording');
                micBtn.textContent = '🛑';
                statusText.textContent = data.data.info || 'Listening...';
            } else {
                micBtn.classList.remove('recording');
                micBtn.textContent = '🎙️';
                statusText.textContent = 'Online';
            }
            break;

        case 'speech_transcription':
            // Speech detected and transcribed by backend!
            // Put it into the input and trigger sendMessage
            messageInput.value = data.data.message;
            sendMessage();
            break;

        case 'pong':
            updateRateLimits(data.data.rate_limits);
            break;
    }
}

// === Send Message ===
function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !isConnected || isThinking) return;

    // Hide welcome on first message
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }

    // Add user message to chat
    addMessage('user', text);

    // Send to backend
    ws.send(JSON.stringify({
        type: 'chat',
        message: text,
    }));

    messageInput.value = '';
    isThinking = true;
}

// === Add Message to Chat ===
function addMessage(sender, text, time = null) {
    const now = time || new Date().toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', hour12: false,
    });

    messageCount++;
    const isUser = sender === 'user';

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;

    // Create waveform bars
    const waveBars = createWaveform(isUser ? 'red' : 'blue');

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

    // Stop waveform animation after a moment
    setTimeout(() => {
        const waveContainer = msgDiv.querySelector('.waveform-container');
        if (waveContainer) {
            const bars = waveContainer.querySelectorAll('.wave-bar');
            bars.forEach(bar => {
                bar.style.animation = 'none';
                bar.style.height = `${4 + Math.random() * 8}px`;
            });
        }
    }, 2000);
}

// === Create Waveform Bars ===
function createWaveform(color) {
    const bars = 12;
    let html = '<div class="waveform-container">';
    for (let i = 0; i < bars; i++) {
        const delay = (i * 0.08).toFixed(2);
        const h = 4 + Math.random() * 14;
        html += `<div class="wave-bar" style="animation-delay:${delay}s; height:${h}px"></div>`;
    }
    html += '</div>';
    return html;
}

// === Format Message Text ===
function formatMessage(text) {
    // Basic markdown-like formatting
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code style="background:rgba(255,255,255,0.08);padding:1px 5px;border-radius:4px;font-size:12px">$1</code>')
        .replace(/\n/g, '<br>');
}

// === Thinking Indicator ===
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
        <span>Wellsy is thinking...</span>
    `;
    chatContainer.appendChild(thinkingEl);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideThinking() {
    isThinking = false;
    const el = document.getElementById('thinkingIndicator');
    if (el) el.remove();
}

// === Rate Limit Display ===
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

// === Event Listeners ===
sendBtn.addEventListener('click', sendMessage);

micBtn.addEventListener('click', () => {
    if (!isConnected) return;
    
    if (isMicActive) {
        // Stop listing
        ws.send(JSON.stringify({ type: 'stop_mic' }));
    } else {
        // Start listening
        ws.send(JSON.stringify({ type: 'start_mic' }));
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
    addMessage('wellsy', 'Stopped! What do you need?');
    // If recording, turn it off
    if (isMicActive) {
        ws.send(JSON.stringify({ type: 'stop_mic' }));
    }
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

// === Ping server every 30s to keep connection alive and update rate limits ===
setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
    }
}, 30000);

// === Start ===
connectWebSocket();
