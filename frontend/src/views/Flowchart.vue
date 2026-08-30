<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import dagre from 'dagre'
import * as graphlib from 'graphlib'

const Graph = graphlib.Graph
const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const inputText = ref('用户发起请求\n验证用户身份\n如果 验证成功 -> 查询数据库\n    如果 数据存在 -> 返回结果 -> 结束\n    如果 数据不存在 -> 提示错误 -> 结束\n如果 验证失败 -> 拒绝访问 -> 结束')
const loading = ref(false)
const error = ref('')
const hasDiagram = ref(false)
const svgContent = ref('')
const zoomLevel = ref(100)
let currentZoom = 1

// 节点尺寸
const ND = {
  start:     { w: 140, h: 42 },
  end:       { w: 140, h: 42 },
  process:   { w: 160, h: 50 },
  decision:  { w: 150, h: 72 },
  io:        { w: 160, h: 42 },
  connector: { w: 32,  h: 32 },
}

// 颜色
const CL = {
  start:     { fill: '#d1fae5', stroke: '#059669', text: '#064e3b' },
  end:       { fill: '#fee2e2', stroke: '#dc2626', text: '#7f1d1d' },
  process:   { fill: '#dbeafe', stroke: '#2563eb', text: '#1e3a5f' },
  decision:  { fill: '#fef3c7', stroke: '#d97706', text: '#78350f' },
  io:        { fill: '#ede9fe', stroke: '#7c3aed', text: '#4c1d95' },
  connector: { fill: '#f3f4f6', stroke: '#6b7280', text: '#1f2937' },
}

async function generate() {
  if (!inputText.value.trim()) return
  loading.value = true
  error.value = ''
  hasDiagram.value = false
  try {
    const res = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'flowchart', description: inputText.value }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `请求失败 (${res.status})`)
    }
    renderFlowchart((await res.json()).data)
    hasDiagram.value = true
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}

