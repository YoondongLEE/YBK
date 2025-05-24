import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAlertStore = defineStore('alert', () => {
  const isVisible = ref(false);
  const title = ref('');
  const message = ref('');
  const type = ref('info');
  const duration = ref(3000);
  const autoClose = ref(true);

  function showAlert(alertOptions) {
    title.value = alertOptions.title || '알림';
    message.value = alertOptions.message || '';
    type.value = alertOptions.type || 'info';
    duration.value = alertOptions.duration !== undefined ? alertOptions.duration : 3000;
    autoClose.value = alertOptions.autoClose !== undefined ? alertOptions.autoClose : true;
    isVisible.value = true;
  }

  function showSuccess(titleText, messageText = '', options = {}) {
    showAlert({
      title: titleText,
      message: messageText,
      type: 'success',
      ...options
    });
  }

  function showError(titleText, messageText = '', options = {}) {
    showAlert({
      title: titleText,
      message: messageText,
      type: 'error',
      ...options
    });
  }

  function showWarning(titleText, messageText = '', options = {}) {
    showAlert({
      title: titleText,
      message: messageText,
      type: 'warning',
      ...options
    });
  }

  function showInfo(titleText, messageText = '', options = {}) {
    showAlert({
      title: titleText,
      message: messageText,
      type: 'info',
      ...options
    });
  }

  function closeAlert() {
    isVisible.value = false;
  }

  return {
    isVisible,
    title,
    message,
    type,
    duration,
    autoClose,
    showAlert,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    closeAlert
  };
});