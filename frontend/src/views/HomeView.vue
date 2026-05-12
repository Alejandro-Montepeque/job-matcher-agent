<script setup lang="ts">
import { useMatcherStore } from '@/stores/matcher'
import MatchForm from '@/components/MatchForm.vue'
import MatchResult from '@/components/MatchResult.vue'
import StatsBar from '@/components/StatsBar.vue'

const store = useMatcherStore()

function handleSubmit(cv: File, jobPosting: string): void {
  store.analyze(cv, jobPosting)
}
</script>

<template>
  <section class="container-app py-16 space-y-10">
    <header class="text-center space-y-3 max-w-2xl mx-auto">
      <h1 class="text-4xl md:text-5xl font-bold tracking-tight">
        Is your CV a match?
      </h1>
      <p class="text-ink-muted">
        Upload your CV and paste a job posting. The agent analyzes both with Gemini and
        gives you a match score, gaps, and concrete suggestions to improve.
      </p>
      <StatsBar />
    </header>

    <div class="grid lg:grid-cols-2 gap-8">
      <MatchForm @submit="handleSubmit" />

      <div>
        <div v-if="store.loading" class="card text-center text-ink-muted">
          Analyzing... this can take 5-15 seconds.
        </div>
        <div v-else-if="store.error" class="card text-red-400">
          {{ store.error }}
        </div>
        <MatchResult v-else-if="store.result" :result="store.result" />
        <div v-else class="card text-center text-ink-muted text-sm">
          Results will appear here.
        </div>
      </div>
    </div>
  </section>
</template>
