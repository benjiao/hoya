<template>
  <li>
    <div
      class="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-gray-50"
      :style="{ paddingLeft: `${depth * 1.25 + 0.75}rem` }"
    >
      <div class="flex items-center gap-2">
        <RouterLink
          :to="`/locations/${node.id}`"
          class="text-sm font-medium text-gray-800 hover:text-brand-600"
        >{{ node.name }}</RouterLink>
        <span v-if="node.children.length" class="text-xs text-gray-400">
          ({{ node.children.length }})
        </span>
      </div>
      <div class="flex gap-2 text-xs text-gray-400">
        <button @click="$emit('create-child', node.id)" class="hover:text-brand-600">+ Child</button>
        <button @click="$emit('edit', node)" class="hover:text-brand-600">Edit</button>
        <button @click="$emit('delete', node)" class="hover:text-red-500">Delete</button>
      </div>
    </div>
    <LocationTree
      v-if="node.children.length"
      :nodes="node.children"
      :depth="depth + 1"
      @create-child="$emit('create-child', $event)"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
    />
  </li>
</template>

<script setup>
import LocationTree from './LocationTree.vue'

defineProps({
  node: Object,
  depth: { type: Number, default: 0 },
})
defineEmits(['create-child', 'edit', 'delete'])
</script>
