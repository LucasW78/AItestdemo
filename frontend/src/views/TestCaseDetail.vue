<template>
  <div class="testcase-detail-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测试用例详情</span>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </template>
      <div class="placeholder-content">
        <p>测试用例详情页面 - 开发中...</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// Test case detail page - will be implemented later
</script>

<style lang="scss" scoped>
.testcase-detail-container {
  .placeholder-content {
    text-align: center;
    padding: 40px;
    color: #909399;
  }
}
</style>