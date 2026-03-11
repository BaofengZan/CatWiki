/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * AI 配置专用响应结构 (扁平化且优雅)
 */
export type AIConfigResponse = {
    /**
     * 各模型项配置 (chat/embedding/...)
     */
    configs: Record<string, any>;
    /**
     * 元数据 (如 Fallback 状态)
     */
    meta?: (Record<string, any> | null);
    /**
     * 平台默认配置 (参考用)
     */
    platform_defaults?: (Record<string, any> | null);
};

