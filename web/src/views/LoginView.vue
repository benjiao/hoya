<template>
  <div class="min-h-screen flex items-center justify-center bg-brand-50">
    <div class="bg-white rounded-xl shadow p-8 w-full max-w-sm">
      <h1 class="text-2xl font-bold text-brand-800 mb-6">Hoya</h1>
      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            v-model="form.username"
            type="text"
            required
            autocomplete="username"
            class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            autocomplete="current-password"
            class="w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-500 focus:border-brand-500"
          />
        </div>
        <ErrorBanner v-if="error" :message="error" />
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-brand-600 hover:bg-brand-700 text-white font-medium py-2 px-4 rounded-md transition disabled:opacity-50"
        >
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useApiRequest } from '@/composables/useApiRequest'
import ErrorBanner from '@/components/ui/ErrorBanner.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { loading, error, run } = useApiRequest()

const form = reactive({ username: '', password: '' })

async function submit() {
  await run(() => auth.login(form.username, form.password)).catch(() => {})
  if (!error.value) {
    router.push(route.query.redirect || '/plants')
  }
}
</script>
