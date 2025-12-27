//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\LanderCanvas.vue total lines 134 
//#######################################################################

<template>
  <div class="lander-canvas-container">
    <VueFlow
      :nodes="nodes"
      :edges="edges"
      :nodes-draggable="true"
      :nodes-connectable="false"
      :elements-selectable="false"
      :zoom-on-scroll="false"
      :zoom-on-pinch="false"
      :pan-on-drag="true"
      :prevent-scrolling="false"
      fit-view-on-init
      class="interactive-diorama"
    >
      <Background :variant="BackgroundVariant.Dots" :gap="25" :size="1.5" color="#2a2a4a" />

      <template #node-default="props">
        <div class="diorama-node">
          <div class="node-header">
            <v-icon :icon="props.data.icon" size="small" class="node-icon"></v-icon>
            <span class="node-name">{{ props.label }}</span>
          </div>
        </div>
      </template>

    </VueFlow>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { VueFlow } from '@vue-flow/core';
import { Background, BackgroundVariant } from '@vue-flow/background';

const nodes = ref([
  { id: '1', type: 'default', label: 'Generate AI Video', position: { x: 50, y: 150 }, data: { icon: 'mdi-movie-open-play-outline' } },
  { id: '2', type: 'default', label: 'Upload to YouTube', position: { x: 400, y: 0 }, data: { icon: 'mdi-youtube' } },
  { id: '3', type: 'default', label: 'Upload to TikTok', position: { x: 400, y: 150 }, data: { icon: 'mdi-music-note-eighth' } },
  { id: '4', type: 'default', label: 'Upload to Instagram', position: { x: 400, y: 300 }, data: { icon: 'mdi-instagram' } },
]);

const edges = ref([
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e1-3', source: '1', target: '3', animated: true },
  { id: 'e1-4', source: '1', target: '4', animated: true },
]);
</script>

<style>
/* COMMENT: [PENAMBAHAN KUNCI] Import CSS dasar Vue Flow agar komponennya punya ukuran dan bisa tampil */
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';

/* COMMENT: Styles updated to better fit as a background element */
.lander-canvas-container {
  height: 450px;
  width: 100%;
  border-radius: 16px;
  background-color: #161625;
  border: 1px solid var(--card-border);
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  overflow: hidden;
  position: relative;
}

.interactive-diorama {
  /* COMMENT: We can remove the border and shadow as it's now a background */
  background-color: transparent;
}

.interactive-diorama .vue-flow__node {
  border: none;
  box-shadow: none;
  background: transparent;
  width: auto;
  height: auto;
  cursor: grab;
}

.interactive-diorama .diorama-node {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  color: var(--text-primary);
  font-family: 'Exo 2', sans-serif;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  border-radius: 50px;
}

.interactive-diorama .diorama-node:hover {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 20px var(--neon-cyan);
}

.interactive-diorama .node-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 0.9rem;
  padding: 10px 18px;
}

.interactive-diorama .node-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.interactive-diorama .node-icon {
  color: var(--neon-cyan);
  margin-right: 8px;
}

/* Custom edge style */
.interactive-diorama .vue-flow__edge-path {
  stroke: var(--neon-purple);
  stroke-width: 2.5;
  stroke-dasharray: 5;
  animation: dashdraw 0.5s linear infinite;
}

@keyframes dashdraw {
  to {
    stroke-dashoffset: -10;
  }
}
</style>
