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
          <div class="flex-shrink-0 relative" @click.stop>
            <button
              ref="menuBtn"
              @click="toggleMenu"
              class="text-gray-400 hover:text-gray-600 text-sm leading-none px-1.5 py-1 rounded hover:bg-gray-100"
            >⋮</button>
            <Teleport to="body">
              <div v-if="menuOpen" class="fixed inset-0 z-40" @click="menuOpen = false"></div>
              <div
                v-if="menuOpen"
                class="fixed z-50 bg-white rounded-md shadow-lg border border-gray-100 py-1 w-32"
                :style="{ top: menuPos.top + 'px', left: menuPos.left + 'px' }"
              >
                <button
                  @click="onEdit"
                  class="block w-full text-left px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
                >Edit</button>
                <button
                  @click="onDuplicate"
                  class="block w-full text-left px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
                >Duplicate</button>
              </div>
            </Teleport>
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
          >Watered {{ relativeTimeDays(plant.last_watered) }}</span>
          <span
            v-if="plant.last_fertilized"
            class="inline-flex items-center text-xs bg-green-50 text-green-700 rounded-full px-2 py-0.5"
            :title="shortDate(plant.last_fertilized)"
          >Fertilized {{ relativeTime(plant.last_fertilized) }}</span>
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

    <!-- Fertilizing progress bar -->
    <div
      v-if="fertilizingProgress !== null"
      class="h-1.5 bg-gray-100"
      :title="fertilizingProgressTitle"
    >
      <div
        class="h-full transition-all duration-300"
        :class="fertilizingProgressColor"
        :style="{ width: fertilizingProgressPct + '%' }"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDateFormat } from '@/composables/useDateFormat'

const props = defineProps({ plant: Object })
const emit = defineEmits(['edit', 'duplicate'])

const { relativeTime, relativeTimeDays, shortDate, daysSince } = useDateFormat()

const lightbox = ref(false)
const menuOpen = ref(false)
const menuBtn = ref(null)
const menuPos = ref({ top: 0, left: 0 })

function onKeydown(e) {
  if (e.key === 'Escape') {
    lightbox.value = false
    menuOpen.value = false
  }
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

function toggleMenu() {
  if (menuOpen.value) {
    menuOpen.value = false
    return
  }
  const rect = menuBtn.value.getBoundingClientRect()
  menuPos.value = { top: rect.bottom + 4, left: rect.right - 128 }
  menuOpen.value = true
}

function onEdit() {
  menuOpen.value = false
  emit('edit', props.plant)
}

function onDuplicate() {
  menuOpen.value = false
  emit('duplicate', props.plant)
}

const wateringProgress = computed(() => {
  if (!props.plant.watering_interval_days || !props.plant.last_watered || props.plant.location_skip_watering) return null
  return daysSince(props.plant.last_watered) / props.plant.watering_interval_days
})

const wateringProgressPct = computed(() => {
  if (wateringProgress.value === null) return 0
  const days = daysSince(props.plant.last_watered)
  const remaining = Math.round(props.plant.watering_interval_days - days)
  if (days === 0 || remaining === 0) return 100
  return Math.min(wateringProgress.value * 100, 100)
})

const wateringProgressColor = computed(() => {
  if (wateringProgress.value === null) return ''
  const days = daysSince(props.plant.last_watered)
  const remaining = Math.round(props.plant.watering_interval_days - days)
  if (days === 0) return 'bg-green-400'
  if (remaining === 0) return 'bg-red-400'
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

const fertilizingProgress = computed(() => {
  if (!props.plant.fertilizing_interval_days || !props.plant.last_fertilized) return null
  return daysSince(props.plant.last_fertilized) / props.plant.fertilizing_interval_days
})

const fertilizingProgressPct = computed(() => {
  if (fertilizingProgress.value === null) return 0
  const days = daysSince(props.plant.last_fertilized)
  const remaining = Math.round(props.plant.fertilizing_interval_days - days)
  if (days === 0 || remaining === 0) return 100
  return Math.min(fertilizingProgress.value * 100, 100)
})

const fertilizingProgressColor = computed(() => {
  if (fertilizingProgress.value === null) return ''
  const days = daysSince(props.plant.last_fertilized)
  const remaining = Math.round(props.plant.fertilizing_interval_days - days)
  if (days === 0) return 'bg-green-400'
  if (remaining === 0) return 'bg-red-400'
  if (fertilizingProgress.value >= 1) return 'bg-red-400'
  if (fertilizingProgress.value >= 0.75) return 'bg-amber-400'
  return 'bg-green-400'
})

const fertilizingProgressTitle = computed(() => {
  if (fertilizingProgress.value === null) return ''
  const days = daysSince(props.plant.last_fertilized)
  const interval = props.plant.fertilizing_interval_days
  const remaining = Math.round(interval - days)
  if (remaining === 0) return `Fertilize today (every ${interval} days)`
  if (remaining < 0) return `Fertilizing overdue by ${Math.abs(remaining)} day${Math.abs(remaining) !== 1 ? 's' : ''} (every ${interval} days)`
  return `Fertilize in ${remaining} day${remaining !== 1 ? 's' : ''} (every ${interval} days)`
})
</script>
