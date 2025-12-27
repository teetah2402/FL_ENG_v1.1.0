//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\views\ModuleFactory.vue total lines 712 
//#######################################################################

<template>
  <div class="module-factory-layout h-100 d-flex flex-column bg-black">

    <div class="forge-header px-4 py-2 d-flex align-center border-bottom-subtle flex-shrink-0 bg-glass">
        <v-btn icon variant="text" color="grey" class="mr-2" @click="handleBack">
            <v-icon>{{ activeComponent ? 'mdi-arrow-left' : 'mdi-home-variant-outline' }}</v-icon>
        </v-btn>

        <div class="d-flex flex-column">
            <span class="text-subtitle-2 font-weight-bold orbitron-font text-amber-darken-1">
                COMPONENT FORGE <span class="text-grey-darken-2 text-caption">v1.3</span>
            </span>
            <span class="text-caption text-grey" v-if="activeComponent">
                Editing: <span class="text-grey-lighten-2">{{ meta.name || 'Untitled Component' }}</span>
                <span v-if="hasUnsavedChanges" class="text-amber-accent-4 font-italic ml-2 text-[10px]">* Unsaved</span>
            </span>
        </div>

        <v-spacer></v-spacer>

        <div v-if="activeComponent" class="d-flex align-center gap-2">
            <v-btn size="small" variant="text" color="grey" prepend-icon="mdi-test-tube" @click="testRun">Test Run</v-btn>
            <v-btn size="small" variant="tonal" color="green-darken-1" prepend-icon="mdi-content-save-outline" :loading="isSaving" @click="saveComponent">Save Build</v-btn>
            <v-btn size="small" variant="flat" color="amber-darken-4" prepend-icon="mdi-publish" @click="showPublishDialog = true">Publish</v-btn>
        </div>
    </div>

    <div v-if="!activeComponent" class="hub-container flex-grow-1 d-flex align-center justify-center pa-6 relative overflow-hidden">
        <div class="grid-bg"></div>

        <div class="hub-content w-100" style="max-width: 1000px; z-index: 2;">
            <div class="text-center mb-10">
                <h1 class="text-h4 font-weight-light text-white orbitron-font mb-2">WHAT WILL YOU <span class="text-amber-darken-1 font-weight-bold">FORGE</span>?</h1>
                <p class="text-body-1 text-grey-darken-1">Select a component type to initialize the development environment.</p>
            </div>

            <v-row>
                <v-col cols="12" md="4" v-for="type in componentTypes" :key="type.id">
                    <v-hover v-slot="{ isHovering, props }">
                        <v-card
                            v-bind="props"
                            class="hub-card pa-6 h-100 d-flex flex-column align-center justify-center text-center cursor-pointer transition-all"
                            :class="{ 'card-hover': isHovering }"
                            :style="{ borderColor: isHovering ? type.color : 'rgba(255,255,255,0.05)' }"
                            color="#121212"
                            @click="initForge(type)"
                        >
                            <v-icon :icon="type.icon" :color="type.color" size="48" class="mb-4 hub-icon opacity-80"></v-icon>
                            <h3 class="text-h6 font-weight-bold text-grey-lighten-2 mb-2">{{ type.name }}</h3>
                            <p class="text-caption text-grey-darken-1">{{ type.desc }}</p>

                            <v-chip size="x-small" :color="type.color" variant="outlined" class="mt-4 text-uppercase font-weight-bold opacity-70">
                                {{ type.tag }}
                            </v-chip>
                        </v-card>
                    </v-hover>
                </v-col>
            </v-row>
        </div>
    </div>

    <div v-else class="workspace-container flex-grow-1 d-flex overflow-hidden">

        <div class="sidebar-left border-right-subtle bg-black d-flex flex-column" style="width: 320px;">
            <div class="pa-4 overflow-y-auto custom-scrollbar flex-grow-1">

                <div class="section-title text-caption font-weight-bold text-grey-darken-1 mb-3 mt-2">IDENTITY MATRIX</div>

                <v-text-field
                    v-model="meta.name"
                    label="Display Name"
                    variant="outlined"
                    density="compact"
                    bg-color="#0a0a0a"
                    color="amber-darken-1"
                    class="mb-3 font-mono subtle-input"
                    hide-details
                    @update:model-value="syncManifest"
                ></v-text-field>

                <v-text-field
                    v-model="meta.id"
                    label="Component ID (Unique)"
                    variant="outlined"
                    density="compact"
                    bg-color="#0a0a0a"
                    color="amber-darken-1"
                    class="mb-4 font-mono text-caption subtle-input"
                    hint="com.flowork.your_module"
                    persistent-hint
                    @update:model-value="syncManifest"
                ></v-text-field>

                <v-divider class="mb-4 border-opacity-10"></v-divider>

                <div class="section-title text-caption font-weight-bold text-grey-darken-1 mb-3">HOLOGRAPHIC ICON</div>

                <div class="icon-preview-box rounded-lg mb-3 d-flex align-center justify-center" :style="{ borderColor: 'rgba(255,255,255,0.1)' }">
                    <v-icon :icon="meta.icon" :color="meta.color" size="48" class="opacity-90"></v-icon>
                </div>

                <div class="d-flex justify-space-between mb-4 px-1">
                    <div
                        v-for="color in neonColors"
                        :key="color"
                        class="color-dot cursor-pointer"
                        :style="{ backgroundColor: color, transform: meta.color === color ? 'scale(1.2)' : 'scale(1)', opacity: meta.color === color ? 1 : 0.5 }"
                        @click="updateColor(color)"
                    ></div>
                </div>

                <v-text-field
                    v-model="iconSearch"
                    prepend-inner-icon="mdi-magnify"
                    placeholder="Search icons..."
                    variant="outlined"
                    density="compact"
                    bg-color="#0a0a0a"
                    hide-details
                    class="mb-2 icon-search subtle-input"
                ></v-text-field>

                <div class="icon-grid d-flex flex-wrap gap-2 justify-start" style="max-height: 150px; overflow-y: auto;">
                    <div
                        v-for="icon in filteredIcons"
                        :key="icon"
                        class="icon-item d-flex align-center justify-center rounded cursor-pointer"
                        :class="{ 'active': meta.icon === icon }"
                        @click="updateIcon(icon)"
                    >
                        <v-icon :icon="icon" size="small" color="grey"></v-icon>
                    </div>
                </div>

                <v-divider class="my-4 border-opacity-10"></v-divider>

                <div class="section-title text-caption font-weight-bold text-grey-darken-1 mb-2">METADATA</div>
                <v-textarea
                    v-model="meta.description"
                    label="Description"
                    variant="outlined"
                    bg-color="#0a0a0a"
                    color="amber-darken-1"
                    rows="3"
                    class="text-caption subtle-input"
                    hide-details
                    @update:model-value="syncManifest"
                ></v-textarea>

                <div class="section-title text-caption font-weight-bold text-grey-darken-1 mt-4 mb-2">DEPENDENCIES</div>
                 <v-textarea
                    v-model="requirementsContent"
                    label="requirements.txt"
                    variant="outlined"
                    bg-color="#0a0a0a"
                    color="amber-darken-1"
                    rows="3"
                    class="text-caption font-mono subtle-input"
                    hide-details
                ></v-textarea>

            </div>
        </div>

        <div class="editor-main flex-grow-1 d-flex flex-column bg-black relative">
            <div class="editor-tabs d-flex bg-black border-bottom-subtle" style="z-index: 5; position: relative;">
                <div class="tab-item px-4 py-2 text-caption font-mono cursor-pointer d-flex align-center"
                     :class="{ 'active-tab': activeTab === 'processor' }"
                     @click="activeTab = 'processor'">
                    <v-icon icon="mdi-language-python" size="small" color="amber-darken-2" class="mr-2"></v-icon>
                    <span class="text-grey-lighten-2">processor.py</span>
                </div>
                <div class="tab-item px-4 py-2 text-caption font-mono cursor-pointer d-flex align-center"
                     :class="{ 'active-tab': activeTab === 'manifest' }"
                     @click="activeTab = 'manifest'">
                    <v-icon icon="mdi-code-json" size="small" color="grey-darken-1" class="mr-2"></v-icon>
                    manifest.json
                </div>
            </div>

            <div class="code-area flex-grow-1 relative">
                <v-textarea
                    v-if="activeTab === 'processor'"
                    v-model="codeContent"
                    variant="plain"
                    class="code-input fill-height font-mono pa-0"
                    bg-color="#050505"
                    color="grey-lighten-2"
                    hide-details
                    no-resize
                    spellcheck="false"
                ></v-textarea>

                <v-textarea
                    v-if="activeTab === 'manifest'"
                    :model-value="manifestJsonString"
                    variant="plain"
                    class="code-input fill-height font-mono pa-0"
                    bg-color="#050505"
                    color="green-lighten-2"
                    hide-details
                    no-resize
                    spellcheck="false"
                    readonly
                ></v-textarea>

                <v-menu location="top end" v-if="activeTab === 'processor'">
                    <template v-slot:activator="{ props }">
                        <v-btn v-bind="props" position="absolute" style="bottom: 20px; right: 20px;" icon="mdi-flash" color="amber-darken-3" size="small" variant="text"></v-btn>
                    </template>
                    <v-list density="compact" bg-color="#121212" class="border-subtle">
                        <v-list-subheader class="text-caption text-uppercase text-grey-darken-1">Inject Snippet</v-list-subheader>
                        <v-list-item @click="injectCode('input_handler')"><v-list-item-title class="text-caption text-grey-lighten-1">Input Validation</v-list-item-title></v-list-item>
                        <v-list-item @click="injectCode('http_request')"><v-list-item-title class="text-caption text-grey-lighten-1">HTTP Request (Requests)</v-list-item-title></v-list-item>
                        <v-list-item @click="injectCode('logger')"><v-list-item-title class="text-caption text-grey-lighten-1">Flowork Logger</v-list-item-title></v-list-item>
                        <v-list-item @click="injectCode('error_handling')"><v-list-item-title class="text-caption text-grey-lighten-1">Error Try/Except</v-list-item-title></v-list-item>
                    </v-list>
                </v-menu>
            </div>
        </div>

        <div class="sidebar-right border-left-subtle bg-black d-flex flex-column" style="width: 300px;">
            <v-tabs v-model="rightTab" density="compact" grow bg-color="transparent" color="amber-darken-1">
                <v-tab value="schema" class="text-caption text-grey-lighten-1">Schema</v-tab>
                <v-tab value="preview" class="text-caption text-grey-lighten-1">Preview</v-tab>
            </v-tabs>

            <v-window v-model="rightTab" class="flex-grow-1">

                <v-window-item value="schema" class="h-100 d-flex flex-column">
                    <div class="pa-4 overflow-y-auto flex-grow-1 custom-scrollbar">

                        <div class="d-flex justify-space-between align-center mb-2">
                            <span class="text-caption font-weight-bold text-amber-darken-3">PROPERTIES (INPUTS)</span>
                            <v-btn icon="mdi-plus" size="x-small" variant="text" color="grey" @click="addPort('input')"></v-btn>
                        </div>
                        <div class="text-caption text-grey-darken-2 mb-2 font-italic" v-if="schema.inputs.length === 0">
                            No configuration properties defined.
                        </div>

                        <div v-for="(port, i) in schema.inputs" :key="'in-'+i" class="schema-item pa-2 rounded bg-grey-darken-4 mb-2 border-subtle">
                            <div class="d-flex align-center mb-1">
                                <v-icon icon="mdi-cog-outline" size="x-small" color="grey" class="mr-2"></v-icon>
                                <input v-model="port.name" @input="syncManifest" class="simple-input flex-grow-1 text-caption text-grey-lighten-1" placeholder="Property ID">
                                <v-btn icon="mdi-close" size="x-small" variant="text" color="grey-darken-1" @click="removePort('input', i)"></v-btn>
                            </div>
                            <input v-model="port.label" @input="syncManifest" class="simple-input w-100 text-caption text-grey mb-1" style="font-size: 10px;" placeholder="Display Label">
                            <select v-model="port.type" @change="syncManifest" class="simple-select w-100 text-caption text-grey">
                                <option value="string">String</option>
                                <option value="number">Number</option>
                                <option value="boolean">Boolean</option>
                                <option value="json">JSON</option>
                                <option value="secret">Secret (Encrypted)</option>
                            </select>
                        </div>

                        <v-divider class="my-3 border-opacity-10"></v-divider>

                        <div class="d-flex justify-space-between align-center mb-2">
                            <span class="text-caption font-weight-bold text-amber-darken-3">OUTPUT PORTS</span>
                            <v-btn icon="mdi-plus" size="x-small" variant="text" color="grey" @click="addPort('output')"></v-btn>
                        </div>

                        <div v-for="(port, i) in schema.outputs" :key="'out-'+i" class="schema-item pa-2 rounded bg-grey-darken-4 mb-2 border-subtle">
                            <div class="d-flex align-center mb-1">
                                <v-icon icon="mdi-export" size="x-small" color="grey" class="mr-2"></v-icon>
                                <input v-model="port.name" @input="syncManifest" class="simple-input flex-grow-1 text-caption text-grey-lighten-1" placeholder="Port Name">
                                <v-btn icon="mdi-close" size="x-small" variant="text" color="grey-darken-1" @click="removePort('output', i)"></v-btn>
                            </div>
                            <input v-model="port.description" @input="syncManifest" class="simple-input w-100 text-caption text-grey mb-1" style="font-size: 10px;" placeholder="Description">
                            <select v-model="port.type" @change="syncManifest" class="simple-select w-100 text-caption text-grey">
                                <option value="any">Any</option>
                                <option value="string">String</option>
                                <option value="json">JSON</option>
                                <option value="image">Image</option>
                            </select>
                        </div>
                    </div>
                </v-window-item>

                <v-window-item value="preview" class="h-100 d-flex align-center justify-center bg-dots">
                    <div class="preview-node rounded-lg pa-0 overflow-hidden" :style="{ boxShadow: `0 4px 10px rgba(0,0,0,0.5)`, border: `1px solid ${meta.color}60` }">
                        <div class="node-header px-3 py-2 d-flex align-center" :style="{ backgroundColor: `${meta.color}15`, borderBottom: `1px solid ${meta.color}30` }">
                            <v-icon :icon="meta.icon" size="small" :color="meta.color" class="mr-2 opacity-80"></v-icon>
                            <span class="text-caption font-weight-bold text-grey-lighten-2 text-truncate" style="max-width: 120px;">{{ meta.name || 'Node' }}</span>
                        </div>
                        <div class="node-body bg-grey-darken-4 pa-2" style="min-width: 180px;">
                            <div class="text-[9px] text-grey-darken-1 mb-1 font-weight-bold" v-if="schema.inputs.length">INPUTS</div>
                            <div v-for="inp in schema.inputs" :key="inp.name" class="d-flex align-center mb-1">
                                <div class="port-dot mr-2 bg-grey-darken-1"></div>
                                <span class="text-caption text-grey" style="font-size: 10px;">{{ inp.label || inp.name }}</span>
                            </div>

                            <v-divider class="my-2 border-opacity-10" v-if="schema.inputs.length && schema.outputs.length"></v-divider>

                            <div class="text-[9px] text-grey-darken-1 mb-1 font-weight-bold text-right" v-if="schema.outputs.length">OUTPUTS</div>
                            <div class="d-flex justify-end mt-1 flex-column align-end">
                                <div v-for="outp in schema.outputs" :key="outp.name" class="d-flex align-center mb-1 ml-2">
                                    <span class="text-caption text-grey mr-2" style="font-size: 10px;">{{ outp.name }}</span>
                                    <div class="port-dot bg-amber-darken-3"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </v-window-item>
            </v-window>
        </div>

    </div>

    <v-dialog v-model="showPublishDialog" max-width="400">
        <v-card color="#181818" class="border-subtle">
            <v-card-title class="text-h6 text-grey-lighten-2 orbitron-font">Publish to Marketplace</v-card-title>
            <v-card-text class="pt-4">
                <p class="text-caption text-grey mb-4">Your component will be reviewed by the Neural Council before being public.</p>
                <v-text-field label="Version" model-value="1.0.0" variant="outlined" density="compact" color="amber-darken-1" bg-color="#0a0a0a"></v-text-field>
                <v-select label="Visibility" :items="['Public', 'Private Engine Only']" variant="outlined" density="compact" color="amber-darken-1" bg-color="#0a0a0a"></v-select>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="grey" variant="text" @click="showPublishDialog = false">Cancel</v-btn>
                <v-btn color="amber-darken-1" variant="flat" class="text-black font-weight-bold" @click="showPublishDialog = false">Submit</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue';
