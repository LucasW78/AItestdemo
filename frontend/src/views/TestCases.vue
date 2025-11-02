<template>
  <div class="testcases-container">
    <div class="page-header">
      <h1 class="page-title">测试用例</h1>
      <el-button type="primary" @click="showGenerateDialog = true">
        <el-icon><Magic /></el-icon>
        生成测试用例
      </el-button>
    </div>

    <!-- Test Cases List -->
    <el-card class="testcases-card">
      <template #header>
        <div class="card-header">
          <span>测试用例列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索测试用例..."
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
              @change="loadTestCases"
            >
              <el-option label="草稿" value="draft" />
              <el-option label="已审核" value="approved" />
              <el-option label="已废弃" value="deprecated" />
            </el-select>
            <el-select
              v-model="priorityFilter"
              placeholder="优先级筛选"
              style="width: 120px"
              clearable
              @change="loadTestCases"
            >
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="critical" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="testCases"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <div class="testcase-title">
              <el-icon class="testcase-icon"><List /></el-icon>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.category" type="info">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityColor(row.priority)">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="步骤数" width="80">
          <template #default="{ row }">
            {{ row.steps?.length || 0 }}
          </template>
        </el-table-column>
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
              @click="viewTestCase(row)"
            >
              查看
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="editTestCase(row)"
            >
              编辑
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="generateMindMap([row.id])"
            >
              导图
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteTestCase(row)"
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
          @size-change="loadTestCases"
          @current-change="loadTestCases"
        />
      </div>
    </el-card>

    <!-- Generate Test Cases Dialog -->
    <TestCaseGenerateDialog
      v-model="showGenerateDialog"
      @success="handleGenerateSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { testCaseService } from '@/services/testCaseService'
import { mindMapService } from '@/services/mindMapService'
import TestCaseGenerateDialog from '@/components/testcases/TestCaseGenerateDialog.vue'
import {
  Magic,
  Search,
  List
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// Data
const loading = ref(false)
const testCases = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const statusFilter = ref('')
const priorityFilter = ref('')
const showGenerateDialog = ref(false)

// Methods
const loadTestCases = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      ...(statusFilter.value && { status: statusFilter.value }),
      ...(priorityFilter.value && { priority: priorityFilter.value }),
      ...(route.query.documentId && { document_id: route.query.documentId })
    }

    const response = await testCaseService.listTestCases(params)
    testCases.value = response.test_cases
    total.value = response.total
  } catch (error) {
    ElMessage.error('加载测试用例列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // TODO: Implement search functionality
  currentPage.value = 1
  loadTestCases()
}

const viewTestCase = (testCase) => {
  router.push(`/testcases/${testCase.id}`)
}

const editTestCase = (testCase) => {
  router.push(`/testcases/${testCase.id}?edit=true`)
}

const generateMindMap = async (testCaseIds) => {
  try {
    const response = await mindMapService.generateMindMap({
      test_case_ids: testCaseIds,
      title: '测试用例思维导图'
    })
    ElMessage.success('思维导图生成已开始')
    router.push('/mindmaps')
  } catch (error) {
    ElMessage.error('思维导图生成失败')
  }
}

const deleteTestCase = async (testCase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例 "${testCase.title}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await testCaseService.deleteTestCase(testCase.id)
    ElMessage.success('测试用例删除成功')
    loadTestCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('测试用例删除失败')
    }
  }
}

const handleGenerateSuccess = () => {
  loadTestCases()
}

// Utility methods
const getPriorityColor = (priority) => {
  const colors = {
    low: 'info',
    medium: 'success',
    high: 'warning',
    critical: 'danger'
  }
  return colors[priority] || 'info'
}

const getPriorityText = (priority) => {
  const texts = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '紧急'
  }
  return texts[priority] || priority
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'info',
    approved: 'success',
    deprecated: 'danger'
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    approved: '已审核',
    deprecated: '已废弃'
  }
  return texts[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// Lifecycle
onMounted(() => {
  loadTestCases()
})
</script>

<style lang="scss" scoped>
.testcases-container {
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

  .testcases-card {
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

    .testcase-title {
      display: flex;
      align-items: center;
      gap: 8px;

      .testcase-icon {
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