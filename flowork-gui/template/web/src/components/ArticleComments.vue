//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\components\ArticleComments.vue total lines 589 
//#######################################################################

<template>
  <div class="comments-section" ref="commentsSectionRef">
    <h3 class="orbitron-font section-title">Comments</h3>

    <v-card v-if="authStore.isAuthenticated" variant="outlined" class="mb-6 comment-form-card">
      <v-card-text>
        <v-textarea
          v-model="newCommentContent"
          label="Leave your comment..."
          rows="3"
          variant="filled"
          auto-grow
          hide-details="auto"
          :counter="2000"
          maxlength="2000"
          :error-messages="postError || rateLimitError"
        ></v-textarea>
        <div class="d-flex justify-end mt-2">
          <v-btn
            color="cyan"
            @click="postComment"
            :loading="isPosting"
            :disabled="!newCommentContent.trim()"
            class="action-btn"
          >
            Post Comment
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
    <v-alert v-else type="info" variant="tonal" density="compact" class="mb-6">
        Please <router-link :to="{ name: 'Login', query: { redirect: $route.fullPath }}">login</router-link> to post a comment.
    </v-alert>


    <div v-if="isLoading" class="text-center">
      <v-progress-circular indeterminate color="cyan"></v-progress-circular>
    </div>
    <v-alert v-else-if="fetchError" type="error" variant="tonal">
      Failed to load comments: {{ fetchError }}
    </v-alert>
    <div v-else-if="comments.length === 0" class="text-grey text-center">
      Be the first to comment!
    </div>

    <v-slide-y-transition group tag="div" class="comment-list">
      <v-card
        v-for="comment in comments"
        :key="comment.id"
        class="mb-4 comment-card"
        variant="outlined"
      >
        <v-card-text class="pb-0">
          <div class="d-flex align-center mb-2">
            <v-avatar size="32" class="mr-3" color="blue-grey-darken-3">
               <v-icon icon="mdi-account-circle"></v-icon>
            </v-avatar>
            <div>
              <div class="comment-author">{{ formatAuthor(comment.author_username) }}</div>
              <div class="comment-date">{{ timeAgo(comment.created_at) }}</div>
            </div>
            <v-spacer></v-spacer>

             <v-tooltip v-if="isAuthor(comment)" text="Edit Comment" location="top">
                <template v-slot:activator="{ props: tooltipProps }">
                    <v-btn
                        v-bind="tooltipProps"
                        icon="mdi-pencil-outline"
                        variant="text"
                        size="small"
                        color="grey-lighten-1"
                        @click="startEdit(comment)"
                        :loading="editingCommentId === comment.id && isUpdating"
                        class="ml-2"
                    ></v-btn>
                </template>
            </v-tooltip>

             <v-tooltip v-if="isAuthor(comment) || isModerator" text="Delete Comment" location="top">
                <template v-slot:activator="{ props: tooltipProps }">
                    <v-btn
                        v-bind="tooltipProps"
                        icon="mdi-delete-outline"
                        variant="text"
                        size="small"
                        color="red-lighten-2"
                        @click="deleteComment(comment.id)"
                        :loading="deletingCommentId === comment.id"
                        class="ml-1"
                    ></v-btn>
                </template>
            </v-tooltip>
          </div>

          <div class="comment-content">
             <div v-if="editingCommentId === comment.id">
                <v-textarea
                  v-model="editingCommentContent"
                  variant="outlined"
                  rows="3"
                  auto-grow
                  hide-details="auto"
                  :counter="2000"
                  maxlength="2000"
                  class="mb-2"
                ></v-textarea>
                <v-btn size="small" variant="text" @click="cancelEdit">Cancel</v-btn>
                <v-btn
                    size="small"
                    color="cyan"
                    @click="saveEdit(comment)"
                    :loading="isUpdating"
                    class="action-btn"
                >Save</v-btn>
              </div>
              <div v-else>
                <span v-if="!comment.expanded && comment.content.length > 300" v-html="linkify(comment.content.substring(0, 300) + '...')"></span>
                <span v-else v-html="linkify(comment.content)"></span>
                <v-btn
                    v-if="comment.content.length > 300"
                    variant="text"
                    size="small"
                    @click="toggleExpand(comment)"
                    class="read-more-btn"
                >
                    {{ comment.expanded ? 'Show Less' : 'Read More' }}
                </v-btn>
             </div>
          </div>
        </v-card-text>

        <v-card-actions class="comment-actions">
           <v-tooltip text="Upvote" location="top">
                <template v-slot:activator="{ props: tooltipProps }">
                    <v-btn
                        v-bind="tooltipProps"
                        icon="mdi-arrow-up-bold-outline"
                        variant="text"
                        size="small"
                        :color="comment.userVote === 'up' ? 'success' : 'grey'"
                        @click="voteComment(comment.id, 'up')"
                        :loading="votingCommentId === comment.id && votingType === 'up'"
                        :disabled="!authStore.isAuthenticated"
                    ></v-btn>
                 </template>
            </v-tooltip>
          <span class="comment-score mx-1" :class="getScoreColor(comment.score)">{{ comment.score }}</span>
          <v-tooltip text="Downvote" location="top">
                <template v-slot:activator="{ props: tooltipProps }">
                    <v-btn
                        v-bind="tooltipProps"
                        icon="mdi-arrow-down-bold-outline"
                        variant="text"
                        size="small"
                        :color="comment.userVote === 'down' ? 'error' : 'grey'"
                        @click="voteComment(comment.id, 'down')"
                        :loading="votingCommentId === comment.id && votingType === 'down'"
                        :disabled="!authStore.isAuthenticated"
                    ></v-btn>
                 </template>
            </v-tooltip>

          <v-spacer></v-spacer>

          <v-tooltip text="Flag Comment" location="top">
             <template v-slot:activator="{ props: tooltipProps }">
                <v-btn
                    v-bind="tooltipProps"
                    icon="mdi-flag-outline"
                    variant="text"
                    size="small"
                    color="grey"
                    @click="flagComment(comment.id)"
                    :loading="flaggingCommentId === comment.id"
                    :disabled="!authStore.isAuthenticated"
                ></v-btn>
             </template>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-slide-y-transition>

    <v-dialog v-model="showLinkWarning" max-width="500">
      <v-card>
        <v-card-title class="headline orbitron-font">External Link Warning</v-card-title>
        <v-card-text>
          You are about to leave Flowork and navigate to the following external URL. Flowork is not responsible for the content of external sites.
          <div class="mt-2 text-caption text-grey-lighten-1" style="word-break: break-all;">{{ externalLinkTarget }}</div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showLinkWarning = false">Cancel</v-btn>
          <v-btn color="primary" @click="proceedToExternalLink">Proceed</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, reactive, nextTick } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useLocaleStore } from '@/store/locale';