import { useUiStore } from '@/store/ui';
import { useComponentStore } from '@/store/components';
import { useRouter } from 'vue-router';

const uiStore = useUiStore();
const componentStore = useComponentStore();
const router = useRouter();

const activeComponent = ref(null);
const rightTab = ref('schema');
const activeTab = ref('processor'); // processor | manifest
const showPublishDialog = ref(false);
const isSaving = ref(false);
const hasUnsavedChanges = ref(false); // [FIX] Added dirty state tracker

const requirementsContent = ref("requests==2.31.0\n");

const meta = reactive({
    name: 'New Component',
    id: 'com.flowork.untitled',
    description: '',
    icon: 'mdi-cube-outline',
    color: '#FFC107' // Amber
});

const codeContent = ref('');

const schema = reactive({
    inputs: [], // Mapped to Properties
    outputs: [] // Mapped to Output Ports
});

watch([meta, schema, codeContent, requirementsContent], () => {
    if (activeComponent.value) {
        hasUnsavedChanges.value = true;
    }
}, { deep: true });

const manifest = reactive({
    id: '',
    name: '',
    author: 'Unknown', // In real app, get from AuthStore
    description: '',
    type: 'module',
    entry_point: 'processor.py',
    version: '1.0',
    requires_input: true,
    properties: [],
    output_ports: [],
    output_schema: [],
    display_properties: { color: '', text_color: '' },
    supported_languages: ['python']
});

