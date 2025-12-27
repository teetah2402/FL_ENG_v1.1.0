//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai\AiChatWindow.vue total lines 250 
//#######################################################################

<template>
    <div class="main-content d-flex flex-column flex-grow-1" style="overflow: hidden; position: relative;">
        <div class="chat-scroll-area flex-grow-1 pa-4 d-flex flex-column align-center" ref="scrollContainer" style="overflow-y: auto; height: 100%;">
            <div class="w-100" style="max-width: 800px; padding-bottom: 120px;">

                <div v-if="currentMessages.length === 0" class="empty-state text-center mt-16 fade-in px-4">
                    <div class="gemini-logo-glow mb-6 mx-auto"><v-icon icon="mdi-creation" size="56" color="transparent" class="gradient-icon-gold"></v-icon></div>
                    <h1 class="text-h4 font-weight-medium text-gold-gradient mb-2 font-secondary">{{ getWelcomeTitle() }}</h1>
                    <p class="text-h6 text-grey-darken-1 font-weight-light mb-10">{{ getWelcomeSubtitle() }}</p>
                    <div class="d-flex flex-wrap justify-center gap-3">
                        <v-card v-for="sug in suggestions" :key="sug" class="suggestion-card pa-4 rounded-xl" variant="outlined" @click="promptInput = sug">
                            <div class="text-body-2 text-grey-lighten-2">{{ sug }}</div>
                        </v-card>
                    </div>
                </div>

                <div v-else class="pt-4">
                    <div v-for="(msg, index) in currentMessages" :key="index" class="mb-6 fade-in-up group">
                        <div v-if="msg.role === 'user'" class="d-flex align-start justify-end">
                            <div v-if="editingIndex === index" class="w-100 d-flex justify-end" style="max-width: 85%;">
                                <v-card color="#2a2b2d" class="w-100 rounded-xl pa-2">
                                    <v-textarea v-model="editContent" variant="plain" bg-color="transparent" auto-grow rows="1" class="px-2 text-body-1" hide-details></v-textarea>
                                    <div class="d-flex justify-end mt-2 px-2 pb-1 gap-2">
                                        <v-btn size="small" variant="text" color="grey" @click="cancelEdit">Cancel</v-btn>
                                        <v-btn size="small" color="#D4AF37" variant="tonal" @click="saveEdit(index)">Update</v-btn>
                                    </div>
                                </v-card>
                            </div>
                            <div v-else class="d-flex flex-column align-end" style="max-width: 85%;">
                                <div class="bg-user-bubble px-5 py-3 rounded-xl rounded-tr-sm text-body-1 text-white font-secondary shadow-sm">{{ msg.content }}</div>
                                <div class="d-flex mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <v-btn size="x-small" variant="text" icon="mdi-pencil" color="grey" @click="startEdit(index, msg.content)" class="mr-1"></v-btn>
                                    <v-btn size="x-small" variant="text" icon="mdi-content-copy" color="grey" @click="copyToClipboard(msg.content)" class="mr-1"></v-btn>
                                    <v-btn size="x-small" variant="text" icon="mdi-delete" color="grey-darken-1" @click="deleteMessage(index)"></v-btn>
                                </div>
                            </div>
                        </div>

                        <div v-else class="d-flex align-start">
                            <div class="ai-avatar mr-4 mt-1">
                                <div v-if="msg.isLoading && !msg.content" class="thinking-pulse"><v-icon icon="mdi-brain" size="22" :color="getThemeColor()"></v-icon></div>
                                <v-icon v-else icon="mdi-shimmer" size="22" :color="msg.error ? 'red-accent-2' : getThemeColor()"></v-icon>
                            </div>
                            <div class="flex-grow-1" style="max-width: 95%;">
                                <div v-if="msg.error" class="text-red-accent-2 bg-red-dim pa-4 rounded-lg border-red-thin">
                                    <v-icon start icon="mdi-alert-circle" size="small" class="mr-2"></v-icon> {{ msg.content }}
                                </div>

                                <div v-else-if="msg.isLoading" class="thinking-container pa-3 rounded-lg border-thin-dashed">
                                    <div class="d-flex align-center text-caption font-mono mb-1" :class="`text-${getThemeColor(true)}`">
                                        <v-progress-circular indeterminate size="16" width="2" :color="getThemeColor(true)" class="mr-2"></v-progress-circular>
                                        <span>{{ msg.status || 'Connecting to Neural Engine...' }}</span>
                                    </div>
                                    <div v-if="msg.queuePos && msg.queuePos > 0" class="text-grey-darken-1 text-caption font-italic mt-1">You are number #{{ msg.queuePos }} in the queue.</div>
                                </div>

                                <div v-else class="markdown-body text-grey-lighten-3">
                                    <pre v-if="msg.content && !msg.mediaType" class="response-text">{{ msg.content }}</pre>

                                    <div v-if="msg.mediaType === 'image'" class="media-container mt-2">
                                        <div v-if="imageStates[msg.mediaUrl] === 'loading'" class="pa-4 bg-grey-darken-4 rounded d-flex align-center justify-center"><v-progress-circular indeterminate color="#D4AF37"></v-progress-circular></div>
                                        <div v-else-if="imageStates[msg.mediaUrl] === 'error'" class="pa-4 bg-red-dim text-red-accent-2 rounded">Failed to load image.</div>
                                        <img v-else :src="secureImages.get(msg.mediaUrl) || msg.mediaUrl" class="rounded-lg border-thin elevation-2" style="max-width: 100%; max-height: 500px;" @error="handleImageError(msg)">
                                    </div>
                                    <div v-if="msg.mediaType === 'audio'" class="media-container mt-2"><audio controls :src="secureImages.get(msg.mediaUrl) || msg.mediaUrl" class="w-100"></audio></div>
                                    <div v-if="msg.mediaType === 'video'" class="media-container mt-2"><video controls :src="secureImages.get(msg.mediaUrl) || msg.mediaUrl" class="w-100 rounded-lg"></video></div>
                                </div>

                                <div v-if="!msg.isLoading" class="d-flex mt-2 opacity-60 hover-opacity-100">
                                    <template v-if="msg.mediaType"><v-btn size="x-small" variant="text" icon="mdi-download" color="grey" class="mr-2" @click="downloadMedia(msg.mediaUrl, msg.mediaType)"></v-btn></template>
                                    <template v-else><v-btn size="x-small" variant="text" icon="mdi-content-copy" color="grey" class="mr-2" @click="copyToClipboard(msg.content)"></v-btn></template>
                                    <v-btn size="x-small" variant="text" :icon="msg.liked ? 'mdi-thumb-up' : 'mdi-thumb-up-outline'" :color="msg.liked ? 'amber-accent-3' : 'grey'" class="mr-2" @click="toggleLike(index)"></v-btn>
                                    <v-btn size="x-small" variant="text" icon="mdi-delete-outline" color="grey" @click="deleteMessage(index)"></v-btn>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="input-footer py-6 px-4 d-flex justify-center bg-gradient-footer flex-grow-0 flex-shrink-0">
            <div class="input-wrapper w-100 position-relative" style="max-width: 760px;">
                <v-textarea v-model="promptInput" :placeholder="getInputPlaceholder()" variant="solo" bg-color="#1e1f20" class="gemini-input font-body-1" hide-details auto-grow rows="1" max-rows="8" rounded="xl" @keydown.enter.prevent="handleSend">
                    <template v-slot:append-inner>
                        <v-btn :disabled="!promptInput || aiCenterStore.isGenerating" icon="mdi-send" variant="flat" :color="promptInput ? getSendBtnColor() : 'grey-darken-3'" class="ml-2 send-btn" size="small" @click="handleSend" :loading="aiCenterStore.isGenerating">
                            <v-icon :color="promptInput ? 'black' : 'grey'" icon="mdi-arrow-up"></v-icon>
                        </v-btn>
                    </template>
                </v-textarea>
                <div class="text-center text-caption text-grey-darken-2 mt-2 font-weight-medium">Flowork can make mistakes. Check important info.</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, inject } from 'vue';
