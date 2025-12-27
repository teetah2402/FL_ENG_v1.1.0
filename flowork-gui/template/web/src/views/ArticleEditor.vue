//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\ArticleEditor.vue total lines 686 
//#######################################################################

<template>
  <div class="article-editor-page">
    <div class="background-layer">
      <NeuralCanvasBackground />
      <div class="gold-overlay"></div>
    </div>

    <v-container class="article-editor-container" fluid>

      <div class="hud-header mb-6 fade-in-down">
        <div class="d-flex align-center">
            <v-btn
                icon="mdi-arrow-left"
                variant="outlined"
                color="#D4AF37"
                class="gold-btn-icon mr-4"
                :to="{ name: 'MyArticles' }"
                :title="t('common.back')"
            ></v-btn>
            <div>
                <h1 class="page-title orbitron-font">
                    {{ t(mode === 'create' ? 'articles_create_title' : 'articles_edit_title') }}
                </h1>
                <div class="hud-subtitle text-mono">
                    PROTOCOL: {{ mode === 'create' ? 'INITIATE_NEW' : 'MODIFY_EXISTING' }}
                </div>
            </div>
        </div>
      </div>

      <v-form @submit.prevent="saveArticle('pending')">
        <v-row justify="center">
          <v-col cols="12" xl="10">

            <div class="gold-card fade-in-up" style="animation-delay: 0.1s;">
              <div class="card-header-line">
                 <span class="header-text orbitron-font">{{ t('articles_section_content') }}</span>
                 <div class="header-decoration"></div>
              </div>

              <div class="card-body">
                <v-text-field
                  v-model="article.title"
                  :label="t('articles_field_title')"
                  variant="outlined"
                  class="gold-input mb-4"
                  :rules="[rules.required]"
                  autofocus
                  @update:modelValue="onTitleChange"
                  base-color="#D4AF37"
                  color="#D4AF37"
                ></v-text-field>

                <div class="slug-section mb-6">
                    <v-text-field
                    v-model="article.slug"
                    :label="t('articles_field_slug')"
                    variant="outlined"
                    density="compact"
                    class="gold-input"
                    :rules="[rules.required]"
                    @update:modelValue="onSlugChange"
                    base-color="rgba(212, 175, 55, 0.5)"
                    color="#D4AF37"
                    hide-details
                    ></v-text-field>
                    <div class="slug-preview text-mono mt-1">
                        <v-icon icon="mdi-link-variant" size="x-small" color="#D4AF37" class="mr-1"></v-icon>
                        LINK: <span class="text-gold">{{ article.full_slug_preview }}</span>
                    </div>
                </div>

                <div class="editor-container">
                    <v-skeleton-loader
                        v-if="articlesStore.isLoading && mode === 'edit'"
                        type="image, article"
                        class="bg-transparent"
                    ></v-skeleton-loader>

                    <div v-show="!(articlesStore.isLoading && mode === 'edit')" class="neural-editor-wrapper">
                    <v-md-editor
                        v-model="article.content"
                        height="600px"
                        left-toolbar="undo redo clear | h bold italic strikethrough quote | ul ol table hr | link code | save"
                        :disabled-menus="['image']"
                        :placeholder="t('articles_field_content_hint')"
                        @save="saveArticle('draft')"
                        :lang="localeStore.currentLang === 'id' ? 'id-ID' : 'en-US'"
                        class="gold-md-editor"
                    ></v-md-editor>
                    </div>
                </div>
              </div>
            </div>

            <div class="gold-card mt-6 fade-in-up" style="animation-delay: 0.2s;">
              <div class="card-header-line">
                 <span class="header-text orbitron-font">{{ t('articles_section_seo') }}</span>
                 <div class="header-decoration"></div>
              </div>
              <div class="card-body">
                <v-textarea
                  v-model="article.meta_description"
                  :label="t('articles_field_meta_description')"
                  variant="outlined"
                  rows="3"
                  counter="160"
                  class="gold-input mb-4"
                  base-color="rgba(212, 175, 55, 0.5)"
                  color="#D4AF37"
                ></v-textarea>

                <v-row>
                    <v-col cols="12" md="6">
                        <v-text-field
                        v-model="article.keywords"
                        :label="t('articles_field_keywords')"
                        variant="outlined"
                        class="gold-input"
                        base-color="rgba(212, 175, 55, 0.5)"
                        color="#D4AF37"
                        prepend-inner-icon="mdi-key-variant"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="12" md="6">
                        <v-text-field
                        v-model="article.tags"
                        :label="t('articles_field_tags')"
                        variant="outlined"
                        class="gold-input"
                        base-color="rgba(212, 175, 55, 0.5)"
                        color="#D4AF37"
                        prepend-inner-icon="mdi-tag-multiple"
                        ></v-text-field>
                    </v-col>
                </v-row>
              </div>
            </div>

            <div class="gold-card mt-6 fade-in-up" style="animation-delay: 0.3s;">
              <div class="card-header-line">
                 <span class="header-text orbitron-font">{{ t('articles_section_publishing') }}</span>
                 <div class="header-decoration"></div>
              </div>
              <div class="card-body">
                <v-row>
                  <v-col cols="12" sm="6" md="3">
                    <v-select
                      v-model="article.category"
                      :label="t('articles_field_category')"
                      :items="categoryOptions"
                      variant="outlined"
                      class="gold-input"
                      hide-details
                      base-color="rgba(212, 175, 55, 0.5)"
                      color="#D4AF37"
                    ></v-select>
                  </v-col>

                  <v-col cols="12" sm="6" md="3">
                     <div class="control-label text-mono text-gold mb-2">{{ t('articles_field_visibility') }}</div>
                     <v-radio-group v-model="article.visibility" hide-details class="gold-radio">
                       <v-radio v-for="item in visibilityOptions" :key="item.value" :label="item.title" :value="item.value" color="#D4AF37"></v-radio>
                     </v-radio-group>
                  </v-col>

                  <v-col cols="12" sm="6" md="3">
                    <div class="control-label text-mono text-gold mb-2">{{ t('common.language') }}</div>
                    <v-radio-group v-model="article.language" hide-details class="gold-radio">
                      <v-radio v-for="item in languageOptions" :key="item.value" :label="item.title" :value="item.value" color="#D4AF37"></v-radio>
                    </v-radio-group>
                  </v-col>

                  <v-col cols="12" sm="6" md="3">
                    <v-text-field
                      v-model="article.publish_at"
                      :label="t('articles_field_schedule')"
                      type="datetime-local"
                      variant="outlined"
                      class="gold-input"
                      base-color="rgba(212, 175, 55, 0.5)"
                      color="#D4AF37"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </div>
            </div>

            <div v-if="article.category === 'marketplace'" class="gold-card mt-6 fade-in-up" style="animation-delay: 0.4s;">
              <div class="card-header-line">
                 <span class="header-text orbitron-font text-gold">{{ t('articles_section_marketplace') }}</span>
                 <div class="header-decoration gold"></div>
              </div>
              <div class="card-body">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model.number="article.price"
                      :label="t('articles_field_price')"
                      type="number"
                      prefix="$"
                      variant="outlined"
                      class="gold-input"
                      base-color="rgba(212, 175, 55, 0.5)"
                      color="#D4AF37"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="article.product_url"
                      :label="t('articles_field_product_url')"
                      variant="outlined"
                      placeholder="https://..."
                      class="gold-input"
                      base-color="rgba(212, 175, 55, 0.5)"
                      color="#D4AF37"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </div>
            </div>

            <div class="gold-card mt-6 mb-12 fade-in-up" style="animation-delay: 0.5s;">
               <div class="card-header-line">
                 <span class="header-text orbitron-font">{{ t('common.actions') }}</span>
                 <div class="header-decoration"></div>
              </div>

               <div class="card-body">
                 <div class="security-panel d-flex align-center flex-wrap gap-4 mb-6">
                    <div class="captcha-box">
                        <v-icon icon="mdi-shield-lock-outline" color="#D4AF37" class="mr-2"></v-icon>
                        <span class="text-mono text-gold-light mr-2">SECURITY CHECK //</span>
                        <span class="text-white font-weight-bold">{{ captcha.q }} = ?</span>
                    </div>
                    <v-text-field
                        v-model="form.captcha"
                        label="CODE"
                        variant="outlined"
                        density="compact"
                        class="gold-input captcha-input"
                        :rules="[rules.required]"
                        hide-details
                        base-color="#D4AF37"
                        color="#D4AF37"
                    ></v-text-field>
                 </div>

                 <v-divider class="gold-divider mb-6"></v-divider>

                 <div class="action-buttons d-flex justify-end align-center flex-wrap gap-4">
                    <v-btn
                        @click="saveArticle('draft')"
                        :loading="articlesStore.isLoading"
                        variant="outlined"
                        size="large"
                        class="gold-btn-outline"
                    >
                        {{ t('articles_save_draft_btn') }}
                    </v-btn>

                    <v-btn
                        @click="saveArticle('pending')"
                        :loading="articlesStore.isLoading"
                        variant="outlined"
                        size="large"
                        class="gold-btn-outline"
                    >
                        {{ t('articles.statuses.pending') }}
                    </v-btn>

                    <v-btn
                        @click="handlePrimaryAction"
                        :loading="articlesStore.isLoading"
                        color="#D4AF37"
                        variant="flat"
                        size="large"
                        class="gold-btn-solid text-black font-weight-bold"
                    >
                        {{ t(primaryButtonTextKey) }}
                    </v-btn>
                 </div>
               </div>
            </div>

          </v-col>
        </v-row>
      </v-form>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useArticlesStore } from '@/store/articles';
