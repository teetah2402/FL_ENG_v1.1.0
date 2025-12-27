//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\NeuralIngestor.vue total lines 295 
//#######################################################################

<template>
  <v-container fluid class="fill-height bg-deep pa-0">
    <div class="neural-ambient-fx"></div>

    <div class="d-flex flex-column w-100 h-100 z-5">

      <div class="d-flex align-center pa-6 border-gold-thin bg-glass-dark">
        <div class="d-flex align-center">
            <v-icon color="#FFD700" size="44" class="mr-4 glow-icon-gold animate-soft-pulse">mdi-brain-sync</v-icon>
            <div>
              <div class="text-h4 font-weight-black text-white orbitron-font tracking-tighter uppercase">Neural<span class="text-gold-subtle">Ingestor</span></div>
              <div class="text-caption text-grey font-mono letter-spacing-2">FLOWORK DATA FACTORY • MULTI-THREAD DISTILLERY</div>
            </div>
        </div>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-close" color="white" variant="text" to="/ai-trainer" size="large"></v-btn>
      </div>

      <div class="d-flex flex-grow-1 overflow-hidden">

        <div class="sidebar-area pa-6 border-r-elegant custom-scrollbar">
          <div class="text-overline text-gold mb-4 opacity-40 letter-spacing-3 font-orbitron">1. TARGET ACQUISITION</div>

          <v-card class="neo-glass-card mb-6" border="thin gold-muted">
            <div class="pa-6 text-center scanner-zone" @click="triggerFolderScan">
              <input type="file" ref="folderInput" webkitdirectory directory multiple style="display: none" @change="handleFolderSelect" />
              <v-icon size="64" :color="files.length > 0 ? '#00E676' : '#FFD700'" class="mb-3">
                {{ files.length > 0 ? 'mdi-folder-check' : 'mdi-folder-plus-outline' }}
              </v-icon>
              <div v-if="files.length === 0" class="text-white font-mono text-body-2">SCAN REPOSITORY</div>
              <div v-else class="text-green-accent-3 font-mono text-h6">{{ files.length }} FILES LOCKED</div>
            </div>
          </v-card>

          <div class="text-overline text-gold mb-2 opacity-40 letter-spacing-3 font-orbitron">2. ASSIGN TEACHER SQUAD</div>
          <v-card class="neo-glass-card pa-4 mb-8">
             <v-select
                v-model="selectedTeachers"
                :items="readyModels"
                item-title="name"
                item-value="id"
                label="Hire AI Distillers"
                variant="outlined"
                multiple
                chips
                color="#FFD700"
                base-color="white"
                class="gold-select font-mono"
              ></v-select>
              <div class="text-caption text-grey-darken-2 font-mono mt-2">Maximum speed: 1 teacher per chunk.</div>
          </v-card>

          <v-btn
            block
            color="#FFD700"
            height="70"
            class="text-black font-weight-black orbitron-font glow-gold-btn"
            :loading="ingestorStore.isDistilling"
            :disabled="selectedTeachers.length === 0 || files.length === 0"
            @click="startParallelProcessing"
          >
            <v-icon start size="large">mdi-flash</v-icon> IGNITE ENGINE
          </v-btn>
        </div>

        <div class="flex-grow-1 d-flex flex-column pa-6 bg-terminal-dark">

          <v-expand-transition>
            <div v-if="ingestorStore.isDistilling" class="neo-glass-card pa-8 mb-6 slide-up-fx">
                <div class="d-flex align-center justify-space-between mb-4">
                  <div class="text-h5 text-white font-mono uppercase tracking-widest">Neural Threads: <span class="text-gold">{{ selectedTeachers.length }}</span></div>
                  <div class="text-h4 text-gold font-mono">{{ progressPercent }}%</div>
                </div>
                <v-progress-linear :model-value="progressPercent" color="#FFD700" height="10" rounded striped indeterminate></v-progress-linear>
                <div class="mt-4 d-flex align-center">
                    <v-icon color="#FFD700" size="18" class="mr-2 spin-fx">mdi-loading</v-icon>
                    <div class="text-caption text-grey font-mono uppercase tracking-wide">{{ currentLog }}</div>
                </div>
            </div>
          </v-expand-transition>

          <v-card class="neo-glass-card flex-grow-1 d-flex flex-column overflow-hidden border-gold-muted">
             <div class="pa-4 border-b-elegant d-flex align-center bg-terminal-header">
                <v-icon color="#FFD700" size="small" class="mr-2">mdi-code-json</v-icon>
                <span class="text-caption text-gold font-mono tracking-widest uppercase">knowledge_distillation_stream</span>
                <v-spacer></v-spacer>
                <div v-if="distilledData.length" class="text-caption text-green font-mono font-weight-bold">
                    [ {{ distilledData.length }} NODES EXTRACTED ]
                </div>
             </div>

             <div class="flex-grow-1 pa-4 bg-terminal-inner custom-scrollbar overflow-auto">
                <pre v-if="distilledData.length" class="json-code font-mono">{{ formattedJson }}</pre>
                <div v-else-if="!ingestorStore.isDistilling" class="d-flex flex-column align-center justify-center h-100 opacity-20">
                    <v-icon size="100" color="#FFD700" class="mb-4">mdi-database-clock-outline</v-icon>
                    <div class="text-h5 text-white font-mono tracking-widest">AWAITING_SIGNAL</div>
                </div>
             </div>

             <div v-if="distilledData.length && !ingestorStore.isDistilling" class="pa-6 bg-glass-bottom d-flex align-center fade-in-fx">
                <v-btn variant="text" color="grey-darken-1" class="font-mono mr-6" @click="resetEngine">PURGE BUFFER</v-btn>
                <v-spacer></v-spacer>
                <v-select
                    v-model="targetDataset"
                    :items="datasets.map(d => d.name)"
                    label="Inject to Dataset Library"
                    variant="outlined"
                    density="compact"
                    hide-details
                    class="mr-4 gold-select-mini"
                ></v-select>
                <v-btn color="green-accent-4" variant="flat" class="text-black font-weight-black px-12" height="44" @click="commitToEliteDB">
                    INJECT TO SQL ELITE
                </v-btn>
             </div>
          </v-card>
        </div>

      </div>
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useNeuralIngestorStore } from '@/store/neuralIngestor';
import { useAiCenterStore } from '@/store/aiCenter';
import { useDatasetStore } from '@/store/datasets';
import { useUiStore } from '@/store/ui';
import { storeToRefs } from 'pinia';

