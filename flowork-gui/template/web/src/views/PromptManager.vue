//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\PromptManager.vue total lines 541 
//#######################################################################

<template>
  <v-container fluid class="prompt-manager-container fill-height pa-0 ma-0 relative overflow-hidden bg-deep-black">
    <div class="bg-grid-moving"></div>
    <div class="vignette-overlay"></div>

    <v-row no-gutters class="fill-height relative z-10">

      <v-col cols="12" md="3" class="library-pane border-right-subtle d-flex flex-column">
        <div class="pane-header pa-4 d-flex align-center justify-space-between bg-black-glass">
           <div class="d-flex align-center">
              <v-icon icon="mdi-database-eye-outline" color="amber-darken-1" class="mr-3"></v-icon>
              <span class="text-subtitle-2 font-weight-bold orbitron-font text-grey-lighten-1 tracking-wider">DATA_CODEX</span>
           </div>
           <v-btn
              variant="text"
              color="amber-darken-1"
              size="small"
              class="font-mono text-caption"
              @click="handleNewPrompt"
            >
              [+] NEW
            </v-btn>
        </div>

        <div class="px-4 py-2 bg-black-glass border-bottom-subtle">
           <v-text-field
            v-model="searchQuery"
            placeholder="search_protocols..."
            variant="plain"
            density="compact"
            hide-details
            class="font-mono terminal-input text-amber-lighten-4"
            prepend-inner-icon="mdi-magnify"
          ></v-text-field>
        </div>

        <div class="flex-grow-1 overflow-y-auto custom-scrollbar pa-3">

          <div class="section-label font-mono text-caption text-cyan-darken-1 mb-2 mt-1 px-1">
              SYSTEM_KERNELS (READ_ONLY)
          </div>

          <div
            v-for="tmpl in filteredTemplates"
            :key="'sys-'+tmpl.id"
            :class="['prompt-item mb-1', { 'active-item-sys': selectedPromptId === 'sys-'+tmpl.id }]"
            @click="handleSelectTemplate(tmpl)"
          >
             <div class="d-flex justify-space-between align-center">
                <div class="text-truncate">
                   <div class="font-weight-medium font-mono text-caption text-cyan-lighten-2">
                      <v-icon start size="x-small" icon="mdi-lock-outline" class="opacity-50 mr-1"></v-icon>
                      {{ tmpl.name }}
                   </div>
                </div>
             </div>
          </div>

          <div class="section-label font-mono text-caption text-amber-darken-3 mb-2 mt-4 px-1">
              USER_PROTOCOLS
          </div>

          <div v-if="filteredUserPrompts.length === 0" class="text-center pa-4 dashed-box opacity-30 font-mono text-caption text-grey">
              NO DATA
          </div>

          <div
            v-for="prompt in filteredUserPrompts"
            :key="prompt.id"
            :class="['prompt-item mb-1', { 'active-item': selectedPromptId === prompt.id }]"
            @click="handleSelectPrompt(prompt)"
          >
             <div class="d-flex justify-space-between align-center">
                <div class="text-truncate">
                   <div class="font-weight-medium font-mono text-caption text-grey-lighten-2">{{ prompt.name }}</div>
                </div>
             </div>
          </div>

        </div>
      </v-col>

      <v-col cols="12" md="6" class="editor-pane border-right-subtle d-flex flex-column relative">

         <div class="pane-header pa-4 d-flex align-center justify-space-between bg-black-glass relative z-10">
            <div class="d-flex align-center">
              <span class="text-subtitle-2 font-weight-bold orbitron-font text-grey-lighten-1 tracking-wider">INJECTION_CORE</span>

              <span v-if="isReadOnly" class="ml-3 text-caption font-mono text-cyan-darken-1">
                 <v-icon start size="x-small" icon="mdi-lock"></v-icon> LOCKED
              </span>
              <span v-else-if="isDirty" class="ml-3 text-caption font-mono text-amber-darken-1">
                 * UNSAVED
              </span>
            </div>

            <div class="d-flex gap-2">
               <v-btn
                  v-if="!isReadOnly && selectedPromptId"
                  variant="text"
                  color="red-darken-1"
                  size="small"
                  class="font-mono"
                  @click="confirmDelete = true"
                >
                  DELETE
                </v-btn>

                <v-btn
                  v-if="!isReadOnly"
                  variant="outlined"
                  color="amber-darken-1"
                  size="small"
                  class="font-mono btn-tactical"
                  :disabled="(!isDirty && !!selectedPromptId) || promptStore.isLoading"
                  :loading="promptStore.isLoading"
                  @click="handleSavePrompt"
                >
                  <v-icon start icon="mdi-content-save-outline" size="small"></v-icon> COMMIT
                </v-btn>

                <v-btn
                  v-if="isReadOnly"
                  variant="outlined"
                  color="cyan-darken-1"
                  size="small"
                  class="font-mono btn-tactical-cyan"
                  @click="handleCloneTemplate"
                >
                  <v-icon start icon="mdi-source-branch" size="small"></v-icon> FORK
                </v-btn>
            </div>
         </div>

         <div class="flex-grow-1 relative pa-4 z-10 d-flex flex-column">
             <div class="d-flex align-center mb-2 font-mono bg-black-transparent px-2 py-1 rounded border-subtle">
                 <span :class="isReadOnly ? 'text-cyan-darken-2' : 'text-amber-darken-4'" class="mr-3 text-caption">NAME:</span>
                 <input
                   v-model="localPrompt.name"
                   type="text"
                   class="terminal-text-input flex-grow-1"
                   :class="isReadOnly ? 'text-cyan-lighten-4' : 'text-white'"
                   :disabled="isReadOnly"
                   placeholder="enter_identifier..."
                 />
             </div>

             <div class="editor-container flex-grow-1 relative border-subtle">
                 <div class="line-numbers font-mono text-grey-darken-3">
                     <div v-for="n in lineCount" :key="n">{{ n }}</div>
                 </div>
                 <textarea
                   ref="editorTextarea"
                   v-model="localPrompt.content"
                   class="code-editor custom-scrollbar font-mono"
                   :class="isReadOnly ? 'read-only-editor' : ''"
                   :placeholder="isReadOnly ? '// SYSTEM LOCKED. CLONE TO EDIT.' : '// Enter instruction... Use {{variable}} for inputs.'"
                   :readonly="isReadOnly"
                   @input="handleContentChange"
                   spellcheck="false"
                 ></textarea>
             </div>
         </div>
      </v-col>

      <v-col cols="12" md="3" class="variables-pane d-flex flex-column bg-deep-black-alt">
         <div class="pane-header pa-4 d-flex align-center bg-black-glass">
            <span class="text-subtitle-2 font-weight-bold orbitron-font text-grey-lighten-1 tracking-wider">VARIABLES</span>
         </div>

         <div class="flex-grow-1 overflow-y-auto custom-scrollbar pa-4 d-flex flex-column">
             <div class="mb-6 relative">
                 <div class="text-caption font-mono text-grey-darken-1 mb-3 border-bottom-subtle">DETECTED INPUTS ({{ extractedVariables.length }})</div>

                 <div v-if="extractedVariables.length === 0" class="text-center pa-4 dashed-box opacity-30">
                    <div class="text-caption font-mono text-grey mt-1">NO VARIABLES</div>
                 </div>

                 <div v-else class="variable-nodes-container">
                     <div v-for="variable in extractedVariables" :key="variable" class="variable-node mb-3">
                         <label class="font-mono text-caption text-grey-lighten-1 mb-1 d-block">{{ variable }}</label>
                         <v-text-field
                           v-model="testVariables[variable]"
                           variant="outlined"
                           density="compact"
                           hide-details
                           bg-color="rgba(255,255,255,0.03)"
                           :color="isReadOnly ? 'cyan-darken-1' : 'amber-darken-1'"
                           class="font-mono terminal-input-field"
                           :placeholder="'Enter value...'"
                         ></v-text-field>
                     </div>
                 </div>
             </div>

             <div class="mb-6">
                 <v-btn
                   block
                   height="48"
                   class="tactical-ops-btn orbitron-font"
                   :class="isReadOnly ? 'tactical-cyan' : 'tactical-amber'"
                   :loading="isTesting"
                   :disabled="!localPrompt.content"
                   @click="handleRunTest"
                   variant="tonal"
                 >
                    <v-icon
                        start
                        :icon="isReadOnly ? 'mdi-play-outline' : 'mdi-flash-outline'"
                        size="small"
                        class="mr-2"
                    ></v-icon>
                    {{ isReadOnly ? 'TEST PROTOCOL' : 'EXECUTE' }}
                 </v-btn>
             </div>

             <div class="simulation-output flex-grow-1 d-flex flex-column">
                 <div class="text-caption font-mono text-grey-darken-1 mb-2 border-bottom-subtle">OUTPUT_LOG</div>
                 <div class="output-console flex-grow-1 custom-scrollbar pa-2 font-mono text-caption">
                     <div v-if="!testResult && !isTesting" class="text-grey-darken-3">Ready to execute...</div>
                     <div v-if="isTesting" class="text-amber-darken-2">Processing...</div>
                     <div v-if="testResult" class="text-grey-lighten-2">
                        <span class="text-green-darken-1">status: 200 OK</span><br/>
                        {{ testResult }}
                     </div>
                 </div>
             </div>
         </div>
      </v-col>
    </v-row>

    <v-dialog v-model="confirmDelete" max-width="400">
      <v-card class="pro-dialog-card">
        <div class="dialog-header">
            <span class="text-subtitle-2 font-weight-bold font-mono text-red-lighten-1">DELETE CONFIRMATION</span>
        </div>
        <v-card-text class="pa-4 pt-4">
            <p class="text-body-2 text-grey-lighten-1 mb-2">
                Are you sure you want to delete this prompt?
            </p>
            <div class="pa-3 bg-black-subtle rounded border-subtle mb-3">
                <div class="text-caption text-grey-darken-1">SELECTED ITEM:</div>
                <div class="font-weight-bold text-white text-truncate">{{ localPrompt.name }}</div>
            </div>
            <p class="text-caption text-grey-darken-1">
                This action cannot be undone.
            </p>
        </v-card-text>
        <v-card-actions class="pa-3 pt-0 justify-end">
          <v-btn
            color="grey-lighten-1"
            variant="text"
            size="small"
            class="font-mono"
            @click="confirmDelete = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="red-accent-2"
            variant="flat"
            size="small"
            class="font-mono font-weight-bold"
            @click="handleDeletePrompt"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue';
