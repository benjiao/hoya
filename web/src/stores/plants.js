import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'
import { extractError } from '@/composables/useApiRequest'

export const usePlantsStore = defineStore('plants', () => {
  const plants = ref([])
  const currentPlant = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const { data } = await client.get('plants/')
      plants.value = data
    } catch (e) {
      error.value = extractError(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    loading.value = true
    error.value = null
    try {
      const { data } = await client.get(`plants/${id}/`)
      currentPlant.value = data
    } catch (e) {
      error.value = extractError(e)
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    const { data } = await client.post('plants/', payload)
    plants.value.push(data)
    return data
  }

  async function update(id, payload) {
    const { data } = await client.patch(`plants/${id}/`, payload)
    if (currentPlant.value?.id === id) currentPlant.value = data
    const idx = plants.value.findIndex(p => p.id === id)
    if (idx !== -1) plants.value[idx] = { ...plants.value[idx], ...data }
    return data
  }

  async function remove(id) {
    await client.delete(`plants/${id}/`)
    plants.value = plants.value.filter(p => p.id !== id)
    if (currentPlant.value?.id === id) currentPlant.value = null
  }

  async function uploadImage(plantId, file, caption = '') {
    const form = new FormData()
    form.append('image', file)
    if (caption) form.append('caption', caption)
    const { data } = await client.post(`plants/${plantId}/images/`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    if (currentPlant.value?.id === plantId) {
      currentPlant.value.images.push(data)
    }
    // Keep list thumbnail in sync when the first image is added
    const idx = plants.value.findIndex(p => p.id === plantId)
    if (idx !== -1 && !plants.value[idx].thumbnail) {
      plants.value[idx] = { ...plants.value[idx], thumbnail: data.image }
    }
    return data
  }

  async function deleteImage(plantId, imageId) {
    await client.delete(`plants/${plantId}/images/${imageId}/`)
    if (currentPlant.value?.id === plantId) {
      currentPlant.value.images = currentPlant.value.images.filter(i => i.id !== imageId)
    }
  }

  async function fetchLogs(plantId) {
    const { data } = await client.get(`plants/${plantId}/logs/`)
    return data
  }

  async function addLog(plantId, payload) {
    const { data } = await client.post(`plants/${plantId}/logs/`, payload)
    return data
  }

  async function deleteLog(plantId, logId) {
    await client.delete(`plants/${plantId}/logs/${logId}/`)
  }

  return {
    plants, currentPlant, loading, error,
    fetchAll, fetchOne, create, update, remove,
    uploadImage, deleteImage, fetchLogs, addLog, deleteLog,
  }
})