const manifestJsonString = computed(() => {
    return JSON.stringify(manifest, null, 4);
});

const iconSearch = ref('');
const commonIcons = [
    'mdi-robot', 'mdi-brain', 'mdi-database', 'mdi-cloud', 'mdi-api', 'mdi-webhook',
    'mdi-email', 'mdi-file-document', 'mdi-image', 'mdi-chart-bar', 'mdi-console',
    'mdi-spider', 'mdi-shield-bug', 'mdi-lock', 'mdi-key', 'mdi-wifi', 'mdi-server',
    'mdi-monitor-dashboard', 'mdi-play-circle', 'mdi-stop-circle', 'mdi-timer', 'mdi-bell',
    'mdi-check-circle', 'mdi-alert', 'mdi-information', 'mdi-twitter', 'mdi-instagram'
];
const neonColors = ['#FFC107', '#FFA000', '#FFD54F', '#FF6F00', '#F57F17', '#E91E63', '#00E676', '#2979FF'];

const filteredIcons = computed(() => {
    if(!iconSearch.value) return commonIcons;
    return commonIcons.filter(i => i.includes(iconSearch.value.toLowerCase()));
});

const componentTypes = [
    { id: 'module', name: 'Logic Module', desc: 'Process data and return results.', icon: 'mdi-puzzle', color: '#FFCA28', tag: 'CORE' },
    { id: 'trigger', name: 'Event Trigger', desc: 'Watch for events and start flows.', icon: 'mdi-lightning-bolt', color: '#FFD54F', tag: 'EVENT' },
    { id: 'action', name: 'Action Node', desc: 'Perform external API actions.', icon: 'mdi-hammer-wrench', color: '#FFA000', tag: 'ACT' },
    { id: 'cron', name: 'Cron Job', desc: 'Scheduled execution task.', icon: 'mdi-clock-outline', color: '#00E676', tag: 'TIME' },
    { id: 'scanner', name: 'System Scanner', desc: 'Diagnostic health checks.', icon: 'mdi-radar', color: '#E91E63', tag: 'DIAG' }
];

