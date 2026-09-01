<script setup>
import { ref, computed, watch, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import ELK from 'elkjs/lib/elk.bundled.js'

const elk = new ELK()
const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const inputText = ref('用户发起请求\n验证用户身份\n如果 验证成功 -> 查询数据库\n    如果 数据存在 -> 返回结果 -> 结束\n    如果 数据不存在 -> 提示错误 -> 结束\n如果 验证失败 -> 拒绝访问 -> 结束')
const inputMode = ref('text') // 'text' | 'code'
const loading = ref(false)
const error = ref('')
const hasDiagram = ref(false)
const svgContent = ref('')
const zoomLevel = ref(100)
let currentZoom = 1
let currentFlowData = null
const showCode = ref(false)
const generatedCode = ref('')
const fcHistory = ref([])
const showSettings = ref(false)

// 颜色配置
const defaultColors = {
  start_end: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' },
  process: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' },
  decision: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' },
  input_output: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' },
  connector: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' },
  edge: { fill: '#000000', active: '#000000' },
  edgeLabel: { fill: '#ffffff', stroke: '#cccccc', text: '#1a1a1a' },
  edgeLabelActive: { fill: '#ffffff', stroke: '#000000', text: '#000000' },
}
const colors = ref(JSON.parse(JSON.stringify(defaultColors)))

// 加载保存的颜色
try {
  const saved = localStorage.getItem('fc-colors-v2')
  if (saved) colors.value = JSON.parse(saved)
} catch(e) {}

// 样式预设
const presets = [
  { name: '默认黑白', start_end: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' }, process: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' }, decision: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' }, input_output: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' }, connector: { fill: '#ffffff', stroke: '#000000', text: '#1a1a1a' }, edge: { fill: '#000000', active: '#000000' }, edgeLabel: { fill: '#ffffff', stroke: '#cccccc', text: '#1a1a1a' }, edgeLabelActive: { fill: '#ffffff', stroke: '#000000', text: '#000000' } },
  { name: '经典彩', start_end: { fill: '#d1fae5', stroke: '#059669', text: '#064e3b' }, process: { fill: '#dbeafe', stroke: '#2563eb', text: '#1e3a5f' }, decision: { fill: '#fef3c7', stroke: '#d97706', text: '#78350f' }, input_output: { fill: '#ede9fe', stroke: '#7c3aed', text: '#4c1d95' }, connector: { fill: '#f3f4f6', stroke: '#6b7280', text: '#1f2937' }, edge: { fill: '#64748b', active: '#2563eb' }, edgeLabel: { fill: '#f8fafc', stroke: '#cbd5e1', text: '#475569' }, edgeLabelActive: { fill: '#eff6ff', stroke: '#93c5fd', text: '#2563eb' } },
  { name: '紫色调', start_end: { fill: '#dcfce7', stroke: '#16a34a', text: '#14532d' }, process: { fill: '#f3e8ff', stroke: '#a855f7', text: '#6b21a8' }, decision: { fill: '#fef9c3', stroke: '#eab308', text: '#854d0e' }, input_output: { fill: '#fce7f3', stroke: '#ec4899', text: '#831843' }, connector: { fill: '#f1f5f9', stroke: '#94a3b8', text: '#334155' }, edge: { fill: '#a78bfa', active: '#7c3aed' }, edgeLabel: { fill: '#faf5ff', stroke: '#d8b4fe', text: '#6b21a8' }, edgeLabelActive: { fill: '#f5f3ff', stroke: '#c4b5fd', text: '#5b21b6' } },
  { name: '深色系', start_end: { fill: '#1a1a2e', stroke: '#4ade80', text: '#bbf7d0' }, process: { fill: '#1e3a5f', stroke: '#60a5fa', text: '#dbeafe' }, decision: { fill: '#451a03', stroke: '#f59e0b', text: '#fef3c7' }, input_output: { fill: '#2d1b4e', stroke: '#c084fc', text: '#e9d5ff' }, connector: { fill: '#1e293b', stroke: '#64748b', text: '#cbd5e1' }, edge: { fill: '#64748b', active: '#60a5fa' }, edgeLabel: { fill: '#1e293b', stroke: '#475569', text: '#cbd5e1' }, edgeLabelActive: { fill: '#1e3a5f', stroke: '#60a5fa', text: '#dbeafe' } },
]

