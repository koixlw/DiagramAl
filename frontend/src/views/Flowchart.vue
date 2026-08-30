<template>
  <div class="bg-background text-on-background font-body-md text-body-md h-screen flex flex-col overflow-hidden">
    <!-- TopNavBar -->
    <header class="bg-surface border-b border-outline-variant flex justify-between items-center w-full px-gutter h-16 flex-shrink-0 z-50">
      <div class="flex items-center gap-4">
        <span class="font-headline-md text-headline-md font-bold text-primary cursor-pointer" @click="$router.push('/')">DiagramAI</span>
        <nav class="hidden md:flex gap-6 ml-8">
          <a class="text-primary border-b-2 border-primary pb-1 flex items-center gap-2 hover:bg-surface-container-low transition-colors active:scale-95 duration-100 cursor-pointer" @click="$router.push('/flowchart')">
            <span class="material-symbols-outlined">account_tree</span> 流程图
          </a>
          <a class="text-secondary pb-1 flex items-center gap-2 hover:bg-surface-container-low transition-colors active:scale-95 duration-100 cursor-pointer" @click="$router.push('/er')">
            <span class="material-symbols-outlined">database</span> E-R 图
          </a>
        </nav>
      </div>
      <div class="flex items-center gap-2">
        <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" title="Download">
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
      <aside class="w-sidebar_width bg-surface-container-low border-r border-outline-variant flex flex-col z-40 flex-shrink-0 transition-transform duration-300 md:translate-x-0 -translate-x-full absolute md:relative h-full">
        <div class="p-4 flex flex-col gap-4 flex-1 overflow-y-auto">
          <div>
            <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-2">处理逻辑 (Process Logic)</h2>
            <textarea
              class="w-full h-40 p-3 bg-surface-container-lowest border border-outline-variant rounded focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary font-code-sm text-code-sm resize-none text-on-surface"
              placeholder="在此输入逻辑，例如：&#10;如果支付成功 -> 发送邮件&#10;如果支付失败 -> 提示重试"
            >用户发起请求
验证用户身份
如果 验证成功 -> 查询数据库
    如果 数据存在 -> 返回结果 -> 结束
    如果 数据不存在 -> 提示错误 -> 结束
