//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai\AiHeader.vue total lines 176 
//#######################################################################

<template>
    <div class="header-bar px-4 py-3 d-flex align-center justify-space-between bg-glass-header flex-grow-0 flex-shrink-0">
        <div class="d-flex align-center">
            <v-app-bar-nav-icon variant="text" color="grey-lighten-1" @click="$emit('toggle-sidebar')"></v-app-bar-nav-icon>
            <div class="d-flex align-center cursor-pointer ml-2 hover-opacity" @click="$router.push('/')">
                <span class="font-weight-bold text-h6 text-grey-lighten-1 orbitron-font">Flowork <span class="text-gold-luxury">AI</span></span>
                <v-chip size="x-small" color="#D4AF37" variant="outlined" class="ml-2 mt-1 font-mono d-none d-sm-flex">
                    {{ aiState.mode === 'council' ? 'COUNCIL' : (aiState.mode === 'agent' ? 'AGENT' : 'BETA') }}
                </v-chip>
            </div>
        </div>

        <div class="d-flex align-center gap-4">
            <v-btn size="small" variant="text" color="grey-lighten-1" class="text-none" @click="$emit('open-system-prompt')">
                <v-icon start icon="mdi-card-text-outline" color="#D4AF37"></v-icon> System Rules
            </v-btn>

            <div class="d-flex align-center bg-grey-darken-4 rounded-pill px-1 border-thin">
                <v-btn size="small" rounded="pill" :color="aiState.mode === 'chat' ? '#2a2b2d' : 'transparent'" variant="flat" class="text-caption" height="32" @click="setMode('chat')">
                    <v-icon start icon="mdi-chat-outline" size="small" :color="aiState.mode === 'chat' ? '#D4AF37' : 'grey'"></v-icon> Chat
                </v-btn>
                <v-btn size="small" rounded="pill" :color="aiState.mode === 'agent' ? '#2a2b2d' : 'transparent'" variant="flat" class="text-caption" height="32" @click="setMode('agent')">
                    <v-icon start icon="mdi-robot" size="small" :color="aiState.mode === 'agent' ? '#D4AF37' : 'grey'"></v-icon> Agent
                </v-btn>
                <v-btn size="small" rounded="pill" :color="aiState.mode === 'council' ? '#2a2b2d' : 'transparent'" variant="flat" class="text-caption" height="32" @click="setMode('council')">
                    <v-icon start icon="mdi-gavel" size="small" :color="aiState.mode === 'council' ? '#D4AF37' : 'grey'"></v-icon> Council
                </v-btn>
            </div>

            <div class="d-flex align-center" v-if="aiState.mode === 'agent'">
                 <v-menu v-model="isPersonaMenuOpen" location="bottom" transition="slide-y-transition" offset="8" :close-on-content-click="true">
                    <template v-slot:activator="{ props }">
                        <div v-bind="props" class="model-selector-btn d-flex align-center px-3 py-2 rounded-lg cursor-pointer transition-all ml-2 border-amber-thin">
                            <v-icon icon="mdi-account-box-outline" color="#D4AF37" size="small" class="mr-2"></v-icon>
                            <span class="text-grey-lighten-1 font-weight-bold mr-2 text-body-2 text-truncate" style="max-width: 150px;">
                                {{ aiState.selectedPersona ? aiState.selectedPersona.name : 'Select Persona' }}
                            </span>
                            <v-icon :icon="isPersonaMenuOpen ? 'mdi-chevron-up' : 'mdi-chevron-down'" color="grey-darken-1" size="small"></v-icon>
                        </div>
                    </template>
                    <v-list bg-color="#1e1f20" density="compact" class="border-thin rounded-lg nav-menu-list mt-2" width="250">
                        <v-list-item value="default" @click="selectPersona(null)" class="mb-1 rounded mx-2" variant="text">
                            <template v-slot:prepend><v-icon icon="mdi-robot-outline" size="small" class="mr-2"></v-icon></template>
                            <v-list-item-title class="font-mono text-caption">Default Assistant</v-list-item-title>
                        </v-list-item>
                        <v-list-item v-for="p in personas" :key="p.id" :value="p.id" @click="selectPersona(p)" class="mb-1 rounded mx-2" variant="text">
                            <template v-slot:prepend><v-icon icon="mdi-account-tie" size="small" class="mr-2 text-gold-luxury"></v-icon></template>
                            <v-list-item-title class="font-mono text-caption">{{ p.name }}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
            </div>

            <div class="d-flex align-center flex-grow-1 justify-center ml-2" v-else-if="aiState.mode === 'council'">
                 <v-menu v-model="isJudgeMenuOpen" location="bottom" transition="slide-y-transition" offset="8" :close-on-content-click="true">
                    <template v-slot:activator="{ props }">
                        <div v-bind="props" class="model-selector-btn d-flex align-center px-3 py-2 rounded-lg cursor-pointer transition-all border-amber-thin">
                            <v-icon icon="mdi-scale-balance" color="#D4AF37" size="small" class="mr-2"></v-icon>
                            <span class="text-grey-lighten-1 font-weight-bold mr-2 text-body-2 text-truncate" style="max-width: 200px;">{{ getSelectedJudgeName() }}</span>
                            <v-chip size="x-small" color="#D4AF37" variant="outlined" class="mr-2 text-caption">PRESIDING JUDGE</v-chip>
                            <v-icon :icon="isJudgeMenuOpen ? 'mdi-chevron-up' : 'mdi-chevron-down'" color="grey-darken-1" size="small"></v-icon>
                        </div>
                    </template>
                    <v-list bg-color="#1e1f20" density="compact" class="border-thin rounded-lg nav-menu-list mt-2" width="300">
                        <v-list-item v-for="provider in aiProviders" :key="provider.id" :value="provider.id" @click="selectJudge(provider.id)" :active="aiState.selectedJudgeId === provider.id" active-color="#D4AF37" class="mb-1 rounded mx-2" variant="text">
                            <template v-slot:prepend><v-icon :icon="getProviderIcon(provider.type)" size="small" :color="provider.status === 'ready' ? 'green-accent-3' : 'grey'" class="mr-2"></v-icon></template>
                            <v-list-item-title class="font-mono text-caption font-weight-medium">{{ provider.name }}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
            </div>

            <div class="d-flex align-center flex-grow-1 justify-center ml-2" v-else>
                 <v-menu v-model="isModelMenuOpen" location="bottom" transition="slide-y-transition" offset="8" :close-on-content-click="true">
                    <template v-slot:activator="{ props }">
                        <div v-bind="props" class="model-selector-btn d-flex align-center px-3 py-2 rounded-lg cursor-pointer transition-all border-amber-thin">
                            <v-icon icon="mdi-shimmer" color="#D4AF37" size="small" class="mr-2"></v-icon>
                            <span class="text-grey-lighten-1 font-weight-bold mr-2 text-body-2 text-truncate" style="max-width: 200px;">{{ getSelectedModelName() }}</span>
                            <v-icon :icon="isModelMenuOpen ? 'mdi-chevron-up' : 'mdi-chevron-down'" color="grey-darken-1" size="small"></v-icon>
                        </div>
                    </template>
                    <v-list bg-color="#1e1f20" density="compact" class="border-thin rounded-lg nav-menu-list mt-2" width="300">
                        <div v-if="aiCenterStore.isLoadingStatus" class="pa-4 text-center"><v-progress-circular indeterminate size="20" width="2" color="#D4AF37"></v-progress-circular></div>
                        <template v-else>
                            <v-list-item v-for="provider in aiProviders" :key="provider.id" :value="provider.id" @click="selectModel(provider.id)" :active="aiState.selectedEndpointId === provider.id" active-color="#D4AF37" class="mb-1 rounded mx-2" variant="text">
                                <template v-slot:prepend><v-icon :icon="getProviderIcon(provider.type)" size="small" :color="provider.status === 'ready' ? 'green-accent-3' : 'grey'" class="mr-2"></v-icon></template>
                                <v-list-item-title class="font-mono text-caption font-weight-medium">{{ provider.name }}</v-list-item-title>
                                <template v-slot:append><v-icon v-if="aiState.selectedEndpointId === provider.id" icon="mdi-check" color="#D4AF37" size="small"></v-icon></template>
                            </v-list-item>
                        </template>
                        <v-divider class="my-2 border-opacity-10"></v-divider>
                        <v-list-item @click="refreshModels" class="mx-2 rounded text-center"><v-list-item-title class="text-caption text-gold-luxury">Refresh List</v-list-item-title></v-list-item>
                    </v-list>
                </v-menu>
            </div>
        </div>

        <div class="d-flex align-center">
             <v-btn v-if="aiState.mode === 'agent'" icon variant="text" color="grey" @click="$emit('toggle-right')"><v-icon icon="mdi-view-sidebar-outline"></v-icon></v-btn>
             <v-btn v-if="aiState.mode === 'council'" icon variant="text" color="grey" @click="$emit('toggle-right')"><v-icon icon="mdi-account-group"></v-icon></v-btn>
             <div v-if="aiState.mode === 'chat'" style="width: 48px;"></div>
        </div>
    </div>
