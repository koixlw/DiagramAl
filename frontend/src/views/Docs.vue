<template>
  <div class="bg-background text-on-background font-body-md h-screen flex flex-col overflow-hidden">
    <header class="bg-surface border-b border-outline-variant flex items-center w-full px-gutter h-16 shrink-0">
      <button @click="router.push('/')" class="flex items-center gap-2 text-primary hover:bg-surface-container-low rounded-lg px-3 py-1.5 transition-colors">
        <span class="material-symbols-outlined">arrow_back</span>
        <span class="font-headline-md font-bold">DiagramAI</span>
      </button>
      <span class="font-label-mono text-label-mono text-on-surface-variant ml-4">使用文档</span>
    </header>

    <div class="flex-1 overflow-auto">
      <div class="max-w-3xl mx-auto p-6 space-y-8">
        <!-- 简介 -->
        <section>
          <h1 class="font-headline-lg text-on-background mb-2">DiagramAI 使用文档</h1>
          <p class="font-body-md text-on-surface-variant">AI 驱动的智能图表生成工具，支持自然语言和代码输入，自动生成流程图和 E-R 图。</p>
        </section>

        <!-- 快速开始 -->
        <section class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">rocket_launch</span>
            快速开始
          </h2>
          <div class="space-y-3">
            <div class="flex gap-3">
              <span class="w-6 h-6 rounded-full bg-primary text-on-primary text-xs flex items-center justify-center shrink-0 font-bold">1</span>
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">选择图表类型</p>
                <p class="font-code-sm text-code-sm text-on-surface-variant text-xs mt-0.5">在左侧点击"流程图"或"E-R 图"进入对应页面</p>
              </div>
            </div>
            <div class="flex gap-3">
              <span class="w-6 h-6 rounded-full bg-primary text-on-primary text-xs flex items-center justify-center shrink-0 font-bold">2</span>
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">输入描述</p>
                <p class="font-code-sm text-code-sm text-on-surface-variant text-xs mt-0.5">流程图支持自然语言和代码输入；E-R 图支持自然语言和 SQL 输入</p>
              </div>
            </div>
            <div class="flex gap-3">
              <span class="w-6 h-6 rounded-full bg-primary text-on-primary text-xs flex items-center justify-center shrink-0 font-bold">3</span>
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">点击生成</p>
                <p class="font-code-sm text-code-sm text-on-surface-variant text-xs mt-0.5">AI 自动解析并生成图表</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 流程图 -->
        <section class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">account_tree</span>
            流程图
          </h2>
          <div class="space-y-4">
            <div>
              <h3 class="font-label-mono text-label-mono text-on-surface mb-2">输入方式</h3>
              <div class="grid grid-cols-2 gap-3">
                <div class="bg-surface-container-low rounded-lg p-3">
                  <p class="font-code-sm text-code-sm font-bold text-on-surface">自然语言</p>
                  <pre class="font-code-sm text-code-sm text-on-surface-variant text-xs mt-1 bg-surface-container-lowest rounded p-2 overflow-x-auto">用户发起请求
验证用户身份
如果 验证成功 -> 查询数据库
如果 数据存在 -> 返回结果 -> 结束</pre>
                </div>
                <div class="bg-surface-container-low rounded-lg p-3">
                  <p class="font-code-sm text-code-sm font-bold text-on-surface">代码</p>
                  <pre class="font-code-sm text-code-sm text-on-surface-variant text-xs mt-1 bg-surface-container-lowest rounded p-2 overflow-x-auto">def is_prime(n):
    if n <= 1: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True</pre>
                </div>
              </div>
            </div>
            <div>
              <h3 class="font-label-mono text-label-mono text-on-surface mb-2">图形规范</h3>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <div class="flex items-center gap-2 p-2 bg-surface-container-low rounded"><div class="w-8 h-5 border-2 border-outline rounded-full shrink-0"></div><span>开始/结束</span></div>
                <div class="flex items-center gap-2 p-2 bg-surface-container-low rounded"><div class="w-8 h-5 border-2 border-outline shrink-0"></div><span>处理过程</span></div>
                <div class="flex items-center gap-2 p-2 bg-surface-container-low rounded"><div class="w-6 h-6 border-2 border-outline rotate-45 shrink-0"></div><span>判断分支</span></div>
                <div class="flex items-center gap-2 p-2 bg-surface-container-low rounded"><div class="w-8 h-5 border-2 border-outline -skew-x-12 shrink-0"></div><span>输入/输出</span></div>
              </div>
            </div>
          </div>
        </section>

        <!-- E-R 图 -->
        <section class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">database</span>
            E-R 图
          </h2>
          <div class="space-y-4">
            <div>
              <h3 class="font-label-mono text-label-mono text-on-surface mb-2">输入方式</h3>
              <div class="grid grid-cols-2 gap-3">
                <div class="bg-surface-container-low rounded-lg p-3">
                  <p class="font-code-sm text-code-sm font-bold text-on-surface">自然语言</p>
                  <pre class="font-code-sm text-code-sm text-on-surface-variant text-xs mt-1 bg-surface-container-lowest rounded p-2 overflow-x-auto">学生有学号、姓名、邮箱
