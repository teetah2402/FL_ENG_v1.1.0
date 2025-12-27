//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\ArticleListView.vue total lines 410 
//#######################################################################

<template>
  <v-main>
    <div class="legal-page article-list-page">
      <canvas ref="canvasEl" class="neural-canvas"></canvas>

      <v-container class="page-content-container">
        <v-row justify="center">
          <v-col cols="12" md="10">
            <h1 class="headline text-center orbitron-font mb-8">
              {{ pageTitle }}
            </h1>

            <v-progress-circular v-if="isLoading" indeterminate color="cyan" class="d-block mx-auto"></v-progress-circular>
            <v-alert v-else-if="error" type="error" variant="tonal" class="mt-4">
                {{ error }}
            </v-alert>
            <div v-else-if="articles.length === 0" class="text-grey mt-4 text-center">
              No articles found matching this criteria.
            </div>

            <div v-else class="masonry-grid">
              <div v-for="article in articles" :key="article.id" class="masonry-item">
                <a :href="getPublicUrl(article)" class="article-grid-link">
                  <v-card class="article-grid-item">
                    <v-card-title class="item-title">{{ truncateTitle(article.title, ) }}</v-card-title>

                    <v-card-text v-if="article.snippet" class="item-snippet">
                      {{ article.snippet }}...
                    </v-card-text>

                    <v-divider></v-divider>

                    <v-card-actions class="pa-2">
                      <v-chip size="small" variant="tonal" color="cyan-lighten-3" class="mr-2">
                        {{ article.category }}
                      </v-chip>
                      <v-spacer></v-spacer>
                      <span class="text-caption text-grey-lighten-1">
                        {{ new Date(article.publish_at || article.created_at).toLocaleDateString() }}
                      </span>
                    </v-card-actions>
                  </v-card>
                </a>
              </div>
            </div>
            </v-col>
        </v-row>
      </v-container>
    </div>
  </v-main>
  <LanderFooter />
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import LanderFooter from '@/components/LanderFooter.vue';

const props = defineProps({
  public_address: String,
  category_slug: String,
  tag_slug: String,
  language: String
});

const route = useRoute();
const articles = ref([]);
const isLoading = ref(true);
const error = ref(null);
const pageTitle = ref('Articles');

function truncateTitle(title, length = 48) {
    if (!title) return '';
    if (title.length <= length) {
        return title;
    }
    return title.substring(0, length) + '...';
}

const mode = computed(() => {
  if (props.public_address) return 'author';
  if (props.category_slug) return 'category';
  if (props.tag_slug) return 'tag';
  if (props.language) return 'language';
  return 'all';
});

const filterValue = computed(() => {
    if (props.public_address) return props.public_address;
    if (props.category_slug) return decodeURIComponent(props.category_slug);
    if (props.tag_slug) return decodeURIComponent(props.tag_slug);
    if (props.language) return props.language;
    return null;
});

function updateStructuredData(articleList) {
  const oldScript = document.getElementById('list-structured-data');
  if (oldScript) {
    oldScript.remove();
  }
  if (!articleList || articleList.length === 0) return;
  const itemListElements = articleList.map((article, index) => {
    const lang = article.language || 'en';
    const url = `https://flowork.cloud/p-${article.slug}-${lang}.html`;
    return {
      "@type": "ListItem",
      "position": index + 1,
      "url": url,
      "name": article.title
    };
  });
  const schema = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": pageTitle.value,
    "itemListElement": itemListElements
  };
  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.id = 'list-structured-data';
  script.text = JSON.stringify(schema);
  document.head.appendChild(script);
  console.log('[SEO] Updated Structured Data (JSON-LD) for this ItemList.'); // English Log
}

async function fetchArticles() {
  isLoading.value = true;
  error.value = null;
  articles.value = [];

  if (!filterValue.value) {
    error.value = "No filter specified.";
    isLoading.value = false;
    return;
  }

  if (mode.value === 'author') {
    pageTitle.value = `Articles by ${filterValue.value.substring(0, 6)}...`;
  } else if (mode.value === 'category') {
    pageTitle.value = `Category: ${filterValue.value}`;
  } else if (mode.value === 'tag') {
    pageTitle.value = `Tag: ${filterValue.value}`;
  } else if (mode.value === 'language') {
    pageTitle.value = props.language === 'id' ? 'Artikel (Bahasa Indonesia)' : 'Articles (English)';
  }

  try {
    const apiUrl = `/api/v1/content/articles/list?${mode.value}=${encodeURIComponent(filterValue.value)}`;
    console.log(`[ArticleListView] Fetching: ${apiUrl}`); // English Log
    const response = await fetch(apiUrl);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch articles');
    }
    articles.value = data;
    updateStructuredData(data);
  } catch (e) {
      console.error(`[ArticleListView] Error: ${e.message}`); // English Log
      error.value = e.message;
  } finally {
      isLoading.value = false;
  }
}

function getPublicUrl(article) {
  const lang = article.language || 'en';
  return `/p-${article.slug}-${lang}.html`;
}

watch(() => route.params, fetchArticles, { immediate: true });

