import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'
import { extractError } from '@/composables/useApiRequest'

export const useLocationsStore = defineStore('locations', () => {
  const locations = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const { data } = await client.get('locations/')
      locations.value = data
    } catch (e) {
      error.value = extractError(e)
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    const { data } = await client.post('locations/', payload)
    locations.value.push(data)
    return data
  }

  async function update(id, payload) {
    const { data } = await client.patch(`locations/${id}/`, payload)
    const idx = locations.value.findIndex(l => l.id === id)
    if (idx !== -1) locations.value[idx] = data
    return data
  }

  async function remove(id) {
    await client.delete(`locations/${id}/`)
    locations.value = locations.value.filter(l => l.id !== id)
  }

  function getTree() {
    const map = {}
    locations.value.forEach(loc => { map[loc.id] = { ...loc, children: [] } })
    const roots = []
    locations.value.forEach(loc => {
      if (loc.parent) {
        map[loc.parent.id]?.children.push(map[loc.id])
      } else {
        roots.push(map[loc.id])
      }
    })
    return roots
  }

  return { locations, loading, error, fetchAll, create, update, remove, getTree }
})
