//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\MyEngines.vue total lines 677 
//#######################################################################

<template>
  <div class="my-engines-page">
    <NeuralCanvasBackground />
    <div class="vignette-overlay"></div>
    <div class="scanline-overlay"></div>

    <v-container fluid class="fill-height pa-0 relative z-10 layout-fix">
      <div class="d-flex flex-column fill-height w-100 pa-4" style="padding-top: 80px !important;">
        <v-card class="reactor-main-panel d-flex flex-column flex-grow-1 overflow-hidden w-100">

            <div class="reactor-header d-flex justify-space-between align-center pa-5 flex-shrink-0">
                <div class="d-flex align-center">
                    <div class="header-deco-box mr-4">
                        <v-icon icon="mdi-server-network" color="amber-darken-1" size="32" class="spin-slow"></v-icon>
                    </div>
                    <div>
                        <div class="text-h5 font-weight-black text-white orbitron-font tracking-wide text-shadow-glow">
                            ENGINE <span class="text-amber-darken-1">REACTOR_BAY</span>
                        </div>
                        <div class="d-flex align-center gap-3 mt-1 font-mono text-caption text-grey">
                            <span class="d-flex align-center"><div class="status-led on mr-2"></div> SYSTEM_STATUS: OPTIMAL</span>
                            <span class="text-grey-darken-2">|</span>
                            <span>SLOTS_USED: {{ ownedEngines.length }} / {{ maxSlots }}</span>
                        </div>
                    </div>
                </div>

                <div class="d-flex align-center gap-4">
                    <v-btn
                        height="44"
                        class="deploy-btn font-mono font-weight-bold"
                        @click="openRegisterDialog"
                    >
                        <v-icon start icon="mdi-plus-thick"></v-icon> DEPLOY_NEW_CORE
                    </v-btn>
                </div>
            </div>

            <div class="server-rack-scroll custom-scrollbar pa-6 flex-grow-1">

                <div v-if="isLoading" class="d-flex flex-column align-center justify-center py-16 fill-height">
                    <div class="reactor-loader mb-4"></div>
                    <div class="font-mono text-amber-darken-2 blink">INITIALIZING REACTOR SEQUENCE...</div>
                </div>

                <div v-else-if="error" class="d-flex flex-column align-center justify-center py-16 fill-height">
                    <div class="error-box d-inline-block pa-6 text-center">
                        <v-icon icon="mdi-alert-octagon" size="64" color="red-accent-2" class="mb-4"></v-icon>
                        <div class="text-h6 font-mono text-red-accent-2">CONNECTION_FAILURE</div>
                        <div class="text-caption text-grey-lighten-1 mb-4">{{ error }}</div>
                        <v-btn color="red-darken-4" variant="outlined" @click="refreshData">RETRY UPLINK</v-btn>
                    </div>
                </div>

                <div v-else>
                    <div class="mb-10">
                        <div class="section-label mb-4">
                            <v-icon icon="mdi-expansion-card-variant" color="amber-darken-1" size="small" class="mr-2"></v-icon>
                            <span class="orbitron-font text-amber-darken-1">PRIMARY_RACK_UNIT (16-CORE)</span>
                            <div class="line-extender"></div>
                        </div>

                        <div class="engine-grid">
                            <div
                                v-for="(slot, index) in reactorSlots"
                                :key="slot.isPlaceholder ? 'slot-'+index : slot.id"
                                class="reactor-unit-wrapper"
                            >
                                <div
                                    v-if="!slot.isPlaceholder"
                                    class="reactor-unit"
                                    :class="getReactorClass(slot)"
                                    @click="handleConnectEngine(slot)"
                                >
                                    <div class="status-light-bar"></div>

                                    <div class="unit-header d-flex justify-space-between align-start">
                                        <div class="text-truncate pr-2 w-100">
                                            <div class="font-mono text-caption text-grey-darken-1 mb-1">UNIT_{{ (index + 1).toString().padStart(2, '0') }}</div>
                                            <div class="text-h6 font-weight-bold text-white orbitron-font text-truncate">{{ slot.name }}</div>
                                        </div>
                                        <div class="status-badge" :class="slot.status">
                                            {{ slot.status === 'online' ? 'ONLINE' : 'OFFLINE' }}
                                        </div>
                                    </div>

                                    <div class="reactor-core-display">
                                        <div class="core-ring" :class="{'spinning': true, 'fast': slot.status === 'online'}"></div>
                                        <div class="core-energy"></div>
                                        <div class="core-icon-wrapper">
                                            <v-icon :icon="slot.status === 'online' ? 'mdi-fan' : 'mdi-fan-off'" size="x-large" :class="{'spin-fan': slot.status === 'online'}"></v-icon>
                                        </div>
                                    </div>

                                    <div class="vitals-panel">
                                        <div v-if="slot.status === 'online'">
                                            <div class="d-flex justify-space-between text-caption2 font-mono text-grey mb-1">
                                                <span>PRESSURE (CPU)</span>
                                                <span :class="getLoadColor(slot.vitals?.cpu_percent)">{{ (slot.vitals?.cpu_percent || 0).toFixed(0) }}%</span>
                                            </div>
                                            <div class="meter-bar-bg mb-2">
                                                <div class="meter-bar-fill" :style="{ width: (slot.vitals?.cpu_percent || 0) + '%', backgroundColor: getLoadColorHex(slot.vitals?.cpu_percent) }"></div>
                                            </div>

                                            <div class="d-flex justify-space-between text-caption2 font-mono text-grey mb-1">
                                                <span>CAPACITY (RAM)</span>
                                                <span :class="getLoadColor(slot.vitals?.ram_percent)">{{ (slot.vitals?.ram_percent || 0).toFixed(0) }}%</span>
                                            </div>
                                            <div class="meter-bar-bg">
                                                <div class="meter-bar-fill" :style="{ width: (slot.vitals?.ram_percent || 0) + '%', backgroundColor: getLoadColorHex(slot.vitals?.ram_percent) }"></div>
                                            </div>
                                        </div>
                                        <div v-else class="offline-readout">
                                            <span class="blink-slow text-red-darken-1">/// SIGNAL_LOST ///</span>
                                        </div>
                                    </div>

                                    <div class="unit-footer d-flex justify-space-between align-center">
                                        <v-btn
                                            v-if="!isEngineSelected(slot.id)"
                                            size="small"
                                            variant="flat"
                                            class="action-btn connect-btn"
                                            :disabled="slot.status !== 'online'"
                                            @click.stop="handleConnectEngine(slot)"
                                        >
                                            <v-icon start icon="mdi-power-plug" size="x-small"></v-icon> ENGAGE
                                        </v-btn>
                                        <v-btn
                                            v-else
                                            size="small"
                                            variant="tonal"
                                            color="green-accent-3"
                                            class="font-weight-bold font-mono"
                                            readonly
                                        >
                                            <v-icon start icon="mdi-check-circle"></v-icon> ACTIVE
                                        </v-btn>

                                        <v-menu location="top end" content-class="cyber-menu">
                                            <template v-slot:activator="{ props }">
                                                <v-btn icon="mdi-cog" variant="text" size="small" v-bind="props" color="grey-darken-1" class="settings-btn"></v-btn>
                                            </template>
                                            <v-list density="compact" bg-color="#111" class="border-amber-thin">
                                                <v-list-item @click="openShareDialog(slot)" prepend-icon="mdi-access-point-network">
                                                    <v-list-item-title class="font-mono text-caption">ACCESS_CONTROL</v-list-item-title>
                                                </v-list-item>
                                                <v-list-item @click="openRenameDialog(slot)" prepend-icon="mdi-pencil-box-outline">
                                                    <v-list-item-title class="font-mono text-caption">RENAME_UNIT</v-list-item-title>
                                                </v-list-item>
                                                <v-list-item @click="handleResetToken(slot)" prepend-icon="mdi-key-wireless">
                                                    <v-list-item-title class="font-mono text-caption">REKEY_AUTH</v-list-item-title>
                                                </v-list-item>
                                                <v-divider class="border-subtle"></v-divider>
                                                <v-list-item @click="handleDeleteEngine(slot)" prepend-icon="mdi-nuke" class="text-red-accent-2">
                                                    <v-list-item-title class="font-mono text-caption">DECOMMISSION</v-list-item-title>
                                                </v-list-item>
                                            </v-list>
                                        </v-menu>
                                    </div>
                                </div>

                                <div
                                    v-else
                                    class="reactor-unit placeholder-unit"
                                    @click="openRegisterDialog"
                                >
                                    <div class="placeholder-content">
                                        <div class="slot-id font-mono">SLOT_{{ (index + 1).toString().padStart(2, '0') }}</div>
                                        <div class="empty-icon-wrapper">
                                            <v-icon icon="mdi-plus" size="large" color="grey-darken-3"></v-icon>
                                        </div>
                                        <div class="text-caption font-mono text-grey-darken-3 mt-2">EMPTY_BAY</div>
                                        <div class="deploy-text text-amber-darken-3 mt-1">CLICK_TO_DEPLOY</div>
                                    </div>
                                    <div class="scan-line-decoration"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-if="sharedWithMeEngines.length > 0">
                        <div class="section-label mb-4">
                            <v-icon icon="mdi-earth" color="cyan-darken-1" size="small" class="mr-2"></v-icon>
                            <span class="orbitron-font text-cyan-darken-1">EXTERNAL_UPLINKS</span>
                            <div class="line-extender-cyan"></div>
                        </div>

                        <div class="engine-grid">
                            <div
                                v-for="engine in sharedWithMeEngines"
                                :key="engine.id"
                                class="reactor-unit unit-shared"
                                :class="getReactorClass(engine)"
                                @click="handleConnectEngine(engine)"
                            >
                                <div class="status-light-bar-cyan"></div>

                                <div class="unit-header d-flex justify-space-between align-start">
                                    <div class="text-truncate pr-2 w-100">
                                        <div class="font-mono text-caption text-grey-darken-1 mb-1">HOST: {{ engine.owner?.username || 'UNKNOWN' }}</div>
                                        <div class="text-h6 font-weight-bold text-white orbitron-font text-truncate">{{ engine.name }}</div>
                                    </div>
                                    <div class="status-badge" :class="engine.status">
                                        {{ engine.status === 'online' ? 'LIVE' : 'OFF' }}
                                    </div>
                                </div>

                                <div class="reactor-core-display">
                                    <div class="core-ring ring-cyan spinning fast"></div>
                                    <div class="core-energy energy-cyan"></div>
                                    <div class="core-icon-wrapper">
                                        <v-icon :icon="engine.status === 'online' ? 'mdi-access-point' : 'mdi-access-point-off'" size="x-large" :class="{'pulse-cyan': engine.status === 'online'}"></v-icon>
                                    </div>
                                </div>

                                <div class="vitals-panel">
                                    <div v-if="engine.status === 'online'">
                                        <div class="d-flex justify-space-between text-caption2 font-mono text-grey mb-1">
                                            <span>CORE_LOAD</span>
                                            <span>{{ (engine.vitals?.cpu_percent || 0).toFixed(0) }}%</span>
                                        </div>
                                        <div class="meter-bar-bg mb-2">
                                            <div class="meter-bar-fill fill-cyan" :style="{ width: (engine.vitals?.cpu_percent || 0) + '%' }"></div>
                                        </div>
                                    </div>
                                    <div v-else class="offline-readout">
                                        <span class="blink-slow text-grey-darken-1">LINK_DOWN</span>
                                    </div>
                                </div>

                                <div class="unit-footer d-flex justify-space-between align-center">
                                    <v-btn
                                        v-if="!isEngineSelected(engine.id)"
                                        size="small"
                                        variant="flat"
                                        class="action-btn connect-btn-cyan"
                                        :disabled="engine.status !== 'online'"
                                        @click.stop="handleConnectEngine(engine)"
                                    >
                                        <v-icon start icon="mdi-connection" size="x-small"></v-icon> LINK
                                    </v-btn>
                                    <v-btn
                                        v-else
                                        size="small"
                                        variant="tonal"
                                        color="cyan-accent-3"
                                        class="font-weight-bold font-mono"
                                        readonly
                                    >
                                        <v-icon start icon="mdi-check-all"></v-icon> LINKED
                                    </v-btn>

                                    <v-tooltip text="Sever Uplink" location="top" content-class="cyber-tooltip">
                                        <template v-slot:activator="{ props }">
                                            <v-btn icon="mdi-link-off" variant="text" size="small" v-bind="props" color="grey-darken-1" @click.stop="handleLeaveEngine(engine)"></v-btn>
                                        </template>
                                    </v-tooltip>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </v-card>
      </div>
    </v-container>

    <v-dialog v-model="isRegisterDialogOpen" max-width="500px" persistent>
      <v-card class="pro-dialog-card">
        <div class="dialog-header">
            <span class="text-subtitle-2 font-weight-bold font-mono text-amber-darken-1">DEPLOY NEW REACTOR</span>
        </div>
        <v-card-text class="pa-4">
          <p class="text-caption mb-3 font-mono text-grey-lighten-1">Initialize new processing node parameters.</p>
          <v-text-field
            v-model="newEngineName"
            label="NODE_IDENTIFIER"
            variant="outlined"
            autofocus
            hide-details
            bg-color="rgba(255,255,255,0.05)"
            color="amber-darken-1"
            class="font-mono terminal-input-field"
            @keyup.enter="confirmRegisterEngine"
          ></v-text-field>
        </v-card-text>
        <v-card-actions class="pa-4 pt-0 justify-end">
          <v-btn color="grey" variant="text" @click="isRegisterDialogOpen = false" class="font-mono">ABORT</v-btn>
          <v-btn color="amber-darken-1" variant="flat" @click="confirmRegisterEngine" :loading="isLoading" class="font-mono font-weight-bold text-black">
            INITIALIZE
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="isRenameDialogOpen" max-width="400px">
        <v-card class="pro-dialog-card">
            <div class="dialog-header"><span class="font-mono text-white">RENAME_NODE</span></div>
            <v-card-text class="pa-4">
                <v-text-field v-model="renameEngineName" variant="outlined" density="compact" hide-details class="font-mono terminal-input-field"></v-text-field>
            </v-card-text>
            <v-card-actions class="pa-4 pt-0 justify-end">
                <v-btn color="amber-darken-1" variant="tonal" @click="confirmRenameEngine">UPDATE</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-dialog v-model="isShareDialogOpen" max-width="600px">
        <v-card class="pro-dialog-card">
            <div class="dialog-header"><span class="font-mono text-white">ACCESS_CONTROL</span></div>
            <v-card-text class="pa-4">
                <div class="d-flex gap-2 mb-4">
                    <v-text-field v-model="newShareIdentifier" placeholder="User Public Address" variant="outlined" density="compact" hide-details class="font-mono terminal-input-field flex-grow-1"></v-text-field>
                    <v-btn color="amber-darken-1" variant="flat" @click="handleGrantShare" :loading="isShareLoading" class="font-mono">GRANT</v-btn>
                </div>
                <div class="text-caption font-mono text-grey mb-2">ACTIVE_SHARES</div>
                <div v-if="sharesForEngine.length === 0" class="text-center pa-2 text-grey-darken-2 font-mono text-caption">NONE</div>
                <div v-else class="share-list">
                    <div v-for="share in sharesForEngine" :key="share.user_id" class="d-flex justify-space-between align-center py-2 border-bottom-subtle">
                        <span class="font-mono text-caption text-white">{{ share.username || share.public_address }}</span>
                        <v-btn icon="mdi-close" size="x-small" variant="text" color="red" @click="handleRevokeShare(share.user_id)"></v-btn>
                    </div>
                </div>
            </v-card-text>
        </v-card>
    </v-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useEngineStore } from '@/store/engines';
