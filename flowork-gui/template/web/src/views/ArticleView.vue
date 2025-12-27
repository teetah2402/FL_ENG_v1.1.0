//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\ArticleView.vue total lines 298 
//#######################################################################

<template>
  <v-main>
    <div class="legal-page article-view-page">
      <DigitalFingerprintBackground />

      <v-container class="page-content-container">
        <v-row justify="center">
          <v-col cols="12" md="8">
            <v-card v-if="isLoading" class="legal-card" :loading="isLoading">
              <v-card-text class="text-center pa-12">
                <v-progress-circular indeterminate color="cyan" size="64"></v-progress-circular>
                <p class="mt-4 text-grey-lighten-1">Loading article...</p>
              </v-card-text>
            </v-card>

            <v-card v-else-if="error" class="legal-card">
              <v-card-text class="text-center pa-12">
                <v-icon icon="mdi-alert-circle-outline" size="64" color="error"></v-icon>
                <h2 class="mt-4 orbitron-font text-error">Article Not Found</h2>
                <p class="mt-2 text-grey-lighten-1">{{ error }}</p>
              </v-card-text>
            </v-card>

            <v-card v-else-if="article" class="article-card-content">
              <v-card-title class="pa-0">
                <h1 id="article-title" class="orbitron-font">{{ article.title }}</h1>
              </v-card-title>

              <div class="article-meta">
                <span>By:
                  <router-link :to="{ name: 'ProfileView', params: { identifier: article.author_username } }" class="article-link">
                    <strong id="article-author">{{ displayAuthorName }}</strong>
                  </router-link>
                  </span>
                <span>Category:
                  <router-link :to="{ name: 'CategoryView', params: { category_slug: article.category } }" class="article-link">
                    <strong id="article-category">{{ article.category }}</strong>
                  </router-link>
                  </span>
              </div>

              <div id="article-content" v-html="renderedContent"></div>

              <v-btn
                v-if="article.category === 'marketplace' && article.product_url"
                :href="article.product_url"
                target="_blank"
                rel="noopener noreferrer"
                color="cyan"
                class="buy-now-button"
                prepend-icon="mdi-cart-outline"
              >
                Get This Item
              </v-btn>

              <div class="cta-card-wrapper">
                <div class="cta-card">
                  <h3 class="cta-title orbitron-font">Start Building Your Future</h3>
                  <p class="cta-text">Your identity, your data, your engine. Take back control of your automation.</p>
                  <div class="cta-actions">
                    <v-btn
                      href="https://download.flowork.cloud/"
                      target="_blank"
                      class="cta-btn download"
                      prepend-icon="mdi-download-outline"
                    >
                      Download Engine
                    </v-btn>
                    <v-btn
                      href="https://docs.flowork.cloud/"
                      target="_blank"
                      class="cta-btn docs"
                      prepend-icon="mdi-book-open-page-variant-outline"
                    >
                      View Docs
                    </v-btn>
                    <v-btn
                      :to="{ name: 'Register' }"
                      class="cta-btn register"
                      prepend-icon="mdi-account-plus-outline"
                    >
                      Create Identity
                    </v-btn>
                  </div>
                </div>
              </div>

              <ArticleComments
                v-if="article && article.id && article.slug"
                :article-id="article.id"
                :article-slug="article.slug"
                :article-author-id="article.author_id"
                class="mt-8"
              />

            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <ArticleSidebar
              v-if="article"
              :category="article.category"
              :tags="article.tags"
              :current-slug="article.slug"
              :current-lang="article.language"
              :current-article-id="article.id"
            />
          </v-col>

        </v-row>
      </v-container>
    </div>
  </v-main>
  <LanderFooter />
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { marked } from 'marked';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import { apiGetPublicArticle } from '@/api';
import { useUiStore } from '@/store/ui';
import LanderFooter from '@/components/LanderFooter.vue';
import ArticleComments from '@/components/ArticleComments.vue';
import ArticleSidebar from '@/components/ArticleSidebar.vue';
import DigitalFingerprintBackground from '@/components/DigitalFingerprintBackground.vue';

