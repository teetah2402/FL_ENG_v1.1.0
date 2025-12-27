//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai-trainer\BattleArena.vue total lines 130 
//#######################################################################

<template>
  <div class="d-flex flex-column fill-height pa-4">
    <div class="d-flex gap-4 mb-4">
        <v-select
            v-model="sparringConfig.base_model"
            :items="textModelsOnly"
            item-title="name"
            item-value="id"
            label="Fighter 1: Base Model"
            variant="outlined"
            density="compact"
            class="gold-input flex-grow-1 font-mono"
            color="#FFD700"
        ></v-select>
        <v-select
            v-model="sparringConfig.adapter_model"
            :items="availableAdapters"
            item-title="new_model_name"
            item-value="new_model_name"
            label="Fighter 2: Trained Adapter"
            variant="outlined"
            density="compact"
            class="gold-input flex-grow-1 font-mono"
            color="#FFD700"
        ></v-select>
    </div>

    <div class="d-flex flex-grow-1 gap-4 overflow-hidden mb-4 position-relative">
        <div v-if="isSparring" class="battle-overlay d-flex flex-column align-center justify-center">
            <h1 class="text-h2 font-weight-black text-gold glitch-text mb-4">NEURAL BATTLE</h1>
            <div class="mt-6 text-center">
                <div class="text-caption text-grey font-mono bg-black px-4 py-2 border-gold" style="min-width: 300px;">
                    <span class="text-gold">>></span> {{ currentStatusLog }}<br>
                    <span class="typing-effect-fast">>> INITIALIZING NEURAL PATHWAYS...</span>
                </div>
            </div>
        </div>

        <v-card class="gold-panel flex-grow-1 d-flex flex-column w-50">
            <div class="pa-4 flex-grow-1 overflow-y-auto font-mono text-grey-lighten-1">
                <div v-if="sparringResult.base_reply" style="white-space: pre-wrap;">{{ sparringResult.base_reply }}</div>
                <div v-else class="text-center mt-10">Waiting for clash...</div>
            </div>
        </v-card>

        <v-card class="gold-panel flex-grow-1 d-flex flex-column w-50 border-gold">
            <div class="pa-4 flex-grow-1 overflow-y-auto font-mono text-white">
                <div v-if="sparringResult.adapter_reply" style="white-space: pre-wrap;">{{ sparringResult.adapter_reply }}</div>
                <div v-else class="text-center mt-10">Waiting for clash...</div>
            </div>
        </v-card>
    </div>

    <div class="d-flex align-end gap-2">
        <v-textarea
            v-model="sparringPrompt"
            rows="2"
            label="Enter Battle Prompt"
            variant="outlined"
            class="gold-input font-mono"
            color="#FFD700"
            @keydown.ctrl.enter="handleSparring"
        ></v-textarea>
        <v-btn height="56" color="#FFD700" class="text-black font-weight-bold" @click="handleSparring" :loading="isSparring">FIGHT!</v-btn>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useTrainingStore } from '@/store/training';
import { storeToRefs } from 'pinia';

const trainingStore = useTrainingStore();
const { localModels: availableBaseModels, trainingJobs } = storeToRefs(trainingStore);
const sparringConfig = ref({ base_model: null, adapter_model: null });
const sparringPrompt = ref("");
const isSparring = ref(false);
const sparringResult = ref({ base_reply: "", adapter_reply: "" });
const currentStatusLog = ref("READY FOR COMBAT");

const textModelsOnly = computed(() => availableBaseModels.value);
const availableAdapters = computed(() => trainingJobs.value.filter(j => j.status === 'COMPLETED'));

function handleStatusUpdate(event) {
    if (event.detail && event.detail.message) {
        currentStatusLog.value = event.detail.message.toUpperCase();
    }
}

onMounted(() => {
    trainingStore.fetchLocalModels();
    trainingStore.fetchTrainingJobs();
    window.addEventListener('COLOSSEUM_LOG_UPDATE', handleStatusUpdate);
});

onUnmounted(() => {
    window.removeEventListener('COLOSSEUM_LOG_UPDATE', handleStatusUpdate);
});

async function handleSparring() {
    if (!sparringPrompt.value || isSparring.value) return;
    isSparring.value = true;
    currentStatusLog.value = "ARENA INITIALIZING...";
    sparringResult.value = { base_reply: "", adapter_reply: "" };

    const result = await trainingStore.runSparringMatch({
        base_model_id: sparringConfig.value.base_model,
        adapter_model_id: sparringConfig.value.adapter_model,
        prompt: sparringPrompt.value
    });

    if (result && !result.error) sparringResult.value = result;
    isSparring.value = false;
}
</script>

<style scoped>
.gold-panel { background: #050505; border: 1px solid rgba(255, 215, 0, 0.1); }
.border-gold { border: 1px solid #FFD700 !important; }
.battle-overlay { position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.9); z-index:100; }
.typing-effect-fast { font-size: 10px; color: #888; animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0; } }
</style>
