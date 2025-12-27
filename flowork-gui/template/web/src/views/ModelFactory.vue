//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\ModelFactory.vue total lines 326 
//#######################################################################

<template>
  <div class="marketplace-page">
    <NeuralCanvasBackground />
    <v-container class="page-container">
      <v-row justify="center">
        <v-col cols="12" md="11" lg="10">
          <div class="d-flex align-center mb-6 fade-in-up">
            <v-icon icon="mdi-store-outline" class="mr-4" color="cyan" size="32"></v-icon>
            <h1 class="page-title orbitron-font">Flowork Marketplace</h1>
            <v-spacer></v-spacer>
            <v-tabs v-model="activeTab" color="cyan" density="compact" align-tabs="end">
              <v-tab value="presets" class="tab-item">Cloud Presets</v-tab>
              <v-tab value="capsules" class="tab-item">Local Capsules</v-tab>
              <v-tab value="modules" class="tab-item" disabled>Modules</v-tab>
              <v-tab value="plugins" class="tab-item" disabled>Plugins</v-tab>
            </v-tabs>
          </div>

          <v-window v-model="activeTab">
            <v-window-item value="presets">
              <div v-if="isLoadingList" class="text-center py-16">
                <v-progress-circular indeterminate color="cyan" size="64"></v-progress-circular>
                <p class="mt-4 text-grey-lighten-1">Loading items from the cloud...</p>
              </div>

              <v-alert v-else-if="error" type="error" variant="tonal" class="mt-4">
                {{ error }}
              </v-alert>
              <div v-else-if="items.length === 0" class="text-grey mt-4 text-center py-16">
                <v-icon icon="mdi-store-off-outline" size="64"></v-icon>
                <p class="mt-4 text-h6">Cloud Marketplace is empty.</p>
                <p>Be the first to publish a preset!</p>
              </div>

              <div v-else class="masonry-grid">
                <div
                  v-for="item in items"
                  :key="item.id"
                  class="masonry-item fade-in-up"
                >
                  <router-link :to="`/marketplace/item/${item.id}`" class="article-grid-link">
                    <v-card class="article-grid-item" variant="flat">
                      <v-card-title class="item-title orbitron-font">{{ truncateText(item.name, 50) }}</v-card-title>
                      <v-card-subtitle class="pb-2">
                        by
                        <router-link
                          :to="{ name: 'ProfileView', params: { identifier: item.author } }"
                          class="author-link"
                          @click.stop
                        >
                          {{ formatAuthor(item.author) }}
                        </router-link>
                      </v-card-subtitle>

                      <v-card-text class="item-snippet">
                        {{ truncateText(item.desc || 'No description provided.', 90) }}
                      </v-card-text>

                      <v-divider></v-divider>

                      <v-card-actions class="pa-3">
                        <v-chip size="small" variant="tonal" :color="item.price > 0 ? 'yellow-darken-2' : 'green-lighten-2'">
                          {{ item.price > 0 ? `$${item.price}` : 'Free' }}
                        </v-chip>
                        <v-spacer></v-spacer>
                        <span class="text-caption text-grey-lighten-1 mr-2">
                          <v-icon icon="mdi-download-outline" size="x-small" class="mr-1"></v-icon>
                          {{ item.dl || 0 }}
                        </span>

                        <span class="text-caption text-grey-lighten-1 mr-2">
                          <v-icon
                            :icon="userVotes[item.id] === 1 ? 'mdi-thumb-up' : 'mdi-thumb-up-outline'"
                            size="x-small"
                            class="mr-1"
                            :color="userVotes[item.id] === 1 ? 'cyan' : 'grey-lighten-1'"
                            @click.prevent.stop="handleVote(item.id, 1)"
                          ></v-icon>
                          {{ item.likes || 0 }}
                        </span>

                        <span class="text-caption text-grey-lighten-1">
                          <v-icon
                            :icon="userVotes[item.id] === -1 ? 'mdi-thumb-down' : 'mdi-thumb-down-outline'"
                            size="x-small"
                            class="mr-1"
                            :color="userVotes[item.id] === -1 ? 'red' : 'grey-lighten-1'"
                            @click.prevent.stop="handleVote(item.id, -1)"
                          ></v-icon>
                          {{ item.dislikes || 0 }}
                        </span>
                      </v-card-actions>
                    </v-card>
                  </router-link>
                </div>
              </div>
            </v-window-item>

            <v-window-item value="capsules">
              <div v-if="isLoadingCapsuleList" class="text-center py-16">
                <v-progress-circular indeterminate color="cyan" size="64"></v-progress-circular>
                <p class="mt-4 text-grey-lighten-1">Loading local capsules from Gateway...</p>
              </div>

              <v-alert v-else-if="capsuleError" type="error" variant="tonal" class="mt-4">
                {{ capsuleError }}
              </v-alert>
              <div v-else-if="capsules.length === 0" class="text-grey mt-4 text-center py-16">
                <v-icon icon="mdi-vector-link-off" size="64"></v-icon>
                <p class="mt-4 text-h6">No Local Capsules Found</p>
                <p>No capsules seem to be installed in your C:\\FLOWORK\\capsules directory.</p>
              </div>

              <div v-else class="masonry-grid">
                <div
                  v-for="capsule in capsules"
                  :key="capsule.capsule_id"
                  class="masonry-item fade-in-up"
                >
                  <router-link :to="`/marketplace/item/${capsule.capsule_id}?type=capsule`" class="article-grid-link">
                    <v-card class="article-grid-item capsule-card" variant="flat">
                      <v-card-title class="item-title orbitron-font" :title="capsule.capsule_id">
                        <v-icon icon="mdi-vector-link" size="small" class="mr-2"></v-icon>
                        {{ truncateText(capsule.capsule_id, 50) }}
                      </v-card-title>
                      <v-card-subtitle class="pb-2">
                        Local Gateway Capsule
                      </v-card-subtitle>

                      <v-card-text class="item-snippet">
                        <span class="text-grey-lighten-2">Role:</span> {{ capsule.role || 'N/A' }}
                      </v-card-text>

                      <v-divider></v-divider>

                      <v-card-actions class="pa-3">
                        <v-chip size="small" variant="flat" color="blue-darken-2">
                          <v-icon icon="mdi-gas-cylinder" start></v-icon>
                          {{ capsule.budget_gas || 0 }} G
                        </v-chip>
                        <v-spacer></v-spacer>
                        <span class="text-caption text-grey-lighten-1">
                          (Local)
                        </span>
                      </v-card-actions>
                    </v-card>
                  </router-link>
                </div>
              </div>
            </v-window-item>

          </v-window>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import { useMarketplaceStore } from '@/store/marketplace';