const ingestorStore = useNeuralIngestorStore();
const aiStore = useAiCenterStore();
const datasetStore = useDatasetStore();
const uiStore = useUiStore();

const { readyModels } = storeToRefs(aiStore);
const { datasets } = storeToRefs(datasetStore);

const folderInput = ref(null);
const files = ref([]);
const selectedTeachers = ref([]);
const targetDataset = ref(null);
const distilledData = ref([]);

const currentLog = ref('STANDBY');
const progressPercent = ref(0);

const formattedJson = computed(() => JSON.stringify(distilledData.value, null, 2));

onMounted(async () => {
  await aiStore.fetchAiStatus();
  await datasetStore.fetchDatasets();
});

function triggerFolderScan() { folderInput.value.click(); }

function handleFolderSelect(event) {
  const selected = Array.from(event.target.files);
  files.value = selected.filter(f => /\.(txt|md|json|py|js|html|docx|pdf)$/i.test(f.name));
}

async function startParallelProcessing() {
  ingestorStore.isDistilling = true;
  distilledData.value = [];
  progressPercent.value = 0;

  const allChunks = [];
  currentLog.value = "FRAGMENTING DATA REPOSITORY...";

  for (const file of files.value) {
    const content = await readFileContent(file);
    const lines = content.split('\n');
    const chunkSize = 1000;
    for (let j = 0; j < lines.length; j += chunkSize) {
      allChunks.push({
        name: `${file.name} (Ch ${Math.floor(j/chunkSize) + 1})`,
        text: lines.slice(j, j + chunkSize).join('\n')
      });
    }
  }

  const total = allChunks.length;
  let finished = 0;
  const numTeachers = selectedTeachers.value.length;

  const dispatchTasks = async () => {
    const pool = [];
    const maxConcurrent = 6;

    for (let i = 0; i < allChunks.length; i++) {
        const chunk = allChunks[i];
        const teacherId = selectedTeachers.value[i % numTeachers];

        const p = (async () => {
            try {
                currentLog.value = `Teacher [${teacherId}] distilling: ${chunk.name}`;
                const result = await ingestorStore.distillChunk(chunk.text, teacherId);
                if (Array.isArray(result)) {
                    distilledData.value.push(...result);
                }
                finished++;
                progressPercent.value = Math.round((finished / total) * 100);
            } catch (err) {
                console.error(`Thread error for teacher ${teacherId}:`, err);
            }
        })();

        pool.push(p);

        if (pool.length >= maxConcurrent) {
            await Promise.race(pool);
            pool.splice(pool.findIndex(task => task.status === 'fulfilled'), 1);
        }
    }
    await Promise.all(pool);
  };

  try {
    await dispatchTasks();
    uiStore.showNotification({ text: "Neural Ingestion Complete!", color: "success" });
  } catch (e) {
    uiStore.showNotification({ text: "Engine Interrupted.", color: "error" });
  } finally {
    ingestorStore.isDistilling = false;
    currentLog.value = "IDLE";
  }
}

