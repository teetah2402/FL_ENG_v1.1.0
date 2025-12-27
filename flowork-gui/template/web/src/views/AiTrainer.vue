//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\AiTrainer.vue total lines 117 
//#######################################################################

<template>
  <div class="ai-trainer-page">
    <div class="trainer-header d-flex align-center px-4 py-2 border-bottom-gold">
        <div class="d-flex align-center">
            <v-icon color="#FFD700" size="large" class="mr-3 beat-icon">mdi-brain</v-icon>
            <div>
                <div class="text-subtitle-2 font-weight-bold text-gold font-mono tracking-wide">NEURAL TRAINING CENTER</div>
                <div class="text-caption text-grey-darken-1 font-mono">FLOWORK ENGINE: {{ trainingStore.activeEngineId || 'LOCAL' }}</div>
            </div>
        </div>
        <v-spacer></v-spacer>
        <div class="d-flex align-center gap-4">
            <div class="status-indicator d-flex align-center mr-4">
                <span class="text-caption text-grey mr-2 font-mono">GPU STATUS:</span>
                <v-icon size="x-small" color="green-accent-3" class="mr-1">mdi-circle</v-icon>
                <span class="text-caption text-green-accent-3 font-mono">ONLINE</span>
            </div>
        </div>
    </div>

    <v-tabs v-model="activeTab" bg-color="transparent" color="#FFD700" grow class="text-white flex-shrink-0 border-bottom-gold">
      <v-tab value="datasets" class="text-grey-lighten-1 font-weight-bold font-mono tracking-wide">
        <v-icon start>mdi-database-edit-outline</v-icon>
        DATASETS
      </v-tab>
      <v-tab value="training" class="text-grey-lighten-1 font-weight-bold font-mono tracking-wide">
        <v-icon start>mdi-school-outline</v-icon>
        TRAINING
      </v-tab>
      <v-tab value="monitor" class="text-grey-lighten-1 font-weight-bold font-mono tracking-wide">
        <v-icon start>mdi-monitor-dashboard</v-icon>
        MONITOR
      </v-tab>
      <v-tab value="colosseum" class="text-grey-lighten-1 font-weight-bold font-mono tracking-wide">
        <v-icon start>mdi-sword-cross</v-icon>
        COLOSSEUM
      </v-tab>
      <v-tab value="factory" class="text-grey-lighten-1 font-weight-bold font-mono tracking-wide">
        <v-icon start>mdi-factory</v-icon>
        FACTORY
      </v-tab>
    </v-tabs>

    <v-window v-model="activeTab" class="fill-height flex-grow-1" style="overflow: hidden;">

      <v-window-item value="datasets" class="fill-height">
        <DatasetLibrary />
      </v-window-item>

      <v-window-item value="training" class="fill-height scroll-y">
        <TrainingConfig @training-started="switchToMonitor" />
      </v-window-item>

      <v-window-item value="monitor" class="fill-height">
        <JobMonitor />
      </v-window-item>

      <v-window-item value="colosseum" class="fill-height">
        <BattleArena />
      </v-window-item>

      <v-window-item value="factory" class="fill-height scroll-y">
        <ModelFactory @conversion-started="switchToMonitor" />
      </v-window-item>

    </v-window>
  </div>
</template>

<script setup>
import { ref, defineAsyncComponent } from 'vue';
import { useTrainingStore } from '@/store/training';
import { useUiStore } from '@/store/ui';

const DatasetLibrary = defineAsyncComponent(() => import('@/components/ai-trainer/DatasetLibrary.vue'));
const TrainingConfig = defineAsyncComponent(() => import('@/components/ai-trainer/TrainingConfig.vue'));
const JobMonitor = defineAsyncComponent(() => import('@/components/ai-trainer/JobMonitor.vue'));
const BattleArena = defineAsyncComponent(() => import('@/components/ai-trainer/BattleArena.vue'));
const ModelFactory = defineAsyncComponent(() => import('@/components/ai-trainer/ModelFactory.vue'));

const trainingStore = useTrainingStore();
const uiStore = useUiStore();
const activeTab = ref('datasets');

function switchToMonitor() {
    activeTab.value = 'monitor';
    uiStore.showNotification({
        text: "Training Protocol Initiated. Monitoring Vital Signs.",
        color: "success",
        timeout: 3000
    });
}
</script>

<style scoped>
/* CYBERPUNK THEME ENGINE (Container Only) */
.ai-trainer-page { height: 100%; display: flex; flex-direction: column; background-color: #000; color: #ffffff; font-family: 'Inter', sans-serif; }
.text-gold { color: #FFD700 !important; }
.border-bottom-gold { border-bottom: 1px solid rgba(255, 215, 0, 0.15) !important; }
.font-mono { font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important; }
.tracking-wide { letter-spacing: 1.5px; }
.beat-icon { animation: beat 2s infinite ease-in-out; }

/* Scrollbars Global for this view */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #050505; }
::-webkit-scrollbar-thumb { background: rgba(255, 215, 0, 0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #FFD700; }

@keyframes beat { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.1); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
</style>
