//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\MarketplaceItem.vue total lines 446 
//#######################################################################

<template>
  <div class="item-detail-page">
    <NeuralCanvasBackground />
    <v-container class="page-container">

      <div v-if="isAppMode" class="app-landing-wrapper">
         <div class="app-header">
            <div class="icon-box">
               <img :src="appData.iconUrl || '/assets/icons/app_default.svg'" alt="App Icon" @error="handleImgError" />
            </div>
            <div class="header-text">
              <h1 class="orbitron-font">{{ appData.name }}</h1>
              <p class="tagline">{{ appData.seo?.title || appData.description }}</p>
              <div class="tags">
                <span v-for="tag in (appData.seo?.keywords || appData.tags)" :key="tag" class="tag">#{{ tag }}</span>
              </div>
            </div>
         </div>

         <div class="action-bar">
            <button class="btn-launch" @click="launchApp">
              🚀 LAUNCH APP
            </button>
            <button class="btn-share" @click="copyLink">
              🔗 Share
            </button>
         </div>

         <div class="description-box">
            <h3>About this App</h3>
            <p>{{ appData.seo?.description || appData.description }}</p>
         </div>

         <div class="preview-box" v-if="appData.iconUrl">
             <img :src="appData.iconUrl" alt="App Preview" @error="handleImgError" />
         </div>

         <div class="text-center mt-8">
             <router-link to="/apps-center" class="text-grey text-decoration-none">← Back to Apps Center</router-link>
         </div>
      </div>

      <v-row v-else justify="center">
        <v-col cols="12" md="11" lg="10">

          <v-btn
            :to="{ name: 'Marketplace' }"
            prepend-icon="mdi-arrow-left"
            variant="text"
            class="mb-4"
          >
            Back to Marketplace
          </v-btn>

          <div v-if="itemType === 'capsule'">
              <v-alert type="info">Capsule View Active</v-alert>
          </div>

          <div v-else>
            <div v-if="isLoadingDetail" class="text-center py-16">
              <v-progress-circular indeterminate color="cyan" size="64"></v-progress-circular>
              <p class="mt-4 text-grey-lighten-1">Loading item detail...</p>
            </div>

            <v-alert v-else-if="error" type="error" variant="tonal" class="mt-4">
              {{ error }}
            </v-alert>

            <v-card v-else-if="selectedItem" class="item-card detail-card-enhanced" variant="flat">

              <div class="hero-header pa-6 d-flex justify-space-between align-start">
                 <div>
                    <v-chip
                        size="small"
                        :color="getTypeColor(selectedItem.type)"
                        class="mb-2 font-weight-bold"
                        variant="outlined"
                    >
                        {{ selectedItem.type ? selectedItem.type.toUpperCase() : 'ITEM' }}
                    </v-chip>

                    <h1 class="item-title-large orbitron-font">{{ selectedItem.name }}</h1>

                    <div class="text-grey-lighten-1 mt-2">
                        Published by
                        <router-link
                          :to="{ name: 'ProfileView', params: { identifier: selectedItem.author || 'anon' } }"
                          class="author-link font-weight-bold text-cyan"
                        >
                          {{ formatAuthor(selectedItem.author) }}
                        </router-link>
                    </div>
                 </div>

                 <div class="d-flex gap-2">
                    <v-btn
                      v-if="canDelete"
                      color="yellow-darken-2"
                      variant="tonal"
                      size="small"
                      prepend-icon="mdi-pencil"
                      @click="showEditDialog = true"
                      class="mr-2"
                    >
                      Edit
                    </v-btn>
                    <v-btn
                      v-if="canDelete"
                      color="red-darken-1"
                      variant="tonal"
                      size="small"
                      prepend-icon="mdi-delete"
                      @click="handleDelete"
                    >
                      Delete
                    </v-btn>
                 </div>
              </div>

              <v-divider class="border-opacity-50"></v-divider>

              <v-card-text class="pa-6">
                <div class="d-flex align-center mb-6">
                  <v-btn
                    variant="tonal"
                    :color="userVoteStatus === 1 ? 'cyan' : 'grey-darken-2'"
                    @click="handleVote(1)"
                    :prepend-icon="userVoteStatus === 1 ? 'mdi-thumb-up' : 'mdi-thumb-up-outline'"
                    class="mr-2"
                    rounded="pill"
                  >
                    {{ selectedItem.likes || 0 }}
                  </v-btn>
                  <v-btn
                    variant="tonal"
                    :color="userVoteStatus === -1 ? 'red' : 'grey-darken-2'"
                    @click="handleVote(-1)"
                    :prepend-icon="userVoteStatus === -1 ? 'mdi-thumb-down' : 'mdi-thumb-down-outline'"
                    class="mr-4"
                    rounded="pill"
                  >
                    {{ selectedItem.dislikes || 0 }}
                  </v-btn>
                  <v-chip variant="text" color="grey">
                    <v-icon start>mdi-calendar-clock</v-icon>
                    {{ selectedItem.created_at ? new Date(selectedItem.created_at).toLocaleDateString() : 'Recent' }}
                  </v-chip>
                </div>

                <div class="content-layout d-flex flex-column flex-md-row gap-6">

                    <div class="description-box flex-grow-1">
                        <h3 class="section-title text-cyan mb-3">Description</h3>
                        <p class="item-description">
                        {{ selectedItem.desc || selectedItem.description || 'No description provided.' }}
                        </p>

                        <div v-if="selectedItem.type !== 'preset'" class="mt-6 pa-4 bg-grey-darken-4 rounded border">
                            <div class="text-caption text-grey mb-2">COMPONENT INFO</div>
                            <div class="d-flex align-center gap-4">
                                <v-chip size="small" label color="purple">Ver: {{ selectedItem.version || '1.0.0' }}</v-chip>
                                <span class="text-caption text-mono">{{ selectedItem.id }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="action-sidebar">
                        <v-card variant="outlined" class="action-box-card pa-4">
                            <div class="mb-4 text-center">
                                <span class="text-h4 orbitron-font text-green-accent-3">
                                    {{ selectedItem.price > 0 ? `$${selectedItem.price}` : 'FREE' }}
                                </span>
                            </div>

                            <v-btn
                                v-if="selectedItem.type === 'preset'"
                                color="cyan"
                                block
                                size="large"
                                variant="flat"
                                class="action-button-glow"
                                @click="handleImportPreset"
                                prepend-icon="mdi-import"
                            >
                                Import Workflow
                            </v-btn>

                            <v-btn
                                v-else
                                color="yellow-darken-1"
                                block
                                size="large"
                                variant="flat"
                                class="action-button-glow text-black"
                                @click="handleInstallComponent"
                                :loading="isInstalling"
                                prepend-icon="mdi-download-box"
                            >
                                Install {{ selectedItem.type ? selectedItem.type : 'Component' }}
                            </v-btn>

                            <p class="text-caption text-center mt-3 text-grey">
                                {{ selectedItem.type === 'preset'
                                    ? 'Instantly add this workflow to your active Designer canvas.'
                                    : 'Download and install this component to your local engine.'
                                }}
                            </p>
                        </v-card>
                    </div>
                </div>
              </v-card-text>
            </v-card>
          </div>

        </v-col>
      </v-row>

      <MarketplacePublishDialog
        v-model="showEditDialog"
        :existing-item="selectedItem"
        @published="handleItemUpdated"
      />

    </v-container>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMarketplaceStore } from '@/store/marketplace';
