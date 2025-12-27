//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\AppToolbox.vue
//#######################################################################

<template>
  <div class="widget-toolbox-container">
    <div class="toolbox-header">
      <div class="title-row">
        <h3>
          <svg style="width:20px;height:20px;vertical-align:middle;margin-right:8px;fill:#FFFFFF;" viewBox="0 0 24 24">
            <path d="M21,16.5C21,16.88 20.79,17.21 20.47,17.38L12.57,21.82C12.41,21.94 12.21,22 12,22C11.79,22 11.59,21.94 11.43,21.82L3.53,17.38C3.21,17.21 3,16.88 3,16.5V7.5C3,7.12 3.21,6.79 3.53,6.62L11.43,2.18C11.59,2.06 11.79,2 12,2C12.21,2 12.41,2.06 12.57,2.18L20.47,6.62C20.79,6.79 21,7.12 21,7.5V16.5M12,4.15L6.04,7.5L12,10.85L17.96,7.5L12,4.15M5,15.91L11,19.29V12.58L5,9.21V15.91M19,15.91V9.21L13,12.58V19.29L19,15.91Z" />
          </svg>
          Quick Apps
        </h3>
        <div class="badge-counter" v-if="apps.length > 0">{{ apps.length }}</div>
      </div>
      <button class="upload-btn" @click="triggerUpload" title="Upload App Folder">
        <svg style="width:24px;height:24px;fill:#E0E0E0;" viewBox="0 0 24 24">
            <path d="M14 13V17H10V13H7L12 8L17 13H14M19.35 10.04C18.67 6.59 15.64 4 12 4C9.11 4 6.6 5.64 5.35 8.04C2.34 8.36 0 10.91 0 14C0 17.31 2.69 20 6 20H19C21.76 20 24 17.76 24 15C24 12.36 21.95 10.22 19.35 10.04Z" />
        </svg>
      </button>
    </div>

    <div class="search-container">
      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 24 24">
          <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
        </svg>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Find apps..."
          class="search-input"
        />
        <span v-if="searchQuery" class="clear-search" @click="searchQuery = ''">×</span>
      </div>
    </div>

    <input type="file" ref="folderInput" webkitdirectory directory style="display: none" @change="handleFolderSelect" />

    <div v-if="isLoading" class="state-container loading">
      <div class="cyber-spinner"></div>
      <p class="blink-text">INITIALIZING...</p>
    </div>

    <div v-else-if="filteredApps.length === 0 && searchQuery" class="state-container empty">
       <p>No apps found for "{{ searchQuery }}"</p>
    </div>

    <div v-else-if="apps.length === 0" class="state-container empty">
      <div style="opacity: 0.5; margin-bottom: 10px;">
         <svg style="width:48px;height:48px;fill:#666;" viewBox="0 0 24 24">
            <path d="M19,3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M19,19H5V5H19V19Z" />
         </svg>
      </div>
      <p>No apps installed.</p>
      <button class="ghost-btn" @click="triggerUpload">Upload App</button>
    </div>

    <div v-else class="widget-grid-wrapper">
      <div class="widget-grid">
        <div v-if="!searchQuery" class="widget-item add-new" @click="triggerUpload">
          <div class="icon-wrapper dashed">
            <svg style="width:28px;height:28px;fill:#00FFFF;" viewBox="0 0 24 24">
                <path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" />
            </svg>
          </div>
          <span class="widget-name">Upload</span>
        </div>

        <div v-for="app in filteredApps" :key="app.id" class="widget-item" @click="handleAppClick(app.id)" v-tooltip.top="app.description || app.name">
          <div class="app-item-shield">
              <div class="icon-wrapper glass">
                <img
                  v-if="resolveIcon(app)"
                  :src="resolveIcon(app)"
                  style="width:32px;height:32px;object-fit:contain;"
                  @error="handleImageError($event)"
                />

                <svg v-else class="fallback-svg" style="width:36px;height:36px;fill:#00FFFF;filter:drop-shadow(0 0 5px rgba(0,255,255,0.5));" viewBox="0 0 24 24">
                    <path d="M21,16.5C21,16.88 20.79,17.21 20.47,17.38L12.57,21.82C12.41,21.94 12.21,22 12,22C11.79,22 11.59,21.94 11.43,21.82L3.53,17.38C3.21,17.21 3,16.88 3,16.5V7.5C3,7.12 3.21,6.79 3.53,6.62L11.43,2.18C11.59,2.06 11.79,2 12,2C12.21,2 12.41,2.06 12.57,2.18L20.47,6.62C20.79,6.79 21,7.12 21,7.5V16.5M12,4.15L6.04,7.5L12,10.85L17.96,7.5L12,4.15M5,15.91L11,19.29V12.58L5,9.21V15.91M19,15.91V9.21L13,12.58V19.29L19,15.91Z" />
                </svg>

                <div v-if="app.source === 'cloud' || isCloudStatic(app)" class="cloud-badge" title="Cloud App">
                   <svg style="width:10px;height:10px;fill:#fff;" viewBox="0 0 24 24">
                      <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4C9.11 4 6.6 5.64 5.35 8.04C2.34 8.36 0 10.91 0 14C0 17.31 2.69 20 6 20H19C21.76 20 24 17.76 24 15C24 12.36 21.95 10.22 19.35 10.04Z" />
                   </svg>
                </div>
              </div>
              <div class="name-shield">
                  <span class="widget-name">{{ app.name || 'Unknown App' }}</span>
              </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useAppStore } from '@/store/apps';