const canvasEl = ref(null);
let animationFrameId = null;
let mouse = { x: null, y: null, radius: 100 };
function handleMouseMove(event) {
    mouse.x = event.clientX;
    mouse.y = event.clientY;
}
const setupCanvasAnimation = () => {
    const canvas = canvasEl.value; if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    const resizeCanvas = () => { if(canvas) { canvas.width = window.innerWidth; canvas.height = window.innerHeight; } };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('mousemove', handleMouseMove);

    class Particle {
        constructor(x, y, size, color, speedX, speedY) {
            this.x = x; this.y = y;
            this.originX = x;
            this.originY = y;
            this.size = size; this.color = color;
            this.speedX = speedX; this.speedY = speedY;
            this.density = (Math.random() * 30) + 1;
        }
        update() {
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let distance = Math.sqrt(dx*dx + dy*dy);
            if (distance < mouse.radius) {
                let forceDirectionX = dx / distance;
                let forceDirectionY = dy / distance;
                let force = (mouse.radius - distance) / mouse.radius;
                let directionX = forceDirectionX * force * this.density * 0.5;
                let directionY = forceDirectionY * force * this.density * 0.5;
                this.x -= directionX;
                this.y -= directionY;
            } else {
                if (this.x !== this.originX) {
                    let dx = this.x - this.originX;
                    this.x -= dx/10;
                }
                if (this.y !== this.originY) {
                    let dy = this.y - this.originY;
                    this.y -= dy/10;
                }
            }
            if (this.x > canvas.width || this.x < 0) this.speedX = -this.speedX;
            if (this.y > canvas.height || this.y < 0) this.speedY = -this.speedY;
            if (distance >= mouse.radius) {
                this.x += this.speedX;
                this.y += this.speedY;
            }
        }
        draw() { ctx.fillStyle = this.color; ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill(); }
    }
    function init() {
        particles = []; let numberOfParticles = (canvas.height * canvas.width) / 15000;
        for (let i = 0; i < numberOfParticles; i++) {
            let size = (Math.random() * 2) + 1; let x = Math.random() * (innerWidth - size * 4) + size * 2; let y = Math.random() * (innerHeight - size * 4) + size * 2;
            let speedX = (Math.random() * 0.3) - 0.15; let speedY = (Math.random() * 0.3) - 0.15;
            particles.push(new Particle(x, y, size, 'rgba(0, 245, 255, 0.3)', speedX, speedY));
        }
    }
    function connect() {
        let opacityValue = 1;
        for (let a = 0; a < particles.length; a++) {
            for (let b = a; b < particles.length; b++) {
                let distance = ((particles[a].x - particles[b].x) * (particles[a].x - particles[b].x)) + ((particles[a].y - particles[b].y) * (particles[a].y - particles[b].y));
                if (distance < (canvas.width / 8) * (canvas.height / 8)) {
                    opacityValue = 1 - (distance / 25000);
                    ctx.strokeStyle = `rgba(191, 0, 255, ${opacityValue * 0.3})`; ctx.lineWidth = 1;
                    ctx.beginPath(); ctx.moveTo(particles[a].x, particles[a].y); ctx.lineTo(particles[b].x, particles[b].y); ctx.stroke();
                }
            }
        }
    }
    function animate() {
        animationFrameId = requestAnimationFrame(animate);
        ctx.clearRect(0, 0, innerWidth, innerHeight);
        particles.forEach(p => { p.update(); p.draw(); });
        connect();
    }
    init(); animate();
};

onMounted(() => {
    setupCanvasAnimation();
});

onUnmounted(() => {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }
    window.removeEventListener('mousemove', handleMouseMove);
});
</script>

<style scoped>
.article-list-page {
  position: relative;
  z-index: 1;
  background-color: #0A0F1E;
}
.neural-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  opacity: 0.5;
}
.page-content-container {
  position: relative;
  z-index: 2;
}
.legal-page { padding: 120px 0; min-height: 100vh; }
.legal-card {
  background: transparent;
  backdrop-filter: none;
  border: none;
  box-shadow: none !important;
}
.headline { color: #00f5ff; }
.orbitron-font { font-family: 'Orbitron', monospace; }

@property --angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}
.masonry-grid {
  column-gap: 16px;
  column-count: 1;
}
@media (min-width: 600px) {
  .masonry-grid {
    column-count: 2;
  }
}
@media (min-width: 960px) {
  .masonry-grid {
    column-count: 3;
  }
}
.masonry-item {
  break-inside: avoid;
  margin-bottom: 16px;
}
.article-grid-link {
  display: block;
  text-decoration: none;
}
.article-grid-item {
  background: rgba(23, 33, 65, 0.7);
  backdrop-filter: blur(10px);

  border: 2px solid transparent;
  background-clip: padding-box, border-box;
  background-origin: padding-box, border-box;
  background-image:
    linear-gradient(rgba(23, 33, 65, 0.7), rgba(23, 33, 65, 0.7)),
    conic-gradient(from var(--angle), transparent 25%, #64ffda, #bf00ff, transparent 75%);

  transition: all 0.3s ease-out;
  animation: border-chase 4s linear infinite;

  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.article-grid-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -75%;
  width: 50%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(0, 245, 255, 0.15),
    transparent
  );
  transform: skewX(-25deg);
  transition: left 0.7s ease-in-out;
  z-index: 1;
}

.article-grid-link:hover .article-grid-item {
  transform: translateY(-10px) perspective(1000px) rotateX(3deg) rotateY(-4deg);
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}

.article-grid-link:hover .article-grid-item::before {
  left: 125%;
}

@keyframes border-chase {
  to {
    --angle: 360deg;
  }
}

.item-title {
  color: #f0f0f0;
  font-weight: 500;
  white-space: normal;
  font-family: 'Exo 2', sans-serif;
  font-size: 1.1rem;
  line-height: 1.4;
  position: relative;
  z-index: 2;
}
.item-snippet {
  color: #B0BEC5;
  font-size: 0.9rem;
  line-height: 1.5;
  padding-bottom: 16px;
  position: relative;
  z-index: 2;
}
.article-grid-item .v-card-actions {
  margin-top: auto;
  background-color: rgba(0,0,0,0.2);
  position: relative;
  z-index: 2;
}
</style>
