<template>
  <div class="w-full max-w-2xl mx-auto my-6 animate-slide-up">
    <!-- Header status and percentage -->
    <div class="flex justify-between items-center mb-2.5">
      <span class="text-sm font-semibold tracking-wide text-indigo-300 uppercase font-display">
        {{ statusLabel }}
      </span>
      <span class="text-sm font-bold font-mono text-indigo-400">
        {{ progress }}%
      </span>
    </div>

    <!-- Progress track -->
    <div class="w-full h-3.5 bg-slate-900 border border-slate-800 rounded-full overflow-hidden shadow-inner p-[1px]">
      <!-- Progress fill -->
      <div
        class="h-full rounded-full transition-all duration-300 cubic-bezier(0.4, 0, 0.2, 1) relative overflow-hidden"
        :class="progressClass"
        :style="{ width: `${progress}%` }"
      >
        <!-- Shimmering overlay effect for active processing -->
        <div
          v-if="isActive"
          class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full animate-shimmer"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  progress: {
    type: Number,
    required: true,
    default: 0,
  },
  status: {
    type: String,
    required: true,
    default: 'PENDING',
  },
});

const statusLabel = computed(() => {
  switch (props.status) {
    case 'UPLOADING':
      return 'Uploading AAB file...';
    case 'PENDING':
      return 'Waiting in queue...';
    case 'PROCESSING':
      return 'Compiling Android Package...';
    case 'SUCCESS':
      return 'Compilation complete!';
    case 'FAILED':
      return 'Compilation failed';
    default:
      return 'Processing...';
  }
});

const progressClass = computed(() => {
  switch (props.status) {
    case 'UPLOADING':
      return 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500';
    case 'PROCESSING':
      return 'bg-gradient-to-r from-indigo-500 via-violet-500 to-emerald-500';
    case 'SUCCESS':
      return 'bg-gradient-to-r from-emerald-500 to-teal-500';
    case 'FAILED':
      return 'bg-gradient-to-r from-red-600 to-rose-600';
    default:
      return 'bg-indigo-500';
  }
});

const isActive = computed(() => {
  return props.status === 'UPLOADING' || props.status === 'PROCESSING';
});
</script>

<style scoped>
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 1.5s infinite;
}
</style>
