//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai-trainer\JobMonitor.vue total lines 441 
//#######################################################################

<template>
  <div class="d-flex flex-row fill-height w-100 overflow-hidden pa-4">
    <v-card class="gold-panel full-height-card mr-4" style="width: 300px; flex-shrink: 0;">
        <v-card-title class="text-gold font-weight-bold border-bottom-gold font-mono text-subtitle-2 d-flex align-center">
            <v-icon size="small" class="mr-2">mdi-pulse</v-icon> ACTIVE JOBS
        </v-card-title>

        <div v-if="trainingJobs.length === 0" class="text-center py-10 text-grey font-mono">
            NO ACTIVE SIGNALS
        </div>

        <v-list bg-color="transparent" class="pa-2 overflow-y-auto flex-grow-1 custom-scrollbar" v-else>
            <v-list-item
                v-for="job in trainingJobs"
                :key="job.job_id"
                class="scanner-item my-1 mb-2"
                :class="{ 'active-scanner': selectedJobId === job.job_id }"
                @click="selectJob(job)"
            >
                <template v-slot:prepend>
                    <v-icon :color="getStatusColor(job.status)" icon="mdi-console-line" class="mr-3"></v-icon>
                </template>
                <v-list-item-title class="text-white font-weight-bold font-mono text-body-2">
                    {{ job.new_model_name }}
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption text-grey font-mono mt-1">
                    <span :class="`text-${getStatusColor(job.status)}`">[{{ job.status }}]</span>
                </v-list-item-subtitle>
                <template v-slot:append>
                    <v-btn icon="mdi-delete" size="small" variant="text" color="red-darken-2" @click.stop="handleDeleteJob(job.job_id)"></v-btn>
                </template>
            </v-list-item>
        </v-list>
    </v-card>

    <div class="d-flex flex-column flex-grow-1 full-height-card" style="min-width: 0; overflow: hidden;">

        <v-card class="gold-panel mb-4 monitor-display" style="height: 35%; flex-shrink: 0;" v-if="selectedJob">

            <div class="crt-lines"></div>
            <div class="crt-flicker"></div>

            <div class="d-flex align-center px-4 py-2 border-bottom-gold bg-black-transparent z-index-top justify-space-between">
                <div class="d-flex align-center">
                    <v-icon icon="mdi-chart-bell-curve-cumulative" color="#FFD700" size="small" class="mr-2 beat-icon"></v-icon>
                    <span class="text-caption text-gold font-weight-mono font-weight-bold tracking-wide">NEURAL LOSS METRICS [LIVE]</span>
                </div>
                <div class="d-flex align-center">
                     <span class="text-caption text-green-accent-3 font-mono blink-fast mr-2" v-if="lossHistory.length > 0">● RECEIVING DATA</span>
                     <span class="text-caption text-amber font-mono blink-slow" v-else>● STANDBY MODE</span>
                </div>
            </div>

            <div class="fill-height pa-4 position-relative d-flex align-end z-index-top" style="overflow: hidden;">

                <div v-if="lossHistory.length > 0" class="w-100 h-100 d-flex flex-column position-relative">

                    <div class="cyber-grid-moving"></div>

                    <div class="tactical-hud-center">
                        <div class="radar-circle"></div>
                        <div class="radar-sweep"></div>
                        <div class="radar-crosshair"></div>
                    </div>

                    <div class="freq-bars-container">
                        <div v-for="n in 15" :key="n" class="freq-bar" :style="`animation-delay: -${Math.random()}s; height: ${20 + Math.random() * 40}px`"></div>
                    </div>

                    <div class="system-metrics-overlay font-mono text-caption text-grey-darken-1">
                        <div class="d-flex align-center justify-end mb-1">
                            <span class="mr-2">VRAM</span>
                            <v-progress-linear model-value="85" color="green-accent-3" style="width: 50px" height="4"></v-progress-linear>
                        </div>
                        <div class="d-flex align-center justify-end mb-1">
                            <span class="mr-2">TENSOR</span>
                            <v-progress-linear indeterminate color="amber" style="width: 50px" height="4"></v-progress-linear>
                        </div>
                        <div class="d-flex align-center justify-end">
                            <span class="mr-2">CUDA CORES</span>
                            <span class="text-gold blink-slow">LOCKED</span>
                        </div>
                    </div>

                    <v-sparkline
                        :model-value="lossHistory"
                        color="#FFD700"
                        line-width="3"
                        padding="16"
                        stroke-linecap="round"
                        smooth
                        auto-draw
                        class="flex-grow-1 neon-graph"
                    >
                        <template v-slot:label="item">
                            {{ item.value.toFixed(3) }}
                        </template>
                    </v-sparkline>

                    <div class="d-flex justify-space-between text-caption text-grey font-mono px-2 mt-2 status-bar">
                        <span>T-MINUS: CALC...</span>
                        <span>EPOCH CYCLE -></span>
                        <span class="text-gold font-weight-bold pulse-text">LOSS: {{ currentLoss }}</span>
                    </div>
                </div>

                <div v-else class="w-100 h-100 d-flex align-center justify-center position-relative">
                    <div class="matrix-rain-bg">
                        <span v-for="n in 20" :key="n" :style="`left: ${Math.random()*100}%; animation-delay: -${Math.random()*5}s`">
                            {{ Math.random().toString(36).substring(7) }}
                        </span>
                    </div>

                    <div class="text-center z-index-top">
                        <div class="radar-spinner mb-4 mx-auto">
                            <div class="radar-scan"></div>
                        </div>
                        <h3 class="text-gold font-mono glitch-text mb-1" data-text="INITIALIZING UPLINK...">INITIALIZING UPLINK...</h3>
                        <div class="text-caption text-grey-darken-1 font-mono typing-effect">
                            >> ESTABLISHING NEURAL HANDSHAKE...<br>
                            >> WAITING FOR LOSS TENSOR STREAM...
                        </div>
                    </div>
                </div>
            </div>
        </v-card>

        <v-card class="terminal-card gold-panel flex-grow-1" style="min-height: 0; display: flex; flex-direction: column;">
            <div class="terminal-header d-flex align-center px-4 py-2 border-bottom-gold flex-shrink-0">
                <v-icon icon="mdi-console" color="grey" size="small" class="mr-2"></v-icon>
                <span class="text-caption text-grey font-weight-mono">TERMINAL OUTPUT STREAM</span>
                <v-spacer></v-spacer>
                <span v-if="selectedJob" class="text-caption text-gold font-weight-bold font-mono">
                    PID: {{ selectedJob.job_id.substring(0,8) }}
                </span>
            </div>

            <div class="terminal-body pa-4 font-weight-mono" ref="terminalBody" style="overflow-y: auto; flex-grow: 1;">
                <div v-if="!selectedJob" class="text-grey-darken-2 text-center mt-10 font-mono">
                </div>
                <div v-else>
                    <div class="log-line text-gold font-weight-bold mb-2">
                        > ESTABLISHING SECURE CONNECTION TO: {{ selectedJob.new_model_name }}
                    </div>

                    <div v-for="(log, index) in parsedLogs" :key="index" class="log-line">
                        <span class="text-grey-darken-2 mr-2" v-if="log.time">[{{ log.time }}]</span>
                        <span :class="log.class">{{ log.msg }}</span>
                    </div>

                    <div v-if="selectedJob.status === 'TRAINING'" class="log-line mt-2">
                        <span class="text-gold blink-cursor">_</span>
                    </div>
                </div>
            </div>
        </v-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue';
