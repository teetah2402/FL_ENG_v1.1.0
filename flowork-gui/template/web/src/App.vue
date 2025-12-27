//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\App.vue
//#######################################################################

<template>
  <v-app>
    <AppBar v-if="isMemberAreaPage" />

    <v-main v-if="isMemberAreaPage" class="main-content" :class="{ 'no-padding-main': isDesignerPage }">
      <NeuralCanvasBackground />

      <div
        class="global-persistent-iframe-layer app-layer"
        :class="{ 'visually-hidden-offscreen': !isAppPage }"
      >
        <div
          v-for="a in activeApps"
          :key="a.instanceId"
          v-show="currentAppTab === a.instanceId"
          class="persistent-iframe-wrapper"
        >
          <div class="iframe-safe-container">
              <iframe
                v-if="resolveUrl(a)"
                :id="`iframe-${a.instanceId}`"
                :src="resolveUrl(a)"
                class="persistent-app-frame"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals allow-downloads"
                @load="onGlobalIframeLoad(a.instanceId, a.id, 'app')"
                @error="onIframeError(a.instanceId)"
              ></iframe>

              <div v-if="appErrorStates[a.instanceId]" class="app-crash-overlay">
                  <v-icon size="x-large" color="error">mdi-alert-octagon</v-icon>
                  <p class="mt-2 luxury-text">APP_LOAD_FAILED</p>
                  <span class="text-caption text-grey">Check your local app's index.html syntax or connection.</span>
                  <v-btn size="small" variant="tonal" class="mt-4" @click="retryApp(a.instanceId)">RETRY_CONNECTION</v-btn>
              </div>
          </div>
        </div>
      </div>

      <AppDashboard v-show="isAppPage" class="persistent-app-layer" />

      <router-view v-slot="{ Component }">
        <transition name="luxury-zoom" mode="out-in">
          <component :is="Component" v-if="!isAppPage" />
        </transition>
      </router-view>
    </v-main>

    <div v-else class="public-layout">
      <DigitalFingerprintBackground />
      <LanderHeader v-if="isPublicPageWithLanderHeader" />
      <router-view v-slot="{ Component }">
        <transition name="luxury-zoom" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>

    <div class="notification-container">
      <TransitionGroup name="slide-x-reverse" tag="div">
        <v-alert
          v-for="notification in uiStore.notifications"
          :key="notification.id"
          v-model="notification.model"
          :color="notification.color"
          variant="tonal"
          closable
          @click:close="uiStore.removeNotification(notification.id)"
          class="notification-alert"
          :icon="`mdi-${notification.color === 'success' ? 'check-circle' : notification.color === 'error' ? 'alert-circle' : 'information'}-outline`"
          prominent
          border="start"
        >
          {{ notification.text }}
        </v-alert>
      </TransitionGroup>
    </div>
    <CommandPalette />
    <CookieConsentBanner />
    <GlobalConfirmationDialog />
    <GlobalTokenDialog />
  </v-app>
</template>

<script setup>
import { onMounted, onUnmounted, computed, watch, ref, reactive } from 'vue'; // [ADDED] reactive
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import { useUiStore } from '@/store/ui';
import { useWorkflowStore } from '@/store/workflow';
import { useAppStore } from '@/store/apps';
import { useSocketStore } from '@/store/socket';
import { apiClient, getGatewayUrl } from '@/api';

import AppBar from '@/components/AppBar.vue';
import LanderHeader from '@/components/LanderHeader.vue';
import CommandPalette from '@/components/CommandPalette.vue';
import NeuralCanvasBackground from '@/components/NeuralCanvasBackground.vue';
import CookieConsentBanner from '@/components/CookieConsentBanner.vue';
import DigitalFingerprintBackground from '@/components/DigitalFingerprintBackground.vue';
import GlobalConfirmationDialog from '@/components/GlobalConfirmationDialog.vue';
import GlobalTokenDialog from '@/components/GlobalTokenDialog.vue';
import AppDashboard from '@/views/AppDashboard.vue';

const route = useRoute();
const authStore = useAuthStore();
const uiStore = useUiStore();
const workflowStore = useWorkflowStore();
const appStore = useAppStore();
const socketStore = useSocketStore();

const isDesignerPage = computed(() => route.name === 'Designer');
const isAppPage = computed(() => route.name === 'AppsCenter');

const activeApps = computed(() => appStore.activeApps);
const currentAppTab = computed(() => appStore.currentTab);

const currentGatewayUrl = ref(getGatewayUrl());

// [ADDED] State for tracking broken apps
const appErrorStates = reactive({});

/**
 * [ADDED] Method to handle iframe load errors
 */
const onIframeError = (instanceId) => {
    console.error(`[AppShield] App instance ${instanceId} failed to load.`);
    appErrorStates[instanceId] = true;
};

/**
 * [ADDED] Method to retry loading a broken app
 */
const retryApp = (instanceId) => {
    appErrorStates[instanceId] = false;
    const iframe = document.getElementById(`iframe-${instanceId}`);
    if (iframe) iframe.src = iframe.src;
};

/**
 * [FIXED LOGIC] resolveUrl
 */