// 颜色变化时自动保存并重渲
watch(colors, () => {
  localStorage.setItem('fc-colors-v2', JSON.stringify(colors.value))
  if (currentFlowData && hasDiagram.value) {
    renderFlowchart(currentFlowData)
  }
}, { deep: true })

function applyFcPreset(preset) {
  colors.value = JSON.parse(JSON.stringify(preset))
}

// 加载历史
try {
  const saved = localStorage.getItem('fc-history')
  if (saved) fcHistory.value = JSON.parse(saved)
} catch(e) {}

function saveFcHistory(input, mode, data) {
  const item = { id: Date.now(), input: input.substring(0, 200), mode, time: new Date().toLocaleString('zh-CN'), data }
  fcHistory.value.unshift(item)
  if (fcHistory.value.length > 20) fcHistory.value.pop()
  localStorage.setItem('fc-history', JSON.stringify(fcHistory.value))
}

const placeholder = computed(() => {
  return inputMode.value === 'code'
    ? '粘贴任意编程语言代码，例如 Python/Java/C++/JavaScript：\n\ndef check_prime(n):\n    if n <= 1: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True'
    : '在此输入逻辑，例如：\n如果支付成功 -> 发送邮件\n如果支付失败 -> 提示重试'
})

// 切换模式时清空输入
watch(inputMode, () => { inputText.value = '' })

// keep-alive 恢复时重新渲染
onActivated(() => {
  if (svgContent.value && hasDiagram.value) {
    const el = document.getElementById('flowchart-canvas')
    if (el) el.innerHTML = svgContent.value
  }
})

function parseToCode(data) {
  const nodes = (data?.nodes || [])
  const edges = (data?.edges || [])
  const nodeMap = {}
  nodes.forEach(n => { nodeMap[n.id] = n })

  // 找开始节点
  let startNode = nodes.find(n => n.type === 'start' || n.type === 'start_end')
  if (!startNode) startNode = nodes[0]
  if (!startNode) return '# 无法解析'

  const lines = ['# 自动生成的代码\n']
  const visited = new Set()

  function walk(nodeId, indent) {
    if (visited.has(nodeId)) return
    visited.add(nodeId)
    const node = nodeMap[nodeId]
    if (!node) return

    const text = node.text || node.label || ''
    const type = node.type

    if (type === 'start' || type === 'start_end') {
      lines.push(`${indent}# ${text}`)
    } else if (type === 'end') {
      lines.push(`${indent}# ${text}`)
    } else if (type === 'decision') {
      lines.push(`${indent}if ${text}:`)
      // 找"是"分支
      const yesEdge = edges.find(e => e.from === nodeId && (e.label === '是' || e.label === 'True' || e.label === 'Yes'))
      const noEdge = edges.find(e => e.from === nodeId && (e.label === '否' || e.label === 'False' || e.label === 'No'))
      if (yesEdge) walk(yesEdge.to, indent + '  ')
      if (noEdge) {
        lines.push(`${indent}else:`)
        walk(noEdge.to, indent + '  ')
      }
    } else if (type === 'process') {
      lines.push(`${indent}# ${text}`)
      const next = edges.find(e => e.from === nodeId && !visited.has(e.to))
      if (next) walk(next.to, indent)
    } else if (type === 'input_output') {
      lines.push(`${indent}print("${text}")`)
      const next = edges.find(e => e.from === nodeId && !visited.has(e.to))
      if (next) walk(next.to, indent)
    }
  }

  walk(startNode.id, '')
  generatedCode.value = lines.join('\n')
  showCode.value = true
}

// 节点尺寸
const ND = {
  start_end:    { w: 150, h: 46 },
  start:        { w: 150, h: 46 },
  end:          { w: 150, h: 46 },
  process:      { w: 170, h: 54 },
  decision:     { w: 160, h: 76 },
  input_output: { w: 170, h: 46 },
  io:           { w: 170, h: 46 },
  connector:    { w: 34,  h: 34 },
}

// 颜色
const CL = {
  start_end:    { fill: '#d1fae5', stroke: '#059669', text: '#064e3b' },
  start:        { fill: '#d1fae5', stroke: '#059669', text: '#064e3b' },
  end:          { fill: '#fee2e2', stroke: '#dc2626', text: '#7f1d1d' },
  process:      { fill: '#dbeafe', stroke: '#2563eb', text: '#1e3a5f' },
  decision:     { fill: '#fef3c7', stroke: '#d97706', text: '#78350f' },
  input_output: { fill: '#ede9fe', stroke: '#7c3aed', text: '#4c1d95' },
  io:           { fill: '#ede9fe', stroke: '#7c3aed', text: '#4c1d95' },
  connector:    { fill: '#f3f4f6', stroke: '#6b7280', text: '#1f2937' },
}

