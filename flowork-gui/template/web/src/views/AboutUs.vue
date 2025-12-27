//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\AboutUs.vue total lines 192 
//#######################################################################

<template>
  <div class="about-us-page">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="10" lg="8">

          <div class="section-container text-center">
            <h1 class="main-title orbitron-font mb-4">{{ loc('about_main_title') }}</h1>
            <p class="text-body-1 text-grey-lighten-1 mx-auto" style="max-width: 700px;">
              {{ loc('about_vision_p1') }}
            </p>
            <p class="text-body-1 text-grey-lighten-1 mx-auto mt-4" style="max-width: 700px;">
              {{ loc('about_vision_p2') }}
            </p>
          </div>

          <div class="section-container">
            <h2 class="section-title orbitron-font">{{ loc('about_team_title') }}</h2>
            <p class="text-center text-grey-lighten-2 mb-8">{{ loc('about_team_intro') }}</p>
            <v-row>
              <v-col v-for="member in team" :key="member.name" cols="12" sm="6" md="3">
                <v-card class="team-card" variant="flat" color="transparent">
                  <div class="card-glow"></div>
                  <div class="card-content">
                    <v-avatar size="100" class="mb-4">
                      <v-img :src="member.avatar" :alt="member.name"></v-img>
                    </v-avatar>
                    <v-card-title class="pa-0 font-weight-bold">{{ member.name }}</v-card-title>
                    <v-card-subtitle class="mb-2">{{ loc(member.roleKey) }}</v-card-subtitle>
                    <v-card-text class="text-caption text-center pa-0">"{{ loc(member.quoteKey) }}"</v-card-text>
                    </div>
                </v-card>
              </v-col>
            </v-row>
          </div>

          <div class="section-container">
              <h2 class="section-title orbitron-font">{{ loc('about_thanks_title') }}</h2>
              <p class="text-center text-grey-lighten-2 mb-8">{{ loc('about_thanks_intro') }}</p>

              <v-card class="special-thanks-card mb-8">
                  <v-card-title class="special-thanks-title orbitron-font">SPECIAL THANKS</v-card-title>
                  <v-card-text class="text-center">
                      <div class="font-weight-bold">JavaFX</div>
                      <div class="text-caption">{{ loc('about_thanks_javafx') }}</div>
                  </v-card-text>
              </v-card>

              <v-row>
                  <v-col cols="12" md="6">
                      <h4 class="sub-section-title">{{ loc('about_thanks_ai_partners_title') }}</h4>
                      <v-list-item :title="loc('about_thanks_gemini_title')" :subtitle="loc('about_thanks_gemini_desc')"></v-list-item>
                      <v-list-item :title="loc('about_thanks_llama_title')" :subtitle="loc('about_thanks_llama_desc')"></v-list-item>
                      <v-list-item :title="loc('about_thanks_whisper_title')" :subtitle="loc('about_thanks_whisper_desc')"></v-list-item>
                  </v-col>
                  <v-col cols="12" md="6">
                      <h4 class="sub-section-title">{{ loc('about_thanks_tools_title') }}</h4>
                      <v-list-item :title="loc('about_thanks_ffmpeg_title')" :subtitle="loc('about_thanks_ffmpeg_desc')"></v-list-item>
                      </v-col>
              </v-row>

              <h4 class="sub-section-title mt-6">{{ loc('about_thanks_tech_title') }}</h4>
              <div class="text-center mt-4">
                  <v-chip v-for="tech in techStack" :key="tech" class="ma-1" color="grey-darken-3">{{ tech }}</v-chip>
              </div>
          </div>


          <div class="section-container text-center">
            <h2 class="section-title orbitron-font">{{ loc('about_community_title') }}</h2>
            <p class="text-body-1 text-grey-lighten-1 mx-auto" style="max-width: 700px;">
             {{ loc('about_community_intro') }}
            </p>
            <div class="mt-8">
              <v-btn v-for="link in communityLinks" :key="link.textKey" :href="link.url" target="_blank" size="large" class="ma-2 community-btn" :color="link.color" :prepend-icon="link.icon">
                {{ loc(link.textKey) }}
              </v-btn>
            </div>
          </div>

          <div class="section-container">
              <h2 class="section-title orbitron-font">{{ loc('about_contributors_title') }}</h2>
              <p class="text-center text-grey-lighten-2 mb-4">{{ loc('about_contributors_desc') }}</p>
              <div class="text-center text-grey">
                  <p>{{ loc('about_contributors_placeholder') }}</p>
                  </div>
          </div>

          <div class="section-container">
              <h2 class="section-title orbitron-font">{{ loc('about_donors_title') }}</h2>
              <p class="text-center text-grey-lighten-2 mb-4">{{ loc('about_donors_desc') }}</p>
              <div class="text-center text-grey">
                  <p>{{ loc('about_donors_placeholder') }}</p>
              </div>
          </div>


        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useLocaleStore } from '@/store/locale';
