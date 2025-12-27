<template>
  <div class="dashboard-layout">
    <div class="ambient-background"></div>

    <aside class="sidebar-area">
      <AppToolbox @open-marketplace="openMarketplace" @request-publish="handleRequestPublish" />
    </aside>

    <main class="canvas-area">
      <div v-if="activeApps.length > 0" class="app-toolbar">
        <div class="active-tabs">
          <button
            v-for="a in activeApps"
            :key="a.instanceId"
            :class="['tab-btn', { active: currentTab === a.instanceId }]"
            @click="currentTab = a.instanceId"
          >
            <img
              v-if="resolveIcon(a)"
              :src="resolveIcon(a)"
              class="tab-icon-img"
              alt=""
              @error="handleIconError($event)"
            />
            <svg v-else style="width:16px;height:16px;fill:#FFFFFF;margin-right:6px;" viewBox="0 0 24 24">
                <path d="M21,16.5C21,16.88 20.79,17.21 20.47,17.38L12.57,21.82C12.41,21.94 12.21,22 12,22C11.79,22 11.59,21.94 11.43,21.82L3.53,17.38C3.21,17.21 3,16.88 3,16.5V7.5C3,7.12 3.21,6.79 3.53,6.62L11.43,2.18C11.59,2.06 11.79,2 12,2C12.21,2 12.41,2.06 12.57,2.18L20.47,6.62C20.79,6.79 21,7.12 21,7.5V16.5M12,4.15L6.04,7.5L12,10.85L17.96,7.5L12,4.15M5,15.91L11,19.29V12.58L5,9.21V15.91M19,15.91V9.21L13,12.58V19.29L19,15.91Z" />
            </svg>
            <span class="tab-label">{{ a.name }}</span>
            <span class="close-btn" @click.stop="closeApp(a.instanceId)" title="Close Tab">
              <svg style="width:14px;height:14px;fill:#FF5555;" viewBox="0 0 24 24">
                  <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
              </svg>
            </span>
          </button>
        </div>

        <div class="toolbar-actions">
           <button class="action-btn save-btn" @click="triggerAppSave" :disabled="isSaving">
              <svg v-if="!isSaving" style="width:16px;height:16px;fill:#00FFFF;margin-right:6px;" viewBox="0 0 24 24">
                  <path d="M15,9H5V5H15M12,19A3,3 0 0,1 9,16A3,3 0 0,1 12,13A3,3 0 0,1 15,16A3,3 0 0,1 12,19M17,3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V7L17,3Z" />
              </svg>
              <div v-else class="spinner-small"></div>
              <span>{{ isSaving ? 'Saving...' : 'Save State' }}</span>
           </button>
           <button class="action-btn" @click="triggerAppRefresh" title="Reload App">
              <svg style="width:16px;height:16px;fill:white;" viewBox="0 0 24 24">
                  <path d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z" />
              </svg>
           </button>
        </div>
      </div>

      <div v-if="activeApps.length === 0" class="launcher-state" :class="{ 'with-active-apps': activeApps.length > 0 }">
        <div class="launcher-header">
            <h2>Applications Center</h2>
            <p>Select an app to launch into your hybrid workspace</p>
        </div>

        <div class="launcher-grid">
            <div
                v-for="app in allApps"
                :key="app.id"
                class="launcher-card"
                @click="openApp(app.id)"
            >
                <button
                  v-if="!isCloudStatic(app)"
                  class="delete-app-btn"
                  @click.stop="deleteOfflineApp(app.id)"
                  title="Uninstall Local App"
                >
                  <svg style="width:16px;height:16px;fill:#FF5555;" viewBox="0 0 24 24">
                    <path d="M9,3V4H4V6H5V19A2,2 0 0,0 7,21H17A2,2 0 0,0 19,19V6H20V4H15V3H9M7,6H17V19H7V6M9,8V17H11V8H9M13,8V17H15V8H13Z" />
                  </svg>
                </button>

                <div class="card-icon">
                    <img
                        v-if="resolveIcon(app)"
                        :src="resolveIcon(app)"
                        alt="icon"
                        @error="handleIconError($event)"
                    />
                    <svg v-else class="default-icon" viewBox="0 0 24 24">
                        <path d="M21,16.5C21,16.88 20.79,17.21 20.47,17.38L12.57,21.82C12.41,21.94 12.21,22 12,22C11.79,22 11.59,21.94 11.43,21.82L3.53,17.38C3.21,17.21 3,16.88 3,16.5V7.5C3,7.12 3.21,6.79 3.53,6.62L11.43,2.18C11.59,2.06 11.79,2 12,2C12.21,2 12.41,2.06 12.57,2.18L20.47,6.62C20.79,6.79 21,7.12 21,7.5V16.5M12,4.15L6.04,7.5L12,10.85L17.96,7.5L12,4.15M5,15.91L11,19.29V12.58L5,9.21V15.91M19,15.91V9.21L13,12.58V19.29L19,15.91Z" />
                    </svg>
                    <div v-if="isCloudStatic(app)" class="cloud-tag" title="Cloud App">
                        <svg viewBox="0 0 24 24"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4C9.11 4 6.6 5.64 5.35 8.04C2.34 8.36 0 10.91 0 14C0 17.31 2.69 20 6 20H19C21.76 20 24 17.76 24 15C24 12.36 21.95 10.22 19.35 10.04Z" /></svg>
                    </div>
                </div>
                <div class="card-info">
                    <h3>{{ app.name }}</h3>
                    <p>{{ app.description || 'No description available' }}</p>
                </div>
                <div class="card-footer">
                    <span class="tier-badge" :class="app.tier">{{ app.tier || 'free' }}</span>
                    <span class="open-txt">Launch</span>
                </div>
            </div>
        </div>
      </div>

      </main>

    <MarketplacePublishDialog v-model="showPublishDialog" :existing-item="pendingPublishItem" @published="onPublished" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useAppStore } from '@/store/apps';
