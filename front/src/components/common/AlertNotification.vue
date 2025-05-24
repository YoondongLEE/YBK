<template>
  <Transition name="alert-fade">
    <div
      v-if="isVisible"
      class="alert-notification"
      :class="[`alert-${type}`, { 'slide-in': isVisible }]"
    >
      <div class="alert-icon">
        <i v-if="type === 'success'" class="fas fa-check-circle"></i>
        <i v-else-if="type === 'error'" class="fas fa-exclamation-circle"></i>
        <i v-else-if="type === 'warning'" class="fas fa-exclamation-triangle"></i>
        <i v-else class="fas fa-info-circle"></i>
      </div>
      <div class="alert-content">
        <div class="alert-title">{{ title }}</div>
        <div v-if="message" class="alert-message">{{ message }}</div>
      </div>
      <div class="alert-close" @click="closeAlert">
        <i class="fas fa-times"></i>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'info',
    validator(value) {
      return ['info', 'success', 'warning', 'error'].includes(value);
    }
  },
  duration: {
    type: Number,
    default: 3000 // 기본 3초 후 자동으로 닫힘
  },
  autoClose: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['close']);

const isVisible = ref(props.show);
let timeoutId = null;

// show prop이 변경되면 알림 표시 상태도 변경
watch(() => props.show, (newValue) => {
  isVisible.value = newValue;
  if (newValue && props.autoClose) {
    startAutoCloseTimer();
  }
});

// 알림 닫기
const closeAlert = () => {
  isVisible.value = false;
  emit('close');
  if (timeoutId) {
    clearTimeout(timeoutId);
    timeoutId = null;
  }
};

// 자동 닫기 타이머 설정
const startAutoCloseTimer = () => {
  if (props.autoClose && props.duration > 0) {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      closeAlert();
    }, props.duration);
  }
};

onMounted(() => {
  if (props.show && props.autoClose) {
    startAutoCloseTimer();
  }
});

onUnmounted(() => {
  if (timeoutId) {
    clearTimeout(timeoutId);
  }
});
</script>

<style scoped>
.alert-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  align-items: center;
  min-width: 300px;
  max-width: 400px;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  color: white;
  transform: translateX(120%);
  transition: transform 0.3s ease;
}

.alert-notification.slide-in {
  transform: translateX(0);
}

.alert-icon {
  margin-right: 15px;
  font-size: 20px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 2px;
}

.alert-message {
  font-size: 14px;
  opacity: 0.9;
}

.alert-close {
  cursor: pointer;
  padding: 5px;
  font-size: 14px;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.alert-close:hover {
  opacity: 1;
}

/* 알림 유형별 색상 */
.alert-success {
  background-color: #28a745;
}

.alert-info {
  background-color: #4a90e2;
}

.alert-warning {
  background-color: #ffc107;
  color: #333;
}

.alert-error {
  background-color: #dc3545;
}

/* 트랜지션 애니메이션 */
.alert-fade-enter-active,
.alert-fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.alert-fade-enter-from,
.alert-fade-leave-to {
  opacity: 0;
  transform: translateX(120%);
}
</style>