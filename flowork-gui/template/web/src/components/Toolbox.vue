<template>
  <div class="toolbox-container">
    <div class="toolbox-header-tactical">
      <div class="title-row">
        <h3>
          <v-icon size="small" color="cyan-accent-2" class="mr-2">mdi-rhombus-split</v-icon>
          {{ activeTab === 'apps' ? 'Flow Nodes' : 'Components' }}
        </h3>
        <div class="badge-counter" v-if="gridItems.length > 0">{{ gridItems.length }}</div>
      </div>

      <button
        v-if="activeTab !== 'plugins'"
        class="upload-btn-tactical"
        @click="triggerItemUpload"
        title="Upload Local App/Node"
      >
        <v-icon size="small">mdi-plus-box-outline</v-icon>
      </button>
    </div>

    <div class="search-wrapper">
      <div class="search-box-tactical">
        <v-icon class="search-icon" size="small">mdi-magnify</v-icon>
        <input
          type="text"
          v-model="searchTerm"
          placeholder="Search nodes..."
          class="search-input-tactical"
        />
        <v-icon v-if="searchTerm" class="clear-icon" size="small" @click="searchTerm = ''">mdi-close</v-icon>
      </div>
    </div>

    <v-tabs
      v-model="activeTab"
      grow
      density="compact"
      class="tabs-header-tactical"
      height="32"
      hide-slider
    >
      <v-tab v-for="tab in tabs" :key="tab.value" :value="tab.value" class="tab-item">
        <v-icon :icon="tab.icon" size="x-small" class="mr-1"></v-icon>
        <span class="tab-label-text">{{ tab.label }}</span>
      </v-tab>
    </v-tabs>

    <div class="toolbox-content">
      <div v-if="isLoading" class="state-loader">
        <v-progress-circular indeterminate size="24" color="cyan"></v-progress-circular>
      </div>

      <div v-else class="widget-grid-wrapper">
        <div class="widget-grid-tactical">
          <div
            v-for="item in gridItems"
            :key="item.id"
            class="widget-item-tactical"
            :draggable="true"
            @dragstart="onDragStart($event, item)"
            v-tooltip.top="item.description || item.name"
          >
            <div class="item-shield">
              <div class="icon-wrapper-tactical glass">
                <img
                  v-if="resolveIcon(item)"
                  :src="resolveIcon(item)"
                  class="item-icon-img"
                  @error="handleIconError($event)"
                />
                <v-icon v-else color="cyan-darken-2" size="large">{{ getFallbackIcon(activeTab) }}</v-icon>

                <div class="item-actions-overlay">
                  <v-btn
                    icon="mdi-heart"
                    size="x-small"
                    variant="text"
                    :color="isFavorite(item.id) ? 'pink' : 'white'"
                    @click.stop="toggleFavorite(item.id)"
                  ></v-btn>

                  <v-btn
                    v-if="!item.is_installed && item.source === 'cloud'"
                    icon="mdi-download"
                    size="x-small"
                    variant="text"
                    color="green-accent-3"
                    @click.stop="installComponent(activeTab, item.id)"
                  ></v-btn>

                  <v-btn
                    v-if="item.source === 'local'"
                    icon="mdi-trash-can-outline"
                    size="x-small"
                    variant="text"
                    color="red-accent-2"
                    @click.stop="deleteComponent(activeTab, item.id)"
                  ></v-btn>
                </div>

                <div v-if="item.source === 'cloud'" class="cloud-badge-tactical">
                  <v-icon size="8">mdi-cloud</v-icon>
                </div>
              </div>
              <div class="name-shield-tactical">
                <span class="widget-name-text">{{ item.name || item.id }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="gridItems.length === 0" class="empty-state">
          <v-icon color="grey-darken-3" size="large">mdi-database-off-outline</v-icon>
          <p>No draggable nodes</p>
        </div>
      </div>
    </div>

    <input type="file" ref="folderInput" webkitdirectory directory style="display: none" @change="handleFolderSelect" />

    <v-dialog v-model="showPublishDialog" max-width="450px">
      <v-card class="publish-card">
        <v-card-title class="orbitron-font text-cyan-accent-2 text-subtitle-1">PUBLISH COMPONENT</v-card-title>
        <v-card-text>Are you sure you want to publish <b>{{ pendingPackage?.manifest?.name }}</b>?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" size="small" @click="showPublishDialog = false">Cancel</v-btn>
          <v-btn color="cyan-accent-2" variant="tonal" size="small" @click="confirmPublish">Confirm Publish</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useComponentStore } from '@/store/components';