import { useSocketStore } from '@/store/socket';
import { useEngineStore } from '@/store/engines';

const emit = defineEmits(['open-marketplace', 'request-publish']);
const appStore = useAppStore();
const socketStore = useSocketStore();
const engineStore = useEngineStore();

const apps = computed(() => appStore.installedApps);
const isLoading = computed(() => appStore.isLoading);
const folderInput = ref(null);
const searchQuery = ref('');

const activeEngineId = computed(() => {
    return engineStore.selectedEngineId || socketStore.engineId || 'local';
});

const isCloudStatic = (app) => {
    if (app.id === 'business_canvas') return true;
    // Check path or slug for cloud identification
    if (app.path && app.path.includes('apps-cloud')) return true;
    if (app.source === 'cloud') return true;
    return false;
};

/**
 * [SMART RESOLVER - V2 COMPATIBLE]
 * Supports both V1 (icon_file) and V2 (icon) field names.
 */
const resolveIcon = (app) => {
    if (!app) return null;

    // 1. [PRIORITY] STATIC CLOUD APPS (e.g. Business Canvas)
    if (isCloudStatic(app)) {
        // [FIXED] Detect if icon filename is 'icon.svg' or something else
        const iconName = app.icon || app.icon_file || 'icon.svg';
        return `/apps-cloud/${app.id}/${iconName}`;
    }

    // 2. [PRIORITY] PRE-DEFINED URL (Provisioned by Store)
    let url = app.iconUrl || app.icon_url;

    // 3. [FALLBACK] MANUAL RECONSTRUCTION (Checking V1 icon_file and V2 icon)
    if (!url) {
        // Search in app root OR inside manifest object
        const iconName = app.icon || app.icon_file || (app.manifest && (app.manifest.icon || app.manifest.icon_file));

        if (iconName) {
            if (app.source === 'cloud') {
                const cloudPath = app.path || app.id;
                url = `/apps-cloud/${cloudPath}/${iconName}`;
            } else {
                url = `/api/v1/apps/${app.id}/assets/${iconName}`;
            }
        }
    }

    if (!url) return null;

    // 4. EXTERNAL ABSOLUTE URLs
    if (url.startsWith('http') || url.startsWith('data:')) {
        return url;
    }

    // 5. LOCAL ENGINE TUNNELING
    const separator = url.includes('?') ? '&' : '?';
    if (url.includes('engine_id=')) return url;

    return `${url}${separator}engine_id=${activeEngineId.value}`;
};

const handleImageError = (event) => {
    event.target.style.display = 'none';
};

const filteredApps = computed(() => {
  if (!searchQuery.value) return apps.value;
  return apps.value.filter(a =>
    a && a.name && a.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

onMounted(() => { appStore.fetchInstalledApps(); });
const handleAppClick = (id) => { appStore.openApp(id); };
const triggerUpload = () => { if (folderInput.value) folderInput.value.click(); };

const handleFolderSelect = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    const packageData = { manifest: {}, files: {}, type: 'app' };
    const IGNORED = ['node_modules', '.git', 'dist', '.DS_Store'];

    for (const file of files) {
        const path = file.webkitRelativePath;
        if (IGNORED.some(x => path.includes(x))) continue;
        try {
            const isBinary = /\.(png|jpg|jpeg|gif|webp|ico|zip)$/i.test(file.name);
            let content;
            if (isBinary) content = await readFileAsBase64(file);
            else content = await file.text();
            if (file.name === 'manifest.json') { try { packageData.manifest = JSON.parse(content); } catch(e){} }
            packageData.files[path] = content;
        } catch (e) {}
    }
    emit('request-publish', packageData);
    event.target.value = '';
};

const readFileAsBase64 = (file) => {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.readAsDataURL(file);
    });
};
</script>

