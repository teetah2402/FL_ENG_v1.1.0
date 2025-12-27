//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\socket.js total lines 712
//#######################################################################

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { io } from 'socket.io-client';
import { useAuthStore } from './auth';
import { useUiStore } from './ui';
import { useLogStore } from './logs';
import { useWorkflowStore } from './workflow';
import { useComponentStore } from './components';
import { useAppStore } from './apps';
import { useEngineStore } from './engines';
import { useVariablesStore } from './variables';
import { useSettingsStore } from './settings';
import { usePromptsStore } from './prompts';
import { ethers } from 'ethers';

import { getGatewayUrl } from '@/api';

const useAgentStore = defineStore('agent', () => {
    const currentSessionId = ref(null);
    const currentWsToken = ref(null);
    const currentPhase = ref('idle');
    const conversation = ref([]);
    const isStreaming = ref(false);

    function startSession(sessionId, wsToken) {
        currentSessionId.value = sessionId;
        currentWsToken.value = wsToken;
        currentPhase.value = 'queued';
        conversation.value = [];
        isStreaming.value = false;
    }

    function addUserMessage(text) {
        conversation.value.push({ type: 'user', content: text });
    }

    function addAgentChunk(chunk) {
        isStreaming.value = true;
        if (conversation.value.length > 0 && conversation.value[conversation.value.length - 1].type === 'agent') {
            conversation.value[conversation.value.length - 1].content += chunk;
        } else {
            conversation.value.push({ type: 'agent', content: chunk });
        }
    }

    function setPhase(phase) {
        currentPhase.value = phase;
        if (phase === 'running') isStreaming.value = false;
        if (phase === 'done' || phase === 'error' || phase === 'cancelled') isStreaming.value = false;
    }

    function setDone(outcome) {
        setPhase('done');
    }

    function setError(code, message) {
        setPhase('error');
        conversation.value.push({ type: 'error', content: `[${code}] ${message}` });
    }

    function reset() {
        currentSessionId.value = null;
        currentWsToken.value = null;
        currentPhase.value = 'idle';
        conversation.value = [];
        isStreaming.value = false;
    }

    return {
        currentSessionId,
        currentWsToken,
        currentPhase,
        conversation,
        isStreaming,
        startSession,
        addUserMessage,
        addAgentChunk,
        setPhase,
        setDone,
        setError,
        reset,
    };
});

const CURRENT_PAYLOAD_VERSION = 2;

const _getAuthHeaders = async () => {
    const authStore = useAuthStore();
    if (!authStore.privateKey || !authStore.user?.id) {
        throw new Error("User not authenticated");
    }
    try {
        const wallet = new ethers.Wallet(authStore.privateKey);
        const timestamp = Math.floor(Date.now() / 1000);
        const messageToSign = `flowork_socket_auth|${wallet.address}|${timestamp}`;
        const signature = await wallet.signMessage(messageToSign);
        return {
            'X-User-Address': wallet.address,
            'X-Signed-Message': messageToSign,
            'X-Signature': signature,
            'X-Payload-Version': CURRENT_PAYLOAD_VERSION
        };
    } catch (error) {
        console.error('[SocketStore] Failed to generate auth headers:', error);
        throw error;
    }
};

