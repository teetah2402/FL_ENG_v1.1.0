//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\variables.js total lines 92 
//#######################################################################

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiGetVariables, apiSaveVariable, apiDeleteVariable, apiSyncVariableToLocal } from '@/api';

export const useVariablesStore = defineStore('variables', () => {
    const variables = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    const SYSTEM_VARIABLES = [
        { name: 'OPENAI_API_KEY', defaultValue: 'CHANGE THIS API' },
        { name: 'GEMINI_API_KEY', defaultValue: 'CHANGE THIS API' },
        { name: 'DEEPSEEK_API_KEY', defaultValue: 'CHANGE THIS API' }
    ];

    async function fetchVariables() {
        isLoading.value = true;
        error.value = null;
        try {
            const cloudData = await apiGetVariables();
            let varList = Array.isArray(cloudData) ? cloudData : [];
            for (const v of varList) {
                if (v.name && v.value) {
                    await apiSyncVariableToLocal(v.name, v.value);
                }
            }

            SYSTEM_VARIABLES.forEach(sysVar => {
                const exists = varList.find(v => v.name === sysVar.name);
                if (!exists) {
                    varList.unshift({
                        name: sysVar.name,
                        value: sysVar.defaultValue,
                        is_enabled: true,
                        is_secret: true,
                        is_protected: true
                    });
                } else {
                    exists.is_protected = true;
                }
            });

            variables.value = varList;
        } catch (e) {
            console.error('[Variables] Fetch/Sync failed:', e);
            error.value = e.message;
        } finally {
            isLoading.value = false;
        }
    }

    async function saveVariable(name, variableData) {
        try {
            const payload = {
                value: variableData.value,
                is_enabled: variableData.is_enabled,
                is_secret: variableData.is_secret,
                mode: variableData.mode || 'single'
            };
            await apiSaveVariable(name, payload);
            await apiSyncVariableToLocal(name, payload.value);
            const idx = variables.value.findIndex(v => v.name === name);
            if (idx !== -1) {
                variables.value[idx] = { ...variables.value[idx], ...payload };
            } else {
                variables.value.push({ name, ...payload });
            }
            return true;
        } catch (e) {
            console.error(`[Variables] Save failed:`, e);
            throw e;
        }
    }

    async function removeVariable(name) {
        if (SYSTEM_VARIABLES.some(sv => sv.name === name)) return false;
        try {
            await apiDeleteVariable(name);
            variables.value = variables.value.filter(v => v.name !== name);
            return true;
        } catch (e) {
            return false;
        }
    }
    return { variables, isLoading, error, fetchVariables, saveVariable, removeVariable };
});
