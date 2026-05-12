<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  submit: [cv: File, jobPosting: string]
}>()

const cv = ref<File | null>(null)
const jobPosting = ref('')
const fileError = ref<string | null>(null)

function onFileChange(event: Event): void {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] ?? null
  if (file && file.type !== 'application/pdf') {
    fileError.value = 'File must be a PDF'
    cv.value = null
    return
  }
  fileError.value = null
  cv.value = file
}

function onSubmit(): void {
  if (!cv.value || jobPosting.value.trim().length < 20) return
  emit('submit', cv.value, jobPosting.value.trim())
}
</script>

<template>
  <form class="card space-y-5" @submit.prevent="onSubmit">
    <div>
      <label class="block text-sm font-semibold mb-2">Your CV (PDF)</label>
      <input
        type="file"
        accept="application/pdf"
        class="block w-full text-sm text-ink-muted file:mr-4 file:py-2 file:px-4
               file:rounded-md file:border-0 file:bg-accent file:text-white
               file:font-semibold hover:file:opacity-90"
        @change="onFileChange"
      />
      <p v-if="fileError" class="text-xs text-red-400 mt-1">{{ fileError }}</p>
      <p v-else-if="cv" class="text-xs text-ink-muted mt-1">{{ cv.name }}</p>
    </div>

    <div>
      <label class="block text-sm font-semibold mb-2">Job posting</label>
      <textarea
        v-model="jobPosting"
        rows="8"
        placeholder="Paste the job description here..."
        class="w-full bg-bg border border-bg-border rounded-md p-3 text-sm
               focus:outline-none focus:border-accent transition"
      />
      <p class="text-xs text-ink-muted mt-1">{{ jobPosting.length }} chars (min 20)</p>
    </div>

    <button
      type="submit"
      class="btn-primary w-full"
      :disabled="!cv || jobPosting.trim().length < 20"
    >
      Analyze match
    </button>
  </form>
</template>