import { useUiStore } from '@/store/ui';
import { storeToRefs } from 'pinia';
import { apiUpdateEngine, apiResetEngineToken } from '@/api';
import NeuralCanvasBackground from '@/components/NeuralCanvasBackground.vue';

const uiStore = useUiStore();
const engineStore = useEngineStore();

const { allAvailableEngines, isLoading, error, selectedEngineId } = storeToRefs(engineStore);
const ownedEngines = computed(() => allAvailableEngines.value.filter(e => e.isOwner));
const sharedWithMeEngines = computed(() => allAvailableEngines.value.filter(e => !e.isOwner));

const maxSlots = 16;
const reactorSlots = computed(() => {
    const slots = [...ownedEngines.value];
    const placeholdersCount = Math.max(0, maxSlots - slots.length);

    for (let i = 0; i < placeholdersCount; i++) {
        slots.push({ isPlaceholder: true });
    }
    return slots;
});

const isRegisterDialogOpen = ref(false);
const newEngineName = ref('');
const isRenameDialogOpen = ref(false);
const engineToRename = ref(null);
const renameEngineName = ref('');
const isShareDialogOpen = ref(false);
const engineToManageShares = ref(null);
const sharesForEngine = ref([]);
const newShareIdentifier = ref('');
const newShareRole = ref('reader');
const isShareLoading = ref(false);