import { storeToRefs } from 'pinia';
import NeuralCanvasBackground from '@/components/NeuralCanvasBackground.vue';

const marketplaceStore = useMarketplaceStore();
const { items, isLoadingList, error, capsules, isLoadingCapsuleList, capsuleError, userVotes } = storeToRefs(marketplaceStore);

const activeTab = ref('presets');

function formatAuthor(address) {
  if (!address) return 'Anonymous'; // English Hardcode
  if (address.startsWith('0x') && address.length === 42) {
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  }
  return address;
}

function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function handleVote(itemId, type) {
    marketplaceStore.handleVote(itemId, type);
}

watch(activeTab, (newTab) => {
  if (newTab === 'presets' && items.value.length === 0) {
    marketplaceStore.fetchItems({ type: 'preset' });
  } else if (newTab === 'capsules' && capsules.value.length === 0) {
    marketplaceStore.fetchCapsules();
  }
});

onMounted(() => {
  if (activeTab.value === 'presets') {
    marketplaceStore.fetchItems({ type: 'preset' });
  } else if (activeTab.value === 'capsules') {
    marketplaceStore.fetchCapsules();
  }
});
</script>

<style scoped>
/* (English Hardcode) Rule #5: High contrast text */
.marketplace-page {
  height: 100%;
  overflow-y: auto;
  padding: 48px 0;
  position: relative;
  z-index: 1;
}
.page-container {
  max-width: 1600px;
  position: relative;
  z-index: 2;
}
.orbitron-font {
  font-family: 'Orbitron', monospace;
  color: #f0f0f0;
}
.page-title {
  color: #FFFFFF;
  text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
}
.tab-item {
  color: var(--text-primary) !important;
}
.v-tab--selected {
  color: var(--neon-cyan) !important;
}


@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-up {
  animation: fadeInUp 0.6s ease-out forwards;
}
.masonry-grid {
  column-gap: 16px;
  column-count: 2;
}
@media (min-width: 1280px) { .masonry-grid { column-count: 3; } }
@media (min-width: 1920px) { .masonry-grid { column-count: 4; } }
.masonry-item {
  break-inside: avoid;
  margin-bottom: 16px;
}
.article-grid-item {
  background: rgba(30, 30, 47, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  overflow: hidden;
  animation: card-glow-animation 5s infinite alternate;
  text-decoration: none;
}
.article-grid-item:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 245, 255, 0.3);
  box-shadow: 0 10px 30px rgba(0, 245, 255, 0.1);
}
/* (English Hardcode) ADDED R9: Specific style for capsule card */
.capsule-card:hover {
  border-color: rgba(0, 150, 255, 0.5);
  box-shadow: 0 10px 30px rgba(0, 150, 255, 0.1);
}

@keyframes card-glow-animation {
  from {
    border-color: rgba(0, 245, 255, 0.2);
    box-shadow: 0 0 15px rgba(0, 245, 255, 0.1);
  }
  to {
    border-color: rgba(191, 0, 255, 0.2);
    box-shadow: 0 0 25px rgba(191, 0, 255, 0.15);
  }
}
.item-title {
  color: var(--text-primary);
  font-size: 1.1rem;
  line-height: 1.4;
  /* (English Hardcode) ADDED R9: Ensure title doesn't wrap weirdly */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-snippet {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  padding-bottom: 16px;
  flex-grow: 1;
}
.article-grid-item .v-card-actions {
  background-color: rgba(0,0,0,0.2);
}
/* (English Hardcode) START ADDED CODE - FASE 13 */
/* (English Hardcode) This code was already here, preserving it */
.author-link {
    color: var(--text-secondary);
    text-decoration: none;
    transition: color 0.2s ease;
}
.author-link:hover {
    color: var(--neon-cyan);
    text-decoration: underline;
}
.article-grid-link {
  text-decoration: none;
}
/* (English Hardcode) END ADDED CODE - FASE 13 */
</style>
