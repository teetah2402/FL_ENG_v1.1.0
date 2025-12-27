//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\widgets.js total lines 250 
//#######################################################################

import { defineStore } from 'pinia';
import { apiClient, getComponentIconUrl } from '@/api';
import { useAuthStore } from '@/store/auth';

export const useWidgetStore = defineStore('widgets', {
    state: () => ({
        installedWidgets: [],
        isLoading: false,
        activeWidgets: [], // Widgets currently open in the workspace
        isSyncing: false,  // Flag to prevent race conditions during sync
        userLicenses: {},   // Cache for user licenses { widget_id: "LICENSE_KEY" }
        currentTab: null
    }),

    getters: {
        getWidgetById: (state) => (id) => state.installedWidgets.find(w => w.id === id),
    },

    actions: {
        setCurrentTab(instanceId) {
            this.currentTab = instanceId;
        },

        async fetchInstalledWidgets() {
            this.isLoading = true;
            let localWidgets = [];
            let cloudWidgets = [];

            const authStore = useAuthStore();

            try {
                const registryReq = await fetch('/widgets-cloud/registry.json');
                if (registryReq.ok) {
                    const registry = await registryReq.json();

                    const widgetPromises = registry.map(async (item) => {
                        try {
                            const manifestPath = `/widgets-cloud/${item.path}/${item.manifest_file || 'manifest.json'}`;
                            const manifestReq = await fetch(manifestPath);

                            if (!manifestReq.ok) {
                                console.warn(`[WidgetStore] Manifest not found for ${item.id} at ${manifestPath}`);
                                return null;
                            }

                            const manifest = await manifestReq.json();

                            return {
                                ...manifest,
                                source: 'cloud',
                                slug: item.slug,
                                iconUrl: manifest.icon_file
                                    ? `/widgets-cloud/${item.path}/${manifest.icon_file}`
                                    : `/assets/icons/cloud_widget.png`,
                                targetUrl: `/widgets-cloud/${item.path}/${manifest.entry_point || 'index.html'}`,
                                tier: manifest.tier || 'free'
                            };
                        } catch (e) {
                            console.warn(`[WidgetStore] Failed to load cloud widget: ${item.id}`, e);
                            return null;
                        }
                    });

                    const results = await Promise.all(widgetPromises);
                    cloudWidgets = results.filter(w => w !== null);
                } else {
                    console.warn("[WidgetStore] registry.json not found. Skipping cloud widgets.");
                }
            } catch (error) {
                console.error("[WidgetStore] Failed to load cloud registry:", error);
            }

            if (authStore.isAuthenticated) {
                try {
                    const response = await apiClient.get('/widgets');
                    if (response.data && Array.isArray(response.data)) {
                        localWidgets = response.data.map(w => ({
                            ...w,
                            source: 'local',
                            tier: w.tier || 'registered',
                            iconUrl: getComponentIconUrl('widget', w.id),
                            targetUrl: `/api/v1/widgets/${w.id}/assets/${w.manifest.entry_point || 'index.html'}`
                        }));
                    }
                } catch (error) {
                    console.warn("[WidgetStore] Gateway offline or unreachable. Local widgets unavailable.");
                }
            } else {
                console.log("[WidgetStore] Guest mode active. Skipping local widgets fetch.");
            }

            this.installedWidgets = [...cloudWidgets, ...localWidgets];

            this.isLoading = false;
            console.log(`[WidgetStore] Total Loaded: ${this.installedWidgets.length} (${cloudWidgets.length} Cloud, ${localWidgets.length} Local).`);
        },

        async checkAccess(widget) {
            const authStore = useAuthStore();

            if (authStore.isPremium) {
                console.log(`[WidgetStore] VIP Access granted for: ${widget.name}. Bypassing license check.`);
                return { allowed: true };
            }

            if (!widget.tier || widget.tier === 'free') {
                return { allowed: true };
            }

            if (widget.tier === 'registered') {
                if (!authStore.isAuthenticated) {
                    return {
                        allowed: false,
                        reason: 'login_required',
                        message: 'You must be logged in to use this widget.'
                    };
                }
                return { allowed: true };
            }

            if (widget.tier === 'paid' || widget.tier === 'pro') {
                if (!authStore.isAuthenticated) {
                    return { allowed: false, reason: 'login_required', message: 'Login required.' };
                }

                const hasLicense = await this.verifyLicense(widget.id);
                if (!hasLicense) {
                    return {
                        allowed: false,
                        reason: 'license_required',
                        message: 'This is a Premium Widget. Please activate a license.'
                    };
                }
                return { allowed: true };
            }

            return { allowed: true };
        },

        async verifyLicense(widgetId) {
            if (this.userLicenses[widgetId]) return true;

            try {
                const response = await apiClient.get(`/variables/license_${widgetId}`);
                if (response.data && response.data.value) {
                    this.userLicenses[widgetId] = response.data.value; // Cache it
                    return true;
                }
            } catch (e) {
            }
            return false;
        },

        async openWidget(widgetId) {
            if (this.installedWidgets.length === 0) await this.fetchInstalledWidgets();

            const widget = this.getWidgetById(widgetId);
            if (!widget) return;

            const access = await this.checkAccess(widget);

            if (!access.allowed) {
                alert(`🛑 ACCESS DENIED: ${access.message}`);
                return;
            }

            const existing = this.activeWidgets.find(w => w.id === widgetId);
            if (!existing) {
                const newInstanceId = Date.now();
                this.activeWidgets.push({
                    ...widget,
                    instanceId: newInstanceId
                });
                this.currentTab = newInstanceId;
                this.syncRemoteState();
            } else {
                this.currentTab = existing.instanceId;
                console.log(`[WidgetStore] ${widget.name} is already open.`);
            }
        },

        async openWidgetBySlug(slug) {
            if (this.installedWidgets.length === 0) await this.fetchInstalledWidgets();
            const widget = this.installedWidgets.find(w => w.slug === slug || w.id === slug);
            if (widget) this.openWidget(widget.id);
        },

        async restoreRemoteState() {
            try {
                if (this.installedWidgets.length === 0) {
                    await this.fetchInstalledWidgets();
                }

                const response = await apiClient.get('/user/state/active_widgets');
                const savedWidgets = response.data;

                if (Array.isArray(savedWidgets) && savedWidgets.length > 0) {
                    this.activeWidgets = savedWidgets.map(saved => {
                        const original = this.installedWidgets.find(w => w.id === saved.id);
                        return original ? {
                            ...original,
                            instanceId: saved.instanceId
                        } : null;
                    }).filter(w => w !== null);

                    if (this.activeWidgets.length > 0 && !this.currentTab) {
                        this.currentTab = this.activeWidgets[0].instanceId;
                    }

                    console.log(`[WidgetStore] Restored ${this.activeWidgets.length} active widgets.`);
                }
            } catch (error) {
                console.warn("[WidgetStore] No remote state found or sync error:", error);
            }
        },

        async syncRemoteState() {
            if (this.isSyncing) return;
            this.isSyncing = true;
            try {
                const payload = this.activeWidgets.map(w => ({
                    id: w.id,
                    instanceId: w.instanceId,
                    name: w.name
                }));

                await apiClient.put('/user/state/active_widgets', payload);
                console.log("[WidgetStore] Layout synced to cloud (Auto-Save).");
            } catch (error) {
                console.error("[WidgetStore] Sync failed:", error);
            } finally {
                this.isSyncing = false;
            }
        },

        closeWidget(instanceId) {
            this.activeWidgets = this.activeWidgets.filter(w => w.instanceId !== instanceId);
            if (this.currentTab === instanceId) {
                this.currentTab = this.activeWidgets.length ? this.activeWidgets[this.activeWidgets.length - 1].instanceId : null;
            }
            this.syncRemoteState();
        }
    }
});
