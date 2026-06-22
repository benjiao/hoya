<template>
  <nav class="bg-brand-800 text-white shadow">
    <div class="max-w-5xl mx-auto px-4 flex items-center justify-between h-14">
      <div class="flex items-center gap-6">
        <span class="font-bold text-lg tracking-wide">Hoya</span>
        <RouterLink
          to="/plants"
          class="text-sm hover:text-brand-100"
          active-class="text-white font-semibold"
        >Plants</RouterLink>
        <RouterLink
          to="/locations"
          class="text-sm hover:text-brand-100"
          active-class="text-white font-semibold"
        >Locations</RouterLink>
      </div>
      <button class="text-sm hover:text-brand-100" @click="handleLogout">Log out</button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
