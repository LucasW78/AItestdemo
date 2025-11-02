<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`文档查看 - ${document?.original_filename || ''}`"
    width="80%"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="document" class="document-viewer">
      <!-- Document Info -->
      <div class="document-info">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="文件名">
            {{ document.original_filename }}
          </el-descriptions-item>
          <el-descriptions-item label="文件类型">
            <el-tag :type="getFileTypeColor(document.file_type)">
              {{ document.file_type.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="文件大小">
            {{ formatFileSize(document.file_size) }}
          </el-descriptions-item>
          <el-descriptions-item label="处理状态">
            <el-tag :type="getStatusColor(document.processing_status)">
              {{ getStatusText(document.processing_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">
            {{ formatDate(document.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(document.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- Processing Actions -->
      <div class="processing-actions">
        <el-button
          v-if="document.processing_status === 'uploaded'"
          type="primary"
          :loading="processing"
          @click="processDocument"
        >
          <el-icon><Tools /></el-icon>
          处理文档
        </el-button>
        <el-button
          v-if="document.processed"
          type="success"
          @click="generateTestCases"
        >
          <el-icon><List /></el-icon>
          生成测试用例
        </el-button>
        <el-button
          v-if="document.processing_status === 'processing'"
          :loading="true"
        >
          <el-icon><Loading /></el-icon>
          处理中...
        </el-button>
      </div>

      <!-- Processing Error -->
      <el-alert
        v-if="document.processing_error"
        :title="'处理失败: ' + document.processing_error"
        type="error"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <!-- Extracted Text -->
      <div v-if="document.extracted_text" class="extracted-text">
        <div class="text-header">
          <h3>提取的文本内容</h3>
          <div class="text-actions">
            <el-button size="small" @click="copyText">
              <el-icon><DocumentCopy /></el-icon>
              复制文本
            </el-button>
            <el-button size="small" @click="downloadText">
              <el-icon><Download /></el-icon>
              下载文本
            </el-button>
          </div>
        </div>
        <el-card class="text-content">
          <pre>{{ document.extracted_text }}</pre>
        </el-card>
      </div>

      <!-- No Text Content -->
      <div v-else-if="document.processed && !document.extracted_text" class="no-content">
        <el-empty description="未提取到文本内容" />
      </div>

      <!-- Not Processed -->
      <div v-else-if="!document.processed" class="not-processed">
        <el-empty description="文档尚未处理">
          <el-button type="primary" @click="processDocument">
            立即处理
          </el-button>
        </el-empty>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { documentService } from '@/services/documentService'
import {
  Tools,
  List,
  Loading,
  DocumentCopy,
  Download
} from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  document: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'processed'])

const router = useRouter()
const processing = ref(false)

// Computed properties
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Methods
const processDocument = async () => {
  if (!props.document) return

  processing.value = true
  try {
    await documentService.processDocument(props.document.id)
    ElMessage.success('文档处理已开始')

    // Emit processed event to parent
    emit('processed')

    // Close dialog after a short delay
    setTimeout(() => {
      handleClose()
    }, 1500)
  } catch (error) {
    ElMessage.error('文档处理失败: ' + error.message)
  } finally {
    processing.value = false
  }
}

const generateTestCases = () => {
  if (!props.document) return

  // Navigate to test cases page with document ID
  router.push({
    path: '/testcases',
    query: { documentId: props.document.id }
  })

  handleClose()
}

const copyText = async () => {
  if (!props.document?.extracted_text) return

  try {
    await navigator.clipboard.writeText(props.document.extracted_text)
    ElMessage.success('文本已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const downloadText = () => {
  if (!props.document?.extracted_text) return

  try {
    const blob = new Blob([props.document.extracted_text], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${props.document.original_filename}_extracted.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('文本文件下载中...')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const handleClose = () => {
  dialogVisible.value = false
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

// Watch for document changes
watch(() => props.document, (newDocument) => {
  if (newDocument) {
    processing.value = false
  }
})
</script>

<style lang="scss" scoped>
.document-viewer {
  .document-info {
    margin-bottom: 20px;
  }

  .processing-actions {
    margin-bottom: 20px;
    display: flex;
    gap: 12px;
  }

  .extracted-text {
    .text-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      h3 {
        margin: 0;
        color: #303133;
      }

      .text-actions {
        display: flex;
        gap: 8px;
      }
    }

    .text-content {
      max-height: 400px;
      overflow-y: auto;

      pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.6;
        margin: 0;
        color: #303133;
      }
    }
  }

  .no-content,
  .not-processed {
    margin: 40px 0;
  }
}
</style>