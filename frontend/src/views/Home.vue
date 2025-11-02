<template>
  <div class="home-container">
    <!-- Hero Section -->
    <section class="hero-section">
      <el-card class="hero-card" shadow="hover">
        <div class="hero-content">
          <h1 class="hero-title">
            <el-icon class="hero-icon"><Cpu /></el-icon>
            AI测试用例生成平台
          </h1>
          <p class="hero-description">
            基于人工智能的测试用例生成平台，支持文档上传、智能分析和思维导图可视化
          </p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="navigateTo('/documents')">
              <el-icon><Upload /></el-icon>
              开始上传文档
            </el-button>
            <el-button size="large" @click="navigateTo('/testcases')">
              <el-icon><View /></el-icon>
              查看测试用例
            </el-button>
          </div>
        </div>
      </el-card>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <h2 class="section-title">核心功能</h2>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="feature-card" shadow="hover">
            <div class="feature-content">
              <el-icon class="feature-icon" size="48"><Document /></el-icon>
              <h3 class="feature-title">文档管理</h3>
              <p class="feature-description">
                支持多种文件格式上传，包括PDF、Word、Excel和图片，自动进行文档内容提取和分析
              </p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card" shadow="hover">
            <div class="feature-content">
              <el-icon class="feature-icon" size="48"><Magic /></el-icon>
              <h3 class="feature-title">AI生成</h3>
              <p class="feature-description">
                基于Gemini AI模型，智能分析文档内容，自动生成高质量的测试用例
              </p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card" shadow="hover">
            <div class="feature-content">
              <el-icon class="feature-icon" size="48"><Share /></el-icon>
              <h3 class="feature-title">思维导图</h3>
              <p class="feature-description">
                将测试用例以思维导图形式可视化，支持交互式编辑和多格式导出
              </p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </section>

    <!-- Statistics Section -->
    <section class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="上传文档" :value="stats.documents" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="生成用例" :value="stats.testCases" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="思维导图" :value="stats.mindMaps" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="处理成功率" :value="stats.successRate" suffix="%" />
          </el-card>
        </el-col>
      </el-row>
    </section>

    <!-- Quick Actions Section -->
    <section class="actions-section">
      <h2 class="section-title">快速操作</h2>
      <el-card class="actions-card" shadow="hover">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="action-item" @click="navigateTo('/documents')">
              <el-icon class="action-icon"><UploadFilled /></el-icon>
              <div class="action-content">
                <h4>上传新文档</h4>
                <p>支持PDF、Word、Excel和图片格式</p>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="action-item" @click="navigateTo('/testcases')">
              <el-icon class="action-icon"><List /></el-icon>
              <div class="action-content">
                <h4>生成测试用例</h4>
                <p>基于文档内容智能生成测试用例</p>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Cpu,
  Upload,
  View,
  Document,
  Magic,
  Share,
  UploadFilled,
  List
} from '@element-plus/icons-vue'

const router = useRouter()

// Mock statistics data
const stats = ref({
  documents: 0,
  testCases: 0,
  mindMaps: 0,
  successRate: 98
})

const navigateTo = (path) => {
  router.push(path)
}

onMounted(() => {
  // TODO: Load real statistics from API
  stats.value = {
    documents: 12,
    testCases: 156,
    mindMaps: 8,
    successRate: 98
  }
})
</script>

<style lang="scss" scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  margin-bottom: 40px;

  .hero-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;

    .hero-content {
      text-align: center;
      padding: 40px 20px;

      .hero-title {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        font-size: 48px;
        margin: 0 0 20px 0;

        .hero-icon {
          font-size: 48px;
        }
      }

      .hero-description {
        font-size: 18px;
        margin: 0 0 30px 0;
        opacity: 0.9;
        line-height: 1.6;
      }

      .hero-actions {
        display: flex;
        gap: 16px;
        justify-content: center;

        .el-button {
          padding: 12px 24px;
          font-size: 16px;
        }
      }
    }
  }
}

.features-section {
  margin-bottom: 40px;

  .section-title {
    text-align: center;
    font-size: 32px;
    margin: 0 0 30px 0;
    color: #303133;
  }

  .feature-card {
    height: 100%;
    transition: transform 0.3s ease;

    &:hover {
      transform: translateY(-5px);
    }

    .feature-content {
      text-align: center;
      padding: 20px;

      .feature-icon {
        color: #409eff;
        margin-bottom: 16px;
      }

      .feature-title {
        font-size: 20px;
        margin: 0 0 12px 0;
        color: #303133;
      }

      .feature-description {
        color: #606266;
        line-height: 1.6;
        margin: 0;
      }
    }
  }
}

.stats-section {
  margin-bottom: 40px;

  .stat-card {
    text-align: center;

    :deep(.el-statistic__head) {
      color: #909399;
    }

    :deep(.el-statistic__content) {
      color: #409eff;
    }
  }
}

.actions-section {
  .section-title {
    text-align: center;
    font-size: 32px;
    margin: 0 0 30px 0;
    color: #303133;
  }

  .actions-card {
    .action-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 20px;
      cursor: pointer;
      border-radius: 8px;
      transition: background-color 0.3s ease;

      &:hover {
        background-color: #f5f7fa;
      }

      .action-icon {
        font-size: 48px;
        color: #409eff;
      }

      .action-content {
        h4 {
          margin: 0 0 8px 0;
          font-size: 18px;
          color: #303133;
        }

        p {
          margin: 0;
          color: #606266;
        }
      }
    }
  }
}
</style>