import { useTrainingStore } from '@/store/training';
import { useUiStore } from '@/store/ui';
import { storeToRefs } from 'pinia';

const trainingStore = useTrainingStore();
const uiStore = useUiStore();
const { trainingJobs } = storeToRefs(trainingStore);

const selectedJobId = ref(null);
const terminalBody = ref(null);
const lossHistory = ref([]);
const currentLoss = ref('N/A');
let pollInterval = null;

const selectedJob = computed(() => {
    return trainingJobs.value.find(j => j.job_id === selectedJobId.value) || null;
});

const parsedLogs = computed(() => {
    if (!selectedJob.value || !selectedJob.value.live_logs) return [];
    const lines = selectedJob.value.live_logs.split('\n');
    const parsedLines = [];
    const tempLoss = [];
    lines.forEach(line => {
        if (!line.trim()) return;
        const timeMatch = line.match(/^\[(\d{2}:\d{2}:\d{2})\](.*)/);
        let time = '';
        let msg = line;
        if (timeMatch) { time = timeMatch[1]; msg = timeMatch[2].trim(); }
        else {
            const lenientMatch = line.match(/^\s*(\d+%|\d+\/\d+|\[.*?\])?\s*(.*)/);
            if(lenientMatch) msg = line;
        }
        const lossMatch = msg.match(/loss['"]?:\s*([\d\.]+)/i);
        if (lossMatch) {
            const val = parseFloat(lossMatch[1]);
            if (!isNaN(val)) { tempLoss.push(val); currentLoss.value = val.toFixed(4); }
        }
        let cssClass = 'text-grey-lighten-1';
        const lowerMsg = msg.toLowerCase();
        if (lowerMsg.includes('error') || lowerMsg.includes('failed')) cssClass = 'text-red-accent-2';
        else if (lowerMsg.includes('warning') || lowerMsg.includes('warn')) cssClass = 'text-amber';
        else if (lowerMsg.includes('success') || lowerMsg.includes('done') || lowerMsg.includes('complete')) cssClass = 'text-green-accent-3';
        else if (lowerMsg.includes('step') || lowerMsg.includes('epoch')) cssClass = 'text-gold';
        else if (lowerMsg.includes('loading') || lowerMsg.includes('starting')) cssClass = 'text-grey';
        parsedLines.push({ time, msg, class: cssClass });
    });
    if (tempLoss.length > 0) lossHistory.value = tempLoss;
    return parsedLines;
});

watch(parsedLogs, () => {
    nextTick(() => {
        if (terminalBody.value) {
            const el = terminalBody.value;
            const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 150;
            if (isAtBottom) el.scrollTop = el.scrollHeight;
        }
    });
});

watch(selectedJobId, () => {
    lossHistory.value = [];
    currentLoss.value = 'N/A';
});

watch(trainingJobs, (newJobs) => {
    if (!selectedJobId.value && newJobs.length > 0) {
        selectedJobId.value = newJobs[0].job_id;
    }
});

onMounted(() => {
    trainingStore.fetchTrainingJobs();
    if (trainingJobs.value.length > 0 && !selectedJobId.value) {
        selectedJobId.value = trainingJobs.value[0].job_id;
    }
    startPolling();
});

onUnmounted(() => stopPolling());

function startPolling() {
    stopPolling();
    pollInterval = setInterval(() => {
        trainingStore.fetchTrainingJobs();
    }, 2000);
}

function stopPolling() {
    if (pollInterval) clearInterval(pollInterval);
}

function selectJob(job) { selectedJobId.value = job.job_id; }

function getStatusColor(status) {
    if (status === 'COMPLETED') return 'green-accent-3';
    if (status === 'FAILED') return 'red-accent-2';
    if (status === 'TRAINING' || status === 'PREPARING' || status === 'CONVERTING') return 'amber';
    return 'grey';
}

async function handleDeleteJob(jobId) {
    const confirmed = await uiStore.showConfirmation({
        title: 'Purge Job Logs',
        text: 'Delete this training history? Model files will remain.',
        color: 'error',
        confirmText: 'Purge'
    });
    if (confirmed) {
        await trainingStore.deleteJob(jobId);
        if (selectedJobId.value === jobId) selectedJobId.value = null;
    }
}
</script>

<style scoped>
.text-gold { color: #FFD700 !important; }
.border-gold-subtle { border-color: rgba(255, 215, 0, 0.1) !important; }
.border-bottom-gold { border-bottom: 1px solid rgba(255, 215, 0, 0.15) !important; }
.gold-panel { background: #080808; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; backdrop-filter: blur(5px); }
.full-height-card { height: 100%; display: flex; flex-direction: column; }
.font-mono { font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important; }
.scanner-item { border-radius: 4px; margin: 0 4px; transition: all 0.2s ease; border-left: 3px solid transparent; background: rgba(255,255,255,0.02); }
.scanner-item:hover { background: rgba(255, 215, 0, 0.08); cursor: pointer; border-left: 3px solid rgba(255, 215, 0, 0.5); }
.scanner-item.active-scanner { background: rgba(255, 215, 0, 0.1); border-left: 3px solid #FFD700; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #050505; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 215, 0, 0.2); border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #FFD700; }

.terminal-card { background: #050505; border: 1px solid rgba(255, 255, 255, 0.1); display: flex; flex-direction: column; box-shadow: inset 0 0 20px rgba(0,0,0,0.8); }
.terminal-body { flex: 1; overflow-y: auto; font-size: 0.8rem; line-height: 1.5; color: #ccc; font-family: 'Fira Code', monospace; }
.log-line { margin-bottom: 2px; word-break: break-all; }
.bg-black-transparent { background-color: rgba(0,0,0,0.5); }
.z-index-top { z-index: 10; position: relative; }

/* ANIMATIONS */
.beat-icon { animation: beat 2s infinite ease-in-out; }
.blink-cursor { animation: blink 1s steps(2, start) infinite; }
.blink-fast { animation: blink 0.5s steps(2, start) infinite; }
.blink-slow { animation: blink 2s infinite; }
@keyframes beat { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.1); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
@keyframes blink { to { visibility: hidden; } }

/* MONITOR EFFECTS */
.monitor-display { position: relative; overflow: hidden; background: #000; }

.crt-lines {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%),
                linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    background-size: 100% 2px, 3px 100%;
    z-index: 2; pointer-events: none;
}

.crt-flicker {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(255,255,255,0.02); opacity: 0;
    z-index: 2; pointer-events: none; animation: flicker 0.15s infinite;
}

@keyframes flicker { 0% { opacity: 0.02; } 50% { opacity: 0.05; } 100% { opacity: 0.02; } }

.matrix-rain-bg span {
    position: absolute; top: -20px;
    color: rgba(0, 255, 65, 0.15); font-family: 'Fira Code', monospace; font-size: 1.2rem;
    animation: matrix-fall-random 3s linear infinite; pointer-events: none; z-index: 1;
}
@keyframes matrix-fall-random { to { top: 120%; } }

.radar-spinner { width: 60px; height: 60px; border: 2px solid rgba(255, 215, 0, 0.3); border-radius: 50%; position: relative; box-shadow: 0 0 15px rgba(255, 215, 0, 0.1); }
.radar-scan { width: 50%; height: 50%; background: linear-gradient(45deg, transparent 50%, rgba(255, 215, 0, 0.8) 100%); border-radius: 100% 0 0 0; position: absolute; top: 0; left: 0; transform-origin: 100% 100%; animation: radar-spin 2s infinite linear; }
@keyframes radar-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.glitch-text { position: relative; color: #FFD700; }
.typing-effect { display: inline-block; overflow: hidden; border-right: 2px solid #FFD700; white-space: nowrap; animation: typing 3.5s steps(40, end), blink-caret .75s step-end infinite; }
@keyframes typing { from { width: 0 } to { width: 100% } }
@keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #FFD700; } }

/* NEW: CYBER MOVING GRID */
.cyber-grid-moving {
    position: absolute;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background:
        linear-gradient(rgba(0, 255, 0, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 0, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    transform: perspective(500px) rotateX(60deg);
    animation: grid-move 5s linear infinite;
    z-index: 0;
}
@keyframes grid-move {
    from { transform: perspective(500px) rotateX(60deg) translateY(0); }
    to { transform: perspective(500px) rotateX(60deg) translateY(40px); }
}

/* NEW: TACTICAL HUD & RADAR ELEMENTS */
.tactical-hud-center {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 300px; height: 300px;
    pointer-events: none; z-index: 1;
    opacity: 0.15; /* Subtle */
}
.radar-circle {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    border: 1px dashed #FFD700; border-radius: 50%;
    animation: spin-slow 20s linear infinite;
}
.radar-sweep {
    position: absolute; top: 50%; left: 50%; width: 50%; height: 2px;
    background: linear-gradient(90deg, transparent, #FFD700);
    transform-origin: 0 0;
    animation: sweep 4s linear infinite;
}
.radar-crosshair {
    position: absolute; top: 50%; left: 0; width: 100%; height: 1px;
    background: rgba(255, 215, 0, 0.3);
}
.radar-crosshair::after {
    content: ''; position: absolute; left: 50%; top: -150px; width: 1px; height: 300px;
    background: rgba(255, 215, 0, 0.3);
}

@keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes sweep { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* NEW: FREQUENCY BARS (STICKS) */
.freq-bars-container {
    position: absolute; bottom: 0; left: 0; width: 100%; height: 50px;
    display: flex; align-items: flex-end; justify-content: center; gap: 4px;
    z-index: 2; opacity: 0.4;
    padding-bottom: 20px;
}
.freq-bar {
    width: 6px; background: #FFD700;
    animation: bounce 0.8s ease-in-out infinite alternate;
}
@keyframes bounce {
    0% { height: 10px; opacity: 0.3; }
    100% { height: 40px; opacity: 0.8; }
}

.system-metrics-overlay {
    position: absolute;
    top: 10px; right: 10px;
    background: rgba(0,0,0,0.7);
    border: 1px solid #333;
    padding: 8px;
    border-radius: 4px;
    z-index: 5;
    pointer-events: none;
}

.status-bar {
    background: rgba(0,0,0,0.6);
    border-top: 1px solid #333;
    z-index: 5;
}

.neon-graph :deep(path) {
    stroke: #FFD700 !important;
    stroke-width: 3px;
    filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.8));
    animation: dash 2s ease-out forwards;
}
.pulse-text { animation: pulse-gold 1s infinite alternate; }
@keyframes pulse-gold {
    0% { opacity: 0.7; transform: scale(1); }
    100% { opacity: 1; text-shadow: 0 0 15px #FFD700; transform: scale(1.05); }
}
</style>
