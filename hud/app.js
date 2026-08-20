// KAIROS OS - Front-End Orchestrator

let socket = null;
let isRecording = false;
let spacePressed = false;

// DOM Elements
const statusLabel = document.getElementById('status-label');
const statusDesc = document.getElementById('status-desc');
const recordBtn = document.getElementById('record-btn');
const btnIcon = document.getElementById('btn-icon');
const btnText = document.getElementById('btn-text');
const coreNode = document.getElementById('core-node');
const coreIcon = document.getElementById('core-icon');
const connectionStatus = document.getElementById('connection-status');
const terminalLog = document.getElementById('terminal-log');
const terminalInput = document.getElementById('terminal-input');
const sendBtn = document.getElementById('send-btn');
const currentTimeEl = document.getElementById('current-time');
const dailyPlanContainer = document.getElementById('daily-plan-container');
const inboxSummaryContainer = document.getElementById('inbox-summary-container');
const footerMicStatus = document.getElementById('footer-mic-status');

// Metrics elements
const metricCpu = document.getElementById('metric-cpu');
const metricRam = document.getElementById('metric-ram');
const metricLatency = document.getElementById('metric-latency');

// Core states configuration
const STATES = {
    idle: {
        label: "MODO REPOSO",
        desc: "Esperando comando...",
        colorClass: "text-cyan-400",
        shadowClass: "shadow-[0_0_20px_rgba(6,182,212,0.4)]",
        borderClass: "border-cyan-400",
        coreBg: "bg-slate-900",
        btnText: "Iniciar Grabación",
        btnColor: "bg-cyan-500/10",
        btnTextCol: "text-cyan-300",
        btnBorder: "border-cyan-500/30"
    },
    listening: {
        label: "ESCUCHANDO...",
        desc: "Escuchando entrada de voz local",
        colorClass: "text-rose-400",
        shadowClass: "shadow-[0_0_30px_rgba(244,63,94,0.6)]",
        borderClass: "border-rose-400",
        coreBg: "bg-rose-950/20",
        btnText: "Grabando... Suelta para enviar",
        btnColor: "bg-rose-500/20",
        btnTextCol: "text-rose-300",
        btnBorder: "border-rose-500/60"
    },
    thinking: {
        label: "PROCESANDO...",
        desc: "Gemini está orquestando tareas",
        colorClass: "text-amber-400",
        shadowClass: "shadow-[0_0_30px_rgba(245,158,11,0.6)]",
        borderClass: "border-amber-400",
        coreBg: "bg-amber-950/20",
        btnText: "Pensando...",
        btnColor: "bg-amber-500/10",
        btnTextCol: "text-amber-300",
        btnBorder: "border-amber-500/30"
    },
    speaking: {
        label: "HABLANDO",
        desc: "Reproduciendo respuesta de voz",
        colorClass: "text-emerald-400",
        shadowClass: "shadow-[0_0_30px_rgba(16,185,129,0.6)]",
        borderClass: "border-emerald-400",
        coreBg: "bg-emerald-950/20",
        btnText: "Asistente hablando...",
        btnColor: "bg-emerald-500/10",
        btnTextCol: "text-emerald-300",
        btnBorder: "border-emerald-500/30"
    }
};

// Current operating state
let currentState = "idle";

// 1. Clock Initialization
function updateClock() {
    const now = new Date();
    currentTimeEl.textContent = now.toLocaleTimeString('es-ES');
}
setInterval(updateClock, 1000);
updateClock();

// 2. Terminal Log Helper
function logToTerminal(sender, message, type = 'system') {
    const logDiv = document.createElement('div');
    const timestamp = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    let colorClass = 'text-slate-400';
    if (sender === 'KAIROS-LOG') colorClass = 'text-cyan-400 font-semibold';
    else if (sender === 'USER-TRANSCRIPT') colorClass = 'text-blue-300';
    else if (sender === 'SYSTEM') colorClass = 'text-slate-500';
    else if (sender === 'ERROR') colorClass = 'text-rose-400 font-bold';
    else if (sender === 'SKILL-EXEC') colorClass = 'text-purple-400';
    
    logDiv.className = colorClass;
    logDiv.innerHTML = `[${timestamp}] [${sender}] ${message}`;
    terminalLog.appendChild(logDiv);
    
    // Auto Scroll to bottom
    terminalLog.scrollTop = terminalLog.scrollHeight;
}