</template>

<script setup>
import { ref, inject, computed } from 'vue';
import { useAiCenterStore } from '@/store/aiCenter';
import { storeToRefs } from 'pinia';

const aiState = inject('aiState');
const aiCenterStore = useAiCenterStore();
const { aiProviders } = storeToRefs(aiCenterStore);

const props = defineProps(['personas']);

const isPersonaMenuOpen = ref(false);
const isJudgeMenuOpen = ref(false);
const isModelMenuOpen = ref(false);

function setMode(mode) {
    aiState.mode = mode;
}

function selectPersona(persona) {
    aiState.selectedPersona = persona;
    isPersonaMenuOpen.value = false;
}

function selectJudge(id) {
    aiState.selectedJudgeId = id;
    isJudgeMenuOpen.value = false;
}

function selectModel(id) {
    aiState.selectedEndpointId = id;
    isModelMenuOpen.value = false;
}

function refreshModels() {
    aiCenterStore.fetchAiStatus();
}

function getSelectedModelName() {
    const m = aiProviders.value.find(p => p.id === aiState.selectedEndpointId);
    return m ? m.name : 'Select Model';
}

function getSelectedJudgeName() {
    const m = aiProviders.value.find(p => p.id === aiState.selectedJudgeId);
    return m ? m.name : 'Select Judge';
}

function getProviderIcon(type) {
    if (type === 'local') return 'mdi-server-network';
    if (type === 'provider') return 'mdi-cloud-outline';
    return 'mdi-brain';
}
</script>

<style scoped>
.orbitron-font { font-family: 'Orbitron', sans-serif; letter-spacing: 1px; }
.bg-glass-header { background-color: #050505; border-bottom: 1px solid rgba(212, 175, 55, 0.05); }
.text-gold-luxury { color: #D4AF37 !important; }
.model-selector-btn { transition: all 0.2s ease; }
.model-selector-btn:hover { background-color: #1e1f20; }
.border-amber-thin { border: 1px solid rgba(212, 175, 55, 0.15); }
.cursor-pointer { cursor: pointer; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
</style>
