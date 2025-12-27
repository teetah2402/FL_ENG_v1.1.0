//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\aiCenter.js total lines 384 
//#######################################################################

import { defineStore } from 'pinia';
import { ref, computed, reactive } from 'vue'; // [FLOWORK DEV UPDATE] Added reactive
import { apiClient, getGatewayUrl, getAuthHeaders } from '@/api';

export const useAiCenterStore = defineStore('aiCenter', () => {
    const aiProviders = ref([]);
    const agents = ref([]);
    const trainingJobs = ref([]);

    const isLoadingStatus = ref(false);
    const isGenerating = ref(false);
    const queueStatus = ref(null);
    const error = ref(null);

    const sessions = ref([]);
    const currentSessionId = ref(null);

    const systemInstruction = ref(localStorage.getItem('flowork_system_instruction') || '');

    const toolConfigs = ref({});

    const aiState = reactive({
        mode: 'chat', // chat, agent, council
        selectedEndpointId: null, // Untuk mode Chat/Agent
        selectedJudgeId: null, // Untuk mode Council (Ketua Hakim)
        selectedCouncilMembers: [], // List ID model buat Council
        selectedPreset: null,
        selectedPersona: null
    });

    const loadingMessages = [
        "Aligning neural pathways...", "Parsing context vectors...", "Calibrating attention heads...",
        "Synthesizing cognitive patterns...", "Loading knowledge graph...", "Optimizing tensor operations...",
        "Establishing semantic connections...", "Thinking deeply...", "Analyzing prompt intent...",
        "Generating creative matrix...", "Consulting the digital oracle...", "Warming up the GPU cores...",
        "De-quantizing model weights...", "Tracing diffusion paths...", "Applying latent transformations...",
        "Refining output tensors...", "Constructing logic gates...", "Filtering noise...", "Finalizing output..."
    ];

    const currentSession = computed(() => sessions.value.find(s => s.id === currentSessionId.value) || null);
    const currentMessages = computed(() => currentSession.value ? currentSession.value.messages : []);
    const readyModels = computed(() => aiProviders.value.filter(m => m.status === 'active' || m.status === 'ready' || !m.status));


    function setSystemInstruction(prompt) {
        systemInstruction.value = prompt;
        localStorage.setItem('flowork_system_instruction', prompt);
    }

    function setToolConfig(toolId, config) {
        toolConfigs.value[toolId] = config;
    }

    function setAiMode(mode) {
        aiState.mode = mode;
    }

    async function fetchAiStatus() {
        isLoadingStatus.value = true;
        error.value = null;
        try {
            console.log("[AI Store] Fetching models via AI Proxy...");
            const response = await apiClient.get('/ai/models');
            const payload = response.data;
            let providers = [];
            if (Array.isArray(payload)) providers = payload;
            else if (payload && Array.isArray(payload.items)) providers = payload.items;
            else if (payload && Array.isArray(payload.models)) providers = payload.models;
            else if (payload && typeof payload === 'object') providers = Object.values(payload);

            aiProviders.value = providers.map(p => ({
                ...p,
                id: p.id || p.model_id,
                name: p.name || p.id
            }));

            if (aiProviders.value.length > 0) {
                if (!aiState.selectedEndpointId) aiState.selectedEndpointId = aiProviders.value[0].id;
                if (!aiState.selectedJudgeId) aiState.selectedJudgeId = aiProviders.value[0].id;

                if (aiState.selectedCouncilMembers.length === 0) {
                     const defaultMembers = aiProviders.value.filter(p => {
                        const searchStr = ((p.name || '') + ' ' + (p.id || '')).toLowerCase();
                        return searchStr.includes('gemini') || searchStr.includes('gpt') || searchStr.includes('openai');
                     }).map(p => p.id);

                     if (defaultMembers.length > 0) {
                        aiState.selectedCouncilMembers = defaultMembers;
                        console.log("[AI Store] Auto-selected Council Members:", defaultMembers);
                     }
                }
            }

        } catch (e) {
            console.error("[AI Store] API Error:", e);
            error.value = 'Failed to connect to AI Engine.';
            aiProviders.value = [];
        } finally {
            isLoadingStatus.value = false;
        }
    }

    async function fetchAgents() {
        try {
            const response = await apiClient.get('/ai/agents');
            agents.value = response.data.items || [];
        } catch (e) { console.warn("[AI Store] Failed to fetch agents:", e); }
    }

    async function loadHistory() {
        try {
            const res = await apiClient.get('/ai/sessions');
            sessions.value = res.data || [];

            const lastId = localStorage.getItem('flowork_last_session_id');
            if (lastId && sessions.value.find(s => s.id === lastId)) {
                switchSession(lastId);
            } else if (sessions.value.length > 0) {
                switchSession(sessions.value[0].id);
            }
        } catch (e) {
            console.error("Failed to load history from server:", e);
        }
    }

    async function createNewSession(title = "New Chat") {
        let defaultModel = readyModels.value.length > 0 ? readyModels.value[0].id : null;
        try {
            const res = await apiClient.post('/ai/sessions', { title: title, model_id: defaultModel });
            const newSession = res.data;
            sessions.value.unshift(newSession);
            switchSession(newSession.id);
            return newSession.id;
        } catch (e) {
            console.error("Create session failed:", e);
        }
    }

    async function switchSession(sessionId) {
        try {
            currentSessionId.value = sessionId;
            localStorage.setItem('flowork_last_session_id', sessionId);

            const res = await apiClient.get(`/ai/sessions/${sessionId}`);
            const sessionData = res.data;

            const idx = sessions.value.findIndex(s => s.id === sessionId);
            if (idx !== -1) sessions.value[idx] = sessionData;
            else sessions.value.unshift(sessionData);

            const reactiveSession = sessions.value.find(s => s.id === sessionId);

            if (reactiveSession && reactiveSession.messages && reactiveSession.messages.length > 0) {
                let resumeCount = 0;
                reactiveSession.messages.forEach(msg => {
                    if (msg.role === 'assistant' && msg.jobId && (!msg.content && !msg.mediaUrl && !msg.error)) {
                        console.log(`[Auto-Resume] Resuming job ${msg.jobId}...`);
                        msg.isLoading = true;
                        msg.status = 'Reconnect to Neural Engine...';
                        isGenerating.value = true;
                        _pollJob(msg.jobId, msg);
                        resumeCount++;
                    }
                });
                if (resumeCount > 0) console.log(`[AI Store] Resumed ${resumeCount} pending jobs.`);
            }
        } catch (e) {
            console.error("Switch session failed:", e);
        }
    }

    async function deleteSession(sessionId) {
        try {
            await apiClient.delete(`/ai/sessions/${sessionId}`);
            sessions.value = sessions.value.filter(s => s.id !== sessionId);
            if (currentSessionId.value === sessionId) {
                const nextId = sessions.value.length > 0 ? sessions.value[0].id : null;
                if (nextId) switchSession(nextId);
                else currentSessionId.value = null;
            }
        } catch (e) { console.error("Delete failed:", e); }
    }

    async function renameSession(sessionId, newTitle) {
        const s = sessions.value.find(s => s.id === sessionId);
        if (s) s.title = newTitle;
        try {
            await apiClient.patch(`/ai/sessions/${sessionId}`, { title: newTitle });
        } catch (e) { console.error("Rename failed:", e); }
    }

    function toggleLike(sessionId, index) {
        const session = sessions.value.find(s => s.id === sessionId);
        if (session && session.messages[index]) {
            session.messages[index].liked = !session.messages[index].liked;
            _syncSessionMessages(sessionId, session.messages);
        }
    }

    async function sendMessage(prompt, modelId, extraPayload = {}) {
        if (!prompt.trim()) return;

        if (!currentSessionId.value) await createNewSession();

        const session = sessions.value.find(s => s.id === currentSessionId.value);
        if (!session) return;

        if (session.messages.length === 0) {
            const newTitle = prompt.substring(0, 40) + (prompt.length > 40 ? '...' : '');
            renameSession(session.id, newTitle);
        }

        session.messages.push({ role: 'user', content: prompt, timestamp: Date.now() });
        await _syncSessionMessages(session.id, session.messages);

        const assistantMsg = {
            role: 'assistant',
            content: '',
            timestamp: Date.now(),
            isLoading: true,
            status: 'Initializing Queue...',
            queuePos: null,
            error: false,
            jobId: null
        };
        session.messages.push(assistantMsg);

        isGenerating.value = true;

        try {
            let finalPayload = {
                prompt,
                endpoint_id: modelId || session.modelId || aiState.selectedEndpointId, // Prioritize user selection
                messages: session.messages.slice(0, -1),
                session_id: session.id,
                system_prompt: systemInstruction.value, // Inject Custom Prompt
                mode: aiState.mode, // Tell backend what mode we are in
                ...extraPayload
            };

            if (aiState.mode === 'agent') {
                finalPayload.tool_configs = toolConfigs.value;
                if (aiState.selectedPreset) finalPayload.preset_id = aiState.selectedPreset.id;
                if (aiState.selectedPersona) finalPayload.persona_id = aiState.selectedPersona.id;
            }
            else if (aiState.mode === 'council') {
                finalPayload.is_council = true; // Trigger for Gateway Timeout
                finalPayload.council_config = {
                    judge_id: aiState.selectedJudgeId,
                    members: aiState.selectedCouncilMembers,
                    topic: prompt
                };
                assistantMsg.status = "Convening the Council...";
            } else {
                finalPayload.tool_configs = toolConfigs.value; // Still allow tools in chat if needed
            }

            const res = await apiClient.post('/ai/jobs/submit', {
                type: aiState.mode === 'council' ? 'council_deliberation' : 'generation', // Switch job type
                payload: finalPayload
            });

            const jobId = res.data.job_id;
            assistantMsg.jobId = jobId;
            await _syncSessionMessages(session.id, session.messages);

            console.log(`[AI Store] Job Submitted: ${jobId} (Pos: ${res.data.position}) Mode: ${aiState.mode}`);
            await _pollJob(jobId, assistantMsg);

        } catch (e) {
            console.error("Job Submit Error:", e);
            assistantMsg.isLoading = false;
            assistantMsg.error = true;
            assistantMsg.content = `[System Error] ${e.response?.data?.error || e.message}`;
            _syncSessionMessages(session.id, session.messages);
        } finally {
            isGenerating.value = false;
            queueStatus.value = null;
        }
    }

    async function _pollJob(jobId, msgObject) {
        const pollInterval = 1500;
        return new Promise((resolve, reject) => {
            const interval = setInterval(async () => {
                try {
                    const res = await apiClient.get(`/ai/jobs/${jobId}`);
                    const status = res.data.status;
                    const result = res.data.result;
                    const pos = res.data.position;

                    if (status === 'QUEUED') {
                        msgObject.status = `Queued (Position: ${pos})`;
                        msgObject.queuePos = pos;
                        queueStatus.value = { position: pos, status: 'QUEUED' };
                    }
                    else if (status === 'PROCESSING') {
                        if (aiState.mode === 'council') {
                            msgObject.status = "The Council is deliberating... (This may take a while)";
                        } else {
                            const randomMsg = loadingMessages[Math.floor(Math.random() * loadingMessages.length)];
                            msgObject.status = randomMsg;
                        }
                        msgObject.queuePos = 0;
                        queueStatus.value = { position: 0, status: 'PROCESSING' };
                    }
                    else if (status === 'COMPLETED') {
                        clearInterval(interval);
                        msgObject.isLoading = false;
                        msgObject.status = null;

                        if (result.type === 'text') {
                            msgObject.content = result.data;
                        } else if (result.type === 'image' || result.type === 'audio' || result.type === 'video') {
                            msgObject.content = "";
                            msgObject.mediaType = result.type;
                            msgObject.mediaUrl = _rewriteMediaUrl(result.url);
                        } else if (result.data) {
                             msgObject.content = typeof result.data === 'string' ? result.data : JSON.stringify(result.data, null, 2);
                        }

                        await _syncSessionMessages(currentSessionId.value, sessions.value.find(s => s.id === currentSessionId.value).messages);
                        resolve();
                    }
                    else if (status === 'FAILED' || status === 'CANCELLED') {
                        clearInterval(interval);
                        msgObject.isLoading = false;
                        msgObject.error = true;
                        msgObject.content = `[Job Failed] ${res.data.error || 'Unknown error'}`;
                        _syncSessionMessages(currentSessionId.value, sessions.value.find(s => s.id === currentSessionId.value).messages);
                        resolve();
                    }
                } catch (e) {
                    console.error("Polling Error (Retrying...):", e);
                }
            }, pollInterval);
        });
    }

    async function editMessage(sessionId, index, newContent) {
        const session = sessions.value.find(s => s.id === sessionId);
        if (!session || !session.messages[index]) return;
        session.messages[index].content = newContent;
        if (session.messages[index].role === 'user') {
            session.messages = session.messages.slice(0, index + 1);
            await sendMessage(newContent, session.modelId);
        } else {
            _syncSessionMessages(sessionId, session.messages);
        }
    }

    function deleteMessage(sessionId, index) {
        const session = sessions.value.find(s => s.id === sessionId);
        if (session) {
            session.messages.splice(index, 1);
            _syncSessionMessages(sessionId, session.messages);
        }
    }

    async function _syncSessionMessages(sessionId, messages) {
        try { await apiClient.patch(`/ai/sessions/${sessionId}`, { messages }); } catch (e) { console.error("Sync error:", e); }
    }

    function _rewriteMediaUrl(url) {
        if (!url) return null;
        const gatewayUrl = getGatewayUrl();
        if (url.startsWith('/api')) return `${gatewayUrl}${url}`;
        return url;
    }

    return {
        aiProviders, agents, trainingJobs, isLoadingStatus, isGenerating, queueStatus,
        sessions, currentSessionId, error, currentSession, currentMessages, readyModels,
        systemInstruction, toolConfigs, aiState, // [FLOWORK DEV UPDATE] Export aiState
        fetchAiStatus, fetchAgents, createNewSession, switchSession, setSystemInstruction, setToolConfig, setAiMode, // [FLOWORK DEV UPDATE] Export setAiMode
        deleteSession, renameSession, sendMessage, editMessage, deleteMessage, loadHistory, toggleLike
    };
});
