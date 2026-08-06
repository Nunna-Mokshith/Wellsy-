// Live Clock
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
    const dateOptions = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    const dateString = now.toLocaleDateString('en-US', dateOptions);
    
    const clockEl = document.getElementById('liveClock');
    if (clockEl) clockEl.textContent = timeString;
    
    const dateEl = document.getElementById('dateText');
    if (dateEl) dateEl.textContent = dateString;
}
setInterval(updateClock, 1000);
updateClock();

// AI Core Sphere
const coreCanvas = document.getElementById('coreCanvas');
let coreCtx;
if (coreCanvas) {
    coreCtx = coreCanvas.getContext('2d');
    coreCanvas.width = 350;
    coreCanvas.height = 350;
}

let orbState = 'idle';
let orbAngle = 0;
const particles = Array.from({length: 40}).map(() => ({
    angle: Math.random() * Math.PI * 2,
    radius: 60 + Math.random() * 80,
    speed: 0.005 + Math.random() * 0.015,
    size: Math.random() * 2,
    alpha: Math.random()
}));

function drawCore() {
    if (!coreCtx || !coreCanvas) return;
    const ctx = coreCtx;
    const w = coreCanvas.width;
    const h = coreCanvas.height;
    const cx = w / 2;
    const cy = h / 2;
    
    ctx.clearRect(0, 0, w, h);
    
    const isActive = orbState === 'active';
    const speedMultiplier = isActive ? 3 : 1;
    const glowMultiplier = isActive ? 1.5 : 1;
    
    orbAngle += 0.01 * speedMultiplier;
    
    const pulse = 1 + 0.05 * Math.sin(Date.now() / (isActive ? 200 : 500));
    
    // Outer ring
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(orbAngle);
    ctx.scale(pulse, pulse);
    ctx.beginPath();
    ctx.arc(0, 0, 140, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(0, 229, 255, ${0.3 * glowMultiplier})`;
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 15]);
    ctx.stroke();
    ctx.restore();
    
    // Middle ring
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(-orbAngle * 1.5);
    ctx.scale(pulse, pulse);
    ctx.beginPath();
    ctx.arc(0, 0, 100, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(0, 229, 255, ${0.5 * glowMultiplier})`;
    ctx.lineWidth = 2;
    ctx.setLineDash([]);
    ctx.stroke();
    ctx.restore();
    
    // Inner ring
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(orbAngle * 2);
    ctx.scale(pulse, pulse);
    ctx.beginPath();
    ctx.arc(0, 0, 60, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(0, 229, 255, ${0.7 * glowMultiplier})`;
    ctx.lineWidth = 3;
    ctx.stroke();
    ctx.restore();
    
    // Core
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(pulse, pulse);
    const grad = ctx.createRadialGradient(0, 0, 0, 0, 0, 30);
    grad.addColorStop(0, `rgba(0, 255, 255, ${1 * glowMultiplier})`);
    grad.addColorStop(1, `rgba(0, 255, 255, 0)`);
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(0, 0, 30, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    
    // Particles
    particles.forEach(p => {
        p.angle += p.speed * speedMultiplier;
        p.alpha += (Math.random() - 0.5) * 0.1;
        if (p.alpha < 0) p.alpha = 0;
        if (p.alpha > 1) p.alpha = 1;
        
        const px = cx + Math.cos(p.angle) * p.radius;
        const py = cy + Math.sin(p.angle) * p.radius;
        
        ctx.fillStyle = `rgba(0, 229, 255, ${p.alpha * glowMultiplier})`;
        ctx.beginPath();
        ctx.arc(px, py, p.size, 0, Math.PI * 2);
        ctx.fill();
    });
    
    // Text overlays
    ctx.fillStyle = `rgba(0, 229, 255, ${0.9 * glowMultiplier})`;
    ctx.textAlign = 'center';
    
    ctx.font = 'bold 14px Orbitron, sans-serif';
    ctx.fillText('WELLSY', cx, cy - 20);
    
    ctx.font = '10px Orbitron, sans-serif';
    ctx.fillText('AI CORE', cx, cy + 5);
    
    ctx.fillStyle = `rgba(0, 229, 255, ${0.4 * glowMultiplier})`;
    ctx.font = '8px Inter, sans-serif';
    ctx.fillText('v2.0.0', cx, cy + 20);
    
    requestAnimationFrame(drawCore);
}
requestAnimationFrame(drawCore);

// System Gauges
const gaugeCanvas = document.getElementById('gaugeCanvas');
let gaugeCtx;
if (gaugeCanvas) {
    gaugeCtx = gaugeCanvas.getContext('2d');
    gaugeCanvas.width = 300;
    gaugeCanvas.height = 120;
}

let gaugeData = { cpu: 0, ram: 0, disk: 0 };

function drawGauges() {
    if (!gaugeCtx || !gaugeCanvas) return;
    const ctx = gaugeCtx;
    const w = gaugeCanvas.width;
    const h = gaugeCanvas.height;
    ctx.clearRect(0, 0, w, h);
    
    const startAngle = 135 * Math.PI / 180;
    const endAngle = 405 * Math.PI / 180;
    const sweep = endAngle - startAngle;
    
    function drawGauge(x, y, radius, value, color, label) {
        // Background arc
        ctx.beginPath();
        ctx.arc(x, y, radius, startAngle, endAngle);
        ctx.strokeStyle = '#333333';
        ctx.lineWidth = 10;
        ctx.lineCap = 'round';
        ctx.stroke();
        
        // Value arc
        const valAngle = startAngle + sweep * (value / 100);
        ctx.beginPath();
        ctx.arc(x, y, radius, startAngle, valAngle);
        ctx.strokeStyle = color;
        ctx.lineWidth = 10;
        ctx.lineCap = 'round';
        ctx.stroke();
        
        // Center text
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 16px Orbitron, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(Math.round(value) + '%', x, y);
        
        // Label
        ctx.fillStyle = '#aaaaaa';
        ctx.font = '10px Inter, sans-serif';
        ctx.fillText(label, x, y + radius + 15);
    }
    
    const r = 35;
    const y = 50;
    drawGauge(50, y, r, gaugeData.cpu, '#00d4ff', 'CPU');
    drawGauge(150, y, r, gaugeData.ram, '#00ff88', 'RAM');
    drawGauge(250, y, r, gaugeData.disk, '#bb00ff', 'DISK');
}

async function fetchSystemStats() {
    try {
        const res = await fetch('/api/system');
        const data = await res.json();
        updateGauges(data);
        const cpuV = document.getElementById('cpuValue');
        const ramV = document.getElementById('ramValue');
        const diskV = document.getElementById('diskValue');
        if (cpuV) cpuV.textContent = Math.round(data.cpu) + '%';
        if (ramV) ramV.textContent = Math.round(data.ram) + '%';
        if (diskV) diskV.textContent = Math.round(data.disk) + '%';
    } catch(e) {
        // Fallback or ignore
    }
}
function updateGauges(data) {
    gaugeData = data;
    drawGauges();
}
setInterval(fetchSystemStats, 3000);
fetchSystemStats();

// WebSocket Connection
let ws = null;
let reconnectDelay = 1000;
let maxReconnectDelay = 30000;
let activeAgent = null;

let sessionTurns = 0;
let toolCalls = 0;

function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8765/ws');
    
    ws.onopen = () => {
        const dot = document.getElementById('statusDot');
        const txt = document.getElementById('statusText');
        if (dot) { dot.style.backgroundColor = '#00ff88'; dot.style.boxShadow = '0 0 10px #00ff88'; }
        if (txt) txt.textContent = 'Connected';
        reconnectDelay = 1000;
    };
    
    ws.onclose = () => {
        const dot = document.getElementById('statusDot');
        const txt = document.getElementById('statusText');
        if (dot) { dot.style.backgroundColor = '#ff3333'; dot.style.boxShadow = '0 0 10px #ff3333'; }
        if (txt) txt.textContent = 'Disconnected';
        
        setTimeout(connectWebSocket, reconnectDelay);
        reconnectDelay = Math.min(reconnectDelay * 2, maxReconnectDelay);
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleWsMessage(data);
        } catch(e) {
            console.error('WS Parse Error:', e);
        }
    };
}

function handleWsMessage(msg) {
    if (msg.type === 'response') {
        appendMessage('ai', msg.text, msg.agent);
        hideThinking();
    } else if (msg.type === 'thinking') {
        showThinking();
    } else if (msg.type === 'agent_active') {
        activateAgent(msg.agent);
        addIntelItem({text: `${msg.agent} activated`, type: 'INFO', time: new Date().toLocaleTimeString()});
        toolCalls++;
        updateMemoryStats();
    } else if (msg.type === 'agent_done') {
        deactivateAgent(msg.agent);
    } else if (msg.type === 'transcript') {
        appendMessage('user', msg.text);
    } else if (msg.type === 'audio') {
        playAudio(msg.data);
    } else if (msg.type === 'intelligence') {
        addIntelItem(msg.item);
    } else if (msg.type === 'rate_limit') {
        // Optional handling for rate limit
    } else if (msg.type === 'confirmation_request') {
        showConfirmationModal(msg.preview);
    }
}

// Confirmation Gate Modal Manager
let currentConfirmationId = null;

function showConfirmationModal(preview) {
    currentConfirmationId = preview.request_id;
    const modal = document.getElementById('confirmModal');
    const badge = document.getElementById('modalBadge');
    const title = document.getElementById('modalTitle');
    const summary = document.getElementById('modalSummary');
    const details = document.getElementById('modalDetails');
    const approveBtn = document.getElementById('modalApproveBtn');
    const rejectBtn = document.getElementById('modalRejectBtn');

    if (!modal) return;

    if (badge) {
        badge.textContent = `${preview.tier} ACTION`;
        badge.className = `modal-badge ${preview.tier.toLowerCase().replace('_', '-')}`;
    }
    if (summary) summary.textContent = preview.summary;

    if (details) {
        details.innerHTML = '';
        if (preview.details && preview.details.length > 0) {
            preview.details.forEach(d => {
                const item = document.createElement('div');
                item.textContent = `• ${d}`;
                details.appendChild(item);
            });
        } else {
            details.textContent = `Action: ${preview.tool_name}`;
        }
    }

    modal.classList.remove('hidden');

    // Click handlers
    if (approveBtn) {
        approveBtn.onclick = () => respondConfirmation(true);
    }
    if (rejectBtn) {
        rejectBtn.onclick = () => respondConfirmation(false);
    }
}

function respondConfirmation(approved) {
    const modal = document.getElementById('confirmModal');
    if (modal) modal.classList.add('hidden');

    if (ws && currentConfirmationId) {
        ws.send(JSON.stringify({
            type: 'confirmation_response',
            request_id: currentConfirmationId,
            approved: approved
        }));
        addIntelItem({
            text: `Action #${currentConfirmationId} ${approved ? 'APPROVED' : 'REJECTED'} by user`,
            type: approved ? 'TIP' : 'WARN',
            time: new Date().toLocaleTimeString()
        });
    }
    currentConfirmationId = null;
}


