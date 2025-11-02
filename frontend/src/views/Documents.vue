<template>
  <div class="documents-container">
    <div class="page-header">
      <h1 class="page-title">文档管理</h1>
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        上传文档
      </el-button>
    </div>

    <!-- Document List -->
    <el-card class="documents-card">
      <template #header>
        <div class="card-header">
          <span>文档列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索文档..."
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
              @change="loadDocuments"
            >
              <el-option label="已上传" value="uploaded" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="documents"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="original_filename" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-info">
              <el-icon class="file-icon"><Document /></el-icon>
              <span>{{ row.original_filename }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="getFileTypeColor(row.file_type)">
              {{ row.file_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="processing_status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.processing_status)">
              {{ getStatusText(row.processing_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.processed"
              type="primary"
              size="small"
              @click="generateTestCases(row)"
            >
              生成用例
            </el-button>
            <el-button
              v-if="row.processing_status === 'uploaded'"
              type="success"
              size="small"
              @click="processDocument(row)"
            >
              处理文档
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="viewDocument(row)"
            >
              查看
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteDocument(row)"
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
          @size-change="loadDocuments"
          @current-change="loadDocuments"
        />
      </div>
    </el-card>

    <!-- Upload Dialog -->
    <FileUploadDialog
      v-model="showUploadDialog"
      @success="handleUploadSuccess"
    />

    <!-- Document Viewer Dialog -->
    <DocumentViewerDialog
      v-model="showViewerDialog"
      :document="selectedDocument"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { documentService } from '@/services/documentService'
import FileUploadDialog from '@/components/document/FileUploadDialog.vue'
import DocumentViewerDialog from '@/components/document/DocumentViewerDialog.vue'
import {
  Upload,
  Search,
  Document
} from '@element-plus/icons-vue'

const router = useRouter()

// Data
const loading = ref(false)
const documents = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const statusFilter = ref('')
const showUploadDialog = ref(false)
const showViewerDialog = ref(false)
const selectedDocument = ref(null)

// Methods
const loadDocuments = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      ...(statusFilter.value && { status: statusFilter.value })
    }

    const response = await documentService.listDocuments(params)
    documents.value = response.documents
    total.value = response.total
  } catch (error) {
    ElMessage.error('加载文档列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // TODO: Implement search functionality
  currentPage.value = 1
  loadDocuments()
}

const processDocument = async (document) => {
  try {
    await documentService.processDocument(document.id)
    ElMessage.success('文档处理已开始')
    loadDocuments()
  } catch (error) {
    ElMessage.error('文档处理失败')
  }
}

const generateTestCases = (document) => {
  router.push({
    path: '/testcases',
    query: { documentId: document.id }
  })
}

const viewDocument = (document) => {
  selectedDocument.value = document
  showViewerDialog.value = true
}

const deleteDocument = async (document) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${document.original_filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await documentService.deleteDocument(document.id)
    ElMessage.success('文档删除成功')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('文档删除失败')
    }
  }
}

const handleUploadSuccess = () => {
  loadDocuments()
}

// Utility methods
const getFileTypeColor = (type) => {
  const colors = {
    pdf: 'danger',
    doc: 'primary',
    docx: 'primary',
    xls: 'success',
    xlsx: 'success',
    jpg: 'warning',
    jpeg: 'warning',
    png: 'warning',
    txt: 'info'
  }
  return colors[type] || 'info'
}

const getStatusColor = (status) => {
  const colors = {
    uploaded: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    uploaded: '已上传',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// Lifecycle
onMounted(() => {
  loadDocuments()
})
</script>

<style lang="scss" scoped>
.documents-container {
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

  .documents-card {
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

    .file-info {
      display: flex;
      align-items: center;
      gap: 8px;

      .file-icon {
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