import { useAppStore } from '@/store/apps';
import { useMarketplaceStore } from '@/store/marketplace';
import { useSocketStore } from '@/store/socket';
import { useEngineStore } from '@/store/engines';

const componentStore = useComponentStore();
const appStore = useAppStore();
const socketStore = useSocketStore();
const engineStore = useEngineStore();
const marketplaceStore = useMarketplaceStore();

const activeTab = ref('apps');
const searchTerm = ref('');
const folderInput = ref(null);
const showPublishDialog = ref(false);
const pendingPackage = ref({});

const tabs = [
  { label: 'Apps', value: 'apps', icon: 'mdi-apps' },
  { label: 'Actions', value: 'modules', icon: 'mdi-play-network' },
  { label: 'Triggers', value: 'triggers', icon: 'mdi-lightning-bolt' },
  { label: 'Tools', value: 'tools', icon: 'mdi-hammer-wrench' }
];

const isLoading = computed(() => activeTab.value === 'apps' ? appStore.isLoading : componentStore[activeTab.value]?.isLoading);

const gridItems = computed(() => {
  let items = [];
  if (activeTab.value === 'apps') {
    items = appStore.installedApps.filter(a =>
      !a.is_example && ((a.nodes && a.nodes.length > 0) || a.capability)
    );
  } else {
    items = (componentStore[activeTab.value]?.items || []).filter(i => !i.is_example);
  }
  if (!searchTerm.value) return items;
  return items.filter(i => (i.name || i.id).toLowerCase().includes(searchTerm.value.toLowerCase()));
});

/**
 * [FIXED] Enhanced Drag Start for better DnD compatibility
 */
const onDragStart = (event, item) => {
  const nodeType = activeTab.value === 'apps' ? 'app_node' : activeTab.value.slice(0, -1);
  const payload = {
    type: nodeType,
    id: item.id,
    label: item.name || item.id,
    originData: JSON.parse(JSON.stringify(item))
  };

  const jsonPayload = JSON.stringify(payload);

  // Clear any existing data
  event.dataTransfer.clearData();

  event.dataTransfer.setData('application/flowork-node', jsonPayload);
  event.dataTransfer.setData('text/plain', jsonPayload);
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.dropEffect = 'copy';

  // Drag Image fix (Optional but helps)
  const dragIcon = event.target.querySelector('img');
  if (dragIcon) {
      event.dataTransfer.setDragImage(dragIcon, 14, 14);
  }

  event.target.classList.add('is-dragging');

  const onDragEnd = () => {
    event.target.classList.remove('is-dragging');
    window.removeEventListener('dragend', onDragEnd);
  };
  window.addEventListener('dragend', onDragEnd);
};

const resolveIcon = (app) => {
  if (!app) return null;
  const activeEngineId = engineStore.selectedEngineId || socketStore.engineId || 'local';
  let url = app.iconUrl || app.icon_url;
  if (!url) {
    const iconName = app.icon || app.icon_file || (app.manifest && (app.manifest.icon || app.manifest.icon_file));
    if (iconName) {
      url = app.source === 'cloud' ? `/apps-cloud/${app.path || app.id}/${iconName}` : `/api/v1/apps/${app.id}/assets/${iconName}`;
    }
  }
  if (!url) return null;
  if (url.startsWith('http') || url.startsWith('data:')) return url;
  const separator = url.includes('?') ? '&' : '?';
  return url.includes('engine_id=') ? url : `${url}${separator}engine_id=${activeEngineId}`;
};

const getFallbackIcon = (tab) => tabs.find(t => t.value === tab)?.icon || 'mdi-help-box';
const handleIconError = (e) => { e.target.style.display = 'none'; };
const isFavorite = (id) => componentStore.favoriteComponents.includes(id);
const toggleFavorite = (id) => componentStore.toggleFavorite(id);
const installComponent = (type, id) => componentStore.installComponent(type, id);
const deleteComponent = (type, id) => { if(confirm('Uninstall?')) componentStore.uninstallComponent(type, id); };

