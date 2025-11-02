<template>
  <div id="app">
    <el-container class="layout-container">
      <!-- Header -->
      <el-header class="app-header">
        <AppHeader />
      </el-header>

      <!-- Main Content -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- Footer -->
      <el-footer class="app-footer">
        <AppFooter />
      </el-footer>
    </el-container>

    <!-- Global Loading -->
    <el-loading
      v-loading="globalLoading"
      element-loading-text="加载中..."
      element-loading-background="rgba(0, 0, 0, 0.7)"
      v-if="globalLoading"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/store'
import AppHeader from '@/components/common/AppHeader.vue'
import AppFooter from '@/components/common/AppFooter.vue'

const appStore = useAppStore()

const globalLoading = computed(() => appStore.globalLoading)
</script>

<style lang="scss">
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  overflow: hidden;
}

.layout-container {
  height: 100vh;
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 60px !important;
  line-height: 60px;
}

.app-main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 120px);
}

.app-footer {
  background-color: #fff;
  border-top: 1px solid #e4e7ed;
  height: 60px !important;
  line-height: 60px;
  text-align: center;
  color: #909399;
  font-size: 14px;
}

// Global element-plus overrides
.el-button {
  &.is-plain {
    &:hover {
      background-color: #409eff;
      color: #fff;
      border-color: #409eff;
    }
  }
}

.el-card {
  &.is-always-shadow {
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }
}

// Fade transition
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>