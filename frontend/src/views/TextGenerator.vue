<template>
  <div class="text-generator-container">
    <div class="page-header">
      <h1 class="page-title">文本输入生成测试用例</h1>
      <el-button @click="$router.push('/testcases')">
        <el-icon><ArrowLeft /></el-icon>
        返回测试用例列表
      </el-button>
    </div>

    <div class="generator-content">
      <el-row :gutter="24">
        <!-- 输入区域 -->
        <el-col :span="12">
          <el-card class="input-card">
            <template #header>
              <div class="card-header">
                <span>输入区域</span>
                <el-tag type="info">简单模式</el-tag>
              </div>
            </template>

            <el-form :model="form" label-width="100px">
              <el-form-item label="功能描述">
                <el-input
                  v-model="form.scenario"
                  placeholder="例如：用户登录功能、商品搜索功能"
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

              <el-form-item>
                <el-button
                  type="primary"
                  @click="generateTestCases"
                  :loading="loading"
                  :disabled="!canGenerate"
                  size="large"
                  style="width: 100%"
                >
                  {{ loading ? '生成中...' : '生成测试用例' }}
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 结果区域 -->
        <el-col :span="12">
          <el-card class="result-card">
            <template #header>
              <div class="card-header">
                <span>生成结果</span>
                <el-button
                  v-if="generatedCases.length > 0"
                  type="success"
                  size="small"
                  @click="saveTestCases"
                >
                  保存到系统
                </el-button>
              </div>
            </template>

            <div v-if="loading" class="loading-container">
              <el-icon class="is-loading"><Loading /></el-icon>
              <p>正在生成测试用例，请稍候...</p>
            </div>

            <div v-else-if="generatedCases.length === 0" class="empty-result">
              <el-empty description="暂无生成结果，请先输入内容并点击生成按钮">
                <el-icon><Document /></el-icon>
              </el-empty>
            </div>

            <div v-else class="result-list">
              <div
                v-for="(testCase, index) in generatedCases"
                :key="testCase.id"
                class="test-case-item"
              >
                <div class="case-header">
                  <h4>{{ testCase.title }}</h4>
                  <el-tag :type="getPriorityColor(testCase.priority)" size="small">
                    {{ getPriorityText(testCase.priority) }}
                  </el-tag>
                </div>
                <p class="case-description">{{ testCase.description }}</p>
                <div class="case-steps">
                  <h5>测试步骤：</h5>
                  <ol>
                    <li v-for="step in testCase.steps" :key="step">{{ step }}</li>
                  </ol>
                </div>
                <div class="case-expected">
                  <strong>预期结果：</strong>{{ testCase.expected_result }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Loading, Document } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const generatedCases = ref([])

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

// 计算属性
const canGenerate = computed(() => {
  return form.value.content.trim().length > 0 && !loading.value
})

// 方法
const applyTemplate = (template) => {
  form.value.scenario = template.scenario
  form.value.content = template.content
  ElMessage.success(`已应用模板: ${template.name}`)
}

const generateTestCases = async () => {
  if (!form.value.content.trim()) {
    ElMessage.warning('请输入要生成测试用例的内容')
    return
  }

  loading.value = true
  generatedCases.value = []

  try {
    const formData = new FormData()
    formData.append('content', form.value.content)
    formData.append('test_type', form.value.testType)
    if (form.value.scenario) {
      formData.append('scenario', form.value.scenario)
    }

    console.log('发送POST请求到: /api/v1/testcases/generate-from-text')
    console.log('FormData内容:', {
      content: form.value.content,
      test_type: form.value.testType,
      scenario: form.value.scenario
    })

    const response = await fetch('/api/v1/testcases/generate-from-text', {
      method: 'POST',
      body: formData
    })

    console.log('响应状态:', response.status, response.statusText)

    if (response.ok) {
      const result = await response.json()
      generatedCases.value = result.generated_cases || []
      ElMessage.success(`成功生成 ${generatedCases.value.length} 个测试用例！`)
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

const saveTestCases = () => {
  // TODO: 实现保存到系统的功能
  ElMessage.success('测试用例已保存到系统！')
  // 可以跳转到测试用例列表页面
  setTimeout(() => {
    this.$router.push('/testcases')
  }, 1000)
}

// 辅助方法
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
</script>

<style scoped>
.text-generator-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.page-title {
  margin: 0;
  font-size: 28px;
  color: #303133;
  font-weight: 600;
}

.generator-content {
  margin-top: 20px;
}

.input-card, .result-card {
  height: fit-content;
  min-height: 600px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.template-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-buttons .el-button {
  margin: 0;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-result {
  padding: 60px 20px;
}

.result-list {
  max-height: 500px;
  overflow-y: auto;
}

.test-case-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background: #fafafa;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.case-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.case-description {
  margin: 0 0 12px 0;
  color: #606266;
  line-height: 1.5;
}

.case-steps {
  margin-bottom: 12px;
}

.case-steps h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
}

.case-steps ol {
  margin: 0;
  padding-left: 20px;
}

.case-steps li {
  margin-bottom: 4px;
  color: #606266;
  line-height: 1.4;
}

.case-expected {
  color: #67c23a;
  font-size: 14px;
  line-height: 1.4;
}

@media (max-width: 1200px) {
  .text-generator-container {
    padding: 16px;
  }

  .el-col {
    margin-bottom: 20px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .template-buttons {
    flex-direction: column;
  }

  .template-buttons .el-button {
    width: 100%;
  }
}
</style>