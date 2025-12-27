//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai-trainer\DatasetLibrary.vue total lines 302 
//#######################################################################

<template>
  <div class="d-flex flex-row fill-height w-100 overflow-hidden">
    <div class="left-panel d-flex flex-column" style="width: 300px; flex-shrink: 0;">
      <v-toolbar color="transparent" density="compact" class="pl-2">
        <v-toolbar-title class="font-mono text-gold font-weight-bold text-caption ml-2">DATA LIBRARY</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-plus" color="#FFD700" variant="text" @click="openNewDatasetDialog" title="Create New Dataset"></v-btn>
      </v-toolbar>
      <v-divider class="border-gold-subtle"></v-divider>

      <div class="overflow-y-auto flex-grow-1 pa-2 custom-scrollbar">
          <div v-if="isLoadingList" class="text-center py-4">
              <v-progress-circular indeterminate color="#FFD700" size="24"></v-progress-circular>
          </div>
          <div v-else-if="datasetStore.error" class="pa-4 text-center text-red-accent-2 text-caption">
              <v-icon icon="mdi-alert-circle" color="red" class="mb-2"></v-icon><br>
              {{ datasetStore.error }}<br>
              <v-btn size="x-small" variant="text" color="white" @click="datasetStore.fetchDatasets()" class="mt-2">Retry</v-btn>
          </div>
          <v-list bg-color="transparent" density="compact" v-else>
          <v-list-item
              v-for="dataset in datasets"
              :key="dataset.name"
              :title="dataset.name"
              :active="selectedDatasetName === dataset.name"
              @click="datasetStore.selectDataset(dataset.name)"
              active-color="#FFD700"
              class="dataset-list-item text-white mb-1"
              rounded="lg"
          >
              <template v-slot:append>
              <div class="text-caption text-grey mr-2 font-mono" v-if="dataset.count !== undefined">[{{ dataset.count }}]</div>
              <v-btn
                  icon="mdi-delete-outline"
                  variant="text"
                  color="red-darken-2"
                  size="small"
                  @click.stop="handleDeleteDataset(dataset.name)"
              ></v-btn>
              </template>
          </v-list-item>
          </v-list>
      </div>
    </div>

    <div class="right-panel flex-grow-1 d-flex flex-column" style="min-width: 0; position: relative;">
      <div v-if="!selectedDatasetName" class="empty-state d-flex flex-column align-center justify-center h-100">
        <v-icon icon="mdi-database-eye-outline" size="80" color="#FFD700" class="mb-4 opacity-20"></v-icon>
        <h2 class="text-grey-darken-1 font-weight-light font-mono">SELECT A DATASET TO INJECT KNOWLEDGE</h2>
      </div>

      <div v-else class="d-flex flex-column h-100 w-100">
        <div class="d-flex align-center pa-4 pb-0 flex-shrink-0">
            <div class="text-h6 text-white font-weight-bold text-uppercase d-flex align-center font-mono">
              <v-icon start color="#FFD700" class="mr-2">mdi-table</v-icon>
              {{ selectedDatasetName }}
            </div>
            <v-spacer></v-spacer>
            <v-btn
              color="#FFD700"
              variant="outlined"
              class="text-gold font-weight-bold hover-fill-gold font-mono"
              prepend-icon="mdi-plus-box"
              @click="openAddDataDialog"
            >
              Add Entry
            </v-btn>
        </div>

        <v-divider class="mx-4 mt-4 mb-0 border-gold-subtle"></v-divider>

        <div class="flex-grow-1 pa-4 overflow-hidden" style="position: relative;">
            <v-data-table
              :headers="dataTableHeaders"
              :items="selectedDatasetData"
              :loading="isLoadingData"
              class="data-table bg-transparent text-white h-100 font-mono"
              density="comfortable"
              hover
              fixed-header
              style="height: 100%; overflow-y: auto;"
            >
              <template v-slot:item.prompt="{ item }">
                  <div class="text-truncate-2 text-white">
                      {{ getDisplayContent(item, 'user') }}
                  </div>
              </template>
              <template v-slot:item.response="{ item }">
                  <div class="text-truncate-2 text-grey">
                      {{ getDisplayContent(item, 'assistant') }}
                  </div>
              </template>
              <template v-slot:item.actions="{ item }">
                  <div class="d-flex justify-end">
                  <v-btn icon="mdi-pencil" variant="text" color="amber-darken-1" size="small" @click="handleEditRow(item)"></v-btn>
                  <v-btn icon="mdi-delete" variant="text" color="red-darken-2" size="small" @click="handleDeleteRow(item)"></v-btn>
                  </div>
              </template>
            </v-data-table>
        </div>
      </div>
    </div>

    <v-dialog v-model="isAddDataDialogOpen" max-width="800px" persistent>
      <v-card class="gold-panel border-gold-thin">
        <v-toolbar color="transparent" class="border-bottom-gold">
            <v-toolbar-title class="text-gold font-weight-bold font-mono">
                {{ isEditMode ? 'EDIT DATA NODE' : `INJECT DATA NODE` }}
            </v-toolbar-title>
            <v-btn icon="mdi-close" variant="text" color="grey" @click="closeAddDataDialog"></v-btn>
        </v-toolbar>

        <v-card-text class="pa-4">
          <p class="text-grey-lighten-1 mb-2 font-mono text-caption">INPUT SIGNAL (USER)</p>
          <v-textarea
            v-model="newPrompt"
            variant="outlined"
            rows="3"
            color="#FFD700"
            base-color="grey-darken-2"
            class="gold-input mb-4 font-mono text-white"
          ></v-textarea>

          <p class="text-grey-lighten-1 mb-2 font-mono text-caption">EXPECTED OUTPUT (ASSISTANT)</p>
          <v-textarea
            v-model="newResponse"
            variant="outlined"
            rows="5"
            color="#FFD700"
            base-color="grey-darken-2"
            class="gold-input font-mono text-white"
          ></v-textarea>
        </v-card-text>
        <v-card-actions class="pa-4 pt-0">
          <v-spacer></v-spacer>
          <v-btn variant="text" color="grey" @click="closeAddDataDialog">CANCEL</v-btn>
          <v-btn color="#FFD700" variant="flat" @click="handleSaveNewData" class="text-black font-weight-bold">COMMIT</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="isNewDatasetDialogOpen" max-width="500px" persistent>
      <v-card class="gold-panel border-gold-thin">
        <v-card-title class="font-mono text-gold pt-4 pl-4">INITIALIZE DATASET</v-card-title>
        <v-card-text class="pt-4">
          <v-text-field
            v-model="newDatasetName"
            label="Dataset Identifier"
            variant="outlined"
            color="#FFD700"
            base-color="grey-darken-2"
            class="gold-input font-mono text-white"
            autofocus
            @keyup.enter="handleCreateNewDataset"
          ></v-text-field>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" color="grey" @click="isNewDatasetDialogOpen = false">ABORT</v-btn>
          <v-btn color="#FFD700" variant="flat" @click="handleCreateNewDataset" class="text-black font-weight-bold">CREATE</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useDatasetStore } from '@/store/datasets';
