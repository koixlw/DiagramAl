<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import * as d3 from 'd3'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const entitiesText = ref('')
const relationshipsText = ref('')
const attributesText = ref('')
const loading = ref(false)
const error = ref('')
const svgContent = ref('')
const zoomLevel = ref(100)
const hasDiagram = ref(false)

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
      body: JSON.stringify({
        type: 'er',
        description: prompt,
      }),
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || `请求失败 (${res.status})`)
    }

    const data = await res.json()
    renderERDiagram(data.data)
    hasDiagram.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function buildPrompt() {
  const parts = []
  if (entitiesText.value.trim()) parts.push(`实体：\n${entitiesText.value}`)
  if (relationshipsText.value.trim()) parts.push(`关系：\n${relationshipsText.value}`)
  if (attributesText.value.trim()) parts.push(`属性：\n${attributesText.value}`)
  return parts.join('\n\n') || '学生选课系统：学生有学号、姓名、邮箱；课程有课程号、名称、学分；学生和课程是多对多的选课关系'
}

function renderERDiagram(data) {
  const entities = data.entities || []
  const relationships = data.relationships || []

  // Build nodes and links for force simulation
  const nodes = []
  const links = []

  entities.forEach((e) => {
    nodes.push({
      id: `entity-${e.id}`,
      refId: e.id,
      type: 'entity',
      name: e.name,
      attributes: e.attributes || [],
    })
  })

  relationships.forEach((r) => {
    nodes.push({
      id: `rel-${r.id}`,
      refId: r.id,
      type: 'relationship',
      name: r.name,
      attributes: r.attributes || [],
      fromEntity: r.from_entity,
      toEntity: r.to_entity,
      fromCardinality: r.from_cardinality,
      toCardinality: r.to_cardinality,
    })
    links.push({ source: `entity-${r.from_entity}`, target: `rel-${r.id}` })
    links.push({ source: `entity-${r.to_entity}`, target: `rel-${r.id}` })
  })

  // Create SVG
  const svgW = 800
  const svgH = 600

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

  // Defs
  const defs = svg.append('defs')
  const marker = defs.append('marker')
    .attr('id', 'er-arrow')
    .attr('viewBox', '0 0 10 7')
    .attr('refX', 10)
    .attr('refY', 3.5)
    .attr('markerWidth', 7)
    .attr('markerHeight', 5)
    .attr('orient', 'auto')
  marker.append('path').attr('d', 'M 0 0 L 10 3.5 L 0 7 Z').attr('fill', '#94a3b8')

  // Force simulation
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id((d) => d.id).distance(200))
    .force('charge', d3.forceManyBody().strength(-600))
    .force('center', d3.forceCenter(svgW / 2, svgH / 2))
    .force('collision', d3.forceCollide().radius(80))
    .stop()

  for (let i = 0; i < 300; i++) simulation.tick()

  const g = svg.append('g')

  // Draw links
  links.forEach((link) => {
    const source = nodes.find((n) => n.id === (link.source.id || link.source))
    const target = nodes.find((n) => n.id === (link.target.id || link.source))
    if (!source || !target) return

    g.append('line')
      .attr('x1', source.x)
      .attr('y1', source.y)
      .attr('x2', target.x)
      .attr('y2', target.y)
      .attr('stroke', '#cbd5e1')
      .attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#er-arrow)')
  })

  // Draw cardinality labels
  relationships.forEach((r) => {
    const fromNode = nodes.find((n) => n.refId === r.from_entity && n.type === 'entity')
    const toNode = nodes.find((n) => n.refId === r.to_entity && n.type === 'entity')
    const relNode = nodes.find((n) => n.refId === r.id && n.type === 'relationship')

    if (fromNode && relNode) {
      const mx = (fromNode.x + relNode.x) / 2
      const my = (fromNode.y + relNode.y) / 2 - 12
      g.append('text')
        .attr('x', mx)
        .attr('y', my)
        .attr('text-anchor', 'middle')
        .attr('font-size', 11)
        .attr('font-family', 'JetBrains Mono, monospace')
        .attr('fill', '#22d3ee')
        .attr('font-weight', '600')
        .text(r.from_cardinality || '')
    }

    if (toNode && relNode) {
      const mx = (toNode.x + relNode.x) / 2
      const my = (toNode.y + relNode.y) / 2 - 12
      g.append('text')
        .attr('x', mx)
        .attr('y', my)
        .attr('text-anchor', 'middle')
        .attr('font-size', 11)
        .attr('font-family', 'JetBrains Mono, monospace')
        .attr('fill', '#22d3ee')
        .attr('font-weight', '600')
        .text(r.to_cardinality || '')
    }
  })

  // Draw entity rectangles
  nodes.filter((n) => n.type === 'entity').forEach((node) => {
    const entityH = Math.max(40, 30 + node.attributes.length * 20)
    const entityW = 140

    const gNode = g.append('g')
      .attr('transform', `translate(${node.x}, ${node.y})`)
      .style('cursor', 'pointer')

    // Rectangle
    gNode.append('rect')
      .attr('x', -entityW / 2)
      .attr('y', -entityH / 2)
      .attr('width', entityW)
      .attr('height', entityH)
      .attr('rx', 4)
      .attr('fill', '#eff6ff')
      .attr('stroke', '#3b82f6')
      .attr('stroke-width', 1.5)

    // Separator line
    gNode.append('line')
      .attr('x1', -entityW / 2)
      .attr('y1', -entityH / 2 + 28)
      .attr('x2', entityW / 2)
      .attr('y2', -entityH / 2 + 28)
      .attr('stroke', '#bfdbfe')
      .attr('stroke-width', 1)

    // Entity name
    gNode.append('text')
      .attr('x', 0)
      .attr('y', -entityH / 2 + 18)
      .attr('text-anchor', 'middle')
      .attr('font-size', 13)
      .attr('font-weight', '600')
      .attr('font-family', 'Inter, sans-serif')
      .attr('fill', '#1e40af')
      .text(node.name)

    // Attributes
    node.attributes.forEach((attr, i) => {
      const attrText = gNode.append('text')
        .attr('x', 0)
        .attr('y', -entityH / 2 + 44 + i * 20)
        .attr('text-anchor', 'middle')
        .attr('font-size', 11)
        .attr('font-family', 'JetBrains Mono, monospace')
        .attr('fill', '#64748b')

      if (attr.is_primary_key) {
        attrText.append('tspan')
          .attr('text-decoration', 'underline')
          .attr('dominant-baseline', 'middle')
          .text(attr.name)
      } else {
        attrText.attr('dominant-baseline', 'middle').text(attr.name)
      }
    })

    // Hover effect
    gNode.on('mouseenter', function () {
      d3.select(this).select('rect')
        .transition().duration(150)
        .attr('filter', 'drop-shadow(0 0 6px rgba(59,130,246,0.3))')
    }).on('mouseleave', function () {
      d3.select(this).select('rect')
        .transition().duration(150)
        .attr('filter', null)
    })
  })

  // Draw relationship diamonds
  nodes.filter((n) => n.type === 'relationship').forEach((node) => {
    const w = 100
    const h = 56

    const gNode = g.append('g')
      .attr('transform', `translate(${node.x}, ${node.y})`)
      .style('cursor', 'pointer')

    gNode.append('polygon')
      .attr('points', `0,${-h / 2} ${w / 2},0 0,${h / 2} ${-w / 2},0`)
      .attr('fill', '#fffbeb')
      .attr('stroke', '#f59e0b')
      .attr('stroke-width', 1.5)

    gNode.append('text')
      .attr('x', 0)
      .attr('y', 3)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', 12)
      .attr('font-weight', '500')
      .attr('font-family', 'Inter, sans-serif')
      .attr('fill', '#92400e')
      .text(node.name)

    gNode.on('mouseenter', function () {
      d3.select(this).select('polygon')
        .transition().duration(150)
        .attr('filter', 'drop-shadow(0 0 6px rgba(245,158,11,0.3))')
    }).on('mouseleave', function () {
      d3.select(this).select('polygon')
        .transition().duration(150)
        .attr('filter', null)
    })
  })

  svgContent.value = svg.node().outerHTML
}

