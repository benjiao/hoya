<template>
  <BaseModal title="Log care" @close="$emit('close')">
    <form @submit.prevent="submit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
        <select
          v-model="form.type"
          class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
        >
          <option :value="null">— General note —</option>
          <option value="watered">Watered</option>
          <option value="repotted">Repotted</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
        <input
          v-model="form.logged_at"
          type="datetime-local"
          class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
        <textarea
          v-model="form.notes"
          rows="3"
          class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
        />
      </div>
      <ErrorBanner v-if="error" :message="error" />
      <div class="flex justify-end gap-3 pt-2">
        <button type="button" @click="$emit('close')" class="text-sm text-gray-600">Cancel</button>
        <button
          type="submit"
          :disabled="loading"
          class="bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium py-1.5 px-4 rounded-md disabled:opacity-50"
        >
          {{ loading ? 'Saving…' : 'Log' }}
        </button>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { reactive } from 'vue'
import { usePlantsStore } from '@/stores/plants'
import { useApiRequest } from '@/composables/useApiRequest'
import BaseModal from '@/components/ui/BaseModal.vue'
import ErrorBanner from '@/components/ui/ErrorBanner.vue'

const props = defineProps({ plantId: [String, Number] })
const emit = defineEmits(['close', 'saved'])

const store = usePlantsStore()
const { loading, error, run } = useApiRequest()

// Strip timezone offset so datetime-local input gets a local-time value
const now = new Date()
now.setMinutes(now.getMinutes() - now.getTimezoneOffset())

const form = reactive({
  type: null,
  logged_at: now.toISOString().slice(0, 16),
  notes: '',
})

async function submit() {
  await run(() => store.addLog(props.plantId, {
    ...form,
    logged_at: new Date(form.logged_at).toISOString(),
  })).catch(() => {})
  if (!error.value) emit('saved')
}
</script>
