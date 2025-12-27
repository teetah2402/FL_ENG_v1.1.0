//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\VariableManagerDialog.vue total lines 199 
//#######################################################################

<template>
  <v-dialog v-model="dialog" fullscreen transition="dialog-bottom-transition">
    <v-card theme="dark" style="background: #000;">
      <v-toolbar color="#050505" height="80" class="border-b-gold">
        <v-btn icon="mdi-safe" color="#FFD700" variant="text" class="ml-2"></v-btn>
        <v-toolbar-title class="text-h6 font-weight-black" style="letter-spacing: 2px;">
          VAULT <span style="color: #FFD700;">MANAGER</span>
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-close" color="#FFD700" @click="closeDialog" variant="outlined" class="mr-4"></v-btn>
      </v-toolbar>

      <v-card-text class="pa-8 custom-scrollbar">
        <v-container style="max-width: 1100px;">
          <div v-if="isLoading" class="text-center py-12">
            <v-progress-circular indeterminate color="#FFD700" size="50"></v-progress-circular>
            <div class="mt-4 text-gold blink text-caption">NEURAL SYNC: D1 CLOUD -> LOCAL ENGINE...</div>
          </div>

          <div v-else>
            <transition-group name="list">
              <v-sheet v-for="(item, index) in localVariables" :key="item.name || index"
                color="#0a0a0a" class="pa-6 mb-4 rounded-lg border-gold-left position-relative">

                <v-row align="center">
                  <v-col cols="12" md="5">
                    <v-text-field
                      v-model="item.name"
                      label="KEY NAME"
                      variant="outlined"
                      color="#FFD700"
                      density="comfortable"
                      class="font-mono"
                      :readonly="item.is_protected"
                      hide-details
                      prepend-inner-icon="mdi-key-variant"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="3">
                    <v-select
                      v-model="item.mode"
                      :items="['single', 'random', 'sequential']"
                      label="MODE"
                      variant="outlined"
                      color="#FFD700"
                      density="comfortable"
                      hide-details
                    ></v-select>
                  </v-col>
                  <v-col cols="12" md="4" class="d-flex align-center justify-end">
                    <v-tooltip text="Hide secret value">
                        <template v-slot:activator="{ props }">
                            <v-checkbox v-bind="props" v-model="item.is_secret" color="amber" label="SECRET" hide-details class="mr-4"></v-checkbox>
                        </template>
                    </v-tooltip>
                    <v-switch v-model="item.is_enabled" color="#FFD700" label="ACTIVE" hide-details class="mr-4"></v-switch>
                    <v-btn icon="mdi-delete" color="red-accent-2" variant="text" :disabled="item.is_protected" @click="removeEntry(index)"></v-btn>
                  </v-col>
                </v-row>

                <v-row class="mt-2">
                  <v-col cols="12">
                    <v-text-field
                      v-if="item.mode === 'single'"
                      v-model="item.valueDisplay"
                      label="VAULT VALUE"
                      variant="outlined"
                      bg-color="#000"
                      color="#FFD700"
                      :type="item.is_secret && !item.showRaw ? 'password' : 'text'"
                      class="font-mono text-white vault-textarea"
                      hide-details
                    >
                        <template v-slot:append-inner>
                            <v-btn v-if="item.is_secret" icon size="small" variant="text" color="grey" @click="item.showRaw = !item.showRaw">
                                <v-icon>{{ item.showRaw ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                            </v-btn>
                        </template>
                    </v-text-field>

                    <v-textarea
                      v-else
                      v-model="item.valueDisplay"
                      label="LIST (One per line)"
                      variant="outlined"
                      bg-color="#000"
                      color="#FFD700"
                      rows="2"
                      auto-grow
                      class="font-mono text-white vault-textarea"
                      hide-details
                    ></v-textarea>

                    </v-col>
                </v-row>
              </v-sheet>
            </transition-group>

            <v-btn block variant="dashed" color="#FFD700" class="mt-6 py-6" @click="addNew">
              <v-icon start>mdi-plus-circle</v-icon> ADD NEW VAULT ENTRY
            </v-btn>
          </div>
        </v-container>
      </v-card-text>

      <v-divider></v-divider>
      <v-card-actions class="pa-6" style="background: #050505;">
        <v-spacer></v-spacer>
        <v-btn color="grey" variant="text" @click="closeDialog" class="px-6">Cancel</v-btn>
        <v-btn color="#FFD700" theme="light" variant="flat" :loading="isSaving" @click="saveAll" class="px-10 font-weight-black rounded-lg text-black">
          <v-icon start>mdi-cloud-sync</v-icon> SYNC ALL VAULTS
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useVariablesStore } from '@/store/variables';
import { useUiStore } from '@/store/ui';
import { storeToRefs } from 'pinia';

const props = defineProps({ modelValue: Boolean });
const emit = defineEmits(['update:modelValue']);

const store = useVariablesStore();
const ui = useUiStore();
const { variables, isLoading } = storeToRefs(store);
const localVariables = ref([]);
const isSaving = ref(false);

const dialog = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
});

watch(dialog, (open) => { if (open) store.fetchVariables(); });

watch(variables, (newVal) => {
  localVariables.value = newVal.map(v => ({
    ...v,
    valueDisplay: Array.isArray(v.value) ? v.value.join('\n') : String(v.value || ''),
    mode: v.mode || 'single',
    showRaw: false
  }));
}, { deep: true });

function addNew() {
  localVariables.value.push({ name: '', valueDisplay: '', mode: 'single', is_enabled: true, is_secret: true, showRaw: false });
}

function removeEntry(idx) { localVariables.value.splice(idx, 1); }

async function saveAll() {
  isSaving.value = true;
  try {
    const currentNames = localVariables.value.map(l => l.name);
    for (const v of variables.value) {
      if (!currentNames.includes(v.name)) await store.removeVariable(v.name);
    }

    for (const item of localVariables.value) {
      if (!item.name) continue;
      const finalVal = (item.mode === 'random' || item.mode === 'sequential')
        ? item.valueDisplay.split('\n').filter(s => s.trim() !== '')
        : item.valueDisplay;

      await store.saveVariable(item.name, { ...item, value: finalVal });
    }
    ui.showNotification({ text: "Success: Cloud and Local Engine Synced!", color: "success" });
    closeDialog();
  } catch (e) {
    ui.showNotification({ text: "Sync Failed: " + e.message, color: "error" });
  } finally {
    isSaving.value = false;
  }
}

function closeDialog() { emit('update:modelValue', false); }
</script>

<style scoped>
.border-b-gold { border-bottom: 1px solid rgba(255, 215, 0, 0.3) !important; }
.border-gold-left { border-left: 4px solid #FFD700 !important; }
.text-gold { color: #FFD700 !important; }
.blink { animation: blink-ani 1.5s infinite; }
@keyframes blink-ani { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.list-enter-active, .list-leave-active { transition: all 0.5s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateX(30px); }
/* Custom CSS to force contrast on textarea input text */
.vault-textarea :deep(.v-field__input) { color: #fff !important; }
</style>
