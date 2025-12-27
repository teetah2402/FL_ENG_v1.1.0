//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\CommunityLinks.vue total lines 71 
//#######################################################################

<template>
  <v-list-item class="mb-2">
    <v-list-item-title class="text-overline">
      {{ $t('dashboard.community_title') }}
    </v-list-item-title>
  </v-list-item>

  <v-list-item
    v-for="item in communityLinks"
    :key="item.title"
    :href="item.href"
    target="_blank"
    rel="noopener noreferrer"
    class="community-link-item"
  >
    <template v-slot:prepend>
      <v-icon :icon="item.icon" :color="item.color"></v-icon>
    </template>
    <v-list-item-title>{{ item.title }}</v-list-item-title>
    <template v-slot:append>
      <v-icon icon="mdi-open-in-new" size="x-small" color="grey-darken-1"></v-icon>
    </template>
  </v-list-item>
</template>

<script setup>
import { ref } from 'vue';

const communityLinks = ref([
  {
    title: 'GitHub Repository',
    icon: 'mdi-github',
    color: 'white',
    href: 'https://github.com/flowork-dev' //
  },
  {
    title: 'Discord Server',
    icon: 'mdi-discord',
    color: '#5865F2',
    href: 'https://discord.gg/Gv7h5fWZY' //
  },
  {
    title: 'Telegram Group',
    icon: 'mdi-telegram',
    color: '#2AABEE',
    href: 'https://t.me/FLOWORK_AUTOMATION'
  },
  {
    title: 'YouTube Tutorials',
    icon: 'mdi-youtube',
    color: '#FF0000',
    href: 'https://www.youtube.com/playlist?list=PLATUnnrT5igDXCqjBVvkmE4UKq9XASUtT'
  }
]);
</script>

<style scoped>
.community-link-item {
  transition: background-color 0.2s ease-in-out;
  border-radius: 8px;
}
.community-link-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
}
</style>
