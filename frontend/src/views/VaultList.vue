<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h2 class="text-3xl font-bold text-white mb-2">Vaults 列表</h2>
      <p class="text-white/80">选择您想要跟单的交易策略</p>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      <p class="text-white mt-4">加载中...</p>
    </div>

    <div v-else-if="error" class="bg-red-500 text-white p-4 rounded-lg mb-4">
      {{ error }}
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="vault in vaults"
        :key="vault.address"
        class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition cursor-pointer"
        @click="goToDetail(vault.address)"
      >
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-xl font-bold text-gray-800">{{ vault.name }}</h3>
          <span
            :class="[
              'px-2 py-1 rounded text-sm font-semibold',
              vault.performance >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            ]"
          >
            {{ vault.performance >= 0 ? '+' : '' }}{{ vault.performance.toFixed(2) }}%
          </span>
        </div>
        
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex justify-between">
            <span>总资产:</span>
            <span class="font-semibold">${{ vault.total_value.toLocaleString() }}</span>
          </div>
          <div class="flex justify-between">
            <span>跟单人数:</span>
            <span class="font-semibold">{{ vault.user_count }}</span>
          </div>
          <div class="flex justify-between">
            <span>管理者分成:</span>
            <span class="font-semibold">{{ (vault.manager_share * 100).toFixed(1) }}%</span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t">
          <div class="text-xs text-gray-500 font-mono break-all">
            {{ vault.address }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="vaults.length === 0 && !loading" class="text-center py-12">
      <p class="text-white">暂无可用的 Vaults</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { vaultApi } from '../api'

const router = useRouter()
const vaults = ref([])
const loading = ref(true)
const error = ref(null)

const fetchVaults = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await vaultApi.getVaults()
    vaults.value = data
  } catch (err) {
    error.value = '加载 Vaults 失败，请稍后重试'
    console.error('Error fetching vaults:', err)
  } finally {
    loading.value = false
  }
}

const goToDetail = (address) => {
  router.push(`/vault/${address}`)
}

onMounted(() => {
  fetchVaults()
})
</script>

