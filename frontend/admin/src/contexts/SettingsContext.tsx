// Copyright 2026 CatWiki Authors
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
 * 设置页面的状态管理 Context
 * 统一管理配置状态、更新逻辑和保存操作
 */

"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { toast } from "sonner"
import { useAIConfig, useUpdateAIConfig } from "@/hooks"
import type { AIConfigUpdate } from "@/lib/api-client"
import { ModelConfig } from "@/lib/api-client"
import { type AIConfigs, initialConfigs, MODEL_TYPES } from "@/types/settings"

type RuntimeModelType = typeof MODEL_TYPES[number]
type PrimitiveConfigValue = string | number | boolean | Record<string, unknown>
const EMPTY_RECORD: Record<string, unknown> = {}

import { isRecord } from "@/lib/utils"

// 深度合并函数
const deepMerge = (target: Record<string, unknown>, source: unknown): Record<string, unknown> => {
  if (!source) return target
  if (!isRecord(source)) return target

  const result = { ...target }
  for (const key in source) {
    const sourceValue = source[key]
    const targetValue = target[key]
    if (isRecord(sourceValue) && !Array.isArray(sourceValue)) {
      result[key] = deepMerge(isRecord(targetValue) ? targetValue : EMPTY_RECORD, sourceValue)
    } else {
      result[key] = sourceValue !== undefined && sourceValue !== null ? sourceValue : targetValue
    }
  }
  return result
}

// 统一配置合并逻辑
const mergeAIConfigs = (backendData: unknown, initial: AIConfigs): AIConfigs => {
  if (!isRecord(backendData)) return initial

  const parseSection = <T extends Record<string, unknown>>(section: unknown, initialSection: T): T => {
    if (!isRecord(section)) return initialSection
    return deepMerge(initialSection, section) as T
  }

  return {
    ...initial,
    chat: parseSection(backendData.chat, initial.chat),
    embedding: parseSection(backendData.embedding, initial.embedding),
    rerank: parseSection(backendData.rerank, initial.rerank),
    vl: parseSection(backendData.vl, initial.vl),
    bot_config: parseSection(backendData.bot_config, initial.bot_config),
  }
}

function toApiModelConfig(config: AIConfigs[RuntimeModelType]): AIConfigUpdate["chat"] {
  return {
    provider: config.provider,
    model: config.model,
    api_key: config.api_key,
    base_url: config.base_url,
    dimension: typeof config.dimension === "number" ? config.dimension : null,
    extra_body: {
      ...(config.extra_body as Record<string, any>),
      chat_template_kwargs: {
        ...(config.extra_body as any)?.chat_template_kwargs,
        enable_thinking: false
      }
    },
    is_vision: config.is_vision ?? false,
    mode: config.mode === "platform"
      ? ModelConfig.mode.PLATFORM
      : config.mode === "custom"
        ? ModelConfig.mode.CUSTOM
        : undefined
  }
}


interface SettingsContextType {
  // 配置状态
  configs: AIConfigs
  savedConfigs: AIConfigs
  isLoading: boolean
  isAiDirty: boolean
  scope: 'platform' | 'tenant'

  // 更新函数
  handleUpdate: (type: RuntimeModelType, field: string, value: PrimitiveConfigValue) => void
  handleSave: (modelType?: RuntimeModelType, overrides?: Partial<Record<string, PrimitiveConfigValue>>) => Promise<void>
  revertToSavedConfig: (modelType: RuntimeModelType) => void

