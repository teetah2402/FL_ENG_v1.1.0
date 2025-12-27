//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai-trainer\ModelFactory.vue total lines 442 
//#######################################################################

<template>
  <v-container fluid class="fill-height align-start justify-center pa-4">
    <v-row class="fill-height w-100">

      <v-col cols="12" md="6" class="d-flex flex-column">
        <v-card class="gold-panel elevation-10 flex-grow-1 d-flex flex-column">
          <v-card-item class="pb-2">
            <template v-slot:prepend>
              <v-icon size="large" color="#FFD700" class="beat-icon">mdi-factory</v-icon>
            </template>
            <v-card-title class="text-h6 font-mono text-white font-weight-bold">ASSEMBLY CONFIG</v-card-title>
            <v-card-subtitle class="text-caption text-grey-darken-1 font-mono">Export & Merge Operations</v-card-subtitle>
          </v-card-item>

          <v-divider class="border-gold-subtle"></v-divider>

          <v-card-text class="pt-6 flex-grow-1 d-flex flex-column justify-space-between">

            <div>
                <div class="text-caption text-gold font-weight-bold mb-1 font-mono">SOURCE ADAPTER</div>
                <div class="d-flex align-center gap-2 mb-2">
                    <v-select
                        v-model="conversionConfig.model_id"
                        :items="convertibleModels"
                        item-title="name"
                        item-value="id"
                        placeholder="Select Trained Adapter..."
                        variant="outlined"
                        color="#FFD700"
                        base-color="grey-darken-2"
                        class="gold-input flex-grow-1 font-mono"
                        prepend-inner-icon="mdi-file-tree"
                        hide-details
                        density="compact"
                        no-data-text="No trained adapters found"
                    ></v-select>

                    <v-btn
                        icon="mdi-refresh"
                        variant="outlined"
                        color="#FFD700"
                        class="gold-btn-outline"
                        :loading="trainingStore.isLoadingModels"
                        @click="refreshData"
                        v-tooltip="'Refresh Model List'"
                    ></v-btn>
                </div>

                <div class="text-caption text-grey-darken-1 mb-6 font-mono" v-if="!conversionConfig.model_id">
                    <v-icon size="small" icon="mdi-information-outline" class="mr-1"></v-icon>
                    <span v-if="convertibleModels.length === 0">No completed training jobs found.</span>
                    <span v-else>Select a trained adapter to unlock protocols.</span>
                </div>
            </div>

            <div class="mb-6 animated-fade-in" v-if="conversionConfig.model_id">
                <div class="text-caption text-gold font-weight-bold mb-2 font-mono">HARDWARE STRATEGY</div>
                <v-select
                    v-model="conversionConfig.strategy"
                    :items="[
                        {title: 'Auto (Smart Detect)', value: 'auto', icon: 'mdi-auto-fix'},
                        {title: 'Force RAM (CPU Safe - 64GB)', value: 'cpu', icon: 'mdi-memory'},
                        {title: 'Force VRAM (GPU Fast - 24GB+)', value: 'gpu', icon: 'mdi-expansion-card'}
                    ]"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    color="#FFD700"
                    base-color="grey-darken-2"
                    class="gold-input font-mono"
                    density="compact"
                    prepend-inner-icon="mdi-chip"
                    hint="Use 'Force RAM' if you have < 16GB VRAM to avoid crashes."
                    persistent-hint
                >
                    <template v-slot:item="{ props, item }">
                        <v-list-item v-bind="props" :prepend-icon="item.raw.icon" class="text-grey-lighten-1 font-mono"></v-list-item>
                    </template>
                </v-select>
            </div>

            <div class="mb-6 animated-fade-in" v-if="conversionConfig.model_id">
                <div class="text-caption text-gold font-weight-bold mb-2 font-mono">OPERATION MODE</div>
                <v-btn-toggle v-model="conversionConfig.mode" mandatory class="w-100 border-gold-subtle custom-toggle" color="#FFD700" density="default">
                    <v-btn value="gguf" class="flex-grow-1 font-mono text-body-2">
                        <v-icon start>mdi-zip-box</v-icon> GGUF BINARY
                    </v-btn>
                    <v-btn value="merge" class="flex-grow-1 font-mono text-body-2">
                        <v-icon start>mdi-call-merge</v-icon> MERGE TO BASE
                    </v-btn>
                </v-btn-toggle>
            </div>

            <div v-if="conversionConfig.mode === 'gguf' && conversionConfig.model_id" class="mb-6 animated-fade-in">
                <div class="text-caption text-gold font-weight-bold mb-2 font-mono">COMPRESSION (QUANTIZATION)</div>

                <v-btn-toggle
                    v-model="conversionConfig.quantization"
                    mandatory
                    class="d-flex flex-wrap gap-2 w-100"
                    style="height: auto; background: transparent; border: none;"
                >
                    <v-btn
                        v-for="q in ['q4_k_m', 'q5_k_m', 'q8_0', 'f16']"
                        :key="q"
                        :value="q"
                        variant="outlined"
                        color="#FFD700"
                        class="flex-grow-1 quant-btn font-mono font-weight-bold mb-2"
                        style="border-color: rgba(255, 215, 0, 0.3); min-width: 80px;"
                    >
                        {{ q.toUpperCase() }}
                        <v-icon end size="small" icon="mdi-check-circle" class="ml-1 active-icon"></v-icon>
                    </v-btn>
                </v-btn-toggle>

                <div class="text-caption text-grey-darken-1 font-mono mt-1">
                    <v-icon size="x-small" color="blue" icon="mdi-information"></v-icon>
                    Selected: <span class="text-white font-weight-bold">{{ conversionConfig.quantization.toUpperCase() }}</span>
                </div>
            </div>

            <div class="mb-6 animated-fade-in" v-if="conversionConfig.model_id">
                <div class="text-caption text-gold font-weight-bold mb-1 font-mono">OUTPUT IDENTITY</div>
                <v-text-field
                    v-model="conversionConfig.new_name"
                    :placeholder="conversionConfig.mode === 'gguf' ? 'flowork-chat.gguf' : 'My-New-Base-v2'"
                    variant="outlined"
                    color="#FFD700"
                    base-color="grey-darken-2"
                    class="gold-input font-mono"
                    prepend-inner-icon="mdi-tag-text"
                    density="compact"
                ></v-text-field>
            </div>

            <v-btn
              block
              size="x-large"
              color="#FFD700"
              variant="flat"
              @click="handleBuildGGUF"
              :loading="trainingStore.isConverting"
              :disabled="!conversionConfig.model_id"
              prepend-icon="mdi-nut"
              class="text-black font-weight-bold glow-button font-mono mt-auto"
            >
              {{ conversionConfig.mode === 'gguf' ? 'COMPILE GGUF BINARY' : 'MERGE & SAVE FULL MODEL' }}
            </v-btn>

          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" class="d-flex flex-column">
        <v-card class="gold-panel elevation-10 flex-grow-1 d-flex flex-column position-relative overflow-hidden">

            <div class="cyber-grid"></div>
            <div class="scanline"></div>

            <div class="d-flex justify-space-between px-4 py-2 border-bottom-gold z-index-top bg-glass">
                <div class="text-caption text-gold font-mono font-weight-bold">
                    <v-icon start size="small" class="beat-icon">mdi-monitor-eye</v-icon>
                    VISUALIZER
                </div>
                <div class="text-caption font-mono" :class="trainingStore.isConverting ? 'text-green-accent-3 blink-text' : 'text-grey'">
                    STATUS: {{ trainingStore.isConverting ? 'COMPILING' : 'IDLE' }}
                </div>
            </div>

            <div class="flex-grow-1 d-flex align-center justify-center position-relative pa-4" style="perspective: 1000px;">

                <div v-if="!trainingStore.isConverting" class="text-center z-index-top animated-fade-in">
                    <div class="holo-box-container mb-6">
                        <div class="holo-cube">
                            <div class="face front"></div>
                            <div class="face back"></div>
                            <div class="face right"></div>
                            <div class="face left"></div>
                            <div class="face top"></div>
                            <div class="face bottom"></div>
                        </div>
                    </div>
                    <div class="text-h6 text-grey-darken-1 font-mono glitch-text">FACTORY OFFLINE</div>
                    <div class="text-caption text-grey-darken-2 font-mono typing-effect">WAITING FOR OPERATOR INPUT...</div>
                </div>

                <div v-else class="text-center z-index-top w-100 h-100 d-flex flex-column align-center justify-center">

                    <div class="compression-chamber mb-8">
                        <div class="compressor-plate top-plate"></div>
                        <div class="raw-data-cloud">
                            <v-icon v-for="n in 10" :key="n"
                                color="#FFD700"
                                size="small"
                                class="floating-particle"
                                :style="`left: ${Math.random()*100}%; animation-delay: -${Math.random()}s`"
                            >mdi-binary</v-icon>
                        </div>
                        <div class="compressor-plate bottom-plate"></div>
                        <div class="laser-beam"></div>
                    </div>

                    <div class="text-h5 text-gold font-mono font-weight-bold mb-2 text-shadow-gold">PROCESSING</div>
                    <div class="w-75">
                        <v-progress-linear indeterminate color="#FFD700" height="4" rounded class="mb-2"></v-progress-linear>
                        <div class="d-flex justify-space-between text-caption font-mono text-green-accent-3">
                            <span>OPTIMIZING TENSORS</span>
                            <span>{{ conversionConfig.quantization.toUpperCase() }}</span>
                        </div>
                    </div>

                    <div class="mt-6 w-100 border-gold-dashed pa-2 bg-black text-left font-mono text-caption text-grey" style="height: 100px; overflow: hidden; opacity: 0.8;">
                        <div class="text-green">> Allocating CUDA buffers... OK</div>
                        <div class="text-green">> Loading model weights... OK</div>
                        <div class="text-gold">> Quantizing layer 1/32...</div>
                        <div class="text-gold blink-text">> Quantizing layer 2/32...</div>
                    </div>
                </div>

            </div>

            <div class="position-absolute bottom-0 left-0 w-100 pa-3 border-top-gold bg-glass z-index-top">
                <v-row dense class="text-caption font-mono">
                    <v-col cols="4" class="text-center border-right-gold-subtle">
                        <div class="text-grey">FORMAT</div>
                        <div class="text-white font-weight-bold">{{ conversionConfig.mode.toUpperCase() }}</div>
                    </v-col>
                    <v-col cols="4" class="text-center border-right-gold-subtle">
                        <div class="text-grey">DEVICE</div>
                        <div class="text-white font-weight-bold">{{ conversionConfig.strategy.toUpperCase() }}</div>
                    </v-col>
                    <v-col cols="4" class="text-center">
                        <div class="text-grey">TARGET</div>
                        <div class="text-gold font-weight-bold">{{ conversionConfig.quantization.toUpperCase() }}</div>
                    </v-col>
                </v-row>
            </div>

        </v-card>
      </v-col>

    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useTrainingStore } from '@/store/training';