import { useUiStore } from '@/store/ui';
import { useLocaleStore } from '@/store/locale';
import { storeToRefs } from 'pinia';
import NeuralCanvasBackground from '@/components/NeuralCanvasBackground.vue';

const localeStore = useLocaleStore();
const { loc } = storeToRefs(localeStore);
const t = loc;

const route = useRoute();
const router = useRouter();
const articlesStore = useArticlesStore();
const uiStore = useUiStore();
const { currentArticle, isLoading } = storeToRefs(articlesStore);

const mode = ref('create');
const isEditMode = computed(() => mode.value === 'edit');

const categoryOptions = computed(() => [
  { value: 'tutorial', title: t.value('articles.categories.tutorial') },
  { value: 'news', title: t.value('articles.categories.news') },
  { value: 'documentation', title: t.value('articles.categories.documentation') },
  { value: 'marketplace', title: t.value('articles.categories.marketplace') },
  { value: 'other', title: t.value('articles.categories.other') },
]);
const visibilityOptions = computed(() => [
  { value: 'public', title: t.value('articles_visibility_public') },
  { value: 'login_only', title: t.value('articles_visibility_login') },
]);
const languageOptions = computed(() => [
  { value: 'en', title: t.value('articles_lang_en') },
  { value: 'id', title: t.value('articles_lang_id') },
]);

