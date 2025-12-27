//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\engines.js total lines 373
//#######################################################################

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from './auth';
import { useUiStore } from './ui';
import { useSocketStore } from './socket';

import api, {
    apiFetchEngines,
    apiRegisterEngine,
    apiDeleteEngine,
    apiFetchSharedEngines,
    apiGrantShare,
    apiRevokeShare,
    apiFetchEngineShares
} from '@/api';

import { useWorkflowStore } from './workflow';
import { useComponentStore } from './components';
import { useVariablesStore } from './variables';
import { useSettingsStore } from './settings';
import { usePromptsStore } from './prompts';
// [KUDETA] Removed training store import completely

export const useEngineStore = defineStore('engines', () => {
    const engines = ref([]);
    const sharedEngines = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    const selectedEngineId = ref(localStorage.getItem('flowork_active_engine_id'));

    const allAvailableEngines = computed(() => {
        const owned = engines.value.map(e => ({
            ...e,
            isOwner: true,
            owner: { username: useAuthStore().user?.username || 'You' }
        }));
        const shared = sharedEngines.value.map(e => ({
            ...e,
            isOwner: false
        }));
        return [...owned, ...shared].sort((a, b) => a.name.localeCompare(b.name));
    });

    const selectedEngine = computed(() => {
        return allAvailableEngines.value.find(e => e.id === selectedEngineId.value);
    });

    const hasOnlineEngine = computed(() => {
        return allAvailableEngines.value.some(e => e.status === 'online');
    });

    async function runModule(engineId, moduleId, payload) {
        isLoading.value = true;
        const uiStore = useUiStore();

        console.log(`[EngineStore] Executing Module ${moduleId} via Raw Workflow...`);

        try {
            if (!api) throw new Error("API Client not initialized");

            const rawWorkflowBody = {
                nodes: [
                    {
                        id: "direct_exec_node",
                        type: moduleId,
                        config: {},
                        position: { x: 0, y: 0 }
                    }
                ],
                connections: [],
                initial_payload: payload,
                start_node_id: "direct_exec_node",
                mode: "EXECUTE"
            };

            const response = await api.post('/workflow/execute_raw', rawWorkflowBody);

            if (response.data && response.data.error) throw new Error(response.data.error);

            console.log("[EngineStore] Raw Execution Queued. Job ID:", response.data.job_id);
            return response.data;

        } catch (e) {
            const errorMsg = e.response?.data?.error || e.message || 'Failed to execute module.';
            console.error('[EngineStore] Module execution failed:', errorMsg);
            uiStore.showNotification({ text: errorMsg, color: 'error' });
            throw e;
        } finally {
            isLoading.value = false;
        }
    }

    async function fetchEngines() {
        isLoading.value = true;
        error.value = null;
        console.log("[EngineStore] Fetching user's owned and shared engines...");
        try {
            const ownedResponseData = await apiFetchEngines();
            if (ownedResponseData.error) throw new Error(ownedResponseData.error);

            const currentStatusMap = {};
            [...engines.value, ...sharedEngines.value].forEach(e => {
                if (e.status) currentStatusMap[e.id] = e.status;
            });
            engines.value = ownedResponseData.map(engine => ({
                ...engine,
                status: currentStatusMap[engine.id] || engine.status || 'unknown',
                vitals: engine.vitals || null,
                isOwner: true
            }));
            console.log(`[EngineStore] Fetched ${engines.value.length} owned engines.`);

            await fetchSharedEngines();

            const currentSelectionValid = allAvailableEngines.value.some(e => e.id === selectedEngineId.value);
            if (!selectedEngineId.value || !currentSelectionValid) {
                console.log("[EngineStore] No valid engine selected or previous selection invalid. Checking for online candidates...");
                const firstOnline = allAvailableEngines.value.find(e => e.status === 'online');
                const firstEngine = allAvailableEngines.value[0];
                const defaultEngineId = firstOnline ? firstOnline.id : (firstEngine ? firstEngine.id : null);

                if (defaultEngineId) {
                    console.log(`[EngineStore] Auto-selecting default: ${defaultEngineId}`);
                    await setSelectedEngineId(defaultEngineId, true);
                }
            } else {
                console.log(`[EngineStore] Previous selection ${selectedEngineId.value} is valid.`);
            }

        } catch (e) {
            error.value = e.error || e.message || 'Failed to fetch engines.';
            console.error('[EngineStore] Error fetching engines:', error.value);
            if (engines.value.length === 0) {
                 engines.value = [];
                 sharedEngines.value = [];
                 setSelectedEngineId(null, false);
            }
        } finally {
            isLoading.value = false;
        }
    }

    async function fetchSharedEngines() {
        console.log("[EngineStore] Fetching shared engines...");
        try {
            const sharedData = await apiFetchSharedEngines();
            if (sharedData.error) throw new Error(sharedData.error);

            const currentStatusMap = {};
            sharedEngines.value.forEach(e => { if(e.status) currentStatusMap[e.id] = e.status; });

            sharedEngines.value = sharedData.map(engine => ({
                ...engine,
                status: currentStatusMap[engine.id] || engine.status || 'unknown',
                vitals: engine.vitals || null,
                isOwner: false
            }));
            console.log(`[EngineStore] Fetched ${sharedEngines.value.length} shared engines.`);
        } catch (e) {
            console.error('[EngineStore] Error fetching shared engines:', e.error || e.message);
            sharedEngines.value = [];
        }
    }

    async function registerEngine(name) {
        isLoading.value = true;
        error.value = null;
        const uiStore = useUiStore();
        console.log(`[EngineStore] Registering new engine with name: ${name}`);
        try {
            const newEngineData = await apiRegisterEngine({ name });
            if (newEngineData.error) throw new Error(newEngineData.error);

            uiStore.showNotification({
                text: `Engine '${newEngineData.name}' registered! Please copy the token and ID below.`,
                color: 'success',
                timeout: 7000
            });
            uiStore.showTokenDialog({
                title: 'Engine Registered Successfully!',
                text: "Copy these details and add them to your engine's .env file. (The token is only shown once!)",
                items: [
                    { label: 'FLOWORK_ENGINE_ID', value: newEngineData.id },
                    { label: 'FLOWORK_ENGINE_TOKEN', value: newEngineData.raw_token }
                ]
            });
            await fetchEngines();
            await setSelectedEngineId(newEngineData.id, true);
            return true;
        } catch (e) {
            error.value = e.error || e.message || 'Failed to register engine.';
            console.error('[EngineStore] Error registering engine:', error.value);
            uiStore.showNotification({ text: error.value, color: 'error' });
            return false;
        } finally {
            isLoading.value = false;
        }
    }

    async function deleteEngine(engineId) {
        isLoading.value = true;
        error.value = null;
        const uiStore = useUiStore();
        const engineToDelete = allAvailableEngines.value.find(e => e.id === engineId);
        console.log(`[EngineStore] Deleting engine: ${engineToDelete?.name || engineId}`);
        try {
            const result = await apiDeleteEngine(engineId);
            if (result.error) throw new Error(result.error);

            uiStore.showNotification({ text: `Engine '${engineToDelete?.name || engineId}' deleted.`, color: 'info' });
            engines.value = engines.value.filter(e => e.id !== engineId);
            sharedEngines.value = sharedEngines.value.filter(e => e.id !== engineId);
            if (selectedEngineId.value === engineId) {
                const nextEngine = allAvailableEngines.value[0];
                console.log("[EngineStore] Deleted engine was selected. Selecting new default:", nextEngine?.id);
                await setSelectedEngineId(nextEngine ? nextEngine.id : null);
            } else {
                 await fetchEngines();
            }
            return true;
        } catch (e) {
            error.value = e.error || e.message || 'Failed to delete engine.';
            console.error('[EngineStore] Error deleting engine:', error.value);
            uiStore.showNotification({ text: error.value, color: 'error' });
            return false;
        } finally {
            isLoading.value = false;
        }
    }

    function updateEngineStatus(statusData) {
        const engineRef = engines.value.find(e => e.id === statusData.engine_id) ||
            sharedEngines.value.find(e => e.id === statusData.engine_id);

        if (engineRef) {
            const oldStatus = engineRef.status;
            engineRef.status = statusData.status || engineRef.status;
            engineRef.last_seen = statusData.last_seen || engineRef.last_seen;
            if (statusData.name) engineRef.name = statusData.name;
            console.log(`[EngineStore] Updated status for engine ${engineRef.name || statusData.engine_id}: ${engineRef.status}`);

            const workflowStore = useWorkflowStore();
            const componentStore = useComponentStore();
            const variableStore = useVariablesStore();
            const settingsStore = useSettingsStore();
            const promptStore = usePromptsStore();

            // [KUDETA] No training store here!

            if (engineRef.id === selectedEngineId.value && engineRef.status === 'online' && oldStatus !== 'online') {
                console.log(`[EngineStore] Selected engine ${engineRef.id} just came ONLINE. Triggering full data re-fetch...`);
                settingsStore.fetchSettings();
                workflowStore.fetchPresets();
                variableStore.fetchVariables();
                componentStore.forceRefetchAllComponents();
                workflowStore.fetchUserFavorites();
                componentStore.fetchUserFavorites();
                promptStore.fetchPrompts();
            }
        }
    }

    function syncEngineStatuses(statusList) {
        if (!Array.isArray(statusList)) return;

        console.log(`[EngineStore] Syncing ${statusList.length} engine statuses from Socket...`);
        statusList.forEach(s => {
            const engine = engines.value.find(e => e.id === s.engine_id) || sharedEngines.value.find(e => e.id === s.engine_id);
            if (engine) {
                engine.status = s.status;
                if (s.vitals) engine.vitals = s.vitals;
            }
        });
    }

    function updateEngineVitals(vitalsData) {
        const engineRef = engines.value.find(e => e.id === vitalsData.engine_id) ||
            sharedEngines.value.find(e => e.id === vitalsData.engine_id);
        if (engineRef) {
            engineRef.vitals = vitalsData.vitals;
            if (engineRef.status !== 'online') {
                engineRef.status = 'online';
                console.log(`[EngineStore] Engine ${engineRef.name || vitalsData.engine_id} marked as online due to vitals update.`);
                useComponentStore().forceRefetchAllComponents();
            }
        }
    }

    async function setSelectedEngineId(engineId, triggerReconnect = true) {
        const socketStore = useSocketStore();

        if (selectedEngineId.value !== engineId || engineId === null) {
            console.log(`[EngineStore] Setting selected engine to: ${engineId}. Trigger Reconnect: ${triggerReconnect}`);
            selectedEngineId.value = engineId;

            if (engineId) {
                localStorage.setItem('flowork_active_engine_id', engineId);

                if (triggerReconnect) {
                    socketStore.switchEngine(engineId);
                }
            } else {
                localStorage.removeItem('flowork_active_engine_id');

                if (triggerReconnect) {
                    socketStore.disconnect();
                }
            }
        }
    }

    async function fetchEngineShares(engineId) {
        const uiStore = useUiStore();
        try {
            const sharesList = await apiFetchEngineShares(engineId);
            if (sharesList.error) throw new Error(sharesList.error);
            return sharesList;
        } catch (e) {
            const errorMsg = e.error || e.message || 'Failed to fetch engine shares.';
            uiStore.showNotification({ text: errorMsg, color: 'error' });
            return [];
        }
    }

    async function grantShare(engineId, shareWithIdentifier, role = 'reader') {
        const uiStore = useUiStore();
        isLoading.value = true;
        try {
            const result = await apiGrantShare(engineId, shareWithIdentifier, role);
            if (result.error) throw new Error(result.error);
            uiStore.showNotification({ text: result.message || 'Share granted successfully.', color: 'success' });
            return true;
        } catch (e) {
            const errorMsg = e.error || e.message || 'Failed to grant share.';
            uiStore.showNotification({ text: errorMsg, color: 'error' });
            return false;
        } finally {
             isLoading.value = false;
        }
    }

    async function revokeShare(engineId, sharedUserId) {
         const uiStore = useUiStore();
         isLoading.value = true;
         try {
            const result = await apiRevokeShare(engineId, sharedUserId);
            if (result.error) throw new Error(result.error);
            uiStore.showNotification({ text: result.message || 'Share revoked successfully.', color: 'info' });
            return true;
        } catch (e) {
            const errorMsg = e.error || e.message || 'Failed to revoke share.';
            uiStore.showNotification({ text: errorMsg, color: 'error' });
            return false;
        } finally {
             isLoading.value = false;
        }
    }

    return {
        engines, sharedEngines, isLoading, error, selectedEngineId,
        allAvailableEngines, selectedEngine, hasOnlineEngine,
        fetchEngines, registerEngine, deleteEngine, updateEngineStatus, updateEngineVitals, setSelectedEngineId,
        fetchSharedEngines, fetchEngineShares, grantShare, revokeShare, syncEngineStatuses,
        runModule
    };
});