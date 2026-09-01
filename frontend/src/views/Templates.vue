<template>
  <div class="bg-background text-on-background font-body-md h-screen flex flex-col overflow-hidden">
    <header class="bg-surface border-b border-outline-variant flex items-center w-full px-gutter h-16 shrink-0">
      <button @click="router.push('/')" class="flex items-center gap-2 text-primary hover:bg-surface-container-low rounded-lg px-3 py-1.5 transition-colors">
        <span class="material-symbols-outlined">arrow_back</span>
        <span class="font-headline-md font-bold">DiagramAI</span>
      </button>
      <span class="font-label-mono text-label-mono text-on-surface-variant ml-4">模板库</span>
    </header>

    <div class="flex-1 overflow-auto">
      <div class="max-w-5xl mx-auto p-6">
        <!-- 流程图模板 -->
        <section class="mb-8">
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">account_tree</span>
            流程图模板
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="t in flowchartTemplates" :key="t.name" @click="useTemplate(t, 'flowchart')" class="bg-surface-container-lowest border border-outline-variant rounded-xl p-4 cursor-pointer hover:border-primary hover:shadow-lg transition-all group">
              <div class="flex items-center justify-between mb-3">
                <span class="material-symbols-outlined text-secondary group-hover:text-primary transition-colors">{{ t.icon }}</span>
                <span class="material-symbols-outlined text-outline-variant group-hover:text-primary text-sm">arrow_forward</span>
              </div>
              <h3 class="font-label-mono text-label-mono font-bold text-on-surface mb-1">{{ t.name }}</h3>
              <p class="font-code-sm text-code-sm text-on-surface-variant text-xs">{{ t.desc }}</p>
              <div class="mt-3 flex gap-1">
                <span v-for="tag in t.tags" :key="tag" class="text-[10px] px-1.5 py-0.5 rounded bg-surface-container-low text-outline-variant">{{ tag }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- E-R 图模板 -->
        <section>
          <h2 class="font-label-mono text-label-mono font-bold text-on-surface mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">database</span>
            E-R 图模板
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="t in erTemplates" :key="t.name" @click="useTemplate(t, 'er')" class="bg-surface-container-lowest border border-outline-variant rounded-xl p-4 cursor-pointer hover:border-primary hover:shadow-lg transition-all group">
              <div class="flex items-center justify-between mb-3">
                <span class="material-symbols-outlined text-secondary group-hover:text-primary transition-colors">{{ t.icon }}</span>
                <span class="material-symbols-outlined text-outline-variant group-hover:text-primary text-sm">arrow_forward</span>
              </div>
              <h3 class="font-label-mono text-label-mono font-bold text-on-surface mb-1">{{ t.name }}</h3>
              <p class="font-code-sm text-code-sm text-on-surface-variant text-xs">{{ t.desc }}</p>
              <div class="mt-3 flex gap-1">
                <span v-for="tag in t.tags" :key="tag" class="text-[10px] px-1.5 py-0.5 rounded bg-surface-container-low text-outline-variant">{{ tag }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const flowchartTemplates = [
  { name: '质数判断', desc: '输入数字判断是否为质数', icon: 'calculate', tags: ['算法', '判断'], input: '判断一个数是否为质数：输入一个大于1的整数n，设置i=2，判断i是否小于等于根号n，如果n能被i整除则不是质数结束，否则i加1继续循环，如果循环结束都没找到因子则n是质数' },
  { name: '用户登录', desc: '用户登录验证流程', icon: 'login', tags: ['认证', '判断'], input: '用户登录流程：输入用户名和密码，验证格式是否正确，如果格式错误则提示重新输入，如果格式正确则查询数据库验证密码，密码正确则登录成功进入主页，密码错误则提示密码错误' },
  { name: '冒泡排序', desc: '冒泡排序算法流程', icon: 'sort', tags: ['算法', '循环'], input: '冒泡排序算法：输入一个数组，设置n为数组长度，从i=0到n-1循环，从j=0到n-i-1循环，比较相邻元素如果前一个大于后一个则交换，完成一轮后最大的元素移到最后，重复直到所有元素有序' },
  { name: '文件处理', desc: '读取、处理、保存文件', icon: 'description', tags: ['IO', '流程'], input: '文件处理流程：打开文件，检查文件是否存在，如果不存在则创建新文件，如果存在则读取内容，处理数据，保存结果，关闭文件，输出处理完成' },
  { name: '订单处理', desc: '电商订单完整流程', icon: 'shopping_cart', tags: ['电商', '业务'], input: '订单处理流程：用户提交订单，验证库存是否充足，如果库存不足则提示缺货结束，如果库存充足则扣减库存，生成订单号，调用支付接口，支付成功则更新订单状态为已支付，通知仓库发货，支付失败则取消订单恢复库存' },
  { name: '数据验证', desc: '表单数据验证流程', icon: 'fact_check', tags: ['验证', '判断'], input: '表单数据验证：接收用户输入，检查必填字段是否为空，如果为空则提示请填写，如果不为空则检查邮箱格式，格式错误则提示重新输入，格式正确则检查密码强度，强度不够则提示修改，所有验证通过则提交数据' },
]

const erTemplates = [
  { name: '学生选课', desc: '学生、课程、选课的ER关系', icon: 'school', tags: ['教育', '多对多'], input: '学生选课系统：学生有学号、姓名、邮箱、入学日期；课程有课程号、名称、学分；学生和课程是多对多的选课关系，包含选课日期和成绩' },
  { name: '电商系统', desc: '用户、商品、订单的ER关系', icon: 'shopping_bag', tags: ['电商', '一对多'], input: '电商系统：用户有用户ID、用户名、邮箱、手机号；商品有商品ID、商品名称、价格、库存数量；订单有订单ID、订单日期、总金额；用户和订单是一对多，订单和商品通过订单明细是多对多' },
  { name: '博客系统', desc: '用户、文章、评论的ER关系', icon: 'article', tags: ['社交', '一对多'], input: '博客系统：用户有用户ID、用户名、邮箱；文章有文章ID、标题、内容、发布时间；评论有评论ID、评论内容、评论时间；用户和文章是一对多，文章和评论是一对多，用户对评论是一对多' },
  { name: '图书管理', desc: '读者、图书、借阅的ER关系', icon: 'menu_book', tags: ['管理', '多对多'], input: '图书管理系统：读者有读者编号、姓名、手机号；图书有ISBN、书名、作者、出版社；借阅记录有记录编号、借阅日期、应还日期；读者和图书通过借阅记录是多对多关系' },
  { name: '员工管理', desc: '部门、员工、项目的ER关系', icon: 'groups', tags: ['企业', '多对多'], input: '员工管理系统：部门有部门编号、部门名称、办公地址；员工有员工ID、姓名、职位、入职日期；项目有项目ID、项目名称、开始日期；部门和员工是一对多，员工和项目是多对多的参与关系' },
  { name: '医院系统', desc: '患者、医生、科室的ER关系', icon: 'medical_services', tags: ['医疗', '多对多'], input: '医院管理系统：患者有患者ID、姓名、性别、出生日期；医生有医生ID、姓名、职称、所属科室；科室有科室编号、科室名称；挂号记录有挂号ID、挂号日期；患者和医生通过挂号是多对多关系' },
]

function useTemplate(template, type) {
  if (type === 'flowchart') {
    router.push('/flowchart')
    setTimeout(() => {
      const event = new CustomEvent('load-template', { detail: template.input })
      window.dispatchEvent(event)
    }, 300)
  } else {
    router.push('/er')
    setTimeout(() => {
      const event = new CustomEvent('load-template', { detail: template.input })
      window.dispatchEvent(event)
    }, 300)
  }
}
</script>
