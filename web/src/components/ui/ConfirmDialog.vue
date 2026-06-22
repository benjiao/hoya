<template>
  <BaseModal title="Confirm" @close="$emit('cancel')">
    <p class="text-sm text-gray-700 mb-6">{{ message }}</p>
    <div class="flex justify-end gap-3">
      <button @click="$emit('cancel')" class="text-sm text-gray-600">Cancel</button>
      <button
        @click="$emit('confirm')"
        class="bg-red-600 hover:bg-red-700 text-white text-sm font-medium py-1.5 px-4 rounded-md"
      >Delete</button>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'
defineProps({ message: String })
defineEmits(['confirm', 'cancel'])
</script>
