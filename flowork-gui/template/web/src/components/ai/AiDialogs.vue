//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai\AiDialogs.vue total lines 118 
//#######################################################################

<template>
    <div>
        <v-dialog v-model="showSystemPrompt" max-width="500">
            <v-card color="#1e1f20" class="border-thin">
                <v-card-title class="text-gold-luxury font-weight-bold">System Rules</v-card-title>
                <v-card-text>
                    <div class="text-caption text-grey mb-2">Instructions given here will be remembered and applied to every conversation.</div>
                    <v-textarea v-model="tempSystemPrompt" label="Global System Prompt" variant="outlined" rows="5" bg-color="#2a2b2d" hide-details color="#D4AF37"></v-textarea>
                </v-card-text>
                <v-card-actions class="justify-end">
                    <v-btn variant="text" @click="showSystemPrompt = false">Cancel</v-btn>
                    <v-btn color="#D4AF37" variant="tonal" @click="saveSystemPrompt">Save Rules</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <v-dialog v-model="showToolConfig" max-width="500">
            <v-card v-if="configuringTool" color="#1e1f20" class="border-thin">
                <v-card-title class="d-flex align-center">
                    <v-icon icon="mdi-hammer-wrench" color="#D4AF37" size="small" class="mr-2"></v-icon>
                    <span class="text-h6 text-grey-lighten-1">{{ configuringTool.manifest?.name || configuringTool.name }}</span>
                </v-card-title>
                <v-card-text class="py-4" style="max-height: 550px; overflow-y: auto;">
                    <div v-if="!configuringTool.manifest?.ui_schema?.length" class="text-center text-grey text-caption">
                        No configuration available for this tool.
                    </div>
                    <div v-else>
                        <DynamicFormRenderer
                            :schema="configuringTool.manifest.ui_schema"
                            v-model="tempToolConfig"
                            :ai-providers="aiProviders"
                            :prompts="prompts"
                        />
                    </div>
                </v-card-text>
                <v-card-actions class="justify-end bg-grey-darken-4">
                    <v-btn variant="text" @click="showToolConfig = false">Close</v-btn>
                    <v-btn color="#D4AF37" variant="tonal" @click="saveToolConfig">Save Config</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script setup>
import { ref, watch, defineExpose } from 'vue';
import { useAiCenterStore } from '@/store/aiCenter';
import { useUiStore } from '@/store/ui';
import { usePromptsStore } from '@/store/prompts';
import { storeToRefs } from 'pinia';

import DynamicFormRenderer from '@/components/DynamicFormRenderer.vue';

const aiCenterStore = useAiCenterStore();
const promptStore = usePromptsStore();
const uiStore = useUiStore();

const { aiProviders } = storeToRefs(aiCenterStore);
const { prompts } = storeToRefs(promptStore);

const showSystemPrompt = ref(false);
const tempSystemPrompt = ref('');
const showToolConfig = ref(false);
const configuringTool = ref(null);
const tempToolConfig = ref({});

watch(showSystemPrompt, (val) => {
    if (val) tempSystemPrompt.value = aiCenterStore.systemInstruction;
});

async function openSystemPrompt() {
    showSystemPrompt.value = true;
}

async function openToolConfig(tool) {
    configuringTool.value = tool;

    try {
        await aiCenterStore.fetchAiStatus();
        await promptStore.fetchPrompts();
    } catch (e) {
        console.warn("Error pre-fetching tool config data:", e);
    }

    const existing = aiCenterStore.toolConfigs[tool.id] || {};
    const defaults = {};
    if (tool.manifest?.ui_schema) {
        tool.manifest.ui_schema.forEach(f => {
            if(f.default !== undefined) defaults[f.id] = f.default;
            if(f.type === 'list' && !defaults[f.id]) defaults[f.id] = [];
        });
    }
    tempToolConfig.value = { ...defaults, ...existing };
    showToolConfig.value = true;
}

function saveToolConfig() {
    if (configuringTool.value) {
        aiCenterStore.setToolConfig(configuringTool.value.id, { ...tempToolConfig.value });
        uiStore.showNotification({ text: 'Config saved', color: 'success' });
        showToolConfig.value = false;
    }
}

function saveSystemPrompt() {
    aiCenterStore.setSystemInstruction(tempSystemPrompt.value);
    showSystemPrompt.value = false;
    uiStore.showNotification({ text: 'Rules updated', color: 'success' });
}

defineExpose({ openSystemPrompt, openToolConfig });
</script>