const refreshData = () => { engineStore.fetchEngines(); };
function isEngineSelected(id) { return selectedEngineId.value === id; }

async function handleConnectEngine(engine) {
    if (engine.isPlaceholder) {
        openRegisterDialog();
        return;
    }
    if (engine.status !== 'online') {
        uiStore.showNotification({ text: 'Node OFFLINE. Cannot engage.', color: 'red-darken-4' });
        return;
    }
    if (isEngineSelected(engine.id)) return;
    await engineStore.setSelectedEngineId(engine.id, true);
    uiStore.showNotification({ text: `Engine '${engine.name}' engaged.`, color: 'amber-darken-4' });
}

function getReactorClass(engine) {
    if (isEngineSelected(engine.id)) return 'reactor-active';
    if (engine.status === 'online') return 'reactor-online';
    return 'reactor-offline';
}

function getLoadColor(val) {
    if (!val) return 'text-grey-darken-1';
    if (val > 80) return 'text-red-accent-2';
    if (val > 50) return 'text-amber-accent-2';
    return 'text-green-accent-3';
}
function getLoadColorHex(val) {
    if (!val) return '#333';
    if (val > 80) return '#FF5252';
    if (val > 50) return '#FFAB40';
    return '#69F0AE';
}

function openRegisterDialog() { newEngineName.value = ''; isRegisterDialogOpen.value = true; }
async function confirmRegisterEngine() {
  if (newEngineName.value.trim()) {
    const success = await engineStore.registerEngine(newEngineName.value.trim());
    if (success) isRegisterDialogOpen.value = false;
  }
}

