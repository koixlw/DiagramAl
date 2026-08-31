<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

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
  start:     { w: 150, h: 46 },
  end:       { w: 150, h: 46 },
  process:   { w: 170, h: 54 },
  decision:  { w: 160, h: 76 },
  io:        { w: 170, h: 46 },
  connector: { w: 34,  h: 34 },
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

/**
 * 改进的分层布局算法
 * 1. BFS 拓扑排序，区分前向边和回边
 * 2. 决策节点按分支方向分配到不同列
 * 3. 回边绕右侧绘制
 * 4. 同层节点水平均匀分布，间距充足
 */
function computeLayout(nodes, edges) {
  const nodeMap = {}
  nodes.forEach(n => {
    nodeMap[n.id] = { ...n, rank: 0, x: 0, y: 0, children: [], parents: [], incomingEdges: [] }
  })

  // 构建图，记录边信息
  const edgeList = []
  edges.forEach(e => {
    if (nodeMap[e.from] && nodeMap[e.to]) {
      nodeMap[e.from].children.push(e.to)
      nodeMap[e.to].parents.push(e.from)
      nodeMap[e.to].incomingEdges.push(e.from)
      edgeList.push(e)
    }
  })

  // BFS 分配层级（最长路径）
  const rootIds = Object.values(nodeMap).filter(n => n.parents.length === 0).map(n => n.id)
  const queue = [...rootIds]
  const visited = new Set()
  while (queue.length > 0) {
    const id = queue.shift()
    if (visited.has(id)) continue
    visited.add(id)
    const node = nodeMap[id]
    node.children.forEach(cid => {
      if (nodeMap[cid]) {
        nodeMap[cid].rank = Math.max(nodeMap[cid].rank, node.rank + 1)
        queue.push(cid)
      }
    })
  }

  // 识别回边（从高rank到低rank的边）
  const backEdges = new Set()
  edgeList.forEach(e => {
    if (nodeMap[e.to].rank <= nodeMap[e.from].rank) {
      backEdges.add(`${e.from}->${e.to}`)
    }
  })

  // 决策节点优化：让"否"分支的节点向右偏移
  edgeList.forEach(e => {
    const from = nodeMap[e.from]
    const to = nodeMap[e.to]
    if (from && to && from.type === 'decision' && e.label === '否') {
      // "否"分支的目标节点 rank 保持不变，但后面布局时会向右偏移
      to._branchOffset = 1
    } else if (from && to && from.type === 'decision' && e.label === '是') {
      to._branchOffset = -1
    }
  })

  // 收集每层的节点
  const rankMap = {}
  Object.values(nodeMap).forEach(n => {
    const r = n.rank
    if (!rankMap[r]) rankMap[r] = []
    rankMap[r].push(n.id)
  })

  const maxRank = Math.max(...Object.keys(rankMap).map(Number))

  // 间距参数（加大）
  const NODE_GAP = 200
  const RANK_GAP = 140
  const MARGIN_X = 140
  const MARGIN_Y = 80

  // 计算每层总宽度
  const rankWidths = {}
  Object.keys(rankMap).forEach(r => {
    const ids = rankMap[r]
    let total = 0
    ids.forEach((id, i) => {
      const w = ND[nodeMap[id].type]?.w || ND.process.w
      total += w
      if (i > 0) total += NODE_GAP
    })
    rankWidths[r] = total
  })

  // 画布宽度：取最大层宽 + 边距，回边需要额外右侧空间
  const maxLayerW = Math.max(...Object.values(rankWidths), 400)
  const backEdgeSpace = backEdges.size > 0 ? 200 : 0
  const canvasW = maxLayerW + MARGIN_X * 2 + backEdgeSpace

  // 分配位置
  Object.keys(rankMap).forEach(r => {
    const ids = rankMap[r]
    const totalW = ids.reduce((s, id, i) => {
      const w = ND[nodeMap[id].type]?.w || ND.process.w
      return s + w + (i > 0 ? NODE_GAP : 0)
    }, 0)
    const startX = (canvasW - totalW) / 2
    let cx = startX
    ids.forEach(id => {
      const w = ND[nodeMap[id].type]?.w || ND.process.w
      // 决策分支偏移
      const offset = (nodeMap[id]._branchOffset || 0) * 80
      nodeMap[id].x = cx + w / 2 + offset
      nodeMap[id].y = parseInt(r) * RANK_GAP + MARGIN_Y
      cx += w + NODE_GAP
    })
  })

  const canvasH = (maxRank + 1) * RANK_GAP + MARGIN_Y * 2

  return { nodeMap, canvasW, canvasH, backEdges, edgeList }
}

