//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\LanderHeader.vue total lines 224
//#######################################################################

<template>
  <v-app-bar color="transparent" flat class="lander-header" :class="{ 'is-scrolled': isScrolled }" height="70">
    <v-container class="d-flex align-center pa-0">

      <div class="header-logo d-flex align-center" style="cursor: pointer;" @click="$router.push('/')">
        <img src="/logo.svg" alt="Flowork" class="header-logo-img" />
      </div>

      <v-spacer></v-spacer>

      <div class="d-none d-md-flex align-center" style="gap: 4px;">
        <v-tooltip text="Home" location="bottom">
            <template v-slot:activator="{ props: tooltipProps }">
                <v-btn
                  v-bind="tooltipProps"
                  :to="{ name: 'Lander' }"
                  icon
                  variant="text"
                  class="header-link"
                >
                    <v-icon color="grey-lighten-1">mdi-home-outline</v-icon>
                </v-btn>
            </template>
        </v-tooltip>

        <v-menu>
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" variant="text" class="header-link" append-icon="mdi-chevron-down">
              <v-icon start color="grey-lighten-1">mdi-translate</v-icon>
              Language
            </v-btn>
          </template>
          <v-list density="compact">
            <v-list-item href="/en/">
              <v-list-item-title>English</v-list-item-title>
            </v-list-item>
            <v-list-item href="/id/">
              <v-list-item-title>Indonesia</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>

        <v-tooltip text="Telegram" location="bottom">
            <template v-slot:activator="{ props: tooltipProps }">
                <v-btn
                  v-bind="tooltipProps"
                  href="https://t.me/FLOWORK_AUTOMATION"
                  target="_blank"
                  rel="noopener noreferrer"
                  icon
                  variant="text"
                  class="header-link"
                >
                    <v-icon color="grey-lighten-1">mdi-send</v-icon>
                    </v-btn>
            </template>
        </v-tooltip>

        <v-tooltip text="YouTube" location="bottom">
            <template v-slot:activator="{ props: tooltipProps }">
                <v-btn
                  v-bind="tooltipProps"
                  href="https://www.youtube.com/playlist?list=PLATUnnrT5igDXCqjBVvkmE4UKq9XASUtT"
                  target="_blank"
                  rel="noopener noreferrer"
                  icon
                  variant="text"
                  class="header-link"
                >
                    <v-icon color="grey-lighten-1">mdi-youtube</v-icon>
                </v-btn>
            </template>
        </v-tooltip>

        <v-tooltip text="Docs" location="bottom">
            <template v-slot:activator="{ props: tooltipProps }">
                <v-btn
                  v-bind="tooltipProps"
                  href="https://docs.flowork.cloud"
                  target="_blank"
                  rel="noopener noreferrer"
                  icon
                  variant="text"
                  class="header-link"
                >
                  <v-icon color="grey-lighten-1">mdi-book-open-page-variant-outline</v-icon>
                </v-btn>
            </template>
        </v-tooltip>
      </div>

      <v-spacer></v-spacer>

      <template v-if="!authStore.isAuthenticated">
        <v-btn
            :to="{ name: 'AppsCenter' }"
            variant="text"
            color="white"
            class="header-btn mx-2 orbitron-font"
        >
            Apps Center
        </v-btn>

        <v-btn
            :to="{ name: 'Marketplace' }"
            variant="text"
            color="white"
            class="header-btn mx-2 orbitron-font"
        >
            Marketplace
        </v-btn>
        <v-btn
            :to="{ name: 'News' }"
            variant="text"
            color="white"
            class="header-btn mx-2 orbitron-font"
        >
            News
        </v-btn>
        <v-btn to="/login" variant="outlined" color="white" class="header-btn mx-2">Login</v-btn>
        <v-btn to="/register" variant="flat" color="cyan" class="header-btn header-btn-primary">
          Sign Up Free
        </v-btn>
      </template>
      <template v-else>
        <v-btn :to="{ name: 'Designer' }" variant="flat" color="cyan" class="header-btn header-btn-primary">
          Go to App
        </v-btn>
      </template>

    </v-container>
  </v-app-bar>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '@/store/auth';
const authStore = useAuthStore();

const isScrolled = ref(false);
const handleScroll = () => { isScrolled.value = window.scrollY > 20; };

onMounted(() => { window.addEventListener('scroll', handleScroll); });
onUnmounted(() => { window.removeEventListener('scroll', handleScroll); });
</script>

<style scoped>
.lander-header {
  transition: background-color 0.3s ease;
  z-index: 1000 !important;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
}
.lander-header.is-scrolled {
  background: rgba(10, 15, 30, 0.8) !important;
  backdrop-filter: blur(10px);
}

/* (MODIFIKASI GEMINI)
   Class .header-logo buat text udah nggak perlu font styling
   karena isinya cuma gambar.
*/
.header-logo {
  /* Biar interaktif */
  transition: opacity 0.2s ease;
}
.header-logo:hover {
  opacity: 0.8;
}

/* [UPDATED] Logo Image Styling */
/* Gue gedein dikit height-nya biar SVG barunya kebaca jelas */
.header-logo-img {
    height: 48px; /* Naik dari 40px biar gagah di Landing Page */
    width: auto;
    display: block;
    filter: drop-shadow(0 0 8px rgba(0, 245, 255, 0.4));
}

.header-link {
  font-weight: 600;
  color: var(--text-secondary) !important;
}
.header-link .v-icon {
    color: var(--text-secondary) !important;
}

.header-btn.orbitron-font {
    font-family: 'Orbitron', monospace;
    color: var(--text-secondary) !important;
}
.header-btn.orbitron-font:hover {
    color: var(--neon-cyan) !important;
}

.header-btn-primary {
  color: #010c03 !important;
  font-weight: bold;
}
.orbitron-font {
  font-family: 'Orbitron', monospace;
}
.header-btn-download {
  font-weight: bold;
  font-size: 0.8rem;
  color: #000 !important;
  background-color: var(--neon-orange);
  border-radius: 20px;
}
.header-btn-download:hover {
  background-color: #f57c00;
}
.header-btn {
    border-radius: 20px;
}
</style>