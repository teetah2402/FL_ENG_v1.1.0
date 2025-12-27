//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\panels\LogPanelContent.vue total lines 304 
//#######################################################################

<template>
  <div class="log-panel-content-wrapper">
    <template v-if="!agentStore.currentSessionId">
      <v-toolbar density="compact" color="transparent" class="px-2">
        <v-btn-toggle
            v-model="activeFilters"
            multiple
            variant="outlined"
            density="compact"
            class="filter-toggle"
        >
          <v-btn value="INFO" size="x-small" color="info">INFO</v-btn>
          <v-btn value="SUCCESS" size="x-small" color="success">SUCCESS</v-btn>
          <v-btn value="WARN" size="x-small" color="warning">WARN</v-btn>
          <v-btn value="ERROR" size="x-small" color="error">ERROR</v-btn>
          <v-btn value="DEBUG" size="x-small" color="grey">DEBUG</v-btn>
        </v-btn-toggle>
        <v-spacer></v-spacer>
        <v-tooltip text="Copy visible logs" location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn
              v-bind="props"
              :icon="copyIcon"
              variant="text"
              size="small"
              @click="copyLog"
              :disabled="filteredLogs.length === 0"
            ></v-btn>
          </template>
        </v-tooltip>
        <v-btn
          icon="mdi-delete-sweep-outline"
          variant="text"
          size="small"
          @click="logStore.clearLogs"
          :disabled="executionLogs.length === 0"
          title="Clear Log"
        ></v-btn>
      </v-toolbar>
      <v-divider></v-divider>

      <div class="panel-content" ref="logContainer">
        <div v-if="executionLogs.length === 0" class="log-entry text-grey">
          [INFO] Waiting for execution to start...
        </div>
        <div v-else-if="filteredLogs.length === 0" class="log-entry text-grey">
          [INFO] No logs match the current filter.
        </div>
        <div
          v-for="(log, index) in filteredLogs"
          :key="index"
          :class="['log-entry', getLogLevelClass(log.level)]"
        >
          <v-icon :icon="getLogLevelIcon(log.level)" size="x-small" class="mr-2 log-icon"></v-icon>
          <span class="log-source">[{{ log.source }}]</span> {{ log.message }}
        </div>
      </div>
    </template>

    <template v-else>
      <v-toolbar density="compact" color="transparent" class="px-2">
        <v-icon icon="mdi-robot-outline" class="mr-2" color="cyan-accent-3"></v-icon>
        <span class="agent-chat-title">Agent Session</span>
        <v-spacer></v-spacer>
        <v-tooltip text="End this Chat Session" location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn
              v-bind="props"
              icon="mdi-stop-circle-outline"
              variant="text"
              size="small"
              color="error"
              @click="endSession"
            ></v-btn>
          </template>
        </v-tooltip>
      </v-toolbar>
      <v-divider></v-divider>
      <div class="panel-content chat-content-wrapper" ref="chatContainer">
        <div v-if="agentStore.conversation.length === 0" class="log-entry text-grey">
          [AGENT] Session started. Waiting for response...
        </div>

        <div
          v-for="(msg, index) in agentStore.conversation"
          :key="index"
          :class="['chat-bubble', msg.type]"
        >
          <div v-if="msg.type === 'user'" class="message-content">
            {{ msg.content }}
          </div>
          <div v-if="msg.type === 'agent'" class="message-content" v-html="renderMarkdown(msg.content)">
          </div>
          <div v-if="msg.type === 'error'" class="message-content error-content">
            <strong>Error:</strong> {{ msg.content }}
          </div>
        </div>

        <div v-if="agentStore.isStreaming" class="chat-bubble agent">
          <v-progress-circular indeterminate color="cyan" size="20" width="2"></v-progress-circular>
        </div>

      </div>
    </template>
    </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue';
import { useLogStore } from '@/store/logs';
import { storeToRefs } from 'pinia';

import { useSocketStore } from '@/store/socket';
import { apiCancelSession } from '@/api';
import MarkdownIt from 'markdown-it';

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true
});
const renderMarkdown = (text) => {
  return md.render(text || '');
};

const socketStore = useSocketStore();
const agentStore = socketStore.useAgentStore();
const chatContainer = ref(null);