import { usePromptsStore } from '@/store/prompts';
import { useUiStore } from '@/store/ui';
import { storeToRefs } from 'pinia';

const promptStore = usePromptsStore();
const uiStore = useUiStore();
const { prompts } = storeToRefs(promptStore);

const searchQuery = ref('');
const selectedPromptId = ref(null);
const isDirty = ref(false);
const confirmDelete = ref(false);
const lineCount = ref(1);
const isReadOnly = ref(false);

const systemTemplates = [
    {
        id: 'sys-seo',
        name: 'SEO_MASTER_AUDIT',
        content: `You are an expert SEO auditor. Analyze the following website content for SEO optimization.\n\nTarget Keyword: {{target_keyword}}\nContent: {{website_content}}\n\nProvide:\n1. Keyword Density Analysis\n2. H1/H2 Tag Suggestions\n3. Meta Description Draft`,
        tags: ['seo', 'system']
    },
    {
        id: 'sys-code',
        name: 'SECURE_CODE_REVIEW',
        content: `Act as a Senior Security Engineer. Review the code snippet below for vulnerabilities (OWASP Top 10).\n\nLanguage: {{language}}\nCode:\n{{source_code}}\n\nOutput Format:\n- Vulnerability Type\n- Severity (High/Med/Low)\n- Fix Suggestion`,
        tags: ['coding', 'security']
    },
    {
        id: 'sys-mail',
        name: 'COLD_EMAIL_GENERATOR',
        content: `Draft a professional cold outreach email.\n\nRecipient Role: {{recipient_role}}\nCompany Name: {{company_name}}\nValue Proposition: {{my_product_value}}\n\nTone: Professional but conversational. Keep it under 150 words.`,
        tags: ['marketing', 'email']
    }
];