async function handleDeleteEngine(engine) {
    const confirmed = await uiStore.showConfirmation({
        title: 'CONFIRM DECOMMISSION',
        text: `Permanently remove reactor "${engine.name}"? This will sever all connections.`,
        color: 'error',
        confirmText: 'NUKE IT'
    });
    if (confirmed) await engineStore.deleteEngine(engine.id);
}

async function handleLeaveEngine(engine) {
    const confirmed = await uiStore.showConfirmation({
        title: 'SEVER UPLINK',
        text: `Disconnect from shared node "${engine.name}"?`,
        color: 'warning',
        confirmText: 'DISCONNECT'
    });
}

async function handleResetToken(engine) {
    const confirmed = await uiStore.showConfirmation({
        title: 'REKEY AUTHENTICATION',
        text: `Regenerate secure token for "${engine.name}"? Existing connections will terminate.`,
        color: 'warning',
        confirmText: 'REKEY'
    });
    if (confirmed) {
        try {
            const response = await apiResetEngineToken(engine.id);
            uiStore.showTokenDialog({
                title: 'NEW ACCESS CREDENTIALS',
                text: 'UPDATE .ENV CONFIGURATION:',
                items: [ { label: 'FLOWORK_ENGINE_ID', value: response.engine_id }, { label: 'FLOWORK_ENGINE_TOKEN', value: response.token } ]
            });
        } catch (e) {}
    }
}

