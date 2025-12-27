//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\RegisterView.vue total lines 120 
//#######################################################################

<template>
  <AuthLayout
    title="CREATE NEW IDENTITY"
    switchText="Already have an identity? Import it"
    switchLink="/login"
  >
    <template #form-fields>
      <div class="text-center pa-4">
        <p class="text-grey-lighten-1 mb-6">
          Flowork uses a self-sovereign identity system. We will generate a unique cryptographic key for you. You are the only one who controls this key.
        </p>
        <p class="text-caption text-red-lighten-1">
          <strong>Warning: We CANNOT recover your account if you lose your key.</strong>
        </p>
      </div>

      </template>
    <template #actions>
      <v-btn
        color="cyan"
        large
        block
        @click="handleRegister"
        :loading="authStore.isLoading"
        class="neon-submit-btn"
      >
        Generate Secure Identity
      </v-btn>
    </template>
  </AuthLayout>

  <v-dialog v-model="authStore.isMnemonicDialogVisible" persistent max-width="700px">
    <v-card class="mnemonic-dialog">
      <v-card-title class="orbitron-font d-flex align-center text-h5">
        <v-icon color="warning" start size="large" icon="mdi-alert-octagon-outline"></v-icon>
        CRITICAL: Back Up Your Recovery Phrase
      </v-card-title>
      <v-card-text class="pa-5">
        <p class="text-body-1 text-grey-lighten-1 mb-4">
          This is your <strong>12-word recovery phrase (Mnemonic)</strong>. It is the ONLY way to recover your identity if you lose access to this device.
        </p>
        <p class="text-body-2 text-warning-lighten-1 mb-4">
          <strong>Write down or store these words in a safe and secret place. Do not save it as a screenshot or a plain text file on your computer.</strong>
        </p>
        <v-sheet class="mnemonic-sheet pa-4 text-center">
          <h3 class="text-h5 orbitron-font">{{ authStore.newMnemonic }}</h3>
        </v-sheet>
        <v-checkbox
          v-model="backupConfirmed"
          color="cyan"
          class="mt-6"
        >
          <template v-slot:label>
            <div class="text-body-2">I have securely written down and stored my recovery phrase. I understand that Flowork cannot help me recover my account if I lose it.</div>
          </template>
        </v-checkbox>
      </v-card-text>
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn
          color="cyan"
          variant="flat"
          size="large"
          @click="confirmBackup"
          :disabled="!backupConfirmed"
          class="neon-submit-btn"
          block
        >
          I Have Saved My Phrase, Create My Identity
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import AuthLayout from '@/components/AuthLayout.vue';

const authStore = useAuthStore();
const backupConfirmed = ref(false);

const handleRegister = async () => {
  await authStore.createNewIdentity();
};

const confirmBackup = async () => {
  const success = await authStore.handleBackupConfirmation();
  if (success) {
      console.log("[RegisterView] Backup confirmed. Triggering login success handler...");
      await authStore.handleLoginSuccess();
  }
}
</script>

<style scoped>
.mnemonic-dialog {
  background-color: #2a2a4a;
  border: 2px solid #ffeb3b;
  box-shadow: 0 0 30px rgba(255, 235, 59, 0.5);
}
.mnemonic-sheet {
  background-color: rgba(47, 129, 26, 0.3);
  border: 1px dashed #ffeb3b;
  color: #f0f0f0;
  letter-spacing: 2px;
  word-spacing: 8px;
}
.neon-submit-btn {
  min-height: 52px;
  font-size: 1rem;
}
</style>
