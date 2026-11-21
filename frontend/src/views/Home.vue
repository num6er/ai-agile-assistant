<template>
  <div>
    <div class="page-header">
      <h2>项目列表</h2>
      <el-button type="primary" @click="showDialog = true">+ 新建项目</el-button>
    </div>

    <el-table :data="projects" border v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ row.created_at ? new Date(row.created_at).toLocaleString() : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/projects/${row.id}`)">进入</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" title="新建项目" width="500px">
      <el-form label-width="80px">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" placeholder="如:AI 敏捷开发助手" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="create">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectApi } from '../api'

const projects = ref([])
const loading = ref(false)
const showDialog = ref(false)
const form = ref({ name: '', description: '' })

const load = async () => {
  loading.value = true
  try {
    const { data } = await projectApi.list()
    projects.value = data
  } finally {
    loading.value = false
  }
}

const create = async () => {
  if (!form.value.name) return ElMessage.warning('请输入项目名称')
  await projectApi.create(form.value)
  showDialog.value = false
  form.value = { name: '', description: '' }
  ElMessage.success('创建成功')
  load()
}

const remove = async (id) => {
  await ElMessageBox.confirm('确认删除该项目?', '提示', { type: 'warning' })
  await projectApi.remove(id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
h2 { margin: 0; }
</style>
