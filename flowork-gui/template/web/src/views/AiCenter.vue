//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\AiCenter.vue total lines 90 
//#######################################################################

<template>
  <div class="gemini-layout fill-height d-flex flex-column">

    <AiSidebar v-model="drawer" />

    <AiAgentPanel v-if="aiCenterStore.aiState.mode === 'agent'" v-model="agentDrawer" @open-config="openToolConfig" />
    <AiCouncilPanel v-if="aiCenterStore.aiState.mode === 'council'" v-model="councilDrawer" />

    <AiHeader
      @toggle-sidebar="drawer = !drawer"
      @toggle-right="toggleRightDrawer"
      @open-system-prompt="dialogsRef.openSystemPrompt()"
    />

    <AiChatWindow />

    <AiDialogs ref="dialogsRef" />

  </div>
</template>

<script setup>
import { ref, reactive, provide, onMounted } from 'vue';
import AiSidebar from '@/components/ai/AiSidebar.vue';
import AiHeader from '@/components/ai/AiHeader.vue';
import AiChatWindow from '@/components/ai/AiChatWindow.vue';
import AiAgentPanel from '@/components/ai/AiAgentPanel.vue';
import AiCouncilPanel from '@/components/ai/AiCouncilPanel.vue';
import AiDialogs from '@/components/ai/AiDialogs.vue';

import { useAiCenterStore } from '@/store/aiCenter';
import { storeToRefs } from 'pinia';

const aiCenterStore = useAiCenterStore();
const { aiProviders, sessions, currentSessionId } = storeToRefs(aiCenterStore);

const drawer = ref(true);
const agentDrawer = ref(true);
const councilDrawer = ref(true);
const dialogsRef = ref(null);

/*
const aiState = reactive({
    mode: 'chat', // chat, agent, council
    selectedEndpointId: null,
    selectedJudgeId: null,
    selectedPersona: null,
    selectedPreset: null,
    selectedCouncilMembers: []
});

provide('aiState', aiState);
*/

provide('aiState', aiCenterStore.aiState);

function toggleRightDrawer() {
    if (aiCenterStore.aiState.mode === 'agent') agentDrawer.value = !agentDrawer.value;
    if (aiCenterStore.aiState.mode === 'council') councilDrawer.value = !councilDrawer.value;
}

function openToolConfig(tool) {
    dialogsRef.value?.openToolConfig(tool);
}

onMounted(async () => {
    await aiCenterStore.fetchAiStatus();
    await aiCenterStore.loadHistory();

    /*
    if (aiProviders.value.length > 0 && !aiState.selectedEndpointId) {
        aiState.selectedEndpointId = aiProviders.value[0].id;
    }
    */

    if (!currentSessionId.value && sessions.value.length > 0) {
        aiCenterStore.switchSession(sessions.value[0].id);
    }
});
</script>

<style scoped>
.gemini-layout { background-color: #000; color: #e3e3e3; height: 100vh; overflow: hidden; }
</style>