function renderFlowchart(data) {
  const nodes = data.nodes || []
  const edges = data.edges || []

  // Dagre 布局
  const g = new Graph()
  g.setGraph({ rankdir: 'TB', nodesep: 100, ranksep: 80, edgesep: 40, marginx: 100, marginy: 80 })
  g.setDefaultEdgeLabel(() => ({}))

  nodes.forEach(n => {
    const d = ND[n.type] || ND.process
    g.setNode(n.id, { w: d.w, h: d.h, label: n.label, nodeType: n.type })
  })
  edges.forEach(e => {
    const fn = nodes.find(x => x.id === e.from)
    const tn = nodes.find(x => x.id === e.to)
    g.setEdge(e.from, e.to, {
      label: e.label || '',
      ft: fn?.type || 'process',
      tt: tn?.type || 'process',
    })
  })
  dagre.layout(g)

  const gw = g.graph()
  const svgW = Math.max(gw.width + 200, 500)
  const svgH = Math.max(gw.height + 160, 400)

  // 用更深的颜色确保可见性
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}" style="font-family:Inter,sans-serif">`
  svg += '<defs>'
  svg += `<marker id="ah" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="10" markerHeight="7" orient="auto"><path d="M0 0L10 3.5L0 7Z" fill="#64748b"/></marker>`
  svg += `<marker id="aha" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="10" markerHeight="7" orient="auto"><path d="M0 0L10 3.5L0 7Z" fill="#2563eb"/></marker>`
  svg += '</defs>'
  svg += `<g transform="translate(0,0)">`

  // ---- 连线（正交路由） ----
  edges.forEach(edge => {
    const fn = g.node(edge.from)
    const tn = g.node(edge.to)
    if (!fn || !tn) return

    const fd = ND[fn.nodeType] || ND.process
    const td = ND[tn.nodeType] || ND.process
    const active = !!edge.label
    const isDec = fn.nodeType === 'decision' || tn.nodeType === 'decision'

    const sx = fn.x
    const sy = fn.y + fd.h / 2
    const ex = tn.x
    const ey = tn.y - td.h / 2

    let d
    if (isDec && edge.label) {
      // 决策分支：折线
      const offset = edge.label === '否' ? 50 : -50
      const midY = sy + (ey - sy) * 0.35
      d = `M${sx},${sy} L${sx},${midY} L${sx + offset},${midY} L${sx + offset},${ey - 8} L${ex},${ey - 8} L${ex},${ey}`
    } else {
      d = `M${sx},${sy} L${ex},${ey}`
    }

    const sc = active ? '#2563eb' : '#64748b'
    const sw = active ? 2 : 1.5
    const mk = active ? 'url(#aha)' : 'url(#ah)'
    svg += `<path d="${d}" fill="none" stroke="${sc}" stroke-width="${sw}" marker-end="${mk}" stroke-linecap="round" stroke-linejoin="round"/>`

    // 标签
    if (edge.label) {
      let lx, ly
      if (isDec) {
        const offset2 = edge.label === '否' ? 50 : -50
        const midY2 = sy + (ey - sy) * 0.35
        lx = sx + offset2 + (offset2 > 0 ? 8 : -8)
        ly = midY2
      } else {
        lx = (sx + ex) / 2 + 12
        ly = (sy + ey) / 2
      }
      const fc = active ? '#2563eb' : '#475569'
      const fb = active ? '#eff6ff' : '#f8fafc'
      const sb = active ? '#93c5fd' : '#cbd5e1'
      const tw = edge.label.length * 12 + 18
      svg += `<rect x="${lx - tw/2}" y="${ly - 10}" width="${tw}" height="20" rx="4" fill="${fb}" stroke="${sb}" stroke-width="1"/>`
      svg += `<text x="${lx}" y="${ly + 4}" text-anchor="middle" font-size="11" fill="${fc}" font-weight="500">${edge.label}</text>`
    }
  })

  // ---- 节点 ----
  nodes.forEach(node => {
    const n = g.node(node.id)
    if (!n) return
    const c = CL[node.type] || CL.process
    const nd = ND[node.type] || ND.process
    const cx = n.x, cy = n.y

    // 形状
    svg += makeShape(node.type, nd.w, nd.h, cx, cy, c)

    // 文字
    const ty = node.type === 'decision' ? cy + 2 : cy + 3
    svg += `<text x="${cx}" y="${ty}" text-anchor="middle" dominant-baseline="middle" font-size="12.5" fill="${c.text}" font-weight="${node.type === 'decision' ? 600 : 400}">${node.label}</text>`
  })

  svg += '</g></svg>'
  svgContent.value = svg

  const el = document.getElementById('flowchart-canvas')
  if (el) el.innerHTML = svg
}

function makeShape(type, w, h, cx, cy, c) {
  switch (type) {
    case 'start':
    case 'end':
      return `<rect x="${cx - w/2}" y="${cy - h/2}" width="${w}" height="${h}" rx="${h/2}" fill="${c.fill}" stroke="${c.stroke}" stroke-width="2"/>`
    case 'process':
      return `<rect x="${cx - w/2}" y="${cy - h/2}" width="${w}" height="${h}" rx="6" fill="${c.fill}" stroke="${c.stroke}" stroke-width="2"/>`
    case 'decision': {
      const hw = w/2, hh = h/2
      return `<polygon points="${cx},${cy-hh} ${cx+hw},${cy} ${cx},${cy+hh} ${cx-hw},${cy}" fill="${c.fill}" stroke="${c.stroke}" stroke-width="2"/>`
    }
    case 'io': {
      const off = 16
      return `<polygon points="${cx-w/2+off},${cy-h/2} ${cx+w/2},${cy-h/2} ${cx+w/2-off},${cy+h/2} ${cx-w/2},${cy+h/2}" fill="${c.fill}" stroke="${c.stroke}" stroke-width="2"/>`
    }
    case 'connector':
      return `<circle cx="${cx}" cy="${cy}" r="${Math.min(w,h)/2}" fill="${c.fill}" stroke="${c.stroke}" stroke-width="2"/>`
    default:
      return `<rect x="${cx - w/2}" y="${cy - h/2}" width="${w}" height="${h}" rx="6" fill="${c.fill}" stroke="${c.stroke}" stroke-width="2"/>`
  }
}