import { useAiCenterStore } from '@/store/aiCenter';
import { storeToRefs } from 'pinia';
import { getAuthHeaders } from '@/api';
import { useUiStore } from '@/store/ui';

const aiState = inject('aiState');
const aiCenterStore = useAiCenterStore();
const uiStore = useUiStore();
const { currentMessages, currentSessionId } = storeToRefs(aiCenterStore);

const promptInput = ref('');
const scrollContainer = ref(null);
const editingIndex = ref(-1);
const editContent = ref('');

const secureImages = reactive(new Map());
const imageStates = reactive({});

const agentSuggestions = ref(["Research AI trends", "Draft email reply", "Scrape prices", "Analyze CSV"]);
const councilSuggestions = ref(["Debate: Rust vs C++", "Analyze Architecture", "Solve SQL Deadlock", "Kafka Config"]);
const defaultSuggestions = ref(["Explain Quantum Computing", "Generate Cyberpunk City", "Python script for CSV", "Debug SQL"]);

const suggestions = computed(() => {
    if (aiState.mode === 'council') return councilSuggestions.value;
    if (aiState.mode === 'agent') return agentSuggestions.value;
    return defaultSuggestions.value;
});

watch(currentMessages, (newMessages) => {
    if (aiCenterStore.isGenerating || editingIndex.value === -1) scrollToBottom();
    newMessages.forEach(msg => {
        if (msg.mediaUrl) {
            const type = msg.mediaType || 'image';
            loadSecureMedia(msg, type);
        }
    });
}, { deep: true });