const triggerItemUpload = () => folderInput.value.click();
const handleFolderSelect = async (event) => { /* logic extraction folder */ };
const confirmPublish = async () => { /* logic publish */ };

onMounted(() => {
  componentStore.fetchAllComponents();
  appStore.fetchInstalledApps();
  componentStore.fetchUserFavorites();
});
</script>

<style scoped>
.toolbox-container { display: flex; flex-direction: column; height: 100%; background: #08080e; color: #fff; border-right: 1px solid rgba(255,255,255,0.05); overflow: hidden; }

.toolbox-header-tactical { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.03); flex-shrink: 0; }
.title-row { display: flex; align-items: center; gap: 8px; }
.title-row h3 { font-family: 'Orbitron'; font-size: 0.7rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin: 0; }
.badge-counter { background: rgba(0, 245, 255, 0.1); color: #00f5ff; font-size: 0.6rem; padding: 1px 5px; border-radius: 4px; border: 1px solid rgba(0,245,255,0.2); font-weight: 900; }
.upload-btn-tactical { background: transparent; border: none; color: #666; cursor: pointer; transition: 0.2s; }
.upload-btn-tactical:hover { color: #00f5ff; transform: scale(1.1); }

.search-wrapper { padding: 6px 12px !important; flex-shrink: 0; }
.search-box-tactical { position: relative; display: flex; align-items: center; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 0 8px; transition: 0.3s; }
.search-input-tactical { width: 100%; background: transparent; border: none; color: #fff; padding: 6px 4px; font-size: 0.7rem; outline: none; }
.search-icon, .clear-icon { color: #555; }

/* FIXED: Massive UI Gape Fix */
.tabs-header-tactical {
  border-bottom: 1px solid rgba(0, 245, 255, 0.15);
  min-height: 32px !important;
  margin-bottom: 0 !important;
}
.tab-item {
  min-width: 0 !important;
  padding: 0 8px !important;
  height: 32px !important;
  color: #666 !important;
  font-size: 0.6rem !important;
}
.v-tab--selected { color: #00f5ff !important; background: rgba(0, 245, 255, 0.05); }
.tab-label-text { font-size: 0.55rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }

.toolbox-content { flex: 1; overflow-y: auto; position: relative; scrollbar-width: thin; }
.widget-grid-wrapper { padding: 10px; }
.widget-grid-tactical { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; align-items: start; }

.widget-item-tactical { display: flex; flex-direction: column; align-items: center; cursor: grab; position: relative; }
.widget-item-tactical:active { cursor: grabbing; }
.is-dragging { opacity: 0.4; transform: scale(0.9); }

.item-shield { display: flex; flex-direction: column; align-items: center; width: 100%; }
.icon-wrapper-tactical { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); transition: 0.3s; }
.widget-item-tactical:hover .icon-wrapper-tactical { border-color: #00f5ff; background: rgba(0,245,255,0.05); transform: translateY(-2px); }

.item-icon-img { width: 24px; height: 24px; object-fit: contain; }

.item-actions-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: flex; align-items: center; justify-content: center; opacity: 0; transition: 0.2s; gap: 2px; }
.icon-wrapper-tactical:hover .item-actions-overlay { opacity: 1; }

.name-shield-tactical { width: 100%; max-height: 24px; overflow: hidden; margin-top: 4px; display: flex; justify-content: center; }
.widget-name-text {
  font-size: 0.55rem;
  color: #777;
  text-align: center;
  line-height: 1.1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  word-break: break-all;
  font-weight: 500;
}
.widget-item-tactical:hover .widget-name-text { color: #00f5ff; }

.cloud-badge-tactical { position: absolute; top: 2px; right: 2px; color: #00f5ff; opacity: 0.8; }
.state-loader { display: flex; justify-content: center; padding-top: 40px; }
.empty-state { text-align: center; padding-top: 60px; opacity: 0.2; font-size: 0.6rem; text-transform: uppercase; letter-spacing: 2px; }

.publish-card { background: #0d0d15 !important; border: 1px solid #00f5ff !important; color: #fff !important; }
</style>