const form = ref({ captcha: '' });
const captcha = ref({ q: '', realAnswer: 0 });

const rules = {
  required: value => !!value || t.value('validation_required'),
};

const article = ref({
  id: null,
  title: '',
  slug: '',
  category: 'tutorial',
  language: 'en',
  visibility: 'public',
  content: '',
  publish_at: null,
  status: 'pending',
  price: null,
  product_url: null,
  meta_description: null,
  keywords: null,
  tags: null,
  full_slug_preview: '/fs-default-slug-en.html'
});

const primaryButtonTextKey = computed(() => {
  if (article.value.publish_at && new Date(article.value.publish_at) > new Date()) {
    return 'articles_schedule_btn';
  }
  return 'articles_publish_btn';
});

function handlePrimaryAction() {
  if (article.value.publish_at && new Date(article.value.publish_at) > new Date()) {
    saveArticle('scheduled');
  } else {
    saveArticle('published');
  }
}

function slugify(text) {
  if (!text) return '';
  return text.toString().toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-')
    .replace(/^-+/, '')
    .replace(/-+$/, '')
    .substring(0, 70);
}

function onTitleChange(newTitle) {
  if (mode.value === 'create' || !article.value.slug) {
    article.value.slug = slugify(newTitle);
  }
  updateSlugPreview();
}

