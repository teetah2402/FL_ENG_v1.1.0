//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\GlobalWidgetOverlay.vue total lines 115 
//#######################################################################

<template>
  <div class="global-widget-overlay" :class="{ 'hidden-mode': !isVisible }">
    <div
      v-for="w in activeWidgets"
      :key="w.instanceId"
      v-show="w.instanceId === currentTab"
      class="widget-wrapper"
    >
      <iframe
        :id="`iframe-${w.instanceId}`"
        :src="resolveWidgetUrl(w)"
        class="widget-frame"
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals allow-downloads"
        @load="onIframeLoad(w)"
      ></iframe>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useWidgetStore } from '@/store/widgets';
import { getGatewayUrl, apiClient } from '@/api';

const route = useRoute();
const widgetStore = useWidgetStore();

const activeWidgets = computed(() => widgetStore.activeWidgets);
const currentTab = computed(() => widgetStore.currentTab);

const isVisible = computed(() => {
  return route.path === '/widgets' && activeWidgets.value.length > 0;
});

const resolveWidgetUrl = (widget) => {
    if (widget.source === 'cloud') {
        return widget.targetUrl;
    } else {
        return `${getGatewayUrl()}${widget.targetUrl}`;
    }
};

const onIframeLoad = async (w) => {
    const dataKey = `widget_${w.id}_data`;
    try {
        const response = await apiClient.get(`/variables/${dataKey}`);
        let variableData = response.data;
        if (!variableData || variableData.value === null) return;

        let savedData = null;
        try {
            savedData = JSON.parse(variableData.value);
            if (typeof savedData === 'string' && (savedData.trim().startsWith('{') || savedData.trim().startsWith('['))) {
                 savedData = JSON.parse(savedData);
            }
        } catch(e) { savedData = variableData.value; }

        const iframe = document.getElementById(`iframe-${w.instanceId}`);
        if (iframe) iframe.contentWindow.postMessage({ type: 'CMD_LOAD', payload: savedData }, '*');
    } catch (e) {
    }
};
</script>

<style scoped>
.global-widget-overlay {
  position: fixed;
  /* Sesuaikan dengan layout dashboard lu */
  top: 64px; /* Tinggi Header/AppBar */
  left: 280px; /* Lebar Sidebar WidgetToolbox */
  right: 0;
  bottom: 0;
  z-index: 50; /* Di atas konten lain pas aktif */
  background: transparent;
  pointer-events: auto;
  display: flex;
  flex-direction: column;
  padding: 1rem; /* Padding samain kayak dashboard */
}

.widget-wrapper {
  width: 100%;
  height: 100%;
  background: #1e1e2e;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
}

.widget-frame {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

/* MODE HANTU: Sembunyi tapi TETAP HIDUP */
.hidden-mode {
  visibility: hidden; /* Jangan display:none, nanti iframe reload! */
  pointer-events: none;
  /* Lempar jauh-jauh biar gak ganggu klik */
  top: -10000px;
  left: -10000px;
  width: 1px;
  height: 1px;
}
</style>