import { useWorkflowStore } from '@/store/workflow';
import { useAuthStore } from '@/store/auth';
import { useUiStore } from '@/store/ui';
import { useAppStore } from '@/store/apps'; // [ADDED] Migrated to AppStore
import { storeToRefs } from 'pinia';
import NeuralCanvasBackground from '@/components/NeuralCanvasBackground.vue';
import MarketplacePublishDialog from '@/components/MarketplacePublishDialog.vue';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const marketplaceStore = useMarketplaceStore();
const workflowStore = useWorkflowStore();
const authStore = useAuthStore();
const uiStore = useUiStore();
const appStore = useAppStore(); // [ADDED]

const { selectedItem, isLoadingDetail, error, userVotes } = storeToRefs(marketplaceStore);
const itemType = computed(() => route.query.type);

const appData = ref(null); // [ADDED] Replaces widgetData
const isAppMode = computed(() => !!appData.value); // [ADDED] Replaces isWidgetMode

const showEditDialog = ref(false);
const isInstalling = ref(false);

const userVoteStatus = computed(() => {
    const itemId = selectedItem.value?.id;
    return itemId ? userVotes.value[itemId] : 0;
});

const canDelete = computed(() => {
    if (!selectedItem.value || !authStore.user) return false;
    const currentUser = authStore.user.id.toLowerCase();
    const author = (selectedItem.value.author || '').toLowerCase();
    const admins = [
        "0xF39733B34131c13E35733E9Af1adD78a5e768929".toLowerCase(),
        "0x0F1F31783A93C94f5055E2A11AA28B2368bA982d".toLowerCase()
    ];
    return currentUser === author || admins.includes(currentUser);
});

