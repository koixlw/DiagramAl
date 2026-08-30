<template>
  <div class="bg-background text-on-background h-screen flex flex-col overflow-hidden font-body-md">
    <!-- TopNavBar -->
    <header class="bg-surface flex justify-between items-center w-full px-gutter h-16 border-b border-outline-variant shrink-0 relative z-10">
      <div class="flex items-center gap-4">
        <span class="font-headline-md text-headline-md font-bold text-primary cursor-pointer" @click="$router.push('/')">DiagramAI</span>
        <nav class="hidden md:flex gap-6 ml-8">
          <a class="text-secondary font-label-mono text-label-mono hover:bg-surface-container-low transition-colors px-2 py-1 rounded cursor-pointer" @click="$router.push('/flowchart')">流程图</a>
          <a class="text-primary font-label-mono text-label-mono border-b-2 border-primary hover:bg-surface-container-low transition-colors px-2 py-1 active:scale-95 duration-100 cursor-pointer" @click="$router.push('/er')">E-R 图</a>
        </nav>
      </div>
      <div class="flex items-center gap-4">
        <button class="text-primary hover:bg-surface-container-low transition-colors p-2 rounded-full">
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
            <textarea class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-24" placeholder="用户&#10;订单&#10;产品"></textarea>
          </div>
          <!-- Relationships Input -->
          <div class="flex flex-col gap-2 mt-2">
            <label class="font-label-mono text-label-mono text-on-surface-variant">关系 (Relationships)</label>
            <textarea class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-24" placeholder="用户 [下单 (1:N)] 订单&#10;订单 [包含 (M:N)] 产品"></textarea>
          </div>
          <!-- Attributes Input -->
          <div class="flex flex-col gap-2 mt-2">
            <label class="font-label-mono text-label-mono text-on-surface-variant">属性 (Attributes)</label>
            <textarea class="bg-surface-container-low border-none rounded-lg p-3 font-code-sm text-code-sm text-on-surface focus:ring-1 focus:ring-primary focus:bg-surface-container-lowest resize-none h-32" placeholder="用户: 编号 (PK), 名称, 邮箱&#10;订单: 订单号 (PK), 日期&#10;产品: 产品号 (PK), 价格"></textarea>
          </div>
          <button class="mt-4 bg-primary-container text-on-primary rounded-lg py-2 font-label-mono text-label-mono hover:opacity-90 transition-opacity">
            生成图表
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
      <main class="flex-1 dot-grid bg-surface-bright relative overflow-hidden flex items-center justify-center">
        <!-- Floating Toolbar -->
        <div class="absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-surface-container-lowest border border-outline-variant rounded-full px-4 py-2 flex gap-4 shadow-sm z-20">
          <button class="text-secondary hover:text-primary transition-colors flex items-center gap-1">
            <span class="material-symbols-outlined text-sm">zoom_in</span>
          </button>
          <button class="text-secondary hover:text-primary transition-colors flex items-center gap-1">
            <span class="material-symbols-outlined text-sm">zoom_out</span>
          </button>
          <div class="w-px bg-outline-variant h-4 my-auto"></div>
          <button class="text-secondary hover:text-primary transition-colors flex items-center gap-1">
            <span class="material-symbols-outlined text-sm">center_focus_strong</span>
          </button>
        </div>

        <!-- Canvas Content (Mockup of ER Diagram) -->
        <div class="relative w-full h-full" id="canvas-container">
          <!-- Connector Lines (SVG) -->
          <svg class="absolute inset-0 w-full h-full pointer-events-none z-0">
            <!-- User to Places -->
            <path d="M 350 250 L 450 250" fill="none" stroke="#cbd5e1" stroke-width="2"></path>
            <text class="font-code-sm text-xs fill-secondary" text-anchor="middle" x="400" y="240">1</text>
            <!-- Places to Order -->
            <path d="M 550 250 L 650 250" fill="none" stroke="#cbd5e1" stroke-width="2"></path>
            <text class="font-code-sm text-xs fill-secondary" text-anchor="middle" x="600" y="240">N</text>
            <!-- Order to Contains -->
            <path d="M 750 250 L 800 250 L 800 450 L 750 450" fill="none" stroke="#cbd5e1" stroke-width="2"></path>
            <!-- Actually let's just make it straight down for simplicity in this visual mockup -->
            <path d="M 700 280 L 700 350" fill="none" stroke="#cbd5e1" stroke-width="2"></path>
            <text class="font-code-sm text-xs fill-secondary" text-anchor="middle" x="715" y="315">M</text>
            <path d="M 700 450 L 700 500" fill="none" stroke="#cbd5e1" stroke-width="2"></path>
            <text class="font-code-sm text-xs fill-secondary" text-anchor="middle" x="715" y="475">N</text>
            <!-- User Attributes Links -->
            <path d="M 250 250 L 200 200" fill="none" stroke="#cbd5e1" stroke-width="1"></path>
            <path d="M 250 250 L 180 250" fill="none" stroke="#cbd5e1" stroke-width="1"></path>
            <path d="M 250 250 L 200 300" fill="none" stroke="#cbd5e1" stroke-width="1"></path>
          </svg>

          <!-- Entities and Relationships -->
          <!-- User Entity -->
          <div class="absolute top-[220px] left-[250px] w-24 h-14 bg-surface-container-lowest border-2 border-[#cbd5e1] flex items-center justify-center shadow-sm z-10 cursor-pointer hover:border-primary-fixed">
            <span class="font-diagram-text text-diagram-text text-on-surface">用户</span>
          </div>
          <!-- User Attributes -->
          <div class="absolute top-[175px] left-[130px] w-20 h-8 bg-surface-container-lowest border border-[#cbd5e1] rounded-[50%] flex items-center justify-center shadow-sm z-10">
            <span class="font-diagram-text text-diagram-text text-on-surface underline">编号</span>
          </div>
          <div class="absolute top-[234px] left-[100px] w-20 h-8 bg-surface-container-lowest border border-[#cbd5e1] rounded-[50%] flex items-center justify-center shadow-sm z-10">
            <span class="font-diagram-text text-diagram-text text-on-surface">名称</span>
          </div>
          <div class="absolute top-[290px] left-[130px] w-20 h-8 bg-surface-container-lowest border border-[#cbd5e1] rounded-[50%] flex items-center justify-center shadow-sm z-10">
            <span class="font-diagram-text text-diagram-text text-on-surface">邮箱</span>
          </div>
          <!-- Places Relationship -->
          <div class="absolute top-[220px] left-[450px] w-20 h-20 bg-surface-container-lowest border border-[#cbd5e1] transform rotate-45 flex items-center justify-center shadow-sm z-10">
            <span class="transform -rotate-45 font-diagram-text text-diagram-text text-on-surface text-sm">下单</span>
          </div>
          <!-- Order Entity -->
          <div class="absolute top-[220px] left-[650px] w-24 h-14 bg-surface-container-lowest border-2 border-[#cbd5e1] flex items-center justify-center shadow-sm z-10 cursor-pointer hover:border-primary-fixed">
            <span class="font-diagram-text text-diagram-text text-on-surface">订单</span>
          </div>
          <!-- Order Attributes -->
          <div class="absolute top-[160px] left-[610px] w-24 h-8 bg-surface-container-lowest border border-[#cbd5e1] rounded-[50%] flex items-center justify-center shadow-sm z-10">
            <span class="font-diagram-text text-diagram-text text-on-surface underline">订单号</span>
          </div>
          <!-- Link order attribute -->
          <svg class="absolute inset-0 w-full h-full pointer-events-none z-0">
            <path d="M 700 220 L 670 190" fill="none" stroke="#cbd5e1" stroke-width="1"></path>
          </svg>
          <!-- Contains Relationship -->
          <div class="absolute top-[380px] left-[660px] w-20 h-20 bg-surface-container-lowest border border-[#cbd5e1] transform rotate-45 flex items-center justify-center shadow-sm z-10">
            <span class="transform -rotate-45 font-diagram-text text-diagram-text text-on-surface text-sm">包含</span>
          </div>
          <!-- Product Entity -->
          <div class="absolute top-[520px] left-[650px] w-24 h-14 bg-surface-container-lowest border-2 border-[#cbd5e1] flex items-center justify-center shadow-sm z-10 cursor-pointer hover:border-primary-fixed">
            <span class="font-diagram-text text-diagram-text text-on-surface">产品</span>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
