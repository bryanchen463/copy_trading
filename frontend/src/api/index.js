import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等认证信息
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

// API 方法
export const vaultApi = {
  // 获取所有 Vaults
  getVaults: () => api.get('/vaults'),
  
  // 获取 Vault 详情
  getVaultDetail: (address) => api.get(`/vaults/${address}`),
  
  // 获取 Vault 交易历史
  getVaultTrades: (address) => api.get(`/vaults/${address}/trades`),
  
  // 创建跟单交易
  createCopyTrade: (data) => api.post('/copy-trade', data)
}

// 账户管理 API
export const accountApi = {
  // 获取账户信息
  getAccountInfo: (walletAddress) => api.get(`/account/${walletAddress}`),
  
  // 获取账户交易历史
  getAccountTrades: (walletAddress, params = {}) => {
    const queryParams = new URLSearchParams()
    if (params.vault_address) queryParams.append('vault_address', params.vault_address)
    if (params.start_time) queryParams.append('start_time', params.start_time)
    if (params.end_time) queryParams.append('end_time', params.end_time)
    if (params.limit) queryParams.append('limit', params.limit)
    const query = queryParams.toString()
    return api.get(`/account/${walletAddress}/trades${query ? '?' + query : ''}`)
  },
  
  // 提取资金
  withdraw: (walletAddress, amount) => api.post(`/account/${walletAddress}/withdraw`, { amount })
}

