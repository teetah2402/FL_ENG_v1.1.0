//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\main.js total lines 147 
//#######################################################################

import { createApp } from 'vue'
import App from './App.vue'
import './styles/main.css'
import './styles/theme.css'
import { createPinia } from 'pinia'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import {
  VApp, VAppBar, VAppBarNavIcon, VBtn, VIcon, VSpacer, VMenu, VList, VListItem, VListItemTitle, VDivider,
  VLayout, VMain, VProgressCircular, VSnackbar, VRow, VCol, VCard, VCardText, VCardActions, VCardTitle,
  VContainer, VForm, VTextField, VCheckbox, VAlert, VImg, VAvatar, VChip, VDialog, VTabs, VTab, VWindow,
  VWindowItem, VNavigationDrawer, VExpansionPanels, VExpansionPanel, VExpansionPanelText, VSelect,
  VTextarea, VFileInput, VRadioGroup, VRadio, VSwitch, VDataTable, VToolbar, VToolbarTitle,
  VSkeletonLoader, VBtnToggle, VTooltip, VListSubheader, VCheckboxBtn
} from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import '@vue-flow/core/dist/style.css'
import router from './router/index.js'
import { useAuthStore } from './store/auth'
import { useLocaleStore } from './store/locale'
import { useSocketStore } from './store/socket' // (English Hardcode) ADDED: Import main socket store for Early Init

import ArticleComments from './components/ArticleComments.vue';
import { useUiStore } from './store/ui';

import VMdEditor from '@kangc/v-md-editor';
import '@kangc/v-md-editor/lib/style/base-editor.css';
import vuepressTheme from '@kangc/v-md-editor/lib/theme/vuepress.js';
import '@kangc/v-md-editor/lib/theme/style/vuepress.css';
import Prism from 'prismjs';

const floworkThemes = {
  themes: {
    flowork_default: {
      dark: true,
      colors: {
        background: '#1a1a2e',
        surface: '#2a2a4a',
        primary: '#64ffda',
        secondary: '#a59dff',
        error: '#ff5252',
        info: '#2196F3',
        success: '#4CAF50',
        warning: '#FB8C00',
      }
    },
    cyberpunk: { /* ... */ },
    light: { /* ... */ }
  }
}

const vuetify = createVuetify({
  components: {
    VApp, VAppBar, VAppBarNavIcon, VBtn, VIcon, VSpacer, VMenu, VList, VListItem, VListItemTitle, VDivider,
    VLayout, VMain, VProgressCircular, VSnackbar, VRow, VCol, VCard, VCardText, VCardActions, VCardTitle,
    VContainer, VForm, VTextField, VCheckbox, VAlert, VImg, VAvatar, VChip, VDialog, VTabs, VTab, VWindow,
    VWindowItem, VNavigationDrawer, VExpansionPanels, VExpansionPanel, VExpansionPanelText, VSelect,
    VTextarea, VFileInput, VRadioGroup, VRadio, VSwitch, VDataTable, VToolbar, VToolbarTitle,
    VSkeletonLoader, VBtnToggle, VTooltip, VListSubheader, VCheckboxBtn
  },
  directives,
  theme: floworkThemes
})

async function initializeApp() {
  const appElement = document.getElementById('app');
  if (appElement) {
    console.log('[Flowork] Main app element found, mounting GUI...');
    const app = createApp(App);
    const pinia = createPinia();
    app.use(pinia);

    const authStore = useAuthStore();
    const socketStore = useSocketStore();
    const localeStore = useLocaleStore();

    VMdEditor.use(vuepressTheme, {
      Prism,
    });
    app.use(VMdEditor);

    await localeStore.fetchDictionary();

    app.use(router);
    app.use(vuetify);

    await authStore.tryAutoLogin();

    if (authStore.isAuthenticated) {
        console.log('[Flowork Main] User is authenticated, connecting socket immediately...');
        socketStore.connect();
    }

    authStore.$subscribe((mutation, state) => {
        const isAuth = !!state.token && !!state.user;

        if (isAuth) {
            if (!socketStore.isConnected && !socketStore.isConnecting) {
                console.log('[Flowork Main Watcher] User logged IN, connecting socket...');
                socketStore.connect();
            }
        } else {
            if (socketStore.isConnected) {
                console.log('[Flowork Main Watcher] User logged OUT, disconnecting socket...');
                socketStore.disconnect();
            }
        }
    });

    app.mount('#app');
  }
}

async function initializeCommentsApp() {
    const commentsElement = document.getElementById('comments-app');
    if (commentsElement) {
        console.log('[Flowork] Comments app element found, mounting...');
        const { articleId, articleSlug } = commentsElement.dataset;

        const pinia = createPinia();
        const commentApp = createApp(ArticleComments, { articleId, articleSlug });

        commentApp.use(pinia);
        commentApp.use(vuetify);

        const localeStore = useLocaleStore(pinia);
        await localeStore.fetchDictionary();

        const authStore = useAuthStore(pinia);
        await authStore.tryAutoLogin();

        useUiStore(pinia);

        commentApp.mount('#comments-app');
        console.log('[Flowork] Comments app mounted successfully.');
    }
}

initializeApp();
initializeCommentsApp();
