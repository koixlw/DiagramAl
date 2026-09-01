<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import * as d3 from 'd3'

const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const inputText = ref('')
const loading = ref(false)
const error = ref('')
const hasDiagram = ref(false)
const svgContent = ref('')
const zoomLevel = ref(100)
let currentZoom = 1

async function generate() {
  if (!inputText.value.trim()) return
  loading.value = true
  error.value = ''
  hasDiagram.value = false

  try {
    const res = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'er', description: inputText.value }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `请求失败 (${res.status})`)
    }
    renderERDiagram((await res.json()).data)
    hasDiagram.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function renderERDiagram(data) {
  const entities = data?.entities || []
  const relationships = data?.relationships || []

  // 用 flatMap 构建所有节点（避开 Vue 编译器对 push() 的 bug）
  const entityParts = entities.flatMap(e => {
    const attrs = (e.attributes || []).map((a, i) => ({
      id: `attr-${e.id}-${i}`,
      type: 'attribute',
      name: a.name,
      isPrimaryKey: a.primary_key || a.is_primary_key || false,
      parentEntity: `e-${e.id}`,
    }))
    return [{ id: `e-${e.id}`, refId: e.id, type: 'entity', name: e.name }, ...attrs]
  })

  const relParts = relationships.flatMap(r => {
    const relId = `r-${r.id}`
    const attrs = (r.attributes || []).map((a, i) => ({
      id: `attr-rel-${r.id}-${i}`,
      type: 'attribute',
      name: a.name,
      isPrimaryKey: a.primary_key || a.is_primary_key || false,
      parentRel: relId,
    }))
    return [{ id: relId, refId: r.id, type: 'relationship', name: r.name, fromEntity: `e-${r.from_entity || r.from}`, toEntity: `e-${r.to_entity || r.to}`, fromCard: r.from_cardinality || r.cardinality?.from || 'N', toCard: r.to_cardinality || r.cardinality?.to || 'M' }, ...attrs]
  })

  const nodes = entityParts.concat(relParts)

  // 用 flatMap + concat 构建所有连线
  const attrLinks = entities.flatMap(e =>
    (e.attributes || []).map((a, i) => ({ source: `e-${e.id}`, target: `attr-${e.id}-${i}` }))
  )
  const relLinks = relationships.flatMap(r => {
    const relId = `r-${r.id}`
    const base = [
      { source: `e-${r.from_entity || r.from}`, target: relId },
      { source: `e-${r.to_entity || r.to}`, target: relId }
    ]
    const attrL = (r.attributes || []).map((a, i) => ({ source: relId, target: `attr-rel-${r.id}-${i}` }))
    return base.concat(attrL)
  })
  const links = attrLinks.concat(relLinks)

  const svgW = 4000, svgH = 3000
  const container = document.getElementById('er-canvas')
  if (!container) return
  container.innerHTML = ''

  const svg = d3.select(container)
    .append('svg')
    .attr('width', svgW)
    .attr('height', svgH)
    .attr('viewBox', `0 0 ${svgW} ${svgH}`)
    .style('width', svgW + 'px')
    .style('height', svgH + 'px')

  // 箭头
  const defs = svg.append('defs')
  defs.append('marker')
    .attr('id', 'er-arrow')
    .attr('viewBox', '0 0 10 7')
    .attr('refX', 10)
    .attr('refY', 3.5)
    .attr('markerWidth', 7)
    .attr('markerHeight', 5)
    .attr('orient', 'auto')
    .append('path').attr('d', 'M0 0L10 3.5L0 7Z').attr('fill', '#94a3b8')

  // 力导向布局
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(200))
    .force('charge', d3.forceManyBody().strength(-600))
    .force('center', d3.forceCenter(svgW / 2, svgH / 2))
    .force('collision', d3.forceCollide().radius(80))
  sim.stop()
  for (let i = 0; i < 300; i++) sim.tick()

  const g = svg.append('g')

  // 连线
  links.forEach(link => {
    const src = nodes.find(n => n.id === (link.source.id || link.source))
    const tgt = nodes.find(n => n.id === (link.target.id || link.target))
    if (!src || !tgt) return
    g.append('line')
      .attr('x1', src.x).attr('y1', src.y)
      .attr('x2', tgt.x).attr('y2', tgt.y)
      .attr('stroke', '#94a3b8').attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#er-arrow)')
  })

  // 基数标注
  relationships.forEach(r => {
    const fn = nodes.find(n => n.refId === (r.from_entity || r.from) && n.type === 'entity')
    const tn = nodes.find(n => n.refId === (r.to_entity || r.to) && n.type === 'entity')
    const rn = nodes.find(n => n.refId === r.id && n.type === 'relationship')
    const fromCard = r.from_cardinality || r.cardinality?.from || 'N'
    const toCard = r.to_cardinality || r.cardinality?.to || 'M'

    if (fn && rn) {
      const mx = (fn.x + rn.x) / 2, my = (fn.y + rn.y) / 2 - 14
      g.append('text').attr('x', mx).attr('y', my)
        .attr('text-anchor', 'middle').attr('font-size', 12)
        .attr('font-family', 'JetBrains Mono,monospace').attr('fill', '#0891b2')
        .attr('font-weight', '600').text(fromCard)
    }
    if (tn && rn) {
      const mx = (tn.x + rn.x) / 2, my = (tn.y + rn.y) / 2 - 14
      g.append('text').attr('x', mx).attr('y', my)
        .attr('text-anchor', 'middle').attr('font-size', 12)
        .attr('font-family', 'JetBrains Mono,monospace').attr('fill', '#0891b2')
        .attr('font-weight', '600').text(toCard)
    }
  })

  // 实体矩形
  nodes.filter(n => n.type === 'entity').forEach(node => {
    const ew = 120, eh = 44
    const gNode = g.append('g').attr('transform', `translate(${node.x}, ${node.y})`)

    gNode.append('rect')
      .attr('x', -ew/2).attr('y', -eh/2).attr('width', ew).attr('height', eh).attr('rx', 4)
      .attr('fill', '#dbeafe').attr('stroke', '#2563eb').attr('stroke-width', 2)

    gNode.append('text')
      .attr('x', 0).attr('y', 4)
      .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
      .attr('font-size', 13).attr('font-weight', '600')
      .attr('font-family', 'Inter,sans-serif').attr('fill', '#1e40af')
      .text(node.name)
  })

  // 属性椭圆
  nodes.filter(n => n.type === 'attribute').forEach(node => {
    const aw = Math.max(50, node.name.length * 14 + 20), ah = 28
    const gNode = g.append('g').attr('transform', `translate(${node.x}, ${node.y})`)

    gNode.append('ellipse')
      .attr('cx', 0).attr('cy', 0).attr('rx', aw/2).attr('ry', ah/2)
      .attr('fill', '#f0fdf4').attr('stroke', '#16a34a').attr('stroke-width', node.isPrimaryKey ? 2.5 : 1.5)

    const txt = gNode.append('text')
      .attr('x', 0).attr('y', 3)
      .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
      .attr('font-size', 11).attr('font-family', 'JetBrains Mono,monospace')
      .attr('fill', node.isPrimaryKey ? '#166534' : '#4b5563')
    if (node.isPrimaryKey) {
      txt.append('tspan').attr('text-decoration', 'underline').text(node.name)
    } else {
      txt.text(node.name)
    }
  })

  // 关系菱形
  nodes.filter(n => n.type === 'relationship').forEach(node => {
    const rw = 100, rh = 56
    const gNode = g.append('g').attr('transform', `translate(${node.x}, ${node.y})`)

    gNode.append('polygon')
      .attr('points', `0,${-rh/2} ${rw/2},0 0,${rh/2} ${-rw/2},0`)
      .attr('fill', '#fef3c7').attr('stroke', '#d97706').attr('stroke-width', 2)

    gNode.append('text')
      .attr('x', 0).attr('y', 3)
      .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
      .attr('font-size', 12).attr('font-weight', '500')
      .attr('font-family', 'Inter,sans-serif').attr('fill', '#78350f')
      .text(node.name)
  })

  svgContent.value = svg.node().outerHTML
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
      <aside class="w-sidebar_width bg-surface-container-lowest border-r border-outline-variant flex flex-col h-full shrink-0 z-10">
        <div class="p-4 border-b border-outline-variant">
          <h2 class="font-label-mono text-label-mono text-on-surface-variant mb-2">E-R 图描述</h2>
          <p class="font-code-sm text-code-sm text-secondary">用自然语言描述实体、关系和属性</p>
        </div>
        <div class="flex-1 overflow-y-auto p-4">
          <div class="flex flex-col gap-2">
            <label class="font-label-mono text-label-mono text-on-surface-variant">描述</label>
            <textarea v-model="inputText" class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-48" placeholder="学生选课系统：学生有学号、姓名、邮箱、入学日期；课程有课程号、名称、学分；学生和课程是多对多的选课关系，包含选课日期和成绩"></textarea>
          </div>
          <button @click="generate" :disabled="loading || !inputText.trim()" class="mt-4 w-full bg-primary-container text-on-primary rounded-lg py-2 font-label-mono text-label-mono hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
            <span v-if="loading" class="material-symbols-outlined animate-spin text-sm">progress_activity</span>
            <span v-else class="material-symbols-outlined text-sm">auto_awesome</span>
            {{ loading ? '生成中...' : '生成图表' }}
          </button>
        </div>
        <div class="p-4 border-t border-outline-variant bg-surface-container">
          <h3 class="font-label-mono text-label-mono text-on-surface-variant mb-3">图例</h3>
          <div class="flex flex-col gap-2">
            <div class="flex items-center gap-3">
              <div class="w-8 h-5 border-2 border-outline bg-surface-container-lowest flex items-center justify-center">
                <span class="font-code-sm text-[10px] text-secondary">实体</span>
              </div>
              <span class="font-code-sm text-code-sm text-on-surface-variant">实体 (矩形)</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-6 h-6 border-2 border-outline bg-surface-container-lowest rotate-45 transform origin-center translate-x-1"></div>
              <span class="font-code-sm text-code-sm text-on-surface-variant ml-2">关系 (菱形)</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-8 h-5 border border-outline bg-surface-container-lowest rounded-full"></div>
              <span class="font-code-sm text-code-sm text-on-surface-variant">属性 (椭圆)</span>
            </div>
            <div class="flex items-center gap-3 mt-1">
              <span class="font-code-sm text-code-sm text-on-surface underline"><u>学号</u></span>
              <span class="font-code-sm text-code-sm text-on-surface-variant">主键 (下划线)</span>
            </div>
          </div>
        </div>
      </aside>

      <main class="flex-1 dot-grid bg-surface-bright relative overflow-hidden flex flex-col">
        <div v-if="error" class="absolute top-4 left-1/2 -translate-x-1/2 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg shadow-sm z-30 text-sm max-w-lg">
          <span class="material-symbols-outlined text-sm align-middle mr-1">error</span> {{ error }}
          <button @click="error = ''" class="ml-2 text-red-500 hover:text-red-700">&times;</button>
        </div>

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

        <div class="flex-1 relative w-full h-full overflow-auto p-8 flex items-center justify-center min-h-[600px] min-w-[800px]">
          <div v-if="!hasDiagram && !loading" class="flex flex-col items-center justify-center text-on-surface-variant">
            <span class="material-symbols-outlined text-6xl text-outline-variant mb-4">database</span>
            <p class="font-label-mono text-label-mono">输入描述后点击「生成图表」</p>
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