import { useVariablesStore } from '@/store/variables';
import { useUiStore } from '@/store/ui';
import { useSocketStore } from '@/store/socket';
import { useEngineStore } from '@/store/engines';
import { apiClient } from '@/api';
import AppToolbox from '@/components/AppToolbox.vue';
import MarketplacePublishDialog from '@/components/MarketplacePublishDialog.vue';

const appStore = useAppStore();
const variablesStore = useVariablesStore();
const uiStore = useUiStore();
const socketStore = useSocketStore();
const engineStore = useEngineStore();

const activeApps = computed(() => appStore.activeApps);
const allApps = computed(() => appStore.installedApps);

const activeEngineId = computed(() => {
    return engineStore.selectedEngineId || socketStore.engineId || localStorage.getItem('flowork_active_engine_id');
});

const currentTab = ref(null);
const isSaving = ref(false);
const showPublishDialog = ref(false);
const pendingPublishItem = ref(null);

const isCloudStatic = (app) => {
    if (!app) return false;
    if (app.id === 'business_canvas') return true;
    if (app.source === 'cloud') return true;
    if (app.path && app.path.includes('apps-cloud')) return true;
    return false;
};

// [UNIFIED ICON RESOLVER]
const resolveIcon = (app) => {
    if (isCloudStatic(app)) {
        return `/apps-cloud/${app.id}/icon.svg`;
    }

    let url = app.iconUrl || app.icon_url;
    if (!url && app.icon_file) {
        url = `/api/v1/apps/${app.id}/assets/${app.icon_file}`;
    }

    if (!url) return null;

    if (url.startsWith('http') || url.startsWith('data:')) return url;

    const separator = url.includes('?') ? '&' : '?';
    if (url.includes('engine_id=')) return url;

    const eid = activeEngineId.value || 'local';
    return `${url}${separator}engine_id=${eid}`;
};

const handleIconError = (e) => {
    e.target.style.display = 'none';
};

