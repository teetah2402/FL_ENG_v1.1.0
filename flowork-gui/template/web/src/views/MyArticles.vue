//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\MyArticles.vue total lines 586 
//#######################################################################

<template>
  <div class="my-articles-page">
    <div class="background-layer">
      <NeuralCanvasBackground />
      <div class="gold-overlay"></div>
    </div>

    <v-container class="page-container" fluid>
      <v-row justify="center">
        <v-col cols="12" xl="10">

          <div class="hud-header mb-8 fade-in-down">
            <div class="hud-title-section">
              <div class="icon-box-gold mr-4">
                <v-icon icon="mdi-notebook-edit-outline" color="#D4AF37" size="32"></v-icon>
              </div>
              <div>
                <h1 class="page-title orbitron-font">{{ t('articles_my_content_title') }}</h1>
                <div class="hud-subtitle text-mono">LOCAL KNOWLEDGE REPOSITORY</div>
              </div>
            </div>

            <div class="hud-controls">
                <v-btn
                  color="#D4AF37"
                  variant="outlined"
                  class="gold-btn"
                  :to="{ name: 'ArticleEditorNew' }"
                  prepend-icon="mdi-plus"
                >
                  {{ t('articles_new_article_btn') }}
                </v-btn>
            </div>
          </div>

          <div v-if="isLoading" class="scanner-loader py-16">
            <div class="scanner-line"></div>
            <v-progress-circular indeterminate color="#D4AF37" size="64" width="2"></v-progress-circular>
            <p class="mt-6 text-mono text-gold blink-text">SCANNING LOCAL REPOSITORY...</p>
          </div>

          <v-alert v-else-if="error" type="error" variant="outlined" color="red" class="gold-alert mt-4">
             <div class="text-mono">DATA CORRUPTION DETECTED: {{ error.message || error }}</div>
          </v-alert>

          <div v-else-if="myArticles.length === 0" class="empty-state-container fade-in-up">

            <div class="text-center py-12 mb-12 empty-box">
                <v-icon icon="mdi-database-off-outline" size="80" color="#333" class="mb-4"></v-icon>
                <h2 class="text-h5 text-gold orbitron-font mb-2">REPOSITORY EMPTY</h2>
                <p class="text-grey-darken-1 mb-8 text-mono">NO KNOWLEDGE PROTOCOLS FOUND.</p>

                <v-btn
                    color="#D4AF37"
                    variant="flat"
                    size="large"
                    :to="{ name: 'ArticleEditorNew' }"
                    class="gold-glow-btn text-black font-weight-bold"
                    prepend-icon="mdi-console-line"
                >
                  INITIALIZE FIRST PROTOCOL
                </v-btn>
            </div>

            <div class="global-feed-section">
                <div class="d-flex align-center mb-6">
                    <v-icon icon="mdi-access-point-network" color="#D4AF37" class="mr-3"></v-icon>
                    <h3 class="text-h6 text-gold orbitron-font">INCOMING GLOBAL SIGNALS</h3>
                    <div class="gold-divider-h ml-4"></div>
                </div>

                <div v-if="loadingPublic" class="text-center py-8">
                    <v-progress-circular indeterminate color="#D4AF37" size="32"></v-progress-circular>
                </div>

                <div v-else class="gold-grid-layout">
                    <div
                      v-for="pubItem in publicArticles"
                      :key="pubItem.id"
                      class="gold-grid-item fade-in-up"
                    >
                      <a :href="getPublicUrl(pubItem)" target="_blank" class="no-decoration">
                          <div class="gold-card global-item">
                            <div class="global-tag text-mono">GLOBAL</div>

                            <div class="card-header">
                                <h3 class="card-title orbitron-font">{{ pubItem.title }}</h3>
                                <div class="text-caption text-gold-light mt-1">
                                    {{ t(`articles.categories.${pubItem.category.toLowerCase()}`) || pubItem.category }}
                                </div>
                            </div>

                            <div class="card-body">
                              <p class="card-desc">
                                {{ pubItem.snippet || 'No preview data available from the neural link.' }}
                              </p>
                            </div>

                            <div class="gold-divider"></div>

                            <div class="card-footer d-flex justify-space-between align-center">
                                <div class="d-flex align-center text-grey">
                                    <v-icon icon="mdi-account-circle-outline" size="small" class="mr-2"></v-icon>
                                    <span class="text-caption text-mono">{{ pubItem.author_name || 'UNKNOWN' }}</span>
                                </div>
                                <span class="text-caption text-grey-darken-1 text-mono">{{ new Date(pubItem.created_at).toLocaleDateString() }}</span>
                            </div>
                          </div>
                      </a>
                    </div>
                </div>
            </div>
          </div>

          <div v-else class="gold-grid-layout">
            <div
              v-for="item in myArticles"
              :key="item.id"
              class="gold-grid-item fade-in-up"
            >
              <div class="gold-card">
                <div class="card-header">
                    <h3 class="card-title orbitron-font">{{ item.title }}</h3>
                    <div class="d-flex justify-space-between align-center mt-2">
                        <span class="text-caption text-gold-light">
                            {{ t(`articles.categories.${item.category.toLowerCase()}`) || item.category }}
                        </span>

                        <div class="status-indicator" :class="getDisplayStatus(item).colorClass">
                            <span class="status-dot"></span>
                            {{ getDisplayStatus(item).text }}
                        </div>
                    </div>
                </div>

                <div class="card-body">
                  <div class="d-flex align-center mt-2">
                    <v-icon icon="mdi-clock-outline" size="x-small" color="grey" class="mr-2"></v-icon>
                    <span class="text-caption text-grey-darken-1 text-mono">UPDATED: {{ new Date(item.updated_at).toLocaleDateString() }}</span>
                  </div>
                </div>

                <div class="gold-divider"></div>

                <div class="card-footer actions-footer">
                  <v-tooltip :text="t('articles.view')" location="top">
                    <template v-slot:activator="{ props: tooltipProps }">
                      <v-btn
                        v-bind="tooltipProps"
                        icon="mdi-eye"
                        variant="text"
                        density="compact"
                        color="grey"
                        class="action-btn-hover"
                        :href="getPublicUrl(item)"
                        target="_blank"
                      ></v-btn>
                    </template>
                  </v-tooltip>

                  <v-spacer></v-spacer>

                  <v-tooltip :text="t('articles.edit')" location="top">
                    <template v-slot:activator="{ props: tooltipProps }">
                      <v-btn
                        v-bind="tooltipProps"
                        icon="mdi-pencil"
                        variant="text"
                        density="compact"
                        color="#D4AF37"
                        class="action-btn-hover"
                        :to="`/my-articles/edit/${item.id}`"
                      ></v-btn>
                    </template>
                  </v-tooltip>

                  <v-tooltip :text="t('articles.delete')" location="top">
                    <template v-slot:activator="{ props: tooltipProps }">
                      <v-btn
                        v-bind="tooltipProps"
                        icon="mdi-delete"
                        variant="text"
                        density="compact"
                        color="red-darken-2"
                        class="action-btn-hover"
                        @click.stop="handleDelete(item.id)"
                      ></v-btn>
                    </template>
                  </v-tooltip>
                </div>
              </div>
            </div>
          </div>

        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useArticlesStore } from '@/store/articles';
