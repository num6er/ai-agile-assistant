<template>
  <div v-loading="loading">
    <el-page-header @back="$router.push('/')" :content="project?.name || '项目详情'" />

    <!-- 步骤指引 -->
    <el-steps :active="step" finish-status="success" class="steps">
      <el-step title="上传 PRD" />
      <el-step title="AI 解析" />
      <el-step title="生成用户故事" />
      <el-step title="拆解任务" />
      <el-step title="估算工时" />
      <el-step title="AI 分配" />
    </el-steps>

    <!-- 成员管理 -->
    <el-card class="block">
      <template #header>
        <div class="card-head">
          <span>团队成员</span>
          <el-button size="small" type="primary" @click="memberDialog = true">+ 添加成员</el-button>
        </div>
      </template>
      <el-tag v-for="m in members" :key="m.id" class="member-tag" closable @close="removeMember(m.id)">
        {{ m.name }} · {{ m.role }}
      </el-tag>
      <el-empty v-if="!members.length" description="暂无成员" :image-size="40" />
    </el-card>

    <!-- PRD 上传 -->
    <el-card class="block">
      <template #header>需求文档(PRD)</template>
      <el-form label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="prdForm.title" placeholder="如:电商后台 PRD v1" />
        </el-form-item>
        <el-form-item label="PRD 内容">
          <el-input v-model="prdForm.content" type="textarea" :rows="6"
            placeholder="粘贴 PRD 文本,系统会用 AI 抽取功能点..." />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveRequirement" :loading="savingPrd">保存需求</el-button>
          <el-button type="success" @click="parseRequirement" :loading="parsing"
            :disabled="!currentRequirementId">① AI 解析功能点</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- AI 解析结果 -->
    <el-card v-if="parsedFeatures" class="block">
      <template #header>AI 解析出的功能点</template>
      <p class="summary">{{ parsedFeatures.summary }}</p>
      <el-table :data="parsedFeatures.features" border size="small">
        <el-table-column prop="name" label="功能" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="100" />
      </el-table>
      <div class="block-actions">
        <el-button type="success" @click="generateStories" :loading="generating">② 生成用户故事</el-button>
      </div>
    </el-card>

    <!-- 用户故事 -->
    <el-card v-if="stories.length" class="block">
      <template #header>用户故事</template>
      <el-table :data="stories" border size="small">
        <el-table-column prop="code" label="编号" width="80" />
        <el-table-column label="故事">
          <template #default="{ row }">
            作为 <b>{{ row.role }}</b>,我希望 <b>{{ row.goal }}</b>,以便 {{ row.benefit }}
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90" />
        <el-table-column prop="story_points" label="故事点" width="80" />
        <el-table-column label="操作" width="130">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="decompose(row.id)" :loading="decomposingId === row.id">
              ③ 拆任务
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 任务看板 -->
    <el-card v-if="tasks.length" class="block">
      <template #header>
        <div class="card-head">
          <span>任务看板(共 {{ tasks.length }} 个)</span>
          <div>
            <el-button size="small" type="success" @click="estimate" :loading="estimating">④ AI 估算工时</el-button>
            <el-button size="small" type="warning" @click="assign" :loading="assigning"
              :disabled="!members.length">⑤ AI 分配</el-button>
          </div>
        </div>
      </template>
      <el-table :data="tasks" border size="small">
        <el-table-column prop="title" label="任务" />
        <el-table-column prop="type" label="类型" width="90" />
        <el-table-column prop="complexity" label="复杂度" width="90" />
        <el-table-column prop="estimate_hours" label="估时(h)" width="100" />
        <el-table-column prop="assignee_name" label="负责人" width="100" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-select v-model="row.status" size="small" @change="updateTask(row)">
              <el-option label="待办" value="todo" />
              <el-option label="进行中" value="doing" />
              <el-option label="已完成" value="done" />
            </el-select>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>

  <!-- 添加成员对话框 -->
  <el-dialog v-model="memberDialog" title="添加成员" width="450px">
    <el-form label-width="80px">
      <el-form-item label="姓名"><el-input v-model="memberForm.name" /></el-form-item>
      <el-form-item label="角色">
        <el-select v-model="memberForm.role">
          <el-option label="组长/产品" value="leader" />
          <el-option label="后端" value="backend" />
          <el-option label="前端" value="frontend" />
          <el-option label="测试" value="test" />
          <el-option label="运维" value="devops" />
        </el-select>
      </el-form-item>
      <el-form-item label="技能">
        <el-input v-model="memberForm.skillsStr" placeholder="逗号分隔,如:python,flask,sql" />
      </el-form-item>
      <el-form-item label="周工时">
        <el-input-number v-model="memberForm.capacity" :min="1" :max="60" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="memberDialog = false">取消</el-button>
      <el-button type="primary" @click="addMember">添加</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { projectApi, requirementApi, storyApi, taskApi, memberApi } from '../api'