const localPrompt = ref({ id: null, name: 'UNTITLED_PROTOCOL', content: '', tags: [] });
const extractedVariables = ref([]);
const testVariables = ref({});
const isTesting = ref(false);
const testResult = ref(null);

const filteredTemplates = computed(() => {
    const q = searchQuery.value.toLowerCase();
    return systemTemplates.filter(p => !q || p.name.toLowerCase().includes(q) || p.content.toLowerCase().includes(q));
});

const filteredUserPrompts = computed(() => {
    const q = searchQuery.value.toLowerCase();
    return prompts.value.filter(p => !q || p.name.toLowerCase().includes(q) || p.content.toLowerCase().includes(q));
});

watch(() => localPrompt.value.content, (val) => {
    if(val) { extractVariables(val); updateLineCount(val); }
});

watch(selectedPromptId, (newId) => {
    if (!newId) { resetLocalPrompt(); return; }

    if (newId.toString().startsWith('sys-')) {
        const tmpl = systemTemplates.find(t => 'sys-'+t.id === newId);
        if (tmpl) {
            localPrompt.value = JSON.parse(JSON.stringify(tmpl));
            isReadOnly.value = true;
            isDirty.value = false;
        }
    } else {
        const p = prompts.value.find(p => p.id === newId);
        if (p) {
            localPrompt.value = JSON.parse(JSON.stringify(p));
            isReadOnly.value = false;
            isDirty.value = false;
        }
    }
    testResult.value = null;
    nextTick(() => {
       if(localPrompt.value.content) {
           extractVariables(localPrompt.value.content);
           updateLineCount(localPrompt.value.content);
       }
    });
});