async function initForge(type) {
    activeComponent.value = type;

    meta.color = type.color;
    meta.icon = type.icon;
    meta.name = `New ${type.name}`;
    meta.id = `com.flowork.${type.id}_${Math.floor(Math.random() * 1000)}`;
    meta.description = type.desc;

    schema.inputs = [];
    schema.outputs = [];

    codeContent.value = generatePythonTemplate(type.id);

    syncManifest();

    await nextTick();
    hasUnsavedChanges.value = false;
}

function generatePythonTemplate(typeId) {
    const header = `"""\nFlowork Component: ${meta.name}\nType: ${typeId.toUpperCase()}\nCreated: ${new Date().toISOString()}\n"""\n\n`;

    if (typeId === 'trigger') {
        return header + `import time

class CustomTrigger:
    def __init__(self, context):
        self.context = context
        self.running = False

    def start(self):
        """Called when workflow starts"""
        self.running = True
        self.context.log("Trigger Started")
        self.loop()

    def loop(self):
        """Main polling loop"""
        while self.running:
            # Check for events here
            # event = check_api()
            # if event:
            #     self.context.emit(event)

            time.sleep(5) # Prevent CPU hogging

    def stop(self):
        self.running = False
`;
    }

    else if (typeId === 'module' || typeId === 'action') {
        return header + `def process(input_data, context):
    """
    Main processing function.
    Args:
        input_data (dict): Data passed from previous node or trigger.
        context (Context): Flowork execution context (logger, env, etc).
    """
    context.log(f"Processing data: {input_data}")

    # 1. Get Property (Input)
    # api_key = context.get_property('api_key')

    # 2. Logic
    result = {
        "status": "success",
        "processed_at": context.timestamp(),
        "data": input_data
    }

    # 3. Return Output
    return result
`;
    }

    else if (typeId === 'scanner') {
        return header + `def scan(context):
    """
    Diagnostic Scan Function
    """
    health_score = 100
    issues = []

    # Check something
    # if not check_db():
    #     health_score -= 50
    #     issues.append("DB Connection Failed")

    return {
        "healthy": health_score > 80,
        "score": health_score,
        "issues": issues
    }
`;
    }

    return header + `# Unknown Type`;
}

