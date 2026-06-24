import { defineStore } from 'pinia';
import axios from 'axios';

// Get API base URL from Vite's env, default to empty string so Vite's proxy config is used
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export const useTaskStore = defineStore('task', {
  state: () => ({
    activeTaskId: null,
    taskStatus: 'IDLE', // IDLE, UPLOADING, PENDING, PROCESSING, SUCCESS, FAILED
    uploadProgress: 0,
    conversionProgress: 0,
    logs: [],
    errorMessage: null,
    pollTimer: null,
  }),

  actions: {
    resetStore() {
      this.stopPolling();
      this.activeTaskId = null;
      this.taskStatus = 'IDLE';
      this.uploadProgress = 0;
      this.conversionProgress = 0;
      this.logs = [];
      this.errorMessage = null;
    },

    stopPolling() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer);
        this.pollTimer = null;
      }
    },

    async uploadAAB(file) {
      this.resetStore();
      this.taskStatus = 'UPLOADING';
      this.uploadProgress = 0;
      this.logs = ['Starting file upload...'];

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post(`${API_BASE}/api/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              this.uploadProgress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              if (this.uploadProgress === 100) {
                this.logs.push('Upload complete, awaiting server acknowledgment...');
              }
            }
          },
        });

        this.activeTaskId = response.data.task_id;
        this.taskStatus = 'PENDING';
        this.logs.push(`Upload accepted. Task ID: ${this.activeTaskId}`);
        
        // Start polling the server for status updates
        this.startPolling();
      } catch (err) {
        console.error('Upload failed:', err);
        this.taskStatus = 'FAILED';
        this.errorMessage = err.response?.data?.detail || 'Failed to upload the .aab file. Please try again.';
        this.logs.push(`[ERROR] Upload failed: ${this.errorMessage}`);
      }
    },

    startPolling() {
      this.stopPolling();
      
      // Poll immediately once
      this.fetchTaskStatus();
      
      // Set interval to poll every 1.5 seconds
      this.pollTimer = setInterval(() => {
        this.fetchTaskStatus();
      }, 1500);
    },

    async fetchTaskStatus() {
      if (!this.activeTaskId) return;

      try {
        const response = await axios.get(`${API_BASE}/api/tasks/${this.activeTaskId}`);
        const data = response.data;

        // Keep local status as UPLOADING if backend says PENDING but we're still processing response
        // Usually backend says PENDING immediately.
        this.taskStatus = data.status;
        this.conversionProgress = data.progress;
        this.logs = data.logs || [];
        this.errorMessage = data.error;

        if (this.taskStatus === 'SUCCESS' || this.taskStatus === 'FAILED') {
          this.stopPolling();
        }
      } catch (err) {
        console.error('Error fetching task status:', err);
        // We do not stop polling immediately on standard network glitches, 
        // to maintain robustness. We only add a note in console.
      }
    },

    getDownloadUrl() {
      if (!this.activeTaskId || this.taskStatus !== 'SUCCESS') return '#';
      return `${API_BASE}/api/tasks/${this.activeTaskId}/download`;
    }
  },
});
