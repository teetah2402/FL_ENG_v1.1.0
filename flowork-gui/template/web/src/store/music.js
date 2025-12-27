//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\music.js total lines 75 
//#######################################################################

import { defineStore } from 'pinia';
import { cloudApiClient } from '@/api';
import { useAuthStore } from './auth';

export const useMusicStore = defineStore('music', {
    state: () => ({
        tracks: JSON.parse(localStorage.getItem('flowork_music_tracks') || '[]'),
        isGenerating: false,
        activeTasks: []
    }),

    actions: {
        async action(type, payload = {}) {
            const auth = useAuthStore();

            if (!auth.isPremium) {
                throw new Error("Access Denied: Premium Subscription Required");
            }

            this.isGenerating = true;
            try {
                const res = await cloudApiClient.post('/ai/music', {
                    type,
                    user_address: auth.user?.id,
                    ...payload
                });

                if (res.data && res.data.code === 200) {
                    if (type === 'audio') {
                        const newTrack = {
                            id: res.data.data.taskId,
                            title: payload.title || 'Neural Track',
                            prompt: payload.prompt,
                            status: 'processing',
                            model: payload.model || 'V5',
                            created_at: new Date().toISOString()
                        };
                        this.tracks.unshift(newTrack);
                        this.activeTasks.push(newTrack.id);
                        this.save();
                    }
                    return res.data;
                } else if (res.data.error) {
                    throw new Error(res.data.error);
                }

                throw new Error("Neural Bridge: Unexpected Response");
            } catch (e) {
                console.error("Neural Studio Error:", e);
                throw e;
            } finally {
                this.isGenerating = false;
            }
        },

        updateTrackStatus(taskId, status, audioUrl = null) {
            const track = this.tracks.find(t => t.id === taskId);
            if (track) {
                track.status = status;
                if (audioUrl) track.audioUrl = audioUrl;
                this.save();
            }
        },

        save() {
            localStorage.setItem('flowork_music_tracks', JSON.stringify(this.tracks.slice(0, 100)));
        }
    }
});
