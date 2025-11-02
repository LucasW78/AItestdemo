<template>
  <div class="app-header">
    <div class="header-left">
      <el-icon class="logo-icon" size="24">
        <Cpu />
      </el-icon>
      <h1 class="app-title">AItestdemo</h1>
    </div>

    <div class="header-center">
      <el-menu
        :default-active="activeIndex"
        mode="horizontal"
        :ellipsis="false"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/documents">
          <el-icon><Document /></el-icon>
          <span>文档管理</span>
        </el-menu-item>
        <el-menu-item index="/testcases">
          <el-icon><List /></el-icon>
          <span>测试用例</span>
        </el-menu-item>
        <el-menu-item index="/mindmaps">
          <el-icon><Share /></el-icon>
          <span>思维导图</span>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="header-right">
      <el-dropdown @command="handleCommand">
        <el-button type="primary" :icon="User" circle />
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/store'
import {
  House,
  Document,
  List,
  Share,
  User,
  Setting,
  SwitchButton,
  Cpu
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const activeIndex = computed(() => route.path)

const handleMenuSelect = (index) => {
  if (index !== route.path) {
    router.push(index)
  }
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      // TODO: Navigate to profile page
      break
    case 'settings':
      // TODO: Navigate to settings page
      break
    case 'logout':
      appStore.logout()
      router.push('/')
      break
  }
}
</script>

<style lang="scss" scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;

  .logo-icon {
    color: #409eff;
  }

  .app-title {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: #303133;
  }
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;

  .el-menu {
    border-bottom: none;
    background: transparent;

    .el-menu-item {
      font-size: 16px;
      border-bottom: 2px solid transparent;

      &:hover {
        background-color: #f5f7fa;
      }

      &.is-active {
        border-bottom-color: #409eff;
        color: #409eff;
      }
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>