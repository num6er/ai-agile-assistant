<template>
  <el-container>
    <el-header class="header">
      <div class="logo">AI 敏捷开发助手</div>
      <div class="subtitle">PRD → 用户故事 → 任务 → 工时 → 分配 一键自动化</div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<style>
body { margin: 0; font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; }
.header {
  background: linear-gradient(90deg, #409eff, #6c5ce7);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 24px;
  height: 70px;
}
.logo { font-size: 20px; font-weight: 600; }
.subtitle { font-size: 12px; opacity: 0.85; margin-top: 4px; }
.el-main { padding: 24px; max-width: 1200px; margin: 0 auto; width: 100%; }
</style>
