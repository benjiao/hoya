<template>
  <ul class="space-y-1">
    <LocationRow
      v-for="node in nodes"
      :key="node.id"
      :node="node"
      :depth="depth"
      @create-child="$emit('create-child', $event)"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
    />
  </ul>
</template>

<script setup>
import LocationRow from './LocationRow.vue'

defineProps({
  nodes: Array,
  depth: { type: Number, default: 0 },
})
defineEmits(['create-child', 'edit', 'delete'])
</script>
