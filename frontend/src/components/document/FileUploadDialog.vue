<template>
  <el-dialog
    v-model="dialogVisible"
    title="上传文档"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="upload-container">
      <!-- Upload Area -->
      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        :auto-upload="false"
        :limit="5"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :file-list="fileList"
        :accept="acceptTypes"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          <p>将文件拖拽到此处，或<em>点击上传</em></p>
          <p class="upload-hint">
            支持格式：TXT、PDF、Excel、JPG、PNG
          </p>
          <p class="upload-hint">
            最大文件大小：{{ maxFileSizeMB }}MB
          </p>
        </div>
      </el-upload>

      <!-- File List -->
      <div v-if="fileList.length > 0" class="file-list">
        <h4>待上传文件：</h4>
        <el-table :data="fileList" style="width: 100%">
          <el-table-column prop="name" label="文件名" min-width="200">
            <template #default="{ row }">
              <div class="file-item">
                <el-icon class="file-icon"><Document /></el-icon>
                <span>{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="size" label="大小" width="100">
            <template #default="{ row }">
              {{ formatFileSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'ready'" type="success">就绪</el-tag>
              <el-tag v-else-if="row.status === 'uploading'" type="warning">上传中</el-tag>
              <el-tag v-else-if="row.status === 'success'" type="success">成功</el-tag>
              <el-tag v-else-if="row.status === 'error'" type="danger">失败</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button
                type="danger"
                size="small"
                @click="removeFile($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Upload Progress -->
      <div v-if="uploading" class="upload-progress">
        <el-progress
          :percentage="uploadProgress"
          :status="uploadStatus"
          :stroke-width="8"
        />
        <p class="progress-text">{{ progressText }}</p>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="fileList.length === 0"
          @click="handleUpload"
        >
          {{ uploading ? '上传中...' : '开始上传' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { documentService } from '@/services/documentService'
import { UploadFilled, Document } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const uploadRef = ref()
const fileList = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const progressText = ref('')

// Computed properties
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const maxFileSizeMB = computed(() => 50) // 50MB
const maxFileSizeBytes = computed(() => maxFileSizeMB.value * 1024 * 1024)

const acceptTypes = computed(() => {
  return '.txt,.pdf,.xls,.xlsx,.jpg,.jpeg,.png'
})

// Methods
const handleFileChange = (file, fileList) => {
  // Validate file size
  if (file.size > maxFileSizeBytes.value) {
    ElMessage.error(`文件 ${file.name} 超过最大大小限制 ${maxFileSizeMB.value}MB`)
    return false
  }

  // Validate file type
  const validTypes = ['txt', 'pdf', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
  const fileExtension = file.name.split('.').pop().toLowerCase()
  if (!validTypes.includes(fileExtension)) {
    ElMessage.error(`文件 ${file.name} 格式不支持`)
    return false
  }

  // Set file status
  file.status = 'ready'
  return true
}

const handleFileRemove = (file, fileList) => {
  // Handle file removal
}

const removeFile = (index) => {
  fileList.value.splice(index, 1)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = ''
  progressText.value = '准备上传...'

  try {
    // Upload files one by one
    const totalFiles = fileList.value.length
    let successCount = 0
    let errorCount = 0

    for (let i = 0; i < totalFiles; i++) {
      const file = fileList.value[i]

      // Update file status to uploading
      file.status = 'uploading'
      progressText.value = `正在上传 ${file.name} (${i + 1}/${totalFiles})`

      try {
        // Create FormData
        const formData = new FormData()
        formData.append('file', file.raw)

        // Upload file with progress callback
        await documentService.uploadDocument(formData, (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            uploadProgress.value = Math.round(((i * 100) + progress) / totalFiles)
          }
        })

        // Update file status to success
        file.status = 'success'
        successCount++

      } catch (error) {
        // Update file status to error
        file.status = 'error'
        errorCount++
        ElMessage.error(`文件 ${file.name} 上传失败: ${error.message}`)
      }
    }

    // Update final progress
    uploadProgress.value = 100
    uploadStatus.value = successCount === totalFiles ? 'success' : 'warning'

    // Show result message
    if (successCount > 0) {
      ElMessage.success(`成功上传 ${successCount} 个文件`)
    }
    if (errorCount > 0) {
      ElMessage.warning(`${errorCount} 个文件上传失败`)
    }

    // Emit success event
    emit('success')

    // Close dialog after delay
    setTimeout(() => {
      handleClose()
    }, 2000)

  } catch (error) {
    ElMessage.error('上传过程中发生错误')
    uploadStatus.value = 'exception'
  } finally {
    uploading.value = false
  }
}

const handleClose = () => {
  // Reset state
  fileList.value = []
  uploading.value = false
  uploadProgress.value = 0
  uploadStatus.value = ''
  progressText.value = ''

  // Clear upload component
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }

  // Close dialog
  dialogVisible.value = false
}

// Watch for dialog visibility changes
watch(dialogVisible, (newValue) => {
  if (!newValue) {
    handleClose()
  }
})
</script>

<style lang="scss" scoped>
.upload-container {
  .upload-area {
    width: 100%;

    :deep(.el-upload-dragger) {
      width: 100%;
      height: 200px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      border: 2px dashed #d9d9d9;
      border-radius: 6px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: border-color 0.3s ease;

      &:hover {
        border-color: #409eff;
      }
    }

    .upload-icon {
      font-size: 48px;
      color: #c0c4cc;
      margin-bottom: 16px;
    }

    .upload-text {
      text-align: center;
      color: #606266;

      p {
        margin: 8px 0;
      }

      .upload-hint {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .file-list {
    margin-top: 20px;

    h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      color: #303133;
    }

    .file-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .file-icon {
        color: #409eff;
      }
    }
  }

  .upload-progress {
    margin-top: 20px;

    .progress-text {
      margin-top: 10px;
      text-align: center;
      color: #606266;
      font-size: 14px;
    }
  }
}
</style>