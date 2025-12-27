//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\LanderView.vue total lines 215 
//#######################################################################

<template>
  <div class="lander-page">
    <DigitalFingerprintBackground />
    <v-main>
      <v-container fluid class="pa-0">

        <section class="hero-section d-flex align-center text-center">
          <v-container class="hero-content">
            <h1 class="hero-title orbitron-font mb-4">
              <span class="text-white">THE WORLD'S FIRST</span>
              <br />
              <span class="text-neon-cyan">HYBRID AI OPERATING SYSTEM</span>
            </h1>

            <p class="hero-subtitle mb-8 text-grey-lighten-1">
              Cloud Control. Local Power. Absolute Privacy.
              <br/>
              <span class="text-neon-purple font-weight-bold">Your Identity. Your Data. Your Engine.</span>
            </p>

            <div class="hero-desc mb-8 mx-auto" style="max-width: 800px;">
              Flowork is the next evolution of AI orchestration. A <strong>Visual AI Factory</strong> where you can run high-performance Hybrid Apps, train private models, and automate everything securely on your own hardware.
            </div>

            <div class="cta-group d-flex justify-center gap-4">
              <v-btn
                color="cyan"
                size="x-large"
                class="cta-btn-primary px-8 orbitron-font"
                to="/register"
              >
                Start Free
                <v-icon end>mdi-arrow-right</v-icon>
              </v-btn>

              <v-btn
                variant="outlined"
                color="white"
                size="x-large"
                class="cta-btn-secondary px-8 orbitron-font"
                href="http://download.flowork.cloud/"
                target="_blank"
              >
                Download Engine
                <v-icon end>mdi-download</v-icon>
              </v-btn>
            </div>
          </v-container>
        </section>

        <section class="apps-showcase py-16" style="background: rgba(0, 245, 255, 0.02);">
          <v-container>
            <div class="text-center mb-12">
              <h2 class="section-title orbitron-font">POWERFUL <span class="text-neon-cyan">HYBRID APPS</span></h2>
              <p class="text-grey-lighten-1 mt-2">Full-scale native applications managed from the cloud. The ultimate evolution of legacy widgets.</p>
              <div class="section-divider mx-auto"></div>
            </div>

            <v-row align="center">
              <v-col cols="12" md="4">
                <v-card class="feature-card h-100" flat to="/apps-center">
                  <div class="card-glow"></div>
                  <v-card-text class="text-center pa-6">
                    <v-icon color="cyan" size="48" class="mb-4">mdi-rocket-launch</v-icon>
                    <h3 class="feature-title orbitron-font mb-2">High-Speed Logic</h3>
                    <p class="feature-desc">Apps utilize your local Engine for Python execution and GPU acceleration.</p>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card class="feature-card h-100" flat to="/apps-center">
                  <div class="card-glow"></div>
                  <v-card-text class="text-center pa-6">
                    <v-icon color="cyan" size="48" class="mb-4">mdi-layers-triple</v-icon>
                    <h3 class="feature-title orbitron-font mb-2">Modular Isolation</h3>
                    <p class="feature-desc">Each app has its own isolated library folder and requirements, zero conflicts.</p>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card class="feature-card h-100" flat to="/apps-center">
                  <div class="card-glow"></div>
                  <v-card-text class="text-center pa-6">
                    <v-icon color="cyan" size="48" class="mb-4">mdi-cloud-lock</v-icon>
                    <h3 class="feature-title orbitron-font mb-2">Secure Bridge</h3>
                    <p class="feature-desc">Control your local apps from the Cloudflare-hosted GUI with end-to-end security.</p>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </section>

        <section class="features-section py-16">
          <v-container>
            <div class="text-center mb-12">
              <h2 class="section-title orbitron-font">ENGINEERED FOR SUPREMACY</h2>
              <div class="section-divider mx-auto"></div>
            </div>

            <v-row>
              <v-col cols="12" md="4">
                <v-card class="feature-card h-100" flat>
                  <div class="card-glow"></div>
                  <v-card-text class="text-center pa-6">
                    <div class="feature-icon mb-4">
                      <v-icon color="cyan-accent-2" size="48">mdi-shield-lock-outline</v-icon>
                    </div>
                    <h3 class="feature-title orbitron-font mb-3">Hybrid Privacy</h3>
                    <p class="feature-desc text-grey-lighten-1">
                      The Engine runs on your hardware. Your sensitive data never leaves your local machine.
                    </p>
                  </v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" md="4">
                <v-card class="feature-card h-100" flat>
                  <div class="card-glow"></div>
                  <v-card-text class="text-center pa-6">
                    <div class="feature-icon mb-4">
                      <v-icon color="purple-accent-2" size="48">mdi-account-group-outline</v-icon>
                    </div>
                    <h3 class="feature-title orbitron-font mb-3">AI Council</h3>
                    <p class="feature-desc text-grey-lighten-1">
                      Assign tasks to a Council of Autonomous Agents that debate and execute workflows.
                    </p>
                  </v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" md="4">
                <v-card class="feature-card h-100" flat>
                  <div class="card-glow"></div>
                  <v-card-text class="text-center pa-6">
                    <div class="feature-icon mb-4">
                      <v-icon color="pink-accent-2" size="48">mdi-factory</v-icon>
                    </div>
                    <h3 class="feature-title orbitron-font mb-3">Local AI Factory</h3>
                    <p class="feature-desc text-grey-lighten-1">
                      Fine-tune LLMs and curate datasets directly on your local GPU.
                    </p>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </section>

        <section class="how-it-works py-16" style="background: rgba(0,0,0,0.3);">
          <v-container>
             <div class="text-center mb-12">
              <h2 class="section-title orbitron-font">DEPLOY IN SECONDS</h2>
              <div class="section-divider mx-auto"></div>
            </div>

            <div class="steps-container d-flex flex-column flex-md-row justify-center align-center gap-8">
              <div class="step-card">
                <div class="step-number">01</div>
                <h3 class="step-title orbitron-font">Claim Identity</h3>
                <p class="step-desc">Create your secure account. Your Dashboard becomes your global command center.</p>
              </div>
              <v-icon icon="mdi-arrow-right" class="d-none d-md-block step-arrow" color="grey"></v-icon>
              <div class="step-card">
                <div class="step-number">02</div>
                <h3 class="step-title orbitron-font">Ignite Engine</h3>
                <p class="step-desc">Run the <strong>Flowork Engine</strong> on your machine. It handles the secure tunnel.</p>
              </div>
              <v-icon icon="mdi-arrow-right" class="d-none d-md-block step-arrow" color="grey"></v-icon>
              <div class="step-card">
                <div class="step-number">03</div>
                <h3 class="step-title orbitron-font">Orchestrate</h3>
                <p class="step-desc">Launch Hybrid Apps, deploy agents, and manage your empire from anywhere.</p>
              </div>
            </div>
          </v-container>
        </section>

      </v-container>
    </v-main>
  </div>