function openRenameDialog(engine) { engineToRename.value = engine; renameEngineName.value = engine.name; isRenameDialogOpen.value = true; }
async function confirmRenameEngine() {
    if (engineToRename.value && renameEngineName.value.trim()) {
        await apiUpdateEngine(engineToRename.value.id, { name: renameEngineName.value.trim() });
        refreshData(); isRenameDialogOpen.value = false;
    }
}

async function openShareDialog(engine) {
    engineToManageShares.value = engine; isShareDialogOpen.value = true; isShareLoading.value = true; sharesForEngine.value = [];
    try {
        const rawShares = await engineStore.fetchEngineShares(engine.id);
        sharesForEngine.value = rawShares.filter(s => s.engine_id === engine.id);
    } finally { isShareLoading.value = false; }
}

async function handleGrantShare() {
    if (engineToManageShares.value && newShareIdentifier.value.trim()) {
        isShareLoading.value = true;
        await engineStore.grantShare(engineToManageShares.value.id, newShareIdentifier.value.trim(), newShareRole.value);
        isShareLoading.value = false; newShareIdentifier.value = '';
        openShareDialog(engineToManageShares.value);
    }
}
async function handleRevokeShare(uid) {
    isShareLoading.value = true;
    await engineStore.revokeShare(engineToManageShares.value.id, uid);
    isShareLoading.value = false;
    openShareDialog(engineToManageShares.value);
}

