<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h2 class="text-3xl font-bold text-white mb-2">交易历史</h2>
      <p class="text-white/80">查看您的所有跟单交易记录</p>
    </div>

    <!-- 筛选器 -->
    <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Vault 地址</label>
          <input
            v-model="filters.vault_address"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="筛选 Vault"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">开始时间</label>
          <input
            v-model="filters.start_time"
            type="date"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">结束时间</label>
          <input
            v-model="filters.end_time"
            type="date"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div class="flex items-end">
          <button
            @click="applyFilters"
            class="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition"
          >
            筛选
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      <p class="text-white mt-4">加载中...</p>
    </div>

    <div v-else-if="error" class="bg-red-500 text-white p-4 rounded-lg mb-4">
      {{ error }}
    </div>

    <div v-else-if="trades.length === 0" class="bg-white rounded-lg shadow-lg p-8 text-center">
      <p class="text-gray-600 text-lg">您还没有跟单记录</p>
      <router-link
        to="/"
        class="mt-4 inline-block bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition"
      >
        去选择 Vault
      </router-link>
    </div>

    <div v-else>
      <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vault</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">类型</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">金额</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">杠杆</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">收益</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">收益率</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="trade in trades" :key="trade.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatTime(trade.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ trade.vault_name || 'Unknown' }}</div>
                    <div class="text-sm text-gray-500 font-mono">{{ trade.vault_address?.slice(0, 10) }}...</div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ trade.type === 'copy_trade' ? '跟单交易' : trade.type }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${{ trade.amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ trade.leverage }}x
                </td>
                <td
                  :class="[
                    'px-6 py-4 whitespace-nowrap text-sm font-semibold',
                    (trade.profit || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                  ]"
                >
                  {{ (trade.profit || 0) >= 0 ? '+' : '' }}${{ (trade.profit || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </td>
                <td
                  :class="[
                    'px-6 py-4 whitespace-nowrap text-sm font-semibold',
                    (trade.profit_rate || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                  ]"
                >
                  {{ (trade.profit_rate || 0) >= 0 ? '+' : '' }}{{ (trade.profit_rate || 0).toFixed(2) }}%
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 rounded text-xs font-semibold',
                      trade.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    ]"
                  >
                    {{ trade.status === 'active' ? '进行中' : '已结束' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="total > trades.length" class="bg-gray-50 px-6 py-4 border-t">
          <p class="text-sm text-gray-600">显示 {{ trades.length }} / {{ total }} 条记录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { accountApi } from '../api'

// 从 localStorage 或全局状态获取钱包地址
// 这里简化处理，实际应该从 App.vue 或 store 获取
const getWalletAddress = () => {
  // 尝试从 window.ethereum 获取
  if (window.ethereum && window.ethereum.selectedAddress) {
    return window.ethereum.selectedAddress
  }
  // 或者从 localStorage 获取
  return localStorage.getItem('walletAddress') || ''
}

const walletAddress = ref(getWalletAddress())
const trades = ref([])
const loading = ref(true)
const error = ref(null)
const total = ref(0)
const filters = ref({
  vault_address: '',
  start_time: '',
  end_time: ''
})

const fetchMyTrades = async () => {
  if (!walletAddress.value) {
    error.value = '请先连接钱包'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = null
    
    const params = {}
    if (filters.value.vault_address) {
      params.vault_address = filters.value.vault_address
    }
    if (filters.value.start_time) {
      params.start_time = Math.floor(new Date(filters.value.start_time).getTime() / 1000)
    }
    if (filters.value.end_time) {
      params.end_time = Math.floor(new Date(filters.value.end_time).getTime() / 1000)
    }
    params.limit = 100

    const data = await accountApi.getAccountTrades(walletAddress.value, params)
    trades.value = data.trades || []
    total.value = data.total || trades.value.length
  } catch (err) {
    error.value = '加载交易历史失败，请稍后重试'
    console.error('Error fetching my trades:', err)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  fetchMyTrades()
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp * 1000).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchMyTrades()
})
</script>