如果 验证失败 -> 拒绝访问 -> 结束</textarea>
          </div>
          <button class="w-full py-2 bg-primary-container text-on-primary rounded hover:bg-primary transition-colors font-label-mono text-label-mono font-bold flex items-center justify-center gap-2 shadow-sm">
            <span class="material-symbols-outlined">auto_awesome</span>
            重新生成图表
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
        <!-- Toolbar -->
        <div class="absolute bottom-6 left-1/2 -translate-x-1/2 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-sm flex items-center gap-1 p-1 z-10">
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" title="Zoom Out">
            <span class="material-symbols-outlined">remove</span>
          </button>
          <span class="font-label-mono text-label-mono text-on-surface-variant w-12 text-center">100%</span>
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors" title="Zoom In">
            <span class="material-symbols-outlined">add</span>
          </button>
          <div class="w-px h-6 bg-outline-variant mx-1"></div>
          <button class="p-2 text-primary hover:bg-surface-container-low rounded transition-colors" title="Toggle Grid">
            <span class="material-symbols-outlined">grid_on</span>
          </button>
          <div class="w-px h-6 bg-outline-variant mx-1"></div>
          <button class="p-2 text-secondary hover:bg-surface-container-low rounded transition-colors flex items-center gap-1 pr-3" title="Center View">
            <span class="material-symbols-outlined">filter_center_focus</span>
            <span class="font-label-mono text-xs hidden sm:inline">居中</span>
          </button>
        </div>

        <!-- Canvas Area (Simulated Flowchart) -->
        <div class="flex-1 relative w-full h-full overflow-auto p-8 flex items-center justify-center min-h-[600px] min-w-[800px]">
          <div class="relative w-[600px] h-[500px]">
            <!-- Nodes -->
            <!-- Start Node -->
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[120px] h-[40px] border-2 border-outline rounded-full bg-surface-container-lowest flex items-center justify-center font-diagram-text text-diagram-text text-on-surface z-10 shadow-sm cursor-pointer hover:border-primary transition-colors">
              用户发起请求
            </div>
            <!-- Process Node 1 -->
            <div class="absolute top-[100px] left-1/2 -translate-x-1/2 w-[140px] h-[48px] border-2 border-outline bg-surface-container-lowest flex items-center justify-center font-diagram-text text-diagram-text text-on-surface z-10 shadow-sm cursor-pointer hover:border-primary transition-colors">
              验证用户身份
            </div>
            <!-- Decision Node 1 -->
            <div class="absolute top-[200px] left-1/2 -translate-x-1/2 w-[100px] h-[100px] border-2 border-outline transform rotate-45 bg-surface-container-lowest flex items-center justify-center z-10 shadow-sm cursor-pointer hover:border-primary transition-colors ring-2 ring-primary ring-offset-2 ring-offset-surface-bright">
              <span class="transform -rotate-45 font-diagram-text text-diagram-text text-on-surface">验证成功？</span>
            </div>
            <!-- Process Node 2 (Left Branch) -->
            <div class="absolute top-[350px] left-[100px] -translate-x-1/2 w-[140px] h-[48px] border-2 border-outline bg-surface-container-lowest flex items-center justify-center font-diagram-text text-diagram-text text-on-surface z-10 shadow-sm cursor-pointer hover:border-primary transition-colors">
              查询数据库
            </div>
            <!-- Process Node 3 (Right Branch) -->
            <div class="absolute top-[350px] left-[500px] -translate-x-1/2 w-[120px] h-[48px] border-2 border-outline bg-surface-container-lowest flex items-center justify-center font-diagram-text text-diagram-text text-on-surface z-10 shadow-sm cursor-pointer hover:border-primary transition-colors">
              拒绝访问
            </div>
            <!-- End Node (Left) -->
            <div class="absolute top-[460px] left-[100px] -translate-x-1/2 w-[100px] h-[40px] border-2 border-outline rounded-full bg-surface-container-lowest flex items-center justify-center font-diagram-text text-diagram-text text-on-surface z-10 shadow-sm cursor-pointer hover:border-primary transition-colors">
              结束
            </div>
            <!-- End Node (Right) -->
            <div class="absolute top-[460px] left-[500px] -translate-x-1/2 w-[100px] h-[40px] border-2 border-outline rounded-full bg-surface-container-lowest flex items-center justify-center font-diagram-text text-diagram-text text-on-surface z-10 shadow-sm cursor-pointer hover:border-primary transition-colors">
              结束
            </div>
            <!-- Edges / Connectors (SVG for clean lines) -->
            <svg class="absolute top-0 left-0 w-full h-full pointer-events-none" style="z-index: 0;">
              <defs>
                <marker id="arrow" markerheight="6" markerwidth="6" orient="auto-start-reverse" refx="8" refy="5" viewbox="0 0 10 10">
                  <path class="fill-outline" d="M 0 0 L 10 5 L 0 10 z"></path>
                </marker>
                <marker id="arrow-active" markerheight="6" markerwidth="6" orient="auto-start-reverse" refx="8" refy="5" viewbox="0 0 10 10">
                  <path class="fill-primary" d="M 0 0 L 10 5 L 0 10 z"></path>
                </marker>
              </defs>
              <!-- Start to Process 1 -->
              <path class="stroke-outline" d="M 300 40 L 300 100" fill="none" marker-end="url(#arrow)" stroke-width="2"></path>
              <!-- Process 1 to Decision -->
              <path class="stroke-outline" d="M 300 148 L 300 200" fill="none" marker-end="url(#arrow)" stroke-width="2"></path>
              <!-- Decision to Left (Yes) -->
              <path class="stroke-primary" d="M 250 250 L 100 250 L 100 350" fill="none" marker-end="url(#arrow-active)" stroke-width="2"></path>
              <!-- Decision to Right (No) -->
              <path class="stroke-outline" d="M 350 250 L 500 250 L 500 350" fill="none" marker-end="url(#arrow)" stroke-width="2"></path>
              <!-- Left Process to End -->
              <path class="stroke-outline" d="M 100 398 L 100 460" fill="none" marker-end="url(#arrow)" stroke-width="2"></path>
              <!-- Right Process to End -->
              <path class="stroke-outline" d="M 500 398 L 500 460" fill="none" marker-end="url(#arrow)" stroke-width="2"></path>
            </svg>
            <!-- Edge Labels -->
            <div class="absolute top-[230px] left-[170px] bg-surface-container-lowest px-1 rounded font-diagram-text text-[11px] text-primary z-20 shadow-sm border border-outline-variant">是</div>
            <div class="absolute top-[230px] left-[400px] bg-surface-bright px-1 rounded font-diagram-text text-[11px] text-on-surface-variant z-20">否</div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