export const useSocketStore = defineStore('socket', () => {
    const socket = ref(null);
    const isConnecting = ref(false);
    const connectionError = ref(null);
    const resolvedGatewayUrl = ref(null);
    const isGracePeriod = ref(true);
    const currentEngineStatus = ref({
        isBusy: false,
        cpuPercent: null,
        memoryPercent: null
    });
    const isConnected = computed(() => socket.value?.connected || false);
    const isDevEngine = computed(() => {
        const engineStore = useEngineStore();
        return engineStore.selectedEngine?.isDev || false;
    });

    async function connect(targetEngineId = null) {
        if (socket.value?.connected) {
            console.log("[SocketStore] Already connected. Skipping.");
            return;
        }
        if (isConnecting.value) {
             console.log("[SocketStore] Connection already in progress.");
             return;
        }

        const authStore = useAuthStore();
        const engineStore = useEngineStore();

        if (!authStore.isAuthenticated) {
            console.warn("[SocketStore] Connection attempt aborted: User not authenticated.");
            isGracePeriod.value = false;
            return;
        }

        isConnecting.value = true;
        isGracePeriod.value = true;

        setTimeout(() => {
            if (!isConnected.value) {
                isGracePeriod.value = false;
            }
        }, 3000);

        connectionError.value = null;
        const gatewayUrl = getGatewayUrl();
        resolvedGatewayUrl.value = gatewayUrl;

        let authHeaders;
        try {
            authHeaders = await _getAuthHeaders();
        } catch (error) {
            connectionError.value = `Auth Failed: ${error.message}`;
            isConnecting.value = false;
            isGracePeriod.value = false;
            authStore.logout();
            return;
        }

        const socketPath = "/api/socket.io";
        const socketNamespace = "/gui-socket";
        let baseSocketUrl = import.meta.env.VITE_SOCKET_URL
            ? import.meta.env.VITE_SOCKET_URL.replace(/\/$/, "")
            : gatewayUrl;

        const socketUrl = baseSocketUrl + socketNamespace;
        console.log(`[SocketStore] Connecting directly to namespace: ${socketUrl} (Path: ${socketPath})`);

        let finalEngineId = targetEngineId || engineStore.selectedEngineId;
        if (!finalEngineId) {
            finalEngineId = localStorage.getItem('flowork_active_engine_id');
        }

        const queryParams = {};
        if (finalEngineId) {
            queryParams.engine_id = finalEngineId;
            console.log(`[SocketStore] Binding connection to Engine ID: ${finalEngineId}`);
        }

        try {
            const newSocket = io(socketUrl, {
                path: socketPath,
                transports: ['websocket'],
                autoConnect: false,
                reconnection: true,
                reconnectionAttempts: Infinity,
                reconnectionDelay: 500,
                reconnectionDelayMax: 2000,
                timeout: 60000,
                ackTimeout: 60000,
                auth: {
                    headers: authHeaders
                },
                query: queryParams
            });

            socket.value = newSocket;
            registerEventHandlers();
            console.log("[SocketStore] Listeners attached. Initiating connection...");
            socket.value.connect();
        } catch (error) {
            console.error("[SocketStore] Failed to initialize socket.io client:", error);
            connectionError.value = `Connection Init Failed: ${error.message}`;
            isConnecting.value = false;
            isGracePeriod.value = false;
        }
    }

    function disconnect() {
        if (socket.value) {
            console.log("[SocketStore] Disconnecting socket...");
            socket.value.disconnect();
            socket.value = null;
        }
        isConnecting.value = false;
        connectionError.value = null;
        resolvedGatewayUrl.value = null;
        currentEngineStatus.value = { isBusy: false, cpuPercent: null, memoryPercent: null };
        isGracePeriod.value = false;

        const agentStore = useAgentStore();
        agentStore.reset();
    }

    async function sendMessage(payload) {
        if (!isConnected.value || !socket.value) {
            console.error("[SocketStore] Cannot send message: Socket not connected.", payload);
            const uiStore = useUiStore();
            uiStore.showConnectEngineDialog();
            throw new Error("Socket not connected");
        }

        const eventName = payload.type;
        if (!eventName) {
            console.error("[SocketStore] Cannot send message: Payload has no 'type' (event name).", payload);
            return;
        }

        const engineStore = useEngineStore();
        if (!payload.target_engine_id && engineStore.selectedEngineId) {
            payload.target_engine_id = engineStore.selectedEngineId;
        }

        const versionedPayload = {
            v: CURRENT_PAYLOAD_VERSION,
            payload: {
                ...payload,
            }
        };

        try {
            console.log(`[SocketStore] Sending Event '${eventName}'`, versionedPayload);
            socket.value.emit('message', versionedPayload); // CHANGED: All commands via 'message' channel usually
        } catch (error) {
            console.error(`[SocketStore] Error emitting socket event '${eventName}':`, error);
        }
    }

    async function joinAgentSession(sessionId, wsToken) {
        if (!isConnected.value || !socket.value) {
            console.error("[SocketStore] Cannot join session: Socket not connected.");
            return;
        }

        const agentStore = useAgentStore();
        agentStore.startSession(sessionId, wsToken);

        const payload = {
            session_id: sessionId,
            ws_token: wsToken
        };

        console.log(`[SocketStore] Emitting 'gui:join' for session ${sessionId}`);
        socket.value.emit('gui:join', payload, (ack) => {
            if (ack.ok) {
                console.log(`[SocketStore] Successfully joined session room ${sessionId}`);
            } else {
                console.error(`[SocketStore] Failed to join session room: ${ack.error}`);
                agentStore.setError('JOIN_FAILED', ack.error);
            }
        });
    }

    async function sendAgentInput(input) {
        const agentStore = useAgentStore();
        const sessionId = agentStore.currentSessionId;

        if (!isConnected.value || !socket.value) {
            console.error("[SocketStore] Cannot send input: Socket not connected.");
            return;
        }
        if (!sessionId) {
            console.error("[SocketStore] Cannot send input: Not in a session.");
            return;
        }

        let payload;
        if (typeof input === 'string') {
            payload = { session_id: sessionId, text: input };
            agentStore.addUserMessage(input);
        } else {
            payload = { session_id: sessionId, tool: input };
        }

        console.log(`[SocketStore] Emitting 'gui:input' for session ${sessionId}`);
        socket.value.emit('gui:input', payload);
    }

    function switchEngine(newEngineId) {
        console.log(`[SocketStore] Switching to engine: ${newEngineId}`);
        const engineStore = useEngineStore();
        if (isConnected.value || socket.value) {
            socket.value.disconnect();
            socket.value = null;
        }

        engineStore.setSelectedEngineId(newEngineId);
        localStorage.setItem('flowork_active_engine_id', newEngineId);

        setTimeout(() => {
            connect(newEngineId);
        }, 100);
    }

    function registerEventHandlers() {
        if (!socket.value) return;

        const uiStore = useUiStore();
        const logStore = useLogStore();
        const workflowStore = useWorkflowStore();
        const componentStore = useComponentStore();
        const appStore = useAppStore();
        const engineStore = useEngineStore();
        const variableStore = useVariablesStore();
        const settingsStore = useSettingsStore();
        const promptStore = usePromptsStore();
        const agentStore = useAgentStore();

        socket.value.onAny((eventName, ...args) => {
            console.log(`%c[Socket IN] ${eventName}`, 'color: cyan; font-weight: bold;', args);
        });

        socket.value.on('connect', () => {
            isConnecting.value = false;
            isGracePeriod.value = false;
            connectionError.value = null;
            console.log(`%c[SocketStore] CONNECTED ✅ (SID: ${socket.value.id})`, 'color: #00FF00; font-size: 14px; font-weight: bold;');
            uiStore.showNotification({ text: `Connected to Flowork Gateway`, color: 'success', timeout: 2000 });

            console.log("[SocketStore] Triggering full data hydration...");

            settingsStore.fetchSettings();
            workflowStore.fetchPresets();
            variableStore.fetchVariables();
            componentStore.forceRefetchAllComponents();
            appStore.fetchInstalledApps();
            workflowStore.fetchUserFavorites();
            componentStore.fetchUserFavorites();
            promptStore.fetchPrompts();
        });

        socket.value.on('connect_error', (error) => {
            console.error('[SocketStore] NAMESPACE Connection Error:', error.message);
            if (!isGracePeriod.value) {
                 connectionError.value = `Connection Failed: ${error.message}`;
            }
            isConnecting.value = false;
        });

        socket.value.on('disconnect', (reason) => {
            console.warn(`[SocketStore] Disconnected: ${reason}`);
            agentStore.setError('DISCONNECTED', reason);
        });

        socket.value.on('error', (data) => {
            const message = data?.payload?.message || data?.message || "Unknown error";
            console.error('[SocketStore] Received error from Gateway:', message);
            uiStore.showNotification({ text: `Error: ${message}`, color: 'error' });
        });

        socket.value.on('initial_engine_statuses', (statuses) => {
            engineStore.syncEngineStatuses(statuses);
        });

        socket.value.on('engine_status_update', (data) => {
            engineStore.updateEngineStatus(data);
            if (data.engine_id === engineStore.selectedEngineId) {
                currentEngineStatus.value.isBusy = data.vitals?.is_busy || false;
                currentEngineStatus.value.cpuPercent = data.vitals?.cpu_percent || null;
                currentEngineStatus.value.memoryPercent = data.vitals?.memory_percent || null;
            }
        });

        socket.value.on('engine_vitals_update', (data) => {
            if (data.engine_id) {
                engineStore.updateEngineVitals(data);
            }
            currentEngineStatus.value.isBusy = data.vitals?.is_busy || false;
            currentEngineStatus.value.cpuPercent = data.vitals?.cpu_percent || null;
            currentEngineStatus.value.memoryPercent = data.vitals?.memory_percent || null;
        });

        socket.value.on('response_presets_list', (data) => {
            const payload = data.payload || data;
            if (payload.error) {
                console.error("[SocketStore] Error fetching presets:", payload.error);
            } else {
                workflowStore.updatePresetsList(payload.presets, payload.favorites);
            }
        });

        socket.value.on('response_load_preset', (data) => {
            const payload = data.payload || data;
            if (payload.error) {
                console.error(`[SocketStore] Error loading preset '${payload.name}':`, payload.error);
                uiStore.showNotification({ text: `Error loading '${payload.name}': ${payload.error}`, color: 'error' });
                workflowStore.handleFetchError(payload.error);
            } else {
                workflowStore.updateSinglePresetData(payload.name, payload.workflow_data);
            }
        });

        socket.value.on('response_variables', (data) => {
            const payload = data.payload || data;
            if (!payload.error) {
                variableStore.variables = payload.variables;
                variableStore.isLoading = false;
            }
        });

        socket.value.on('response_component_list', (data) => {
            const payload = data.payload || data;
            if (payload.error) {
                console.error(`[SocketStore] Error fetching components for ${payload.component_type}:`, payload.error);
            } else {
                if (payload.component_type === 'apps' || payload.component_type === 'widgets') {
                    appStore.fetchInstalledApps();
                }
                componentStore.updateComponentsList(payload.component_type, payload.components);
            }
        });

        socket.value.on('APPS_RELOADED', () => {
             console.log("[SocketStore] Apps reloaded event received.");
             appStore.fetchInstalledApps();
        });

        socket.value.on('settings_response', (data) => {
            const payload = data.payload || data;
            if (!payload.error) {
                settingsStore.settings = payload.settings;
                uiStore.loadUiPreferences(payload.settings);
            }
            settingsStore.isLoading = false;
        });

        socket.value.on('response_prompts_list', (data) => {
            const payload = data.payload || data;
            if (!payload.error) {
                promptStore.setPromptsList(payload.prompts);
            }
            promptStore.isLoading = false;
        });

        socket.value.on('response_datasets_list', (data) => {
            const payload = data.payload || data;
            if (!payload.error) {
                const datasetStore = (async () => (await import('./datasets')).useDatasetStore())();
                datasetStore.setDatasetsList(payload.datasets);
            }
        });

        socket.value.on('response_dataset_data', (data) => {
            const payload = data.payload || data;
            if (!payload.error) {
                const datasetStore = (async () => (await import('./datasets')).useDatasetStore())();
                datasetStore.setDatasetData(payload.data);
            }
        });

        socket.value.on('component_install_status', (data) => {
            const payload = data.payload || data;
            componentStore.handleInstallStatusUpdate(payload);
            if (payload.component_type === 'apps' || payload.component_type === 'widgets') {
                appStore.fetchInstalledApps();
            }
        });

        socket.value.on('WORKFLOW_EXECUTION_UPDATE', (data) => {
            const payload = data.payload || data;
            workflowStore.updateExecutionStatus(payload);
        });

        socket.value.on('NODE_METRIC_UPDATE', (data) => {
            const payload = data.payload || data;
            workflowStore.updateNodeExecutionStatus(payload.metric);
            logStore.updateTimelineEntry(payload.metric);
        });

        socket.value.on('CONNECTION_UPDATE', (data) => {
            const payload = data.payload || data;
            workflowStore.updateConnectionStatus(payload);
        });

        socket.value.on('WORKFLOW_LOG_ENTRY', (data) => {
            const payload = data.payload || data;
            logStore.addExecutionLog(payload);

            if (payload.node_id) {
                let status = 'RUNNING';
                const lvl = (payload.level || '').toUpperCase();
                const msg = (payload.message || '').toUpperCase();

                if (lvl.includes('SUCCESS') || msg.includes('COMPLETE')) status = 'SUCCESS';
                else if (lvl.includes('ERROR') || lvl.includes('FAIL')) status = 'FAILED';
                else if (lvl.includes('INFO') || lvl.includes('DEBUG')) status = 'RUNNING';

                workflowStore.updateNodeExecutionStatus({
                    node_id: payload.node_id,
                    status: status,
                    timestamp: payload.ts ? new Date(payload.ts).getTime() / 1000 : Date.now() / 1000,
                    workflow_context_id: payload.job_id
                });

                if (status === 'RUNNING') {
                    workflowStore.animateIncomingEdges(payload.node_id);
                }

                logStore.updateTimelineEntry({
                    node_id: payload.node_id,
                    module_id: payload.source,
                    status: status,
                    timestamp: payload.ts ? new Date(payload.ts).getTime() / 1000 : Date.now() / 1000,
                    execution_time_ms: null
                });
            }
        });

        socket.value.on('SHOW_DEBUG_POPUP', (data) => {
            console.log("%c[SocketStore] 🔥 DEBUG POPUP TRIGGERED! 🔥", 'background: #FFD700; color: black; font-size: 16px; padding: 4px;', data);
            const payload = data.payload || data;
            uiStore.showDataViewer(payload);
        });

        socket.value.on('CONNECTION_DATA_RESPONSE', (data) => {
            const payload = data.payload || data;
            if (payload.error) {
                uiStore.showDataViewer({
                    title: `Data for ${payload.connection_id?.substring(0,8)}...`,
                    error: `No data found.`,
                    content: payload.error
                });
            } else {
                uiStore.showDataViewer({
                    title: `Data History for ${payload.connection_id?.substring(0,8)}... (Job: ${payload.job_id?.substring(0,8)})`,
                    payload: payload.history
                });
            }
        });

        socket.value.on('agent:status', (data) => {
            if (data.session_id === agentStore.currentSessionId) {
                agentStore.setPhase(data.phase);
            }
        });

        socket.value.on('agent:token', (data) => {
            if (data.session_id === agentStore.currentSessionId) {
                agentStore.addAgentChunk(data.chunk);
            }
        });

        socket.value.on('agent:tool', (data) => {
            if (data.session_id === agentStore.currentSessionId) {
                agentStore.addAgentChunk(`\n\n**Tool Call: \`${data.name}\`**\n\`\`\`json\n${JSON.stringify(data.args, null, 2)}\n\`\`\`\n`);
            }
        });

        socket.value.on('agent:done', (data) => {
            if (data.session_id === agentStore.currentSessionId) {
                agentStore.setDone(data.outcome);
            }
        });

        socket.value.on('agent:error', (data) => {
            if (data.session_id === agentStore.currentSessionId) {
                agentStore.setError(data.code, data.message);
            }
        });

        socket.value.on('colosseum_log', (data) => {
            const payload = data.payload || data;
            console.log(`[SocketStore] Colosseum Update: ${payload.message}`);
            window.dispatchEvent(new CustomEvent('COLOSSEUM_LOG_UPDATE', { detail: payload }));
        });

        socket.value.on('FILESYSTEM_LIST_RESPONSE', (data) => {
            const payload = data.payload || data;
            window.dispatchEvent(new CustomEvent('FILESYSTEM_DATA_READY', { detail: payload }));
        });

        socket.value.on('app_action_request', async (data) => {
            const payload = data.payload || data;
            console.log("[Hybrid Bridge] 🌉 Received Request from Core:", payload);

            uiStore.showNotification({
                text: `App Action Request: ${payload.action}`,
                color: 'info',
                timeout: 3000
            });

            const responsePayload = {
                type: 'app_action_response',
                request_id: payload.request_id,
                result: {
                    status: 'ok',
                    data: null
                }
            };

            try {
                const customEvent = new CustomEvent('FLOWORK_APP_ACTION', {
                    detail: {
                        ...payload,
                        _callback: (resultData) => {
                        }
                    }
                });
                window.dispatchEvent(customEvent);

                if (payload.action === 'run_scrape' || payload.action === 'scrape') {
                    responsePayload.result.data = {
                        message: "Action dispatched to Browser",
                        target_url: payload.params?.url || "unknown",
                        timestamp: Date.now()
                    };
                } else {
                    responsePayload.result.data = { message: "Event dispatched to DOM" };
                }

            } catch (err) {
                console.error("[Hybrid Bridge] Error processing action:", err);
                responsePayload.result.status = 'error';
                responsePayload.result.error = err.message;
            }

            console.log("[Hybrid Bridge] 🚀 Sending Response back to Core:", responsePayload);
            socket.value.emit('app_action_response', responsePayload);
        });

    }

    return {
        socket,
        isConnected,
        isConnecting,
        connectionError,
        resolvedGatewayUrl,
        currentEngineStatus,
        isDevEngine,
        isGracePeriod,
        connect,
        disconnect,
        sendMessage,
        switchEngine,
        joinAgentSession,
        sendAgentInput,
        useAgentStore
    };
});