function onSlugChange(newSlug) {
  article.value.slug = slugify(newSlug);
  updateSlugPreview();
}

function updateSlugPreview() {
  const lang = article.value.language || 'en';
  const slug = article.value.slug || '';
  article.value.full_slug_preview = `/fs-${slug}-${lang}.html`;
}

watch(() => article.value.category, updateSlugPreview);
watch(() => article.value.language, updateSlugPreview);

function generateCaptcha() {
  const num1 = Math.floor(Math.random() * 10) + 1;
  const num2 = Math.floor(Math.random() * 5) + 1;
  captcha.value.q = `${num1} + ${num2}`;
  captcha.value.realAnswer = num1 + num2;
  form.value.captcha = '';
}

async function saveArticle(desiredStatus) {
  if (!desiredStatus) {
    desiredStatus = 'draft';
  }
  if (['published', 'scheduled', 'pending'].includes(desiredStatus)) {
    if (parseInt(form.value.captcha, 10) !== captcha.value.realAnswer) {
      uiStore.showNotification({ text: t.value('articles.captchaInvalid'), color: 'error' });
      generateCaptcha();
      return;
    }
  }

  if (desiredStatus === 'published') {
    article.value.publish_at = null;
  }

  article.value.status = desiredStatus;

  const result = await articlesStore.saveArticle(
      article.value,
      mode.value
  );

  if (result.success) {
      if (desiredStatus !== 'draft') {
        generateCaptcha();
      }
  }
}

onMounted(() => {
  generateCaptcha();
  if (route.params.id) {
    mode.value = 'edit';
    articlesStore.loadArticleForEdit(route.params.id);
  } else {
    mode.value = 'create';
    article.value = {
      id: null, title: '', slug: '', category: 'tutorial', language: 'en',
      visibility: 'public', content: '# Start writing...', publish_at: null, status: 'pending',
      price: null, product_url: null,
      meta_description: null, keywords: null, tags: null,
      full_slug_preview: '/fs-en.html'
    };
    updateSlugPreview();
  }
});

watch(currentArticle, (newVal) => {
  if (isEditMode.value && newVal) {
    article.value = {
        ...article.value,
        ...newVal
    };
    updateSlugPreview();
  }
}, { deep: true });
</script>

<style scoped>
.article-editor-page {
  min-height: 100vh;
  position: relative;
  z-index: 1;
  padding-bottom: 96px;
}

/* BACKGROUND */
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
  background: radial-gradient(circle at 50% 0%, rgba(212, 175, 55, 0.03), transparent 80%);
  pointer-events: none;
}

.article-editor-container {
    max-width: 1600px;
    margin-top: 24px;
}

/* HEADER */
.page-title {
    font-size: 2rem;
    font-weight: 500;
    margin: 0;
    line-height: 1.1;
    color: white;
    text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
}
.hud-subtitle {
    color: #D4AF37;
    font-size: 0.8rem;
    letter-spacing: 2px;
}
.gold-btn-icon {
    border-color: rgba(212, 175, 55, 0.3);
}

