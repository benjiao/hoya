import { ref } from 'vue'

export function useApiRequest() {
  const loading = ref(false)
  const error = ref(null)

  async function run(fn) {
    loading.value = true
    error.value = null
    try {
      return await fn()
    } catch (e) {
      error.value = extractError(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return { loading, error, run }
}

export function extractError(e) {
  const data = e.response?.data
  if (!data) return e.message || 'An unexpected error occurred.'
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  if (data.non_field_errors) return data.non_field_errors.join(' ')
  const msgs = Object.entries(data)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
  return msgs.join(' | ')
}
