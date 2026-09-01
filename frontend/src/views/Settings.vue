<template>
  <div class="bg-background text-on-background font-body-md h-screen flex flex-col overflow-hidden">
    <header class="bg-surface border-b border-outline-variant flex items-center w-full px-gutter h-16 shrink-0">
      <button @click="router.push('/')" class="flex items-center gap-2 text-primary hover:bg-surface-container-low rounded-lg px-3 py-1.5 transition-colors">
        <span class="material-symbols-outlined">arrow_back</span>
        <span class="font-headline-md font-bold">DiagramAI</span>
      </button>
      <span class="font-label-mono text-label-mono text-on-surface-variant ml-4">设置</span>
    </header>

    <div class="flex-1 overflow-auto">
      <div class="max-w-2xl mx-auto p-6 space-y-6">
        <!-- API 配置 -->
        <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">api</span>
            API 配置
          </h2>
          <div class="space-y-4">
            <div>
              <label class="font-code-sm text-code-sm text-on-surface-variant block mb-1">API Key</label>
              <input v-model="apiConfig.key" type="password" class="w-full bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 font-code-sm text-code-sm focus:ring-1 focus:ring-primary focus:border-primary focus:outline-none" placeholder="输入 API Key">
            </div>
            <div>
              <label class="font-code-sm text-code-sm text-on-surface-variant block mb-1">Base URL</label>
              <input v-model="apiConfig.baseUrl" type="text" class="w-full bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 font-code-sm text-code-sm focus:ring-1 focus:ring-primary focus:border-primary focus:outline-none" placeholder="http://127.0.0.1:8000/api">
            </div>
            <div>
              <label class="font-code-sm text-code-sm text-on-surface-variant block mb-1">模型</label>
              <select v-model="apiConfig.model" class="w-full bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 font-code-sm text-code-sm focus:ring-1 focus:ring-primary focus:border-primary focus:outline-none">
                <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
                <option value="claude-opus-4-20250514">Claude Opus 4</option>
                <option value="claude-haiku-4-20250514">Claude Haiku 4</option>
              </select>
            </div>
            <button @click="saveApiConfig" class="bg-primary-container text-on-primary rounded-lg py-2 px-6 font-label-mono text-label-mono hover:opacity-90 transition-opacity">保存配置</button>
            <p v-if="saveMsg" class="text-xs" :class="saveMsg.success ? 'text-emerald-600' : 'text-red-600'">{{ saveMsg.text }}</p>
          </div>
        </div>

        <!-- 清除数据 -->
        <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-secondary">delete_sweep</span>
            数据管理
          </h2>
          <div class="space-y-3">
            <div class="flex items-center justify-between p-3 bg-surface-container-low rounded-lg">
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">ER 图历史</p>
                <p class="font-code-sm text-code-sm text-outline-variant text-xs">{{ erHistoryCount }} 条记录</p>
              </div>
              <button @click="clearHistory('er')" class="text-red-500 hover:text-red-700 text-xs font-label-mono border border-red-200 rounded-lg px-3 py-1.5 hover:bg-red-50 transition-colors">清除</button>
            </div>
            <div class="flex items-center justify-between p-3 bg-surface-container-low rounded-lg">
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">流程图历史</p>
                <p class="font-code-sm text-code-sm text-outline-variant text-xs">{{ fcHistoryCount }} 条记录</p>
              </div>
              <button @click="clearHistory('fc')" class="text-red-500 hover:text-red-700 text-xs font-label-mono border border-red-200 rounded-lg px-3 py-1.5 hover:bg-red-50 transition-colors">清除</button>
            </div>
            <div class="flex items-center justify-between p-3 bg-surface-container-low rounded-lg">
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">所有样式设置</p>
                <p class="font-code-sm text-code-sm text-outline-variant text-xs">恢复默认颜色</p>
              </div>
              <button @click="clearStyles" class="text-red-500 hover:text-red-700 text-xs font-label-mono border border-red-200 rounded-lg px-3 py-1.5 hover:bg-red-50 transition-colors">重置</button>
            </div>
          </div>
        </div>

        <!-- 关于 -->
        <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-secondary">info</span>
            关于
          </h2>
          <div class="space-y-2">
            <p class="font-label-mono text-label-mono text-on-surface">DiagramAI v0.1.0</p>
            <p class="font-code-sm text-code-sm text-on-surface-variant">AI 驱动的智能图表生成工具</p>
            <p class="font-code-sm text-code-sm text-on-surface-variant text-xs">支持自然语言和代码输入，自动生成流程图和 E-R 图</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const apiConfig = ref({
  key: '',
  baseUrl: 'http://127.0.0.1:8000/api',
  model: 'claude-sonnet-4-20250514'
})
const saveMsg = ref(null)

const erHistoryCount = ref(0)
const fcHistoryCount = ref(0)

onMounted(() => {
  // 加载 API 配置
  try {
    const saved = localStorage.getItem('api-config')
    if (saved) apiConfig.value = JSON.parse(saved)
  } catch(e) {}

  // 统计历史数量
  try {
    const erH = localStorage.getItem('er-history')
    erHistoryCount.value = erH ? JSON.parse(erH).length : 0
    const fcH = localStorage.getItem('fc-history')
    fcHistoryCount.value = fcH ? JSON.parse(fcH).length : 0
  } catch(e) {}
})

function saveApiConfig() {
  try {
    localStorage.setItem('api-config', JSON.stringify(apiConfig.value))
    saveMsg.value = { success: true, text: '配置已保存' }
    setTimeout(() => { saveMsg.value = null }, 2000)
  } catch(e) {
    saveMsg.value = { success: false, text: '保存失败' }
  }
}

function clearHistory(type) {
  if (!confirm(`确定清除${type === 'er' ? 'ER 图' : '流程图'}历史？`)) return
  localStorage.removeItem(type === 'er' ? 'er-history' : 'fc-history')
  if (type === 'er') erHistoryCount.value = 0
  else fcHistoryCount.value = 0
}

function clearStyles() {
  if (!confirm('确定重置所有样式为默认？')) return
  localStorage.removeItem('er-colors-v2')
  localStorage.removeItem('fc-colors-v2')
}
</script>
