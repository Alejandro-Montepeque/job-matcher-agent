import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analyzeMatch } from '@/api/analyze'
import type { AnalyzeResponse } from '@/types/analyze'

export const useMatcherStore = defineStore('matcher', () => {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<AnalyzeResponse | null>(null)

  async function analyze(cv: File, jobPosting: string): Promise<void> {
    loading.value = true
    error.value = null
    result.value = null
    try {
      result.value = await analyzeMatch(cv, jobPosting)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unexpected error'
    } finally {
      loading.value = false
    }
  }

  function reset(): void {
    result.value = null
    error.value = null
  }

  return { loading, error, result, analyze, reset }
})