async function readFileContent(file) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.readAsText(file);
  });
}

async function commitToEliteDB() {
  if (!targetDataset.value) return;
  const success = await datasetStore.addDataToSelectedDataset(distilledData.value, targetDataset.value);
  if (success) {
    uiStore.showNotification({ text: "Knowledge injected to SQL Elite!", color: "success" });
    distilledData.value = [];
  }
}

function resetEngine() {
  files.value = [];
  distilledData.value = [];
  progressPercent.value = 0;
}
</script>

<style scoped>
.bg-deep { background-color: #000; position: relative; }
.neural-ambient-fx {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(circle at 70% 30%, rgba(255, 215, 0, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 20% 80%, rgba(0, 245, 255, 0.02) 0%, transparent 40%);
}

.sidebar-area { width: 380px; background: rgba(5, 5, 8, 0.95); z-index: 10; }
.bg-terminal-dark { background: #010101; }
.border-gold-thin { border-bottom: 1px solid rgba(255, 215, 0, 0.1) !important; }
.border-r-elegant { border-right: 1px solid rgba(255, 215, 0, 0.1) !important; }
.border-b-elegant { border-bottom: 1px solid rgba(255, 215, 0, 0.1) !important; }
.border-gold-muted { border: 1px solid rgba(255, 215, 0, 0.15) !important; }

.neo-glass-card { background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(25px); border-radius: 4px; }
.bg-glass-dark { background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(15px); }
.text-gold-subtle { color: rgba(255, 215, 0, 0.4); font-weight: 200; }
.bg-terminal-inner { background: #000; }
.json-code { color: #00FF9C; font-size: 0.85rem; line-height: 1.6; white-space: pre-wrap; }

.scanner-zone { cursor: pointer; transition: 0.3s; border: 2px dashed rgba(255,215,0,0.15); }
.scanner-zone:hover { background: rgba(255, 215, 0, 0.05); border-color: #FFD700; }

.orbitron-font { font-family: 'Orbitron', sans-serif !important; }
.glow-icon-gold { filter: drop-shadow(0 0 15px rgba(255, 215, 0, 0.3)); }
.animate-soft-pulse { animation: softPulse 3s infinite ease-in-out; }
@keyframes softPulse { 0%, 100% { transform: scale(1); opacity: 0.7; } 50% { transform: scale(1.05); opacity: 1; } }

.glow-gold-btn { box-shadow: 0 0 20px rgba(255, 215, 0, 0.1); }
.custom-scrollbar::-webkit-scrollbar { width: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 215, 0, 0.2); border-radius: 10px; }

.gold-select :deep(.v-field) { background: rgba(255, 255, 255, 0.02) !important; }
.gold-select-mini :deep(.v-field) { background: rgba(255, 255, 255, 0.05) !important; color: white !important; font-family: monospace; }
</style>
