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

    <section v-if="wateringProgress !== null" class="mb-6">
      <div class="flex items-center justify-between mb-1.5">
        <span class="text-sm font-medium text-gray-700">Watering</span>
        <span class="text-xs text-gray-500">{{ wateringProgressLabel }}</span>
      </div>
      <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-300"
          :class="wateringProgressColor"
          :style="{ width: wateringProgressPct + '%' }"
        />
      </div>
    </section>

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
import { useDateFormat } from '@/composables/useDateFormat'
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
const { daysSince } = useDateFormat()

const wateringProgress = computed(() => {
  const p = plant.value
  if (!p?.watering_interval_days || !p?.last_watered) return null
  return daysSince(p.last_watered) / p.watering_interval_days
})

const wateringProgressPct = computed(() => {
  if (wateringProgress.value === null) return 0
  if (daysSince(plant.value?.last_watered) === 0) return 100
  return Math.min(wateringProgress.value * 100, 100)
})

const wateringProgressColor = computed(() => {
  if (wateringProgress.value === null) return ''
  if (daysSince(plant.value?.last_watered) === 0) return 'bg-green-400'
  if (wateringProgress.value >= 1) return 'bg-red-400'
  if (wateringProgress.value >= 0.75) return 'bg-amber-400'
  return 'bg-blue-400'
})

const wateringProgressLabel = computed(() => {
  const p = plant.value
  if (!p?.watering_interval_days || !p?.last_watered) return ''
  const days = daysSince(p.last_watered)
  const interval = p.watering_interval_days
  const remaining = Math.round(interval - days)
  if (remaining <= 0) return `Overdue by ${Math.abs(remaining)} day${Math.abs(remaining) !== 1 ? 's' : ''} · every ${interval} days`
  return `${days} of ${interval} days · due in ${remaining} day${remaining !== 1 ? 's' : ''}`
})
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
