//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\DMCA.vue total lines 92 
//#######################################################################

<template>
  <v-main>
    <div class="legal-page">
      <DigitalFingerprintBackground />

      <v-container class="page-content-container">
        <v-row justify="center">
          <v-col cols="12" md="8">
            <v-card class="article-card-content">
              <v-card-title class="headline text-center orbitron-font">DMCA Policy</v-card-title>
              <v-card-text>
                <p>Flowork respects the intellectual property rights of others and expects its users to do the same. In accordance with the Digital Millennium Copyright Act of 1998, the text of which may be found on the U.S. Copyright Office website at <a href="http://www.copyright.gov/legislation/dmca.pdf" target="_blank" rel="noopener noreferrer">http://www.copyright.gov/legislation/dmca.pdf</a>, Flowork will respond expeditiously to claims of copyright infringement committed using the Flowork service and/or the Flowork website (the "Site") if such claims are reported to Flowork's Designated Copyright Agent identified in the sample notice below.</p>

                <h2 class="section-title">DMCA Notice of Alleged Infringement ("Notice")</h2>
                <p>If you are a copyright owner, authorized to act on behalf of one, or authorized to act under any exclusive right under copyright, please report alleged copyright infringements taking place on or through the Site by completing the following DMCA Notice of Alleged Infringement and delivering it to Flowork's Designated Copyright Agent.</p>
                <ol>
                    <li>Identify the copyrighted work that you claim has been infringed, or - if multiple copyrighted works are covered by this Notice - you may provide a representative list of the copyrighted works that you claim have been infringed.</li>
                    <li>Identify the material or link you claim is infringing (or the subject of infringing activity) and to which access is to be disabled, including at a minimum, if applicable, the URL of the link shown on the Site or the exact location where such material may be found.</li>
                    <li>Provide your company affiliation (if applicable), mailing address, telephone number, and, if available, email address.</li>
                    <li>Include both of the following statements in the body of the Notice:
                        <ul>
                            <li>"I hereby state that I have a good faith belief that the disputed use of the copyrighted material is not authorized by the copyright owner, its agent, or the law (e.g., as a fair use)."</li>
                            <li>"I hereby state that the information in this Notice is accurate and, under penalty of perjury, that I am the owner, or authorized to act on behalf of, the owner, of the copyright or of an exclusive right under the copyright that is allegedly infringed."</li>
                        </ul>
                    </li>
                    <li>Provide your full legal name and your electronic or physical signature.</li>
                </ol>
                <p>Deliver this Notice, with all items completed, to Flowork's Designated Copyright Agent:</p>
                <p><strong>Copyright Agent</strong><br>
                Flowork Legal Department<br>
                Email: sahidinaola@gmail.com</p>
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