function zoomIn() { currentZoom = Math.min(currentZoom * 1.2, 3); applyZoom() }
function zoomOut() { currentZoom = Math.max(currentZoom / 1.2, 0.3); applyZoom() }
function resetZoom() { currentZoom = 1; applyZoom() }
function applyZoom() {
  zoomLevel.value = Math.round(currentZoom * 100)
  const svg = document.querySelector('#flowchart-canvas svg')
  if (svg) { svg.style.transform = `scale(${currentZoom})`; svg.style.transformOrigin = 'center top' }
}
function downloadSVG() {
  if (!svgContent.value) return
  const blob = new Blob([svgContent.value], { type: 'image/svg+xml' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
  a.download = `flowchart-${Date.now()}.svg`; a.click()
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
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" @click="downloadSVG" :disabled="!svgContent">
          <span class="material-symbols-outlined">download</span>
        </button>
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors">
          <span class="material-symbols-outlined">share</span>
        </button>
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors">
          <span class="material-symbols-outlined">code</span>
        </button>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden relative">
      <!-- Left Panel -->
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

      <!-- Right Canvas -->
      <main class="flex-1 bg-surface-bright dot-grid relative overflow-hidden flex flex-col">
        <!-- Error -->
        <div v-if="error" class="absolute top-4 left-1/2 -translate-x-1/2 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg shadow-sm z-30 text-sm max-w-lg">
          <span class="material-symbols-outlined text-sm align-middle mr-1">error</span>
          {{ error }}
          <button @click="error = ''" class="ml-2 text-red-500 hover:text-red-700">&times;</button>
        </div>

        <!-- Toolbar -->
        <div class="absolute bottom-6 left-1/2 -translate-x-1/2 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-sm flex items-center gap-1 p-1 z-10">
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" @click="zoomOut" :disabled="!hasDiagram">
            <span class="material-symbols-outlined">remove</span>
          </button>
          <span class="font-label-mono text-label-mono text-on-surface-variant w-12 text-center">{{ zoomLevel }}%</span>
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" @click="zoomIn" :disabled="!hasDiagram">
            <span class="material-symbols-outlined">add</span>
          </button>
          <div class="w-px h-6 bg-outline-variant mx-1"></div>
          <button class="p-2 text-primary hover:bg-surface-container-low rounded transition-colors">
            <span class="material-symbols-outlined">grid_on</span>
          </button>
          <div class="w-px h-6 bg-outline-variant mx-1"></div>
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors flex items-center gap-1 pr-3" @click="resetZoom" :disabled="!hasDiagram">
            <span class="material-symbols-outlined">filter_center_focus</span>
            <span class="font-label-mono text-xs hidden sm:inline">居中</span>
          </button>
        </div>

        <!-- Canvas -->
        <div class="flex-1 relative w-full h-full overflow-auto p-8 flex items-center justify-center min-h-[600px] min-w-[800px]">
          <div v-if="!hasDiagram && !loading" class="flex flex-col items-center justify-center text-on-surface-variant">
            <span class="material-symbols-outlined text-6xl text-outline-variant mb-4">account_tree</span>
            <p class="font-label-mono text-label-mono">输入处理逻辑后点击「生成图表」</p>
          </div>
          <div v-if="loading" class="flex flex-col items-center justify-center text-on-surface-variant">
            <span class="material-symbols-outlined text-4xl animate-spin mb-3">progress_activity</span>
            <p class="font-label-mono text-label-mono">AI 正在生成中...</p>
          </div>
          <div id="flowchart-canvas" class="relative"></div>
        </div>
      </main>
    </div>
  </div>
</template>