function mapNodeType(t) {
  if (t === 'start_end') return 'start_end'
  if (t === 'start') return 'start'
  if (t === 'end') return 'end'
  if (t === 'process') return 'process'
  if (t === 'decision') return 'decision'
  if (t === 'input_output') return 'input_output'
  if (t === 'io') return 'io'
  return 'process'
}

async function generate() {
  if (!inputText.value.trim()) return
  loading.value = true
  error.value = ''
  hasDiagram.value = false
  try {
    const description = inputMode.value === 'code'
      ? `请将以下代码转换为流程图：\n\n${inputText.value}`
      : inputText.value

    const res = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'flowchart', description: inputText.value }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `请求失败 (${res.status})`)
    }
    await renderFlowchart((await res.json()).data)
  } catch (e) {
    error.value = e.message
    loading.value = false
  }
}

/**
 * 使用 ELK.js 端口系统自动布局
 */
async function computeLayout(nodes, edges) {
  const elkNodes = nodes.map(n => {
    const t = mapNodeType(n.type)
    const d = ND[t] || ND.process
    const hw = d.w / 2, hh = d.h / 2

    // 为每个节点定义四个方向的端口
    const ports = [
      { id: `${n.id}.north`, layoutOptions: { 'side': 'NORTH', 'portIndex': '0' } },
      { id: `${n.id}.south`, layoutOptions: { 'side': 'SOUTH', 'portIndex': '0' } },
      { id: `${n.id}.west`,  layoutOptions: { 'side': 'WEST',  'portIndex': '0' } },
      { id: `${n.id}.east`,  layoutOptions: { 'side': 'EAST',  'portIndex': '0' } },
    ]

    // 菱形额外添加角端口
    if (t === 'decision') {
      ports.push(
        { id: `${n.id}.top`,     layoutOptions: { 'side': 'NORTH', 'portIndex': '1' } },
        { id: `${n.id}.bottom`,  layoutOptions: { 'side': 'SOUTH', 'portIndex': '1' } },
        { id: `${n.id}.left`,    layoutOptions: { 'side': 'WEST',  'portIndex': '1' } },
        { id: `${n.id}.right`,   layoutOptions: { 'side': 'EAST',  'portIndex': '1' } },
      )
    }

    return {
      id: n.id,
      width: d.w,
      height: d.h,
      labels: [{ text: n.text || n.label || '', width: d.w - 16 }],
      ports,
      layoutOptions: {
        'elk.nodeLabels.placement': 'INSIDE V_CENTER H_CENTER',
        'elk.portConstraints': 'FIXED_ORDER',
        'elk.portAlignment': 'CENTER',
        'elk.portSide': 'FIXED',
      }
    }
  })

  const elkEdges = edges.map((e, i) => {
    const fromOrig = nodes.find(n => n.id === e.from)
    const toOrig = nodes.find(n => n.id === e.to)
    const fromType = fromOrig ? mapNodeType(fromOrig.type) : 'process'
    const toType = toOrig ? mapNodeType(toOrig.type) : 'process'
    const isDecision = fromType === 'decision' && e.label

    // 节点坐标
    const fromX = fromOrig?.x || 0
    const toX = toOrig?.x || 0
    const fromY = fromOrig?.y || 0
    const toY = toOrig?.y || 0
    const isHorizontal = Math.abs(fromY - toY) < 80 && Math.abs(fromX - toX) > 50

    // 源端口
    let srcPort
    if (isDecision) {
      srcPort = e.label === '是' ? `${e.from}.bottom` : `${e.from}.left`
    } else if (isHorizontal) {
      srcPort = fromX < toX ? `${e.from}.east` : `${e.from}.west`
    } else {
      srcPort = `${e.from}.south`
    }

    // 目标端口
    let tgtPort
    if (toType === 'decision') {
      tgtPort = `${e.to}.top`
    } else if (isHorizontal) {
      tgtPort = fromX < toX ? `${e.to}.west` : `${e.to}.east`
    } else {
      tgtPort = `${e.to}.north`
    }

    return {
      id: `edge-${i}`,
      sources: [e.from],
      targets: [e.to],
      sourcePortRef: srcPort,
      targetPortRef: tgtPort,
      labels: e.label ? [{ text: e.label }] : [],
      layoutOptions: {
        'elk.edgeLabels.placement': 'OUTSIDE',
        'elk.edgeRouting': 'POLYLINE',
      }
    }
  })

  const graph = {
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': 'DOWN',
      'elk.layered.spacing.nodeNodeBetweenLayers': 100,
      'elk.layered.spacing.nodeNode': 140,
      'elk.spacing.nodeNode': 140,
      'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
      'elk.layered.cycleBreaking.strategy': 'GREEDY',
      'elk.layered.nodePlacement.strategy': 'BRANDES_KOEPF',
      'elk.edgeRouting': 'POLYLINE',
      'elk.layered.mergeEdges': 'true',
      'elk.layered.feedbackEdges': 'true',
      'elk.portConstraints': 'FIXED_SIDE',
    },
    children: elkNodes,
    edges: elkEdges,
  }

  const layoutedGraph = await elk.layout(graph)

  let maxX = 0, maxY = 0, minX = Infinity, minY = Infinity
  layoutedGraph.children?.forEach(n => {
    maxX = Math.max(maxX, n.x + n.width)
    maxY = Math.max(maxY, n.y + n.height)
    minX = Math.min(minX, n.x)
    minY = Math.min(minY, n.y)
  })

  const padding = 80
  return {
    layoutedGraph,
    canvasW: maxX - minX + padding * 2,
    canvasH: maxY - minY + padding * 2,
    offsetX: padding - minX,
    offsetY: padding - minY,
  }
}