<style scoped>
.widget-toolbox-container { height: 100%; width: 280px; display: flex; flex-direction: column; padding: 1.5rem; color: #fff; font-family: 'Inter', sans-serif; }
.toolbox-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
.title-row { display: flex; align-items: center; gap: 0.5rem; }
.toolbox-header h3 { margin: 0; font-size: 1rem; font-weight: 700; color: white; font-family: 'Orbitron', sans-serif; text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; }
.badge-counter { background: rgba(0, 255, 255, 0.2); color: #00FFFF; font-size: 0.75rem; padding: 2px 8px; border-radius: 10px; font-weight: bold; border: 1px solid rgba(0, 255, 255, 0.3); }
.upload-btn { background: transparent; border: none; color: white; cursor: pointer; transition: all 0.2s; padding: 0.5rem; border-radius: 8px; }
.upload-btn:hover { background: rgba(255, 255, 255, 0.1); color: #00FFFF; }
.search-container { margin-bottom: 1.5rem; }
.search-box { position: relative; display: flex; align-items: center; }
.search-input { width: 100%; background: rgba(0, 0, 0, 0.2); border: 1px solid rgba(255, 255, 255, 0.15); color: #fff; padding: 8px 30px 8px 32px; border-radius: 8px; font-size: 0.85rem; outline: none; transition: all 0.2s; font-family: 'Inter', sans-serif; }
.search-input:focus { border-color: #00FFFF; background: rgba(0, 0, 0, 0.3); }
.search-input::placeholder { color: rgba(255, 255, 255, 0.4); }
.search-icon { position: absolute; left: 8px; width: 16px; height: 16px; fill: rgba(255, 255, 255, 0.4); pointer-events: none; }
.clear-search { position: absolute; right: 10px; color: rgba(255, 255, 255, 0.5); cursor: pointer; font-weight: bold; font-size: 1.1rem; }
.clear-search:hover { color: #fff; }
.state-container { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; gap: 1rem; color: #aaa; }
.cyber-spinner { width: 40px; height: 40px; border: 3px solid transparent; border-top: 3px solid #00FFFF; border-right: 3px solid #00FFFF; border-radius: 50%; animation: spin 1s linear infinite; }
.ghost-btn { background: transparent; border: 1px solid #aaa; color: white; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; transition: all 0.3s; font-size: 0.8rem; }
.ghost-btn:hover { border-color: #00FFFF; color: #00FFFF; }
.widget-grid-wrapper { flex: 1; overflow-y: auto; padding-right: 5px; }
.widget-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem 0.5rem; align-items: start; }
.widget-item { display: flex; flex-direction: column; align-items: center; cursor: pointer; position: relative; width: 100%; }

.app-item-shield {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    min-height: 80px;
    justify-content: flex-start;
}

.icon-wrapper { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); position: relative; overflow: hidden; flex-shrink: 0; }
.icon-wrapper.glass { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
.widget-item:hover .icon-wrapper.glass { transform: translateY(-5px) scale(1.05); background: rgba(255, 255, 255, 0.1); border-color: #00FFFF; box-shadow: 0 0 15px rgba(0, 255, 255, 0.3); }
.icon-wrapper.dashed { background: rgba(0, 0, 0, 0.2); border: 2px dashed rgba(255, 255, 255, 0.2); color: rgba(255, 255, 255, 0.5); }
.widget-item:hover .icon-wrapper.dashed { border-color: #00FFFF; color: #00FFFF; background: rgba(0, 255, 255, 0.1); }

.name-shield {
    width: 100%;
    max-height: 32px;
    overflow: hidden;
    display: flex;
    justify-content: center;
}

.widget-name { font-size: 0.7rem; text-align: center; color: #ccc; line-height: 1.2; max-width: 100%; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; padding: 0 2px; font-weight: 500; word-break: break-all; }
.widget-item:hover .widget-name { color: white; }
.cloud-badge { position: absolute; top: 4px; right: 4px; background: rgba(0, 255, 255, 0.8); border-radius: 50%; width: 14px; height: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 5px #00FFFF; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>