// 3. WebSocket Connection
function connectWebSocket() {
    const wsUrl = `ws://${window.location.host}/ws`;
    logToTerminal('SYSTEM', `Estableciendo conexión en ${wsUrl}...`);
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
        connectionStatus.innerHTML = `
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            CONECTADO
        `;
        connectionStatus.className = "px-2 py-0.5 rounded text-[10px] font-bold border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 flex items-center gap-1.5";
        logToTerminal('SYSTEM', 'Conexión WebSocket establecida con éxito.');
    };
    
    socket.onclose = () => {
        connectionStatus.innerHTML = `
            <span class="w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse"></span>
            DESCONECTADO
        `;
        connectionStatus.className = "px-2 py-0.5 rounded text-[10px] font-bold border border-rose-500/30 bg-rose-500/10 text-rose-400 flex items-center gap-1.5";
        logToTerminal('SYSTEM', 'Conexión WebSocket cerrada. Intentando reconectar en 3 segundos...', 'error');
        setTimeout(connectWebSocket, 3000);
        updateState('idle');
    };
    
    socket.onerror = (error) => {
        logToTerminal('ERROR', `Fallo de WebSocket: ${error.message || 'Error desconocido'}`);
    };
    
    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleServerMessage(data);
        } catch (err) {
            logToTerminal('ERROR', `Error parseando mensaje WebSocket: ${err.message}`);
        }
    };
}

// 4. Handle Incoming Messages from Server
function handleServerMessage(data) {
    switch (data.type) {
        case 'status':
            updateState(data.state, data.description);
            break;
        case 'log':
            logToTerminal(data.sender || 'KAIROS-LOG', data.message);
            break;
        case 'plan':
            renderDailyPlan(data.content);
            break;
        case 'inbox':
            renderInbox(data.content);
            break;
        case 'metrics':
            updateMetrics(data.cpu, data.ram, data.latency);
            break;
        default:
            logToTerminal('SYSTEM', `Tipo de mensaje no controlado: ${data.type}`);
    }
}

// 5. Update UI States (idle, listening, thinking, speaking)
function updateState(state, customDesc = null) {
    if (!STATES[state]) return;
    currentState = state;
    const config = STATES[state];
    
    // Update labels and descriptions
    statusLabel.textContent = config.label;
    statusLabel.className = `font-orbitron font-bold text-xl ${config.colorClass} tracking-wider transition-all duration-300`;
    statusDesc.textContent = customDesc || config.desc;
    
    // Core visual node classes
    coreNode.className = `relative w-28 h-28 rounded-full transition-all duration-300 flex items-center justify-center z-20 ${config.coreBg} border ${config.borderClass} ${config.shadowClass}`;
    
    // Core Icons representing state
    if (state === 'listening') {
        coreIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>';
        coreIcon.className = "w-8 h-8 text-rose-400 animate-pulse";
        footerMicStatus.textContent = "ACTIVE";
        footerMicStatus.className = "text-rose-400 font-bold";
    } else if (state === 'thinking') {
        coreIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>';
        coreIcon.className = "w-8 h-8 text-amber-400 animate-spin-slow";
        footerMicStatus.textContent = "MUTED";
        footerMicStatus.className = "text-slate-500 font-bold";
    } else if (state === 'speaking') {
        coreIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path>';
        coreIcon.className = "w-8 h-8 text-emerald-400 animate-bounce";
        footerMicStatus.textContent = "MUTED";
        footerMicStatus.className = "text-slate-500 font-bold";
    } else { // idle
        coreIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>';
        coreIcon.className = "w-8 h-8 text-cyan-400";
        footerMicStatus.textContent = "MUTED";
        footerMicStatus.className = "text-slate-500 font-bold";
    }
    
    // Update PTT Button styles
    btnText.textContent = config.btnText;
    btnText.className = `relative ${config.btnTextCol} font-orbitron`;
    recordBtn.className = `w-full py-4 px-6 rounded-xl font-bold uppercase tracking-wider transition-all duration-300 flex items-center justify-center gap-3 border shadow-md relative overflow-hidden select-none cursor-pointer ${config.btnColor} ${config.btnBorder}`;
    
    if (state === 'listening') {
        btnIcon.className = "relative w-4 h-4 rounded-full bg-rose-500 animate-ping";
        recordBtn.classList.add('recording');
    } else {
        btnIcon.className = `relative w-4 h-4 rounded-full ${state === 'idle' ? 'bg-cyan-400 animate-pulse' : state === 'thinking' ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400 animate-pulse'}`;
        recordBtn.classList.remove('recording');
    }
}

