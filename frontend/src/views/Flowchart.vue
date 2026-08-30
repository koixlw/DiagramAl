<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import dagre from 'dagre'

const router = useRouter()
const API_BASE = 'http://127.0.0.1:8000'

const inputText = ref('用户发起请求\n验证用户身份\n如果 验证成功 -> 查询数据库\n    如果 数据存在 -> 返回结果 -> 结束\n    如果 数据不存在 -> 提示错误 -> 结束\n如果 验证失败 -> 拒绝访问 -> 结束')
const loading = ref(false)
const svgContent = ref('')
const error = ref('')
const zoomLevel = ref(100)
const svgContainer = ref(null)

// SVG namespace
const SVG_NS = 'http://www.w3.org/2000/svg'

const nodeDimensions = {
  start: { w: 130, h: 40 },
  end: { w: 130, h: 40 },
  process: { w: 150, h: 48 },
  decision: { w: 140, h: 70 },
  io: { w: 150, h: 40 },
  connector: { w: 30, h: 30 },
}

const nodeTypeColors = {
  start: { fill: '#ecfdf5', stroke: '#10b981', text: '#065f46' },
  end: { fill: '#fef2f2', stroke: '#ef4444', text: '#991b1b' },
  process: { fill: '#eff6ff', stroke: '#3b82f6', text: '#1e40af' },
  decision: { fill: '#fffbeb', stroke: '#f59e0b', text: '#92400e' },
  io: { fill: '#f5f3ff', stroke: '#8b5cf6', text: '#5b21b6' },
  connector: { fill: '#f9fafb', stroke: '#6b7280', text: '#374151' },
}

