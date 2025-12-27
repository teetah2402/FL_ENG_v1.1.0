//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\AuthorizeEngine.vue total lines 123 
//#######################################################################

<template>
  <div class="auth-page d-flex align-center justify-center">
    <v-card class="auth-card pa-6 text-center" max-width="500">
      <div v-if="step === 'loading'">
        <v-progress-circular indeterminate color="cyan" size="64"></v-progress-circular>
        <p class="mt-4 text-grey-lighten-1">Verifying your session...</p>
      </div>

      <div v-if="step === 'login_required'">
        <h2 class="orbitron-font mb-3">Authentication Required</h2>
        <p class="text-grey-lighten-1 mb-6">To link your Flowork Engine, you need to be logged into your account.</p>
        <v-btn color="cyan" @click="goToLogin" size="large" class="action-btn">
          Login to Continue
        </v-btn>
      </div>

      <div v-if="step === 'selection'">
        <h2 class="orbitron-font mb-3">Authorize Engine</h2>
        <p class="text-grey-lighten-1 mb-6">Select which of your registered engines you want to connect:</p>
        <v-list bg-color="transparent" density="compact">
          <v-list-item
            v-for="engine in engineStore.engines"
            :key="engine.id"
            class="engine-list-item"
            @click="selectEngine(engine.id)"
          >
            <template v-slot:prepend>
              <v-icon icon="mdi-server"></v-icon>
            </template>
            <v-list-item-title class="font-weight-bold">{{ engine.name }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </div>

      <div v-if="step === 'success'">
        <v-icon icon="mdi-check-circle-outline" color="success" size="64"></v-icon>
        <h3 class="mt-4 orbitron-font text-success">Authorization Complete!</h3>
        <p class="text-grey-lighten-1">Your Core Engine has been linked. This window will now close.</p>
      </div>

      <div v-if="step === 'error'">
        <v-icon icon="mdi-alert-circle-outline" color="error" size="64"></v-icon>
        <h3 class="mt-4 orbitron-font text-error">An Error Occurred</h3>
        <p class="text-grey-lighten-1">{{ errorMessage }}</p>
      </div>

    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useEngineStore } from '@/store/engines';
import { useAuthStore } from '@/store/auth';
import { apiSelectEngineForAuth } from '@/api';

const route = useRoute();
const router = useRouter();
const engineStore = useEngineStore();
const authStore = useAuthStore();

const step = ref('loading');
const errorMessage = ref('');
const requestId = ref(null);

function goToLogin() {
    router.push({ name: 'Login', query: { redirect: route.fullPath } });
}

async function selectEngine(engineId) {
    step.value = 'loading';
    try {
        const response = await apiSelectEngineForAuth(requestId.value, engineId);
        if (response.status === 'success') {
            step.value = 'success';
            setTimeout(() => window.close(), 3000);
        } else {
            throw new Error(response.message || 'Failed to select engine.');
        }
    } catch (error) {
        errorMessage.value = error.error || 'Could not complete authorization.';
        step.value = 'error';
    }
}

onMounted(async () => {
    requestId.value = route.query.req_id;
    if (!requestId.value) {
        errorMessage.value = 'Request ID is missing from the URL.';
        step.value = 'error';
        return;
    }

    if (!authStore.isAuthenticated) {
        step.value = 'login_required';
        return;
    }

    await engineStore.fetchEngines();
    if (engineStore.error) {
        errorMessage.value = 'Could not load your engines.';
        step.value = 'error';
    } else {
        step.value = 'selection';
    }
});
</script>

<style scoped>
.auth-page { height: 100vh; background: radial-gradient(circle, #161625 0%, #0A0F1E 100%); }
.auth-card { background: rgba(23, 33, 65, 0.85); backdrop-filter: blur(10px); border: 1px solid var(--neon-cyan); }
.orbitron-font { font-family: 'Orbitron', monospace; }
.engine-list-item { cursor: pointer; border: 1px solid transparent; border-radius: 8px; }
.engine-list-item:hover { background-color: rgba(0, 245, 255, 0.1); border-color: rgba(0, 245, 255, 0.3); }
.action-btn { font-weight: bold; }
</style>