import { useUiStore } from '@/store/ui';
import { storeToRefs } from 'pinia';

const emit = defineEmits(['conversion-started']);
const trainingStore = useTrainingStore();
const uiStore = useUiStore();
const { localModels: availableBaseModels, trainingJobs } = storeToRefs(trainingStore);

const conversionConfig = ref({
    model_id: null,
    quantization: 'q4_k_m',
    mode: 'gguf',
    new_name: '',
    strategy: 'auto'
});

const convertibleModels = computed(() => {
    /*
    return availableBaseModels.value.filter(m => {
        if (m.name.toLowerCase().endsWith('.gguf')) return false;
        return true;
    });
    */

    return trainingJobs.value
        .filter(j => j.status === 'COMPLETED')
        .map(j => ({
            id: j.new_model_name, // Using folder name/model name as ID
            name: j.new_model_name
        }));
});

onMounted(() => {
    trainingStore.fetchTrainingJobs();
    trainingStore.fetchLocalModels();
});

function refreshData() {
    trainingStore.fetchTrainingJobs();
    trainingStore.rescanModels();
}

async function handleBuildGGUF() {
    if (!conversionConfig.value.model_id) return;
    const success = await trainingStore.startConversionJob({
        model_id: conversionConfig.value.model_id,
        quantization: conversionConfig.value.quantization,
        new_model_name: conversionConfig.value.new_name,
        mode: conversionConfig.value.mode,
        strategy: conversionConfig.value.strategy
    });
    if (success) {
        uiStore.showNotification({ text: "Factory Protocol Initiated.", color: "cyan" });
        emit('conversion-started');
    }
}
</script>

