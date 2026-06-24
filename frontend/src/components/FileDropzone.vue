<template>
  <div
    class="relative w-full max-w-2xl mx-auto transition-all duration-300"
    :class="[
      isDragActive 
        ? 'scale-[1.01] animate-pulse-border border-indigo-500/80 bg-indigo-950/10' 
        : 'border-slate-800/80 hover:border-slate-700/80 bg-slate-900/20'
    ]"
    @dragenter.prevent="isDragActive = true"
    @dragover.prevent="isDragActive = true"
    @dragleave.prevent="isDragActive = false"
    @drop.prevent="handleDrop"
  >
    <div
      class="flex flex-col items-center justify-center py-16 px-6 border-2 border-dashed rounded-2xl glass-card transition-all duration-300 cursor-pointer"
      @click="triggerFileInput"
    >
      <!-- File input -->
      <input
        ref="fileInput"
        type="file"
        accept=".aab"
        class="hidden"
        @change="handleFileSelect"
        @click.stop
      />

      <!-- Icon & Text -->
      <div 
        class="p-4 mb-5 rounded-full bg-slate-800/50 text-indigo-400 border border-slate-700/50 shadow-inner group-hover:scale-110 transition-transform duration-300"
        :class="{ 'scale-110 text-indigo-300 bg-indigo-950/40': isDragActive }"
      >
        <UploadCloudIcon class="w-10 h-10" />
      </div>

      <h3 class="text-xl font-semibold font-display tracking-wide mb-2 text-slate-100">
        Drag & Drop your .aab file
      </h3>
      <p class="text-sm text-slate-400 text-center max-w-sm mb-6 leading-relaxed">
        Select your Android App Bundle (.aab) to compile it into a universal test APK.
      </p>

      <button
        type="button"
        class="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-medium text-sm rounded-xl shadow-lg shadow-indigo-900/30 hover:shadow-indigo-900/50 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
      >
        Browse Files
      </button>

      <!-- Local Validation Error -->
      <div 
        v-if="validationError" 
        class="absolute bottom-4 left-4 right-4 flex items-center justify-center gap-2 p-3 bg-red-950/60 border border-red-800/40 rounded-xl text-red-300 text-xs animate-slide-up"
      >
        <AlertTriangleIcon class="w-4 h-4 flex-shrink-0" />
        <span>{{ validationError }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { UploadCloud as UploadCloudIcon, AlertTriangle as AlertTriangleIcon } from 'lucide-vue-next';

const emit = defineEmits(['file-selected']);

const isDragActive = ref(false);
const fileInput = ref(null);
const validationError = ref(null);

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

const handleFileSelect = (event) => {
  validationError.value = null;
  const files = event.target.files;
  if (files && files.length > 0) {
    validateAndEmit(files[0]);
  }
};

const handleDrop = (event) => {
  isDragActive.value = false;
  validationError.value = null;
  const files = event.dataTransfer.files;
  if (files && files.length > 0) {
    validateAndEmit(files[0]);
  }
};

const validateAndEmit = (file) => {
  if (!file.name.toLowerCase().endsWith('.aab')) {
    validationError.value = 'Invalid file type. Please select an Android App Bundle (.aab) file.';
    return;
  }
  emit('file-selected', file);
};
</script>
