//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai\AiCouncilPanel.vue total lines 120 
//#######################################################################

<template>
    <v-navigation-drawer v-model="drawer" location="right" color="#050505" width="340" class="border-l-thin" floating>
        <div class="d-flex flex-column fill-height">
            <div class="pa-4 border-b-thin bg-grey-darken-4 flex-shrink-0">
                <div class="d-flex align-center justify-space-between">
                    <span class="text-subtitle-2 font-weight-bold text-gold-luxury orbitron-font">COUNCIL CHAMBER</span>
                    <v-icon icon="mdi-gavel" color="#D4AF37" size="small"></v-icon>
                </div>
                <div class="text-caption text-grey-darken-1 mt-1">Select participating models for debate.</div>
            </div>

            <div class="flex-grow-1 d-flex flex-column" style="min-height: 0; flex-basis: 55%;">
                <div class="px-4 pt-3 pb-2">
                     <div class="d-flex justify-space-between align-center mb-2">
                        <div class="text-caption font-weight-bold text-grey-darken-1">COUNCIL MEMBERS</div>
                        <v-chip size="x-small" color="#D4AF37" variant="text">{{ aiState.selectedCouncilMembers.length }} Selected</v-chip>
                    </div>
                </div>

                <div class="council-scroll-area px-2 pb-2" style="overflow-y: auto;">
                    <div v-if="councilList.length === 0" class="text-center text-caption text-grey py-4">No AI Models Found.</div>

                    <v-list bg-color="transparent" density="compact">
                        <v-list-item v-for="model in councilList" :key="model.id" class="mb-1 rounded-lg border-thin bg-grey-darken-4 council-item">
                            <template v-slot:prepend>
                                <v-checkbox-btn v-model="aiState.selectedCouncilMembers" :value="model.id" density="compact" color="#D4AF37"></v-checkbox-btn>
                            </template>
                            <v-list-item-title class="text-caption font-weight-bold text-grey-lighten-2">{{ model.name }}</v-list-item-title>
                            <v-list-item-subtitle class="text-caption text-grey-darken-1" style="font-size: 9px !important;">
                                {{ model.type === 'local' ? 'Local Engine' : 'Cloud Provider' }}
                            </v-list-item-subtitle>
                            <template v-slot:append>
                                <v-icon :icon="getProviderIcon(model.type)" size="small" color="grey-darken-2"></v-icon>
                            </template>
                        </v-list-item>
                    </v-list>
                </div>
            </div>

            <v-divider class="border-opacity-10"></v-divider>

            <div class="flex-grow-1 d-flex flex-column bg-black" style="min-height: 0; flex-basis: 45%;">
                <div class="px-4 py-2 border-b-thin border-opacity-10 d-flex justify-space-between align-center bg-grey-darken-4">
                    <div class="d-flex align-center">
                        <span class="text-caption font-weight-bold text-grey-darken-1 mr-2">MEETING MINUTES</span>
                        <v-chip size="x-small" color="#D4AF37" variant="text" v-if="aiCenterStore.isGenerating" class="pulsing-dot">● DEBATING</v-chip>
                    </div>
                     <v-btn icon size="x-small" variant="text" color="grey" @click="clearLogs">
                        <v-icon icon="mdi-trash-can-outline" size="small"></v-icon>
                    </v-btn>
                </div>
                 <div class="council-log-container flex-grow-1 pa-3 font-mono text-caption text-grey-lighten-2" style="overflow-y: auto; font-size: 10px; line-height: 1.4;">
                    <div v-if="councilLogs.length === 0" class="text-grey-darken-3 text-center mt-4 font-italic">Council is in recess.</div>
                    <div v-for="(log, i) in councilLogs" :key="i" class="mb-2 d-flex align-start">
                         <span class="text-gold-dim mr-2 text-caption font-weight-bold" style="min-width: 60px;">[{{ log.speaker }}]</span>
                         <span class="text-grey-lighten-1">{{ log.message }}</span>
                    </div>
                </div>
            </div>
        </div>
    </v-navigation-drawer>
</template>

<script setup>
import { ref, computed, inject } from 'vue';
import { useAiCenterStore } from '@/store/aiCenter';
import { storeToRefs } from 'pinia';

const props = defineProps(['modelValue']);
const emit = defineEmits(['update:modelValue']);

const aiState = inject('aiState');
const aiCenterStore = useAiCenterStore();
const { aiProviders } = storeToRefs(aiCenterStore);

const drawer = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
});

const councilLogs = ref([]);

function clearLogs() {
    councilLogs.value = [];
}

const defaultModels = [
    { id: 'gemini-pro', name: 'Google Gemini Pro', type: 'provider' },
    { id: 'gpt-4', name: 'OpenAI ChatGPT-4', type: 'provider' },
    { id: 'claude-3', name: 'Anthropic Claude 3', type: 'provider' }
];

const councilList = computed(() => {
    if (!aiProviders.value || aiProviders.value.length === 0) {
        return defaultModels;
    }
    return aiProviders.value;
});

function getProviderIcon(type) {
    if (type === 'local') return 'mdi-server-network';
    return 'mdi-brain';
}
</script>

<style scoped>
.council-item:hover { background-color: #252525 !important; }
.border-l-thin { border-left: 1px solid rgba(255,255,255,0.1); }
.text-gold-luxury { color: #D4AF37 !important; }
.text-gold-dim { color: rgba(212, 175, 55, 0.7) !important; }
.orbitron-font { font-family: 'Orbitron', sans-serif; letter-spacing: 1px; }
.pulsing-dot { animation: pulseGreen 2s infinite; }
@keyframes pulseGreen { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