async function renderFlowchart(data) {
  const nodes = (data?.nodes || []).filter(n => n && n.id)
  let edges = (data?.edges || []).filter(e => e && e.from && e.to)

  // 过滤掉引用不存在节点的边
  const validIds = new Set(nodes.map(n => n.id))
  edges = edges.filter(e => validIds.has(e.from) && validIds.has(e.to))

  if (nodes.length === 0) {
    error.value = 'AI 返回了空数据，请换一种描述重试'
    return
  }

  const { layoutedGraph, canvasW, canvasH, offsetX, offsetY } = await computeLayout(nodes, edges)

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${canvasW}" height="${canvasH}" viewBox="0 0 ${canvasW} ${canvasH}" style="font-family:Inter,sans-serif">`
  svg += '<defs>'
  svg += `<marker id="ah" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="10" markerHeight="7" orient="auto"><path d="M0 0L10 3.5L0 7Z" fill="${colors.value.edge.fill}"/></marker>`
  svg += `<marker id="aha" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="10" markerHeight="7" orient="auto"><path d="M0 0L10 3.5L0 7Z" fill="${colors.value.edge.active}"/></marker>`
  svg += '</defs>'
  svg += '<g>'

  // ---- ELK 自动路由连线 ----
  layoutedGraph.edges?.forEach(le => {
    const fromId = le.sources[0]
    const toId = le.targets[0]
    const origEdge = edges.find(e => e.from === fromId && e.to === toId)
    const active = !!origEdge?.label
    const sc = active ? colors.value.edge.active : colors.value.edge.fill
    const sw = active ? 2 : 1.5
    const mk = active ? 'url(#aha)' : 'url(#ah)'

    const points = []
    if (le.sections && le.sections.length > 0) {
      le.sections.forEach(sec => {
        if (sec.startPoint) points.push(`${sec.startPoint.x + offsetX},${sec.startPoint.y + offsetY}`)
        if (sec.bendPoints) sec.bendPoints.forEach(bp => points.push(`${bp.x + offsetX},${bp.y + offsetY}`))
        if (sec.endPoint) points.push(`${sec.endPoint.x + offsetX},${sec.endPoint.y + offsetY}`)
      })
    }

    if (points.length >= 2) {
      const d = `M${points.join(' L')}`
      svg += `<path d="${d}" fill="none" stroke="${sc}" stroke-width="${sw}" marker-end="${mk}" stroke-linecap="round" stroke-linejoin="round"/>`
    }

    // 标签
    if (le.labels && le.labels.length > 0) {
      le.labels.forEach((lbl, li) => {
        const lblColors = active ? colors.value.edgeLabelActive : colors.value.edgeLabel
        const fc = lblColors.text
        const fb = lblColors.fill
        const sb = lblColors.stroke
        const tw = (lbl.text?.length || 1) * 12 + 18
        const lx = (lbl.x || 0) + offsetX
        const ly = (lbl.y || 0) + offsetY
        const labelId = `label-${le.id || i}-${li}`
        svg += `<g data-label-id="${labelId}" transform="translate(${lx}, ${ly})" style="cursor:grab">`
        svg += `<rect x="${-tw/2}" y="-10" width="${tw}" height="20" rx="4" fill="${fb}" stroke="${sb}" stroke-width="1"/>`
        svg += `<text x="0" y="4" text-anchor="middle" font-size="11" fill="${fc}" font-weight="500">${lbl.text || ''}</text>`
        svg += `</g>`
      })
    }
  })

  // ---- 节点 ----
  layoutedGraph.children?.forEach(ln => {
    const origNode = nodes.find(n => n.id === ln.id)
    if (!origNode || ln.x == null || ln.y == null) return
    const nodeType = mapNodeType(origNode.type)
    const cc = colors.value[nodeType] || colors.value.process
    const nd = ND[nodeType] || ND.process
    const cx = ln.x + ln.width / 2
    const cy = ln.y + ln.height / 2

    svg += `<g data-node-id="${origNode.id}" transform="translate(${cx + offsetX}, ${cy + offsetY})" style="cursor:grab">`
    svg += makeShape(nodeType, nd.w, nd.h, 0, 0, cc)
    const label = origNode.text || origNode.label || ln.labels?.[0]?.text || ''
    const ty = nodeType === 'decision' ? 2 : 3
    svg += `<text x="0" y="${ty}" text-anchor="middle" dominant-baseline="middle" font-size="12.5" fill="${cc.text}" font-weight="${nodeType === 'decision' ? 600 : 400}">${label}</text>`
    svg += `</g>`
  })

  svg += '</g></svg>'
  svgContent.value = svg
  currentFlowData = data

  const el = document.getElementById('flowchart-canvas')
  if (el) el.innerHTML = svg

  // 流程图拖拽（节点 + 标签）
  const svgEl = el.querySelector('svg')
  if (!svgEl) return
  const gEl = svgEl.querySelector('g')
  if (!gEl) return

  const nodeGroups = gEl.querySelectorAll('g[data-node-id]')
  const labelGroups = gEl.querySelectorAll('g[data-label-id]')
  let fcDragging = null
  const nodePos = {}

  nodeGroups.forEach(ng => {
    const id = ng.getAttribute('data-node-id')
    const transform = ng.getAttribute('transform')
    const m = transform.match(/translate\(([-\d.]+),\s*([-\d.]+)\)/)
    if (m) nodePos[id] = { x: parseFloat(m[1]), y: parseFloat(m[2]) }
    ng.addEventListener('mousedown', function(e) {
      e.stopPropagation(); e.preventDefault()
      fcDragging = { id, el: ng }
      ng.style.cursor = 'grabbing'
      ng.parentNode.appendChild(ng)
    })
  })

  labelGroups.forEach(lg => {
    lg.addEventListener('mousedown', function(e) {
      e.stopPropagation(); e.preventDefault()
      fcDragging = { el: lg, isLabel: true }
      lg.style.cursor = 'grabbing'
      lg.parentNode.appendChild(lg)
    })
  })

  window.addEventListener('mousemove', function(e) {
    if (!fcDragging) return
    const { el, isLabel } = fcDragging
    const rect = svgEl.getBoundingClientRect()
    const scaleX = svgEl.viewBox.baseVal.width / rect.width
    const scaleY = svgEl.viewBox.baseVal.height / rect.height
    const mx = (e.clientX - rect.left) * scaleX
    const my = (e.clientY - rect.top) * scaleY
    el.setAttribute('transform', `translate(${mx}, ${my})`)
  })

  window.addEventListener('mouseup', function() {
    if (fcDragging) {
      fcDragging.el.style.cursor = 'grab'
      fcDragging = null
    }
  })

  loading.value = false
  hasDiagram.value = true
  saveFcHistory(inputText.value, inputMode.value, data)
}

