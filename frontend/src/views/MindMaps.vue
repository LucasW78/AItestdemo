<template>
  <div class="mindmaps-container">
    <div class="page-header">
      <h1 class="page-title">思维导图</h1>
      <el-button type="primary" @click="showGenerateDialog = true">
        <el-icon><Share /></el-icon>
        生成思维导图
      </el-button>
    </div>

    <!-- Mind Maps List -->
    <el-card class="mindmaps-card">
      <template #header>
        <div class="card-header">
          <span>思维导图列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索思维导图..."
              style="width: 200px"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="statusFilter"
              placeholder="状态筛选"
              style="width: 120px"
              clearable
              @change="loadMindMaps"
            >
              <el-option label="活跃" value="active" />
              <el-option label="已归档" value="archived" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="mindMaps"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <div class="mindmap-title">
              <el-icon class="mindmap-icon"><Share /></el-icon>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="节点数" width="100">
          <template #default="{ row }">
            {{ row.nodes?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="连接数" width="100">
          <template #default="{ row }">
            {{ row.edges?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="测试用例" width="100">
          <template #default="{ row }">
            {{ row.test_case_ids?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewMindMap(row)"
            >
              查看
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="editMindMap(row)"
            >
              编辑
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="exportMindMap(row)"
            >
              导出
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteMindMap(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadMindMaps"
          @current-change="loadMindMaps"
        />
      </div>
    </el-card>

    <!-- Generate Mind Map Dialog -->
    <MindMapGenerateDialog
      v-model="showGenerateDialog"
      @success="handleGenerateSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { mindMapService } from '@/services/mindMapService'
import MindMapGenerateDialog from '@/components/mindmap/MindMapGenerateDialog.vue'
import {
  Share,
  Search
} from '@element-plus/icons-vue'

const router = useRouter()

// Data
const loading = ref(false)
const mindMaps = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const statusFilter = ref('')
const showGenerateDialog = ref(false)

// Methods
const loadMindMaps = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      ...(statusFilter.value && { status: statusFilter.value })
    }

    const response = await mindMapService.listMindMaps(params)
    mindMaps.value = response.mind_maps
    total.value = response.total
  } catch (error) {
    ElMessage.error('加载思维导图列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // TODO: Implement search functionality
  currentPage.value = 1
  loadMindMaps()
}

const viewMindMap = (mindMap) => {
  router.push(`/mindmaps/${mindMap.id}`)
}

const editMindMap = (mindMap) => {
  router.push(`/mindmaps/${mindMap.id}?edit=true`)
}

const exportMindMap = async (mindMap) => {
  try {
    // TODO: Implement export functionality
    ElMessage.success('导出功能开发中...')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const deleteMindMap = async (mindMap) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除思维导图 "${mindMap.title}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await mindMapService.deleteMindMap(mindMap.id)
    ElMessage.success('思维导图删除成功')
    loadMindMaps()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('思维导图删除失败')
    }
  }
}

const handleGenerateSuccess = () => {
  loadMindMaps()
}

// Utility methods
const getStatusColor = (status) => {
  const colors = {
    active: 'success',
    archived: 'info'
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    active: '活跃',
    archived: '已归档'
  }
  return texts[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// Lifecycle
onMounted(() => {
  loadMindMaps()
})
</script>

<style lang="scss" scoped>
.mindmaps-container {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      margin: 0;
      font-size: 24px;
      color: #303133;
    }
  }

  .mindmaps-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-actions {
        display: flex;
        gap: 12px;
        align-items: center;
      }
    }

    .mindmap-title {
      display: flex;
      align-items: center;
      gap: 8px;

      .mindmap-icon {
        color: #409eff;
      }
    }

    .pagination-wrapper {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}
</style>