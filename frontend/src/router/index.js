import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: '首页',
      icon: 'House'
    }
  },
  {
    path: '/documents',
    name: 'Documents',
    component: () => import('@/views/Documents.vue'),
    meta: {
      title: '文档管理',
      icon: 'Document'
    }
  },
  {
    path: '/testcases',
    name: 'TestCases',
    component: () => import('@/views/TestCases.vue'),
    meta: {
      title: '测试用例',
      icon: 'List'
    }
  },
  {
    path: '/mindmaps',
    name: 'MindMaps',
    component: () => import('@/views/MindMaps.vue'),
    meta: {
      title: '思维导图',
      icon: 'Share'
    }
  },
  {
    path: '/testcases/:id',
    name: 'TestCaseDetail',
    component: () => import('@/views/TestCaseDetail.vue'),
    meta: {
      title: '测试用例详情',
      hidden: true
    }
  },
  {
    path: '/mindmaps/:id',
    name: 'MindMapDetail',
    component: () => import('@/views/MindMapDetail.vue'),
    meta: {
      title: '思维导图详情',
      hidden: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面不存在',
      hidden: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  // Set page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - AItestdemo`
  }

  // TODO: Add authentication logic
  next()
})

router.afterEach(() => {
  // Scroll to top
  window.scrollTo(0, 0)
})

export default router