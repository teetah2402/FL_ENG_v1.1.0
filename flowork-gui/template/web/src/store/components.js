//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\components.js
//#######################################################################

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useSocketStore } from './socket';
import { useLocaleStore } from './locale';
import exampleComponents from '../../public/example/components.json';
import { apiGetUserComponentFavorites, apiSetUserComponentFavorites, apiSaveCustomComponent } from '@/api';
import { debounce } from '@/utils/debounce.js';
import { useAuthStore } from './auth';
import { useUiStore } from './ui';
import { useEngineStore } from './engines';
// [OBSOLETE] import { useAppStore } from './apps'; // Moved to dynamic import inside function

const CACHE_KEY_PREFIX = 'flowork_component_cache_';

const createComponentTypeState = () => ({
  items: [],
  isLoading: false,
  hasFetched: false,
});

export const useComponentStore = defineStore('components', () => {
  const modules = ref(createComponentTypeState());
  const plugins = ref(createComponentTypeState());
  const tools = ref(createComponentTypeState());
  const triggers = ref(createComponentTypeState());
  const apps = ref(createComponentTypeState());

  const favoriteComponents = ref([]);
  const installingComponentId = ref(null);
  const uninstallingComponentId = ref(null);

  const fetchTimers = ref({});
  const error = ref(null);

  const isLoading = computed(() =>
    modules.value.isLoading ||
    plugins.value.isLoading ||
    tools.value.isLoading ||
    triggers.value.isLoading ||
    apps.value.isLoading
  );

  const allComponents = computed(() => {
    const all = [];
    modules.value.items.forEach(m => all.push({ ...m, componentType: 'modules' }));
    plugins.value.items.forEach(p => all.push({ ...p, componentType: 'plugins' }));
    tools.value.items.forEach(t => all.push({ ...t, componentType: 'tools' }));
    triggers.value.items.forEach(t => all.push({ ...t, componentType: 'triggers' }));
    apps.value.items.forEach(a => all.push({ ...a, componentType: 'apps' }));
    return all;
  });

  const findComponentById = (id) => {
    return allComponents.value.find(c => c.id === id);
  };

  function clearTimersForType(type) {
    if (fetchTimers.value[type]) {
      clearTimeout(fetchTimers.value[type]?.realDataTimeoutId);
      delete fetchTimers.value[type];
    }
  }

  const saveFavoritesDebounced = debounce(async () => {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;
    try {
        console.log("[ComponentStore] Debounced save: Sending updated component favorites to Gateway...");
        await apiSetUserComponentFavorites(favoriteComponents.value);
        console.log("[ComponentStore] Debounced save: Component favorites successfully saved to Gateway.");
    } catch (error) {
        console.error("[ComponentStore] Debounced save: Failed to save component favorites:", error);
        const uiStore = useUiStore();
        uiStore.showNotification({ text: `Error saving component favorites: ${error.error || error.message}`, color: 'error'});
    }
  }, 1500);

  async function fetchUserFavorites() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;
    try {
        console.log("[ComponentStore] Fetching user favorite components from Gateway...");
        const favorites = await apiGetUserComponentFavorites();
        if (favorites.error) throw new Error(favorites.error);
        favoriteComponents.value = favorites;
        console.log(`[ComponentStore] User component favorites loaded: ${favorites.length} items.`);
    } catch (error) {
        console.error("[ComponentStore] Failed to fetch user component favorites:", error);
        favoriteComponents.value = [];
    }
  }

  function toggleFavorite(componentId) {
    const index = favoriteComponents.value.indexOf(componentId);
    if (index > -1) {
        favoriteComponents.value.splice(index, 1);
    } else {
        favoriteComponents.value.push(componentId);
    }
    saveFavoritesDebounced();
  }

  async function installComponent(componentType, componentId) {
    if (installingComponentId.value || uninstallingComponentId.value) {
        useUiStore().showNotification({ text: 'Another component operation is already in progress.', color: 'warning' });
        return;
    }
    const socketStore = useSocketStore();
    installingComponentId.value = componentId;
    try {
        await socketStore.sendMessage({
            type: 'install_component',
            component_type: componentType,
            component_id: componentId,
        });
        useUiStore().showNotification({ text: `Installation started for ${componentId}...`, color: 'info' });
    } catch (e) {
        console.error("[ComponentStore] Failed to send install request:", e);
        useUiStore().showNotification({ text: `Failed to start installation: ${e.message}`, color: 'error' });
        installingComponentId.value = null;
    }
  }

  async function uninstallComponent(componentType, componentId) {
    if (installingComponentId.value || uninstallingComponentId.value) {
        useUiStore().showNotification({ text: 'Another component operation is already in progress.', color: 'warning' });
        return;
    }
    const socketStore = useSocketStore();
    uninstallingComponentId.value = componentId;
    try {
        await socketStore.sendMessage({
            type: 'uninstall_component',
            component_type: componentType,
            component_id: componentId,
        });
        useUiStore().showNotification({ text: `Uninstalling ${componentId}...`, color: 'info' });
    } catch (e) {
        console.error("[ComponentStore] Failed to send uninstall request:", e);
        useUiStore().showNotification({ text: `Failed to start uninstallation: ${e.message}`, color: 'error' });
        uninstallingComponentId.value = null;
    }
  }

  function handleInstallStatusUpdate(data) {
    const { component_id, component_type, success, message, is_installed } = data;

    if (installingComponentId.value === component_id) installingComponentId.value = null;
    if (uninstallingComponentId.value === component_id) uninstallingComponentId.value = null;

    const uiStore = useUiStore();
    if (success) {
        uiStore.showNotification({ text: `${component_id}: ${message}`, color: 'success' });
    } else {
        uiStore.showNotification({ text: `${component_id}: ${message}`, color: 'error', timeout: 7000 });
    }

    const stateMap = { modules, plugins, tools, triggers, apps };
    const stateRef = stateMap[component_type];
    if (stateRef && stateRef.value) {
        const item = stateRef.value.items.find(i => i.id === component_id);
        if (item) {
            item.is_installed = is_installed;
            console.log(`[ComponentStore] Updated install status for ${component_id}: ${is_installed}`);
            saveToCache(component_type, stateRef.value.items);
        }
    }
  }

  function updateComponentsList(type, components, errorMessage = null) {
    const stateMap = { modules, plugins, tools, triggers, apps };
    const stateRef = stateMap[type];

    if (stateRef && stateRef.value) {
      stateRef.value.isLoading = false;
      stateRef.value.hasFetched = true;

      if (errorMessage) {
          console.warn(`[ComponentStore] Received ERROR for ${type}: ${errorMessage}`);
          return;
      }

      console.log(`[ComponentStore] Received ${components.length} REAL items for ${type}. Updating state and cache.`);

      const processedComponents = components.map(c => {
          return {
            ...c,
            is_example: false,
            is_installed: c.is_installed || false,
            // [ADDED] Fallback for node labels to ensure Toolbox text appears
            name: c.label || c.name || c.id,
            // [FIXED] Variable name must match frontend expectation (camelCase)
            iconUrl: c.icon ? `/api/v1/apps/${c.app_id || c.id}/assets/${c.icon}` : null
          };
      });

      stateRef.value.items = processedComponents;
      error.value = null;

      saveToCache(type, processedComponents);

    } else {
      console.warn(`[ComponentStore] Received update for unknown type: ${type}`);
    }
  }

  function saveToCache(type, items) {
      try {
          localStorage.setItem(CACHE_KEY_PREFIX + type, JSON.stringify(items));
      } catch (e) {
          console.warn("[ComponentStore] Failed to save components to cache:", e);
      }
  }

  async function fetchComponentsForType(type, options = { reset: false }) {
    // [SPECIAL CASE] Apps are handled by AppStore, but we can hook into it
    if (type === 'apps') {
        const { useAppStore } = await import('./apps'); // [FIXED] Dynamic import
        const appStore = useAppStore();
        await appStore.fetchInstalledApps();

        // [ADDED] Synchronization logic to bridge AppStore into Designer Toolbox
        apps.value.items = appStore.installedApps.map(a => ({
            ...a,
            componentType: 'apps',
            is_installed: true
        }));
        apps.value.hasFetched = true;
        apps.value.isLoading = false;

        // [OBSOLETE] apps.value.items = appStore.installedApps;
        return;
    }

    const stateMap = { modules, plugins, tools, triggers, apps };
    const stateRef = stateMap[type];
    if (!stateRef || !stateRef.value) {
        return;
    }
    const currentState = stateRef.value;

    clearTimersForType(type);

    if (options.reset) {
        currentState.hasFetched = false;
    }

    if (currentState.items.length === 0) {
        try {
            const cachedData = localStorage.getItem(CACHE_KEY_PREFIX + type);
            if (cachedData) {
                const parsedItems = JSON.parse(cachedData);
                if (Array.isArray(parsedItems) && parsedItems.length > 0) {
                    currentState.items = parsedItems;
                }
            }
        } catch (e) {}
    }

    currentState.isLoading = true;
    error.value = null;

    if (currentState.items.length === 0) {
        const localeStore = useLocaleStore();
        const exampleData = exampleComponents[type] || [];
        const translatedExamples = exampleData.map(c => ({
            ...c,
            name: localeStore.loc(c.name) || c.name,
            manifest: {
                ...c.manifest,
                name: localeStore.loc(c.manifest?.name) || c.manifest?.name || c.name,
                description: localeStore.loc(c.manifest?.description) || c.manifest?.description || ''
            },
            is_example: true,
            is_installed: false
        }));
        currentState.items = translatedExamples;
    }

    const socketStore = useSocketStore();
    const engineStore = useEngineStore();

    if (socketStore.isConnected) {
        try {
            const payload = {
                type: 'request_components_list',
                component_type: type,
                target_engine_id: engineStore.selectedEngineId
            };
            socketStore.sendMessage(payload);

            fetchTimers.value[type] = {
                realDataTimeoutId: setTimeout(() => {
                    if (currentState.isLoading) {
                        currentState.isLoading = false;
                    }
                }, 5000)
            };

        } catch (e) {
            currentState.isLoading = false;
            currentState.hasFetched = false;
        }
    } else {
        if (currentState.items.length > 0) {
             currentState.isLoading = false;
        }
    }
  }

  async function fetchAllComponents() {
      await Promise.all([
          fetchComponentsForType('modules'),
          fetchComponentsForType('plugins'),
          fetchComponentsForType('tools'),
          fetchComponentsForType('triggers'),
          fetchComponentsForType('apps')
      ]);
  }

  async function forceRefetchAllComponents() {
      await Promise.all([
          fetchComponentsForType('modules',  { reset: true }),
          fetchComponentsForType('plugins',  { reset: true }),
          fetchComponentsForType('tools',    { reset: true }),
          fetchComponentsForType('triggers', { reset: true }),
          fetchComponentsForType('apps',     { reset: true })
      ]);
  }

  async function saveCustomComponent(componentData) {
      const uiStore = useUiStore();
      try {
          const result = await apiSaveCustomComponent(componentData);
          if (result.error) throw new Error(result.error);

          uiStore.showNotification({ text: `Component ${componentData.id} saved successfully!`, color: 'success' });

          const typeMap = {
              'module': 'modules',
              'plugin': 'plugins',
              'tool': 'tools',
              'trigger': 'triggers',
              'app': 'apps'
          };
          const targetType = typeMap[componentData.type] || 'modules';
          await fetchComponentsForType(targetType, { reset: true });

          return { success: true };
      } catch (e) {
          uiStore.showNotification({ text: `Failed to save component: ${e.message}`, color: 'error' });
          return { success: false, error: e.message };
      }
  }

  return {
    modules, plugins, tools, triggers, apps,
    favoriteComponents,
    installingComponentId,
    uninstallingComponentId,
    isLoading,
    allComponents,
    fetchComponentsForType,
    fetchAllComponents,
    forceRefetchAllComponents,
    updateComponentsList,
    findComponentById,
    fetchUserFavorites,
    toggleFavorite,
    installComponent,
    uninstallComponent,
    handleInstallStatusUpdate,
    saveCustomComponent,
    error
  };
});