<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import * as d3 from 'd3'

const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const entitiesText = ref('')
const relationshipsText = ref('')
const attributesText = ref('')
const loading = ref(false)
const error = ref('')
const svgContent = ref('')
const hasDiagram = ref(false)
const zoomLevel = ref(100)
let currentZoom = 1

async function generate() {
  const prompt = buildPrompt()
  if (!prompt.trim()) return
  loading.value = true
  error.value = ''
  hasDiagram.value = false

  try {
    const res = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'er', description: prompt }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `请求失败 (${res.status})`)
    }
    const data = await res.json()
    renderER(data.data)
    hasDiagram.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function buildPrompt() {
  const p = []
  if (entitiesText.value.trim()) p.push(`实体：\n${entitiesText.value}`)
  if (relationshipsText.value.trim()) p.push(`关系：\n${relationshipsText.value}`)
  if (attributesText.value.trim()) p.push(`属性：\n${attributesText.value}`)
  return p.join('\n\n') || '学生选课系统：学生有学号、姓名、邮箱；课程有课程号、名称、学分；学生和课程是多对多的选课关系'
}

function renderER(data) {
  const entities = data.entities || []
  const relationships = data.relationships || []

  const nodes = []
  const links = []

  entities.forEach(e => {
    nodes.push({ id: `e-${e.id}`, refId: e.id, type: 'entity', name: e.name, attributes: e.attributes || [] })
  })
  relationships.forEach(r => {
    nodes.push({ id: `r-${r.id}`, refId: r.id, type: 'rel', name: r.name, attributes: r.attributes || [], fromEntity: r.from_entity, toEntity: r.to_entity, fromCard: r.from_cardinality, toCard: r.to_cardinality })
    links.push({ source: `e-${r.from_entity}`, target: `r-${r.id}` })
    links.push({ source: `e-${r.to_entity}`, target: `r-${r.id}` })
  })

  const svgW = 800, svgH = 600
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(200))
    .force('charge', d3.forceManyBody().strength(-600))
    .force('center', d3.forceCenter(svgW / 2, svgH / 2))
    .force('collision', d3.forceCollide().radius(80))
  sim.stop()
  for (let i = 0; i < 300; i++) sim.tick()

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}">`
  svg += `<defs><marker id="ea" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="7" markerHeight="5" orient="auto"><path d="M0 0L10 3.5L0 7Z" fill="#94a3b8"/></marker></defs>`

  // Links
  links.forEach(link => {
    const src = nodes.find(n => n.id === (link.source.id || link.source))
    const tgt = nodes.find(n => n.id === (link.target.id || link.target))
    if (src && tgt) {
      svg += `<line x1="${src.x}" y1="${src.y}" x2="${tgt.x}" y2="${tgt.y}" stroke="#cbd5e1" stroke-width="1.5" marker-end="url(#ea)"/>`
    }
  })

  // Cardinality
  relationships.forEach(r => {
    const fn = nodes.find(n => n.refId === r.from_entity && n.type === 'entity')
    const tn = nodes.find(n => n.refId === r.to_entity && n.type === 'entity')
    const rn = nodes.find(n => n.refId === r.id && n.type === 'rel')
    if (fn && rn) {
      const mx = (fn.x + rn.x) / 2, my = (fn.y + rn.y) / 2 - 14
      svg += `<text x="${mx}" y="${my}" text-anchor="middle" font-size="12" font-family="JetBrains Mono,monospace" fill="#0891b2" font-weight="600">${r.from_cardinality || ''}</text>`
    }
    if (tn && rn) {
      const mx = (tn.x + rn.x) / 2, my = (tn.y + rn.y) / 2 - 14
      svg += `<text x="${mx}" y="${my}" text-anchor="middle" font-size="12" font-family="JetBrains Mono,monospace" fill="#0891b2" font-weight="600">${r.to_cardinality || ''}</text>`
    }
  })

  // Entity rects
  nodes.filter(n => n.type === 'entity').forEach(node => {
    const eh = Math.max(40, 30 + node.attributes.length * 20)
    const ew = 140
    const ex = node.x, ey = node.y
    svg += `<rect x="${ex - ew/2}" y="${ey - eh/2}" width="${ew}" height="${eh}" rx="4" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>`
    svg += `<line x1="${ex - ew/2}" y1="${ey - eh/2 + 28}" x2="${ex + ew/2}" y2="${ey - eh/2 + 28}" stroke="#bfdbfe" stroke-width="1"/>`
    svg += `<text x="${ex}" y="${ey - eh/2 + 18}" text-anchor="middle" font-size="13" font-weight="600" font-family="Inter,sans-serif" fill="#1e40af">${node.name}</text>`
    node.attributes.forEach((a, i) => {
      const ay = ey - eh/2 + 44 + i * 20
      if (a.is_primary_key) {
        svg += `<text x="${ex}" y="${ay}" text-anchor="middle" dominant-baseline="middle" font-size="11" font-family="JetBrains Mono,monospace" fill="#64748b"><tspan text-decoration="underline">${a.name}</tspan></text>`
      } else {
        svg += `<text x="${ex}" y="${ay}" text-anchor="middle" dominant-baseline="middle" font-size="11" font-family="JetBrains Mono,monospace" fill="#64748b">${a.name}</text>`
      }
    })
  })

  // Relationship diamonds
  nodes.filter(n => n.type === 'rel').forEach(node => {
    const rw = 100, rh = 56
    const rx = node.x, ry = node.y
    svg += `<polygon points="${rx},${ry-rh/2} ${rx+rw/2},${ry} ${rx},${ry+rh/2} ${rx-rw/2},${ry}" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>`
    svg += `<text x="${rx}" y="${ry + 3}" text-anchor="middle" dominant-baseline="middle" font-size="12" font-weight="500" font-family="Inter,sans-serif" fill="#78350f">${node.name}</text>`
  })

  svg += '</svg>'
  svgContent.value = svg

  const el = document.getElementById('er-canvas')
  if (el) el.innerHTML = svg
}