async function generate() {
  if (!inputText.value.trim()) return
  loading.value = true
  error.value = ''
  svgContent.value = ''

  try {
    const res = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'flowchart',
        description: inputText.value,
      }),
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || `请求失败 (${res.status})`)
    }

    const data = await res.json()
    renderFlowchart(data.data)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function renderFlowchart(data) {
  const nodes = data.nodes || []
  const edges = data.edges || []

  const g = new dagre.graphlib.Graph()
  g.setGraph({ rankdir: 'TB', nodesep: 50, ranksep: 70, marginx: 60, marginy: 60 })
  g.setDefaultEdgeLabel(() => ({}))

  nodes.forEach((node) => {
    const dim = nodeDimensions[node.type] || nodeDimensions.process
    g.setNode(node.id, { ...dim, label: node.label, nodeType: node.type })
  })

  edges.forEach((edge) => {
    g.setEdge(edge.from, edge.to, { label: edge.label || '' })
  })

  dagre.layout(g)

  const graphObj = g.graph()
  const svgW = Math.max(graphObj.width + 120, 600)
  const svgH = Math.max(graphObj.height + 120, 400)

  const svg = document.createElementNS(SVG_NS, 'svg')
  svg.setAttribute('width', svgW)
  svg.setAttribute('height', svgH)
  svg.setAttribute('viewBox', `0 0 ${svgW} ${svgH}`)
  svg.style.width = svgW + 'px'
  svg.style.height = svgH + 'px'

  // Defs
  const defs = document.createElementNS(SVG_NS, 'defs')

  // Arrow marker
  const marker = document.createElementNS(SVG_NS, 'marker')
  marker.setAttribute('id', 'arrowhead')
  marker.setAttribute('viewBox', '0 0 10 7')
  marker.setAttribute('refX', '10')
  marker.setAttribute('refY', '3.5')
  marker.setAttribute('markerWidth', '8')
  marker.setAttribute('markerHeight', '6')
  marker.setAttribute('orient', 'auto')
  const arrowPath = document.createElementNS(SVG_NS, 'path')
  arrowPath.setAttribute('d', 'M 0 0 L 10 3.5 L 0 7 Z')
  arrowPath.setAttribute('fill', '#94a3b8')
  marker.appendChild(arrowPath)
  defs.appendChild(marker)

  // Active arrow marker
  const markerActive = document.createElementNS(SVG_NS, 'marker')
  markerActive.setAttribute('id', 'arrowhead-active')
  markerActive.setAttribute('viewBox', '0 0 10 7')
  markerActive.setAttribute('refX', '10')
  markerActive.setAttribute('refY', '3.5')
  markerActive.setAttribute('markerWidth', '8')
  markerActive.setAttribute('markerHeight', '6')
  markerActive.setAttribute('orient', 'auto')
  const arrowPathActive = document.createElementNS(SVG_NS, 'path')
  arrowPathActive.setAttribute('d', 'M 0 0 L 10 3.5 L 0 7 Z')
  arrowPathActive.setAttribute('fill', '#3b82f6')
  markerActive.appendChild(arrowPathActive)
  defs.appendChild(markerActive)

  svg.appendChild(defs)

  const group = document.createElementNS(SVG_NS, 'g')

  // Draw edges
  edges.forEach((edge) => {
    const fromNode = g.node(edge.from)
    const toNode = g.node(edge.to)
    if (!fromNode || !toNode) return

    const isDecision = fromNode.nodeType === 'decision' || toNode.nodeType === 'decision'
    const isActive = !!edge.label

    const path = document.createElementNS(SVG_NS, 'path')
    const startX = fromNode.x
    const startY = fromNode.y + fromNode.height / 2
    const endX = toNode.x
    const endY = toNode.y - toNode.height / 2

    if (isDecision) {
      // L-shaped path for decision branches
      const midY = (startY + endY) / 2
      path.setAttribute('d', `M${startX},${startY} L${startX},${midY} L${endX},${midY} L${endX},${endY}`)
    } else {
      path.setAttribute('d', `M${startX},${startY} L${endX},${endY}`)
    }

    path.setAttribute('fill', 'none')
    path.setAttribute('stroke', isActive ? '#3b82f6' : '#cbd5e1')
    path.setAttribute('stroke-width', isActive ? '2' : '1.5')
    path.setAttribute('marker-end', isActive ? 'url(#arrowhead-active)' : 'url(#arrowhead)')
    group.appendChild(path)

    // Edge label
    if (edge.label) {
      let labelX, labelY
      if (isDecision) {
        const midY2 = (startY + endY) / 2
        labelX = (startX + endX) / 2 + (edge.label === '否' ? 12 : -12)
        labelY = midY2
      } else {
        labelX = (startX + endX) / 2
        labelY = (startY + endY) / 2
      }

      const labelBg = document.createElementNS(SVG_NS, 'rect')
      const textW = edge.label.length * 12 + 12
      labelBg.setAttribute('x', labelX - textW / 2)
      labelBg.setAttribute('y', labelY - 10)
      labelBg.setAttribute('width', textW)
      labelBg.setAttribute('height', 20)
      labelBg.setAttribute('rx', '4')
      labelBg.setAttribute('fill', isActive ? '#eff6ff' : '#f8fafc')
      labelBg.setAttribute('stroke', isActive ? '#bfdbfe' : '#e2e8f0')
      labelBg.setAttribute('stroke-width', '1')
      group.appendChild(labelBg)

      const text = document.createElementNS(SVG_NS, 'text')
      text.setAttribute('x', labelX)
      text.setAttribute('y', labelY + 4)
      text.setAttribute('text-anchor', 'middle')
      text.setAttribute('font-size', '11')
      text.setAttribute('font-family', 'Inter, sans-serif')
      text.setAttribute('fill', isActive ? '#2563eb' : '#64748b')
      text.setAttribute('font-weight', '500')
      text.textContent = edge.label
      group.appendChild(text)
    }
  })

  // Draw nodes
  nodes.forEach((node) => {
    const n = g.node(node.id)
    if (!n) return

    const colors = nodeTypeColors[node.type] || nodeTypeColors.process
    const gNode = document.createElementNS(SVG_NS, 'g')
    gNode.setAttribute('transform', `translate(${n.x}, ${n.y})`)
    gNode.style.cursor = 'pointer'

    const shape = createShape(node.type, n.width, n.height)
    shape.setAttribute('fill', colors.fill)
    shape.setAttribute('stroke', colors.stroke)
    shape.setAttribute('stroke-width', '1.5')
    gNode.appendChild(shape)

    const text = document.createElementNS(SVG_NS, 'text')
    text.setAttribute('x', 0)
    text.setAttribute('y', node.type === 'decision' ? 2 : 4)
    text.setAttribute('text-anchor', 'middle')
    text.setAttribute('dominant-baseline', 'middle')
    text.setAttribute('font-size', node.type === 'decision' ? '12' : '12')
    text.setAttribute('font-family', 'Inter, sans-serif')
    text.setAttribute('fill', colors.text)
    text.setAttribute('font-weight', node.type === 'decision' ? '500' : '400')
    text.textContent = node.label
    gNode.appendChild(text)

    // Hover effect
    gNode.addEventListener('mouseenter', () => {
      shape.setAttribute('filter', 'drop-shadow(0 0 6px rgba(59,130,246,0.3))')
    })
    gNode.addEventListener('mouseleave', () => {
      shape.removeAttribute('filter')
    })

    group.appendChild(gNode)
  })

  svg.appendChild(group)

  // Replace the canvas content
  const canvasEl = document.getElementById('flowchart-canvas')
  if (canvasEl) {
    canvasEl.innerHTML = ''
    canvasEl.appendChild(svg)
    svgContent.value = svg.outerHTML
  }
}

