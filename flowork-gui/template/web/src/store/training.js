//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\training.js total lines 172 
//#######################################################################

import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/api';
import { useUiStore } from './ui';

export const useTrainingStore = defineStore('training', () => {
    const localModels = ref([]);
    const trainingJobs = ref([]);
    const conversionJobs = ref([]);
    const isConverting = ref(false);
    const activeEngineId = ref('LOCAL');
    const isLoadingModels = ref(false);
    const isLoadingJobs = ref(false);
    const error = ref(null);

    async function fetchLocalModels() {
        isLoadingModels.value = true;
        try {
            const response = await api.get('/api/v1/models/local');
            const rawData = response.data || [];
            let formattedModels = [];
            if (Array.isArray(rawData)) {
                formattedModels = rawData.map(m => ({ id: m.id || m.name, name: m.name || m.id }));
            } else if (typeof rawData === 'object') {
                formattedModels = Object.entries(rawData).map(([key, val]) => ({ id: key, name: val.name || key }));
            }
            localModels.value = formattedModels;
        } catch (e) {
            console.warn("[TrainingStore] Failed to load models:", e);
        } finally {
            isLoadingModels.value = false;
        }
    }

    async function rescanModels() {
        isLoadingModels.value = true;
        const uiStore = useUiStore();
        try {
            await api.post('/api/v1/models/rescan');
            await fetchLocalModels();
            uiStore.showNotification({ text: "Model list refreshed!", color: "success" });
        } catch (e) {
            console.error("Rescan failed:", e);
            uiStore.showNotification({ text: "Failed to rescan models.", color: "error" });
        } finally {
            isLoadingModels.value = false;
        }
    }

    async function fetchTrainingJobs() {
        isLoadingJobs.value = true;
        try {
            const response = await api.get('/api/v1/training/jobs');
            if (Array.isArray(response.data)) trainingJobs.value = response.data;
            const convResponse = await api.get('/api/v1/models/conversions');
            if (Array.isArray(convResponse.data)) conversionJobs.value = convResponse.data;
        } catch (e) {
            console.error("[TrainingStore] Failed to list jobs:", e);
        } finally {
            isLoadingJobs.value = false;
        }
    }

    async function startTrainingJob(config) {
        isLoadingJobs.value = true;
        const uiStore = useUiStore();
        try {
            const response = await api.post('/api/v1/training/start', config);
            if (response.data && response.data.job_id) {
                addTrainingJobStatus({
                    job_id: response.data.job_id,
                    status: 'QUEUED',
                    new_model_name: config.new_model_name,
                    base_model_id: config.base_model_id,
                    message: 'Request sent. Waiting for sync...',
                    live_logs: 'Connecting...'
                });
                setTimeout(() => fetchTrainingJobs(), 1000);
                return { success: true, job_id: response.data.job_id };
            }
            return { success: false, error: "No Job ID returned from server." };
        } catch (e) {
            const msg = e.response?.data?.error || e.message;
            uiStore.showNotification({ text: msg, color: 'error' });
            return { success: false, error: msg };
        } finally {
            isLoadingJobs.value = false;
        }
    }

    async function startConversionJob(payload) {
        isConverting.value = true;
        const uiStore = useUiStore();
        try {
            const response = await api.post('/api/v1/training/convert', payload);
            addTrainingJobStatus({
                job_id: response.data.job_id || 'job_' + Date.now(),
                type: 'CONVERSION',
                source_model: payload.model_id,
                status: 'QUEUED',
                progress: 0,
                live_logs: 'Initializing GGUF Factory...',
                new_model_name: `GGUF-${payload.model_id}`
            });
            uiStore.showNotification({ text: 'Conversion Started!', color: 'cyan' });
            setTimeout(() => fetchTrainingJobs(), 1000);
            return { success: true };
        } catch (e) {
            uiStore.showNotification({ text: 'Failed to start conversion.', color: 'error' });
            return { success: false, error: e.message };
        } finally {
            isConverting.value = false;
        }
    }

    async function runSparringMatch(payload) {
        const uiStore = useUiStore();
        try {
            const response = await api.post('/api/v1/training/sparring', payload, {
                timeout: 300000
            });
            return response.data;
        } catch (e) {
            console.error("Sparring Failed:", e);
            const errorMsg = e.response?.data?.error || e.message;
            uiStore.showNotification({ text: 'Sparring Match Failed: ' + errorMsg, color: 'error' });
            return null;
        }
    }

    async function deleteJob(jobId) {
        const uiStore = useUiStore();
        try {
            await api.delete(`/api/v1/training/jobs/${jobId}`);
            trainingJobs.value = trainingJobs.value.filter(j => j.job_id !== jobId);
            uiStore.showNotification({ text: 'Job deleted.', color: 'success' });
            return true;
        } catch (e) {
            uiStore.showNotification({ text: 'Failed to delete job.', color: 'error' });
            return false;
        }
    }

    function addTrainingJobStatus(statusData) {
        const index = trainingJobs.value.findIndex(j => j.job_id === statusData.job_id);
        if (index !== -1) trainingJobs.value[index] = { ...trainingJobs.value[index], ...statusData };
        else trainingJobs.value.unshift(statusData);
    }

    return {
        localModels,
        trainingJobs,
        conversionJobs,
        isLoadingModels,
        isLoadingJobs,
        isConverting,
        activeEngineId,
        fetchLocalModels,
        rescanModels,
        fetchTrainingJobs,
        startTrainingJob,
        startConversionJob,
        runSparringMatch,
        deleteJob
    };
});