function zoomIn() { currentZoom = Math.min(currentZoom * 1.2, 3); applyZoom() }
function zoomOut() { currentZoom = Math.max(currentZoom / 1.2, 0.3); applyZoom() }
function resetZoom() { currentZoom = 1; applyZoom() }
function applyZoom() {
  zoomLevel.value = Math.round(currentZoom * 100)
  const svg = document.querySelector('#er-canvas svg')
  if (svg) { svg.style.transform = `scale(${currentZoom})`; svg.style.transformOrigin = 'center top' }
}
function downloadSVG() {
  if (!svgContent.value) return
  const blob = new Blob([svgContent.value], { type: 'image/svg+xml' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
  a.download = `er-diagram-${Date.now()}.svg`; a.click()
}
</script>

<template>
  <div class="bg-background text-on-background h-screen flex flex-col overflow-hidden font-body-md">
    <!-- TopNavBar -->
    <header class="bg-surface flex justify-between items-center w-full px-gutter h-16 border-b border-outline-variant shrink-0 relative z-10">
      <div class="flex items-center gap-4">
        <span class="font-headline-md text-headline-md font-bold text-primary cursor-pointer" @click="router.push('/')">DiagramAI</span>
        <nav class="hidden md:flex gap-6 ml-8">
          <a class="text-secondary font-label-mono text-label-mono hover:bg-surface-container-low transition-colors px-2 py-1 rounded cursor-pointer" @click="router.push('/flowchart')">流程图</a>
          <a class="text-primary font-label-mono text-label-mono border-b-2 border-primary hover:bg-surface-container-low transition-colors px-2 py-1 active:scale-95 duration-100 cursor-pointer">E-R 图</a>
        </nav>
      </div>
      <div class="flex items-center gap-4">
        <button class="text-primary hover:bg-surface-container-low transition-colors p-2 rounded-full" @click="downloadSVG" :disabled="!svgContent">
          <span class="material-symbols-outlined">download</span>
        </button>
        <button class="text-primary hover:bg-surface-container-low transition-colors p-2 rounded-full">
          <span class="material-symbols-outlined">share</span>
        </button>
        <button class="text-primary hover:bg-surface-container-low transition-colors p-2 rounded-full">
          <span class="material-symbols-outlined">code</span>
        </button>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden relative">
      <!-- Sidebar -->
      <aside class="w-sidebar_width bg-surface-container-lowest border-r border-outline-variant flex flex-col h-full shrink-0 z-10">
        <div class="p-4 border-b border-outline-variant">
          <h2 class="font-label-mono text-label-mono text-on-surface-variant mb-2">E-R 图配置</h2>
          <p class="font-code-sm text-code-sm text-secondary">定义实体、关系和属性以生成图表。</p>
        </div>
        <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-stack_gap">
          <div class="flex flex-col gap-2">
            <label class="font-label-mono text-label-mono text-on-surface-variant">实体 (Entities)</label>
            <textarea v-model="entitiesText" class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-24" placeholder="用户&#10;订单&#10;产品"></textarea>
          </div>
          <div class="flex flex-col gap-2 mt-2">
            <label class="font-label-mono text-label-mono text-on-surface-variant">关系 (Relationships)</label>
            <textarea v-model="relationshipsText" class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-24" placeholder="用户 [下单 (1:N)] 订单&#10;订单 [包含 (M:N)] 产品"></textarea>
          </div>
          <div class="flex flex-col gap-2 mt-2">
            <label class="font-label-mono text-label-mono text-on-surface-variant">属性 (Attributes)</label>
            <textarea v-model="attributesText" class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-32" placeholder="用户: 编号 (PK), 名称, 邮箱&#10;订单: 订单号 (PK), 日期&#10;产品: 产品号 (PK), 价格"></textarea>
          </div>
          <button @click="generate" :disabled="loading" class="mt-4 bg-primary-container text-on-primary rounded-lg py-2 font-label-mono text-label-mono hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
            <span v-if="loading" class="material-symbols-outlined animate-spin text-sm">progress_activity</span>
            <span v-else class="material-symbols-outlined text-sm">auto_awesome</span>
            {{ loading ? '生成中...' : '生成图表' }}
          </button>
        </div>
        <!-- Legend -->
        <div class="p-4 border-t border-outline-variant bg-surface-container">
          <h3 class="font-label-mono text-label-mono text-on-surface-variant mb-3">图例 (Legend)</h3>
          <div class="flex flex-col gap-2">
            <div class="flex items-center gap-3">
              <div class="w-8 h-5 border border-outline bg-surface-container-lowest flex items-center justify-center">
                <span class="font-code-sm text-code-sm text-secondary text-[10px]">实体</span>
              </div>
              <span class="font-code-sm text-code-sm text-on-surface-variant">实体 (Entity)</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-6 h-6 border border-outline bg-surface-container-lowest rotate-45 transform origin-center translate-x-1"></div>
              <span class="font-code-sm text-code-sm text-on-surface-variant ml-2">关系 (Relationship)</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-8 h-5 border border-outline bg-surface-container-lowest rounded-full"></div>
              <span class="font-code-sm text-code-sm text-on-surface-variant">属性 (Attribute)</span>
            </div>
            <div class="flex items-center gap-3 mt-1">
              <span class="font-code-sm text-code-sm text-on-surface underline"><u>编号</u></span>
              <span class="font-code-sm text-code-sm text-on-surface-variant">主键 (Primary Key)</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Canvas -->
      <main class="flex-1 dot-grid bg-surface-bright relative overflow-hidden flex flex-col">
        <div v-if="error" class="absolute top-4 left-1/2 -translate-x-1/2 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg shadow-sm z-30 text-sm max-w-lg">
          <span class="material-symbols-outlined text-sm align-middle mr-1">error</span> {{ error }}
          <button @click="error = ''" class="ml-2 text-red-500 hover:text-red-700">&times;</button>
        </div>

        <!-- Toolbar -->
        <div class="absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-surface-container-lowest border border-outline-variant rounded-full px-4 py-2 flex gap-4 shadow-sm z-20">
          <button class="text-secondary hover:text-primary transition-colors" @click="zoomIn" :disabled="!hasDiagram">
            <span class="material-symbols-outlined text-sm">zoom_in</span>
          </button>
          <button class="text-secondary hover:text-primary transition-colors" @click="zoomOut" :disabled="!hasDiagram">
            <span class="material-symbols-outlined text-sm">zoom_out</span>
          </button>
          <div class="w-px bg-outline-variant h-4 my-auto"></div>
          <button class="text-secondary hover:text-primary transition-colors" @click="resetZoom" :disabled="!hasDiagram">
            <span class="material-symbols-outlined text-sm">center_focus_strong</span>
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 relative w-full h-full overflow-auto p-8 flex items-center justify-center min-h-[600px] min-w-[800px]">
          <div v-if="!hasDiagram && !loading" class="flex flex-col items-center justify-center text-on-surface-variant">
            <span class="material-symbols-outlined text-6xl text-outline-variant mb-4">database</span>
            <p class="font-label-mono text-label-mono">输入实体和关系后点击「生成图表」</p>
          </div>
          <div v-if="loading" class="flex flex-col items-center justify-center text-on-surface-variant">
            <span class="material-symbols-outlined text-4xl animate-spin mb-3">progress_activity</span>
            <p class="font-label-mono text-label-mono">AI 正在生成中...</p>
          </div>
          <div id="er-canvas" class="relative"></div>
        </div>
      </main>
    </div>
  </div>
</template>
