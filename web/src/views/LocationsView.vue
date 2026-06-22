<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-semibold text-gray-900">Locations</h1>
      <button
        @click="openCreate(null)"
        class="bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium py-1.5 px-4 rounded-md"
      >+ Add location</button>
    </div>

    <LoadingSpinner v-if="store.loading" />
    <ErrorBanner v-else-if="store.error" :message="store.error" />
    <p v-else-if="!tree.length" class="text-sm text-gray-400">No locations yet.</p>
    <LocationTree
      v-else
      :nodes="tree"
      @create-child="openCreate"
      @edit="openEdit"
      @delete="confirmDelete"
    />

    <LocationModal
      v-if="modalOpen"
      :location="editingLocation"
      :parent-id="newParentId"
      @close="modalOpen = false"
      @saved="onSaved"
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
import { useLocationsStore } from '@/stores/locations'
import LocationTree from '@/components/locations/LocationTree.vue'
import LocationModal from '@/components/locations/LocationModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ErrorBanner from '@/components/ui/ErrorBanner.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'

const store = useLocationsStore()
const tree = computed(() => store.getTree())
const modalOpen = ref(false)
const editingLocation = ref(null)
const newParentId = ref(null)
const deletingLocation = ref(null)

onMounted(() => store.fetchAll())

function openCreate(parentId) {
  editingLocation.value = null
  newParentId.value = parentId
  modalOpen.value = true
}
function openEdit(location) {
  editingLocation.value = location
  newParentId.value = null
  modalOpen.value = true
}
function confirmDelete(location) { deletingLocation.value = location }
function onSaved() { modalOpen.value = false }
async function doDelete() {
  await store.remove(deletingLocation.value.id)
  deletingLocation.value = null
}
</script>
