//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\neuralIngestor.js total lines 45 
//#######################################################################

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient, getAuthHeaders } from '@/api';

export const useNeuralIngestorStore = defineStore('neuralIngestor', () => {
    const isDistilling = ref(false);

    async function distillChunk(textChunk, modelId) {
        const url = '/api/v1/neural-ingestor/distill';
        const headers = await getAuthHeaders(url, 'POST');

        const payload = {
            prompt: `Distill this knowledge into JSON: ${textChunk}`,
            endpoint_id: modelId,
            mode: 'distillation',
            system_prompt: "Return ONLY a valid JSON array. Be witty, genius, and concise."
        };

        try {
            const res = await apiClient.post(url, payload, { headers });

            let rawData = res.data.data || res.data.result?.data || res.data;

            if (typeof rawData === 'string') {
                const jsonMatch = rawData.match(/\[[\s\S]*\]/);
                if (jsonMatch) {
                    return JSON.parse(jsonMatch[0]);
                }
                throw new Error("Neural output is not a valid JSON array.");
            }
            return rawData;
        } catch (e) {
            console.error("[Neural Ingestor] Distillation Failed:", e.response?.status, e.message);
            throw e;
        }
    }

    return { isDistilling, distillChunk };
});