function syncManifest() {
    manifest.id = meta.id;
    manifest.name = meta.name;
    manifest.description = meta.description;
    manifest.display_properties.color = meta.color;
    manifest.type = activeComponent.value?.id || 'module';

    manifest.properties = schema.inputs.map(inp => ({
        id: inp.name,
        type: inp.type,
        label: inp.label || inp.name,
        default: null,
        description: ""
    }));

    manifest.output_ports = schema.outputs.map(outp => ({
        name: outp.name,
        display_name: outp.name, // Can be separate in future
        tooltip: outp.description || "",
        type: outp.type // Adding type metadata to port for filtering
    }));

    manifest.output_schema = schema.outputs.map(outp => ({
        name: outp.name,
        type: outp.type,
        description: outp.description
    }));
}

function updateColor(color) {
    meta.color = color;
    syncManifest();
}

function updateIcon(icon) {
    meta.icon = icon;
}

function addPort(type) {
    if(type === 'input') {
        schema.inputs.push({ name: 'new_property', label: 'New Property', type: 'string' });
    } else {
        schema.outputs.push({ name: 'result', description: 'Main result', type: 'json' });
    }
    syncManifest();
}

function removePort(type, index) {
    if(type === 'input') schema.inputs.splice(index, 1);
    else schema.outputs.splice(index, 1);
    syncManifest();
}

