import { apiClient } from './client'
import type { StatsResponse } from '@/types/analyze'

export async function fetchStats(): Promise<StatsResponse> {
  const { data } = await apiClient.get<StatsResponse>('/api/stats')
  return data
}