import { useLocaleStore } from '@/store/locale';
import { storeToRefs } from 'pinia';
import NeuralCanvasBackground from '@/components/NeuralCanvasBackground.vue';

const articleStore = useArticlesStore();
const localeStore = useLocaleStore();
const { myArticles, isLoading, error } = storeToRefs(articleStore);
const t = localeStore.loc;

const publicArticles = ref([]);
const loadingPublic = ref(false);

async function fetchPublicInspiration() {
    loadingPublic.value = true;
    try {
        const response = await fetch('/api/v1/content/articles/list?mode=all&limit=6');
        if (response.ok) {
            const data = await response.json();
            publicArticles.value = Array.isArray(data) ? data : (data.data || []);
        }
    } catch (e) {
        console.warn("Signal lost:", e);
    } finally {
        loadingPublic.value = false;
    }
}

onMounted(() => {
  const initData = async () => {
    await articleStore.fetchMyArticles();
    if (myArticles.value.length === 0) {
        await fetchPublicInspiration();
    }
  };

  if (typeof t !== 'function') {
    localeStore.fetchDictionary().then(() => {
        initData();
    });
  } else {
    initData();
  }
});

function getDisplayStatus(item) {
    let statusKey = item.status.toLowerCase();
    let colorClass = 'status-grey'; // Default

    if (statusKey === 'pending' && item.publish_at && new Date(item.publish_at) > new Date()) {
        statusKey = 'scheduled';
    }

    switch (statusKey) {
        case 'published': colorClass = 'status-green'; break;
        case 'pending': colorClass = 'status-orange'; break;
        case 'scheduled': colorClass = 'status-blue'; break;
        case 'draft': colorClass = 'status-gold'; break; // Gold for draft
        case 'hidden': colorClass = 'status-grey'; break;
    }

    const text = t(`articles.statuses.${statusKey}`) || item.status;
    return { text, colorClass };
}

async function handleDelete(articleId) {
    const articleToDelete = myArticles.value.find(art => art.id === articleId);
    const title = articleToDelete ? articleToDelete.title : 'this article';
    const confirmMessage = t('articles_delete_confirm', { title: title });
    if (confirm(confirmMessage)) {
        await articleStore.deleteArticle(articleId);
    }
}

function getPublicUrl(item) {
  const lang = item.language || 'en';
  return `/p-${item.slug}-${lang}.html`;
}
</script>

<style scoped>
.my-articles-page {
  min-height: 100vh;
  position: relative;
  z-index: 1;
  padding-bottom: 48px;
}

/* BACKGROUND LAYER */
.background-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  background-color: #050505;
}

.gold-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 50% 0%, rgba(212, 175, 55, 0.05), transparent 70%);
  pointer-events: none;
}

