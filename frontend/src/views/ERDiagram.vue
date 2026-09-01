<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import * as d3 from 'd3'

const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const inputText = ref('')
const inputMode = ref('text') // 'text' | 'sql'
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
    const description = inputMode.value === 'sql'
      ? `请解析以下 SQL 建表语句，生成 E-R 图：\n\n${inputText.value}`
      : inputText.value

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

  // ========== 智能初始布局 ==========
  const entityNodes = nodes.filter(n => n.type === 'entity')
  const relNodes = nodes.filter(n => n.type === 'relationship')
  const attrNodes = nodes.filter(n => n.type === 'attribute')

  // 构建实体邻接关系
  const entityAdj = {}
  entityNodes.forEach(e => { entityAdj[e.id] = new Set() })
  relationships.forEach(r => {
    const fid = `e-${r.from_entity || r.from}`
    const tid = `e-${r.to_entity || r.to}`
    if (entityAdj[fid]) entityAdj[fid].add(tid)
    if (entityAdj[tid]) entityAdj[tid].add(fid)
  })

  // BFS 分层
  const layers = []
  const placed = new Set()
  const visited = new Set()
  const centerEntity = entityNodes.reduce((max, e) =>
    (entityAdj[e.id]?.size || 0) > (entityAdj[max.id]?.size || 0) ? e : max, entityNodes[0])
  let queue = [centerEntity.id]
  visited.add(centerEntity.id)

  while (queue.length > 0) {
    layers.push(queue)
    const nextQueue = []
    for (const eid of queue) {
      for (const adj of (entityAdj[eid] || [])) {
        if (!visited.has(adj)) {
          nextQueue.push(adj)
          visited.add(adj)
        }
      }
    }
    queue = nextQueue
  }
  entityNodes.forEach(e => { if (!visited.has(e.id)) { layers.push([e.id]); visited.add(e.id) } })

  if (entityNodes.length >= 6) {
    // 6+ 实体：分层布局
    const layerGap = 600
    const entityGap = 450
    layers.forEach((layer, li) => {
      const count = layer.length
      const totalW = (count - 1) * entityGap
      layer.forEach((eid, ei) => {
        const node = entityNodes.find(e => e.id === eid)
        if (node) {
          node.x = -totalW / 2 + ei * entityGap
          node.y = li * layerGap
        }
      })
    })
  } else {
    // ≤5 实体：圆形布局
    const ordered = layers.flat().map(id => entityNodes.find(e => e.id === id)).filter(Boolean)
    const radius = 350
    const step = (2 * Math.PI) / Math.max(ordered.length, 1)
    ordered.forEach((e, i) => {
      e.x = Math.cos(i * step - Math.PI / 2) * radius
      e.y = Math.sin(i * step - Math.PI / 2) * radius
    })
  }

  // 关系节点放两实体中点
  relNodes.forEach(r => {
    const fromE = entityNodes.find(e => e.id === r.fromEntity)
    const toE = entityNodes.find(e => e.id === r.toEntity)
    if (fromE && toE) {
      r.x = (fromE.x + toE.x) / 2
      r.y = (fromE.y + toE.y) / 2
    }
  })

  // 属性节点绕父实体分布
  const parentAttrMap = {}
  attrNodes.forEach(a => {
    const link = links.find(l => l.target === a.id || l.source === a.id)
    if (!link) return
    const pid = link.source === a.id ? link.target : link.source
    if (!parentAttrMap[pid]) parentAttrMap[pid] = []
    parentAttrMap[pid].push(a)
  })
  Object.entries(parentAttrMap).forEach(([pid, group]) => {
    const parent = nodes.find(n => n.id === pid)
    if (!parent) return
    const aStep = (2 * Math.PI) / Math.max(group.length, 1)
    group.forEach((a, i) => {
      a.x = parent.x + Math.cos(i * aStep - Math.PI / 2) * 140
      a.y = parent.y + Math.sin(i * aStep - Math.PI / 2) * 140
    })
  })

  // BFS布局 + 轻量力导向微调
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(150).strength(0.8))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('collision', d3.forceCollide().radius(60))
  sim.stop()
  for (let i = 0; i < 200; i++) sim.tick()

  // 根据节点实际位置自动计算画布大小
  const padding = 200
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  nodes.forEach(n => {
    minX = Math.min(minX, n.x); minY = Math.min(minY, n.y)
    maxX = Math.max(maxX, n.x); maxY = Math.max(maxY, n.y)
  })
  const svgW = Math.max(maxX - minX + padding * 2, 600)
  const svgH = Math.max(maxY - minY + padding * 2, 400)
  const offsetX = padding - minX
  const offsetY = padding - minY

  // 平移所有节点到正坐标
  nodes.forEach(n => { n.x += offsetX; n.y += offsetY })

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

  // 基数标注（可拖动）
  const cardTexts = []
  relationships.forEach(r => {
    const fn = nodes.find(n => n.refId === (r.from_entity || r.from) && n.type === 'entity')
    const tn = nodes.find(n => n.refId === (r.to_entity || r.to) && n.type === 'entity')
    const rn = nodes.find(n => n.refId === r.id && n.type === 'relationship')
    const fromCard = r.from_cardinality || r.cardinality?.from || 'N'
    const toCard = r.to_cardinality || r.cardinality?.to || 'M'

    if (fn && rn) {
      const mx = (fn.x + rn.x) / 2, my = (fn.y + rn.y) / 2 - 14
      const cardNode = { x: mx, y: my, type: 'cardinality', text: fromCard }
      cardTexts.push(cardNode)
      const gText = g.append('g').attr('class', 'card-group')
        .attr('transform', `translate(${mx}, ${my})`).datum(cardNode)
      gText.append('text').attr('text-anchor', 'middle').attr('font-size', 12)
        .attr('font-family', 'JetBrains Mono,monospace').attr('fill', '#0891b2')
        .attr('font-weight', '600').text(fromCard)
    }
    if (tn && rn) {
      const mx = (tn.x + rn.x) / 2, my = (tn.y + rn.y) / 2 - 14
      const cardNode = { x: mx, y: my, type: 'cardinality', text: toCard }
      cardTexts.push(cardNode)
      const gText = g.append('g').attr('class', 'card-group')
        .attr('transform', `translate(${mx}, ${my})`).datum(cardNode)
      gText.append('text').attr('text-anchor', 'middle').attr('font-size', 12)
        .attr('font-family', 'JetBrains Mono,monospace').attr('fill', '#0891b2')
        .attr('font-weight', '600').text(toCard)
    }
  })

  // 实体矩形
  nodes.filter(n => n.type === 'entity').forEach(node => {
    const ew = 120, eh = 44
    const gNode = g.append('g').attr('class', 'node-group').attr('transform', `translate(${node.x}, ${node.y})`)

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
    const gNode = g.append('g').attr('class', 'node-group').attr('transform', `translate(${node.x}, ${node.y})`)

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
    const gNode = g.append('g').attr('class', 'node-group').attr('transform', `translate(${node.x}, ${node.y})`)

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

  // 拖拽行为（原生鼠标事件）
  let draggingNode = null

  // 先给每个节点组绑定对应的 node 数据
  g.selectAll('g.node-group').each(function() {
    const gEl = d3.select(this)
    const transform = gEl.attr('transform')
    const match = transform.match(/translate\(([-\d.]+),\s*([-\d.]+)\)/)
    if (match) {
      const tx = parseFloat(match[1]), ty = parseFloat(match[2])
      const node = nodes.find(n => Math.abs(n.x - tx) < 2 && Math.abs(n.y - ty) < 2)
      if (node) gEl.datum(node)
    }
  })

  // 所有节点组添加拖拽
  g.selectAll('g.node-group, g.card-group')
    .attr('style', 'cursor: grab')
    .on('mousedown', function(event) {
      event.stopPropagation()
      event.preventDefault()
      const gEl = d3.select(this)
      const node = gEl.datum()
      if (!node) return
      draggingNode = { node, el: gEl }
      gEl.attr('style', 'cursor: grabbing')
      gEl.raise()
    })

  d3.select(window).on('mousemove.drag', function(event) {
    if (!draggingNode) return
    const { node, el } = draggingNode
    const [mx, my] = d3.pointer(event, g.node())
    node.x = mx
    node.y = my
    el.attr('transform', `translate(${mx}, ${my})`)
    updateLines()
  })

  d3.select(window).on('mouseup.drag', function() {
    if (draggingNode) {
      draggingNode.el.attr('style', 'cursor: grab')
      draggingNode = null
    }
  })

  function updateLines() {
    const lineElements = g.selectAll('line').nodes()
    lineElements.forEach((lineEl, i) => {
      const link = links[i]
      if (!link) return
      const src = nodes.find(n => n.id === (link.source.id || link.source))
      const tgt = nodes.find(n => n.id === (link.target.id || link.target))
      if (src && tgt) {
        d3.select(lineEl).attr('x1', src.x).attr('y1', src.y).attr('x2', tgt.x).attr('y2', tgt.y)
      }
    })
  }

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
function downloadPNG() {
  if (!svgContent.value) return
  const svgEl = document.querySelector('#er-canvas svg')
  if (!svgEl) return
  const svgData = new XMLSerializer().serializeToString(svgEl)
  const canvas = document.createElement('canvas')
  canvas.width = svgEl.viewBox.baseVal.width * 2
  canvas.height = svgEl.viewBox.baseVal.height * 2
  const ctx = canvas.getContext('2d')
  ctx.scale(2, 2)
  const img = new Image()
  const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svgBlob)
  img.onload = function() {
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0)
    URL.revokeObjectURL(url)
    canvas.toBlob(blob => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `er-diagram-${Date.now()}.png`
      a.click()
    }, 'image/png')
  }
  img.src = url
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
        <button class="text-primary hover:bg-surface-container-low transition-colors p-2 rounded-full" @click="downloadSVG" :disabled="!svgContent" title="下载 SVG">
          <span class="material-symbols-outlined">download</span>
        </button>
        <button class="text-primary hover:bg-surface-container-low transition-colors p-2 rounded-full" @click="downloadPNG" :disabled="!svgContent" title="下载 PNG">
          <span class="material-symbols-outlined">image</span>
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
          <h2 class="font-label-mono text-label-mono text-on-surface-variant mb-2">输入方式</h2>
          <div class="flex gap-1 p-1 bg-surface-container-low rounded-lg">
            <button @click="inputMode = 'text'" :class="inputMode === 'text' ? 'bg-primary-container text-on-primary' : 'text-on-surface-variant'" class="flex-1 py-1.5 px-3 rounded-md text-sm font-medium transition-all">自然语言</button>
            <button @click="inputMode = 'sql'" :class="inputMode === 'sql' ? 'bg-primary-container text-on-primary' : 'text-on-surface-variant'" class="flex-1 py-1.5 px-3 rounded-md text-sm font-medium transition-all">SQL 语句</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto p-4">
          <textarea
            v-model="inputText"
            class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-48 w-full"
            :placeholder="inputMode === 'sql' ? 'CREATE TABLE 学生 (\n  学号 VARCHAR(20) PRIMARY KEY,\n  姓名 VARCHAR(50)\n);\n\nCREATE TABLE 课程 (\n  课程号 VARCHAR(20) PRIMARY KEY,\n  名称 VARCHAR(100)\n);' : '学生选课系统：学生有学号、姓名、邮箱；课程有课程号、名称、学分；学生和课程是多对多的选课关系'"
          ></textarea>
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
