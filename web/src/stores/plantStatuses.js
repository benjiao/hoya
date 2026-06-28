import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'
import { extractError } from '@/composables/useApiRequest'

export const usePlantStatusesStore = defineStore('plantStatuses', () => {
  const statuses = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchAll() {
    if (statuses.value.length) return
    loading.value = true
    error.value = null
    try {
      const { data } = await client.get('plant-statuses/')
      statuses.value = data
    } catch (e) {
      error.value = extractError(e)
    } finally {
      loading.value = false
    }
  }

  return { statuses, loading, error, fetchAll }
})