connectWebSocket();

// Chat Interface
function appendMessage(sender, text, agent = '') {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;
    
    const msgDiv = document.createElement('div');
    msgDiv.className = \`msg-\${sender}\`;
    msgDiv.style.margin = '10px 0';
    msgDiv.style.padding = '10px';
    msgDiv.style.borderRadius = '5px';
    msgDiv.style.maxWidth = '80%';
    msgDiv.style.clear = 'both';
    
    if (sender === 'user') {
        msgDiv.style.float = 'right';
        msgDiv.style.backgroundColor = '#00d4ff22';
        msgDiv.style.border = '1px solid #00d4ff55';
    } else {
        msgDiv.style.float = 'left';
        msgDiv.style.backgroundColor = '#222222';
        msgDiv.style.border = '1px solid #444444';
        
        if (agent) {
            const agentTag = document.createElement('div');
            agentTag.textContent = agent;
            agentTag.style.fontSize = '10px';
            agentTag.style.color = '#00d4ff';
            agentTag.style.marginBottom = '5px';
            msgDiv.appendChild(agentTag);
        }
    }
    
    const textSpan = document.createElement('span');
    textSpan.textContent = text;
    textSpan.style.color = '#ffffff';
    textSpan.style.fontFamily = 'Inter, sans-serif';
    
    msgDiv.appendChild(textSpan);
    chatContainer.appendChild(msgDiv);
    
    const clearDiv = document.createElement('div');
    clearDiv.style.clear = 'both';
    chatContainer.appendChild(clearDiv);
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showThinking() {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;
    const thinkingDiv = document.createElement('div');
    thinkingDiv.id = 'thinkingIndicator';
    thinkingDiv.textContent = 'Thinking...';
    thinkingDiv.style.color = '#00d4ff';
    thinkingDiv.style.padding = '10px';
    thinkingDiv.style.fontFamily = 'Inter, sans-serif';
    chatContainer.appendChild(thinkingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Animate dots
    let dots = 0;
    thinkingDiv.dataset.interval = setInterval(() => {
        dots = (dots + 1) % 4;
        thinkingDiv.textContent = 'Thinking' + '.'.repeat(dots);
    }, 500);
}

function hideThinking() {
    const indicator = document.getElementById('thinkingIndicator');
    if (indicator) {
        clearInterval(indicator.dataset.interval);
        indicator.remove();
    }
}

function sendChatMessage(text) {
    if (!text || !text.trim() || !ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: 'chat', text: text }));
    appendMessage('user', text);
    const input = document.getElementById('chatInput');
    if (input) input.value = '';
    sessionTurns++;
    updateMemoryStats();
}

const sendBtn = document.getElementById('sendBtn');
const chatInput = document.getElementById('chatInput');
if (sendBtn) {
    sendBtn.addEventListener('click', () => {
        if (chatInput) sendChatMessage(chatInput.value);
    });
}
if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage(chatInput.value);
        }
    });
}

const stopBtn = document.getElementById('stopBtn');
if (stopBtn) {
    stopBtn.addEventListener('click', () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'stop' }));
        }
    });
}

// Voice / Mic
let isListening = false;
function toggleVoice() {
    isListening = !isListening;
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'voice_toggle' }));
    }
    
    const talkBtn = document.getElementById('talkBtn');
    if (talkBtn) {
        if (isListening) {
            talkBtn.textContent = 'I am listening...';
            talkBtn.classList.add('pulsing');
        } else {
            talkBtn.textContent = 'TALK';
            talkBtn.classList.remove('pulsing');
        }
    }
}

const talkBtn = document.getElementById('talkBtn');
if (talkBtn) talkBtn.addEventListener('click', toggleVoice);

const micBtn = document.getElementById('micBtn');
if (micBtn) micBtn.addEventListener('click', toggleVoice);

const sidebarMicBtn = document.getElementById('sidebarMicBtn');
if (sidebarMicBtn) sidebarMicBtn.addEventListener('click', toggleVoice);

// Intelligence Feed
function addIntelItem(item) {
    const intelList = document.getElementById('intelList');
    if (!intelList) return;
    
    const li = document.createElement('li');
    li.style.padding = '8px';
    li.style.borderBottom = '1px solid #333';
    li.style.fontSize = '12px';
    li.style.color = '#ddd';
    li.style.fontFamily = 'Inter, sans-serif';
    
    const timeSpan = document.createElement('span');
    timeSpan.textContent = \`[\${item.time || new Date().toLocaleTimeString()}] \`;
    timeSpan.style.color = '#888';
    
    const typeSpan = document.createElement('span');
    typeSpan.textContent = \`\${item.type || 'INFO'} \`;
    typeSpan.style.fontWeight = 'bold';
    
    if (item.type === 'WARN') typeSpan.style.color = '#ffaa00';
    else if (item.type === 'TIP') typeSpan.style.color = '#00ff88';
    else typeSpan.style.color = '#00d4ff';
    
    const textSpan = document.createElement('span');
    textSpan.textContent = item.text;
    
    li.appendChild(timeSpan);
    li.appendChild(typeSpan);
    li.appendChild(textSpan);
    
    intelList.insertBefore(li, intelList.firstChild);
    
    if (intelList.children.length > 20) {
        intelList.removeChild(intelList.lastChild);
    }
}

// Agent Status Updates
function activateAgent(agentId) {
    activeAgent = agentId;
    orbState = 'active';
    
    const card = document.getElementById(\`agentCard-\${agentId}\`);
    if (card) {
        card.classList.add('agent-active');
        const badge = card.querySelector('.status-badge');
        if (badge) {
            badge.textContent = 'Active';
            badge.style.color = '#00ff88';
        }
    }
}

function deactivateAgent(agentId) {
    if (activeAgent === agentId) {
        activeAgent = null;
        orbState = 'idle';
    }
    
    const card = document.getElementById(\`agentCard-\${agentId}\`);
    if (card) {
        card.classList.remove('agent-active');
        const badge = card.querySelector('.status-badge');
        if (badge) {
            badge.textContent = 'Standby';
            badge.style.color = '#888888';
        }
    }
}

// Sidebar Navigation
const navItems = document.querySelectorAll('.nav-item');
navItems.forEach(item => {
    item.addEventListener('click', () => {
        navItems.forEach(ni => ni.classList.remove('active'));
        item.classList.add('active');
    });
});

// Quick Commands
const cmdNewTask = document.getElementById('cmdNewTask');
if (cmdNewTask) {
    cmdNewTask.addEventListener('click', () => {
        if (chatInput) {
            chatInput.value = 'Schedule a task: ';
            chatInput.focus();
        }
    });
}

const cmdVoiceChat = document.getElementById('cmdVoiceChat');
if (cmdVoiceChat) {
    cmdVoiceChat.addEventListener('click', toggleVoice);
}

const cmdCalendar = document.getElementById('cmdCalendar');
if (cmdCalendar) {
    cmdCalendar.addEventListener('click', () => {
        sendChatMessage('Show my schedule for today');
    });
}

const cmdWorkflow = document.getElementById('cmdWorkflow');
if (cmdWorkflow) {
    cmdWorkflow.addEventListener('click', () => {
        sendChatMessage('What workflows are available?');
    });
}

// Audio Playback
function playAudio(base64Data) {
    try {
        const audio = new Audio('data:audio/mp3;base64,' + base64Data);
        audio.play().catch(e => console.error('Audio play error:', e));
    } catch(e) {
        console.error('Audio setup error:', e);
    }
}

// Memory Stats
function updateMemoryStats() {
    const turns = document.getElementById('sessionTurns');
    const tools = document.getElementById('toolCalls');
    
    if (turns) turns.textContent = sessionTurns;
    if (tools) tools.textContent = toolCalls;
}

// Responsive Handling
window.addEventListener('resize', () => {
    // Basic handler for resize, canvases handle their own internal bounds in the rendering loop
});

// CSS for pulse effect
const style = document.createElement('style');
style.textContent = \`
    .pulsing {
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
\`;
document.head.appendChild(style);
