<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchStats } from '@/api/stats'
import type { StatsResponse } from '@/types/analyze'

const stats = ref<StatsResponse | null>(null)

onMounted(async () => {
  try {
    stats.value = await fetchStats()
  } catch {
    stats.value = null
  }
})
</script>

<template>
  <div
    v-if="stats && stats.total_analyses > 0"
    class="flex items-center justify-center gap-6 text-xs text-ink-muted font-mono"
  >
    <span><span class="text-ink">{{ stats.total_analyses }}</span> analyses</span>
    <span class="opacity-40">·</span>
    <span><span class="text-ink">{{ stats.average_score }}%</span> avg match</span>
  </div>
</template>
