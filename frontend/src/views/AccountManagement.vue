<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h2 class="text-3xl font-bold text-white mb-2">账户管理</h2>
      <p class="text-white/80 font-mono text-sm">{{ walletAddress }}</p>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      <p class="text-white mt-4">加载中...</p>
    </div>

    <div v-else-if="error" class="bg-red-500 text-white p-4 rounded-lg mb-4">
      {{ error }}
    </div>

    <div v-else>
      <!-- 账户概览 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="text-sm text-gray-600 mb-2">总资产</div>
          <div class="text-3xl font-bold text-gray-800">
            ${{ accountInfo.total_balance?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00' }}
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="text-sm text-gray-600 mb-2">可用余额</div>
          <div class="text-3xl font-bold text-blue-600">
            ${{ accountInfo.available_balance?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00' }}
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="text-sm text-gray-600 mb-2">总收益</div>
          <div
            :class="[
              'text-3xl font-bold',
              (accountInfo.total_profit || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            ]"
          >
            {{ (accountInfo.total_profit || 0) >= 0 ? '+' : '' }}${{ (accountInfo.total_profit || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="text-sm text-gray-600 mb-2">收益率</div>
          <div
            :class="[
              'text-3xl font-bold',
              (accountInfo.total_profit_rate || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            ]"
          >
            {{ (accountInfo.total_profit_rate || 0) >= 0 ? '+' : '' }}{{ (accountInfo.total_profit_rate || 0).toFixed(2) }}%
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="text-sm text-gray-600 mb-2">活跃持仓</div>
          <div class="text-2xl font-bold text-gray-800">
            {{ accountInfo.active_positions || 0 }}
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="text-sm text-gray-600 mb-2">总投入</div>
          <div class="text-2xl font-bold text-gray-800">
            ${{ accountInfo.total_deposited?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00' }}
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="text-sm text-gray-600 mb-2">已用保证金</div>
          <div class="text-2xl font-bold text-orange-600">
            ${{ ((accountInfo.total_balance || 0) - (accountInfo.available_balance || 0)).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </div>
        </div>
      </div>

      <!-- 持仓列表 -->
      <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h3 class="text-xl font-bold text-gray-800 mb-4">当前持仓</h3>
        <div v-if="accountInfo.positions && accountInfo.positions.length > 0">
          <div
            v-for="position in accountInfo.positions"
            :key="position.vault_address"
            class="border-b last:border-b-0 py-4"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h4 class="font-semibold text-gray-800">{{ position.vault_name }}</h4>
                <p class="text-sm text-gray-500 font-mono mt-1">{{ position.vault_address }}</p>
              </div>
              <div class="text-right">
                <div class="text-sm text-gray-600">持仓金额</div>
                <div class="text-lg font-semibold text-gray-800">${{ position.amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
              </div>
              <div class="text-right ml-6">
                <div class="text-sm text-gray-600">收益</div>
                <div
                  :class="[
                    'text-lg font-semibold',
                    position.profit >= 0 ? 'text-green-600' : 'text-red-600'
                  ]"
                >
                  {{ position.profit >= 0 ? '+' : '' }}${{ position.profit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </div>
                <div
                  :class="[
                    'text-sm',
                    position.profit_rate >= 0 ? 'text-green-600' : 'text-red-600'
                  ]"
                >
                  {{ position.profit_rate >= 0 ? '+' : '' }}{{ position.profit_rate.toFixed(2) }}%
                </div>
              </div>
              <div class="ml-6">
                <span
                  :class="[
                    'px-3 py-1 rounded text-sm font-semibold',
                    position.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  ]"
                >
                  {{ position.status === 'active' ? '进行中' : '已结束' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          暂无持仓
        </div>
      </div>

      <!-- 提取资金 -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">提取资金</h3>
        <form @submit.prevent="handleWithdraw" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              提取金额 (USDC)
            </label>
            <input
              v-model.number="withdrawAmount"
              type="number"
              step="0.01"
              min="0"
              :max="accountInfo.available_balance"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="输入提取金额"
            />
            <p class="text-sm text-gray-500 mt-1">
              可用余额: ${{ accountInfo.available_balance?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00' }}
            </p>
          </div>
          <button
            type="submit"
            :disabled="withdrawing || !withdrawAmount || withdrawAmount <= 0"
            class="w-full bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition"
          >
            {{ withdrawing ? '处理中...' : '确认提取' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { accountApi } from '../api'

const props = defineProps({
  walletAddress: {
    type: String,
    required: true
  }
})

const accountInfo = ref({})
const loading = ref(true)
const error = ref(null)
const withdrawAmount = ref(0)
const withdrawing = ref(false)

const fetchAccountInfo = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await accountApi.getAccountInfo(props.walletAddress)
    accountInfo.value = data
  } catch (err) {
    error.value = '加载账户信息失败，请稍后重试'
    console.error('Error fetching account info:', err)
  } finally {
    loading.value = false
  }
}

const handleWithdraw = async () => {
  if (withdrawAmount.value <= 0 || withdrawAmount.value > accountInfo.value.available_balance) {
    alert('提取金额无效')
    return
  }

  try {
    withdrawing.value = true
    const result = await accountApi.withdraw(props.walletAddress, withdrawAmount.value)
    alert('提取成功！交易哈希: ' + result.transaction_hash)
    withdrawAmount.value = 0
    // 重新加载账户信息
    await fetchAccountInfo()
  } catch (err) {
    alert('提取失败，请稍后重试')
    console.error('Error withdrawing:', err)
  } finally {
    withdrawing.value = false
  }
}

onMounted(() => {
  fetchAccountInfo()
})
</script>