课程有课程号、名称、学分
学生和课程是多对多的选课关系</pre>
                </div>
                <div class="bg-surface-container-low rounded-lg p-3">
                  <p class="font-code-sm text-code-sm font-bold text-on-surface">SQL 语句</p>
                  <pre class="font-code-sm text-code-sm text-on-surface-variant text-xs mt-1 bg-surface-container-lowest rounded p-2 overflow-x-auto">CREATE TABLE 学生 (
  学号 VARCHAR(20) PRIMARY KEY,
  姓名 VARCHAR(50)
);</pre>
                </div>
              </div>
            </div>
            <div>
              <h3 class="font-label-mono text-label-mono text-on-surface mb-2">图形规范</h3>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <div class="flex items-center gap-2 p-2 bg-surface-container-low rounded"><div class="w-8 h-5 border-2 border-outline shrink-0"></div><span>实体 (矩形)</span></div>
                <div class="flex items-center gap-2 p-2 bg-surface-container-low rounded"><div class="w-6 h-6 border-2 border-outline rotate-45 shrink-0"></div><span>关系 (菱形)</span></div>
                <div class="flex items-center gap-2 p-2 bg-surface-container-low rounded"><div class="w-8 h-5 border border-outline rounded-full shrink-0"></div><span>属性 (椭圆)</span></div>
                <div class="flex items-center gap-2 p-2 bg-surface-container-low rounded"><span class="font-code-sm underline">学号</span><span>主键 (下划线)</span></div>
              </div>
            </div>
          </div>
        </section>

        <!-- 高级功能 -->
        <section class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">tune</span>
            高级功能
          </h2>
          <div class="space-y-3">
            <div class="flex gap-3">
              <span class="material-symbols-outlined text-secondary shrink-0">swap_horiz</span>
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">拖拽节点</p>
                <p class="font-code-sm text-code-sm text-on-surface-variant text-xs">流程图和 E-R 图的所有节点（实体、属性、关系、标签）都可以自由拖拽</p>
              </div>
            </div>
            <div class="flex gap-3">
              <span class="material-symbols-outlined text-secondary shrink-0">palette</span>
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">自定义样式</p>
                <p class="font-code-sm text-code-sm text-on-surface-variant text-xs">在侧边栏底部"样式设置"中可选择预设样式或自定义每个元素的颜色</p>
              </div>
            </div>
            <div class="flex gap-3">
              <span class="material-symbols-outlined text-secondary shrink-0">history</span>
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">历史记录</p>
                <p class="font-code-sm text-code-sm text-on-surface-variant text-xs">每次生成自动保存，点击历史记录可快速恢复之前的图表</p>
              </div>
            </div>
            <div class="flex gap-3">
              <span class="material-symbols-outlined text-secondary shrink-0">download</span>
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">导出图片</p>
                <p class="font-code-sm text-code-sm text-on-surface-variant text-xs">支持导出 SVG（矢量）和 PNG（位图）两种格式</p>
              </div>
            </div>
            <div class="flex gap-3">
              <span class="material-symbols-outlined text-secondary shrink-0">zoom_in</span>
              <div>
                <p class="font-label-mono text-label-mono text-on-surface">缩放和平移</p>
                <p class="font-code-sm text-code-sm text-on-surface-variant text-xs">底部工具栏支持放大、缩小、居中；拖拽节点时自动调整视图</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 设置 -->
        <section class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">settings</span>
            设置
          </h2>
          <p class="font-code-sm text-code-sm text-on-surface-variant text-sm">点击侧边栏"设置"进入设置页面，可配置 API Key、Base URL、模型，以及管理历史数据和样式。</p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
