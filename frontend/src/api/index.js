import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// 项目
export const projectApi = {
  list: () => api.get('/projects'),
  create: (data) => api.post('/projects', data),
  get: (id) => api.get(`/projects/${id}`),
  remove: (id) => api.delete(`/projects/${id}`),
}

// 需求
export const requirementApi = {
  create: (data) => api.post('/requirements', data),
  list: (projectId) => api.get('/requirements', { params: { project_id: projectId } }),
  parse: (rid) => api.post(`/requirements/${rid}/parse`),
}

// 用户故事
export const storyApi = {
  list: (projectId) => api.get('/stories', { params: { project_id: projectId } }),
  generate: (requirementId) => api.post('/stories/generate', { requirement_id: requirementId }),
}

// 任务
export const taskApi = {
  list: (projectId) => api.get('/tasks', { params: { project_id: projectId } }),
  decompose: (storyId) => api.post('/tasks/decompose', { story_id: storyId }),
  estimate: (projectId) => api.post('/tasks/estimate', { project_id: projectId }),
  assign: (projectId) => api.post('/tasks/assign', { project_id: projectId }),
  update: (tid, data) => api.put(`/tasks/${tid}`, data),
}

// 成员
export const memberApi = {
  list: (projectId) => api.get('/members', { params: { project_id: projectId } }),
  create: (data) => api.post('/members', data),
  remove: (id) => api.delete(`/members/${id}`),
}