const logStore = useLogStore();
const { executionLogs } = storeToRefs(logStore);

const logContainer = ref(null);
const activeFilters = ref(['INFO', 'SUCCESS', 'WARN', 'ERROR', 'DEBUG']);
const copyIcon = ref('mdi-content-copy');

const filteredLogs = computed(() => {
    if (activeFilters.value.length === 5) return executionLogs.value;
    return executionLogs.value.filter(log => activeFilters.value.includes(log.level.toUpperCase()));
});

const getLogLevelClass = (level) => {
  const levelLower = (level || 'info').toLowerCase();
  if (levelLower.includes('success')) return 'log-success';
  if (levelLower.includes('warn')) return 'log-warn';
  if (levelLower.includes('error') || levelLower.includes('critical')) return 'log-error';
  if (levelLower.includes('debug') || levelLower.includes('detail')) return 'log-debug';
  return 'log-info';
};

const getLogLevelIcon = (level) => {
  const levelLower = (level || 'info').toLowerCase();
  if (levelLower.includes('success')) return 'mdi-check-circle-outline';
  if (levelLower.includes('warn')) return 'mdi-alert-outline';
  if (levelLower.includes('error') || levelLower.includes('critical')) return 'mdi-alert-circle-outline';
  if (levelLower.includes('debug') || levelLower.includes('detail')) return 'mdi-bug-outline';
  return 'mdi-information-outline';
};

const copyLog = () => {
    const logText = filteredLogs.value.map(log => `[${log.level.toUpperCase()}] [${log.source}] ${log.message}`).join('\n');
    navigator.clipboard.writeText(logText).then(() => {
        copyIcon.value = 'mdi-check';
        setTimeout(() => {
            copyIcon.value = 'mdi-content-copy';
        }, 1500);
    });
};

watch(executionLogs, () => {
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    }
  });
}, { deep: true });

watch(() => agentStore.conversation, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
}, { deep: true });

async function endSession() {
  const sessionId = agentStore.currentSessionId;
  if (!sessionId) return;

  console.log(`[LogPanel] User requested to end session ${sessionId}`);
  agentStore.reset();

  try {
    await apiCancelSession(sessionId);
  } catch (e) {
    console.error(`[LogPanel] Error sending cancel request:`, e);
  }
}
</script>

<style scoped>
.log-panel-content-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.panel-content {
  flex-grow: 1;
  overflow-y: auto;
  background-color: rgba(20, 20, 30, 0.4);
  border-radius: 4px;
  padding: 16px !important;
}
.filter-toggle {
    height: 28px !important;
}
.log-entry {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.85rem;
  margin-bottom: 4px;
  white-space: pre-wrap;
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.7);
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
}
.log-source {
  font-weight: bold;
  margin-right: 8px;
}
.log-icon {
  margin-top: 3px;
}
.log-info { color: #00f5ff; }
.log-success { color: #39ff14; }
.log-warn { color: #ffeb3b; }
.log-error { color: #ff5252; }
.log-debug { color: #9E9E9E; }
.agent-chat-title {
  color: #00f5ff !important;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
}
.chat-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.chat-bubble {
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 90%;
  line-height: 1.6;
  font-size: 0.95rem;
  color: var(--text-primary);
  word-wrap: break-word;
}
.chat-bubble.user {
  background-color: rgba(60, 60, 100, 0.6);
  align-self: flex-end;
  border-top-right-radius: 0;
}
.chat-bubble.agent {
  background-color: rgba(30, 30, 50, 0.8);
  align-self: flex-start;
  border-top-left-radius: 0;
  min-width: 60px;
}
.chat-bubble.error {
  background-color: rgba(100, 30, 30, 0.7);
  align-self: flex-start;
  border-top-left-radius: 0;
}
.message-content :deep(p) {
  margin-bottom: 8px;
}
.message-content :deep(pre) {
  background-color: rgba(0, 0, 0, 0.3);
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.85rem;
}
.message-content :deep(code) {
  font-family: 'Courier New', Courier, monospace;
  background-color: rgba(0, 0, 0, 0.2);
  padding: 2px 4px;
  border-radius: 3px;
}
.message-content :deep(pre) > code {
  background-color: transparent;
  padding: 0;
}
.message-content.error-content {
  color: #ff8a8a;
}
</style>
