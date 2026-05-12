<script setup lang="ts"></script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="border-b border-bg-border">
      <div class="container-app h-16 flex items-center justify-between">
        <RouterLink to="/" class="font-mono text-lg font-bold">
          JobMatcher<span class="text-accent">.ai</span>
        </RouterLink>
        <a
          href="https://github.com/Alejandro-Montepeque/job-matcher-agent"
          target="_blank"
          rel="noopener"
          class="text-sm text-ink-muted hover:text-ink"
        >
          GitHub
        </a>
      </div>
    </header>

    <main class="flex-1">
      <RouterView />
    </main>

    <footer class="border-t border-bg-border py-6 text-center text-xs text-ink-muted">
      Built by Alejandro Montepeque · {{ new Date().getFullYear() }}
    </footer>
  </div>
</template>
