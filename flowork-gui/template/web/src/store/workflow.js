//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\workflow.js total lines 1220 
//#######################################################################

import { defineStore } from 'pinia';
import { ref, computed, watch, nextTick } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { useUiStore } from '@/store/ui';
import { useComponentStore } from '@/store/components';
import { useLogStore } from '@/store/logs';
import { useSocketStore } from '@/store/socket';
import { ethers } from 'ethers';
import { useAuthStore } from '@/store/auth';
import { useEngineStore } from '@/store/engines';
import { apiCreateShareLink, apiGetWorkflowShares, apiUpdateSharePermission, apiDeleteShare, apiResolveShareToken, apiGetUserFavorites, apiSetUserFavorites } from '@/api';
import { debounce } from '@/utils/debounce.js';


const delay = (ms) => new Promise(res => setTimeout(res, ms));


/**
 * (English Hardcode) Robust stringify for deep sorting.
 * (English Hardcode) Ensures deterministic JSON strings for signing.
 */
function stableStringify(obj) {
    const replacer = (key, value) => {
        if (value === null) {
            return null;
        }
        if (typeof value === 'object' && !Array.isArray(value)) {
            return Object.keys(value)
                .sort() // (English Hardcode) Sort keys alphabetically
                .reduce((sorted, key) => {
                    sorted[key] = value[key];
                    return sorted;
                }, {});
        }
        return value;
    };
    try {
        const initiallySortedString = JSON.stringify(obj, replacer);
        const fullySortedObject = JSON.parse(initiallySortedString);
        return JSON.stringify(fullySortedObject, replacer, undefined);
    } catch (e) {
        console.warn("[WorkflowStore] Error during stableStringify, falling back to basic stringify:", e);
        return JSON.stringify(obj);
    }
}


