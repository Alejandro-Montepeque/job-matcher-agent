<script setup lang="ts">
import type { AnalyzeResponse } from '@/types/analyze'

defineProps<{ result: AnalyzeResponse }>()
</script>

<template>
  <section class="card space-y-6">
    <header class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <h2 class="text-xl font-bold">Match score</h2>
        <span
          v-if="result.cached"
          class="text-[10px] font-mono uppercase tracking-wider
                 px-2 py-0.5 rounded bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/30"
          title="Result served from cache"
        >
          cached
        </span>
      </div>
      <span class="text-3xl font-mono font-bold text-accent">{{ result.match_score }}%</span>
    </header>

    <div class="h-2 bg-bg rounded overflow-hidden">
      <div
        class="h-full bg-gradient-to-r from-accent to-accent-cyan transition-all"
        :style="{ width: `${result.match_score}%` }"
      />
    </div>

    <p class="text-sm text-ink-muted leading-relaxed">{{ result.summary }}</p>

    <div v-if="result.matches.length" class="space-y-2">
      <h3 class="text-sm font-semibold text-accent-cyan">Matches</h3>
      <ul class="space-y-1 text-sm">
        <li v-for="(m, i) in result.matches" :key="i" class="flex gap-2">
          <span class="text-accent-cyan">✓</span>
          <span>{{ m }}</span>
        </li>
      </ul>
    </div>

    <div v-if="result.gaps.length" class="space-y-2">
      <h3 class="text-sm font-semibold text-amber-400">Gaps</h3>
      <ul class="space-y-1 text-sm">
        <li v-for="(g, i) in result.gaps" :key="i" class="flex gap-2">
          <span class="text-amber-400">!</span>
          <span>{{ g }}</span>
        </li>
      </ul>
    </div>

    <div v-if="result.suggestions.length" class="space-y-3">
      <h3 class="text-sm font-semibold text-accent">Suggestions</h3>
      <div
        v-for="(s, i) in result.suggestions"
        :key="i"
        class="border border-bg-border rounded-md p-3 space-y-1"
      >
        <p class="text-sm font-semibold">{{ s.title }}</p>
        <p class="text-xs text-ink-muted">{{ s.detail }}</p>
      </div>
    </div>
  </section>
</template>
