<template>
  <div>
    <div class="flex items-start justify-between mb-6 gap-4">
      <div>
        <RouterLink to="/locations" class="text-sm text-brand-600 hover:underline">&larr; All locations</RouterLink>
        <div v-if="location" class="mt-1">
          <p v-if="location.path_names.length > 1" class="text-xs text-gray-400">
            {{ location.path_names.slice(0, -1).join(' > ') }}
          </p>
          <h1 class="text-2xl font-bold text-gray-900">{{ location.name }}</h1>
          <span
            v-if="location.skip_watering"
            class="inline-block mt-1 text-xs bg-amber-50 text-amber-700 rounded-full px-2 py-0.5"
          >Skip watering monitoring</span>
        </div>
      </div>
      <div v-if="location" class="flex gap-2 flex-shrink-0">
        <button @click="openEdit(location)" class="text-sm text-brand-600 hover:underline">Edit</button>
        <button @click="deletingLocation = location" class="text-sm text-red-500 hover:underline">Delete</button>
      </div>
    </div>

    <LoadingSpinner v-if="store.loading" />
    <ErrorBanner v-else-if="store.error" :message="store.error" />
    <template v-else-if="location">
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-base font-semibold text-gray-800">Child locations</h2>
          <button
            @click="openCreate(location.id)"
            class="text-sm bg-brand-600 hover:bg-brand-700 text-white px-3 py-1 rounded-md"
          >+ Add child</button>
        </div>
        <p v-if="!children.length" class="text-sm text-gray-400">No child locations.</p>
        <ul v-else class="space-y-1">
          <li
            v-for="child in children"
            :key="child.id"
            class="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-gray-50"
          >
            <RouterLink
              :to="`/locations/${child.id}`"
              class="text-sm font-medium text-gray-800 hover:text-brand-600"
            >{{ child.name }}</RouterLink>
            <div class="flex gap-2 text-xs text-gray-400">
              <button @click="openCreate(child.id)" class="hover:text-brand-600">+ Child</button>
              <button @click="openEdit(child)" class="hover:text-brand-600">Edit</button>
              <button @click="deletingLocation = child" class="hover:text-red-500">Delete</button>
            </div>
          </li>
        </ul>
      </section>
    </template>

    <LocationModal
      v-if="modalOpen"
      :location="editingLocation"
      :parent-id="newParentId"
      @close="modalOpen = false"
      @saved="modalOpen = false"
    />
    <ConfirmDialog
      v-if="deletingLocation"
      :message="`Delete '${deletingLocation.name}'? Child locations will become root-level.`"
      @confirm="doDelete"
      @cancel="deletingLocation = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLocationsStore } from '@/stores/locations'
import LocationModal from '@/components/locations/LocationModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ErrorBanner from '@/components/ui/ErrorBanner.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'

const props = defineProps({ id: String })
const store = useLocationsStore()
const router = useRouter()

const location = computed(() =>
  store.locations.find(l => String(l.id) === String(props.id))
)
const children = computed(() =>
  store.locations.filter(l => l.parent?.id === Number(props.id))
)

const modalOpen = ref(false)
const editingLocation = ref(null)
const newParentId = ref(null)
const deletingLocation = ref(null)

onMounted(async () => {
  if (!store.locations.length) await store.fetchAll()
})

function openCreate(parentId) {
  editingLocation.value = null
  newParentId.value = parentId
  modalOpen.value = true
}

function openEdit(loc) {
  editingLocation.value = loc
  newParentId.value = null
  modalOpen.value = true
}

async function doDelete() {
  const isCurrentPage = deletingLocation.value.id === Number(props.id)
  await store.remove(deletingLocation.value.id)
  deletingLocation.value = null
  if (isCurrentPage) router.push('/locations')
}
</script>
