<template>
  <div
    class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow transition cursor-pointer flex flex-col"
    @click="$router.push(`/plants/${plant.id}`)"
  >
    <div class="p-4 flex gap-3 flex-1">
      <!-- Thumbnail -->
      <div
        class="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100"
        :class="{ 'cursor-zoom-in': plant.thumbnail }"
        @click.stop="plant.thumbnail && (lightbox = true)"
      >
        <img
          v-if="plant.thumbnail"
          :src="plant.thumbnail"
          :alt="plant.name"
          class="w-full h-full object-cover"
        />
        <div
          v-else
          class="w-full h-full flex items-center justify-center text-3xl text-gray-300"
        >🌱</div>
      </div>

      <Teleport to="body">
        <div
          v-if="lightbox"
          class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center"
          @click.self="lightbox = false"
        >
          <button
            @click="lightbox = false"
            class="absolute top-4 right-4 text-white text-3xl leading-none hover:text-gray-300"
          >&times;</button>
          <img
            :src="plant.full_image ?? plant.thumbnail"
            :alt="plant.name"
            class="max-w-[90vw] max-h-[90vh] object-contain rounded-lg"
          />
        </div>
      </Teleport>

      <!-- Content -->
      <div class="flex flex-col gap-1 flex-1 min-w-0">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <p class="font-semibold text-gray-900 truncate">{{ plant.name }}</p>
            <p v-if="plant.scientific_name" class="text-xs text-gray-400 italic truncate">
              {{ plant.scientific_name }}
            </p>
          </div>
          <div class="flex gap-1 flex-shrink-0" @click.stop>
            <button
              @click="$emit('edit', plant)"
              class="text-gray-400 hover:text-brand-600 text-xs px-1"
            >Edit</button>
            <button
              @click="$emit('delete', plant)"
              class="text-gray-400 hover:text-red-500 text-xs px-1"
            >Delete</button>
          </div>
        </div>

        <p v-if="plant.location_display_name" class="text-xs text-gray-500 truncate">
          {{ plant.location_display_name }}
        </p>

        <div class="flex gap-2 flex-wrap mt-auto">
          <span
            v-if="plant.last_repotted"
            class="inline-flex items-center text-xs bg-amber-50 text-amber-700 rounded-full px-2 py-0.5"
            :title="shortDate(plant.last_repotted)"
          >Repotted {{ relativeTime(plant.last_repotted) }}</span>
          <span
            v-if="plant.last_watered && !plant.location_skip_watering"
            class="inline-flex items-center text-xs bg-blue-50 text-blue-700 rounded-full px-2 py-0.5"
            :title="shortDate(plant.last_watered)"
          >Watered {{ relativeTime(plant.last_watered) }}</span>
        </div>
      </div>
    </div>

    <!-- Watering progress bar -->
    <div
      v-if="wateringProgress !== null"
      class="h-1.5 bg-gray-100"
      :title="wateringProgressTitle"
    >
      <div
        class="h-full transition-all duration-300"
        :class="wateringProgressColor"
        :style="{ width: wateringProgressPct + '%' }"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDateFormat } from '@/composables/useDateFormat'

const props = defineProps({ plant: Object })
defineEmits(['edit', 'delete'])

const { relativeTime, shortDate, daysSince } = useDateFormat()

const lightbox = ref(false)
function onKeydown(e) { if (e.key === 'Escape') lightbox.value = false }
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

const wateringProgress = computed(() => {
  if (!props.plant.watering_interval_days || !props.plant.last_watered || props.plant.location_skip_watering) return null
  return daysSince(props.plant.last_watered) / props.plant.watering_interval_days
})

const wateringProgressPct = computed(() => {
  if (wateringProgress.value === null) return 0
  if (daysSince(props.plant.last_watered) === 0) return 100
  return Math.min(wateringProgress.value * 100, 100)
})

const wateringProgressColor = computed(() => {
  if (wateringProgress.value === null) return ''
  if (daysSince(props.plant.last_watered) === 0) return 'bg-green-400'
  if (wateringProgress.value >= 1) return 'bg-red-400'
  if (wateringProgress.value >= 0.75) return 'bg-amber-400'
  return 'bg-blue-400'
})

const wateringProgressTitle = computed(() => {
  const p = wateringProgress.value
  if (p === null) return ''
  const days = daysSince(props.plant.last_watered)
  const interval = props.plant.watering_interval_days
  const remaining = Math.round(interval - days)
  if (remaining === 0) return `Due today (every ${interval} days)`
  if (remaining < 0) return `Overdue by ${Math.abs(remaining)} day${Math.abs(remaining) !== 1 ? 's' : ''} (every ${interval} days)`
  return `Due in ${remaining} day${remaining !== 1 ? 's' : ''} (every ${interval} days)`
})
</script>