.page-container {
  max-width: 1600px;
  margin-top: 24px;
}

/* FONTS */
.orbitron-font {
  font-family: 'Orbitron', monospace;
  letter-spacing: 2px;
  color: #f0f0f0;
}
.text-mono {
  font-family: 'Fira Code', monospace;
}

/* HUD HEADER */
.hud-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(212, 175, 55, 0.2);
  padding: 0 0 20px 0;
  margin-bottom: 32px;
  opacity: 0;
}

.hud-title-section {
  display: flex;
  align-items: center;
}

.icon-box-gold {
  border: 1px solid rgba(212, 175, 55, 0.3);
  padding: 8px;
  border-radius: 4px;
  background: rgba(212, 175, 55, 0.05);
  box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
}

.page-title {
  font-size: 1.8rem;
  font-weight: 500;
  margin: 0;
  line-height: 1;
  text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
}

.hud-subtitle {
  color: #888;
  font-size: 0.75rem;
  margin-top: 6px;
  letter-spacing: 1px;
}

/* GOLD BUTTONS */
.gold-btn {
  border-color: rgba(212, 175, 55, 0.5);
  color: #D4AF37;
  letter-spacing: 1px;
  transition: all 0.3s;
}
.gold-btn:hover {
  background: rgba(212, 175, 55, 0.1);
  box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);
}

.gold-glow-btn {
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
    transition: all 0.3s ease;
}
.gold-glow-btn:hover {
    box-shadow: 0 0 30px rgba(212, 175, 55, 0.6);
    transform: translateY(-2px);
}

/* GRID LAYOUT */
.gold-grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

/* GOLD CARD DESIGN */
.gold-card {
  background: rgba(15, 15, 20, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
}

.gold-card:hover {
  transform: translateY(-4px);
  border-color: rgba(212, 175, 55, 0.4);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

/* Hover line effect top */
.gold-card:hover::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #D4AF37, transparent);
  box-shadow: 0 0 10px #D4AF37;
}

.card-header {
  padding: 20px 20px 10px 20px;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e0e0e0;
  letter-spacing: 0.5px;
  line-height: 1.4;
}

.card-body {
  padding: 0 20px 20px 20px;
  flex: 1;
}

.card-desc {
  font-size: 0.85rem;
  color: #999;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.gold-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
  width: 100%;
}

.card-footer {
  padding: 12px 20px;
  background: rgba(0, 0, 0, 0.2);
  font-size: 0.8rem;
}

/* GLOBAL FEED SPECIFIC */
.gold-card.global-item {
    border: 1px dashed rgba(255, 255, 255, 0.1);
}
.gold-card.global-item:hover {
    border-style: solid;
    border-color: rgba(212, 175, 55, 0.6);
}

.global-tag {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(212, 175, 55, 0.1);
    border: 1px solid rgba(212, 175, 55, 0.3);
    color: #D4AF37;
    font-size: 0.6rem;
    padding: 2px 6px;
    border-radius: 2px;
}

.empty-box {
    border: 1px dashed rgba(255,255,255,0.1);
    border-radius: 8px;
    background: rgba(255,255,255,0.02);
}

.gold-divider-h {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(212, 175, 55, 0.3), transparent);
}

/* UTILS */
.text-gold { color: #D4AF37; }
.text-gold-light { color: #F0E68C; }
.blink-text { animation: blink 2s infinite; }
.no-decoration { text-decoration: none; color: inherit; }

/* STATUS INDICATORS */
.status-indicator {
    font-size: 0.7rem;
    font-family: 'Fira Code', monospace;
    display: flex;
    align-items: center;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(0,0,0,0.3);
    border: 1px solid transparent;
}
.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 6px;
    background: currentColor;
}

.status-green { color: #4CAF50; border-color: rgba(76, 175, 80, 0.2); }
.status-orange { color: #FF9800; border-color: rgba(255, 152, 0, 0.2); }
.status-blue { color: #2196F3; border-color: rgba(33, 150, 243, 0.2); }
.status-gold { color: #D4AF37; border-color: rgba(212, 175, 55, 0.2); }
.status-grey { color: #9E9E9E; border-color: rgba(158, 158, 158, 0.2); }

.action-btn-hover:hover {
    color: #fff !important;
}

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* ANIMATIONS */
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-down { animation: fadeInDown 0.5s ease-out forwards; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-up { animation: fadeInUp 0.4s ease-out forwards; }

.scanner-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
.scanner-line {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 600px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #D4AF37, transparent);
  box-shadow: 0 0 10px #D4AF37;
  animation: scanVertical 3s infinite ease-in-out;
}
@keyframes scanVertical {
  0% { top: 10%; opacity: 0; }
  50% { opacity: 1; }
  100% { top: 90%; opacity: 0; }
}

/* RESPONSIVE */
@media (max-width: 600px) {
  .hud-header { flex-direction: column; align-items: flex-start; }
  .hud-controls { width: 100%; margin-top: 16px; display: flex; justify-content: flex-start; }
  .gold-grid-layout { grid-template-columns: 1fr; }
}
</style>
