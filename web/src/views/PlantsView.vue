<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-semibold text-gray-900">Plants</h1>
      <button
        @click="showCreate = true"
        class="bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium py-1.5 px-4 rounded-md"
      >+ Add plant</button>
    </div>

    <div class="flex gap-3 mb-6">
      <input
        v-model="search"
        type="search"
        placeholder="Search plants…"
        class="flex-1 rounded-md border-gray-300 text-sm shadow-sm focus:ring-brand-500 focus:border-brand-500"
      />
      <select
        v-model="sortBy"
        class="rounded-md border-gray-300 text-sm shadow-sm focus:ring-brand-500 focus:border-brand-500"
      >
        <option value="name_asc">A → Z</option>
        <option value="name_desc">Z → A</option>
        <option value="last_watered_desc">Last watered ↓</option>
        <option value="last_watered_asc">Last watered ↑</option>
        <option value="watering_due">Due for watering</option>
      </select>
    </div>

    <LoadingSpinner v-if="store.loading" />
    <ErrorBanner v-else-if="store.error" :message="store.error" />
    <p v-else-if="store.plants.length === 0" class="text-gray-500 text-sm">
      No plants yet. Add your first plant!
    </p>
    <p v-else-if="displayedPlants.length === 0" class="text-gray-500 text-sm">
      No plants match your search.
    </p>
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <PlantCard
        v-for="plant in displayedPlants"
        :key="plant.id"
        :plant="plant"
        @edit="openEdit"
        @delete="confirmDelete"
      />
    </div>

    <PlantModal
      v-if="showCreate"
      :plant="null"
      @close="showCreate = false"
      @saved="showCreate = false"
    />
    <PlantModal
      v-if="editingPlant"
      :plant="editingPlant"
      @close="editingPlant = null"
      @saved="editingPlant = null"
    />
    <ConfirmDialog
      v-if="deletingPlant"
      :message="`Delete '${deletingPlant.name}'? This cannot be undone.`"
      @confirm="doDelete"
      @cancel="deletingPlant = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePlantsStore } from '@/stores/plants'
import { useDateFormat } from '@/composables/useDateFormat'
import PlantCard from '@/components/plants/PlantCard.vue'
import PlantModal from '@/components/plants/PlantModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ErrorBanner from '@/components/ui/ErrorBanner.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'

const route = useRoute()
const router = useRouter()
const store = usePlantsStore()
const showCreate = ref(false)
const editingPlant = ref(null)
const deletingPlant = ref(null)

const { daysSince } = useDateFormat()

const VALID_SORTS = ['name_asc', 'name_desc', 'last_watered_desc', 'last_watered_asc', 'watering_due']
const DEFAULT_SORT = 'watering_due'
const search = ref(route.query.q || '')
const sortBy = ref(VALID_SORTS.includes(route.query.sort) ? route.query.sort : DEFAULT_SORT)

watch([search, sortBy], ([q, sort]) => {
  router.replace({ query: { ...(q ? { q } : {}), ...(sort !== DEFAULT_SORT ? { sort } : {}) } })
})

const displayedPlants = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list = store.plants

  if (q) {
    list = list.filter(p =>
      p.name.toLowerCase().includes(q) ||
      (p.scientific_name || '').toLowerCase().includes(q) ||
      (p.location_display_name || '').toLowerCase().includes(q)
    )
  }

  return [...list].sort((a, b) => {
    if (sortBy.value === 'name_desc') return b.name.localeCompare(a.name)
    if (sortBy.value === 'last_watered_desc' || sortBy.value === 'last_watered_asc') {
      const asc = sortBy.value === 'last_watered_asc'
      if (a.location_skip_watering !== b.location_skip_watering) return a.location_skip_watering ? 1 : -1
      if (!a.last_watered && !b.last_watered) return 0
      if (!a.last_watered) return asc ? -1 : 1
      if (!b.last_watered) return asc ? 1 : -1
      const diff = new Date(a.last_watered) - new Date(b.last_watered)
      return asc ? diff : -diff
    }
    if (sortBy.value === 'watering_due') {
      const key = p => {
        if (p.location_skip_watering) return [3, 0]
        if (!p.watering_interval_days || !p.last_watered) return [2, 0]
        if (daysSince(p.last_watered) === 0) return [1, 0]
        return [0, p.watering_interval_days - daysSince(p.last_watered)]
      }
      const [aPri, aVal] = key(a)
      const [bPri, bVal] = key(b)
      return aPri !== bPri ? aPri - bPri : aVal - bVal
    }
    return a.name.localeCompare(b.name)
  })
})

onMounted(() => store.fetchAll())

function openEdit(plant) { editingPlant.value = plant }
function confirmDelete(plant) { deletingPlant.value = plant }
async function doDelete() {
  await store.remove(deletingPlant.value.id)
  deletingPlant.value = null
}
</script>
