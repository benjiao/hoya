<template>
  <div>
    <div class="flex flex-wrap gap-3 mb-3">
      <div
        v-for="img in plant.images"
        :key="img.id"
        class="relative group w-28 h-28"
      >
        <img
          :src="img.image"
          :alt="img.caption || plant.name"
          class="w-full h-full object-cover rounded-lg"
        />
        <button
          @click="remove(img.id)"
          class="absolute top-1 right-1 bg-black/60 text-white text-xs rounded px-1 opacity-0 group-hover:opacity-100 transition"
          title="Remove"
        >&times;</button>
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { usePlantsStore } from '@/stores/plants'
import { extractError } from '@/composables/useApiRequest'

const props = defineProps({ plant: Object })
const store = usePlantsStore()
const uploading = ref(false)
const uploadError = ref(null)

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
</script>
