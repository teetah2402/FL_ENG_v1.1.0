//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\PrivacyPolicy.vue total lines 106 
//#######################################################################

<template>
  <v-main>
    <div class="legal-page">
      <DigitalFingerprintBackground />

      <v-container class="page-content-container">
        <v-row justify="center">
          <v-col cols="12" md="8">
            <v-card class="article-card-content">
              <v-card-title class="headline text-center orbitron-font">Privacy Policy</v-card-title>
              <v-card-text>
                <p><strong>Last Updated: {{ new Date().toLocaleDateString('en-US') }}</strong></p>

                <p>Welcome to Flowork ("we," "our," or "us"). We are committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our services through our website (app.teetah.art) and our downloadable Engine software.</p>

                <h2 class="section-title">1. Information We Collect</h2>
                <p>We may collect information about you in a variety of ways. The information we may collect includes:</p>
                <ul>
                  <li><strong>Personal Data:</strong> Personally identifiable information, such as your name, email address, and username, that you voluntarily give to us when you register for an account.</li>
                  <li><strong>Subscription Data:</strong> Information related to your subscription tier and payment status, which is managed through our third-party payment processor (e.g., Lemon Squeezy). We do not store your credit card details.</li>
                  <li><strong>Engine Configuration Data:</strong> We store a unique, secret token associated with your account to authenticate your self-hosted Flowork Engines.</li>
                </ul>

                <h2 class="section-title">2. Information We DO NOT Collect</h2>
                <p>Our hybrid architecture is designed for your privacy. We explicitly DO NOT collect, see, or store:</p>
                <ul>
                  <li>Any data processed by your Flowork Engines on your servers.</li>
                  <li>The content of your workflow presets.</li>
                  <li>Files, database contents, or any other information that your workflows interact with on your local machines or private networks.</li>
                </ul>

                <h2 class="section-title">3. Use of Your Information</h2>
                <p>Having accurate information about you permits us to provide you with a smooth, efficient, and customized experience. Specifically, we may use information collected about you to:</p>
                <ul>
                  <li>Create and manage your account.</li>
                  <li>Process payments and manage your subscriptions.</li>
                  <li>Authenticate your Flowork Engines to ensure they can receive jobs from your account.</li>
                  <li>Email you regarding your account or order.</li>
                </ul>

                <h2 class="section-title">4. Security of Your Information</h2>
                <p>We use administrative, technical, and physical security measures to help protect your personal information. While we have taken reasonable steps to secure the personal information you provide to us, please be aware that despite our efforts, no security measures are perfect or impenetrable, and no method of data transmission can be guaranteed against any interception or other type of misuse.</p>

                <h2 class="section-title">5. Contact Us</h2>
                <p>If you have questions or comments about this Privacy Policy, please contact us at: sahidinaola@gmail.com</p>
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