function createShape(type, w, h) {
  switch (type) {
    case 'start':
    case 'end':
      const r = document.createElementNS(SVG_NS, 'rect')
      r.setAttribute('x', -w / 2)
      r.setAttribute('y', -h / 2)
      r.setAttribute('width', w)
      r.setAttribute('height', h)
      r.setAttribute('rx', h / 2)
      return r
    case 'process':
      const rect = document.createElementNS(SVG_NS, 'rect')
      rect.setAttribute('x', -w / 2)
      rect.setAttribute('y', -h / 2)
      rect.setAttribute('width', w)
      rect.setAttribute('height', h)
      rect.setAttribute('rx', '4')
      return rect
    case 'decision':
      const polygon = document.createElementNS(SVG_NS, 'polygon')
      polygon.setAttribute('points', `0,${-h / 2} ${w / 2},0 0,${h / 2} ${-w / 2},0`)
      return polygon
    case 'io':
      const io = document.createElementNS(SVG_NS, 'polygon')
      io.setAttribute('points', `${-w / 2 + 14},${-h / 2} ${w / 2},${-h / 2} ${w / 2 - 14},${h / 2} ${-w / 2},${h / 2}`)
      return io
    case 'connector':
      const circle = document.createElementNS(SVG_NS, 'circle')
      circle.setAttribute('cx', 0)
      circle.setAttribute('cy', 0)
      circle.setAttribute('r', Math.min(w, h) / 2)
      return circle
    default:
      const d = document.createElementNS(SVG_NS, 'rect')
      d.setAttribute('x', -w / 2)
      d.setAttribute('y', -h / 2)
      d.setAttribute('width', w)
      d.setAttribute('height', h)
      d.setAttribute('rx', '4')
      return d
  }
}
</script>