<style scoped>
/* UTILS */
.text-gold { color: #FFD700 !important; }
.border-gold-subtle { border-color: rgba(255, 215, 0, 0.1) !important; }
.border-gold-dashed { border: 1px dashed rgba(255, 215, 0, 0.3); border-radius: 4px; }
.border-bottom-gold { border-bottom: 1px solid rgba(255, 215, 0, 0.2); }
.border-top-gold { border-top: 1px solid rgba(255, 215, 0, 0.2); }
.border-right-gold-subtle { border-right: 1px solid rgba(255, 215, 0, 0.1); }
.text-shadow-gold { text-shadow: 0 0 10px rgba(255, 215, 0, 0.8); }
.z-index-top { z-index: 5; position: relative; }

/* PANEL */
.gold-panel {
    background: #080808;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
}
.bg-glass { background: rgba(20,20,20,0.8); backdrop-filter: blur(5px); }
.bg-black { background-color: #000; }

/* INPUTS */
.gold-input :deep(.v-field) { background-color: rgba(255,255,255,0.03) !important; border-color: rgba(255,255,255,0.1); font-family: 'JetBrains Mono', monospace; }
.gold-input :deep(.v-field--focused) { border-color: #FFD700 !important; box-shadow: 0 0 5px rgba(255, 215, 0, 0.2); }
.gold-input :deep(.v-field__input), .gold-input :deep(.v-select__selection-text) { color: white !important; }
.gold-btn-outline { border-color: rgba(255,215,0,0.3); }

/* TOGGLE BUTTONS */
.custom-toggle .v-btn { color: rgba(255, 255, 255, 0.5) !important; background: rgba(0,0,0,0.3); }
.custom-toggle .v-btn--active { color: black !important; background-color: #FFD700 !important; font-weight: bold; }

/* QUANTIZATION BUTTONS (TACTICAL) */
.quant-btn {
    transition: all 0.2s ease;
    background: rgba(255, 255, 255, 0.02) !important;
}
.quant-btn.v-btn--active {
    background: rgba(255, 215, 0, 0.15) !important;
    border-color: #FFD700 !important;
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
    color: white !important;
}
.quant-btn .active-icon { display: none; }
.quant-btn.v-btn--active .active-icon { display: inline-flex; color: #FFD700; }

/* ANIMATIONS GENERAL */
.beat-icon { animation: beat 2s infinite ease-in-out; }
.glow-button { box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); transition: all 0.3s ease; }
.glow-button:hover { box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); transform: translateY(-2px); }
.blink-text { animation: blink 0.5s infinite; }
.animated-fade-in { animation: fadeIn 0.5s ease-out; }
.glitch-text { animation: glitch 2s infinite; }

@keyframes beat { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.1); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
@keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes glitch { 0% { opacity: 1; } 98% { opacity: 1; transform: skewX(0); } 99% { opacity: 0.8; transform: skewX(10deg); } 100% { opacity: 1; transform: skewX(0); } }

/* ============================
   HOLOGRAPHIC & FACTORY FX
   ============================ */
.cyber-grid {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background-image: linear-gradient(rgba(255, 215, 0, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 215, 0, 0.03) 1px, transparent 1px);
    background-size: 30px 30px;
    z-index: 0;
}
.scanline {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.2));
    background-size: 100% 4px; pointer-events: none; z-index: 2; opacity: 0.3;
}

/* 3D CUBE (IDLE) */
.holo-box-container { width: 100px; height: 100px; margin: 0 auto; perspective: 600px; }
.holo-cube {
    width: 100%; height: 100%; position: relative; transform-style: preserve-3d;
    animation: spin-cube 10s infinite linear;
}
.face {
    position: absolute; width: 100px; height: 100px;
    border: 1px solid #FFD700; background: rgba(255, 215, 0, 0.05);
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.1);
}
.front  { transform: rotateY(0deg) translateZ(50px); }
.back   { transform: rotateY(180deg) translateZ(50px); }
.right  { transform: rotateY(90deg) translateZ(50px); }
.left   { transform: rotateY(-90deg) translateZ(50px); }
.top    { transform: rotateX(90deg) translateZ(50px); }
.bottom { transform: rotateX(-90deg) translateZ(50px); }

