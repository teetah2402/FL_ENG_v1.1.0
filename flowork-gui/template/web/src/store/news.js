//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\store\news.js total lines 137 
//#######################################################################

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiFetchNews } from '@/api';

async function fetchYouTubeNews() {
    const YOUTUBE_CHANNEL_ID = 'UCULzlhJUh-_VjdCXu-GouOQ'; // Contoh: Google Developers
    const RSS_URL = `https://www.youtube.com/feeds/videos.xml?channel_id=${YOUTUBE_CHANNEL_ID}`;

    const API_URL = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(RSS_URL)}`;

    console.log('[STORE] Fetching YouTube news from:', API_URL);

    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`rss2json API returned status ${response.status}`);
        }
        const data = await response.json();

        if (data.status !== 'ok') {
            throw new Error(`rss2json API error: ${data.message}`);
        }

        return data.items.map(item => ({
            title: item.title,
            link: item.link,
            pubDate: item.pubdate,
            imageUrl: item.thumbnail,
            source: 'YouTube'
        }));

    } catch (e) {
        console.error('[STORE] Failed to fetch YouTube news:', e);
        return [];
    }
}


export const useNewsStore = defineStore('news', () => {
    const articles = ref([]);
    const isLoading = ref(false);
    const error = ref(null);
    const currentPage = ref(1);
    const itemsPerPage = ref(10);

    const totalPages = computed(() => {
        return Math.ceil(articles.value.length / itemsPerPage.value);
    });

    const paginatedArticles = computed(() => {
        const startIndex = (currentPage.value - 1) * itemsPerPage.value;
        const endIndex = startIndex + itemsPerPage.value;
        return articles.value.slice(startIndex, endIndex);
    });

    async function fetchNews() {
        isLoading.value = true;
        error.value = null;

        try {
            const [coreResult, youtubeResult] = await Promise.allSettled([
                apiFetchNews(),
                fetchYouTubeNews()
            ]);

            let coreArticles = [];
            let youtubeArticles = [];
            if (coreResult.status === 'fulfilled' && !coreResult.value.error) {
                console.log('[STORE] Fetched Core news:', coreResult.value.length);
                coreArticles = coreResult.value;
            } else if (coreResult.status === 'rejected' || (coreResult.value && coreResult.value.error)) {
                console.warn('[STORE] Failed to fetch Core news (core/gateway might be offline):', coreResult.reason || coreResult.value.error);
            }

            if (youtubeResult.status === 'fulfilled') {
                console.log('[STORE] Fetched YouTube news:', youtubeResult.value.length);
                youtubeArticles = youtubeResult.value;
            } else {
                console.error('[STORE] YouTube fetch promise was rejected:', youtubeResult.reason);
                error.value = 'Failed to load YouTube news feed.';
            }

            const allArticles = [...coreArticles, ...youtubeArticles];

            const uniqueLinks = new Set();
            const uniqueAndSortedArticles = allArticles
                .filter(article => {
                    if (!article.link || uniqueLinks.has(article.link)) {
                        return false;
                    }
                    uniqueLinks.add(article.link);
                    return true;
                })
                .sort((a, b) => new Date(b.pubDate) - new Date(a.pubDate));

            articles.value = uniqueAndSortedArticles;

            if (articles.value.length === 0 && error.value) {
                console.error('[STORE] No articles loaded and an error occurred.');
            } else if (articles.value.length === 0) {
                console.warn('[STORE] No articles found from any source.');
                error.value = "No news or videos found."
            }


        } catch (e) {
            error.value = e.message || 'Failed to fetch news.';
            console.error('[STORE] Global failure in fetchNews:', e);
        } finally {
            isLoading.value = false;
        }
    }

    function setPage(page) {
        if (page > 0 && page <= totalPages.value) {
            currentPage.value = page;
        }
    }

    return {
        articles,
        isLoading,
        error,
        fetchNews,
        currentPage,
        itemsPerPage,
        totalPages,
        paginatedArticles,
        setPage
    };
});