<template>
  <div class="bg-background text-on-background font-body-md text-body-md h-screen flex flex-col overflow-hidden">
    <!-- TopNavBar -->
    <header class="bg-surface border-b border-outline-variant flex justify-between items-center w-full px-gutter h-16 flex-shrink-0 z-50">
      <div class="flex items-center gap-4">
        <span class="font-headline-md text-headline-md font-bold text-primary cursor-pointer" @click="router.push('/')">DiagramAI</span>
        <nav class="hidden md:flex gap-6 ml-8">
          <a class="text-primary border-b-2 border-primary pb-1 flex items-center gap-2 hover:bg-surface-container-low transition-colors active:scale-95 duration-100 cursor-pointer" @click="router.push('/flowchart')">
            <span class="material-symbols-outlined">account_tree</span> 流程图
          </a>
          <a class="text-secondary pb-1 flex items-center gap-2 hover:bg-surface-container-low transition-colors active:scale-95 duration-100 cursor-pointer" @click="router.push('/er')">
            <span class="material-symbols-outlined">database</span> E-R 图
          </a>
        </nav>
      </div>
      <div class="flex items-center gap-2">
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" title="Download" @click="downloadSVG" :disabled="!svgContent">
          <span class="material-symbols-outlined">download</span>
        </button>
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" title="Share">
          <span class="material-symbols-outlined">share</span>
        </button>
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" title="Code">
          <span class="material-symbols-outlined">code</span>
        </button>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden relative">
      <!-- Left Panel: Configuration -->
      <aside class="w-sidebar_width bg-surface-container-low border-r border-outline-variant flex flex-col z-40 flex-shrink-0 h-full">
        <div class="p-4 flex flex-col gap-4 flex-1 overflow-y-auto">
          <div>
            <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-2">处理逻辑 (Process Logic)</h2>
            <textarea
              v-model="inputText"
              class="w-full h-40 p-3 bg-surface-container-lowest border border-outline-variant rounded focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary font-code-sm text-code-sm resize-none text-on-surface"
              placeholder="在此输入逻辑，例如：&#10;如果支付成功 -> 发送邮件&#10;如果支付失败 -> 提示重试"
            ></textarea>
          </div>
          <button
            @click="generate"
            :disabled="loading || !inputText.trim()"
            class="w-full py-2 bg-primary-container text-on-primary rounded hover:bg-primary transition-colors font-label-mono text-label-mono font-bold flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="material-symbols-outlined animate-spin">progress_activity</span>
            <span v-else class="material-symbols-outlined">auto_awesome</span>
            {{ loading ? '生成中...' : '生成图表' }}
          </button>
          <div class="mt-6 border-t border-outline-variant pt-4">
            <h3 class="font-label-mono text-label-mono font-bold text-on-surface mb-3 flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary">category</span>
              标准形状图例
            </h3>
            <div class="flex flex-col gap-3 font-diagram-text text-diagram-text text-on-surface-variant">
              <div class="flex items-center gap-3">
                <div class="w-10 h-6 border-2 border-outline rounded-full flex items-center justify-center bg-surface-container-lowest"></div>
                <span>开始/结束 (Start/End)</span>
              </div>
              <div class="flex items-center gap-3">
                <div class="w-10 h-6 border-2 border-outline flex items-center justify-center bg-surface-container-lowest"></div>
                <span>处理 (Process)</span>
              </div>
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 border-2 border-outline transform rotate-45 flex items-center justify-center bg-surface-container-lowest ml-1 mr-1"></div>
                <span>判断 (Decision)</span>
              </div>
              <div class="flex items-center gap-3">
                <div class="w-10 h-6 border-2 border-outline transform -skew-x-12 flex items-center justify-center bg-surface-container-lowest ml-1"></div>
                <span>输入/输出 (I/O)</span>
              </div>
              <div class="flex items-center gap-3">
                <div class="w-4 h-4 border-2 border-outline rounded-full bg-surface-container-lowest ml-3 mr-3"></div>
                <span>连接符 (Connector)</span>
              </div>
              <div class="flex items-center gap-3">
                <div class="w-10 h-0 border-b-2 border-outline relative ml-0 mr-0">
                  <div class="absolute right-0 top-1/2 -translate-y-1/2 w-0 h-0 border-t-[4px] border-t-transparent border-l-[6px] border-l-outline border-b-[4px] border-b-transparent"></div>
                </div>
                <span>流程线 (Flow Line)</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Right Canvas: Preview -->
      <main class="flex-1 bg-surface-bright dot-grid relative overflow-hidden flex flex-col">
        <!-- Error Banner -->
        <div v-if="error" class="absolute top-4 left-1/2 -translate-x-1/2 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg shadow-sm z-30 text-sm max-w-lg">
          <span class="material-symbols-outlined text-sm align-middle mr-1">error</span>
          {{ error }}
          <button @click="error = ''" class="ml-2 text-red-500 hover:text-red-700">&times;</button>
        </div>

        <!-- Toolbar -->
        <div class="absolute bottom-6 left-1/2 -translate-x-1/2 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-sm flex items-center gap-1 p-1 z-10">
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" title="Zoom Out" @click="zoomOut" :disabled="!svgContent">
            <span class="material-symbols-outlined">remove</span>
          </button>
          <span class="font-label-mono text-label-mono text-on-surface-variant w-12 text-center">{{ zoomLevel }}%</span>
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" title="Zoom In" @click="zoomIn" :disabled="!svgContent">
            <span class="material-symbols-outlined">add</span>
          </button>
          <div class="w-px h-6 bg-outline-variant mx-1"></div>
          <button class="p-2 text-primary hover:bg-surface-container-low rounded transition-colors" title="Toggle Grid">
            <span class="material-symbols-outlined">grid_on</span>
          </button>
          <div class="w-px h-6 bg-outline-variant mx-1"></div>
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors flex items-center gap-1 pr-3" title="Center View" @click="resetZoom" :disabled="!svgContent">
            <span class="material-symbols-outlined">filter_center_focus</span>
            <span class="font-label-mono text-xs hidden sm:inline">居中</span>
          </button>
        </div>

        <!-- Canvas Area -->
        <div class="flex-1 relative w-full h-full overflow-auto p-8 flex items-center justify-center min-h-[600px] min-w-[800px]">
          <!-- Empty State -->
          <div v-if="!svgContent && !loading" class="flex flex-col items-center justify-center text-on-surface-variant">
            <span class="material-symbols-outlined text-6xl text-outline-variant mb-4">account_tree</span>
            <p class="font-label-mono text-label-mono">输入处理逻辑后点击「生成图表」</p>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="flex flex-col items-center justify-center text-on-surface-variant">
            <span class="material-symbols-outlined text-4xl animate-spin mb-3">progress_activity</span>
            <p class="font-label-mono text-label-mono">AI 正在生成中...</p>
          </div>

          <!-- Flowchart SVG -->
          <div id="flowchart-canvas" class="relative"></div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentZoom: 1,
    }
  },
  methods: {
    zoomIn() {
      this.currentZoom = Math.min(this.currentZoom * 1.2, 3)
      this.applyZoom()
    },
    zoomOut() {
      this.currentZoom = Math.max(this.currentZoom / 1.2, 0.3)
      this.applyZoom()
    },
    resetZoom() {
      this.currentZoom = 1
      this.applyZoom()
    },
    applyZoom() {
      this.zoomLevel = Math.round(this.currentZoom * 100)
      const svg = document.querySelector('#flowchart-canvas svg')
      if (svg) {
        svg.style.transform = `scale(${this.currentZoom})`
        svg.style.transformOrigin = 'center top'
      }
    },
    downloadSVG() {
      if (!this.svgContent) return
      const blob = new Blob([this.svgContent], { type: 'image/svg+xml' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `flowchart-${Date.now()}.svg`
      a.click()
      URL.revokeObjectURL(url)
    },
  },
}
</script>