function renderFlowchart(data) {
  const nodes = (data?.nodes || []).filter(n => n && n.id)
  const edges = (data?.edges || []).filter(e => e && e.from && e.to)

  if (nodes.length === 0) {
    error.value = 'AI 返回了空数据，请换一种描述重试'
    return
  }

  const { nodeMap, canvasW, canvasH, backEdges, edgeList } = computeLayout(nodes, edges)

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${canvasW}" height="${canvasH}" viewBox="0 0 ${canvasW} ${canvasH}" style="font-family:Inter,sans-serif">`
  svg += '<defs>'
  svg += `<marker id="ah" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="10" markerHeight="7" orient="auto"><path d="M0 0L10 3.5L0 7Z" fill="#64748b"/></marker>`
  svg += `<marker id="aha" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="10" markerHeight="7" orient="auto"><path d="M0 0L10 3.5L0 7Z" fill="#2563eb"/></marker>`
  svg += '</defs>'
  svg += '<g>'

  // ---- 连线 ----
  edges.forEach(edge => {
    const fn = nodeMap[edge.from]
    const tn = nodeMap[edge.to]
    if (!fn || !tn) return

    const fd = ND[fn.type] || ND.process
    const td = ND[tn.type] || ND.process
    const active = !!edge.label
    const isBackEdge = backEdges.has(`${edge.from}->${edge.to}`)
    const sc = active ? '#2563eb' : '#64748b'
    const sw = active ? 2 : 1.5
    const mk = active ? 'url(#aha)' : 'url(#ah)'

    const sx = fn.x
    const sy = fn.y + fd.h / 2
    const ex = tn.x
    const ey = tn.y - td.h / 2

    let d, lx, ly

    if (fn.type === 'decision' && edge.label) {
      // 决策分支：从菱形左/右角出发
      const side = edge.label === '否' ? 1 : -1
      const hw = fd.w / 2, hh = fd.h / 2
      const startX = fn.x + side * hw * 0.55
      const startY = fn.y + side * hh * 0.55
      const midY = sy + (ey - sy) * 0.5
      d = `M${sx},${sy} L${startX},${startY} L${startX},${midY} L${ex},${midY} L${ex},${ey}`
      lx = (startX + ex) / 2 + side * 20
      ly = midY

    } else if (isBackEdge) {
      // 回边：从源节点底部→右→下→左→目标节点顶部
      const rightX = canvasW - 60
      d = `M${sx},${sy} L${rightX},${sy} L${rightX},${ey} L${ex},${ey}`
      lx = rightX + 16
      ly = (sy + ey) / 2

    } else if (Math.abs(sx - ex) < 2) {
      // 垂直直连
      d = `M${sx},${sy} L${ex},${ey}`
      lx = sx + 18
      ly = (sy + ey) / 2

    } else {
      // 普通折线
      const midY = sy + (ey - sy) * 0.5
      d = `M${sx},${sy} L${sx},${midY} L${ex},${midY} L${ex},${ey}`
      lx = Math.max(sx, ex) + 18
      ly = midY
    }

    svg += `<path d="${d}" fill="none" stroke="${sc}" stroke-width="${sw}" marker-end="${mk}" stroke-linecap="round" stroke-linejoin="round"/>`

    if (edge.label) {
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
    const n = nodeMap[node.id]
    if (!n) return
    const c = CL[node.type] || CL.process
    const nd = ND[node.type] || ND.process

    svg += makeShape(node.type, nd.w, nd.h, n.x, n.y, c)

    const ty = node.type === 'decision' ? n.y + 2 : n.y + 3
    svg += `<text x="${n.x}" y="${ty}" text-anchor="middle" dominant-baseline="middle" font-size="12.5" fill="${c.text}" font-weight="${node.type === 'decision' ? 600 : 400}">${node.label}</text>`
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
      <aside class="w-sidebar_width bg-surface-container-low border-r border-outline-variant flex flex-col z-40 flex-shrink-0 h-full">
        <div class="p-4 flex flex-col gap-4 flex-1 overflow-y-auto">
          <div>
            <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-2">处理逻辑 (Process Logic)</h2>
            <textarea v-model="inputText" class="w-full h-40 p-3 bg-surface-container-lowest border border-outline-variant rounded focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary font-code-sm text-code-sm resize-none text-on-surface" placeholder="在此输入逻辑，例如：&#10;如果支付成功 -> 发送邮件&#10;如果支付失败 -> 提示重试"></textarea>
          </div>
          <button @click="generate" :disabled="loading || !inputText.trim()" class="w-full py-2 bg-primary-container text-on-primary rounded hover:bg-primary transition-colors font-label-mono text-label-mono font-bold flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">
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
              <div class="flex items-center gap-3"><div class="w-10 h-6 border-2 border-outline rounded-full flex items-center justify-center bg-surface-container-lowest"></div><span>开始/结束 (Start/End)</span></div>
              <div class="flex items-center gap-3"><div class="w-10 h-6 border-2 border-outline flex items-center justify-center bg-surface-container-lowest"></div><span>处理 (Process)</span></div>
              <div class="flex items-center gap-3"><div class="w-8 h-8 border-2 border-outline transform rotate-45 flex items-center justify-center bg-surface-container-lowest ml-1 mr-1"></div><span>判断 (Decision)</span></div>
              <div class="flex items-center gap-3"><div class="w-10 h-6 border-2 border-outline transform -skew-x-12 flex items-center justify-center bg-surface-container-lowest ml-1"></div><span>输入/输出 (I/O)</span></div>
              <div class="flex items-center gap-3"><div class="w-4 h-4 border-2 border-outline rounded-full bg-surface-container-lowest ml-3 mr-3"></div><span>连接符 (Connector)</span></div>
              <div class="flex items-center gap-3"><div class="w-10 h-0 border-b-2 border-outline relative ml-0 mr-0"><div class="absolute right-0 top-1/2 -translate-y-1/2 w-0 h-0 border-t-[4px] border-t-transparent border-l-[6px] border-l-outline border-b-[4px] border-b-transparent"></div></div><span>流程线 (Flow Line)</span></div>
            </div>
          </div>
        </div>
      </aside>

      <main class="flex-1 bg-surface-bright dot-grid relative overflow-hidden flex flex-col">
        <div v-if="error" class="absolute top-4 left-1/2 -translate-x-1/2 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg shadow-sm z-30 text-sm max-w-lg">
          <span class="material-symbols-outlined text-sm align-middle mr-1">error</span> {{ error }}
          <button @click="error = ''" class="ml-2 text-red-500 hover:text-red-700">&times;</button>
        </div>
        <div class="absolute bottom-6 left-1/2 -translate-x-1/2 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-sm flex items-center gap-1 p-1 z-10">
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" @click="zoomOut" :disabled="!hasDiagram"><span class="material-symbols-outlined">remove</span></button>
          <span class="font-label-mono text-label-mono text-on-surface-variant w-12 text-center">{{ zoomLevel }}%</span>
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" @click="zoomIn" :disabled="!hasDiagram"><span class="material-symbols-outlined">add</span></button>
          <div class="w-px h-6 bg-outline-variant mx-1"></div>
          <button class="p-2 text-primary hover:bg-surface-container-low rounded transition-colors"><span class="material-symbols-outlined">grid_on</span></button>
          <div class="w-px h-6 bg-outline-variant mx-1"></div>
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors flex items-center gap-1 pr-3" @click="resetZoom" :disabled="!hasDiagram"><span class="material-symbols-outlined">filter_center_focus</span><span class="font-label-mono text-xs hidden sm:inline">居中</span></button>
        </div>
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