const route = useRoute();
const uiStore = useUiStore();
const article = ref(null);
const isLoading = ref(true);
const error = ref(null);

function updateSEOTags(articleData) {
  document.title = `${articleData.title} | Flowork`;
  let metaDesc = document.querySelector('meta[name="description"]');
  if (!metaDesc) {
    metaDesc = document.createElement('meta');
    metaDesc.setAttribute('name', 'description');
    document.head.appendChild(metaDesc);
  }
  metaDesc.setAttribute('content', articleData.meta_description || articleData.title);
  if (articleData.keywords) {
    let metaKeywords = document.querySelector('meta[name="keywords"]');
    if (!metaKeywords) {
        metaKeywords = document.createElement('meta');
        metaKeywords.setAttribute('name', 'keywords');
        document.head.appendChild(metaKeywords);
    }
    metaKeywords.setAttribute('content', articleData.keywords);
  }
}

function updateStructuredData(articleData) {
  const oldScript = document.getElementById('article-structured-data');
  if (oldScript) {
    oldScript.remove();
  }
  const lang = articleData.language || 'en';
  const fullUrl = `https://flowork.cloud/p-${articleData.slug}-${lang}.html`;
  const schema = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": fullUrl
    },
    "headline": articleData.title,
    "description": articleData.meta_description || articleData.title,
    "author": {
      "@type": "Person",
      "name": articleData.author_username || "Flowork Team"
    },
    "publisher": {
      "@type": "Organization",
      "name": "Flowork",
      "logo": {
        "@type": "ImageObject",
        "url": "https://flowork.cloud/favicon.svg"
      }
    },
    "datePublished": new Date(articleData.publish_at || articleData.created_at).toISOString(),
    "dateModified": new Date(articleData.updated_at).toISOString()
  };
  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.id = 'article-structured-data';
  script.text = JSON.stringify(schema);
  document.head.appendChild(script);
}


async function fetchArticle() {
  isLoading.value = true;
  error.value = null;
  const slug = route.params.slug;
  const lang = route.params.lang;
  if (!slug || !lang) {
      error.value = "Invalid URL structure.";
      isLoading.value = false;
      return;
  }
  const result = await apiGetPublicArticle(slug, lang);
  if (result.error) {
    error.value = result.error;
    document.title = "Article Not Found | Flowork";
  } else {
    article.value = result;
    updateSEOTags(result);
    updateStructuredData(result);
  }
  isLoading.value = false;
}
const renderedContent = computed(() => {
  if (article.value && article.value.content) {
    const html = marked.parse(article.value.content);
    nextTick(() => {
        Prism.highlightAll();
    });
    return html;
  }
  return '';
});
const displayAuthorName = computed(() => {
  const username = article.value?.author_username;
  if (!username) {
    return 'Flowork Team';
  }
  return username;
});

onMounted(() => {
  fetchArticle();
});

onUnmounted(() => {
});

watch(() => route.params, fetchArticle);
</script>