const formatProxyUrl = (url) => {
    if (!url) return '';
    const eid = activeEngineId.value;
    if (!eid) return '';
    if (url.startsWith('http') && !url.includes(window.location.hostname)) {
        return url;
    }
    if (url.includes('engine_id=')) return url;
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}engine_id=${eid}`;
};

// [FIXED] Sync local ref with global store current tab
watch(() => appStore.currentTab, (newVal) => {
    currentTab.value = newVal;
}, { immediate: true });

watch(currentTab, (newVal) => {
    appStore.setCurrentTab(newVal);
});

const triggerAppSave = () => {
  if (!currentTab.value) return;
  isSaving.value = true;
  const iframe = document.getElementById(`iframe-${currentTab.value}`);
  if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage({ type: 'CMD_SAVE' }, '*');
      setTimeout(() => { if(isSaving.value) isSaving.value = false; }, 5000);
  } else { isSaving.value = false; }
};

const triggerAppRefresh = () => {
    if (!currentTab.value) return;
    const iframe = document.getElementById(`iframe-${currentTab.value}`);
    if (iframe) iframe.src = iframe.src;
};

const handleAppMessage = async (event) => {
  if (!event.data || !event.data.type) return;
  const { type, payload } = event.data;

  if (type === 'APP_SAVE_REQUEST' || type === 'WIDGET_SAVE_REQUEST') {
    try {
      let senderApp = activeApps.value.find(a => a.instanceId === currentTab.value);
      if (!senderApp) return;

      const enforcedKey = `app_${senderApp.id}_data`;
      const dataToSave = JSON.stringify(payload.data);

      await variablesStore.saveVariable(enforcedKey, {
          value: dataToSave,
          is_enabled: true,
          is_secret: false
      });

      uiStore.showNotification({ text: `${senderApp.name} state saved!`, color: "success" });

      if (event.source) {
          event.source.postMessage({ type: 'APP_SAVE_SUCCESS' }, '*');
      }

    } catch (e) {
      uiStore.showNotification({ text: "Save Failed", color: "error" });
    } finally {
      isSaving.value = false;
    }
  }
};

const deleteOfflineApp = async (appId) => {
  const confirmed = await uiStore.showConfirmation({
    title: "Uninstall App",
    text: "Are you sure you want to remove this local app from your engine?",
    color: "error"
  });

  if (confirmed) {
    try {
      await appStore.uninstallApp(appId);
      uiStore.showNotification({ text: "App uninstalled successfully", color: "success" });
    } catch (e) {
      uiStore.showNotification({ text: "Failed to uninstall app", color: "error" });
    }
  }
};

onMounted(() => {
    if (appStore.installedApps.length === 0) {
        appStore.fetchInstalledApps();
    }
    window.addEventListener('message', handleAppMessage);
});

onUnmounted(() => {
    window.removeEventListener('message', handleAppMessage);
});

watch(() => activeApps.value.length, (newLen, oldLen) => {
    if (newLen > oldLen) {
        currentTab.value = activeApps.value[newLen - 1].instanceId;
    } else if (newLen === 0) {
        currentTab.value = null;
    }
});

const openApp = (id) => { appStore.openApp(id); };
const closeApp = (id) => { appStore.closeApp(id); };
const openMarketplace = () => { uiStore.setDesignerMode('marketplace'); }; // FIXED: Use real logic

const handleRequestPublish = (packageData) => {
  pendingPublishItem.value = {
    source: 'smart_package',
    componentType: packageData.type,
    data: { ...packageData.manifest, zip_data: packageData.files }
  };
  showPublishDialog.value = true;
};

const onPublished = () => { appStore.fetchInstalledApps(); };
</script>

<style scoped>
/* FIXED: Use flex-grow and overflow hidden to avoid gap issues with AppBar */
.dashboard-layout {
  display: flex;
  height: 100%;
  min-height: 0;
  background: var(--surface-ground);
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}
.ambient-background { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(circle at 50% 50%, rgba(0, 255, 255, 0.05) 0%, transparent 60%); pointer-events: none; z-index: 0; }
.sidebar-area { z-index: 2; background: rgba(30, 30, 46, 0.95); border-right: 1px solid var(--surface-border); width: 280px; }
.canvas-area { flex: 1; padding: 1rem; overflow: hidden; position: relative; display: flex; flex-direction: column; z-index: 1; gap: 0.5rem; }

.app-toolbar { display: flex; justify-content: space-between; align-items: center; background: var(--surface-card); border: 1px solid var(--surface-border); padding: 0.5rem; border-radius: 12px; z-index: 10; position: relative; }

/* FIXED: Remove Panah by hiding scrollbar but keeping functional scroll */
.active-tabs {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.active-tabs::-webkit-scrollbar { display: none; }

.tab-btn { background: transparent; border: 1px solid transparent; color: #ccc; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s; font-size: 0.85rem; white-space: nowrap; }
.tab-btn:hover { background: rgba(255,255,255,0.05); color: white; }
.tab-btn.active { background: rgba(0, 255, 255, 0.1); color: #00FFFF; border-color: #00FFFF; font-weight: 600; }
.tab-icon-img { width: 16px; height: 16px; object-fit: contain; margin-right: 6px; }
.close-btn { opacity: 0.5; margin-left: 5px; display: flex; align-items: center; }
.close-btn:hover { opacity: 1; }

.launcher-state { flex: 1; display: flex; flex-direction: column; padding: 2rem 4rem; overflow-y: auto; z-index: 5; position: relative; }
.launcher-state.with-active-apps { padding: 1rem 4rem; }

.launcher-header { margin-bottom: 2rem; }
.launcher-header h2 { font-size: 2rem; color: white; font-family: 'Orbitron', sans-serif; letter-spacing: 1px; margin-bottom: 0.5rem; }
.launcher-header p { color: #aaa; }
.launcher-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1.5rem; }

.launcher-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
}

/* DELETE BUTTON FOR OFFLINE APPS */
.delete-app-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 85, 85, 0.1);
  border: 1px solid rgba(255, 85, 85, 0.2);
  padding: 5px;
  border-radius: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 10;
}
.launcher-card:hover .delete-app-btn { opacity: 1; }
.delete-app-btn:hover { background: rgba(255, 85, 85, 0.3); border-color: #FF5555; }

.launcher-card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.07); border-color: #00FFFF; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3), 0 0 10px rgba(0, 255, 255, 0.2); }
.card-icon { width: 64px; height: 64px; margin-bottom: 1rem; position: relative; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.2); border-radius: 12px; padding: 8px;}
.card-icon img { width: 100%; height: 100%; object-fit: contain; }
.default-icon { width: 40px; height: 40px; fill: #00FFFF; }
.cloud-tag { position: absolute; bottom: -5px; right: -5px; background: #00FFFF; color: black; border-radius: 50%; padding: 4px; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; }
.cloud-tag svg { width: 12px; height: 12px; fill: #000; }
.card-info { flex: 1; margin-bottom: 1rem; }
.card-info h3 { color: #fff; margin-bottom: 0.5rem; font-size: 1.1rem; }
.card-info p { color: #888; font-size: 0.85rem; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-footer { width: 100%; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem; }
.tier-badge { font-size: 0.7rem; text-transform: uppercase; padding: 2px 8px; border-radius: 4px; font-weight: bold; background: #333; color: #aaa; }
.tier-badge.free { background: rgba(0, 255, 0, 0.2); color: #00ff00; }
.tier-badge.paid { background: rgba(255, 215, 0, 0.2); color: #ffd700; }
.open-txt { color: #00FFFF; font-size: 0.85rem; font-weight: 600; }

.toolbar-actions { display: flex; gap: 0.5rem; }
.action-btn { background: rgba(255,255,255,0.05); border: 1px solid var(--surface-border); color: #ccc; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; font-weight: 600; transition: all 0.2s; }
.action-btn:hover { border-color: #00FFFF; color: #00FFFF; }
.save-btn { background: rgba(0, 255, 255, 0.1); color: #00FFFF; border-color: rgba(0, 255, 255, 0.3); }
.save-btn:hover { background: rgba(0, 255, 255, 0.2); }
.save-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.spinner-small { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top: 2px solid #fff; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; }

.engine-wait-overlay { position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.8); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 100; color: #00FFFF; font-family: 'Orbitron', sans-serif; gap: 1rem; }
.spinner-large { width: 40px; height: 40px; border: 4px solid rgba(0, 255, 255, 0.2); border-top: 4px solid #00FFFF; border-radius: 50%; animation: spin 1s linear infinite; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>