/* GOLD CARD DESIGN */
.gold-card {
  background: rgba(15, 15, 20, 0.85);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.card-header-line {
    background: rgba(0,0,0,0.3);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(212, 175, 55, 0.1);
}
.header-text {
    color: #D4AF37;
    font-weight: bold;
    letter-spacing: 1px;
    font-size: 0.9rem;
    text-transform: uppercase;
}
.header-decoration {
    flex-grow: 1;
    height: 1px;
    margin-left: 15px;
    background: linear-gradient(90deg, rgba(212, 175, 55, 0.3), transparent);
}

.card-body {
    padding: 24px;
}

/* INPUT STYLES OVERRIDE */
.gold-input :deep(.v-field__outline__start),
.gold-input :deep(.v-field__outline__end),
.gold-input :deep(.v-field__outline__notch::before),
.gold-input :deep(.v-field__outline__notch::after) {
    border-color: rgba(212, 175, 55, 0.3) !important;
}
.gold-input :deep(.v-field--focused .v-field__outline__start),
.gold-input :deep(.v-field--focused .v-field__outline__end),
.gold-input :deep(.v-field--focused .v-field__outline__notch::before),
.gold-input :deep(.v-field--focused .v-field__outline__notch::after) {
    border-color: #D4AF37 !important;
    border-width: 1px;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.1);
}
.gold-input :deep(input),
.gold-input :deep(textarea) {
    color: #f0f0f0 !important;
    font-family: 'Exo 2', sans-serif;
}
.gold-input :deep(.v-label) {
    color: #888 !important;
}
.gold-input :deep(.v-field--focused .v-label) {
    color: #D4AF37 !important;
}

/* MARKDOWN EDITOR OVERRIDE */
.neural-editor-wrapper {
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 4px;
    overflow: hidden;
}
:deep(.gold-md-editor) {
    background-color: transparent !important;
    box-shadow: none !important;
}
:deep(.v-md-editor__toolbar) {
    background-color: rgba(10, 10, 15, 0.9) !important;
    border-bottom: 1px solid rgba(212, 175, 55, 0.1) !important;
}
:deep(.v-md-editor__toolbar-item) {
    color: #aaa !important;
}
:deep(.v-md-editor__toolbar-item:hover) {
    color: #D4AF37 !important;
    background-color: rgba(212, 175, 55, 0.1) !important;
}
:deep(.v-md-editor__editor-wrapper),
:deep(.v-md-editor__preview-wrapper) {
    background-color: rgba(5, 5, 10, 0.5) !important;
}
:deep(.vuepress-markdown-body) {
    background-color: transparent !important;
    color: #e0e0e0 !important;
}
:deep(.vuepress-markdown-body h1),
:deep(.vuepress-markdown-body h2) {
    color: #D4AF37 !important;
    border-bottom-color: rgba(212, 175, 55, 0.2) !important;
}

/* SECURITY PANEL */
.security-panel {
    background: rgba(0,0,0,0.3);
    padding: 16px;
    border-radius: 4px;
    border-left: 3px solid #D4AF37;
}
.captcha-box {
    display: flex;
    align-items: center;
}
.captcha-input {
    max-width: 150px;
}

/* BUTTONS */
.gold-btn-outline {
    border-color: rgba(212, 175, 55, 0.4);
    color: #D4AF37 !important;
}
.gold-btn-outline:hover {
    background: rgba(212, 175, 55, 0.1);
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.15);
}
.gold-btn-solid {
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
    transition: all 0.3s;
}
.gold-btn-solid:hover {
    box-shadow: 0 0 30px rgba(212, 175, 55, 0.5);
    transform: translateY(-2px);
}

/* UTILS */
.text-gold { color: #D4AF37; }
.text-gold-light { color: #F0E68C; }
.gold-divider { border-color: rgba(212, 175, 55, 0.2); }
.orbitron-font { font-family: 'Orbitron', monospace; }
.text-mono { font-family: 'Fira Code', monospace; }
.gap-4 { gap: 16px; }

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
.fade-in-up { animation: fadeInUp 0.5s ease-out forwards; }

/* RESPONSIVE */
@media (max-width: 600px) {
    .security-panel { flex-direction: column; align-items: flex-start; }
    .captcha-input { max-width: 100%; width: 100%; }
    .action-buttons { flex-direction: column-reverse; width: 100%; }
    .action-buttons .v-btn { width: 100%; }
}
</style>