@keyframes spin-cube { from { transform: rotateX(0) rotateY(0); } to { transform: rotateX(360deg) rotateY(360deg); } }

/* COMPRESSION CHAMBER (ACTIVE) */
.compression-chamber {
    width: 150px; height: 150px; position: relative;
    display: flex; flex-direction: column; justify-content: space-between; align-items: center;
}
.compressor-plate {
    width: 100%; height: 10px; background: #FFD700;
    box-shadow: 0 0 15px #FFD700;
    animation: compress-move 2s infinite ease-in-out;
}
.top-plate { margin-bottom: auto; }
.bottom-plate { margin-top: auto; }

.laser-beam {
    position: absolute; top: 0; bottom: 0; left: 50%; width: 2px;
    background: white; box-shadow: 0 0 10px cyan;
    animation: laser-flash 0.1s infinite;
}

.floating-particle { position: absolute; opacity: 0; animation: particle-rise 2s infinite; }

@keyframes compress-move {
    0% { transform: scaleX(1); height: 10px; }
    50% { transform: scaleX(0.8) translateY(30px); height: 20px; } /* Plates move closer */
    100% { transform: scaleX(1); height: 10px; }
}
@keyframes laser-flash { 0% { opacity: 0.5; } 100% { opacity: 1; } }
@keyframes particle-rise {
    0% { transform: translateY(50px) scale(0); opacity: 0; }
    50% { opacity: 1; }
    100% { transform: translateY(-50px) scale(1); opacity: 0; }
}

.font-mono { font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important; }
.typing-effect { overflow: hidden; border-right: 2px solid #FFD700; white-space: nowrap; animation: typing 3s steps(30, end) infinite; display: inline-block; }
@keyframes typing { 0% { width: 0 } 50% { width: 100% } 100% { width: 100% } }
</style>