async function loadSecureMedia(msg, type='image') {
    if (!msg.mediaUrl || secureImages.has(msg.mediaUrl) || imageStates[msg.mediaUrl] === 'loading') return;
    imageStates[msg.mediaUrl] = 'loading';
    try {
        const headers = await getAuthHeaders(msg.mediaUrl, 'GET');
        const urlObj = new URL(msg.mediaUrl);
        const engineId = urlObj.searchParams.get('engine_id');
        if (engineId) headers['X-Flowork-Engine-ID'] = engineId;
        const response = await fetch(msg.mediaUrl, { headers });
        if (!response.ok) throw new Error('Failed');
        const blob = await response.blob();

        let blobType = blob.type;
        if (type === 'audio' && !blobType) blobType = 'audio/wav';
        if (type === 'video' && !blobType) blobType = 'video/mp4';

        secureImages.set(msg.mediaUrl, URL.createObjectURL(new Blob([blob], { type: blobType })));
        imageStates[msg.mediaUrl] = 'loaded';
    } catch (e) { imageStates[msg.mediaUrl] = 'error'; }
}

function handleImageError(msg) { imageStates[msg.mediaUrl] = 'error'; }

async function downloadMedia(url, type) {
    uiStore.showNotification({ text: 'Preparing download...', color: 'info' });
    try {
        let objectUrl = secureImages.get(url);
        if (!objectUrl) {
             const headers = await getAuthHeaders(url, 'GET');
             const response = await fetch(url, { headers });
             if (!response.ok) throw new Error('Download failed');
             const blob = await response.blob();
             objectUrl = URL.createObjectURL(blob);
        }
        const a = document.createElement('a');
        a.href = objectUrl;
        a.download = `flowork_${type}_${Date.now()}.${type==='image'?'png':'mp4'}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } catch { uiStore.showNotification({ text: 'Download Failed.', color: 'error' }); }
}

function handleSend() {
    if (!promptInput.value) return;
    const extra = {};

    if (aiState.mode === 'agent') {
        extra.is_agent = true;
    } else if (aiState.mode === 'council') {
        if (!aiState.selectedJudgeId) { uiStore.showNotification({ text: 'Select Judge!', color: 'warning' }); return; }
        extra.is_council = true;
        extra.judge_id = aiState.selectedJudgeId;
        extra.members = aiState.selectedCouncilMembers;
    }

    let modelId = aiState.selectedEndpointId;
    if (aiState.mode === 'council') modelId = aiState.selectedJudgeId;

    aiCenterStore.sendMessage(promptInput.value, modelId, extra);
    promptInput.value = '';
    scrollToBottom();
}

function startEdit(index, content) { editingIndex.value = index; editContent.value = content; }
function cancelEdit() { editingIndex.value = -1; }
function saveEdit(index) { aiCenterStore.editMessage(currentSessionId.value, index, editContent.value); editingIndex.value = -1; }
function deleteMessage(idx) { aiCenterStore.deleteMessage(currentSessionId.value, idx); }
function copyToClipboard(text) { navigator.clipboard.writeText(text); uiStore.showNotification({ text: 'Copied!', color: 'success' }); }
function toggleLike(index) { aiCenterStore.toggleLike(currentSessionId.value, index); }
function scrollToBottom() { nextTick(() => { if (scrollContainer.value) scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight; }); }

function getWelcomeTitle() { return aiState.mode === 'council' ? 'Neural Council' : (aiState.mode === 'agent' ? 'Agent Command' : 'Flowork AI'); }
function getWelcomeSubtitle() { return 'Architect your digital workflow.'; }
function getInputPlaceholder() { return 'Enter prompt...'; }
function getThemeColor(darker=false) { return darker ? '#D4AF37' : '#E5C550'; }
function getSendBtnColor() { return '#D4AF37'; }

</script>

<style scoped>
.chat-scroll-area::-webkit-scrollbar { width: 8px; }
.chat-scroll-area::-webkit-scrollbar-track { background: transparent; }
.chat-scroll-area::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
.bg-user-bubble { background-color: #151515; border: 1px solid rgba(212, 175, 55, 0.08); }
.response-text { white-space: pre-wrap; font-family: 'Roboto', sans-serif; line-height: 1.6; }
.markdown-body pre { background: #1e1f20; padding: 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); }
.bg-gradient-footer { background: linear-gradient(to top, #000 80%, rgba(0,0,0,0) 100%); }
.gemini-input :deep(.v-field) { border-radius: 28px !important; background-color: #1e1f20 !important; border: 1px solid rgba(212, 175, 55, 0.1); }
.gemini-input :deep(.v-field--focused) { border-color: #D4AF37 !important; box-shadow: 0 0 15px rgba(212, 175, 55, 0.1) !important; }
.thinking-container { background: rgba(212, 175, 55, 0.01); border: 1px dashed rgba(212, 175, 55, 0.15); }
.thinking-pulse { animation: brainPulse 2s infinite ease-in-out; }
@keyframes brainPulse {
    0% { transform: scale(1); opacity: 0.7; } 50% { transform: scale(1.1); opacity: 1; } 100% { transform: scale(1); opacity: 0.7; }
}
.gradient-icon-gold {
    background: linear-gradient(45deg, #D4AF37 0%, #F0E68C 100%);
    background-clip: text; /* Fix CSS Warning */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.text-gold-gradient {
    background: linear-gradient(90deg, #D4AF37, #E5C550);
    background-clip: text; /* Fix CSS Warning */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