import { storeToRefs } from 'pinia';

const localeStore = useLocaleStore();
const { loc } = storeToRefs(localeStore);

const team = ref([
  { name: 'Awenk Audico', roleKey: 'about_team_role_architect', quoteKey: 'about_team_quote_awenk', avatar: 'https://cdn.icon-icons.com/icons2/1378/PNG/512/avatardefault_92824.png' },
  { name: 'Imam Oechil', roleKey: 'about_team_role_plugin', quoteKey: 'about_team_quote_imam', avatar: 'https://cdn.icon-icons.com/icons2/1378/PNG/512/avatardefault_92824.png' },
  { name: 'Irzad', roleKey: 'about_team_role_module', quoteKey: 'about_team_quote_irzad', avatar: 'https://cdn.icon-icons.com/icons2/1378/PNG/512/avatardefault_92824.png' },
  { name: 'Teguh FX', roleKey: 'about_team_role_widget', quoteKey: 'about_team_quote_teguh', avatar: 'https://cdn.icon-icons.com/icons2/1378/PNG/512/avatardefault_92824.png' },
]);

const techStack = ref(['Python', 'Vue.js', 'Vuetify', 'Pinia', 'Vite', 'Flask', 'Axios', 'Vue Flow', 'and many more...']);

const communityLinks = ref([
    { textKey: 'about_community_btn_telegram', url: 'https://t.me/FLOWORK_AUTOMATION', icon: 'mdi-send', color: 'blue-lighten-1' },
    { textKey: 'about_community_btn_youtube', url: 'https://www.youtube.com/playlist?list=PLATUnnrT5igDXCqjBVvkmE4UKq9XASUtT', icon: 'mdi-youtube', color: 'red' },
    { textKey: 'about_community_btn_support', url: 'https://www.paypal.com/paypalme/TeetahDev', icon: 'mdi-heart', color: 'yellow-darken-2' }
]);
</script>

<style scoped>
.about-us-page {
  height: 100%;
  overflow-y: auto;
  padding: 48px 0;
}
.section-container {
  margin-bottom: 96px;
}
.main-title {
  color: #f0f0f0;
  text-shadow: 0 0 10px var(--neon-cyan), 0 0 20px var(--neon-cyan);
}
.section-title {
  text-align: center;
  margin-bottom: 32px;
  color: #e0e0e0;
  text-shadow: 0 0 8px var(--neon-purple);
}
.sub-section-title {
    font-family: 'Exo 2', sans-serif;
    color: var(--neon-cyan);
    margin-bottom: 16px;
    border-left: 3px solid var(--neon-cyan);
    padding-left: 12px;
}
.team-card {
  position: relative;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease-in-out;
  height: 100%;
}
.team-card:hover {
  transform: translateY(-10px);
  border-color: var(--neon-cyan);
  box-shadow: 0 10px 30px rgba(0, 245, 255, 0.2);
}
.special-thanks-card {
    background: linear-gradient(135deg, rgba(255, 223, 0, 0.1), rgba(255, 165, 0, 0.1));
    border: 1px solid #FFD700;
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
}
.special-thanks-title {
    color: #FFD700;
    text-align: center;
    letter-spacing: 2px;
}
.community-btn {
  font-weight: bold;
}
.v-list-item {
    background: transparent !important;
}
</style>
