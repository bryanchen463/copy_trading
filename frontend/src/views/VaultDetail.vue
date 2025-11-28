<template>
  <div class="container mx-auto px-4 py-8">
    <button
      @click="$router.back()"
      class="mb-4 text-white hover:text-gray-200 flex items-center"
    >
      ← 返回列表
    </button>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      <p class="text-white mt-4">加载中...</p>
    </div>

    <div v-else-if="error" class="bg-red-500 text-white p-4 rounded-lg">
      {{ error }}
    </div>

    <div v-else class="bg-white rounded-lg shadow-lg p-8">
      <div class="mb-6">
        <h2 class="text-3xl font-bold text-gray-800 mb-2">{{ vaultInfo.name || 'Vault 详情' }}</h2>
        <p class="text-gray-600 font-mono text-sm break-all">{{ address }}</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-gray-50 p-4 rounded-lg">
          <div class="text-sm text-gray-600 mb-1">总资产</div>
          <div class="text-2xl font-bold text-gray-800">
            ${{ vaultInfo.total_value?.toLocaleString() || '0' }}
          </div>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg">
          <div class="text-sm text-gray-600 mb-1">收益率</div>
          <div
            :class="[
              'text-2xl font-bold',
              (vaultInfo.performance || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            ]"
          >
            {{ (vaultInfo.performance || 0) >= 0 ? '+' : '' }}{{ (vaultInfo.performance || 0).toFixed(2) }}%
          </div>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg">
          <div class="text-sm text-gray-600 mb-1">跟单人数</div>
          <div class="text-2xl font-bold text-gray-800">
            {{ vaultInfo.user_count || 0 }}
          </div>
        </div>
      </div>

      <!-- 跟单表单 -->
      <div class="border-t pt-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">开始跟单</h3>
        <form @submit.prevent="handleCopyTrade" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              跟单金额 (USDC)
            </label>
            <input
              v-model.number="copyAmount"
              type="number"
              step="0.01"
              min="0"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="输入跟单金额"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              杠杆倍数
            </label>
            <input
              v-model.number="leverage"
              type="number"
              step="0.1"
              min="1"
              max="20"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="1.0"
            />
          </div>
          <button
            type="submit"
            :disabled="submitting"
            class="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition"
          >
            {{ submitting ? '提交中...' : '确认跟单' }}
          </button>
        </form>
      </div>

      <!-- 交易历史 -->
      <div class="border-t pt-6 mt-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">交易历史</h3>
        <div v-if="tradesLoading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400"></div>
        </div>
        <div v-else-if="trades.length === 0" class="text-center py-8 text-gray-500">
          暂无交易记录
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">交易对</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">方向</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">数量</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">价格</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="trade in trades" :key="trade.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatTime(trade.timestamp) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ trade.symbol }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 rounded text-xs font-semibold',
                      trade.side === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    ]"
                  >
                    {{ trade.side === 'buy' ? '买入' : '卖出' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ trade.size }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{ trade.price }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { vaultApi } from '../api'

const route = useRoute()
const address = route.params.address

const vaultInfo = ref({})
const trades = ref([])
const loading = ref(true)
const tradesLoading = ref(false)
const error = ref(null)
const copyAmount = ref(0)
const leverage = ref(1.0)
const submitting = ref(false)

const fetchVaultDetail = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await vaultApi.getVaultDetail(address)
    vaultInfo.value = data
  } catch (err) {
    error.value = '加载 Vault 详情失败'
    console.error('Error fetching vault detail:', err)
  } finally {
    loading.value = false
  }
}

const fetchTrades = async () => {
  try {
    tradesLoading.value = true
    const data = await vaultApi.getVaultTrades(address)
    trades.value = data.trades || []
  } catch (err) {
    console.error('Error fetching trades:', err)
  } finally {
    tradesLoading.value = false
  }
}

const getWalletAddress = () => {
  if (window.ethereum && window.ethereum.selectedAddress) {
    return window.ethereum.selectedAddress
  }
  return localStorage.getItem('walletAddress') || ''
}

const handleCopyTrade = async () => {
  const walletAddress = getWalletAddress()
  if (!walletAddress) {
    alert('请先连接钱包')
    return
  }

  try {
    submitting.value = true
    const result = await vaultApi.createCopyTrade({
      vault_address: address,
      amount: copyAmount.value,
      leverage: leverage.value,
      wallet_address: walletAddress
    })
    alert('跟单交易创建成功！')
    console.log('Copy trade result:', result)
    // 重置表单
    copyAmount.value = 0
    leverage.value = 1.0
  } catch (err) {
    alert('跟单交易创建失败，请稍后重试')
    console.error('Error creating copy trade:', err)
  } finally {
    submitting.value = false
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp * 1000).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchVaultDetail()
  fetchTrades()
})
</script>

