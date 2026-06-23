<template>
  <div>
    <div class="flex flex-wrap gap-3 mb-3">
      <div
        v-for="img in plant.images"
        :key="img.id"
        class="relative group w-28 h-28 cursor-pointer"
        @click="open(img)"
      >
        <img
          :src="img.image"
          :alt="img.caption || plant.name"
          class="w-full h-full object-cover rounded-lg"
        />
        <button
          @click.stop="remove(img.id)"
          class="absolute top-1 right-1 bg-black/60 text-white text-xs rounded px-1 opacity-0 group-hover:opacity-100 transition"
          title="Remove"
        >&times;</button>
        <!-- Thumbnail indicator -->
        <span
          v-if="img.id === effectiveThumbnailId"
          class="absolute bottom-1 left-1 bg-black/60 text-white text-xs rounded px-1 pointer-events-none"
        >★</span>
        <!-- Set as thumbnail button (non-thumbnail images only) -->
        <button
          v-else
          @click.stop="setThumbnail(img)"
          class="absolute bottom-1 left-1 bg-black/60 text-white text-xs rounded px-1 opacity-0 group-hover:opacity-100 transition"
          title="Set as thumbnail"
        >★</button>
      </div>
    </div>
    <label class="cursor-pointer inline-flex items-center gap-1 text-sm text-brand-600 hover:underline">
      <input
        type="file"
        accept="image/*"
        class="hidden"
        :disabled="uploading"
        @change="upload"
      />
      {{ uploading ? 'Uploading…' : '+ Add photo' }}
    </label>
    <p v-if="uploadError" class="text-xs text-red-600 mt-1">{{ uploadError }}</p>

    <Teleport to="body">
      <div
        v-if="selected"
        class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center"
        @click.self="close"
      >
        <button
          @click="close"
          class="absolute top-4 right-4 text-white text-3xl leading-none hover:text-gray-300"
        >&times;</button>
        <div class="flex flex-col items-center max-w-[90vw] max-h-[90vh]">
          <img
            :src="selected.image"
            :alt="selected.caption || plant.name"
            class="max-w-full max-h-[85vh] object-contain rounded-lg"
          />
          <p v-if="selected.caption" class="text-white text-sm mt-2">{{ selected.caption }}</p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePlantsStore } from '@/stores/plants'
import { extractError } from '@/composables/useApiRequest'

const props = defineProps({ plant: Object })
const store = usePlantsStore()
const uploading = ref(false)
const uploadError = ref(null)
const selected = ref(null)

const effectiveThumbnailId = computed(() =>
  props.plant.thumbnail_image_id ?? props.plant.images[0]?.id ?? null
)

function open(img) { selected.value = img }
function close() { selected.value = null }

function onKeydown(e) { if (e.key === 'Escape') close() }
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

async function upload(e) {
  const file = e.target.files[0]
  if (!file) return
  uploading.value = true
  uploadError.value = null
  try {
    await store.uploadImage(props.plant.id, file)
  } catch (err) {
    uploadError.value = extractError(err)
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

async function remove(imageId) {
  await store.deleteImage(props.plant.id, imageId)
}

async function setThumbnail(img) {
  await store.setThumbnail(props.plant.id, img.id, img.image)
}
</script>