async function restoreFcHistory(item) {
  inputText.value = item.input
  inputMode.value = item.mode
  hasDiagram.value = true
  const data = item.data.data || item.data
  await renderFlowchart(data)
  currentFlowData = data
}

function makeShape(type, w, h, cx, cy, c) {
  switch (type) {
    case 'start':
    case 'end':
    case 'start_end':
      return `<rect x="${cx - w/2}" y="${cy - h/2}" width="${w}" height="${h}" rx="${h/2}" fill="${c.fill}" stroke="${c.stroke}" stroke-width="2"/>`
    case 'process':
      return `<rect x="${cx - w/2}" y="${cy - h/2}" width="${w}" height="${h}" rx="6" fill="${c.fill}" stroke="${c.stroke}" stroke-width="2"/>`
    case 'decision':
      return `<polygon points="${cx},${cy-h/2} ${cx+w/2},${cy} ${cx},${cy+h/2} ${cx-w/2},${cy}" fill="${c.fill}" stroke="${c.stroke}" stroke-width="2"/>`
    case 'io':
    case 'input_output': {
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
  if (svg) { svg.style.transform = `scale(${currentZoom})`; svg.style.transformOrigin = 'center center' }
}
function downloadSVG() {
  if (!svgContent.value) return
  const blob = new Blob([svgContent.value], { type: 'image/svg+xml' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
  a.download = `flowchart-${Date.now()}.svg`; a.click()
}
function downloadPNG() {
  if (!svgContent.value) return
  const svgEl = document.querySelector('#flowchart-canvas svg')
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
      a.download = `flowchart-${Date.now()}.png`
      a.click()
    }, 'image/png')
  }
  img.src = url
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
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" @click="downloadSVG" :disabled="!svgContent" title="下载 SVG">
          <span class="material-symbols-outlined">download</span>
        </button>
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" @click="downloadPNG" :disabled="!svgContent" title="下载 PNG">
          <span class="material-symbols-outlined">image</span>
        </button>
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" @click="parseToCode(currentFlowData)" :disabled="!svgContent" title="解析为代码">
          <span class="material-symbols-outlined">code</span>
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
            <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-2">输入方式</h2>
            <div class="flex gap-1 p-1 bg-surface-container-low rounded-lg mb-3">
              <button @click="inputMode = 'text'" :class="inputMode === 'text' ? 'bg-primary-container text-on-primary' : 'text-on-surface-variant'" class="flex-1 py-1.5 px-3 rounded-md text-sm font-medium transition-all">自然语言</button>
              <button @click="inputMode = 'code'" :class="inputMode === 'code' ? 'bg-primary-container text-on-primary' : 'text-on-surface-variant'" class="flex-1 py-1.5 px-3 rounded-md text-sm font-medium transition-all">代码</button>
            </div>
            <textarea v-model="inputText" class="w-full h-40 p-3 bg-surface-container-lowest border border-outline-variant rounded focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary font-code-sm text-code-sm resize-none text-on-surface" :placeholder="placeholder"></textarea>
          </div>
          <button @click="generate" :disabled="loading || !inputText.trim()" class="w-full py-2 bg-primary-container text-on-primary rounded hover:bg-primary transition-colors font-label-mono text-label-mono font-bold flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">
            <span v-if="loading" class="material-symbols-outlined animate-spin">progress_activity</span>
            <span v-else class="material-symbols-outlined">auto_awesome</span>
            {{ loading ? '生成中...' : '生成图表' }}
          </button>
          <div class="border-t border-outline-variant pt-4">
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-label-mono text-label-mono text-on-surface-variant">对话历史</h3>
              <button v-if="fcHistory.length" @click="fcHistory = []; localStorage.removeItem('fc-history')" class="text-xs text-secondary hover:text-primary">清空</button>
            </div>
            <div v-if="fcHistory.length" class="space-y-2 max-h-36 overflow-y-auto mb-4">
              <div v-for="item in fcHistory" :key="item.id" @click="restoreFcHistory(item)" class="p-2 bg-surface-container-lowest rounded-lg cursor-pointer hover:bg-surface-container-low transition-colors">
                <p class="font-code-sm text-code-sm text-on-surface truncate">{{ item.input }}</p>
                <div class="flex items-center justify-between mt-1">
                  <span class="text-[10px] text-secondary">{{ item.mode === 'code' ? '代码' : '自然语言' }}</span>
                  <span class="text-[10px] text-outline-variant">{{ item.time }}</span>
                </div>
              </div>
            </div>
            <p v-else class="font-code-sm text-code-sm text-outline-variant text-sm mb-4">暂无历史</p>
            <!-- 样式设置 -->
            <div class="border-t border-outline-variant pt-4 mb-4">
              <div class="flex items-center justify-between mb-3 cursor-pointer" @click="showSettings = !showSettings">
                <h3 class="font-label-mono text-label-mono text-on-surface-variant flex items-center gap-2">
                  <span class="material-symbols-outlined text-secondary">palette</span>
                  样式设置
                </h3>
                <span class="material-symbols-outlined text-sm text-secondary" :style="{ transform: showSettings ? 'rotate(180deg)' : '' }">expand_more</span>
              </div>
              <div v-if="showSettings" class="space-y-3">
                <div>
                  <p class="text-xs text-on-surface-variant mb-2">预设样式</p>
                  <div class="grid grid-cols-2 gap-1.5">
                    <button v-for="p in presets" :key="p.name" @click="applyFcPreset(p)" class="px-2 py-1.5 rounded-lg text-xs font-medium border transition-colors" :style="{ borderColor: p.process.stroke, backgroundColor: p.process.fill + '40', color: p.process.text }">{{ p.name }}</button>
                  </div>
                </div>
                <div>
                  <p class="text-xs text-on-surface-variant mb-2">处理节点颜色</p>
                  <div class="flex gap-2">
                    <div class="flex-1"><label class="text-[10px] text-outline-variant">背景</label><input type="color" v-model="colors.process.fill" class="w-full h-6 rounded cursor-pointer"></div>
                    <div class="flex-1"><label class="text-[10px] text-outline-variant">边框</label><input type="color" v-model="colors.process.stroke" class="w-full h-6 rounded cursor-pointer"></div>
                    <div class="flex-1"><label class="text-[10px] text-outline-variant">文字</label><input type="color" v-model="colors.process.text" class="w-full h-6 rounded cursor-pointer"></div>
                  </div>
                </div>
                <div>
                  <p class="text-xs text-on-surface-variant mb-2">判断节点颜色</p>
                  <div class="flex gap-2">
                    <div class="flex-1"><label class="text-[10px] text-outline-variant">背景</label><input type="color" v-model="colors.decision.fill" class="w-full h-6 rounded cursor-pointer"></div>
                    <div class="flex-1"><label class="text-[10px] text-outline-variant">边框</label><input type="color" v-model="colors.decision.stroke" class="w-full h-6 rounded cursor-pointer"></div>
                    <div class="flex-1"><label class="text-[10px] text-outline-variant">文字</label><input type="color" v-model="colors.decision.text" class="w-full h-6 rounded cursor-pointer"></div>
                  </div>
                </div>
                <div>
                  <p class="text-xs text-on-surface-variant mb-2">连线颜色</p>
                  <div class="flex gap-2">
                    <div class="flex-1"><label class="text-[10px] text-outline-variant">普通</label><input type="color" v-model="colors.edge.fill" class="w-full h-6 rounded cursor-pointer"></div>
                    <div class="flex-1"><label class="text-[10px] text-outline-variant">激活</label><input type="color" v-model="colors.edge.active" class="w-full h-6 rounded cursor-pointer"></div>
                  </div>
                </div>
                <button @click="colors = JSON.parse(JSON.stringify(defaultColors)); if(currentFlowData && hasDiagram.value) renderFlowchart(currentFlowData)" class="w-full py-1.5 text-xs border border-outline-variant rounded-lg text-secondary hover:text-primary hover:border-primary transition-colors">恢复默认</button>
              </div>
            </div>
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

        <!-- 代码面板 -->
        <div v-if="showCode" class="absolute inset-0 bg-surface-bright/95 backdrop-blur-sm z-30 flex flex-col">
          <div class="flex items-center justify-between p-4 border-b border-outline-variant">
            <h3 class="font-label-mono text-label-mono font-bold">生成代码 (Python)</h3>
            <button @click="showCode = false" class="text-secondary hover:text-primary p-1">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <pre class="flex-1 p-4 font-code-sm text-code-sm text-on-surface overflow-auto"><code>{{ generatedCode }}</code></pre>
          <div class="p-4 border-t border-outline-variant flex gap-2">
            <button @click="navigator.clipboard.writeText(generatedCode)" class="bg-primary-container text-on-primary rounded-lg py-2 px-4 font-label-mono text-label-mono">复制代码</button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
