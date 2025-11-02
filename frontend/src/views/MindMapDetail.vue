<template>
  <div class="mindmap-detail-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>思维导图详情</span>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </template>
      <div class="placeholder-content">
        <p>思维导图详情页面 - 开发中...</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// Mind map detail page - will be implemented later
</script>

<style lang="scss" scoped>
.mindmap-detail-container {
  .placeholder-content {
    text-align: center;
    padding: 40px;
    color: #909399;
  }
}
</style>