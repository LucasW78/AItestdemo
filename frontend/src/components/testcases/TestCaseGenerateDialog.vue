<template>
  <el-dialog
    v-model="dialogVisible"
    title="生成测试用例"
    width="70%"
    :before-close="handleClose"
  >
    <div class="test-case-generation">
      <!-- 输入方式选择 -->
      <el-form :model="form" label-width="120px">
        <el-form-item label="输入方式">
          <el-radio-group v-model="inputMode" @change="handleInputModeChange">
            <el-radio label="text">在线文本输入</el-radio>
            <el-radio label="file">上传文档</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 在线文本输入区域 -->
        <template v-if="inputMode === 'text'">
          <el-form-item label="功能描述">
            <el-input
              v-model="form.scenario"
              type="text"
              placeholder="例如：用户登录功能、商品搜索功能、订单支付流程等"
              clearable
            />
          </el-form-item>

          <el-form-item label="详细内容">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="8"
              placeholder="请详细描述要测试的功能、业务流程、界面交互等内容..."
              show-word-limit
              maxlength="2000"
            />
          </el-form-item>
        </template>

        <!-- 文档上传区域 -->
        <template v-else>
          <el-form-item label="选择文档">
            <el-upload
              ref="uploadRef"
              class="upload-demo"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="false"
              accept=".txt,.pdf,.doc,.docx,.xls,.xlsx"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 txt/pdf/doc/docx/xls/xlsx 文件，文件大小不超过 50MB
                </div>
              </template>
            </el-upload>

            <div v-if="selectedFile" class="file-info">
              <el-tag type="success" closable @close="clearFile">
                <el-icon><Document /></el-icon>
                {{ selectedFile.name }}
              </el-tag>
            </div>
          </el-form-item>
        </template>

        <el-form-item label="测试类型">
          <el-select v-model="form.testType" placeholder="选择测试类型">
            <el-option label="功能测试" value="functional" />
            <el-option label="性能测试" value="performance" />
            <el-option label="安全测试" value="security" />
          </el-select>
        </el-form-item>

        <!-- 快速模板 -->
        <el-form-item label="快速模板">
          <div class="template-buttons">
            <el-button
              v-for="template in templates"
              :key="template.name"
              size="small"
              @click="applyTemplate(template)"
            >
              {{ template.name }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="generateTestCases" :loading="loading" :disabled="!canGenerate">
          {{ inputMode === 'text' ? '生成测试用例' : '上传并生成' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineEmits, defineProps, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'generated'])

const dialogVisible = ref(props.modelValue)
const loading = ref(false)
const inputMode = ref('text')
const selectedFile = ref(null)
const uploadRef = ref(null)

const form = ref({
  content: '',
  scenario: '',
  testType: 'functional'
})

// 快速模板
const templates = ref([
  {
    name: '用户登录',
    scenario: '用户登录功能',
    content: '用户需要通过用户名和密码登录系统，登录成功后跳转到首页。需要支持记住密码、忘记密码等功能。'
  },
  {
    name: '商品搜索',
    scenario: '商品搜索功能',
    content: '用户可以在搜索框中输入关键词搜索商品，支持模糊搜索、分类筛选、价格区间筛选等功能。'
  },
  {
    name: '购物车',
    scenario: '购物车功能',
    content: '用户可以将商品添加到购物车，修改数量，删除商品，进行结算。支持优惠券使用和价格计算。'
  },
  {
    name: '订单支付',
    scenario: '订单支付流程',
    content: '用户选择商品后生成订单，选择支付方式完成支付，支持支付宝、微信支付等多种支付方式。'
  },
  {
    name: '用户注册',
    scenario: '用户注册功能',
    content: '新用户需要填写用户名、邮箱、密码等信息完成注册，需要进行邮箱验证和手机号验证。'
  }
])

// 计算属性：是否可以生成测试用例
const canGenerate = computed(() => {
  if (inputMode.value === 'text') {
    return form.value.content.trim().length > 0
  } else {
    return selectedFile.value !== null
  }
})

const handleClose = () => {
  dialogVisible.value = false
  emit('update:modelValue', false)
  resetForm()
}

const resetForm = () => {
  form.value = {
    content: '',
    scenario: '',
    testType: 'functional'
  }
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const handleInputModeChange = (mode) => {
  resetForm()
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  ElMessage.success(`已选择文件: ${file.name}`)
}

const clearFile = () => {
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const applyTemplate = (template) => {
  form.value.scenario = template.scenario
  form.value.content = template.content
  ElMessage.success(`已应用模板: ${template.name}`)
}

const generateTestCases = async () => {
  if (inputMode.value === 'text' && !form.value.content.trim()) {
    ElMessage.warning('请输入要生成测试用例的内容')
    return
  }

  if (inputMode.value === 'file' && !selectedFile.value) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  loading.value = true
  try {
    let response

    if (inputMode.value === 'text') {
      // 使用文本输入API
      const formData = new FormData()
      formData.append('content', form.value.content)
      formData.append('test_type', form.value.testType)
      if (form.value.scenario) {
        formData.append('scenario', form.value.scenario)
      }

      response = await fetch('/api/v1/testcases/generate-from-text', {
        method: 'POST',
        body: formData
      })
    } else {
      // 使用文件上传API
      const formData = new FormData()
      formData.append('file', selectedFile.value)

      response = await fetch('/api/v1/documents/upload', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const uploadResult = await response.json()

        // 上传成功后生成测试用例
        const generateData = {
          content: uploadResult.filename,
          test_type: form.value.testType
        }

        const generateResponse = await fetch('/api/v1/testcases/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(generateData)
        })

        if (generateResponse.ok) {
          response = generateResponse
        } else {
          throw new Error('生成测试用例失败')
        }
      }
    }

    if (response.ok) {
      const result = await response.json()
      ElMessage.success('测试用例生成成功！')
      emit('generated', {
        ...result,
        inputMode: inputMode.value,
        generatedAt: new Date().toISOString()
      })
      handleClose()
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '生成测试用例失败，请重试')
    }
  } catch (error) {
    console.error('生成测试用例错误:', error)
    ElMessage.error('生成测试用例失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.test-case-generation {
  padding: 20px 0;
}

.template-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-buttons .el-button {
  margin: 0;
}

.file-info {
  margin-top: 10px;
}

.file-info .el-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.upload-demo {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-form-item__content) {
  display: block;
}

:deep(.el-radio-group) {
  display: flex;
  gap: 20px;
}

@media (max-width: 768px) {
  .template-buttons {
    flex-direction: column;
  }

  .template-buttons .el-button {
    width: 100%;
  }
}
</style>