const props = defineProps({ id: String })

const loading = ref(false)
const project = ref(null)
const members = ref([])
const requirements = ref([])
const currentRequirementId = ref(null)
const parsedFeatures = ref(null)
const stories = ref([])
const tasks = ref([])

const prdForm = ref({ title: '', content: '' })
const savingPrd = ref(false)
const parsing = ref(false)
const generating = ref(false)
const decomposingId = ref(null)
const estimating = ref(false)
const assigning = ref(false)

const memberDialog = ref(false)
const memberForm = ref({ name: '', role: 'backend', skillsStr: '', capacity: 40 })

const step = computed(() => {
  if (assigning.value || tasks.value.some(t => t.assignee_id)) return 6
  if (tasks.value.some(t => t.estimate_hours)) return 5
  if (tasks.value.length) return 4
  if (stories.value.length) return 3
  if (parsedFeatures.value) return 2
  if (currentRequirementId.value) return 1
  return 0
})

const load = async () => {
  loading.value = true
  try {
    const [{ data: p }, { data: ms }, { data: reqs }, { data: ss }, { data: ts }] = await Promise.all([
      projectApi.get(props.id), memberApi.list(props.id),
      requirementApi.list(props.id), storyApi.list(props.id), taskApi.list(props.id),
    ])
    project.value = p
    members.value = ms
    requirements.value = reqs
    stories.value = ss
    tasks.value = ts
    if (reqs.length) {
      currentRequirementId.value = reqs[0].id
      prdForm.value.title = reqs[0].title
      prdForm.value.content = reqs[0].content
    }
  } finally {
    loading.value = false
  }
}

const saveRequirement = async () => {
  if (!prdForm.value.title || !prdForm.value.content) return ElMessage.warning('请填写标题和内容')
  savingPrd.value = true
  try {
    const { data } = await requirementApi.create({ project_id: Number(props.id), ...prdForm.value })
    currentRequirementId.value = data.id
    ElMessage.success('需求已保存')
  } finally {
    savingPrd.value = false
  }
}

const parseRequirement = async () => {
  parsing.value = true
  try {
    const { data } = await requirementApi.parse(currentRequirementId.value)
    parsedFeatures.value = data
    ElMessage.success(`AI 解析出 ${data.features.length} 个功能点`)
  } catch (e) {
    ElMessage.error('AI 解析失败:' + (e.response?.data?.error || e.message))
  } finally {
    parsing.value = false
  }
}

const generateStories = async () => {
  generating.value = true
  try {
    const { data } = await storyApi.generate(currentRequirementId.value)
    stories.value = data
    ElMessage.success(`生成 ${data.length} 个用户故事`)
  } catch (e) {
    ElMessage.error('生成失败:' + (e.response?.data?.error || e.message))
  } finally {
    generating.value = false
  }
}

const decompose = async (storyId) => {
  decomposingId.value = storyId
  try {
    const { data } = await taskApi.decompose(storyId)
    tasks.value = [...tasks.value, ...data]
    ElMessage.success(`拆解出 ${data.length} 个任务`)
  } catch (e) {
    ElMessage.error('拆解失败:' + (e.response?.data?.error || e.message))
  } finally {
    decomposingId.value = null
  }
}

const estimate = async () => {
  estimating.value = true
  try {
    const { data } = await taskApi.estimate(props.id)
    tasks.value = data
    ElMessage.success('工时估算完成')
  } catch (e) {
    ElMessage.error('估算失败:' + (e.response?.data?.error || e.message))
  } finally {
    estimating.value = false
  }
}

const assign = async () => {
  assigning.value = true
  try {
    const { data } = await taskApi.assign(props.id)
    tasks.value = data
    ElMessage.success('AI 分配完成')
  } catch (e) {
    ElMessage.error('分配失败:' + (e.response?.data?.error || e.message))
  } finally {
    assigning.value = false
  }
}

const updateTask = async (row) => {
  await taskApi.update(row.id, { status: row.status })
}

const addMember = async () => {
  if (!memberForm.value.name) return ElMessage.warning('请输入姓名')
  await memberApi.create({
    project_id: Number(props.id),
    name: memberForm.value.name,
    role: memberForm.value.role,
    skills: memberForm.value.skillsStr.split(',').map(s => s.trim()).filter(Boolean),
    capacity_hours: memberForm.value.capacity,
  })
  memberDialog.value = false
  memberForm.value = { name: '', role: 'backend', skillsStr: '', capacity: 40 }
  ElMessage.success('已添加')
  load()
}

const removeMember = async (id) => {
  await memberApi.remove(id)
  load()
}

load()
</script>

<style scoped>
.steps { margin: 20px 0; }
.block { margin-bottom: 20px; }
.card-head { display: flex; justify-content: space-between; align-items: center; }
.block-actions { margin-top: 12px; }
.summary { color: #666; margin: 0 0 12px; }
.member-tag { margin: 0 8px 8px 0; }
</style>