// 6. Push-to-Talk Recording Trigger Handler
function startVoiceCapture() {
    if (currentState !== 'idle' || isRecording) return;
    isRecording = true;
    updateState('listening');
    
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ action: 'start_recording' }));
    }
}

function stopVoiceCapture() {
    if (!isRecording) return;
    isRecording = false;
    updateState('thinking');
    
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ action: 'stop_recording' }));
    }
}

// Event Listeners for Record Button
recordBtn.addEventListener('mousedown', (e) => {
    e.preventDefault();
    startVoiceCapture();
});

window.addEventListener('mouseup', (e) => {
    if (isRecording) {
        stopVoiceCapture();
    }
});

// Touch Devices Support
recordBtn.addEventListener('touchstart', (e) => {
    e.preventDefault();
    startVoiceCapture();
});

recordBtn.addEventListener('touchend', (e) => {
    e.preventDefault();
    stopVoiceCapture();
});

// Spacebar Key Support (Push-to-Talk)
window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !spacePressed) {
        // Skip hotkey if user is focused inside terminal input field
        if (document.activeElement === terminalInput) return;
        
        e.preventDefault();
        spacePressed = true;
        startVoiceCapture();
    }
});

window.addEventListener('keyup', (e) => {
    if (e.code === 'Space') {
        if (document.activeElement === terminalInput) return;
        
        e.preventDefault();
        spacePressed = false;
        stopVoiceCapture();
    }
});

// 7. Manual Text Command Sending
function sendTextCommand() {
    const text = terminalInput.value.trim();
    if (!text) return;
    
    logToTerminal('USER-INPUT', text);
    
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ action: 'text_input', text: text }));
        updateState('thinking');
    } else {
        logToTerminal('ERROR', 'No se pudo enviar el comando. WebSocket desconectado.');
    }
    
    terminalInput.value = '';
}

sendBtn.addEventListener('click', sendTextCommand);
terminalInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        sendTextCommand();
    }
});

