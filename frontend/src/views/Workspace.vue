<template>
  <div class="bg-background text-on-background font-body-md h-screen w-screen overflow-hidden flex">
    <!-- SideNavBar -->
    <nav class="bg-surface-container-low border-r border-outline-variant flex flex-col h-full py-node_padding px-4 gap-stack_gap w-sidebar_width flex-shrink-0 z-20 relative">
      <div class="mb-8 px-2">
        <h1 class="font-headline-md text-headline-md text-primary font-bold">DiagramAI</h1>
        <p class="font-label-mono text-label-mono text-secondary">AI Architect</p>
      </div>
      <div class="flex-1 flex flex-col gap-2">
        <!-- Active Tab: 流程图 -->
        <router-link
          to="/flowchart"
          class="bg-secondary-container text-on-secondary-container rounded-lg font-bold flex items-center gap-3 px-4 py-3 transition-all active:scale-95 duration-100"
        >
          <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">account_tree</span>
          <span class="font-label-mono text-label-mono">流程图</span>
        </router-link>
        <!-- Inactive Tab: E-R图 -->
        <router-link
          to="/er"
          class="text-on-surface-variant hover:bg-surface-variant rounded-lg flex items-center gap-3 px-4 py-3 transition-all"
        >
          <span class="material-symbols-outlined">database</span>
          <span class="font-label-mono text-label-mono">E-R图</span>
        </router-link>
      </div>
      <div class="mt-auto border-t border-outline-variant pt-4 flex flex-col gap-2">
        <a class="text-on-surface-variant hover:bg-surface-variant rounded-lg flex items-center gap-3 px-4 py-3 transition-all cursor-pointer" href="#">
          <span class="material-symbols-outlined">settings</span>
          <span class="font-label-mono text-label-mono">设置</span>
        </a>
        <a class="text-on-surface-variant hover:bg-surface-variant rounded-lg flex items-center gap-3 px-4 py-3 transition-all cursor-pointer" href="#">
          <span class="material-symbols-outlined">help</span>
          <span class="font-label-mono text-label-mono">文档</span>
        </a>
      </div>
    </nav>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 bg-surface-bright relative z-10">
      <!-- TopNavBar -->
      <header class="bg-surface border-b border-outline-variant flex justify-between items-center w-full px-gutter h-16 flex-shrink-0 z-20">
        <div class="flex items-center gap-4">
          <span class="font-label-mono text-label-mono text-secondary">Workspace / Flowcharts</span>
        </div>
        <div class="flex items-center gap-2 text-primary">
          <button class="p-2 hover:bg-surface-container-low transition-colors rounded-full flex items-center justify-center">
            <span class="material-symbols-outlined">download</span>
          </button>
          <button class="p-2 hover:bg-surface-container-low transition-colors rounded-full flex items-center justify-center">
            <span class="material-symbols-outlined">share</span>
          </button>
          <button class="p-2 hover:bg-surface-container-low transition-colors rounded-full flex items-center justify-center">
            <span class="material-symbols-outlined">code</span>
          </button>
          <div class="ml-4 w-8 h-8 bg-primary-container text-on-primary-container rounded-full flex items-center justify-center font-bold text-sm">
            AI
          </div>
        </div>
      </header>

      <!-- Canvas Area -->
      <main class="flex-1 overflow-auto relative dot-grid p-canvas_margin">
        <div class="max-w-6xl mx-auto space-y-8">
          <!-- Welcome Section -->
          <section>
            <h2 class="font-headline-lg text-headline-lg text-on-background mb-2">欢迎回来，架构师</h2>
            <p class="text-on-surface-variant">选择一个模块开始生成高保真逻辑结构。</p>
          </section>

          <!-- Modules Grid -->
          <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Flowchart Card -->
            <div
              class="bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden hover:border-primary hover:shadow-lg transition-all duration-300 group cursor-pointer flex flex-col relative"
              @click="$router.push('/flowchart')"
            >
              <div class="h-48 bg-surface-container-low flex items-center justify-center relative overflow-hidden border-b border-outline-variant">
                <div class="absolute inset-0 opacity-20 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PHBhdGggZD0iTTIwIDAgTDIwIDQwIE0wIDIwIEw0MCAyMCIgc3Ryb2tlPSIjY2JkNWUxIiBzdHJva2Utd2lkdGg9IjEiLz48L3N2Zz4=')]"></div>
                <div class="relative flex flex-col items-center gap-4">
                  <div class="w-24 h-12 border-2 border-primary bg-surface-container-lowest rounded flex items-center justify-center font-code-sm text-code-sm text-primary shadow-sm z-10">Start</div>
                  <div class="w-[2px] h-8 bg-outline-variant"></div>
                  <div class="w-20 h-20 border-2 border-tertiary-container bg-surface-container-lowest rotate-45 flex items-center justify-center shadow-sm z-10">
                    <span class="-rotate-45 font-code-sm text-code-sm text-tertiary-container">Check</span>
                  </div>
                </div>
              </div>
              <div class="p-6 flex-1 flex flex-col">
                <h3 class="font-headline-md text-headline-md mb-2 flex items-center justify-between">
                  流程图
                  <span class="material-symbols-outlined text-primary opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-[-10px] group-hover:translate-x-0 duration-300">arrow_forward</span>
                </h3>
                <p class="text-on-surface-variant text-sm mb-6 flex-1">在 AI 辅助下生成复杂的业务工作流、决策树和过程逻辑。</p>
                <button class="bg-primary text-on-primary font-label-mono text-label-mono py-2 px-4 rounded hover:bg-primary-container transition-colors w-full text-center">
                  创建新流程图
                </button>
              </div>
            </div>

            <!-- ER Diagram Card -->
            <div
              class="bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden hover:border-primary hover:shadow-lg transition-all duration-300 group cursor-pointer flex flex-col relative"
              @click="$router.push('/er')"
            >
              <div class="h-48 bg-surface-container-low flex items-center justify-center relative overflow-hidden border-b border-outline-variant">
                <div class="absolute inset-0 opacity-20 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PHBhdGggZD0iTTIwIDAgTDIwIDQwIE0wIDIwIEw0MCAyMCIgc3Ryb2tlPSIjY2JkNWUxIiBzdHJva2Utd2lkdGg9IjEiLz48L3N2Zz4=')]"></div>
                <div class="relative flex items-center justify-center w-full h-full">
                  <div class="border-2 border-secondary bg-surface-container-lowest rounded-md w-32 shadow-sm z-10 flex flex-col overflow-hidden">
                    <div class="bg-secondary-fixed-dim border-b border-secondary px-2 py-1 font-label-mono text-code-sm text-on-secondary-container font-bold text-center">User</div>
                    <div class="px-2 py-1 font-code-sm text-code-sm text-on-surface-variant border-b border-outline-variant underline">id : INT</div>
                    <div class="px-2 py-1 font-code-sm text-code-sm text-on-surface-variant">name : VARCHAR</div>
                  </div>
                </div>
              </div>
              <div class="p-6 flex-1 flex flex-col">
                <h3 class="font-headline-md text-headline-md mb-2 flex items-center justify-between">
                  E-R图
                  <span class="material-symbols-outlined text-primary opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-[-10px] group-hover:translate-x-0 duration-300">arrow_forward</span>
                </h3>
                <p class="text-on-surface-variant text-sm mb-6 flex-1">精准规划数据库模式、实体关系和属性结构。</p>
                <button class="bg-surface text-primary border border-outline-variant font-label-mono text-label-mono py-2 px-4 rounded hover:bg-surface-container-low transition-colors w-full text-center">
                  创建新 E-R 图
                </button>
              </div>
            </div>
          </section>

          <!-- Recent & Templates Split -->
          <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Recent Projects -->
            <div class="lg:col-span-2 bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-label-mono text-label-mono font-bold text-on-background">最近的架构</h3>
                <button class="text-primary font-label-mono text-code-sm hover:underline">查看全部</button>
              </div>
              <div class="space-y-2">
                <!-- List Item 1 -->
                <div class="flex items-center justify-between p-3 hover:bg-surface-container-low rounded-lg transition-colors cursor-pointer border border-transparent hover:border-outline-variant group">
                  <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-secondary-container text-on-secondary-container rounded flex items-center justify-center">
                      <span class="material-symbols-outlined text-sm">account_tree</span>
                    </div>
                    <div>
                      <h4 class="font-diagram-text text-diagram-text font-bold text-on-background">身份验证流程</h4>
                      <p class="font-code-sm text-code-sm text-on-surface-variant">流程图 &bull; 2小时前编辑</p>
                    </div>
                  </div>
                  <button class="opacity-0 group-hover:opacity-100 text-secondary hover:text-primary transition-all">
                    <span class="material-symbols-outlined">more_horiz</span>
                  </button>
                </div>
                <!-- List Item 2 -->
                <div class="flex items-center justify-between p-3 hover:bg-surface-container-low rounded-lg transition-colors cursor-pointer border border-transparent hover:border-outline-variant group">
                  <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-tertiary-container text-on-tertiary-container rounded flex items-center justify-center">
                      <span class="material-symbols-outlined text-sm">database</span>
                    </div>
                    <div>
                      <h4 class="font-diagram-text text-diagram-text font-bold text-on-background">电商架构 v2</h4>
                      <p class="font-code-sm text-code-sm text-on-surface-variant">E-R图 &bull; 昨天编辑</p>
                    </div>
                  </div>
                  <button class="opacity-0 group-hover:opacity-100 text-secondary hover:text-primary transition-all">
                    <span class="material-symbols-outlined">more_horiz</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Templates -->
            <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-label-mono text-label-mono font-bold text-on-background">快速开始</h3>
              </div>
              <div class="flex flex-col gap-3">
                <button class="flex items-center gap-3 p-3 border border-outline-variant rounded-lg hover:border-primary hover:bg-surface-container-low transition-all text-left">
                  <span class="material-symbols-outlined text-secondary">add_circle</span>
                  <span class="font-diagram-text text-diagram-text text-on-background">空白画布</span>
                </button>
                <button class="flex items-center gap-3 p-3 border border-outline-variant rounded-lg hover:border-primary hover:bg-surface-container-low transition-all text-left">
                  <span class="material-symbols-outlined text-secondary">view_agenda</span>
                  <span class="font-diagram-text text-diagram-text text-on-background">微服务模板</span>
                </button>
                <button class="flex items-center gap-3 p-3 border border-outline-variant rounded-lg hover:border-primary hover:bg-surface-container-low transition-all text-left">
                  <span class="material-symbols-outlined text-secondary">schema</span>
                  <span class="font-diagram-text text-diagram-text text-on-background">用户 RBAC E-R图</span>
                </button>
              </div>
            </div>
          </section>

          <!-- Footer -->
          <footer class="mt-12 bg-surface-container-lowest border-t border-outline-variant flex justify-between items-center px-gutter py-2 text-xs rounded-b-xl shadow-sm">
            <span class="text-secondary font-label-mono text-label-mono">&copy; 2024 DiagramAI Engine</span>
            <div class="flex gap-4">
              <a class="text-secondary-fixed-variant hover:text-primary transition-colors opacity-80 hover:opacity-100 font-label-mono text-label-mono" href="#">隐私</a>
              <a class="text-secondary-fixed-variant hover:text-primary transition-colors opacity-80 hover:opacity-100 font-label-mono text-label-mono" href="#">条款</a>
              <a class="text-secondary-fixed-variant hover:text-primary transition-colors opacity-80 hover:opacity-100 font-label-mono text-label-mono" href="#">API</a>
            </div>
          </footer>
        </div>
      </main>
    </div>
  </div>
</template>
