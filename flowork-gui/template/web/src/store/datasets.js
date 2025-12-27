//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\datasets.js total lines 142 
//#######################################################################

import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/api';

export const useDatasetStore = defineStore('datasets', () => {
    const datasets = ref([]);
    const selectedDatasetName = ref(null);
    const selectedDatasetData = ref([]);
    const isLoadingList = ref(false);
    const isLoadingData = ref(false);
    const error = ref(null);

    async function fetchDatasets() {
        isLoadingList.value = true;
        error.value = null;
        try {
            const response = await api.get('/api/v1/datasets');

            if (response.data && response.data.data && Array.isArray(response.data.data)) {
                datasets.value = response.data.data;
            } else if (response.data && Array.isArray(response.data)) {
                datasets.value = response.data;
            } else {
                datasets.value = [];
            }
        } catch (e) {
            console.error("[DatasetStore] Fetch failed:", e);
            datasets.value = [];
        } finally {
            isLoadingList.value = false;
        }
    }

    async function selectDataset(datasetName) {
        if (!datasetName) {
            selectedDatasetName.value = null;
            selectedDatasetData.value = [];
            return;
        }
        selectedDatasetName.value = datasetName;
        isLoadingData.value = true;

        try {
            const response = await api.get(`/api/v1/datasets/${datasetName}/data`);

            let rawData = [];
            if (response.data && response.data.data && Array.isArray(response.data.data)) {
                rawData = response.data.data;
            } else if (response.data && Array.isArray(response.data)) {
                rawData = response.data;
            }

            selectedDatasetData.value = rawData;
        } catch (e) {
            console.error("[DatasetStore] Load data failed:", e);
            selectedDatasetData.value = [];
        } finally {
            isLoadingData.value = false;
        }
    }

    async function createNewDataset(name) {
        if (!name || !name.trim()) return false;
        isLoadingList.value = true;
        try {
            await api.post('/api/v1/datasets', { name: name.trim() });
            await fetchDatasets();
            return true;
        } catch(e) {
            error.value = e.response?.data?.message || e.message || 'Failed to create dataset.';
            return false;
        } finally {
            isLoadingList.value = false;
        }
    }

    async function addDataToSelectedDataset(dataRows) {
        if (!selectedDatasetName.value || !dataRows) return false;
        isLoadingData.value = true;
        try {
            await api.post(`/api/v1/datasets/${selectedDatasetName.value}/data`, { data: dataRows });
            await selectDataset(selectedDatasetName.value); // Refresh data
            return true;
        } catch (e) {
            error.value = e.message || 'Failed to add data.';
            return false;
        } finally {
            isLoadingData.value = false;
        }
    }

    async function updateRowInSelectedDataset(rowData) {
        if (!selectedDatasetName.value || !rowData.id) return false;
        try {
            await api.put(`/api/v1/datasets/${selectedDatasetName.value}/data/${rowData.id}`, rowData);
            await selectDataset(selectedDatasetName.value);
            return true;
        } catch(e) {
            return false;
        }
    }

    async function removeRowFromSelectedDataset(rowId) {
        if (!selectedDatasetName.value || !rowId) return;
        try {
            await api.delete(`/api/v1/datasets/${selectedDatasetName.value}/data/${rowId}`);
            selectedDatasetData.value = selectedDatasetData.value.filter(r => r.id !== rowId);
        } catch (e) {
            console.error("Failed to delete row", e);
        }
    }

    async function removeDataset(datasetName) {
        isLoadingList.value = true;
        try {
            await api.delete(`/api/v1/datasets/${datasetName}`);
            if (selectedDatasetName.value === datasetName) {
                selectedDatasetName.value = null;
                selectedDatasetData.value = [];
            }
            await fetchDatasets();
        } catch (e) {
            console.error("Failed to delete dataset", e);
        } finally {
            isLoadingList.value = false;
        }
    }

    return {
        datasets, selectedDatasetName, selectedDatasetData,
        isLoadingList, isLoadingData, error,
        fetchDatasets, selectDataset, createNewDataset,
        addDataToSelectedDataset, removeDataset,
        updateRowInSelectedDataset, removeRowFromSelectedDataset
    };
});
