//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\PropertiesPanel.vue total lines 196
//#######################################################################

<template>
  <div class="properties-container">
    <div v-if="!selectedNode" class="properties-empty-state">
      <v-icon icon="mdi-cursor-default-click-outline" size="48" class="mb-4 text-grey"></v-icon>
      <div class="text-h6 text-grey">Select a Node</div>
      <div class="text-body-2 text-grey-lighten-1">Click on a node in the canvas to view and edit its properties here.</div>
    </div>

    <div v-else class="properties-form">
      <div class="node-title">
        <v-icon icon="mdi-cog" class="node-icon-title mr-3"></v-icon>
        {{ activeNodeName }}
        <v-spacer></v-spacer>
        <v-btn
          :icon="uiStore.isPropertiesPanelPinned ? 'mdi-pin' : 'mdi-pin-outline'"
          :color="uiStore.isPropertiesPanelPinned ? 'cyan' : 'grey'"
          variant="text"
          size="small"
          @click="uiStore.togglePropertiesPanelPin"
        ></v-btn>
        <v-btn icon="mdi-close" variant="text" size="small" @click="workflowStore.clearSelectedNode"></v-btn>
      </div>

      <div class="node-description">
        {{ activeNodeDescription }}
      </div>

      <v-divider class="my-4"></v-divider>

      <div class="config-section">
        <div class="config-title">CONFIGURATION</div>

        <DynamicFormRenderer
            v-if="activeSchema.length > 0"
            :schema="activeSchema"
            :model-value="nodeConfigValues"
            :ai-providers="aiProviders"
            :prompts="prompts"
            @update:modelValue="handleDynamicFormUpdate"
        />

        <div v-else class="text-center text-caption text-grey mt-4">
            <v-icon icon="mdi-information-outline" class="mb-1"></v-icon><br>
            This node has no configurable properties.
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useWorkflowStore } from '@/store/workflow';
import { useLocaleStore } from '@/store/locale';
import { useUiStore } from '@/store/ui';
import { useComponentStore } from '@/store/components';
// [KUDETA] Commented out AiCenter store import
// import { useAiCenterStore } from '@/store/aiCenter';
import { usePromptsStore } from '@/store/prompts';
import DynamicFormRenderer from '@/components/DynamicFormRenderer.vue';

const workflowStore = useWorkflowStore();
const localeStore = useLocaleStore();
const uiStore = useUiStore();
const componentStore = useComponentStore();
// [KUDETA] Commented out AiCenter store init
// const aiStore = useAiCenterStore(); // For AI Provider Select
const promptsStore = usePromptsStore(); // For Prompt Select

const { selectedNode } = storeToRefs(workflowStore);
const { loc } = storeToRefs(localeStore);

// [KUDETA] Empty array for aiProviders since store is removed
const aiProviders = computed(() => []);
const prompts = computed(() => promptsStore.prompts || []);

const appManifest = computed(() => {
    if (!selectedNode.value?.data?.moduleId) return {};
    const component = componentStore.findComponentById(selectedNode.value.data.moduleId);
    return component?.manifest || {};
});

const activeNodeDefinition = computed(() => {
    const manifest = appManifest.value;
    if (!manifest) return null;

    const fullType = selectedNode.value?.data?.type || '';
    const nodeIdSuffix = fullType.split('.').pop();

    if (manifest.nodes && Array.isArray(manifest.nodes)) {
        const foundNode = manifest.nodes.find(n => n.id === nodeIdSuffix);
        if (foundNode) return foundNode;
    }

    return manifest;
});

const activeSchema = computed(() => {
    const def = activeNodeDefinition.value;
    if (!def) return [];

    if (def.inputs && Array.isArray(def.inputs)) {
        return def.inputs;
    }

    return def.ui_schema || def.properties || [];
});

const activeNodeName = computed(() => {
    const def = activeNodeDefinition.value;
    return loc(def?.name || selectedNode.value?.data?.label || 'Node');
});

const activeNodeDescription = computed(() => {
    const def = activeNodeDefinition.value;
    return loc(def?.description || 'No description available.');
});

const nodeConfigValues = computed(() => {
  if (selectedNode.value && !selectedNode.value.data.config_values) {
    selectedNode.value.data.config_values = {};
  }
  return selectedNode.value?.data?.config_values || {};
});

function updateConfig(key, value) {
  if (selectedNode.value) {
    workflowStore.updateNodeConfig({
      nodeId: selectedNode.value.id,
      key,
      value
    });
  }
}

function handleDynamicFormUpdate(newConfig) {
  if (!selectedNode.value) return;

  Object.keys(newConfig).forEach(key => {
    if (JSON.stringify(nodeConfigValues.value[key]) !== JSON.stringify(newConfig[key])) {
      updateConfig(key, newConfig[key]);
    }
  });
}
</script>

<style scoped>
.properties-container {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  background-color: var(--bg-surface-1); /* Ensure contrast */
}
.properties-empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}
.node-title {
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--neon-cyan);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}
.node-description {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  padding-bottom: 8px;
}
.config-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--text-secondary);
    margin-bottom: 16px;
}
.node-icon-title {
    width: 24px;
    height: 24px;
    color: var(--neon-cyan);
}
</style>