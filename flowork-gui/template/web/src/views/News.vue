//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\News.vue total lines 336 
//#######################################################################

<template>
  <div class="news-page">
    <div class="tech-grid-bg"></div>
    <NeuralCanvasBackground class="subtle-neural" />

    <v-container class="news-container">
      <v-row justify="center">
        <v-col cols="12" md="11" lg="10">

          <div class="header-section text-center mb-12 fade-in-down">
            <div class="d-inline-flex align-center justify-center px-4 py-1 border-cyan-dim rounded-pill mb-4 bg-black-transparent">
                <v-icon icon="mdi-access-point-network" color="cyan" size="small" class="mr-2 icon-pulse"></v-icon>
                <span class="text-caption text-cyan font-mono tracking-widest">LIVE DATA STREAM</span>
            </div>
            <h1 class="main-title orbitron-font text-white">
              GLOBAL <span class="text-gold">INTELLIGENCE</span>
            </h1>
            <p class="text-grey-lighten-1 mt-2 font-mono" style="max-width: 600px; margin: 0 auto;">
              Latest transmissions, system updates, and neural network expansions from the Flowork core.
            </p>
          </div>

          <div v-if="isLoading" class="text-center py-16">
            <div class="scanner-container mx-auto mb-6">
                <div class="scanner-line"></div>
            </div>
            <p class="text-cyan font-mono blink-text">ESTABLISHING UPLINK...</p>
          </div>

          <div v-else-if="error" class="text-center py-16 border-red-dim pa-8 rounded-lg bg-black-transparent">
            <v-icon icon="mdi-alert-octagon-outline" size="64" color="red-accent-2" class="mb-4"></v-icon>
            <h3 class="text-h6 text-red-accent-2 orbitron-font">CONNECTION INTERRUPTED</h3>
            <p class="text-grey font-mono mt-2">{{ error }}</p>
            <v-btn variant="outlined" color="red-accent-2" class="mt-6 font-mono" @click="newsStore.fetchNews()">
                RETRY HANDSHAKE
            </v-btn>
          </div>

          <v-row v-else>
            <v-col
              v-for="(article, index) in paginatedArticles"
              :key="article.link"
              cols="12"
              md="6"
              lg="4"
              class="fade-in-up"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <a :href="article.link" target="_blank" rel="noopener noreferrer" class="card-link">
                  <div class="holo-card">
                    <div class="image-wrapper">
                        <v-img
                          :src="article.imageUrl || '/images/default-news-bg.jpg'"
                          class="card-image"
                          aspect-ratio="16/9"
                          cover
                        >
                          <template v-slot:placeholder>
                            <div class="d-flex align-center justify-center fill-height bg-grey-darken-4">
                              <v-progress-circular indeterminate color="cyan" size="24"></v-progress-circular>
                            </div>
                          </template>
                        </v-img>
                        <div class="tech-overlay"></div>
                        <div class="scan-line"></div>
                    </div>

                    <div class="card-content pa-5 d-flex flex-column flex-grow-1">
                        <div class="d-flex justify-space-between align-center mb-3">
                            <span class="text-caption text-cyan font-mono border-cyan px-2 py-0-5 rounded-0">
                                {{ article.category || 'SYSTEM' }}
                            </span>
                            <span class="text-caption text-grey font-mono">
                                {{ formatDate(article.pubDate) }}
                            </span>
                        </div>

                        <h3 class="article-title orbitron-font mb-3">
                            {{ article.title }}
                        </h3>

                        <p class="article-snippet text-grey-lighten-1 font-sans mb-4 flex-grow-1">
                            {{ truncateText(article.snippet || article.description, 100) }}
                        </p>

                        <div class="d-flex align-center mt-auto pt-4 border-top-dim">
                            <span class="text-caption text-gold font-weight-bold text-uppercase tracking-wide read-more-text">
                                ACCESS DATA
                            </span>
                            <v-spacer></v-spacer>
                            <v-icon icon="mdi-arrow-right-thin" color="amber-accent-3" class="arrow-anim"></v-icon>
                        </div>
                    </div>

                    <div class="corner-tl"></div>
                    <div class="corner-br"></div>
                  </div>
              </a>
            </v-col>
          </v-row>

          <v-row justify="center" v-if="totalPages > 1" class="mt-12">
            <v-col cols="auto">
              <v-pagination
                v-model="currentPage"
                :length="totalPages"
                :total-visible="5"
                rounded="0"
                active-color="cyan"
                color="grey-darken-3"
                class="tech-pagination"
                @update:modelValue="newsStore.setPage"
              ></v-pagination>
            </v-col>
          </v-row>

        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useNewsStore } from '@/store/news';
import { storeToRefs } from 'pinia';
import NeuralCanvasBackground from '@/components/NeuralCanvasBackground.vue';

const newsStore = useNewsStore();
const { isLoading, error, paginatedArticles, totalPages } = storeToRefs(newsStore);

const currentPage = computed({
  get: () => newsStore.currentPage,
  set: (value) => newsStore.setPage(value)
});

function formatDate(dateString) {
    try {
        if (!dateString) return 'UNKNOWN DATE';
        const date = new Date(dateString);
        return date.toISOString().split('T')[0].replace(/-/g, '.');
    } catch (e) {
        return dateString;
    }
}