// 8. Markdown rendering logic for Daily Plan
function renderDailyPlan(markdown) {
    if (!markdown || markdown.trim().includes("Error")) {
        dailyPlanContainer.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-center text-slate-500 p-4">
                <p class="text-xs font-mono uppercase tracking-wider">Plan Diario Inexistente</p>
                <p class="text-[10px] text-slate-600 mt-2 font-mono">Di "Actualiza mi plan del día" para crearlo</p>
            </div>
        `;
        return;
    }
    
    // Parse simplified markdown in JS
    let html = '';
    const lines = markdown.split('\n');
    let insideList = false;
    
    lines.forEach(line => {
        line = line.trim();
        if (!line) return;
        
        if (line.startsWith('# ')) {
            if (insideList) { html += '</ol>'; insideList = false; }
            html += `<h1>${line.substring(2)}</h1>`;
        } else if (line.startsWith('## ')) {
            if (insideList) { html += '</ol>'; insideList = false; }
            html += `<h2>${line.substring(3)}</h2>`;
        } else if (line.match(/^\d+\.\s+\[\s*\]/)) {
            // Task uncompleted (e.g., 1. [ ] Learn Gemini)
            if (!insideList) { html += '<ol class="space-y-3">'; insideList = true; }
            const text = line.replace(/^\d+\.\s+\[\s*\]/, '').trim();
            html += `<li><input type="checkbox" class="mr-2" disabled> <span>${text}</span></li>`;
        } else if (line.match(/^\d+\.\s+\[x\]/i)) {
            // Task completed (e.g., 1. [x] Buy milk)
            if (!insideList) { html += '<ol class="space-y-3">'; insideList = true; }
            const text = line.replace(/^\d+\.\s+\[x\]/i, '').trim();
            html += `<li><input type="checkbox" class="mr-2" checked disabled> <span class="line-through text-slate-500">${text}</span></li>`;
        } else if (line.startsWith('- ') || line.startsWith('* ')) {
            if (insideList) { html += '</ol>'; insideList = false; }
            const text = line.substring(2);
            html += `<p class="text-xs text-slate-400 my-1 font-mono">${text}</p>`;
        } else {
            if (insideList) { html += '</ol>'; insideList = false; }
            html += `<p class="text-xs text-slate-400 mb-2">${line}</p>`;
        }
    });
    
    if (insideList) { html += '</ol>'; }
    
    dailyPlanContainer.innerHTML = html;
}

// 9. Render Inbox summary
function renderInbox(content) {
    if (!content) {
        inboxSummaryContainer.innerHTML = '<p class="text-slate-500 font-mono text-center mt-6">La bandeja de entrada está vacía.</p>';
        return;
    }
    
    // Clean headers slightly
    let formatted = content.replace(/### Note: /g, '<strong>📌 ').replace(/\n/g, '<br>');
    inboxSummaryContainer.innerHTML = `<div class="font-mono text-[11px] text-slate-300 leading-relaxed">${formatted}</div>`;
}

// 10. Update metrics
function updateMetrics(cpu, ram, latency) {
    if (cpu !== undefined) metricCpu.textContent = `${cpu}%`;
    if (ram !== undefined) metricRam.textContent = `${ram}%`;
    if (latency !== undefined) metricLatency.textContent = `${latency}ms`;
}

// 11. Core 3D Hologram Visualizer (Three.js WebGL)
const canvas = document.getElementById('waveform-canvas');

// Scene, Camera, and WebGL Renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
camera.position.z = 10;

const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

function resizeCanvas() {
    const parent = canvas.parentElement;
    const width = parent.clientWidth * 0.7;
    const height = parent.clientHeight * 0.7;
    renderer.setSize(width, height);
    camera.aspect = 1;
    camera.updateProjectionMatrix();
}
window.addEventListener('resize', resizeCanvas);
setTimeout(resizeCanvas, 100);

// Create Holographic Particle Sphere (using Fibonacci distribution)
const particleCount = 500;
const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);
const initialPositions = new Float32Array(particleCount * 3);

for (let i = 0; i < particleCount; i++) {
    const offset = 2 / particleCount;
    const increment = Math.PI * (3 - Math.sqrt(5));
    
    const y = ((i * offset) - 1) + (offset / 2);
    const r = Math.sqrt(1 - Math.pow(y, 2));
    const phi = i * increment;
    
    const x = Math.cos(phi) * r;
    const z = Math.sin(phi) * r;
    
    const radius = 3.3; // Base radius of the sphere
    
    positions[i * 3] = x * radius;
    positions[i * 3 + 1] = y * radius;
    positions[i * 3 + 2] = z * radius;
    
    initialPositions[i * 3] = x * radius;
    initialPositions[i * 3 + 1] = y * radius;
    initialPositions[i * 3 + 2] = z * radius;
}

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

// Create glowing neon points
const material = new THREE.PointsMaterial({
    color: 0x06b6d4, // Default Cyan
    size: 0.13,
    transparent: true,
    opacity: 0.75,
    blending: THREE.AdditiveBlending
});

const particleSystem = new THREE.Points(geometry, material);
scene.add(particleSystem);

// Add inner wireframe sphere for visual depth
const sphereGeo = new THREE.SphereGeometry(3.2, 12, 12);
const sphereMat = new THREE.MeshBasicMaterial({
    color: 0x06b6d4,
    wireframe: true,
    transparent: true,
    opacity: 0.08
});
const wireframeSphere = new THREE.Mesh(sphereGeo, sphereMat);
scene.add(wireframeSphere);

let clock = new THREE.Clock();

function animate3D() {
    requestAnimationFrame(animate3D);
    
    const elapsedTime = clock.getElapsedTime();
    const pos = geometry.attributes.position.array;
    
    let colorHex = 0x06b6d4; // Default Cyan
    let rotationSpeed = 0.3;
    let waveFreq = 2.0;
    let waveAmp = 0.1;
    
    // Check states dynamically
    if (currentState === 'listening') {
        colorHex = 0xf43f5e; // Rose/Red
        rotationSpeed = 1.3;
        waveFreq = 7.0;
        waveAmp = 0.55;
    } else if (currentState === 'thinking') {
        colorHex = 0xf59e0b; // Amber/Yellow
        rotationSpeed = 2.2;
        waveFreq = 4.0;
        waveAmp = 0.18;
    } else if (currentState === 'speaking') {
        colorHex = 0x10b981; // Emerald/Green
        rotationSpeed = 0.7;
        waveFreq = 5.0;
        waveAmp = 0.3 + Math.sin(elapsedTime * 6) * 0.15; // Pulse with voice
    } else { // idle
        colorHex = 0x06b6d4; // Cyan
        rotationSpeed = 0.2;
        waveFreq = 1.5;
        waveAmp = 0.04;
    }
    
    material.color.setHex(colorHex);
    sphereMat.color.setHex(colorHex);
    
    // Wave displacement calculations on the particles
    for (let i = 0; i < particleCount; i++) {
        const xIdx = i * 3;
        const yIdx = i * 3 + 1;
        const zIdx = i * 3 + 2;
        
        const ix = initialPositions[xIdx];
        const iy = initialPositions[yIdx];
        const iz = initialPositions[zIdx];
        
        const len = Math.sqrt(ix*ix + iy*iy + iz*iz);
        const dx = ix / len;
        const dy = iy / len;
        const dz = iz / len;
        
        // Deform using a beautiful sinusoidal noise
        const offset = Math.sin(ix * waveFreq + elapsedTime * 4) * Math.cos(iy * waveFreq + elapsedTime * 3) * waveAmp;
        
        pos[xIdx] = ix + dx * offset;
        pos[yIdx] = iy + dy * offset;
        pos[zIdx] = iz + dz * offset;
    }
    
    geometry.attributes.position.needsUpdate = true;
    
    // Rotate models
    particleSystem.rotation.y = elapsedTime * rotationSpeed;
    particleSystem.rotation.x = elapsedTime * (rotationSpeed * 0.5);
    wireframeSphere.rotation.y = -elapsedTime * (rotationSpeed * 0.7);
    
    // High energy expansion and contraction on 'thinking' state
    if (currentState === 'thinking') {
        const scale = 1.0 + Math.sin(elapsedTime * 14) * 0.07;
        particleSystem.scale.set(scale, scale, scale);
        wireframeSphere.scale.set(scale, scale, scale);
        sphereMat.opacity = 0.22;
    } else {
        particleSystem.scale.set(1, 1, 1);
        wireframeSphere.scale.set(1, 1, 1);
        sphereMat.opacity = 0.08;
    }
    
    renderer.render(scene, camera);
}
animate3D();


// 12. Run on Load
connectWebSocket();
logToTerminal('KAIROS-LOG', 'Sistemas listos. Conectando al orquestador central...');

// 13. Diagnostics Drawer Toggle Actions
const diagBtn = document.getElementById('diag-toggle-btn');
const diagDrawer = document.getElementById('diag-drawer');
const closeDiagBtn = document.getElementById('diag-close-btn');

if (diagBtn && diagDrawer) {
    diagBtn.addEventListener('click', () => {
        diagDrawer.classList.remove('translate-x-full');
    });
}
if (closeDiagBtn && diagDrawer) {
    closeDiagBtn.addEventListener('click', () => {
        diagDrawer.classList.add('translate-x-full');
    });
}

// 14. Interactive Core Node Mouse/Touch Recording Trigger
if (coreNode) {
    coreNode.addEventListener('mousedown', (e) => {
        e.preventDefault();
        startVoiceCapture();
    });
    
    coreNode.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startVoiceCapture();
    });
}
