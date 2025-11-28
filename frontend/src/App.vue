<template>
  <div id="app">
    <nav class="bg-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center space-x-8">
            <h1 class="text-2xl font-bold text-gray-800">Hyperliquid 跟单交易</h1>
            <nav class="hidden md:flex space-x-4">
              <router-link
                to="/"
                class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                active-class="text-blue-600 bg-blue-50"
              >
                Vaults
              </router-link>
              <router-link
                to="/my-trades"
                class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                active-class="text-blue-600 bg-blue-50"
              >
                交易历史
              </router-link>
              <router-link
                v-if="walletConnected"
                :to="`/account/${walletAddress}`"
                class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                active-class="text-blue-600 bg-blue-50"
              >
                账户管理
              </router-link>
            </nav>
          </div>
          <div class="flex items-center space-x-4">
            <button
              v-if="!walletConnected"
              @click="connectWallet"
              class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition"
            >
              连接钱包
            </button>
            <span v-else class="text-gray-700 font-mono">
              {{ walletAddress.slice(0, 6) }}...{{ walletAddress.slice(-4) }}
            </span>
          </div>
        </div>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const walletConnected = ref(false)
const walletAddress = ref('')

const connectWallet = async () => {
  // 这里实现钱包连接逻辑
  // 例如使用 MetaMask 或其他 Web3 钱包
  try {
    if (window.ethereum) {
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      })
      walletAddress.value = accounts[0]
      walletConnected.value = true
      // 保存到 localStorage
      localStorage.setItem('walletAddress', accounts[0])
      
      // 监听账户切换
      window.ethereum.on('accountsChanged', (newAccounts) => {
        if (newAccounts.length > 0) {
          walletAddress.value = newAccounts[0]
          localStorage.setItem('walletAddress', newAccounts[0])
        } else {
          walletAddress.value = ''
          walletConnected.value = false
          localStorage.removeItem('walletAddress')
        }
      })
    } else {
      alert('请安装 MetaMask 或其他 Web3 钱包')
    }
  } catch (error) {
    console.error('连接钱包失败:', error)
  }
}

// 页面加载时检查是否已连接钱包
const checkWalletConnection = () => {
  const savedAddress = localStorage.getItem('walletAddress')
  if (savedAddress && window.ethereum) {
    walletAddress.value = savedAddress
    walletConnected.value = true
  }
}

// 组件挂载时检查
onMounted(() => {
  checkWalletConnection()
})
</script>

<style scoped>
#app {
  min-height: 100vh;
}
</style>