import { apiGetComments, apiPostComment, apiVoteComment, apiFlagComment, apiDeleteComment, apiUpdateComment } from '@/api';
import linkifyIt from 'linkify-it';
import tlds from 'tlds';
import { useUiStore } from '@/store/ui';

const props = defineProps({
  articleId: { type: String, required: true },
  articleSlug: { type: String, required: true },
  articleAuthorId: { type: String, default: '' }
});

const authStore = useAuthStore();
const localeStore = useLocaleStore();
const uiStore = useUiStore();
const t = localeStore.loc;

const comments = ref([]);
const isLoading = ref(true);
const fetchError = ref(null);
const newCommentContent = ref('');
const isPosting = ref(false);
const postError = ref('');
const rateLimitError = ref('');

const votingCommentId = ref(null);
const votingType = ref(null);
const flaggingCommentId = ref(null);
const deletingCommentId = ref(null);

const editingCommentId = ref(null);
const editingCommentContent = ref('');
const isUpdating = ref(false);

const showLinkWarning = ref(false);
const externalLinkTarget = ref('');

const linkifyInstance = linkifyIt();
linkifyInstance.tlds(tlds);

async function postComment() {
  if (!newCommentContent.value.trim() || !authStore.isAuthenticated) return;
  isPosting.value = true;
  postError.value = '';
  rateLimitError.value = '';
  try {
    const result = await apiPostComment(props.articleSlug, newCommentContent.value, null);
    if (result.error) {
        if (result.status === 429) {
            rateLimitError.value = result.error || 'Rate limit exceeded.';
            uiStore.showNotification({ text: rateLimitError.value, color: 'error' });
        } else {
            postError.value = result.error || `HTTP error ${result.status}`;
            uiStore.showNotification({ text: postError.value, color: 'error' });
        }
        throw new Error(result.error || `HTTP error ${result.status}`);
     }
    comments.value.unshift(reactive({ ...result, expanded: false, userVote: null }));
    newCommentContent.value = '';
  } catch (err) {
    console.error("Failed to post comment:", err);
    if (!postError.value && !rateLimitError.value) {
        const errorMsg = err.message || "Could not post comment.";
        postError.value = errorMsg;
        uiStore.showNotification({ text: errorMsg, color: 'error' });
    }
  } finally {
    isPosting.value = false;
  }
}