onMounted(async () => {
  const slug = route.params.slug;
  const itemId = route.params.id;

  if (slug) {
      await checkRegistryForApp(slug); // [ADDED] Direct hit to Apps Center logic
  } else if (itemId) {
      if (itemType.value === 'capsule') {
        marketplaceStore.fetchCapsuleDetails(itemId);
      } else {
        marketplaceStore.fetchItemDetail(itemId);
      }
  }
});

async function checkRegistryForApp(slug) {
    try {
        const res = await fetch('/apps-cloud/registry.json');
        if (!res.ok) throw new Error("Registry not found");
        const registry = await res.json();
        const found = registry.find(a => a.slug === slug || a.id === slug);

        if (found) {
            const manifestPath = `/apps-cloud/${found.path}/${found.manifest_file || 'manifest.json'}`;
            const mRes = await fetch(manifestPath);
            if(mRes.ok) {
                const m = await mRes.json();
                appData.value = {
                    ...found,
                    ...m,
                    iconUrl: m.icon_file ? `/apps-cloud/${found.path}/${m.icon_file}` : '/assets/icons/app_default.svg'
                };
            }

            document.title = found.seo?.title || `${found.name} - Flowork Hybrid App`;
            updateMeta('description', found.seo?.description || found.description);
        } else {
            error.value = "App not found in hybrid registry.";
        }
    } catch(e) {
        console.error("App Registry error", e);
    }
}

/* [WIDGET_DEPRECATED]
async function checkRegistryForWidget(slug) {
    try {
        const res = await fetch('/widgets-cloud/registry.json');
        ...
    } catch(e) { ... }
}
*/

function launchApp() {
    if (!appData.value) return;
    appStore.openAppBySlug(appData.value.slug);
    router.push({ name: 'AppsCenter' });
}

/* [WIDGET_DEPRECATED]
function launchWidget() {
    widgetStore.openWidget(widgetData.value.id);
    router.push({ path: '/widgets', query: { open: widgetData.value.id } });
}
*/

function copyLink() {
    navigator.clipboard.writeText(window.location.href);
    uiStore.showNotification({ text: "App link copied!", color: "info" });
}

function handleImgError(e) {
    e.target.src = '/assets/icons/app_default.svg';
}

function updateMeta(name, content) {
    let el = document.querySelector(`meta[name="${name}"]`);
    if(el && content) el.setAttribute('content', content);
}

function formatAuthor(address) {
  if (!address) return 'Anonymous';
  if (address.startsWith('0x')) {
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  }
  return address;
}

function getTypeColor(type) {
    if (!type) return 'grey';
    if (type === 'preset') return 'cyan';
    if (type === 'module') return 'purple-accent-2';
    return 'blue';
}

async function handleVote(type) {
    if (!selectedItem.value) return;
    await marketplaceStore.handleVote(selectedItem.value.id, type);
}

