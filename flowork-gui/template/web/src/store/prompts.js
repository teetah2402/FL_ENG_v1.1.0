//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\prompts.js total lines 134 
//#######################################################################

import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/api';
import { useUiStore } from './ui';
import { useEngineStore } from './engines';

export const usePromptsStore = defineStore('prompts', () => {
    const prompts = ref([]);
    const selectedPrompt = ref(null);
    const isLoading = ref(false);
    const error = ref(null);

    function getApiConfig() {
        const engineStore = useEngineStore();
        const activeEngineId = engineStore.activeEngine?.id || engineStore.engines[0]?.id; // Fallback

        if (!activeEngineId) {
            console.warn("[PromptStore] No active engine found!");
            return {};
        }

        return {
            headers: {
                'X-Flowork-Engine-ID': activeEngineId
            }
        };
    }

    function selectPrompt(prompt) {
        selectedPrompt.value = { ...prompt };
    }

    function clearSelection() {
        selectedPrompt.value = null;
    }

    async function fetchPrompts() {
        isLoading.value = true;
        error.value = null;
        try {
            console.log("[PromptStore] Requesting prompts via HTTP API...");
            const response = await api.get('/prompts', getApiConfig());
            prompts.value = response.data;
        } catch (e) {
            error.value = e.message || 'Failed to request prompts.';
            console.error("[PromptStore] Fetch Error:", e);
            if (e.response && e.response.status === 503) {
                useUiStore().showNotification({ text: 'Gateway 503: Engine not reachable. Check connection.', color: 'warning' });
            }
        } finally {
            isLoading.value = false;
        }
    }

    async function savePrompt(promptData) {
        isLoading.value = true;
        error.value = null;
        const uiStore = useUiStore();
        const isUpdate = !!promptData.id;
        const config = getApiConfig();

        try {
            console.log(`[PromptStore] ${isUpdate ? 'Updating' : 'Creating'} prompt...`, promptData);

            let response;
            if (isUpdate) {
                response = await api.put(`/prompts/${promptData.id}`, promptData, config);

                const index = prompts.value.findIndex(p => p.id === promptData.id);
                if (index !== -1) prompts.value[index] = promptData;
            } else {
                response = await api.post('/prompts', promptData, config);

                if (response.data) {
                    prompts.value.push(response.data);
                    selectedPrompt.value = response.data;
                }
            }

            uiStore.showNotification({ text: `Prompt ${isUpdate ? 'updated' : 'created'} successfully.`, color: 'success' });
            await fetchPrompts();
            return true;
        } catch (e) {
            error.value = e.message || `Failed to ${isUpdate ? 'update' : 'create'} prompt.`;
            uiStore.showNotification({ text: error.value, color: 'error' });
            console.error("[PromptStore] Save Error:", e);
            return false;
        } finally {
             isLoading.value = false;
        }
    }

    async function removePrompt(promptId) {
        isLoading.value = true;
        error.value = null;
        const uiStore = useUiStore();
        const config = getApiConfig();

        try {
            console.log(`[PromptStore] Deleting prompt ${promptId}...`);
            await api.delete(`/prompts/${promptId}`, config);

            prompts.value = prompts.value.filter(p => p.id !== promptId);
            if (selectedPrompt.value && selectedPrompt.value.id === promptId) {
                selectedPrompt.value = null;
            }

            uiStore.showNotification({ text: 'Prompt deleted successfully.', color: 'success' });
        } catch (e) {
            error.value = e.message || 'Failed to delete prompt.';
            uiStore.showNotification({ text: error.value, color: 'error' });
        } finally {
            isLoading.value = false;
        }
    }

    return {
        prompts,
        selectedPrompt,
        isLoading,
        error,
        fetchPrompts,
        savePrompt,
        removePrompt,
        selectPrompt,
        clearSelection
    };
});
