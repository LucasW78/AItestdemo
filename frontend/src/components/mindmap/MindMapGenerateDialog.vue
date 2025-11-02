<template>
  <el-dialog
    v-model="dialogVisible"
    title="生成思维导图"
    width="60%"
    :before-close="handleClose"
  >
    <div class="mindmap-generation">
      <el-form :model="form" label-width="120px">
        <el-form-item label="主题内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="请输入要生成思维导图的内容..."
          />
        </el-form-item>
        <el-form-item label="导图样式">
          <el-select v-model="form.style" placeholder="选择导图样式">
            <el-option label="思维导图" value="mindmap" />
            <el-option label="组织结构图" value="org" />
            <el-option label="流程图" value="flow" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="generateMindMap" :loading="loading">
          生成思维导图
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineEmits, defineProps } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'generated'])

const dialogVisible = ref(props.modelValue)
const loading = ref(false)
const form = ref({
  content: '',
  style: 'mindmap'
})

const handleClose = () => {
  dialogVisible.value = false
  emit('update:modelValue', false)
}

const generateMindMap = async () => {
  if (!form.value.content.trim()) {
    ElMessage.warning('请输入要生成思维导图的内容')
    return
  }

  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))

    ElMessage.success('思维导图生成成功！')
    emit('generated', {
      content: form.value.content,
      style: form.value.style,
      generatedAt: new Date().toISOString()
    })
    handleClose()
  } catch (error) {
    ElMessage.error('生成思维导图失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.mindmap-generation {
  padding: 20px 0;
}
</style>