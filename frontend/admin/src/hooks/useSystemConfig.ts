// Copyright 2024 CatWiki Authors
// 
// Licensed under the CatWiki Open Source License (Modified Apache 2.0);
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// 
//     https://github.com/CatWiki/CatWiki/blob/main/LICENSE
// 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * React Query hooks for System Config management
 */

import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api-client'
import type { AIConfigUpdate, BotConfigUpdate } from '@/lib/api-client'
import { isAuthenticated } from '@/lib/auth'
import { useAdminMutation } from './useAdminMutation'

// ==================== Query Keys ====================

export const systemConfigKeys = {
  all: ['systemConfig'] as const,
  aiConfig: () => [...systemConfigKeys.all, 'ai'] as const,
  botConfig: () => [...systemConfigKeys.all, 'bot'] as const,
  allConfigs: () => [...systemConfigKeys.all, 'all'] as const,
}

// ==================== Hooks ====================

/**
 * 获取 AI 模型配置
 */
export function useAIConfig() {
  const isAuth = isAuthenticated()

  return useQuery({
    queryKey: systemConfigKeys.aiConfig(),
    queryFn: () => api.systemConfig.getAIConfig(),
    enabled: isAuth,
    staleTime: 5 * 60 * 1000,
  })
}

/**
 * 获取机器人配置
 */
export function useBotConfig() {
  const isAuth = isAuthenticated()

  return useQuery({
    queryKey: systemConfigKeys.botConfig(),
    queryFn: () => api.systemConfig.getBotConfig(),
    enabled: isAuth,
    staleTime: 5 * 60 * 1000,
  })
}

/**
 * 获取所有配置
 */
export function useAllConfigs() {
  const isAuth = isAuthenticated()

  return useQuery({
    queryKey: systemConfigKeys.allConfigs(),
    queryFn: () => api.systemConfig.getAllConfigs(),
    enabled: isAuth,
    staleTime: 5 * 60 * 1000,
  })
}

/**
 * 更新 AI 模型配置
 */
export function useUpdateAIConfig() {
  return useAdminMutation({
    mutationFn: (config: AIConfigUpdate) => api.systemConfig.updateAIConfig(config),
    invalidateKeys: [systemConfigKeys.aiConfig(), systemConfigKeys.allConfigs()],
  })
}

/**
 * 更新机器人配置
 */
export function useUpdateBotConfig() {
  return useAdminMutation({
    mutationFn: (config: BotConfigUpdate) => api.systemConfig.updateBotConfig(config),
    invalidateKeys: [systemConfigKeys.botConfig(), systemConfigKeys.allConfigs()],
    successMsg: '机器人配置更新成功',
  })
}

/**
 * 删除指定配置
 */
export function useDeleteConfig() {
  return useAdminMutation({
    mutationFn: (configKey: string) => api.systemConfig.deleteConfig(configKey),
    invalidateKeys: [systemConfigKeys.allConfigs()],
    successMsg: '配置删除成功',
  })
}

/**
 * 测试模型连接
 */
export function useTestConnection() {
  return useMutation({
    mutationFn: (data: { modelType: string; config: any }) => api.systemConfig.testConnection(data.modelType, data.config),
  })
}