</template>

<script setup>
import DigitalFingerprintBackground from '@/components/DigitalFingerprintBackground.vue'
</script>

<style scoped>
.lander-page { background-color: #030305; min-height: 100vh; color: #fff; overflow-x: hidden; }
.hero-section { min-height: 90vh; position: relative; z-index: 1; padding-top: 80px; }
.hero-title { font-size: 3rem; line-height: 1.2; text-shadow: 0 0 20px rgba(0, 245, 255, 0.3); }
@media (min-width: 960px) { .hero-title { font-size: 4.5rem; } }
.hero-subtitle { font-size: 1.2rem; font-family: 'Inter', sans-serif; letter-spacing: 1px; }
.hero-desc { font-size: 1.1rem; color: #94a3b8; line-height: 1.6; }
.cta-btn-primary { background: linear-gradient(45deg, var(--neon-cyan), var(--neon-blue)); color: #000 !important; font-weight: 900; letter-spacing: 1px; box-shadow: 0 0 20px rgba(0, 245, 255, 0.4); }
.cta-btn-primary:hover { transform: scale(1.05); }
.section-title { font-size: 2rem; font-weight: 700; color: #fff; letter-spacing: 2px; }
.section-divider { width: 60px; height: 4px; background: var(--neon-cyan); margin-top: 15px; box-shadow: 0 0 10px var(--neon-cyan); }
.feature-card { background: rgba(255, 255, 255, 0.03) !important; border: 1px solid rgba(255, 255, 255, 0.05); position: relative; border-radius: 16px; transition: all 0.3s ease; }
.feature-card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.05) !important; border-color: rgba(0, 245, 255, 0.2); }
.card-glow { position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent); opacity: 0; }
.feature-card:hover .card-glow { opacity: 1; }
.step-card { background: rgba(15, 15, 25, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; text-align: center; width: 100%; max-width: 350px; position: relative; }
.step-number { font-family: 'Orbitron', monospace; font-size: 3rem; color: rgba(255, 255, 255, 0.05); position: absolute; top: 10px; right: 20px; }
.text-neon-cyan { color: #00f5ff; }
.orbitron-font { font-family: 'Orbitron', sans-serif; }
.gap-4 { gap: 16px; }
.gap-8 { gap: 32px; }
</style>