async function voteComment(commentId, type) {
    if (!authStore.isAuthenticated) return;
    votingCommentId.value = commentId;
    votingType.value = type;
     try {
         const result = await apiVoteComment(commentId, type);
         if (result.error) throw new Error(result.error || `HTTP error ${result.status}`);
         const comment = comments.value.find(c => c.id === commentId);
         if (comment) {
            if (comment.userVote === type) { comment.score += (type === 'up' ? -1 : 1); comment.userVote = null; }
            else if (comment.userVote) { comment.score += (type === 'up' ? 2 : -2); comment.userVote = type; }
            else { comment.score += (type === 'up' ? 1 : -1); comment.userVote = type; }
         }
     } catch (err) {
         console.error("Failed to vote:", err);
         uiStore.showNotification({ text: `Error voting: ${err.message}`, color: 'error' });
     } finally {
         votingCommentId.value = null;
         votingType.value = null;
     }
}

async function flagComment(commentId) {
    if (!authStore.isAuthenticated) return;
    if (!confirm("Are you sure you want to flag this comment as inappropriate?")) return;
    flaggingCommentId.value = commentId;
    try {
        const result = await apiFlagComment(commentId);
        if (result.error && result.status !== 409) {
             throw new Error(result.error || `HTTP error ${result.status}`);
        }
        if (result.status === 409) {
            uiStore.showNotification({ text: result.message, color: 'info' });
        } else {
             uiStore.showNotification({ text: "Comment flagged successfully.", color: 'success' });
        }
    } catch (err) {
        console.error("Failed to flag comment:", err);
        uiStore.showNotification({ text: `An error occurred: ${err.message}`, color: 'error' });
    } finally {
        flaggingCommentId.value = null;
    }
}

async function deleteComment(commentId) {
    if (!authStore.isAuthenticated) return;
    if (!confirm("Are you sure you want to permanently delete this comment?")) return;
    deletingCommentId.value = commentId;
     try {
        const result = await apiDeleteComment(commentId);
        if (result.error) throw new Error(result.error || `HTTP error ${result.status}`);
        comments.value = comments.value.filter(c => c.id !== commentId);
        uiStore.showNotification({ text: "Comment deleted.", color: 'info' });
     } catch (err) {
        console.error("Failed to delete comment:", err);
        uiStore.showNotification({ text: `Error deleting: ${err.message}`, color: 'error' });
     } finally {
         deletingCommentId.value = null;
     }
}

function startEdit(comment) {
  editingCommentId.value = comment.id;
  editingCommentContent.value = comment.content;
}

function cancelEdit() {
  editingCommentId.value = null;
  editingCommentContent.value = '';
}

async function saveEdit(comment) {
  if (!editingCommentContent.value.trim()) {
      uiStore.showNotification({ text: "Comment cannot be empty.", color: 'error' });
      return;
  }
  isUpdating.value = true;
  try {
    const result = await apiUpdateComment(comment.id, editingCommentContent.value);
    if (result.error) throw new Error(result.error);
    comment.content = editingCommentContent.value;
    uiStore.showNotification({ text: 'Comment updated!', color: 'success' });
    cancelEdit();
  } catch (err) {
    console.error("Failed to update comment:", err);
    uiStore.showNotification({ text: `Update failed: ${err.message}`, color: 'error' });
  } finally {
      isUpdating.value = false;
  }
}

function toggleExpand(comment) {
  comment.expanded = !comment.expanded;
}

function formatAuthor(address) {
  if (!address) return 'Anonymous';
  if (address.startsWith('0x') && address.length === 42) {
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  }
  return address;
}

function timeAgo(dateString) {
  const date = new Date(dateString);
  const seconds = Math.floor((new Date() - date) / 1000);
  let interval = seconds / 31536000;
  if (interval > 1) return Math.floor(interval) + " years ago";
  interval = seconds / 2592000;
  if (interval > 1) return Math.floor(interval) + " months ago";
  interval = seconds / 86400;
  if (interval > 1) return Math.floor(interval) + " days ago";
  interval = seconds / 3600;
  if (interval > 1) return Math.floor(interval) + " hours ago";
  interval = seconds / 60;
  if (interval > 1) return Math.floor(interval) + " minutes ago";
  return seconds < 5 ? "just now" : Math.floor(seconds) + " seconds ago";
}


function getScoreColor(score) {
  if (score > 0) return 'text-success';
  if (score < 0) return 'text-error';
  return 'text-grey';
}

