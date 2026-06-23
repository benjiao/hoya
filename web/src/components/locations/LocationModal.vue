<template>
  <BaseModal :title="location ? 'Edit location' : 'Add location'" @close="$emit('close')">
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
        <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
          <input type="checkbox" v-model="form.skip_watering" class="rounded" />
          Skip watering monitoring (e.g. prop box, storage)
        </label>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Parent location</label>
        <select
          v-model="form.parent_id"
          class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
        >
          <option :value="null">— Root level —</option>
          <option
            v-for="loc in eligibleParents"
            :key="loc.id"
            :value="loc.id"
          >{{ loc.display_name }}</option>
        </select>
      </div>
      <ErrorBanner v-if="error" :message="error" />
      <div class="flex justify-end gap-3 pt-2">
        <button type="button" @click="$emit('close')" class="text-sm text-gray-600">Cancel</button>
        <button
          type="submit"
          :disabled="loading"
          class="bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium py-1.5 px-4 rounded-md disabled:opacity-50"
        >
          {{ loading ? 'Saving…' : (location ? 'Save changes' : 'Add') }}
        </button>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { useLocationsStore } from '@/stores/locations'
import { useApiRequest } from '@/composables/useApiRequest'
import BaseModal from '@/components/ui/BaseModal.vue'
import ErrorBanner from '@/components/ui/ErrorBanner.vue'

const props = defineProps({ location: Object, parentId: Number })
const emit = defineEmits(['close', 'saved'])

const store = useLocationsStore()
const { loading, error, run } = useApiRequest()

const form = reactive({
  name: props.location?.name || '',
  parent_id: props.location?.parent?.id ?? props.parentId ?? null,
  skip_watering: props.location?.skip_watering ?? false,
})

// Exclude the location being edited to prevent self-reference cycles
const eligibleParents = computed(() => {
  if (!props.location) return store.locations
  return store.locations.filter(l => l.id !== props.location.id)
})

async function submit() {
  await run(() =>
    props.location
      ? store.update(props.location.id, form)
      : store.create(form)
  ).catch(() => {})
  if (!error.value) emit('saved')
}
</script>
