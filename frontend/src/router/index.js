import { createRouter, createWebHistory } from 'vue-router'
import VaultList from '../views/VaultList.vue'
import VaultDetail from '../views/VaultDetail.vue'
import MyTrades from '../views/MyTrades.vue'
import AccountManagement from '../views/AccountManagement.vue'

const routes = [
  {
    path: '/',
    name: 'VaultList',
    component: VaultList
  },
  {
    path: '/vault/:address',
    name: 'VaultDetail',
    component: VaultDetail,
    props: true
  },
  {
    path: '/my-trades',
    name: 'MyTrades',
    component: MyTrades
  },
  {
    path: '/account/:walletAddress',
    name: 'AccountManagement',
    component: AccountManagement,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