import { useUiStore } from '@/store/ui';
import { storeToRefs } from 'pinia';

const datasetStore = useDatasetStore();
const uiStore = useUiStore();

const { datasets, selectedDatasetName, selectedDatasetData, isLoadingList, isLoadingData } = storeToRefs(datasetStore);

const isAddDataDialogOpen = ref(false);
const isNewDatasetDialogOpen = ref(false);
const isEditMode = ref(false);
const editingRowId = ref(null);
const newPrompt = ref('');
const newResponse = ref('');
const newDatasetName = ref('');

const dataTableHeaders = ref([
  { title: 'Prompt', key: 'prompt', sortable: false, width: '40%', class: 'text-gold font-weight-bold text-uppercase' },
  { title: 'Response', key: 'response', sortable: false, width: '45%', class: 'text-gold font-weight-bold text-uppercase' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end', width: '15%', class: 'text-gold font-weight-bold text-uppercase' },
]);

onMounted(async () => {
    await datasetStore.fetchDatasets();
});


function openNewDatasetDialog() {
    newDatasetName.value = '';
    isNewDatasetDialogOpen.value = true;
}

async function handleCreateNewDataset() {
  if (newDatasetName.value && newDatasetName.value.trim()) {
    await datasetStore.createNewDataset(newDatasetName.value.trim());
    isNewDatasetDialogOpen.value = false;
  }
}

async function handleDeleteDataset(name) {
  const confirmed = await uiStore.showConfirmation({
    title: 'Delete Dataset',
    text: `Delete "${name}"? Data will be lost forever.`,
    color: 'error',
    confirmText: 'Delete'
  });

  if (confirmed) {
    await datasetStore.removeDataset(name);
  }
}

function openAddDataDialog() {
    isEditMode.value = false;
    newPrompt.value = '';
    newResponse.value = '';
    isAddDataDialogOpen.value = true;
}

function handleEditRow(item) {
    const actualItem = item.raw || item;
    isEditMode.value = true;
    editingRowId.value = actualItem.id;
    newPrompt.value = actualItem.prompt || (actualItem.messages?.find(m => m.role === 'user')?.content) || '';
    newResponse.value = actualItem.response || (actualItem.messages?.find(m => m.role === 'assistant')?.content) || '';
    isAddDataDialogOpen.value = true;
}

function getDisplayContent(item, role) {
    const actual = item.raw || item;
    if (role === 'user' && actual.prompt) return actual.prompt;
    if (role === 'assistant' && actual.response) return actual.response;
    if (actual.messages) {
        const msg = actual.messages.find(m => m.role === role);
        return msg ? msg.content : '(empty)';
    }
    return '(invalid format)';
}

function closeAddDataDialog() { isAddDataDialogOpen.value = false; }

async function handleSaveNewData() {
    if (!newPrompt.value || !newResponse.value) return;
    if (isEditMode.value) await datasetStore.updateRowInSelectedDataset({ id: editingRowId.value, prompt: newPrompt.value, response: newResponse.value });
    else await datasetStore.addDataToSelectedDataset([{ prompt: newPrompt.value, response: newResponse.value }]);
    closeAddDataDialog();
}

async function handleDeleteRow(item) {
    const rowId = (item.raw || item).id;
    if (!rowId) return;
    const confirmed = await uiStore.showConfirmation({
        title: 'Prune Data',
        text: 'Remove this training node?',
        color: 'warning',
        confirmText: 'Prune'
    });
    if (confirmed) await datasetStore.removeRowFromSelectedDataset(rowId);
}
</script>

<style scoped>
/* Copied styles to ensure consistency without global pollution yet */
.text-gold { color: #FFD700 !important; }
.border-gold-subtle { border-color: rgba(255, 215, 0, 0.1) !important; }
.border-gold-thin { border: 1px solid rgba(255, 215, 0, 0.2) !important; }
.border-bottom-gold { border-bottom: 1px solid rgba(255, 215, 0, 0.15) !important; }
.gold-panel { background: #080808; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; backdrop-filter: blur(5px); }
.left-panel { background-color: rgba(10, 10, 10, 0.98) !important; border-right: 1px solid rgba(255, 255, 255, 0.05) !important; }
.right-panel { background-color: #030303 !important; }
.font-mono { font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important; }
.dataset-list-item:hover { background-color: rgba(255, 215, 0, 0.05); }
.custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #050505; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 215, 0, 0.2); border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #FFD700; }

/* Table Overrides */
.data-table :deep(th) { background-color: #0a0a0a !important; color: #FFD700 !important; font-family: 'JetBrains Mono', monospace; letter-spacing: 1px; }
.data-table :deep(td) { border-bottom: 1px solid rgba(255,255,255,0.05) !important; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }
.data-table :deep(tr:hover) { background-color: rgba(255, 215, 0, 0.05) !important; }
.hover-fill-gold:hover { background-color: #FFD700 !important; color: #000 !important; }

/* Inputs */
.gold-input :deep(.v-field) { background-color: rgba(20,20,20,0.5) !important; border-color: rgba(255,255,255,0.1); font-family: 'JetBrains Mono', monospace; }
.gold-input :deep(.v-field--focused) { border-color: #FFD700 !important; box-shadow: 0 0 5px rgba(255, 215, 0, 0.2); }
</style>
