//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\profile.js total lines 106 
//#######################################################################

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';
import { apiClient } from '@/api';

export const useProfileStore = defineStore('profile', () => {
    const profile = ref(null);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchProfile() {
        const authStore = useAuthStore();
        const identifier = authStore.user?.public_address || authStore.user?.username;
        if (!identifier) return;

        isLoading.value = true;
        error.value = null;

        try {
            /*
            const response = await fetch(`${import.meta.env.VITE_GATEWAY_URL}/api/v1/user/public/${identifier}?t=${Date.now()}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!response.ok) throw new Error('Failed to fetch profile');
            const data = await response.json();
            */

            const response = await apiClient.get(`/user/public/${identifier}?t=${Date.now()}`);
            const data = response.data;

            profile.value = data;
            console.log('[ProfileStore] Profile loaded:', data);
        } catch (e) {
            console.error('[ProfileStore] Error:', e);
            const msg = e.response?.data?.error || e.message;
            error.value = msg;
        } finally {
            isLoading.value = false;
        }
    }

    async function saveProfile(updatedData) {
        const authStore = useAuthStore();
        if (!authStore.token && !authStore.privateKey) return false;

        isLoading.value = true;
        error.value = null;

        try {
            /*
            const response = await fetch(`${import.meta.env.VITE_GATEWAY_URL}/api/v1/user/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.token}`,
                    'X-Flowork-Auth': 'true'
                },
                body: JSON.stringify(updatedData)
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || 'Failed to save profile');
            }
            */

            const response = await apiClient.put('/user/profile', updatedData);
            const result = response.data;

            if (result.user && result.user.name) {
                if (authStore.user) {
                    authStore.user.username = result.user.name;

                    if(result.user.avatar) authStore.user.avatar = result.user.avatar;

                    localStorage.setItem('flowork_user', JSON.stringify(authStore.user));
                }

                profile.value = { ...profile.value, ...result.user };
            }

            return true;
        } catch (e) {
            console.error('[ProfileStore] Save failed:', e);
            const msg = e.response?.data?.error || e.message || "Unknown error";
            error.value = msg;
            return false;
        } finally {
            isLoading.value = false;
        }
    }

    return {
        profile,
        isLoading,
        error,
        fetchProfile,
        saveProfile
    };
});