<style scoped>
/* (English Hardcode) Rule #5: High contrast text */
.article-view-page { position: relative; z-index: 1; }
.page-content-container { position: relative; z-index: 2; }
.legal-page { padding: 120px 0; background-color: var(--bg-dark); min-height: 100vh; }
.article-card-content { background: var(--bg-panel-glass); backdrop-filter: blur(10px); border: 1px solid var(--border-glow-soft); padding: 24px 32px; animation: card-border-glow 4s infinite alternate; }
@keyframes card-border-glow { from { border-color: var(--border-glow-soft); box-shadow: 0 0 15px rgba(0, 245, 255, 0.1); } to { border-color: var(--border-glow-purple-soft); box-shadow: 0 0 30px rgba(191, 0, 255, 0.15); } }
.orbitron-font { font-family: 'Orbitron', monospace; }
.article-view-page { padding-top: 80px; }
#article-title { font-family: 'Orbitron', monospace; color: var(--text-primary); text-shadow: 0 0 10px var(--neon-cyan); margin-bottom: 10px; font-size: 2.5rem; line-height: 1.2; white-space: normal; word-wrap: break-word; }
.article-meta { color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 30px; border-bottom: 1px solid var(--border-glow-soft); padding-bottom: 15px; }
.article-meta span { margin-right: 15px; }
.article-meta strong { color: var(--neon-cyan); }
.article-link { color: inherit; text-decoration: none; }
.article-link:hover strong { color: var(--neon-green); text-decoration: underline; }
.buy-now-button { display: inline-block; background-color: var(--neon-cyan); color: #000 !important; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold; font-family: 'Orbitron', monospace; margin-bottom: 20px; transition: background-color 0.3s ease, transform 0.2s ease; }
.buy-now-button:hover { background-color: var(--neon-green); transform: translateY(-2px); text-decoration: none; }
#comments-app { margin-top: 40px; }

@property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
.cta-card-wrapper { margin-top: 48px; padding-top: 32px; border-top: 1px solid var(--border-glow-soft); }
.cta-card { position: relative; background-color: var(--bg-panel); border-radius: 12px; padding: 32px; text-align: center; overflow: hidden; border: 2px solid transparent; background-clip: padding-box, border-box; background-origin: padding-box, border-box; background-image: linear-gradient(var(--bg-panel), var(--bg-panel)), conic-gradient(from var(--angle), transparent 25%, var(--neon-green), var(--neon-purple), transparent 75%); animation: border-chase 4s linear infinite; }
@keyframes border-chase { to { --angle: 360deg; } }
.cta-title { color: var(--text-primary); font-size: 1.5rem; margin-bottom: 8px; }
.cta-text { color: var(--text-secondary); max-width: 450px; margin: 0 auto 24px auto; }
.cta-actions { display: flex; justify-content: center; gap: 16px; flex-wrap: wrap; }
.cta-btn { font-weight: bold; border-radius: 8px; transition: all 0.3s ease; }
.cta-btn.download { background-color: var(--neon-orange); color: #000 !important; }
.cta-btn.download:hover { background-color: #f57c00; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(255, 152, 0, 0.3); }
.cta-btn.docs { background-color: transparent; border: 1px solid var(--neon-cyan); color: var(--neon-cyan) !important; }
.cta-btn.docs:hover { background-color: rgba(0, 245, 255, 0.1); transform: translateY(-2px); }
.cta-btn.register { background-color: var(--neon-cyan); color: #000 !important; }
.cta-btn.register:hover { background-color: var(--neon-green); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 245, 255, 0.3); }
</style>

<style>
/* (English Hardcode) Rule #5: High contrast text */
#article-content { line-height: 1.7; color: var(--text-primary); }
#article-content h2, #article-content h3, #article-content h4 { font-family: 'Orbitron', monospace; color: var(--text-primary); margin-top: 1.8em; margin-bottom: 0.8em; border-bottom: 1px solid var(--border-glow-soft); padding-bottom: 0.3em; }
#article-content h2 { font-size: 1.8rem; }
#article-content h3 { font-size: 1.5rem; }
#article-content a { color: var(--neon-green); text-decoration: none; }
#article-content a:hover { text-decoration: underline; }
#article-content code { background-color: rgba(0, 0, 0, 0.3); padding: 0.2em 0.4em; border-radius: 3px; font-family: monospace; color: #ffeb3b; font-size: 0.9em; }
#article-content pre { background-color: rgba(0, 0, 0, 0.2) !important; padding: 15px; border-radius: 5px; overflow-x: auto; border: 1px solid var(--border-glow-soft); }
#article-content pre code { background-color: transparent !important; padding: 0; color: var(--text-primary) !important; }
#article-content blockquote { border-left: 4px solid var(--neon-cyan); margin-left: 0; padding-left: 15px; color: var(--text-secondary); font-style: italic; }
#article-content img { max-width: 100%; height: auto; border-radius: 4px; margin: 15px 0; }
</style>