const resolveUrl = (item) => {
    if (!item || !item.targetUrl) return null;

    let finalUrl = '';
    if (item.source === 'cloud') {
        finalUrl = item.targetUrl;
    } else {
        finalUrl = `${currentGatewayUrl.value}${item.targetUrl}`;
        const engineId = socketStore.engineId || localStorage.getItem('flowork_active_engine_id');
        if (engineId && !finalUrl.includes('engine_id=')) {
            const separator = finalUrl.includes('?') ? '&' : '?';
            finalUrl = `${finalUrl}${separator}engine_id=${engineId}`;
        }
    }
    return finalUrl;
};

// ... keep onGlobalIframeLoad and other variables ...

const onGlobalIframeLoad = async (instanceId, itemId, type) => {
    // [ADDED] Clear error state on successful load
    appErrorStates[instanceId] = false;

    const dataKey = `${type}_${itemId}_data`;
    try {
        const response = await apiClient.get(`/variables/${dataKey}`).catch(() => null);
        if (!response || !response.data || response.data.value === null) return;

        let variableData = response.data;
        let savedData = null;
        try {
            savedData = JSON.parse(variableData.value);
        } catch(e) { savedData = variableData.value; }

        const iframe = document.getElementById(`iframe-${instanceId}`);
        if (iframe) iframe.contentWindow.postMessage({ type: 'CMD_LOAD', payload: savedData }, '*');
    } catch (e) { }
};

const memberAreaPages = [
  'Designer', 'Dashboard', 'MyEngines', 'Settings', 'Profile',
  'AiCenter', 'AiTrainer', 'QuickTools', 'AppsCenter',
  'MyArticles', 'ArticleEditorNew', 'ArticleEditorEdit',
  'ModelFactory', 'ModuleFactory', 'PromptManager', 'CoreEditor', 'Diagnostics',
  'AuthorizeEngine'
];

const hybridPages = ['News', 'Marketplace', 'MarketplaceItem'];
const publicPagesWithLanderHeader = [
  'Lander', 'PrivacyPolicy', 'TermsOfService', 'DMCA', 'ContactUs',
  'Login', 'Register', 'ArticleView', 'AuthorView', 'CategoryView', 'TagView', 'ArticleListEnglish', 'ArticleListIndonesian',
  'AboutUs'
];

const isMemberAreaPage = computed(() => {
  return memberAreaPages.includes(route.name) || (hybridPages.includes(route.name) && authStore.isAuthenticated);
});

const isPublicPageWithLanderHeader = computed(() => {
  return publicPagesWithLanderHeader.includes(route.name) || (hybridPages.includes(route.name) && !authStore.isAuthenticated);
});

const handleKeyDown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    uiStore.isCommandPaletteVisible ? uiStore.hideCommandPalette() : uiStore.showCommandPalette();
  }
};

onMounted(async () => {
  window.addEventListener('keydown', handleKeyDown);
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  if (token) {
    authStore.setToken(token);
    window.history.replaceState({}, document.title, window.location.pathname);
  }
  if (authStore.isAuthenticated) {
      appStore.restoreRemoteState();
  }
});

watch(() => authStore.isAuthenticated, (newVal) => {
    if (newVal) {
        appStore.restoreRemoteState();
    }
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});
</script>

<style scoped>
.main-content { position: relative; height: 100vh; overflow-y: auto; background-color: var(--bg-dark); }
.main-content.no-padding-main { padding-top: 0 !important; height: 100vh; overflow: hidden; background-color: var(--bg-dark); }

/* [FIXED] Standardized Persistent Layer */
.global-persistent-iframe-layer { position: fixed; top: 160px; left: 300px; right: 20px; bottom: 20px; z-index: 5; display: flex; flex-direction: column; pointer-events: none; }
.persistent-iframe-wrapper { width: 100%; height: 100%; pointer-events: auto; }

/* [ADDED] Shield Styles */
.iframe-safe-container { position: relative; width: 100%; height: 100%; overflow: hidden; border-radius: 16px; }
.app-crash-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(10, 15, 30, 0.95); z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border: 2px dashed #FF5252; border-radius: 16px; }
.luxury-text { font-family: 'Orbitron', sans-serif; letter-spacing: 2px; color: white; }

.persistent-app-frame { width: 100%; height: 100%; border: none; display: block; background: #1e1e2e; box-shadow: 0 0 50px rgba(0,0,0,0.5); border: 1px solid rgba(0, 245, 255, 0.2); }
.persistent-app-layer { width: 100%; height: 100%; }

.visually-hidden-offscreen { visibility: hidden; pointer-events: none !important; left: -9999px; top: -9999px; width: 1px; height: 1px; }
.public-layout { min-height: 100vh; display: flex; flex-direction: column; position: relative; background-color: var(--bg-dark); }
.notification-container { position: fixed; bottom: 16px; right: 16px; z-index: 10000; width: 100%; max-width: 350px; }
.notification-alert { margin-top: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); border-width: 2px !important; }
.slide-x-reverse-enter-active, .slide-x-reverse-leave-active { transition: all 0.3s ease; }
.slide-x-reverse-enter-from, .slide-x-reverse-leave-to { transform: translateX(100%); opacity: 0; }
</style>