function zoomIn() {
  currentZoom = Math.min(currentZoom * 1.2, 3)
  applyZoom()
}

function zoomOut() {
  currentZoom = Math.max(currentZoom / 1.2, 0.3)
  applyZoom()
}

function resetZoom() {
  currentZoom = 1
  applyZoom()
}

function applyZoom() {
  zoomLevel.value = Math.round(currentZoom * 100)
  const svg = document.querySelector('#er-canvas svg')
  if (svg) {
    svg.style.transform = `scale(${currentZoom})`
    svg.style.transformOrigin = 'center top'
  }
}

function downloadSVG() {
  if (!svgContent.value) return
  const blob = new Blob([svgContent.value], { type: 'image/svg+xml' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `er-diagram-${Date.now()}.svg`
  a.click()
  URL.revokeObjectURL(url)
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
      <!-- Sidebar (Left Configuration Panel) -->
      <aside class="w-sidebar_width bg-surface-container-lowest border-r border-outline-variant flex flex-col h-full shrink-0 z-10">
        <div class="p-4 border-b border-outline-variant">
          <h2 class="font-label-mono text-label-mono text-on-surface-variant mb-2">E-R 图配置</h2>
          <p class="font-code-sm text-code-sm text-secondary">定义实体、关系和属性以生成图表。</p>
        </div>
        <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-stack_gap">
          <!-- Entities Input -->
          <div class="flex flex-col gap-2">
            <label class="font-label-mono text-label-mono text-on-surface-variant">实体 (Entities)</label>
            <textarea v-model="entitiesText" class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-24" placeholder="用户&#10;订单&#10;产品"></textarea>
          </div>
          <!-- Relationships Input -->
          <div class="flex flex-col gap-2 mt-2">
            <label class="font-label-mono text-label-mono text-on-surface-variant">关系 (Relationships)</label>
            <textarea v-model="relationshipsText" class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-24" placeholder="用户 [下单 (1:N)] 订单&#10;订单 [包含 (M:N)] 产品"></textarea>
          </div>
          <!-- Attributes Input -->
          <div class="flex flex-col gap-2 mt-2">
            <label class="font-label-mono text-label-mono text-on-surface-variant">属性 (Attributes)</label>
            <textarea v-model="attributesText" class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-32" placeholder="用户: 编号 (PK), 名称, 邮箱&#10;订单: 订单号 (PK), 日期&#10;产品: 产品号 (PK), 价格"></textarea>
          </div>
          <button
            @click="generate"
            :disabled="loading"
            class="mt-4 bg-primary-container text-on-primary rounded-lg py-2 font-label-mono text-label-mono hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
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
        <!-- Error Banner -->
        <div v-if="error" class="absolute top-4 left-1/2 -translate-x-1/2 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg shadow-sm z-30 text-sm max-w-lg">
          <span class="material-symbols-outlined text-sm align-middle mr-1">error</span>
          {{ error }}
          <button @click="error = ''" class="ml-2 text-red-500 hover:text-red-700">&times;</button>
        </div>

        <!-- Floating Toolbar -->
        <div class="absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-surface-container-lowest border border-outline-variant rounded-full px-4 py-2 flex gap-4 shadow-sm z-20">
          <button class="text-secondary hover:text-primary transition-colors flex items-center gap-1" @click="zoomIn" :disabled="!hasDiagram">
            <span class="material-symbols-outlined text-sm">zoom_in</span>
          </button>
          <button class="text-secondary hover:text-primary transition-colors flex items-center gap-1" @click="zoomOut" :disabled="!hasDiagram">
            <span class="material-symbols-outlined text-sm">zoom_out</span>
          </button>
          <div class="w-px bg-outline-variant h-4 my-auto"></div>
          <button class="text-secondary hover:text-primary transition-colors flex items-center gap-1" @click="resetZoom" :disabled="!hasDiagram">
            <span class="material-symbols-outlined text-sm">center_focus_strong</span>
          </button>
        </div>

        <!-- Canvas Content -->
        <div class="flex-1 relative w-full h-full overflow-auto p-8 flex items-center justify-center min-h-[600px] min-w-[800px]">
          <!-- Empty State -->
          <div v-if="!hasDiagram && !loading" class="flex flex-col items-center justify-center text-on-surface-variant">
            <span class="material-symbols-outlined text-6xl text-outline-variant mb-4">database</span>
            <p class="font-label-mono text-label-mono">输入实体和关系后点击「生成图表」</p>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="flex flex-col items-center justify-center text-on-surface-variant">
            <span class="material-symbols-outlined text-4xl animate-spin mb-3">progress_activity</span>
            <p class="font-label-mono text-label-mono">AI 正在生成中...</p>
          </div>

          <!-- ER Diagram SVG -->
          <div id="er-canvas" class="relative"></div>
        </div>
      </main>
    </div>
  </div>
</template>
