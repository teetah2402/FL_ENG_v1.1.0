//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\ContactUs.vue total lines 197 
//#######################################################################

<template>
  <v-main>
    <div class="legal-page">
      <DigitalFingerprintBackground />

      <v-container class="page-content-container">
        <v-row justify="center">
          <v-col cols="12" md="8" lg="6">
            <v-card class="article-card-content">
              <v-card-title class="headline text-center orbitron-font">Contact Us</v-card-title>
              <v-card-text class="pa-6">
                <p class="text-center text-grey-lighten-1 mb-8">
                  Have a question, feedback, or need support? Fill out the form below and our team will get back to you as soon as possible.
                </p>

                <div v-if="formStatus === 'success'" class="text-center">
                    <v-icon icon="mdi-check-circle-outline" color="success" size="64"></v-icon>
                    <h3 class="mt-4">Thank you!</h3>
                    <p>Your message has been sent successfully. We'll be in touch shortly.</p>
                </div>

                <v-form v-else @submit.prevent="handleSubmit">
                  <v-text-field
                    v-model="form.name"
                    label="Full Name"
                    variant="outlined"
                    class="mb-4"
                    :rules="[rules.required]"
                  ></v-text-field>
                  <v-text-field
                    v-model="form.email"
                    label="Email Address"
                    type="email"
                    variant="outlined"
                    class="mb-4"
                    :rules="[rules.required, rules.email]"
                  ></v-text-field>
                  <v-text-field
                    v-model="form.subject"
                    label="Subject"
                    variant="outlined"
                    class="mb-4"
                    :rules="[rules.required]"
                  ></v-text-field>
                  <v-textarea
                    v-model="form.message"
                    label="Your Message"
                    variant="outlined"
                    rows="5"
                    class="mb-4"
                    :rules="[rules.required]"
                  ></v-textarea>

                  <div class="captcha-wrapper">
                    <span class="captcha-question">To prevent spam, please answer: {{ num1 }} + {{ num2 }} = ?</span>
                    <v-text-field
                      v-model="form.captcha"
                      label="Answer"
                      variant="outlined"
                      density="compact"
                      class="captcha-input"
                      :rules="[rules.required]"
                      required
                    ></v-text-field>
                  </div>

                  <v-alert v-if="formStatus === 'error'" type="error" density="compact" class="mt-4" variant="tonal">
                    {{ errorMessage }}
                  </v-alert>

                  <v-btn
                    type="submit"
                    block
                    size="large"
                    color="cyan"
                    class="mt-6 action-btn"
                    :loading="formStatus === 'sending'"
                  >
                    Send Message
                  </v-btn>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </v-main>
  <LanderFooter />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import LanderFooter from '@/components/LanderFooter.vue';
import DigitalFingerprintBackground from '@/components/DigitalFingerprintBackground.vue';

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: '',
  captcha: ''
});

const formStatus = ref('idle');
const errorMessage = ref('');

const num1 = ref(0);
const num2 = ref(0);

const rules = {
  required: value => !!value || 'This field is required.',
  email: value => /.+@.+\..+/.test(value) || 'E-mail must be valid.',
};

function generateCaptcha() {
  num1.value = Math.floor(Math.random() * 10) + 1;
  num2.value = Math.floor(Math.random() * 10) + 1;
}

async function handleSubmit() {
  formStatus.value = 'sending';
  errorMessage.value = '';
  if (!form.value.name || !form.value.email || !form.value.subject || !form.value.message || !form.value.captcha) {
    errorMessage.value = 'Please fill out all fields.';
    formStatus.value = 'error';
    return;
  }
  if (parseInt(form.value.captcha, 10) !== (num1.value + num2.value)) {
    errorMessage.value = 'Incorrect captcha answer. Please try again.';
    formStatus.value = 'error';
    generateCaptcha();
    return;
  }
  console.log('Form data to be sent to cs@teetah.art:');
  console.log(JSON.stringify(form.value, null, 2));
  await new Promise(resolve => setTimeout(resolve, 1500));
  formStatus.value = 'success';
}

onMounted(() => {
  generateCaptcha();
});

onUnmounted(() => {
});
</script>

<style scoped>
.page-content-container {
  position: relative;
  z-index: 2;
}
.legal-page { padding: 120px 0; background-color: #0A0F1E; min-height: 100vh; position: relative; z-index: 1; }
.article-card-content {
  background: rgba(23, 33, 65, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 245, 255, 0.2);
  padding: 24px 32px;
  animation: card-border-glow 4s infinite alternate;
}
@keyframes card-border-glow {
  from {
    border-color: rgba(0, 245, 255, 0.2);
    box-shadow: 0 0 15px rgba(0, 245, 255, 0.1);
  }
  to {
    border-color: rgba(191, 0, 255, 0.2);
    box-shadow: 0 0 30px rgba(191, 0, 255, 0.15);
  }
}
.headline { color: #00f5ff; }
.orbitron-font { font-family: 'Orbitron', monospace; }
.action-btn { font-weight: bold; color: #010c03 !important; }
.captcha-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  background-color: rgba(0,0,0,0.2);
  padding: 12px;
  border-radius: 8px;
  flex-wrap: wrap;
}
.captcha-question {
  font-family: 'Orbitron', monospace;
  color: #B0BEC5;
}
.captcha-input {
  max-width: 120px;
}
</style>
