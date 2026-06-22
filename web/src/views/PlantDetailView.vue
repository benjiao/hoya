<template>
  <div v-if="store.loading" class="py-12 text-center">
    <LoadingSpinner />
  </div>
  <ErrorBanner v-else-if="store.error" :message="store.error" />
  <div v-else-if="store.currentPlant">
    <div class="flex items-start justify-between mb-6 gap-4">
      <div>
        <RouterLink to="/plants" class="text-sm text-brand-600 hover:underline">&larr; All plants</RouterLink>
        <h1 class="text-2xl font-bold text-gray-900 mt-1">{{ plant.name }}</h1>
        <p v-if="plant.scientific_name" class="text-sm italic text-gray-400">{{ plant.scientific_name }}</p>
        <p v-if="plant.location" class="text-sm text-gray-500 mt-1">{{ plant.location.display_name }}</p>
      </div>
      <div class="flex gap-2 flex-shrink-0">
        <button @click="showEdit = true" class="text-sm text-brand-600 hover:underline">Edit</button>
        <button @click="showDelete = true" class="text-sm text-red-500 hover:underline">Delete</button>
      </div>
    </div>

    <section class="mb-8">
      <h2 class="text-base font-semibold text-gray-800 mb-3">Photos</h2>
      <PlantImages :plant="plant" />
    </section>

    <section>
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-base font-semibold text-gray-800">Care log</h2>
        <button
          @click="showLog = true"
          class="text-sm bg-brand-600 hover:bg-brand-700 text-white px-3 py-1 rounded-md"
        >+ Log care</button>
      </div>
      <CareLogList :plant-id="plant.id" ref="careLogRef" />
    </section>

    <PlantModal
      v-if="showEdit"
      :plant="plant"
      @close="showEdit = false"
      @saved="onEdited"
    />
    <CareLogModal
      v-if="showLog"
      :plant-id="plant.id"
      @close="showLog = false"
      @saved="onLogSaved"
    />
    <ConfirmDialog
      v-if="showDelete"
      :message="`Delete '${plant.name}'?`"
      @confirm="doDelete"
      @cancel="showDelete = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlantsStore } from '@/stores/plants'
import PlantModal from '@/components/plants/PlantModal.vue'
import PlantImages from '@/components/plants/PlantImages.vue'
import CareLogList from '@/components/plants/CareLogList.vue'
import CareLogModal from '@/components/plants/CareLogModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ErrorBanner from '@/components/ui/ErrorBanner.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'

const props = defineProps({ id: String })
const store = usePlantsStore()
const router = useRouter()
const plant = computed(() => store.currentPlant)
const showEdit = ref(false)
const showLog = ref(false)
const showDelete = ref(false)
const careLogRef = ref(null)

onMounted(() => store.fetchOne(props.id))

function onEdited() { showEdit.value = false; store.fetchOne(props.id) }
function onLogSaved() { showLog.value = false; careLogRef.value?.refresh() }
async function doDelete() {
  await store.remove(props.id)
  router.push('/plants')
}
</script>
