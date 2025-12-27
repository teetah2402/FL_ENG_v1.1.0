//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\TermsOfService.vue total lines 99 
//#######################################################################

<template>
  <v-main>
    <div class="legal-page">
      <DigitalFingerprintBackground />

      <v-container class="page-content-container">
        <v-row justify="center">
          <v-col cols="12" md="8">
            <v-card class="article-card-content">
              <v-card-title class="headline text-center orbitron-font">Terms of Service</v-card-title>
              <v-card-text>
                <p><strong>Last Updated: {{ new Date().toLocaleDateString('en-US') }}</strong></p>

                <h2 class="section-title">1. Agreement to Terms</h2>
                <p>By using our services, you agree to be bound by these Terms of Service. If you do not agree to these Terms, do not use the services.</p>

                <h2 class="section-title">2. Your Account</h2>
                <p>You are responsible for safeguarding your account. You agree that you will not disclose your password to any third party and that you will take sole responsibility for any activities or actions under your account, whether or not you have authorized such activities or actions.</p>

                <h2 class="section-title">3. User Responsibilities</h2>
                <p>You agree not to misuse the Flowork services. For example, you must not, and must not attempt to, do the following:</p>
                <ul>
                  <li>Use the services for any unlawful purposes or for promotion of illegal activities.</li>
                  <li>Post any content on the service in violation of any applicable law, including intellectual property laws and right of privacy or publicity laws, or any contractual obligation.</li>
                  <li>Probe, scan, or test the vulnerability of any system or network or breach or circumvent any security or authentication measures.</li>
                </ul>

                <h2 class="section-title">4. Service Availability</h2>
                <p>We will use reasonable efforts to make the services available 24/7/365, but we do not guarantee that the services will be uninterrupted or error-free. The security and operation of your self-hosted Flowork Engines are your sole responsibility.</p>

                <h2 class="section-title">5. Termination</h2>
                <p>We may terminate or suspend your access to our services immediately, without prior notice or liability, for any reason whatsoever, including without limitation if you breach the Terms.</p>

                <h2 class="section-title">6. Changes to Terms</h2>
                <p>We reserve the right, at our sole discretion, to modify or replace these Terms at any time. We will provide at least 30 days' notice before any new terms taking effect. By continuing to access or use our Service after those revisions become effective, you agree to be bound by the revised terms.</p>

                <h2 class="section-title">7. Contact Us</h2>
                <p>If you have any questions about these Terms, please contact us at: sahidinaola@gmail.com</p>
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
import LanderFooter from '@/components/LanderFooter.vue';
import { ref, onMounted, onUnmounted } from 'vue';
import DigitalFingerprintBackground from '@/components/DigitalFingerprintBackground.vue';


onMounted(() => {
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
.section-title { margin-top: 24px; margin-bottom: 16px; color: #e0e0e0; }
p, li, ul { color: #B0BEC5; }
ul { padding-left: 20px; }
li { margin-bottom: 8px; }
a { color: #00f5ff; }
.orbitron-font { font-family: 'Orbitron', monospace; }
</style>