  // 工具函数
  isModelConfigured: (modelType: RuntimeModelType) => boolean
  platformFallback: Record<string, boolean>
  platformDefaults: AIConfigs | null
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

export function SettingsProvider({ children, scope = 'tenant' }: { children: ReactNode, scope?: 'platform' | 'tenant' }) {
  const [configs, setConfigs] = useState<AIConfigs>(initialConfigs)
  const [savedConfigs, setSavedConfigs] = useState<AIConfigs>(initialConfigs)
  const [platformFallback, setPlatformFallback] = useState<Record<string, boolean>>({})
  const [platformDefaults, setPlatformDefaults] = useState<AIConfigs | null>(null)

  // 使用 React Query hooks
  const { data: aiConfigData, isLoading } = useAIConfig(scope)
  const updateAIConfigMutation = useUpdateAIConfig(scope)

  // [✨ 亮点] 统一的状态更新逻辑，确保初始加载和保存后逻辑一致
  const updateStateFromResponse = (data: any) => {
    if (!data) return

    // 1. 更新模型配置 (configs 只包含 chat/embedding 等项目)
    if (data.configs) {
      const updated = mergeAIConfigs(data.configs, initialConfigs)
      setConfigs(updated)
      setSavedConfigs(updated)
    }

    // 2. 更新元数据 (meta.is_platform_fallback)
    if (data.meta) {
      const fallback = data.meta.is_platform_fallback
      if (isRecord(fallback)) {
        const parsed = Object.entries(fallback).reduce<Record<string, boolean>>((acc, [key, value]) => {
          if (typeof value === "boolean") {
            acc[key] = value
          }
          return acc
        }, {})
        setPlatformFallback(parsed)
      }
    } else {
      setPlatformFallback({})
    }

    // 3. 更新平台默认值
    if (data.platform_defaults) {
      setPlatformDefaults(mergeAIConfigs(data.platform_defaults, initialConfigs))
    } else {
      setPlatformDefaults(null)
    }
  }

  // 当配置数据加载完成时，同步到本地状态
  useEffect(() => {
    if (aiConfigData) {
      updateStateFromResponse(aiConfigData)
    }
  }, [aiConfigData])

  const handleUpdate = (type: RuntimeModelType, field: string, value: PrimitiveConfigValue) => {
    setConfigs(prev => {
      const newConfigs = { ...prev }
      const modelConfig = prev[type]
      const updatedConfig = { ...modelConfig, [field]: value }
      newConfigs[type] = updatedConfig
      return newConfigs
    })
  }

  const handleSave = async (modelType?: RuntimeModelType, overrides?: Partial<Record<string, PrimitiveConfigValue>>) => {
    // 构造更新 Payload
    let aiConfig: AIConfigUpdate = {}

    if (modelType) {
      const mergedConfig = overrides
        ? { ...configs[modelType], ...overrides }
        : configs[modelType]
      aiConfig[modelType] = toApiModelConfig(mergedConfig)
    } else {
      aiConfig = {
        chat: toApiModelConfig(configs.chat),
        embedding: toApiModelConfig(configs.embedding),
        rerank: toApiModelConfig(configs.rerank),
        vl: toApiModelConfig(configs.vl)
      }
    }

    try {
      const data = await updateAIConfigMutation.mutateAsync(aiConfig)
      if (data) {
        updateStateFromResponse(data)
        toast.success("AI 模型配置已保存")
      }
    } catch (error) {
      // 错误由 useAdminMutation 统一处理
      throw error
    }
  }

  const revertToSavedConfig = (modelType: RuntimeModelType) => {
    setConfigs(prev => ({
      ...prev,
      [modelType]: deepMerge({}, savedConfigs[modelType] as Record<string, unknown>) as AIConfigs[RuntimeModelType]
    }))
  }

  const isAiDirty = (() => {
    const normalize = (obj: unknown): string => {
      if (obj === null || obj === undefined) return ''
      if (typeof obj !== 'object') return String(obj)
      if (Array.isArray(obj)) return obj.map(normalize).join(',')
      const record = obj as Record<string, unknown>
      return Object.keys(obj)
        .filter(k => record[k] !== undefined && record[k] !== null) // Filter out null/undefined keys
        .sort()
        .map(k => `${k}:${normalize(record[k])}`)
        .join('|')
    }
    const currentStr = normalize({ chat: configs.chat, embedding: configs.embedding, rerank: configs.rerank, vl: configs.vl, bot_config: configs.bot_config })
    const savedStr = normalize({ chat: savedConfigs.chat, embedding: savedConfigs.embedding, rerank: savedConfigs.rerank, vl: savedConfigs.vl, bot_config: savedConfigs.bot_config })
    return currentStr !== savedStr
  })()

  const isModelConfigured = (modelType: RuntimeModelType) => {
    const config = configs[modelType]

    // 如果使用了平台资源或正在使用平台回退，则视为已配置
    if (config.mode === "platform" || platformFallback[modelType]) {
      return true
    }

    // 自定义模式下必须填写所有必填项
    return !!(config.provider && config.model && config.api_key && config.base_url)
  }

  const value: SettingsContextType = {
    configs,
    savedConfigs,
    isLoading,
    isAiDirty,
    scope,
    handleUpdate,
    handleSave,
    revertToSavedConfig,
    isModelConfigured,
    platformFallback,
    platformDefaults
  }

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const context = useContext(SettingsContext)
  if (context === undefined) {
    throw new Error("useSettings must be used within a SettingsProvider")
  }
  return context
}
