<template>
  <div class="min-h-full flex flex-col justify-between bg-slate-950 relative overflow-hidden">
    <!-- Ambient glowing backgrounds -->
    <div class="absolute top-[10%] left-[10%] w-[450px] h-[450px] bg-indigo-650/10 rounded-full blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-[10%] right-[10%] w-[450px] h-[450px] bg-violet-650/10 rounded-full blur-[120px] pointer-events-none"></div>

    <!-- Top Navigation -->
    <nav class="border-b border-slate-900/80 bg-slate-950/40 backdrop-blur-md sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-900/30">
            <span class="text-base">📦</span>
          </div>
          <span class="font-bold text-base tracking-wide font-display bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
            AAB2APK
          </span>
        </div>
        <div class="flex items-center gap-4">
          <a
            href="https://github.com/google/bundletool"
            target="_blank"
            rel="noopener noreferrer"
            class="text-xs text-slate-400 hover:text-indigo-400 transition-colors font-medium border border-slate-800/80 rounded-lg px-3 py-1.5 bg-slate-900/30 hover:bg-slate-900/60"
          >
            Google Bundletool
          </a>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <div class="flex-grow flex items-center justify-center py-6">
      <Dashboard />
    </div>

    <!-- Footer -->
    <footer class="border-t border-slate-900/40 bg-slate-950/40 py-6 text-center z-10">
      <p class="text-[10px] sm:text-xs text-slate-600 tracking-wide font-medium">
        AAB to APK Converter &bull; Built with Vue 3, FastAPI, and Google Bundletool.
      </p>
    </footer>
  </div>
</template>

<script setup>
import Dashboard from './views/Dashboard.vue';
</script>
