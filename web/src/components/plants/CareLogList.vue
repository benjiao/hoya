<template>
  <div>
    <ConfirmDialog
      v-if="pendingDeleteId"
      message="Delete this care log entry?"
      @confirm="confirmDelete"
      @cancel="pendingDeleteId = null"
    />
    <LoadingSpinner v-if="loading" />
    <p v-else-if="!logs.length" class="text-sm text-gray-400">No care entries yet.</p>
    <ul v-else class="space-y-2">
      <li
        v-for="log in logs"
        :key="log.id"
        class="flex items-start justify-between bg-white border border-gray-100 rounded-lg px-4 py-3 text-sm"
      >
        <div>
          <span
            v-if="log.type"
            :class="log.type === 'watered' ? 'bg-blue-100 text-blue-700' : log.type === 'fertilized' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'"
            class="text-xs font-medium px-2 py-0.5 rounded-full capitalize mr-2"
          >{{ log.type }}</span>
          <span class="text-gray-500">{{ shortDate(log.logged_at) }}</span>
          <p v-if="log.notes" class="text-gray-600 mt-1">{{ log.notes }}</p>
        </div>
        <button
          @click="pendingDeleteId = log.id"
          class="text-gray-300 hover:text-red-500 ml-4 flex-shrink-0 text-xs"
        >Delete</button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usePlantsStore } from '@/stores/plants'
import { useDateFormat } from '@/composables/useDateFormat'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'

const props = defineProps({ plantId: [String, Number] })
const store = usePlantsStore()
const logs = ref([])
const loading = ref(false)
const pendingDeleteId = ref(null)
const { shortDate } = useDateFormat()

async function refresh() {
  loading.value = true
  logs.value = await store.fetchLogs(props.plantId)
  loading.value = false
}

async function confirmDelete() {
  await store.deleteLog(props.plantId, pendingDeleteId.value)
  logs.value = logs.value.filter(l => l.id !== pendingDeleteId.value)
  pendingDeleteId.value = null
}

onMounted(refresh)
defineExpose({ refresh })
</script>
