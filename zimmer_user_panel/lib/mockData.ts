export interface Automation {
  id: number
  name: string
  description: string
  status: 'active' | 'inactive' | 'expired'
  purchaseDate?: string
  expiryDate?: string
  usage?: number
  maxUsage?: number
}

export interface TokenUsage {
  used: number
  remaining: number
  total: number
}