function injectCode(snippet) {
    let code = "";
    if(snippet === 'input_handler') {
        code = `\n    # Validate Input\n    if 'target' not in input_data:\n        raise ValueError("Missing 'target' in input data")\n`;
    } else if (snippet === 'http_request') {
        code = `\n    # HTTP Request\n    response = requests.get('https://api.example.com/data')\n    if response.status_code != 200:\n        raise Exception("API Failed")\n    data = response.json()\n`;
    } else if (snippet === 'logger') {
        code = `\n    context.log("Info: Operation started...", level="info")\n`;
    } else if (snippet === 'error_handling') {
        code = `\n    try:\n        # Unsafe code here\n        pass\n    except Exception as e:\n        context.log(f"Error: {str(e)}", level="error")\n        return {"status": "error", "message": str(e)}\n`;
    }

    codeContent.value += code;
}

async function handleBack() {
    if (activeComponent.value) {
        if (hasUnsavedChanges.value) {
            const confirmed = await uiStore.showConfirmation({
                title: 'Unsaved Changes',
                text: 'Return to Hub? Unsaved changes will be lost.',
                color: 'warning',
                confirmText: 'Discard & Leave'
            });
            if (!confirmed) return; // Stay if user cancels
        }
        activeComponent.value = null;
        hasUnsavedChanges.value = false;
    } else {
        router.push({ name: 'Dashboard' });
    }
}

