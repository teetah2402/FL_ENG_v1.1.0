//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ModuleToolbox.vue total lines 257 
//#######################################################################

<template>
  <v-card class="toolbox-card">
    <v-card-title class="pa-4 pb-0">
      <v-text-field
        v-model="search"
        :placeholder="localization.search_modules_placeholder"
        prepend-inner-icon="mdi-magnify"
        clearable
        hide-details
        density="compact"
        variant="solo-filled"
      ></v-text-field>
    </v-card-title>
    <v-divider></v-divider>

    <v-card-text class="pa-0">
      <v-expansion-panels variant="accordion" multiple>
        <v-expansion-panel
          v-for="category in filteredCategories"
          :key="category.id"
          :title="category.name"
        >
          <v-expansion-panel-text class="pa-0">
            <v-list dense>

              <template v-for="app in category.items" :key="app.id">

                <template v-if="app.manifest && app.manifest.nodes && app.manifest.nodes.length > 0">
                    <v-list-subheader class="text-caption text-uppercase text-grey mt-2 mb-1 px-4 font-weight-bold">
                        {{ app.name }}
                    </v-list-subheader>

                    <v-list-item
                        v-for="node in app.manifest.nodes"
                        :key="app.id + '.' + node.id"
                        class="draggable-item pl-6"
                        :data-node-id="app.id + '.' + node.id"
                        draggable="true"
                        @dragstart="onDragStart($event, node, app.id)"
                        @dragend="onDragEnd"
                    >
                        <template v-slot:prepend>
                            <v-icon size="small" color="cyan">mdi-function</v-icon>
                        </template>
                        <v-list-item-title class="text-caption font-weight-medium">{{ node.name }}</v-list-item-title>
                        <v-list-item-subtitle style="font-size: 10px;">{{ node.description }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-divider class="my-1"></v-divider>
                </template>

                <v-list-item
                    v-else
                    class="draggable-item"
                    :data-module-id="app.id"
                    draggable="true"
                    @dragstart="onDragStart($event, app, null)"
                    @dragend="onDragEnd"
                >
                    <template v-slot:prepend>
                    <v-icon
                        :color="app.is_premium ? 'yellow' : 'blue'"
                    >mdi-puzzle</v-icon>
                    </template>
                    <v-list-item-title>{{ app.name }}</v-list-item-title>
                    <v-list-item-subtitle>{{ app.description }}</v-list-item-subtitle>

                    <template v-slot:append>
                    <div class="d-flex align-center gap-2">
                        <v-btn
                        v-if="!app.is_core && !app.is_premium"
                        icon="mdi-cloud-upload"
                        variant="text"
                        density="compact"
                        color="cyan"
                        :loading="packagingId === app.id"
                        @click.stop="triggerSmartPublish(app, category.id)"
                        title="Publish to Marketplace"
                        ></v-btn>

                        <v-chip
                        v-if="app.is_premium"
                        color="yellow"
                        label
                        density="compact"
                        >Premium</v-chip>
                        <v-chip
                        v-else-if="app.is_core"
                        color="grey"
                        label
                        density="compact"
                        >Core</v-chip>
                    </div>
                    </template>
                </v-list-item>

              </template>

            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const emit = defineEmits(['publish-request']);

const search = ref('');
const modules = ref([]);
const plugins = ref([]);
const widgets = ref([]);
const triggers = ref([]);
const packagingId = ref(null);

const localization = ref({
  search_modules_placeholder: 'Search components...',
  modules_category_name: 'Modules',
  plugins_category_name: 'Plugins',
  widgets_category_name: 'Widgets',
  triggers_category_name: 'Triggers'
});

const onDragStart = (event, item, appId) => {
  const payload = appId
    ? { type: 'node_v2', id: `${appId}.${item.id}`, label: item.name, moduleId: appId }
    : { type: 'module', id: item.id, label: item.name, moduleId: item.id };

  console.log('Drag started:', payload);
  event.dataTransfer.setData('application/json', JSON.stringify(payload));
  event.dataTransfer.effectAllowed = 'move';
};

const onDragEnd = () => {
  console.log('Drag ended.');
};

const triggerSmartPublish = async (item, categoryId) => {
  try {
    packagingId.value = item.id;
    console.log(`Initiating smart package for ${item.id} from ${categoryId}`);

    const typeMap = {
      'modules': 'module',
      'plugins': 'plugin',
      'widgets': 'widget',
      'triggers': 'trigger'
    };
    const singularType = typeMap[categoryId] || 'module';

    const response = await axios.post('/api/v1/components/package', {
      type: singularType,
      id: item.id
    });

    const packageData = response.data;

    emit('publish-request', {
      source: 'smart_package',
      componentType: singularType,
      data: packageData
    });

  } catch (error) {
    console.error("Smart packaging failed:", error);
  } finally {
    packagingId.value = null;
  }
};

const fetchComponents = async () => {
  try {
    const [modulesRes, pluginsRes, widgetsRes, triggersRes] = await Promise.all([
      axios.get('/api/v1/modules'),
      axios.get('/api/v1/plugins'),
      axios.get('/api/v1/widgets'),
      axios.get('/api/v1/triggers')
    ]);
    modules.value = modulesRes.data;
    plugins.value = pluginsRes.data;
    widgets.value = widgetsRes.data;
    triggers.value = triggersRes.data || [];
  } catch (error) {
    console.error('Error fetching components:', error);
  }
};

onMounted(() => {
  fetchComponents();
});

const componentCategories = computed(() => {
  return [
    { id: 'modules', name: localization.value.modules_category_name, items: modules.value },
    { id: 'plugins', name: localization.value.plugins_category_name, items: plugins.value },
    { id: 'triggers', name: localization.value.triggers_category_name, items: triggers.value },
    { id: 'widgets', name: localization.value.widgets_category_name, items: widgets.value },
  ];
});

const filteredCategories = computed(() => {
  if (!search.value) {
    return componentCategories.value;
  }
  const searchText = search.value.toLowerCase();

  return componentCategories.value.map(category => {
    const filteredItems = category.items.filter(item => {
        const appMatch = item.name.toLowerCase().includes(searchText) ||
                       (item.description && item.description.toLowerCase().includes(searchText));

        let nodesMatch = false;
        if (item.manifest && item.manifest.nodes) {
            nodesMatch = item.manifest.nodes.some(n =>
                n.name.toLowerCase().includes(searchText) ||
                (n.description && n.description.toLowerCase().includes(searchText))
            );
        }

        return appMatch || nodesMatch;
    });
    return { ...category, items: filteredItems };
  }).filter(category => category.items.length > 0);
});
</script>

<style scoped>
.toolbox-card {
  height: 100%;
  max-width: 350px;
  background-color: rgba(255, 255, 255, 0.05) !important;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
}

.draggable-item {
  cursor: grab;
}

.draggable-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.gap-2 {
  gap: 8px;
}
</style>
