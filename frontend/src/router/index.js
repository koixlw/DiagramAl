import { createRouter, createWebHistory } from 'vue-router'
import Workspace from '../views/Workspace.vue'

const routes = [
  {
    path: '/',
    name: 'workspace',
    component: Workspace,
  },
  {
    path: '/flowchart',
    name: 'flowchart',
    component: () => import('../views/Flowchart.vue'),
  },
  {
    path: '/er',
    name: 'er',
    component: () => import('../views/ERDiagram.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/Settings.vue'),
  },
  {
    path: '/docs',
    name: 'docs',
    component: () => import('../views/Docs.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
