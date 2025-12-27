//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\articles.js total lines 101 
//#######################################################################

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiGetMyArticles, apiCreateArticle, apiUpdateArticle, apiDeleteArticle, apiGetArticleForEdit } from '@/api';
import { useUiStore } from './ui';
import router from '@/router';

export const useArticlesStore = defineStore('articles', () => {
    const myArticles = ref([]);
    const currentArticle = ref(null);
    const isLoading = ref(false);
    const uiStore = useUiStore();
    async function fetchMyArticles() {
        isLoading.value = true;
        const result = await apiGetMyArticles();
        if (result.error) {
            uiStore.showNotification({ text: result.error, color: 'error' });
        } else {
            myArticles.value = result;
        }
        isLoading.value = false;
    }

    async function loadArticleForEdit(articleId) {
        isLoading.value = true;
        currentArticle.value = null;
        const result = await apiGetArticleForEdit(articleId);
        if (result.error) {
            uiStore.showNotification({ text: result.error, color: 'error' });
            router.push('/my-articles');
            isLoading.value = false;
            return { success: false, error: result.error };
        } else {
            currentArticle.value = result;
            isLoading.value = false;
            return { success: true, data: result };
        }
    }

    async function saveArticle(articleData, mode) {
        isLoading.value = true;
        const uiStore = useUiStore();
        const payload = { ...articleData };

        try {
            let result;
            if (mode === 'edit') {
                if (!articleData.id) {
                    throw new Error("Article ID is missing for update operation.");
                }
                result = await apiUpdateArticle(articleData.id, payload);
            } else { // Mode 'create'
                result = await apiCreateArticle(payload);
            }
            if (result.error) throw new Error(result.error);
            uiStore.showNotification({ text: 'Article saved successfully!', color: 'success' });
            await fetchMyArticles();
            router.push('/my-articles');

            return { success: true, data: result };
        } catch (e) {
            uiStore.showNotification({ text: e.message || 'Failed to save article.', color: 'error' });
            return { success: false, error: e.message };
        } finally {
            isLoading.value = false;
        }
    }

    async function deleteArticle(articleId) {
        isLoading.value = true;
        const uiStore = useUiStore();
        try {
            const result = await apiDeleteArticle(articleId);
            if (result.error) throw new Error(result.error);
            if (result.message) { // api/index.js mengembalikan { message: ... }
                uiStore.showNotification({ text: 'Article deleted successfully.', color: 'info' });
                await fetchMyArticles();
            } else {
                throw new Error('Delete API did not confirm success.');
            }
        } catch (e) {
            uiStore.showNotification({ text: e.message || 'Failed to delete article.', color: 'error' });
        } finally {
            isLoading.value = false;
        }
    }
    return {
        myArticles,
        currentArticle,
        isLoading,
        fetchMyArticles,
        loadArticleForEdit,
        saveArticle,
        deleteArticle
    };
});
