/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocProcessorConfig } from './DocProcessorConfig';
/**
 * 文档处理服务最终响应
 */
export type DocProcessorResponse = {
    /**
     * 服务列表 (已合并租户与平台资源)
     */
    processors: Array<DocProcessorConfig>;
};

