<template>
  <BaseModal :title="plant ? 'Edit plant' : 'Add plant'" @close="$emit('close')">
    <form @submit.prevent="submit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
        <input
          v-model="form.name"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Scientific name</label>
        <input
          v-model="form.scientific_name"
          class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
        <select
          v-model="form.location_id"
          class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
        >
          <option :value="null">— None —</option>
          <option
            v-for="loc in locationsStore.locations"
            :key="loc.id"
            :value="loc.id"
          >{{ loc.display_name }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
        <select
          v-model="form.status_id"
          class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
        >
          <option :value="null">— None —</option>
          <option
            v-for="s in statusesStore.statuses"
            :key="s.id"
            :value="s.id"
          >{{ s.name }}</option>
        </select>
      </div>
      <ErrorBanner v-if="error" :message="error" />
      <div class="flex justify-end gap-3 pt-2">
        <button type="button" @click="$emit('close')" class="text-sm text-gray-600 hover:text-gray-800">
          Cancel
        </button>
        <button
          type="submit"
          :disabled="loading"
          class="bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium py-1.5 px-4 rounded-md disabled:opacity-50"
        >
          {{ loading ? 'Saving…' : (plant ? 'Save changes' : 'Add plant') }}
        </button>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { usePlantsStore } from '@/stores/plants'
import { useLocationsStore } from '@/stores/locations'
import { usePlantStatusesStore } from '@/stores/plantStatuses'
import { useApiRequest } from '@/composables/useApiRequest'
import BaseModal from '@/components/ui/BaseModal.vue'
import ErrorBanner from '@/components/ui/ErrorBanner.vue'

const props = defineProps({ plant: Object })
const emit = defineEmits(['close', 'saved'])

const plantsStore = usePlantsStore()
const locationsStore = useLocationsStore()
const statusesStore = usePlantStatusesStore()
const { loading, error, run } = useApiRequest()

const form = reactive({
  name: props.plant?.name || '',
  scientific_name: props.plant?.scientific_name || '',
  location_id: props.plant?.location?.id ?? null,
  status_id: props.plant?.status?.id ?? props.plant?.status_id ?? null,
})

onMounted(() => {
  if (!locationsStore.locations.length) locationsStore.fetchAll()
  statusesStore.fetchAll()
})

async function submit() {
  await run(() =>
    props.plant
      ? plantsStore.update(props.plant.id, form)
      : plantsStore.create(form)
  ).catch(() => {})
  if (!error.value) emit('saved')
}
</script>