export const useWorkflowStore = defineStore('workflow', () => {
    const elements = ref([]);
    const selectedNode = ref(null);
    const currentPresetName = ref(null);
    const isExecuting = ref(false);
    const isPaused = ref(false);
    const jobId = ref(null);
    const executionStatus = ref({});
    const connectionStatus = ref({});
    const presets = ref([]);
    const favoritePresets = ref([]);
    const clipboard = ref(null);
    const globalLoopConfig = ref({
        isEnabled: false,
        iterations: 1,
        isDelayEnabled: false,
        delayType: 'static', // 'static' or 'random_range'
        delayStatic: 1,
        delayRandomMin: 1,
        delayRandomMax: 5
    });
    const isStopRequested = ref(false);
    const permissionLevel = ref('edit');
    const error = ref(null);
    const isModified = ref(false);
    const isLoadingPresets = ref(false);

    const nodes = computed(() => elements.value.filter(el => 'position' in el));
    const edges = computed(() => elements.value.filter(el => 'source' in el));
    const isCanvasEmpty = computed(() => nodes.value.length === 0);
    const isReadOnly = computed(() => permissionLevel.value === 'view');

    const canExecute = computed(() => {
        const hasPermission = permissionLevel.value === 'view-run' || permissionLevel.value === 'edit' || permissionLevel.value === 'view-edit-run';
        return hasPermission && !isCanvasEmpty.value;
    });

    const selectedNodeHasBehavior = computed(() => (behaviorName) => {
        if (!selectedNode.value?.data?.manifest?.behaviors) {
            return false;
        }
        return selectedNode.value.data.manifest.behaviors.includes(behaviorName);
    });
    const getWorkflowForPublishing = computed(() => {
        return {
            nodes: nodes.value.map(node => ({
                id: node.id,
                name: node.label,
                x: node.position.x,
                y: node.position.y,
                module_id: node.data.moduleId,
                type: node.data.type, // V2: Store specific node type/id
                config_values: node.data.config_values || {},
                ...(node.data.color && { data: { color: node.data.color } })
            })),
            connections: edges.value.map(edge => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
                source_port_name: edge.sourceHandle,
                target_port_name: edge.targetHandle,
                type: edge.type,
                animated: edge.animated,
            })),
            global_loop_config: globalLoopConfig.value
        };
    });
    async function fetchUserFavorites() {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) return;
        try {
            console.log("[WorkflowStore] Fetching user favorite presets from Gateway...");
            const favorites = await apiGetUserFavorites();
            if (favorites.error) throw new Error(favorites.error);
            favoritePresets.value = favorites;
            console.log(`[WorkflowStore] User favorites loaded: ${favorites.length} items.`);
        } catch (error) {
            console.error("[WorkflowStore] Failed to fetch user favorites:", error);
            favoritePresets.value = [];
        }
    }

    const saveFavoritesDebounced = debounce(async () => {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) return;
        try {
            console.log("[WorkflowStore] Debounced save: Sending updated favorites to Gateway...");
            await apiSetUserFavorites(favoritePresets.value);
            console.log("[WorkflowStore] Debounced save: Favorites successfully saved to Gateway.");
        } catch (error) {
            console.error("[WorkflowStore] Debounced save: Failed to save favorites:", error);
            const uiStore = useUiStore();
            uiStore.showNotification({ text: `Error saving favorites: ${error.error || error.message}`, color: 'error'});
        }
    }, 1500);

    function toggleFavorite(presetName) {
        const index = favoritePresets.value.indexOf(presetName);
        if (index > -1) {
            favoritePresets.value.splice(index, 1);
        } else {
            favoritePresets.value.push(presetName);
        }

        saveFavoritesDebounced();
    }

    function applyChanges(changes) {
        if (isReadOnly.value) return;

        let tempElements = [...elements.value];
        let selectionChanged = false;

        changes.forEach(change => {
            const index = tempElements.findIndex(el => el.id === change.id);

            if (change.type === 'remove' && index !== -1) {
                if (selectedNode.value && selectedNode.value.id === change.id) {
                    selectionChanged = true;
                }
                tempElements.splice(index, 1);
                isModified.value = true;
            } else if (change.type === 'position' && change.position && index !== -1) {
                tempElements[index].position = change.position;
                isModified.value = true;
            }
        });

        elements.value = tempElements;

        if (selectionChanged) {
            clearSelectedNode();
        }
    }

    async function fetchConnectionData(connectionId) {
        const uiStore = useUiStore();
        const currentJobId = jobId.value;

        if (!currentJobId) {
            console.warn("[WorkflowStore] Cannot fetch connection history, no active or recent job ID stored.");
            uiStore.showDataViewer({
                title: `Data for ${connectionId.substring(0,8)}...`,
                error: "Workflow has not been run in this session.",
                details: "Run the workflow at least once to see connection data."
            });
            return;
        }

        try {
            const socketStore = useSocketStore();
            await socketStore.sendMessage({
                type: 'request_connection_history',
                job_id: currentJobId,
                connection_id: connectionId
            });
            console.log(`[WorkflowStore] Requested history for connection ${connectionId} (Job: ${currentJobId})`);
        } catch (error) {
            console.error(`[WorkflowStore] Failed to request history for connection ${connectionId}:`, error);
            uiStore.showDataViewer({
                title: `Data for ${connectionId.substring(0,8)}...`,
                error: "No history data found for this connection in the last run.",
                details: error.message
            });
        }
    }

    function updateConnectionStatus(data) {
        if (!data?.connection_id) return;

        connectionStatus.value = {
            ...connectionStatus.value,
            [data.connection_id]: {
                status: data.status,
                timestamp: Date.now()
            }
        };

        if (data.status === 'ACTIVE') {
            setTimeout(() => {
                 if (connectionStatus.value[data.connection_id]) {
                     connectionStatus.value = {
                         ...connectionStatus.value,
                         [data.connection_id]: {
                             ...connectionStatus.value[data.connection_id],
                             status: 'IDLE' // Back to boring gray
                         }
                     };
                 }
            }, 2000);
        }
    }

    function animateIncomingEdges(targetNodeId) {
        const incomingEdges = edges.value.filter(e => e.target === targetNodeId);

        incomingEdges.forEach(edge => {
            updateConnectionStatus({
                connection_id: edge.id,
                status: 'ACTIVE'
            });
        });
    }

    function setNodeColor({ nodeId, color }) {
      if (isReadOnly.value) return;
      const node = elements.value.find(el => el.id === nodeId);
      if (node) {
        if (!node.data) node.data = {};
        node.data.color = color;
        isModified.value = true;
      }
    }

    function removeElements(elementsToRemove) {
      if (isReadOnly.value) return;
      const idsToRemove = new Set(elementsToRemove.map(el => el.id));
      elements.value = elements.value.filter(el => !idsToRemove.has(el.id));
      if (selectedNode.value && idsToRemove.has(selectedNode.value.id)) {
          clearSelectedNode();
      }
      isModified.value = true;
    }

    function copyNode(node) {
        clipboard.value = JSON.parse(JSON.stringify(node));
        console.log('[WorkflowStore] Node copied to clipboard:', node.id);
    }

    function pasteNode({ x, y }) {
        const uiStore = useUiStore();
        if (isReadOnly.value) {
            uiStore.showNotification({ text: 'Cannot paste: Workflow is read-only.', color: 'warning' });
            return;
        }
        if (!clipboard.value) {
            console.warn('[WorkflowStore] Clipboard is empty.');
            return;
        }

        const nodeDataToPaste = JSON.parse(JSON.stringify(clipboard.value.data));
        const componentStore = useComponentStore();
        const component = componentStore.findComponentById(nodeDataToPaste.moduleId);

        if (!component) {
            console.error(`[WorkflowStore] Component not found for pasted node: ${nodeDataToPaste.moduleId}. Cannot paste.`);
            uiStore.showNotification({ text: `Cannot paste: Component '${nodeDataToPaste.moduleId}' not found.`, color: 'error' });
            return;
        }

        const defaultConfig = (component.manifest?.properties || []).reduce((acc, prop) => {
            if (prop.default !== undefined) {
              let defaultValue = prop.default;
              if (prop.type === 'integer' || prop.type === 'float') {
                  defaultValue = Number(defaultValue);
              } else if (prop.type === 'boolean') {
                  defaultValue = String(defaultValue).toLowerCase() === 'true';
              } else if (prop.type === 'list' && !Array.isArray(defaultValue)) {
                  defaultValue = [];
              }
              acc[prop.id] = defaultValue;
            }
            return acc;
        }, {});

        const newNode = {
            id: uuidv4(),
            type: 'default',
            label: clipboard.value.label,
            position: { x, y },
            data: {
              moduleId: nodeDataToPaste.moduleId,
              componentType: nodeDataToPaste.componentType,
              type: nodeDataToPaste.type, // V2 support for paste
              config_values: { ...defaultConfig, ...(nodeDataToPaste.config_values || {}) },
              color: nodeDataToPaste.color,
            },
        };
        elements.value = [...elements.value, newNode];
        console.log('[WorkflowStore] Node pasted from clipboard:', newNode.id);
        isModified.value = true;
    }

    function duplicateNode(node) {
        const uiStore = useUiStore();
        if (isReadOnly.value) {
            uiStore.showNotification({ text: 'Cannot duplicate: Workflow is read-only.', color: 'warning' });
            return;
        }
        const { x, y } = node.position;
        const offset = 40;
        copyNode(node);
        pasteNode({ x: x + offset, y: y + offset });
    }

    async function fetchPresets() {
        isLoadingPresets.value = true;
        try {
            console.log("[WorkflowStore] Requesting presets list from local engine via WebSocket...");
            const socketStore = useSocketStore();
            if (socketStore.isConnected) {
                await socketStore.sendMessage({ type: 'request_presets_list' });
            } else {
                console.warn("[WorkflowStore] Cannot fetch presets, socket not connected.");
                isLoadingPresets.value = false;
            }
        } catch (error) {
            console.error("[WorkflowStore] Failed to send preset list request via WebSocket:", error);
            presets.value = [];
            const uiStore = useUiStore();
            uiStore.showNotification({ text: 'Failed to request preset list.', color: 'error' });
            isLoadingPresets.value = false;
        }
    }

    function updatePresetsList(presetList) {
        console.log(`[WorkflowStore] Received ${presetList.length} presets from engine.`);
        presets.value = presetList.map(p => ({
             id: p.name,
             name: p.name
        }));
        isLoadingPresets.value = false;
    }

    function handleFetchError(errorMessage) {
        console.warn(`[WorkflowStore] Fetch presets failed: ${errorMessage}`);
        isLoadingPresets.value = false;
        error.value = errorMessage;
    }

    /**
     * [MANIFEST V2 UPDATE]
     * Handles dropping both legacy modules and new V2 nodes.
     * Extracts correct defaults from the specific node definition if V2.
     */
    function addNode(componentData) {
        const uiStore = useUiStore();
        if (isReadOnly.value) {
             uiStore.showNotification({ text: 'Cannot add node: Workflow is read-only.', color: 'warning' });
            return;
        }
        if (!componentData?.moduleId) {
            console.error('[WorkflowStore] addNode called without valid component data.');
            return;
        }

        const componentStore = useComponentStore();
        const fullComponentData = componentStore.findComponentById(componentData.moduleId);

        if (!fullComponentData) {
            console.error(`[WorkflowStore] Component with ID ${componentData.moduleId} not found in componentStore.`);
            uiStore.showNotification({ text: `Failed to add node: Component ${componentData.moduleId} not found.`, color: 'error'});
            return;
        }

        let nodeDefinition = fullComponentData.manifest; // Default to app-level config (Legacy)
        let nodeSpecificId = null;

        if (componentData.type === 'node_v2') {
            nodeSpecificId = componentData.id; // e.g. "email.send"
            const shortNodeId = nodeSpecificId.split('.').pop(); // "send"

            if (fullComponentData.manifest && fullComponentData.manifest.nodes) {
                const found = fullComponentData.manifest.nodes.find(n => n.id === shortNodeId);
                if (found) {
                    nodeDefinition = found;
                } else {
                    console.warn(`[WorkflowStore] Node definition '${shortNodeId}' not found in app manifest. Using default.`);
                }
            }
        }

        const schema = nodeDefinition.inputs || nodeDefinition.properties || [];

        const defaultConfig = schema.reduce((acc, prop) => {
            const key = prop.name || prop.id;

            if (prop.default !== undefined) {
                let defaultValue = prop.default;
                if (prop.type === 'integer' || prop.type === 'float' || prop.type === 'number') {
                    defaultValue = Number(defaultValue);
                } else if (prop.type === 'boolean' || prop.type === 'toggle') {
                    defaultValue = String(defaultValue).toLowerCase() === 'true';
                } else if ((prop.type === 'list' || prop.type === 'key-value') && !Array.isArray(defaultValue)) {
                    defaultValue = [];
                }
                acc[key] = defaultValue;
            }
            return acc;
        }, {});

        const newNode = {
            id: uuidv4(),
            type: 'default',
            label: componentData.label || nodeDefinition.name || fullComponentData.name,
            position: { x: componentData.x, y: componentData.y },
            data: {
                moduleId: fullComponentData.id,
                componentType: fullComponentData.componentType,
                type: nodeSpecificId || fullComponentData.id, // Store specific V2 ID if available
                config_values: defaultConfig,
            }
        };

        elements.value = [...elements.value, newNode];
        console.log(`[WorkflowStore] Added node: ${newNode.id} (${newNode.label})`);
        isModified.value = true;
    }

    function addEdge(connectionData) {
        const uiStore = useUiStore();
        if (isReadOnly.value) {
            uiStore.showNotification({ text: 'Cannot add connection: Workflow is read-only.', color: 'warning' });
            return;
        }
        const newEdge = {
            id: `edge-${uuidv4()}`,
            type: 'default',
            animated: true,
            source: connectionData.source,
            target: connectionData.target,
            sourceHandle: connectionData.sourceHandle,
            targetHandle: connectionData.targetHandle,
        };
        elements.value = [...elements.value, newEdge];
        console.log(`[WorkflowStore] Added edge from ${newEdge.source} to ${newEdge.target}`);
        isModified.value = true;
    }

    function setSelectedNode(node) {
        if (selectedNode.value?.id !== node.id) {
            selectedNode.value = node;
            console.log(`[WorkflowStore] Node selected: ${node.id}`);
        }
    }

    function clearSelectedNode() {
        if (selectedNode.value) {
            console.log(`[WorkflowStore] Node deselected: ${selectedNode.value.id}`);
            selectedNode.value = null;
        }
    }

    function updateNodeConfig({ nodeId, key, value }) {
        if (isReadOnly.value) return;
        const nodeIndex = elements.value.findIndex(el => el.id === nodeId && 'position' in el);
        if (nodeIndex !== -1) {
            if (!elements.value[nodeIndex].data.config_values) {
                elements.value[nodeIndex].data.config_values = {};
            }
            elements.value[nodeIndex].data.config_values[key] = value;
            console.log(`[WorkflowStore] Updated config '${key}' for node ${nodeId}`);
            isModified.value = true;
        } else {
             console.warn(`[WorkflowStore] Attempted to update config for non-existent node: ${nodeId}`);
        }
    }

    async function loadWorkflow(presetName, ownerId = null) {
        if (!presetName) return false;

        const uiStore = useUiStore();
        const socketStore = useSocketStore();

        try {
            console.log(`[WorkflowStore] Requesting workflow '${presetName}' data (Owner: ${ownerId || 'Self'}) from local engine...`);

            const componentStore = useComponentStore();
             if (componentStore.modules.items.length === 0 ||
                 componentStore.plugins.items.length === 0 ||
                 componentStore.tools.items.length === 0 ||
                 componentStore.triggers.items.length === 0)
             {
                 console.log("[WorkflowStore] Component lists seem empty, ensuring they are fetched before loading preset...");
                 await Promise.all([
                     componentStore.fetchComponentsForType('modules', { reset: true }),
                     componentStore.fetchComponentsForType('plugins', { reset: true }),
                     componentStore.fetchComponentsForType('tools', { reset: true }),
                     componentStore.fetchComponentsForType('triggers', { reset: true })
                 ]);
                 await delay(200);
             }


            if (socketStore.isConnected) {
                await socketStore.sendMessage({
                    type: 'load_preset',
                    name: presetName,
                    owner_id: ownerId
                });
                return true;
            } else {
                 console.error(`[WorkflowStore] Cannot load workflow '${presetName}', socket not connected.`);
                 uiStore.showConnectEngineDialog();
                 throw new Error("Socket not connected");
            }

        } catch (error) {
            console.error(`[WorkflowStore] Failed to send load request for workflow ${presetName}:`, error);
            uiStore.showNotification({ text: `Error loading workflow: ${error.message || error}`, color: 'error'});
            clearCanvas();
            return false;
        }
    }

     function updateSinglePresetData(presetName, presetData) {
        if (!presetData) {
             console.warn(`[WorkflowStore] Received empty data for preset '${presetName}'. Clearing canvas.`);
             clearCanvas();
             currentPresetName.value = presetName;
             const uiStore = useUiStore();
             uiStore.showNotification({ text: `Could not load data for '${presetName}'. It might be empty or corrupted.`, color: 'warning'});
             return;
        }
        console.log(`[WorkflowStore] Received data for preset '${presetName}'. Updating canvas...`);
        const componentStore = useComponentStore();

        const newNodes = (presetData.nodes || []).map(node => {
            const component = componentStore.findComponentById(node.module_id);
            if (!component) {
                console.warn(`[WorkflowStore] Component '${node.module_id}' for node '${node.name || node.id}' not found during preset load. Node may not function correctly.`);
            }
            const nodeConfig = node.config_values || {};

            let manifestProps = [];

            if (component?.manifest?.nodes) {
                const nodeTypeSuffix = node.type ? node.type.split('.').pop() : '';
                const v2Node = component.manifest.nodes.find(n => n.id === nodeTypeSuffix);
                if (v2Node && v2Node.inputs) {
                    manifestProps = v2Node.inputs;
                }
            }

            if (manifestProps.length === 0) {
                manifestProps = component?.manifest?.properties || [];
            }

            manifestProps.forEach(prop => {
                const key = prop.name || prop.id;
                if (!(key in nodeConfig) && prop.default !== undefined) {
                    let defaultValue = prop.default;
                     if (prop.type === 'integer' || prop.type === 'float' || prop.type === 'number') {
                         defaultValue = Number(defaultValue);
                     } else if (prop.type === 'boolean' || prop.type === 'toggle') {
                         defaultValue = String(defaultValue).toLowerCase() === 'true';
                     } else if ((prop.type === 'list' || prop.type === 'key-value') && !Array.isArray(defaultValue)) {
                         defaultValue = [];
                     }
                    nodeConfig[key] = defaultValue;
                }
            });


            return {
                id: node.id || uuidv4(),
                type: 'default',
                label: node.name || component?.name || node.module_id,
                position: { x: node.x || 0, y: node.y || 0 },
                data: {
                    moduleId: node.module_id,
                    componentType: component ? component.componentType : 'modules',
                    type: node.type || node.module_id, // Preserve V2 Type if present
                    config_values: nodeConfig,
                    color: node.data?.color,
                }
            }
        });

        const newConnections = (presetData.connections || []).map(conn => ({
            id: conn.id || `edge-${uuidv4()}`,
            type: conn.type || 'default',
            animated: conn.animated !== undefined ? conn.animated : true,
            source: conn.source || conn.from,
            target: conn.target || conn.to,
            sourceHandle: conn.source_port_name || conn.sourceHandle || null,
            targetHandle: conn.target_port_name || conn.targetHandle || null,
        }));

        executionStatus.value = {};
        connectionStatus.value = {};
        jobId.value = null;
        isExecuting.value = false;
        isPaused.value = false;
        isStopRequested.value = false;
        isModified.value = false;

        elements.value = [...newNodes, ...newConnections];

        if (!permissionLevel.value.startsWith('view')) {
             currentPresetName.value = presetName;
        }

        if (presetData.global_loop_config) {
            globalLoopConfig.value = { ...globalLoopConfig.value, ...presetData.global_loop_config };
        } else {
            globalLoopConfig.value = {
                isEnabled: false, iterations: 1, isDelayEnabled: false,
                delayType: 'static', delayStatic: 1, delayRandomMin: 1, delayRandomMax: 5
            };
        }

        clearSelectedNode();
        console.log(`[WorkflowStore] Workflow '${presetName}' loaded and rendered successfully.`);

    }

    async function loadSharedWorkflow(token) {
        error.value = null;
        const uiStore = useUiStore();
        uiStore.showNotification({ text: 'Loading shared workflow...', color: 'info' });
        try {
            const shareDetails = await apiResolveShareToken(token);
            if (shareDetails.error) throw new Error(shareDetails.error);

            const { preset_name: presetName, owner_id: ownerPublicAddress, permission_level: sharedPermission, workflow_name: sharedName } = shareDetails;

            const componentStore = useComponentStore();
             await Promise.all([
                 componentStore.fetchComponentsForType('modules', { reset: true }),
                 componentStore.fetchComponentsForType('plugins', { reset: true }),
                 componentStore.fetchComponentsForType('tools', { reset: true }),
                 componentStore.fetchComponentsForType('triggers', { reset: true })
             ]);
            await delay(200);

            const socketStore = useSocketStore();
            const engineStore = useEngineStore();

            const ownerEngine = engineStore.allAvailableEngines.find(e =>
                e.isOwner === false &&
                e.owner?.public_address?.toLowerCase() === ownerPublicAddress?.toLowerCase() &&
                e.status === 'online'
            );
            let targetEngineId = null;

            if (ownerEngine) {
                targetEngineId = ownerEngine.id;
                console.log(`[WorkflowStore] Found owner's online engine for shared workflow: ${targetEngineId}`);
            } else {
                targetEngineId = engineStore.selectedEngineId;
                if (targetEngineId) {
                     console.log(`[WorkflowStore] Owner engine not found/offline. Falling back to user's active engine: ${targetEngineId}`);
                } else {
                     throw new Error("No active engine (yours or the owner's) is available to load the shared workflow.");
                }
            }

            socketStore.switchEngine(targetEngineId);

            await new Promise(resolve => setTimeout(resolve, 1500));

            if (!socketStore.isConnected) {
                 throw new Error(`Failed to connect to the required engine (${targetEngineId.substring(0,8)}...).`);
            }

            const loadSuccess = await loadWorkflow(presetName, ownerPublicAddress);
            if (!loadSuccess) {
                 throw new Error(`Engine connected, but failed to load preset '${presetName}' from it.`);
            }

            permissionLevel.value = sharedPermission || 'view';
            currentPresetName.value = `Shared: ${sharedName || presetName}`;

            uiStore.showNotification({ text: `Shared workflow loaded (${permissionLevel.value} mode).`, color: 'success' });
            return true;
        } catch (e) {
            error.value = e.error || e.message || 'Failed to load shared workflow.';
            uiStore.showNotification({ text: error.value, color: 'error'});
            clearCanvas();
            return false;
        }
    }

    function sanitizeForFilename(name) {
        if (!name || typeof name !== 'string') return 'untitled_workflow';
        return name
            .trim()
            .replace(/[<>:"/\\|?*]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .substring(0, 50);
    }

    async function saveCurrentWorkflow(newPresetName) {
        if (isReadOnly.value) {
            const uiStore = useUiStore();
            uiStore.showNotification({ text: 'You do not have permission to save this workflow.', color: 'warning' });
            return false;
        }
        const uiStore = useUiStore();
        const socketStore = useSocketStore();
        const authStore = useAuthStore();

        if (!socketStore.isConnected) {
             uiStore.showConnectEngineDialog();
             return false;
        }

        if (!authStore.privateKey) {
             uiStore.showNotification({ text: 'Error: Private key not found. Cannot sign and save workflow.', color: 'error' });
            return false;
        }

        try {
            const sanitizedNameForRequest = sanitizeForFilename(newPresetName);
            if (!sanitizedNameForRequest) {
                uiStore.showNotification({ text: 'Invalid preset name.', color: 'error' });
                return false;
            }

            const workflowData = {
                nodes: elements.value.filter(el => 'position' in el).map(node => ({
                    id: node.id,
                    name: node.label,
                    x: node.position.x,
                    y: node.position.y,
                    module_id: node.data.moduleId,
                    type: node.data.type, // V2: Persist Type
                    config_values: node.data.config_values || {},
                    ...(node.data.color && { data: { color: node.data.color } })
                })),
                connections: elements.value.filter(el => 'source' in el).map(edge => ({
                    id: edge.id,
                    source: edge.source,
                    target: edge.target,
                    source_port_name: edge.sourceHandle,
                    target_port_name: edge.targetHandle,
                    type: edge.type,
                    animated: edge.animated,
                })),
                 global_loop_config: globalLoopConfig.value
            };

            const wallet = new ethers.Wallet(authStore.privateKey);
            const unsignedDataBlock = {
                "workflow_data": workflowData
            };
            const messageToSign = stableStringify(unsignedDataBlock);
            const dataSignature = await wallet.signMessage(messageToSign);

            const payload = {
                type: 'save_preset',
                name: sanitizedNameForRequest,
                workflow_data: workflowData,
                signature: dataSignature
            };

            console.log('[WorkflowStore] Preparing to send save payload:', JSON.stringify(payload, null, 2));

            await socketStore.sendMessage(payload);

            currentPresetName.value = newPresetName;
            isModified.value = false;
            uiStore.showNotification({ text: `Workflow '${newPresetName}' save request sent.`, color: 'success' });
            await fetchPresets();
            return true;

        } catch (error) {
            console.error(`[WorkflowStore] Failed to save workflow as ${newPresetName}:`, error);
            uiStore.showNotification({ text: `Error saving workflow: ${error.message || error}`, color: 'error' });
            return false;
        }
    }

    async function deletePresetAction(presetName) {
        const uiStore = useUiStore();
        if (isReadOnly.value) {
             uiStore.showNotification({ text: 'Cannot delete: Workflow is read-only.', color: 'warning' });
             return false;
        }
        const socketStore = useSocketStore();

        if (!socketStore.isConnected) {
             uiStore.showConnectEngineDialog();
             return false;
        }

        try {
             const presetToDelete = presets.value.find(p => p.id === presetName);
             if (!presetToDelete) throw new Error("Preset not found in local list.");

            await socketStore.sendMessage({ type: 'delete_preset', name: presetToDelete.id });

            if (currentPresetName.value === presetName) {
                clearCanvas();
            }

            uiStore.showNotification({ text: `Preset '${presetName}' delete request sent.`, color: 'info' });
            await fetchPresets();
            return true;
        } catch (error) {
            console.error(`[WorkflowStore] Failed to delete preset ${presetName}:`, error);
            uiStore.showNotification({ text: `Error deleting preset: ${error.message || error}`, color: 'error' });
            return false;
        }
    }

    function clearCanvas() {
        elements.value = [];
        selectedNode.value = null;
        currentPresetName.value = null;
        executionStatus.value = {};
        connectionStatus.value = {};
        permissionLevel.value = 'edit';
        jobId.value = null;
        isExecuting.value = false;
        isPaused.value = false;
        isStopRequested.value = false;
        isModified.value = false;
        globalLoopConfig.value = {
            isEnabled: false, iterations: 1, isDelayEnabled: false,
            delayType: 'static', delayStatic: 1, delayRandomMin: 1, delayRandomMax: 5
        };
        console.log("[WorkflowStore] Canvas cleared.");
    }

    function applyAutoLayout(updatedNodes) {
        if (isReadOnly.value) return;
        if (!Array.isArray(updatedNodes)) {
             console.warn("[WorkflowStore] applyAutoLayout received invalid data:", updatedNodes);
            return;
        }
        const nodeMap = new Map(updatedNodes.map(n => [n.id, n.position]));

        const newElements = elements.value.map(el => {
            if ('position' in el && nodeMap.has(el.id)) {
                return { ...el, position: nodeMap.get(el.id) };
            }
            return el;
        });

        elements.value = newElements;
        isModified.value = true;
        console.log("[WorkflowStore] Applied auto-layout positions.");
    }

    async function _startExecutionLoop(startNodeId = null, mode = 'EXECUTE') {
        const uiStore = useUiStore();
        const socketStore = useSocketStore();

        if (!socketStore.isConnected) {
            uiStore.showConnectEngineDialog();
            return;
        }

        if (isExecuting.value) {
            console.warn("[WorkflowStore] Execution already in progress.");
            return;
        }

        if (!canExecute.value) {
            if (isCanvasEmpty.value) {
                uiStore.showNotification({ text: 'Cannot run an empty workflow. Add some nodes first!', color: 'warning' });
            } else if (isReadOnly.value && mode === 'EXECUTE') {
                uiStore.showNotification({ text: 'You do not have permission to run this workflow.', color: 'warning' });
            } else if (isReadOnly.value && mode === 'SIMULATE') {
                 console.log("[WorkflowStore] Allowing SIMULATE in read-only mode.");
            } else {
                 uiStore.showNotification({ text: 'Cannot execute workflow at this time.', color: 'warning' });
            }
            if (!(isReadOnly.value && mode === 'SIMULATE')) {
                 return;
            }
        }

        const logStore = useLogStore();

        let nodesToExecute, connectionsToExecute;
        let effectivePresetName = currentPresetName.value || 'unsaved-workflow';

        nodesToExecute = nodes.value.map(node => ({
            id: node.id,
            name: node.label,
            x: node.position.x,
            y: node.position.y,
            module_id: node.data.moduleId,
            type: node.data.type, // V2 Execution ID
            config_values: node.data.config_values || {},
            ...(node.data.color && { data: { color: node.data.color } })
        }));
        connectionsToExecute = edges.value.map(edge => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
            source_port_name: edge.sourceHandle,
            target_port_name: edge.targetHandle,
            type: edge.type,
            animated: edge.animated,
        }));

        isExecuting.value = true;
        isPaused.value = false;
        isStopRequested.value = false;
        logStore.clearLogs();
        executionStatus.value = {};
        connectionStatus.value = {};

        const newJobId = uuidv4();
        jobId.value = newJobId;

        const notificationText = mode === 'SIMULATE'
            ? `Simulating '${effectivePresetName}'...`
            : `Executing '${effectivePresetName}'...`;
        uiStore.showNotification({ text: notificationText, color: 'info' });

        const payload = {
            type: 'execute_workflow',
            job_id: newJobId,
            preset_name: effectivePresetName,
            workflow_data: {
                nodes: nodesToExecute,
                connections: connectionsToExecute,
                global_loop_config: globalLoopConfig.value
            },
            initial_payload: {},
            start_node_id: startNodeId,
            mode: mode,
        };

        console.log('[WorkflowStore] Preparing to send execution payload:', JSON.stringify(payload, null, 2));

        try {
            await socketStore.sendMessage(payload);
            console.log(`[WorkflowStore] ${mode} request sent for job ${newJobId}`);
        } catch (error) {
             console.error(`[WorkflowStore] Failed to send ${mode} request:`, error);
             uiStore.showNotification({ text: `Failed to start ${mode.toLowerCase()}: ${error.message || error}`, color: 'error'});
             isExecuting.value = false;
             jobId.value = null;
        }
    }

    async function executePresetByName(presetName) {
        const uiStore = useUiStore();
        const socketStore = useSocketStore();

        if (!socketStore.isConnected) {
            uiStore.showConnectEngineDialog();
            return;
        }

        if (isExecuting.value) {
            console.warn("[WorkflowStore] Execution already in progress.");
            uiStore.showNotification({ text: 'Another workflow is already running.', color: 'warning' });
            return;
        }

        uiStore.showNotification({ text: `Loading & running '${presetName}'...`, color: 'info' });

        try {
            const loadRequestSent = await loadWorkflow(presetName);

            if (!loadRequestSent) {
                return;
            }

            const targetPresetName = presetName;

            await new Promise((resolve, reject) => {
                const unwatch = watch(currentPresetName, (newName) => {
                    if (newName === targetPresetName) {
                        unwatch();
                        nextTick(() => {
                            console.log(`[WorkflowStore] Quick Run: Preset '${targetPresetName}' loaded. Starting execution...`);
                            resolve();
                        });
                    }
                });

                setTimeout(() => {
                    unwatch();
                    if (!isExecuting.value && currentPresetName.value !== targetPresetName) {
                         console.error(`[WorkflowStore] Quick Run: Timeout waiting for preset '${targetPresetName}' to load.`);
                         reject(new Error(`Timeout loading data for '${targetPresetName}'. Aborted run.`));
                    } else {
                         resolve();
                    }
                }, 10000);
            });

            _startExecutionLoop(null, 'EXECUTE');

        } catch (error) {
            console.error(`[WorkflowStore] Quick Run failed for '${presetName}':`, error);
            uiStore.showNotification({ text: `Failed to start Quick Run: ${error.message || error}`, color: 'error'});
        }
    }

    function executeCurrentWorkflow(startNodeId = null) {
        _startExecutionLoop(startNodeId, 'EXECUTE');
    }

    function simulateCurrentWorkflow(startNodeId = null) {
        _startExecutionLoop(startNodeId, 'SIMULATE');
    }

    function updateExecutionStatus(data) {
        const statusData = data.status_data || {};
        const receivedJobId = data.job_id;
        const jobStatus = statusData.status?.toUpperCase();

        console.log(`[WorkflowStore] Received status update for job ${receivedJobId}: ${jobStatus}`);

        const isCurrentJob = receivedJobId === jobId.value;
        const isTerminalStatus = ['SUCCEEDED', 'FAILED', 'STOPPED'].includes(jobStatus);
        const isCurrentlyExecuting = isExecuting.value;

        if (isCurrentJob || (isTerminalStatus && isCurrentlyExecuting)) {

            if (jobStatus === 'RUNNING') {
                isExecuting.value = true;
                isPaused.value = false;
                if (!isCurrentJob) jobId.value = receivedJobId;
                isStopRequested.value = false;
            } else if (jobStatus === 'PAUSED') {
                isPaused.value = true;
                isExecuting.value = true;
            } else if (isTerminalStatus) {
                const uiStore = useUiStore();
                 let notificationColor = 'info';
                 let notificationText = `Run finished with status: ${jobStatus}`;

                if (jobStatus === 'SUCCEEDED') {
                     notificationColor = 'success';
                     notificationText = `Run finished successfully.`;
                } else if (jobStatus === 'FAILED') {
                    notificationColor = 'error';
                    notificationText = `Run failed: ${statusData.error || 'Unknown error'}`;
                } else if (jobStatus === 'STOPPED') {
                    notificationColor = 'warning';
                    notificationText = `Run was stopped.`;
                }

                if (isCurrentJob) {
                    uiStore.showNotification({ text: notificationText, color: notificationColor });
                } else if (isCurrentlyExecuting) {
                    uiStore.showNotification({ text: `Forcing UI reset. Received terminal status from a different job.`, color: 'warning' });
                    console.warn(`[WorkflowStore] Force resetting UI state. Was tracking job ${jobId.value} but received terminal status for ${receivedJobId}.`);
                }

                isExecuting.value = false;
                isPaused.value = false;
                isStopRequested.value = false;
                jobId.value = null;
                 console.log(`[WorkflowStore] Resetting execution state due to terminal status: ${jobStatus}`);
            }
        } else {
             console.log(`[WorkflowStore] Ignoring status update for different job: ${receivedJobId} (current: ${jobId.value})`);
        }
    }

    function updateNodeExecutionStatus(metric) {
        if (!metric?.node_id) return;

        executionStatus.value = {
            ...executionStatus.value,
            [metric.node_id]: {
                status: metric.status,
                timestamp: metric.timestamp
            }
        };
    }

    async function stopCurrentWorkflow() {
        if (!jobId.value) {
            console.warn("[WorkflowStore] No active job ID to stop.");
            if (isExecuting.value) {
                isExecuting.value = false;
                isPaused.value = false;
                 console.warn("[WorkflowStore] UI was stuck in executing state, forcing reset.");
            }
            return;
        }
        if (!isExecuting.value) {
            console.warn("[WorkflowStore] Workflow is not currently executing, cannot stop.");
            return;
        }
        isStopRequested.value = true;
        const uiStore = useUiStore();
        try {
            console.log(`[WorkflowStore] Sending stop request for job: ${jobId.value}`);
            const socketStore = useSocketStore();
            await socketStore.sendMessage({ type: 'stop_workflow', job_id: jobId.value });
            uiStore.showNotification({ text: 'Stop signal sent to workflow.', color: 'warning' });
        } catch (error) {
            uiStore.showNotification({ text: `Failed to send stop signal: ${error.message || error}`, color: 'error' });
            isStopRequested.value = false;
        }
    }

    async function stopJobById(jobIdToStop) {
        if (!jobIdToStop) return;
        const uiStore = useUiStore();
        try {
            console.log(`[WorkflowStore] Sending stop request for specific job: ${jobIdToStop}`);
            const socketStore = useSocketStore();
            await socketStore.sendMessage({ type: 'stop_workflow', job_id: jobIdToStop });
            uiStore.showNotification({ text: `Stop signal sent to job ${jobIdToStop.substring(0,8)}...`, color: 'warning' });
        } catch (error) {
            uiStore.showNotification({ text: `Failed to send stop signal: ${error.message || error}`, color: 'error' });
        }
    }

    async function pauseCurrentWorkflow() {
        if (!jobId.value) {
             console.warn("[WorkflowStore] No active job ID to pause.");
            return;
        }
        if (!isExecuting.value || isPaused.value) {
            console.warn("[WorkflowStore] Workflow not running or already paused, cannot pause.");
            return;
        }
        const uiStore = useUiStore();
        try {
            console.log(`[WorkflowStore] Sending pause request for job: ${jobId.value}`);
            const socketStore = useSocketStore();
            await socketStore.sendMessage({ type: 'pause_workflow', job_id: jobId.value });
            uiStore.showNotification({ text: 'Pause signal sent.', color: 'info' });
        } catch (error) {
            uiStore.showNotification({ text: `Failed to pause workflow: ${error.message || error}`, color: 'error' });
        }
    }

    async function resumeCurrentWorkflow() {
        if (!jobId.value) {
            console.warn("[WorkflowStore] No active job ID to resume.");
            return;
        }
        if (!isExecuting.value || !isPaused.value) {
            console.warn("[WorkflowStore] Workflow not paused, cannot resume.");
            return;
        }
        const uiStore = useUiStore();
        try {
            console.log(`[WorkflowStore] Sending resume request for job: ${jobId.value}`);
            const socketStore = useSocketStore();
            await socketStore.sendMessage({ type: 'resume_workflow', job_id: jobId.value });
            uiStore.showNotification({ text: 'Resume signal sent.', color: 'info' });
        } catch (error) {
            uiStore.showNotification({ text: `Failed to resume workflow: ${error.message || error}`, color: 'error' });
        }
    }

    return {
        elements, selectedNode, currentPresetName, isExecuting, jobId, executionStatus, presets, clipboard,
        isPaused, connectionStatus, globalLoopConfig, permissionLevel, error, favoritePresets,
        isModified,
        nodes, edges, isCanvasEmpty, isReadOnly, canExecute, selectedNodeHasBehavior,
        getWorkflowForPublishing,
        fetchPresets, updatePresetsList,
        loadWorkflow, updateSinglePresetData, loadSharedWorkflow,
        saveCurrentWorkflow, deletePresetAction,
        clearCanvas, applyAutoLayout,
        addNode, addEdge, setSelectedNode, clearSelectedNode, updateNodeConfig,
        removeElements, copyNode, pasteNode, duplicateNode, setNodeColor,
        toggleFavorite, fetchUserFavorites,
        fetchConnectionData, updateConnectionStatus,
        executeCurrentWorkflow, simulateCurrentWorkflow, executePresetByName,
        updateExecutionStatus, updateNodeExecutionStatus,
        stopCurrentWorkflow, pauseCurrentWorkflow, resumeCurrentWorkflow, stopJobById,
        applyChanges,
        isLoadingPresets,
        handleFetchError,
        animateIncomingEdges
    };
});
