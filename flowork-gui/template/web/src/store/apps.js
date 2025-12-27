//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\apps.js total lines 160
//#######################################################################

import { defineStore } from 'pinia';
import { apiClient, getComponentIconUrl } from '@/api';
import { useAuthStore } from '@/store/auth';
import { useSocketStore } from '@/store/socket'; // [REQUIRED] Ambil Engine ID

export const useAppStore = defineStore('apps', {
    state: () => ({
        installedApps: [],
        isLoading: false,
        activeApps: [],
        isSyncing: false,
        currentTab: null,
        // [ADDED] Storage for engine-side nodes used in Designer Toolbox
        appNodes: []
    }),

    getters: {
        getAppById: (state) => (id) => state.installedApps.find(a => a.id === id),
        getAppBySlug: (state) => (slug) => state.installedApps.find(a => a.slug === slug || a.id === slug),
    },

    actions: {
        setCurrentTab(instanceId) {
            this.currentTab = instanceId;
        },

        async fetchInstalledApps() {
            this.isLoading = true;
            let localApps = [];
            let cloudApps = [];
            const authStore = useAuthStore();
            const socketStore = useSocketStore(); // Akses socket untuk engine id

            console.log("[AppStore] Fetching apps...");

            try {
                const registryReq = await fetch('/apps-cloud/registry.json').catch(() => null);
                if (registryReq && registryReq.ok) {
                    const registry = await registryReq.json();
                    const appPromises = registry.map(async (item) => {
                        try {
                            const manifestPath = `/apps-cloud/${item.path}/manifest.json`;
                            const manifestReq = await fetch(manifestPath);
                            if (!manifestReq.ok) return null;
                            const manifest = await manifestReq.json();
                            return {
                                ...manifest,
                                source: 'cloud',
                                id: item.id,
                                slug: item.slug || item.id,
                                // [FIXED] Priority Name mapping for Cloud Apps
                                name: manifest.name || item.name || item.id,
                                iconUrl: manifest.icon_file || manifest.icon ? `/apps-cloud/${item.path}/${manifest.icon_file || manifest.icon}` : `/assets/icons/app_default.svg`,
                                targetUrl: `/apps-cloud/${item.path}/${manifest.entry_point || 'index.html'}`,
                                tier: manifest.tier || 'free'
                            };
                        } catch (e) { return null; }
                    });
                    const results = await Promise.all(appPromises);
                    cloudApps = results.filter(a => a !== null);
                }
            } catch (error) {
                console.warn("[AppStore] Failed to fetch cloud registry:", error);
            }

            if (authStore.isAuthenticated) {
                try {
                    const response = await apiClient.get('/apps').catch((err) => {
                        console.warn("[AppStore] /apps endpoint failed:", err);
                        return { data: [] };
                    });

                    if (response && response.data && Array.isArray(response.data)) {
                        const currentEngineId = socketStore.engineId;

                        localApps = response.data.map(a => {
                            const entryPoint = a.manifest?.entry_point || 'index.html';
                            const baseProxyPath = `/api/v1/apps/${a.id}/assets/${entryPoint}`;

                            const finalTargetUrl = currentEngineId
                                ? `${baseProxyPath}?engine_id=${currentEngineId}`
                                : baseProxyPath;

                            return {
                                ...a,
                                source: 'local',
                                id: a.id,
                                // [FIXED] Priority Name mapping: Search manifest first, then direct name, fallback to ID
                                name: a.manifest?.name || a.name || a.id,
                                description: a.manifest?.description || a.description || '',
                                iconUrl: getComponentIconUrl('app', a.id),
                                targetUrl: finalTargetUrl
                            };
                        });
                    }
                } catch (error) {
                    console.error("[AppStore] Error processing local apps:", error);
                }
            }

            this.installedApps = [...cloudApps, ...localApps];
            console.log(`[AppStore] Loaded ${this.installedApps.length} apps.`);

            // [ADDED] Synchronization logic for Designer Toolbox
            if (authStore.isAuthenticated) {
                try {
                    const nodeResponse = await apiClient.get('/apps/nodes').catch(() => ({ data: [] }));
                    if (nodeResponse && nodeResponse.data) {
                        this.appNodes = nodeResponse.data;
                        const { useComponentStore } = await import('./components');
                        const componentStore = useComponentStore();

                        const triggers = this.appNodes.filter(n => n.category === 'triggers');
                        const actions = this.appNodes.filter(n => n.category === 'modules');
                        const tools = this.appNodes.filter(n => n.category === 'tools');

                        if (triggers.length) componentStore.updateComponentsList('triggers', triggers);
                        if (actions.length) componentStore.updateComponentsList('modules', actions);
                        if (tools.length) componentStore.updateComponentsList('tools', tools);
                    }
                } catch (e) { }
            }

            this.isLoading = false;
        },

        async openApp(appId) {
            if (this.installedApps.length === 0) await this.fetchInstalledApps();
            const app = this.getAppById(appId);
            if (!app) return;

            const existing = this.activeApps.find(a => a.id === appId);
            if (!existing) {
                const newInstanceId = `app-${Date.now()}`;
                this.activeApps.push({ ...app, instanceId: newInstanceId });
                this.currentTab = newInstanceId;
                this.syncRemoteState();
            } else {
                this.currentTab = existing.instanceId;
            }
        },

        async restoreRemoteState() {
            try {
                if (this.installedApps.length === 0) await this.fetchInstalledApps();
                const response = await apiClient.get('/user/state/active_apps').catch(() => ({ data: [] }));
                const savedApps = response.data;

                if (Array.isArray(savedApps) && savedApps.length > 0) {
                    this.activeApps = savedApps.map(saved => {
                        const original = this.installedApps.find(a => a.id === saved.id);
                        return original ? { ...original, instanceId: saved.instanceId } : null;
                    }).filter(a => a !== null);

                    if (this.activeApps.length > 0 && !this.currentTab) {
                        this.currentTab = this.activeApps[0].instanceId;
                    }
                }
            } catch (error) {}
        },

        async syncRemoteState() {
            if (this.isSyncing) return;
            this.isSyncing = true;
            try {
                const payload = this.activeApps.map(a => ({ id: a.id, instanceId: a.instanceId, name: a.name }));
                await apiClient.put('/user/state/active_apps', payload).catch(() => {});
            } catch (error) {
            } finally { this.isSyncing = false; }
        },

        closeApp(instanceId) {
            this.activeApps = this.activeApps.filter(a => a.instanceId !== instanceId);
            if (this.currentTab === instanceId) {
                this.currentTab = this.activeApps.length ? this.activeApps[this.activeApps.length - 1].instanceId : null;
            }
            this.syncRemoteState();
        }
    }
});