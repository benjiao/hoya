<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar />
    <main class="max-w-5xl mx-auto px-4 py-6">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import NavBar from './NavBar.vue'
</script>
