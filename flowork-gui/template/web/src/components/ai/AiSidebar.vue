//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ai\AiSidebar.vue total lines 91 
//#######################################################################

<template>
    <v-navigation-drawer v-model="drawer" color="#050505" width="280" class="border-r-thin" floating>
        <div class="pa-4">
            <v-btn block rounded="xl" color="#1a1a1a" class="text-none justify-start text-grey-lighten-1 new-chat-btn mb-4" height="44" variant="tonal" @click="aiCenterStore.createNewSession()">
                <v-icon start icon="mdi-plus" color="#D4AF37"></v-icon> New chat
            </v-btn>
            <div class="text-caption font-weight-bold text-grey-darken-1 mb-2 ml-2">Recent</div>
            <div v-if="sessions.length === 0" class="text-caption text-grey-darken-2 text-center mt-4 italic">No history yet.</div>

            <v-list bg-color="transparent" density="compact" class="history-list">
                <v-hover v-for="session in sessions" :key="session.id" v-slot="{ isHovering, props }">
                    <v-list-item v-bind="props" rounded="lg" :active="currentSessionId === session.id" active-class="active-session-item" class="mb-1 history-item" @click="aiCenterStore.switchSession(session.id)">
                        <template v-slot:prepend><v-icon icon="mdi-message-outline" size="small" class="mr-3 text-grey-darken-1"></v-icon></template>

                        <v-list-item-title v-if="renamingId !== session.id" @dblclick="startRename(session)" class="text-body-2 text-grey-lighten-2 text-truncate cursor-pointer" title="Double click to rename">
                            {{ session.title }}
                        </v-list-item-title>
                        <v-text-field
                            v-else v-model="renameTemp" density="compact" variant="plain" class="pa-0 ma-0 text-body-2" hide-details autofocus
                            @blur="saveRename(session)" @keydown.enter="saveRename(session)" @click.stop
                        ></v-text-field>

                        <template v-slot:append>
                            <div v-if="isHovering || currentSessionId === session.id">
                                <v-menu location="end">
                                    <template v-slot:activator="{ props }"><v-btn icon v-bind="props" variant="text" density="compact" size="small" color="grey"><v-icon icon="mdi-dots-vertical" size="small"></v-icon></v-btn></template>
                                    <v-list bg-color="#2d2e30" density="compact" class="rounded-lg border-thin">
                                        <v-list-item @click.stop="startRename(session)"><template v-slot:prepend><v-icon icon="mdi-pencil" size="small"></v-icon></template><v-list-item-title>Rename</v-list-item-title></v-list-item>
                                        <v-list-item @click.stop="aiCenterStore.deleteSession(session.id)" class="text-red-accent-2"><template v-slot:prepend><v-icon icon="mdi-delete-outline" size="small"></v-icon></template><v-list-item-title>Delete</v-list-item-title></v-list-item>
                                    </v-list>
                                </v-menu>
                            </div>
                        </template>
                    </v-list-item>
                </v-hover>
            </v-list>
        </div>
        <template v-slot:append>
            <div class="pa-4 text-caption text-grey-darken-2">
                <div class="d-flex align-center mb-1"><v-icon icon="mdi-map-marker" size="x-small" class="mr-1"></v-icon> Jakarta, ID</div>
                <div class="font-mono" style="font-size: 10px;">Flowork Neural v3.5 (Gold Edition)</div>
            </div>
        </template>
    </v-navigation-drawer>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAiCenterStore } from '@/store/aiCenter';
import { storeToRefs } from 'pinia';

const props = defineProps(['modelValue']);
const emit = defineEmits(['update:modelValue']);

const aiCenterStore = useAiCenterStore();
const { sessions, currentSessionId } = storeToRefs(aiCenterStore);

const drawer = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
});

const renamingId = ref(null);
const renameTemp = ref('');

function startRename(session) {
    renamingId.value = session.id;
    renameTemp.value = session.title;
}

function saveRename(session) {
    if (renamingId.value) {
        aiCenterStore.renameSession(session.id, renameTemp.value);
        renamingId.value = null;
    }
}
</script>

<style scoped>
.new-chat-btn:hover { background-color: #333435 !important; color: white !important; border: 1px solid #D4AF37; }
.history-item:hover { background-color: #2d2e30; }
.active-session-item { background-color: transparent !important; border-left: 2px solid #D4AF37; }
.cursor-pointer { cursor: pointer; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
</style>