const isAuthor = (comment) => {
    return authStore.isAuthenticated && comment.author_id?.toLowerCase() === authStore.user.id?.toLowerCase();
};

const isModerator = computed(() => {
    return authStore.isAuthenticated && props.articleAuthorId?.toLowerCase() === authStore.user.id?.toLowerCase();
});

function linkify(text) {
  const matches = linkifyInstance.match(text);
  if (!matches) {
    return escapeHtml(text);
  }
  let result = '';
  let lastIndex = 0;
  matches.forEach(match => {
    result += escapeHtml(text.slice(lastIndex, match.index));
    result += `<a href="${escapeHtml(match.url)}" target="_blank" rel="nofollow noopener noreferrer" data-external-link="true" data-url="${escapeHtml(match.url)}">${escapeHtml(match.text)}</a>`;
    lastIndex = match.lastIndex;
  });
  result += escapeHtml(text.slice(lastIndex));
  return result;
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function handleLinkClick(event) {
    const target = event.target.closest('a[data-external-link="true"]');
    if (target) {
        event.preventDefault();
        externalLinkTarget.value = target.dataset.url;
        showLinkWarning.value = true;
    }
}

function proceedToExternalLink() {
    if (externalLinkTarget.value) {
        window.open(externalLinkTarget.value, '_blank', 'noopener,noreferrer');
    }
    showLinkWarning.value = false;
    externalLinkTarget.value = '';
}

const commentsSectionRef = ref(null);

onMounted(() => {
    fetchComments();
    nextTick(() => {
        if (commentsSectionRef.value) {
            commentsSectionRef.value.addEventListener('click', handleLinkClick);
        }
    });
});

onUnmounted(() => {
    if (commentsSectionRef.value) {
         commentsSectionRef.value.removeEventListener('click', handleLinkClick);
    }
});

async function fetchComments() {
  isLoading.value = true;
  fetchError.value = null;
  try {
    const result = await apiGetComments(props.articleSlug);
    if (result.error) throw new Error(result.error);
    comments.value = result.map(c => reactive({ ...c, expanded: false, userVote: null }));
    console.log("[Comments] Successfully loaded comments:", comments.value); // English Log
  } catch (err) {
    console.error("[Comments] Failed to load comments:", err); // English Log
    fetchError.value = err.message;
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.comments-section {
  margin-top: 40px;
  position: relative;
}
.section-title {
  color: #00f5ff;
  border-bottom: 1px solid rgba(0, 245, 255, 0.2);
  padding-bottom: 8px;
  margin-bottom: 24px;
}
.comment-form-card {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.action-btn {
  font-weight: bold;
  color: #000 !important;
}
.comment-list {
  padding-top: 10px;
}
.comment-card {
  background: rgba(23, 33, 65, 0.7);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 245, 255, 0.15);
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}
.comment-card::before {
  content: '';
  position: absolute;
  top: -50%; left: -50%;
  width: 200%; height: 200%;
  background: conic-gradient(
    transparent,
    rgba(0, 245, 255, 0.1),
    transparent 30%
  );
  animation: rotate 6s linear infinite;
  opacity: 0;
  transition: opacity 0.5s ease;
}
.comment-card:hover::before {
    opacity: 1;
}
@keyframes rotate {
  100% { transform: rotate(360deg); }
}
.comment-author {
  font-weight: 600;
  color: #e0e0e0;
}
.comment-date {
  font-size: 0.75rem;
  color: #94A3B8;
}
.comment-content {
  color: #cfcfcf;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  padding-top: 8px;
}
.read-more-btn {
    color: #00f5ff;
    padding: 0;
    height: auto;
    font-size: 0.8rem;
    margin-left: 4px;
    text-transform: none;
}
:deep(.comment-content a[data-external-link="true"]) {
    color: #64ffda;
    text-decoration: none;
    border-bottom: 1px dashed rgba(100, 255, 218, 0.5);
    transition: all 0.2s ease;
}
:deep(.comment-content a[data-external-link="true"]:hover) {
    color: #ffffff;
    background-color: rgba(100, 255, 218, 0.1);
    border-bottom-style: solid;
}
.comment-actions {
  padding-top: 0;
  padding-bottom: 8px;
  min-height: 40px;
}
.comment-score {
    font-family: 'Orbitron', monospace;
    font-size: 0.9rem;
    min-width: 20px;
    text-align: center;
}
.orbitron-font { font-family: 'Orbitron', monospace; }
</style>