onMounted(() => { refreshData(); });
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&display=swap');

.my-engines-page {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  display: flex; background-color: #030303; overflow: hidden; z-index: 5;
}
.relative { position: relative; }
.z-10 { z-index: 10; }
.w-100 { width: 100%; }

/* UTILS */
.gap-3 { gap: 12px; } .gap-4 { gap: 16px; }
.orbitron-font { font-family: 'Orbitron', sans-serif; letter-spacing: 1px; }
.font-mono { font-family: 'Fira Code', monospace; }
.text-caption2 { font-size: 0.65rem; }
.text-shadow-glow { text-shadow: 0 0 10px rgba(255, 193, 7, 0.3); }

/* STATUS LED */
.status-led { width: 8px; height: 8px; background: #333; border-radius: 50%; box-shadow: 0 0 5px #333; }
.status-led.on { background: #00E676; box-shadow: 0 0 8px #00E676; }

/* OVERLAYS */
.scanline-overlay {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    background-size: 100% 2px, 3px 100%; pointer-events: none; z-index: 1; opacity: 0.4;
}
.vignette-overlay {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: radial-gradient(circle, transparent 60%, rgba(0,0,0,0.9) 100%); pointer-events: none; z-index: 2;
}

/* PANEL */
.reactor-main-panel {
    background: rgba(10, 10, 10, 0.9) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.5);
    border-radius: 4px;
}
.reactor-header {
    background: linear-gradient(90deg, rgba(20,20,20,1) 0%, rgba(10,10,10,0.8) 100%);
    border-bottom: 1px solid rgba(255, 193, 7, 0.1);
}
.header-deco-box {
    width: 48px; height: 48px; border: 1px solid rgba(255, 193, 7, 0.3);
    background: rgba(255, 193, 7, 0.05); display: flex; align-items: center; justify-content: center;
}
.deploy-btn {
    background: rgba(255, 193, 7, 0.1) !important; border: 1px solid rgba(255, 193, 7, 0.3); color: #FFC107 !important;
}
.deploy-btn:hover { background: rgba(255, 193, 7, 0.2) !important; box-shadow: 0 0 15px rgba(255, 193, 7, 0.2); }

/* GRID LAYOUT - ADJUSTED FOR 16 SLOTS (DENSE) */
.engine-grid {
    display: grid;
    /* Updated min-width to 240px to potentially fit 8 items on 1920px+ screens */
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 20px;
}
.section-label {
    display: flex; align-items: center; gap: 12px; font-weight: bold; letter-spacing: 2px;
}
.line-extender { flex-grow: 1; height: 1px; background: linear-gradient(90deg, #FFC107, transparent); }
.line-extender-cyan { flex-grow: 1; height: 1px; background: linear-gradient(90deg, #00E5FF, transparent); }

/* REACTOR UNIT (THE CARD) */
.reactor-unit {
    background: #0e0e0e;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 2px;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex; flex-direction: column;
    height: 320px;
}
.reactor-unit:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    background: #121212;
}
.reactor-online { border-color: rgba(255, 193, 7, 0.3); }
.reactor-active { border-color: #FFC107; box-shadow: 0 0 15px rgba(255, 193, 7, 0.1); }
.reactor-offline { border-color: rgba(255, 255, 255, 0.05); opacity: 0.8; }
.unit-shared { border-left: 3px solid #00E5FF; }

/* PLACEHOLDER SLOT */
.placeholder-unit {
    background: repeating-linear-gradient(45deg, rgba(20,20,20,1), rgba(20,20,20,1) 10px, rgba(15,15,15,1) 10px, rgba(15,15,15,1) 20px);
    border: 1px dashed rgba(255,255,255,0.1);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    opacity: 0.5; transition: opacity 0.2s;
}
.placeholder-unit:hover { opacity: 0.8; border-color: rgba(255, 193, 7, 0.3); }
.placeholder-content { text-align: center; z-index: 2; }
.slot-id { color: #444; font-size: 0.8rem; margin-bottom: 10px; }
.empty-icon-wrapper {
    width: 60px; height: 60px; border-radius: 50%; border: 2px dashed #333;
    display: flex; align-items: center; justify-content: center; margin: 0 auto;
}
.deploy-text { font-size: 0.7rem; letter-spacing: 1px; }

/* Status Bar */
.status-light-bar { height: 2px; width: 100%; background: #333; position: absolute; top: 0; left: 0; }
.reactor-online .status-light-bar { background: #00E676; box-shadow: 0 0 10px #00E676; }
.reactor-active .status-light-bar { background: #FFC107; box-shadow: 0 0 10px #FFC107; }
.status-light-bar-cyan { height: 2px; width: 100%; background: #00E5FF; position: absolute; top: 0; left: 0; box-shadow: 0 0 5px #00E5FF; }

/* Header inside Unit */
.unit-header { padding: 12px 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); background: rgba(0,0,0,0.2); }
.status-badge {
    font-size: 0.6rem; font-family: 'Fira Code', monospace; padding: 2px 6px; border-radius: 2px; border: 1px solid #333; color: #555;
}
.status-badge.online { border-color: #00E676; color: #00E676; background: rgba(0, 230, 118, 0.1); }

/* CENTER CORE ANIMATION */
.reactor-core-display {
    flex-grow: 1;
    display: flex; align-items: center; justify-content: center;
    position: relative;
    background: radial-gradient(circle, rgba(20,20,20,1) 0%, rgba(10,10,10,1) 70%);
}
.core-ring {
    position: absolute; width: 80px; height: 80px; border-radius: 50%;
    border: 2px dashed rgba(255, 255, 255, 0.1);
}
.core-ring.spinning { animation: spin 20s linear infinite; } /* Idle spin */
.core-ring.spinning.fast { animation: spin 4s linear infinite; border-color: rgba(255, 193, 7, 0.6); border-style: solid; border-top-color: transparent; }
.ring-cyan.spinning.fast { border-color: rgba(0, 229, 255, 0.6); }

.core-energy {
    position: absolute; width: 60px; height: 60px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 193, 7, 0.1) 0%, transparent 70%);
    opacity: 0; transition: opacity 0.5s;
}
.reactor-online .core-energy { opacity: 1; animation: pulse-core 2s infinite; }
.energy-cyan { background: radial-gradient(circle, rgba(0, 229, 255, 0.1) 0%, transparent 70%); }

.core-icon-wrapper { position: relative; z-index: 2; color: #333; }
.reactor-online .core-icon-wrapper { color: #FFC107; text-shadow: 0 0 15px rgba(255, 193, 7, 0.6); }
.unit-shared .reactor-online .core-icon-wrapper { color: #00E5FF; text-shadow: 0 0 15px rgba(0, 229, 255, 0.6); }

.spin-fan { animation: spin 2s linear infinite; }
.pulse-cyan { animation: pulse-opacity 2s infinite; }

/* VITALS */
.vitals-panel { padding: 12px 16px; background: rgba(0,0,0,0.3); border-top: 1px solid rgba(255,255,255,0.03); height: 90px; }
.meter-bar-bg { width: 100%; height: 4px; background: #222; border-radius: 1px; overflow: hidden; }
.meter-bar-fill { height: 100%; transition: width 0.5s ease; }
.fill-cyan { background-color: #00E5FF !important; }
.offline-readout { text-align: center; color: #444; font-family: 'Fira Code', monospace; font-size: 0.7rem; margin-top: 15px; border: 1px dashed #333; padding: 6px; }

/* FOOTER ACTIONS */
.unit-footer { padding: 8px 12px; border-top: 1px solid rgba(255, 255, 255, 0.03); background: #0c0c0c; }
.action-btn { font-family: 'Orbitron', sans-serif; letter-spacing: 1px; }
.connect-btn { background: rgba(255, 193, 7, 0.1) !important; color: #FFC107 !important; border: 1px solid rgba(255, 193, 7, 0.2); }
.connect-btn:hover { background: rgba(255, 193, 7, 0.2) !important; border-color: #FFC107; }
.connect-btn-cyan { background: rgba(0, 229, 255, 0.1) !important; color: #00E5FF !important; border: 1px solid rgba(0, 229, 255, 0.2); }
.connect-btn-cyan:hover { background: rgba(0, 229, 255, 0.2) !important; border-color: #00E5FF; }
.settings-btn:hover { color: #fff !important; }

/* ANIMATIONS */
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes pulse-core { 0% { transform: scale(0.9); opacity: 0.5; } 50% { transform: scale(1.1); opacity: 0.9; } 100% { transform: scale(0.9); opacity: 0.5; } }
@keyframes pulse-opacity { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
.spin-slow { animation: spin 10s linear infinite; }
.reactor-loader {
    width: 60px; height: 60px; border: 4px solid #333; border-top-color: #FFC107; border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* SCROLLBAR */
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: rgba(255, 193, 7, 0.2); border-radius: 3px; }

/* DIALOGS */
.pro-dialog-card { background: #080808 !important; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 2px; }
.dialog-header { padding: 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); background: #050505; }
.terminal-input-field :deep(.v-field__outline) { --v-field-border-color: rgba(255, 255, 255, 0.1); }
.terminal-input-field :deep(.v-field__input) { color: white; font-family: 'Fira Code', monospace; }
</style>