/**
 * [MODIFIED BY FLOWORK DEV]
 * Now calls the Component Store to persist data to Gateway/Core.
 */
async function saveComponent() {
    isSaving.value = true;
    syncManifest(); // Ensure latest state

    if (!manifest.id.includes(".")) {
        uiStore.showNotification({ text: "ID must contain dots (e.g. com.user.module)", color: "error" });
        isSaving.value = false;
        return;
    }

    const payload = {
        id: manifest.id,
        type: manifest.type,
        code: codeContent.value,
        manifest: manifest,
        requirements: requirementsContent.value
    };

    const result = await componentStore.saveCustomComponent(payload);

    if (result.success) {
        hasUnsavedChanges.value = false; // [FIX] Mark as clean after save
    }

    isSaving.value = false;
}

function testRun() {
    uiStore.showNotification({ text: "Sending to Sandbox...", color: "info" });
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

.orbitron-font { font-family: 'Orbitron', sans-serif; }
.font-mono { font-family: 'Fira Code', monospace; }

.bg-glass { background: rgba(18, 18, 18, 0.9); backdrop-filter: blur(10px); }
.border-bottom-subtle { border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
.border-right-subtle { border-right: 1px solid rgba(255, 255, 255, 0.05); }
.border-left-subtle { border-left: 1px solid rgba(255, 255, 255, 0.05); }
.border-subtle { border: 1px solid rgba(255, 255, 255, 0.05); }

.hub-container {
    background: radial-gradient(circle at center, #1a1a1a 0%, #000000 100%);
}
.grid-bg {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background-image: linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 40px 40px;
    opacity: 0.3; z-index: 1;
}

.hub-card {
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;
}
.card-hover:hover { transform: translateY(-3px); }
.hub-icon { transition: transform 0.3s; }
.card-hover:hover .hub-icon { transform: scale(1.05); opacity: 1; }

/* Sidebar Styles */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }

/* Icon Picker */
.icon-preview-box {
    height: 100px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05);
}
.color-dot { width: 16px; height: 16px; border-radius: 50%; transition: transform 0.2s; border: 1px solid rgba(255,255,255,0.2); }
.icon-item { width: 32px; height: 32px; border: 1px solid transparent; }
.icon-item:hover { background: rgba(255,255,255,0.05); }
.icon-item.active { border-color: #FFC107; background: rgba(255, 193, 7, 0.05); }

/* Editor */
.editor-tabs { height: 36px; }
.active-tab { background: #050505; border-top: 2px solid #FFC107; color: white; }
.code-input :deep(textarea) {
    font-size: 13px; line-height: 1.5; padding: 16px !important;
    color: #d4d4d4 !important; outline: none;
}

.subtle-input :deep(.v-field) {
    border-color: rgba(255,255,255,0.05);
}
.subtle-input :deep(.v-field--focused) {
    border-color: #FFC107;
}

/* Schema & Preview */
.simple-input, .simple-select {
    background: transparent; border: none; outline: none; color: #ddd;
}
.simple-select { background: rgba(0,0,0,0.3); border-radius: 4px; padding: 2px; }
.bg-dots {
    background-image: radial-gradient(#222 1px, transparent 1px); background-size: 20px 20px;
}
.port-dot { width: 8px; height: 8px; border-radius: 50%; }
.hover-text-white:hover { color: white !important; }
</style>