function truncateText(text, length) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
}

onMounted(() => {
  newsStore.fetchNews();
});
</script>

<style scoped>
/* --- BASE LAYOUT --- */
.news-page {
  height: 100%;
  overflow-y: auto;
  position: relative;
  background-color: #050505;
  color: #e0e0e0;
}
.news-container {
    padding-top: 60px;
    padding-bottom: 100px;
    position: relative;
    z-index: 2;
}

/* Background Layers */
.tech-grid-bg {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    z-index: 0;
    pointer-events: none;
}
.subtle-neural {
    opacity: 0.3;
    pointer-events: none;
    z-index: 0;
}

/* --- TYPOGRAPHY & COLORS --- */
.orbitron-font { font-family: 'Orbitron', sans-serif; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
.font-sans { font-family: 'Inter', sans-serif; line-height: 1.5; font-size: 0.9rem; }

.text-gold { color: #FFD700 !important; text-shadow: 0 0 15px rgba(255, 215, 0, 0.3); }
.text-cyan { color: #00F5FF !important; }
.border-cyan { border: 1px solid #00F5FF; }
.border-cyan-dim { border: 1px solid rgba(0, 245, 255, 0.2); }
.border-red-dim { border: 1px solid rgba(255, 82, 82, 0.3); }
.border-top-dim { border-top: 1px solid rgba(255, 255, 255, 0.1); }
.bg-black-transparent { background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(5px); }

.main-title {
    font-size: 2.5rem;
    letter-spacing: 2px;
    text-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
}

/* --- HOLOGRAPHIC CARD --- */
.card-link { text-decoration: none; display: block; height: 100%; }

.holo-card {
    background: rgba(10, 15, 25, 0.7);
    border: 1px solid rgba(0, 245, 255, 0.1);
    backdrop-filter: blur(10px);
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.holo-card:hover {
    transform: translateY(-5px);
    border-color: rgba(0, 245, 255, 0.5);
    box-shadow: 0 10px 30px rgba(0, 245, 255, 0.1);
}

/* Image Tech Effects */
.image-wrapper {
    position: relative;
    overflow: hidden;
    height: 200px;
    border-bottom: 1px solid rgba(0, 245, 255, 0.1);
}
.card-image {
    transition: transform 0.6s ease;
}
.holo-card:hover .card-image {
    transform: scale(1.05);
}
.tech-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(5,5,5,0.8) 100%);
    z-index: 1;
}
.scan-line {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 2px;
    background: #00F5FF;
    opacity: 0;
    z-index: 2;
    box-shadow: 0 0 10px #00F5FF;
}
.holo-card:hover .scan-line {
    animation: scan 1.5s linear infinite;
    opacity: 0.7;
}

@keyframes scan {
    0% { top: 0%; }
    100% { top: 100%; }
}

/* Card Content */
.article-title {
    color: #fff;
    font-size: 1.1rem;
    line-height: 1.4;
    transition: color 0.3s;
}
.holo-card:hover .article-title {
    color: #00F5FF;
}

/* Interactive Elements */
.read-more-text { transition: letter-spacing 0.3s; }
.holo-card:hover .read-more-text { letter-spacing: 0.1em; }

.arrow-anim { transition: transform 0.3s; }
.holo-card:hover .arrow-anim { transform: translateX(5px); }

/* Decorative Corners */
.corner-tl { position: absolute; top: 0; left: 0; width: 10px; height: 10px; border-top: 2px solid #00F5FF; border-left: 2px solid #00F5FF; opacity: 0; transition: 0.3s; }
.corner-br { position: absolute; bottom: 0; right: 0; width: 10px; height: 10px; border-bottom: 2px solid #FFD700; border-right: 2px solid #FFD700; opacity: 0; transition: 0.3s; }

.holo-card:hover .corner-tl, .holo-card:hover .corner-br { opacity: 1; }

/* --- ANIMATIONS --- */
.fade-in-down { animation: fadeInDown 0.8s ease-out forwards; }
.fade-in-up { opacity: 0; animation: fadeInUp 0.6s ease-out forwards; }

@keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.icon-pulse { animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

.blink-text { animation: blink 1s infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* Scanner Loader */
.scanner-container { width: 200px; height: 2px; background: rgba(0, 245, 255, 0.2); position: relative; overflow: hidden; }
.scanner-line { width: 50%; height: 100%; background: #00F5FF; position: absolute; animation: scannerMove 1.5s infinite ease-in-out; box-shadow: 0 0 10px #00F5FF; }
@keyframes scannerMove { 0% { left: -50%; } 100% { left: 100%; } }

/* --- PAGINATION OVERRIDE --- */
.tech-pagination :deep(.v-pagination__item) {
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin: 0 2px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    transition: all 0.3s;
}
.tech-pagination :deep(.v-pagination__item--is-active) {
    border-color: #00F5FF;
    background: rgba(0, 245, 255, 0.1);
    color: #00F5FF !important;
    box-shadow: 0 0 10px rgba(0, 245, 255, 0.2);
}
.tech-pagination :deep(.v-pagination__next), .tech-pagination :deep(.v-pagination__prev) {
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* UTILS */
.tracking-widest { letter-spacing: 0.15em; }
.tracking-wide { letter-spacing: 0.05em; }
</style>