async function handleImportPreset() {
  if (!selectedItem.value || !selectedItem.value.data) return;
  try {
    let workflowData = selectedItem.value.data;
    if (typeof workflowData === 'string') {
        try { workflowData = JSON.parse(workflowData); } catch(e) { }
    }
    const newPresetName = `Imported - ${selectedItem.value.name}`;
    workflowStore.updateSinglePresetData(newPresetName, workflowData);
    workflowStore.currentPresetName = newPresetName;
    router.push({ name: 'Designer' });
  } catch (e) { }
}

async function handleInstallComponent() {
    if (!selectedItem.value?.data) return;
    isInstalling.value = true;
    try {
        await axios.post('/api/v1/marketplace/component/install', {
            id: selectedItem.value.id,
            type: selectedItem.value.type,
            zip_data: selectedItem.value.data
        });
        uiStore.showNotification({ text: `Installation Success!`, color: 'success' });
    } catch (error) {
        uiStore.showNotification({ text: `Installation Failed`, color: 'error' });
    } finally {
        isInstalling.value = false;
    }
}

async function handleDelete() {
    const confirmed = await uiStore.showConfirmation({ title: 'Delete Item', message: 'Are you sure?', color: 'red' });
    if (confirmed && (await marketplaceStore.deleteItem(selectedItem.value.id))) {
        router.push({ name: 'Marketplace' });
    }
}

async function handleItemUpdated() {
    if (selectedItem.value?.id) await marketplaceStore.fetchItemDetail(selectedItem.value.id);
}
</script>

<style scoped>
.item-detail-page { height: 100%; overflow-y: auto; padding: 48px 0; position: relative; z-index: 1; }
.page-container { max-width: 1600px; position: relative; z-index: 2; }
.orbitron-font { font-family: 'Orbitron', monospace; color: #f0f0f0; }
.detail-card-enhanced { background: rgba(30, 30, 47, 0.85); backdrop-filter: blur(15px); border: 1px solid rgba(0, 245, 255, 0.2); box-shadow: 0 0 30px rgba(0, 0, 0, 0.5); overflow: hidden; }
.item-title-large { font-size: 2.8rem; line-height: 1.1; color: white; text-shadow: 0 0 15px rgba(0, 245, 255, 0.4); }
.item-description { font-size: 1.1rem; line-height: 1.8; color: #ccc; white-space: pre-wrap; }
.action-box-card { background: rgba(0, 0, 0, 0.3); border-color: rgba(255, 255, 255, 0.1); }
.action-button-glow { font-weight: bold; box-shadow: 0 0 15px rgba(0, 245, 255, 0.5); transition: all 0.3s ease; }
.author-link { text-decoration: none; transition: all 0.3s ease; }

/* Hybrid App Landing Styles */
.app-landing-wrapper { max-width: 800px; margin: 0 auto; color: white; font-family: 'Inter', sans-serif; }
.app-header { display: flex; gap: 20px; align-items: center; margin-bottom: 30px; }
.icon-box img { width: 80px; height: 80px; border-radius: 20px; object-fit: contain; background: rgba(255,255,255,0.1); padding: 10px; border: 1px solid rgba(0, 245, 255, 0.2); }
.tag { background: rgba(0, 245, 255, 0.1); padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; color: #00FFFF; margin-right: 5px; border: 1px solid rgba(0, 245, 255, 0.2); }
.action-bar { display: flex; gap: 15px; margin-bottom: 40px; }
.btn-launch { background: #00FFFF; color: black; border: none; padding: 15px 40px; border-radius: 8px; font-weight: 800; font-size: 1.2rem; cursor: pointer; box-shadow: 0 0 20px rgba(0, 255, 255, 0.4); transition: 0.3s; }
.btn-launch:hover { transform: scale(1.05); box-shadow: 0 0 30px rgba(0, 255, 255, 0.6); }
.btn-share { background: transparent; border: 1px solid #555; color: white; padding: 0 20px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
.btn-share:hover { background: rgba(255,255,255,0.05); }
.description-box { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; line-height: 1.6; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
.preview-box img { width: 100%; border-radius: 12px; border: 1px solid #333; max-height: 450px; object-fit: contain; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
</style>