watch(localPrompt, (newVal) => {
    if (isReadOnly.value) return;
    if (!selectedPromptId.value) {
        isDirty.value = newVal.name !== 'UNTITLED_PROTOCOL' || newVal.content !== '';
        return;
    }
    const original = prompts.value.find(p => p.id === selectedPromptId.value);
    if (original) isDirty.value = JSON.stringify(newVal) !== JSON.stringify(original);
}, { deep: true });

function updateLineCount(c) { lineCount.value = c ? c.split('\n').length : 1; }

function resetLocalPrompt() {
    localPrompt.value = { id: null, name: 'UNTITLED_PROTOCOL', content: '', tags: [] };
    isReadOnly.value = false; isDirty.value = false;
    extractedVariables.value = []; testVariables.value = {}; testResult.value = null; lineCount.value = 1;
}

function handleNewPrompt() { selectedPromptId.value = null; resetLocalPrompt(); }

function handleSelectTemplate(tmpl) { selectedPromptId.value = 'sys-' + tmpl.id; }
function handleSelectPrompt(p) { selectedPromptId.value = p.id; }

function handleContentChange() {}

function handleCloneTemplate() {
    const clonedContent = localPrompt.value.content;
    const clonedName = `COPY_OF_${localPrompt.value.name}`;
    selectedPromptId.value = null;
    isReadOnly.value = false;
    localPrompt.value = { id: null, name: clonedName, content: clonedContent, tags: [] };
    uiStore.showSnackbar('Protocol cloned. You have write access.', 'success');
}

function extractVariables(content) {
    const regex = /\{\{([^}]+)\}\}/g;
    const matches = [...content.matchAll(regex)];
    const unique = [...new Set(matches.map(m => m[1].trim()))];
    const newVars = {};
    unique.forEach(v => newVars[v] = testVariables.value[v] || '');
    extractedVariables.value = unique;
    testVariables.value = newVars;
}

async function handleSavePrompt() {
    if (!localPrompt.value.content.trim()) return;
    const success = await promptStore.savePrompt({ ...localPrompt.value });
    if (success) {
        if (!selectedPromptId.value || selectedPromptId.value.toString().startsWith('sys-')) {
             const created = promptStore.selectedPrompt;
             if(created && created.id) selectedPromptId.value = created.id;
        }
        isDirty.value = false;
    }
}

async function handleDeletePrompt() {
    if (!selectedPromptId.value || isReadOnly.value) return;
    await promptStore.removePrompt(selectedPromptId.value);
    confirmDelete.value = false;
    handleNewPrompt();
}

async function handleRunTest() {
    if (!localPrompt.value.content) return;
    isTesting.value = true;
    testResult.value = null;

    let promptText = localPrompt.value.content;
    extractedVariables.value.forEach(v => {
        promptText = promptText.replace(new RegExp(`\{\{${v}\}\}`, 'g'), testVariables.value[v] || `[${v}]`);
    });

    console.log("Simulating:", promptText);
    setTimeout(() => {
        testResult.value = `SIMULATION COMPLETE.\n\n> Input Processed.\n> Context: ${promptText.substring(0,50)}...\n> Status: OPTIMAL`;
        isTesting.value = false;
    }, 1200);
}

