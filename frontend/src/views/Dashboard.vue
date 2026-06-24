<template>
  <div class="max-w-4xl mx-auto px-4 py-12">
    <!-- Header -->
    <header class="text-center mb-12 animate-slide-up">
      <div class="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-semibold text-indigo-400 mb-4 shadow-sm">
        <CpuIcon class="w-3.5 h-3.5" />
        <span>Bundletool Engine v1.18.3</span>
      </div>
      <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight font-display bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent mb-3">
        AAB to APK Converter
      </h1>
      <p class="text-slate-400 max-w-lg mx-auto text-base md:text-lg font-light leading-relaxed">
        Upload your Android App Bundle (.aab) and instantly compile a universal, signed test APK for your physical devices.
      </p>
    </header>

    <!-- Main Container -->
    <main class="animate-slide-up" style="animation-delay: 0.1s">
      <!-- 1. IDLE STATE: Upload Dropzone -->
      <div v-if="taskStore.taskStatus === 'IDLE'">
        <FileDropzone @file-selected="onFileSelected" />
      </div>

      <!-- 2. UPLOADING & PROCESSING STATES -->
      <div 
        v-else-if="taskStore.taskStatus === 'UPLOADING' || taskStore.taskStatus === 'PENDING' || taskStore.taskStatus === 'PROCESSING'"
        class="glass-panel rounded-2xl p-6 md:p-8 shadow-xl"
      >
        <ProgressBar 
          :progress="currentProgress" 
          :status="taskStore.taskStatus" 
        />
        
        <!-- Logs terminal -->
        <div class="mt-8">
          <div class="flex justify-between items-center mb-3">
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5 font-display">
              <TerminalIcon class="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
              Compiler Logs
            </span>
            <span class="flex items-center gap-1">
              <span class="w-2 h-2 bg-emerald-500 rounded-full animate-ping"></span>
              <span class="text-[10px] font-medium text-slate-400 font-mono">LIVE</span>
            </span>
          </div>
          
          <div 
            ref="terminalBody"
            :key="'terminalBody'"
            class="bg-slate-950/80 border border-slate-900 rounded-xl p-4 overflow-y-auto max-h-[250px] font-mono text-[11px] leading-relaxed text-slate-300 shadow-inner"
          >
            <div 
              v-for="(log, idx) in taskStore.logs" 
              :key="idx" 
              class="py-0.5 border-b border-slate-950/30 last:border-b-0"
              :class="getLogClass(log)"
            >
              {{ log }}
            </div>
            <div v-if="taskStore.logs.length === 0" class="text-slate-600 italic">
              Awaiting logs...
            </div>
          </div>
        </div>
      </div>

      <!-- 3. SUCCESS STATE -->
      <div 
        v-else-if="taskStore.taskStatus === 'SUCCESS'"
        class="glass-panel rounded-2xl p-8 text-center max-w-2xl mx-auto shadow-2xl relative overflow-hidden"
      >
        <!-- Decorative Glow -->
        <div class="absolute -top-24 -left-24 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl"></div>
        <div class="absolute -bottom-24 -right-24 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl"></div>

        <div class="relative z-10">
          <div class="inline-flex p-4 bg-emerald-950/40 border border-emerald-800/40 rounded-full text-emerald-400 mb-6 shadow-inner animate-bounce">
            <CheckCircleIcon class="w-12 h-12" />
          </div>

          <h2 class="text-2xl font-bold font-display text-slate-100 mb-2">
            Conversion Successful!
          </h2>
          <p class="text-sm text-slate-400 mb-8 max-w-md mx-auto leading-relaxed">
            Your universal APK has been successfully compiled and signed. It is now ready for sideloading on your device.
          </p>

          <!-- Download Action -->
          <a
            :href="taskStore.getDownloadUrl()"
            download
            class="inline-flex items-center gap-2.5 px-8 py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-base rounded-xl shadow-lg shadow-emerald-900/30 hover:shadow-emerald-950/50 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
          >
            <DownloadIcon class="w-5 h-5 stroke-[2.5]" />
            Download Universal APK
          </a>

          <div class="mt-8 border-t border-slate-900 pt-6">
            <button
              @click="taskStore.resetStore()"
              class="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors uppercase tracking-wider font-display flex items-center gap-1.5 mx-auto"
            >
              <RotateCcwIcon class="w-3.5 h-3.5" />
              Convert Another File
            </button>
          </div>
        </div>
      </div>

      <!-- 4. FAILED STATE -->
      <div 
        v-else-if="taskStore.taskStatus === 'FAILED'"
        class="glass-panel rounded-2xl p-8 max-w-2xl mx-auto shadow-2xl"
      >
        <div class="text-center mb-6">
          <div class="inline-flex p-4 bg-red-950/40 border border-red-800/40 rounded-full text-red-500 mb-4 shadow-inner">
            <AlertCircleIcon class="w-12 h-12" />
          </div>

          <h2 class="text-2xl font-bold font-display text-slate-100 mb-2">
            Conversion Failed
          </h2>
          <p class="text-sm text-red-300/80 mb-6 max-w-md mx-auto leading-relaxed">
            An error occurred during bundletool processing. Review the log details below.
          </p>
        </div>

        <!-- Error display -->
        <div class="bg-red-950/20 border border-red-900/50 rounded-xl p-4 mb-6 text-left">
          <h4 class="text-xs font-bold text-red-400 uppercase tracking-wider mb-1.5 font-display flex items-center gap-1">
            <XOctagonIcon class="w-3.5 h-3.5" />
            Error Details
          </h4>
          <p class="text-xs font-mono text-red-300 leading-relaxed whitespace-pre-wrap break-all">
            {{ taskStore.errorMessage || 'Unknown system compilation error.' }}
          </p>
        </div>

        <!-- Failed logs terminal -->
        <div class="mb-8">
          <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 font-display flex items-center gap-1.5">
            <TerminalIcon class="w-3.5 h-3.5" />
            Subprocess Console Logs
          </h4>
          <div 
            class="bg-slate-950/80 border border-slate-900 rounded-xl p-4 overflow-y-auto max-h-[180px] font-mono text-[11px] leading-relaxed text-slate-300 shadow-inner"
          >
            <div 
              v-for="(log, idx) in taskStore.logs" 
              :key="idx" 
              class="py-0.5"
              :class="getLogClass(log)"
            >
              {{ log }}
            </div>
          </div>
        </div>

        <div class="flex justify-center border-t border-slate-900 pt-6">
          <button
            @click="taskStore.resetStore()"
            class="px-5 py-2.5 bg-slate-900 hover:bg-slate-850 text-slate-300 border border-slate-800 hover:border-slate-700 font-semibold text-sm rounded-xl transition-all duration-200 flex items-center gap-2"
          >
            <RotateCcwIcon class="w-4 h-4 text-indigo-400" />
            Return to Upload
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue';
import { useTaskStore } from '../stores/taskStore';
import FileDropzone from '../components/FileDropzone.vue';
import ProgressBar from '../components/ProgressBar.vue';
import {
  Cpu as CpuIcon,
  Terminal as TerminalIcon,
  CheckCircle as CheckCircleIcon,
  Download as DownloadIcon,
  AlertCircle as AlertCircleIcon,
  RotateCcw as RotateCcwIcon,
  XOctagon as XOctagonIcon
} from 'lucide-vue-next';

const taskStore = useTaskStore();
const terminalBody = ref(null);

const currentProgress = computed(() => {
  if (taskStore.taskStatus === 'UPLOADING') {
    return taskStore.uploadProgress;
  }
  return taskStore.conversionProgress;
});

const onFileSelected = (file) => {
  taskStore.uploadAAB(file);
};

// Scroll terminal logs container to the bottom when logs change
watch(
  () => taskStore.logs,
  async () => {
    await nextTick();
    if (terminalBody.value) {
      terminalBody.value.scrollTop = terminalBody.value.scrollHeight;
    }
  },
  { deep: true }
);

// Helper for formatting stdout, stderr, and system logs in terminal
const getLogClass = (log) => {
  if (log.startsWith('[stderr]')) {
    if (log.toLowerCase().includes('error') || log.toLowerCase().includes('failed')) {
      return 'text-red-400';
    }
    if (log.toLowerCase().includes('warn')) {
      return 'text-amber-400';
    }
    return 'text-indigo-300/80';
  }
  if (log.startsWith('[ERROR]')) {
    return 'text-red-500 font-bold';
  }
  if (log.startsWith('[stdout]')) {
    return 'text-slate-300';
  }
  // System logs
  return 'text-slate-400 italic';
};
</script>
