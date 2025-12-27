//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai\AiAgentPanel.vue total lines 123 
//#######################################################################

<template>
    <v-navigation-drawer v-model="drawer" location="right" color="#050505" width="340" class="border-l-thin" floating>
        <div class="d-flex flex-column fill-height">
            <div class="pa-4 border-b-thin bg-grey-darken-4 flex-shrink-0">
                <div class="d-flex align-center justify-space-between mb-3">
                    <span class="text-subtitle-2 font-weight-bold text-gold-luxury orbitron-font">AGENT COMMAND</span>
                    <v-icon icon="mdi-robot-industrial" color="#D4AF37" size="small"></v-icon>
                </div>
                <div class="mb-3">
                    <div class="text-caption text-grey-darken-1 font-weight-bold mb-1">WORKFLOW PRESET</div>
                    <v-select v-model="aiState.selectedPreset" :items="presets" item-title="name" item-value="id" placeholder="No Preset Selected" variant="outlined" density="compact" bg-color="#1a1a1a" hide-details class="agent-select text-caption" :loading="isLoadingPresets" return-object clearable>
                        <template v-slot:prepend-inner><v-icon icon="mdi-sitemap" size="small" color="#D4AF37"></v-icon></template>
                    </v-select>
                </div>
                <div v-if="aiState.selectedPersona" class="rounded pa-2 bg-gold-dim border-gold-subtle">
                    <div class="d-flex align-center">
                        <v-icon icon="mdi-account-tie" size="small" color="#D4AF37" class="mr-2"></v-icon>
                        <div>
                            <div class="text-caption font-weight-bold text-gold-luxury">{{ aiState.selectedPersona.name }}</div>
                            <div class="text-caption text-grey-lighten-1 text-truncate" style="font-size: 10px; max-width: 220px;">{{ aiState.selectedPersona.content }}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex-grow-1 d-flex flex-column" style="min-height: 0; flex-basis: 55%;">
                <div class="px-4 pt-4 pb-2">
                    <div class="d-flex justify-space-between align-center mb-2">
                        <div class="text-caption font-weight-bold text-grey-darken-1">AVAILABLE TOOLS</div>
                        <div class="d-flex align-center">
                             <v-progress-circular v-if="isStoreLoading" indeterminate size="12" width="2" color="#D4AF37" class="mr-2"></v-progress-circular>
                             <v-chip size="x-small" color="#D4AF37" variant="text">{{ filteredTools.length }} Items</v-chip>
                        </div>
                    </div>
                    <v-text-field v-model="toolSearch" placeholder="Search tools..." variant="outlined" density="compact" bg-color="#1a1a1a" hide-details class="tool-search mb-2 text-caption">
                        <template v-slot:prepend-inner><v-icon icon="mdi-magnify" size="small" color="grey"></v-icon></template>
                    </v-text-field>
                </div>

                <div class="tools-scroll-area px-2 pb-2" style="overflow-y: auto;">
                    <div v-if="filteredTools.length === 0" class="text-center text-caption text-grey py-4">{{ isStoreLoading ? 'Loading tools...' : 'No tools found.' }}</div>
                    <div v-for="tool in filteredTools" :key="tool.id" class="tool-item rounded-lg mb-2 pa-2 border-thin bg-grey-darken-4 cursor-pointer" @click="$emit('open-config', tool)">
                        <div class="d-flex align-center">
                            <div class="tool-icon rounded bg-grey-darken-3 d-flex align-center justify-center mr-3 border-gold-thin" style="width: 36px; height: 36px;">
                                <v-icon icon="mdi-hammer-wrench" color="#D4AF37" size="small"></v-icon>
                            </div>
                            <div class="flex-grow-1" style="min-width: 0;">
                                <div class="d-flex align-center">
                                    <div class="text-caption font-weight-bold text-grey-lighten-1 text-truncate mr-1">{{ tool.manifest?.name || tool.name }}</div>
                                </div>
                                <div class="text-caption text-grey-darken-1 text-truncate" style="font-size: 10px;">{{ tool.manifest?.description || tool.description || 'Click to configure' }}</div>
                            </div>
                            <div class="d-flex align-center">
                                <v-icon icon="mdi-cog" size="x-small" color="grey" class="mr-2"></v-icon>
                                <template v-if="tool.is_installed">
                                    <v-btn icon size="x-small" variant="text" color="red-accent-2" @click.stop="handleUninstall(tool)"><v-icon icon="mdi-delete-outline" size="small"></v-icon></v-btn>
                                </template>
                                <template v-else>
                                    <v-btn size="small" variant="tonal" color="#D4AF37" class="text-caption px-1" style="height: 24px;" @click.stop="handleInstall(tool)">Get</v-btn>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </v-navigation-drawer>
</template>

<script setup>
import { ref, computed, inject, onMounted } from 'vue';
import { useComponentStore } from '@/store/components';
import { storeToRefs } from 'pinia';
import api from '@/api';

const props = defineProps(['modelValue']);
const emit = defineEmits(['update:modelValue', 'open-config']);

const aiState = inject('aiState');
const componentStore = useComponentStore();
const { favoriteComponents, isLoading: isStoreLoading } = storeToRefs(componentStore);

const drawer = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
});

const toolSearch = ref('');
const presets = ref([]);
const isLoadingPresets = ref(false);

const filteredTools = computed(() => {
    let items = componentStore.tools.items.map(t => ({...t, category: 'tool'}));
    if (toolSearch.value) {
        const q = toolSearch.value.toLowerCase();
        items = items.filter(t => (t.name && t.name.toLowerCase().includes(q)) || (t.description && t.description.toLowerCase().includes(q)));
    }
    return items;
});

function handleInstall(tool) { componentStore.installComponent('tools', tool.id); }
function handleUninstall(tool) { componentStore.uninstallComponent('tools', tool.id); }

onMounted(async () => {
    isLoadingPresets.value = true;
    try {
        const response = await api.get('/presets');
        presets.value = response.data || [];
    } catch { presets.value = []; } finally { isLoadingPresets.value = false; }
});
</script>

<style scoped>
.tool-item:hover { background-color: #252525 !important; }
.border-gold-thin { border: 1px solid rgba(212, 175, 55, 0.3); }
.text-gold-luxury { color: #D4AF37 !important; }
</style>