onMounted(() => {
    if(prompts.value.length === 0) promptStore.fetchPrompts();
    if(systemTemplates.length > 0) handleSelectTemplate(systemTemplates[0]);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&display=swap');

/* GLOBAL & LAYOUT */
.bg-deep-black { background-color: #020202; }
.bg-deep-black-alt { background-color: #050505; }
.relative { position: relative; }
.z-10 { z-index: 10; }
.overflow-hidden { overflow: hidden; }

/* ANIMATED BG (SUBTLE) */
.bg-grid-moving {
    position: absolute; top: 0; left: 0; width: 200%; height: 200%;
    background-image: linear-gradient(rgba(255, 255, 255, 0.01) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.01) 1px, transparent 1px);
    background-size: 30px 30px;
    transform: perspective(500px) rotateX(60deg);
    animation: gridMoveSlow 60s linear infinite;
    pointer-events: none; z-index: 0; opacity: 0.3;
}
@keyframes gridMoveSlow { from { transform: perspective(500px) rotateX(60deg) translateY(0); } to { transform: perspective(500px) rotateX(60deg) translateY(60px); } }

.vignette-overlay {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: radial-gradient(circle, transparent 50%, rgba(0,0,0,1) 120%);
    pointer-events: none; z-index: 2;
}

/* TYPOGRAPHY */
.orbitron-font { font-family: 'Orbitron', sans-serif; letter-spacing: 1px; }
.font-mono { font-family: 'Fira Code', monospace; }

/* PANELS */
.library-pane { background: rgba(10, 10, 10, 0.95); }
.bg-black-glass { background: rgba(15, 15, 15, 0.95); border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
.bg-black-transparent { background: rgba(0, 0, 0, 0.3); }
.border-right-subtle { border-right: 1px solid rgba(255, 255, 255, 0.03); }
.border-subtle { border: 1px solid rgba(255, 255, 255, 0.05); }
.border-bottom-subtle { border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
.dashed-box { border: 1px dashed rgba(255,255,255,0.1); border-radius: 4px; }

/* LIST ITEMS */
.prompt-item {
    cursor: pointer; padding: 6px 8px; border-radius: 4px; transition: all 0.2s;
    border: 1px solid transparent;
}
.prompt-item:hover { background: rgba(255, 255, 255, 0.03); }
.active-item { background: rgba(255, 193, 7, 0.05); border-color: rgba(255, 193, 7, 0.2); }
.active-item-sys { background: rgba(0, 229, 255, 0.05); border-color: rgba(0, 229, 255, 0.2); }

/* EDITOR */
.editor-pane { background: rgba(5, 5, 5, 0.95); }
.editor-container { background: rgba(0, 0, 0, 0.5); display: flex; position: relative; border-radius: 2px; overflow: hidden; }
.code-editor { flex-grow: 1; background: transparent; color: #e0e0e0; border: none; resize: none; padding: 16px; outline: none; font-size: 0.9rem; line-height: 1.5; caret-color: #FFC107; }
.read-only-editor { color: #80DEEA; caret-color: transparent; }
.line-numbers { padding: 16px 8px; text-align: right; background: rgba(0, 0, 0, 0.2); border-right: 1px solid rgba(255, 255, 255, 0.03); user-select: none; color: #444; }

/* BUTTONS (TACTICAL STYLE) */
.btn-tactical { border-color: rgba(255, 193, 7, 0.3); background: rgba(255, 193, 7, 0.05) !important; }
.btn-tactical:hover { border-color: #FFC107; background: rgba(255, 193, 7, 0.1) !important; }
.btn-tactical-cyan { border-color: rgba(0, 229, 255, 0.3); background: rgba(0, 229, 255, 0.05) !important; }
.btn-tactical-cyan:hover { border-color: #00E5FF; background: rgba(0, 229, 255, 0.1) !important; }

/* MAIN EXECUTE BUTTON */
.tactical-ops-btn {
    letter-spacing: 1px;
    border-radius: 2px !important;
    transition: all 0.2s;
    background: transparent !important;
    border: 1px solid;
}
.tactical-amber { color: #FFC107 !important; border-color: rgba(255, 193, 7, 0.4) !important; }
.tactical-amber:hover { background: rgba(255, 193, 7, 0.1) !important; border-color: #FFC107 !important; box-shadow: 0 0 15px rgba(255, 193, 7, 0.2); }
.tactical-cyan { color: #00E5FF !important; border-color: rgba(0, 229, 255, 0.4) !important; }
.tactical-cyan:hover { background: rgba(0, 229, 255, 0.1) !important; border-color: #00E5FF !important; box-shadow: 0 0 15px rgba(0, 229, 255, 0.2); }

/* DIALOG (PROFESSIONAL) */
.pro-dialog-card { background: #111 !important; border: 1px solid #333; border-radius: 4px; }
.dialog-header { padding: 16px; border-bottom: 1px solid #222; background: #0a0a0a; }
.bg-black-subtle { background: #080808; }

/* INPUTS */
.terminal-text-input { background: transparent; border: none; outline: none; font-family: 'Fira Code', monospace; font-size: 0.9rem; }
.terminal-input-field :deep(.v-field__outline) { --v-field-border-color: rgba(255, 255, 255, 0.1); }
.terminal-input-field :deep(.v-field__input) { color: white; font-family: 'Fira Code', monospace; font-size: 0.85rem; }

/* SCROLLBAR */
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: rgba(255, 255, 255, 0.1); border-radius: 3px; }
</style>
