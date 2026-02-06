/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatCompletionRequest } from '../models/ChatCompletionRequest';
import type { ChatCompletionResponse } from '../models/ChatCompletionResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ChatService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Create Chat Completion
     * 创建聊天补全 (OpenAI 兼容接口) - 公开/Web挂件使用
     *
     * 安全机制：
     * 1. CORS/Origin 校验：确保请求来自受信任的域名（防止跨站调用滥用）
     * 2. 速率限制 (TODO)：建议在网关层配置
     * @returns ChatCompletionResponse Successful Response
     * @throws ApiError
     */
    public createChatCompletion({
        requestBody,
        origin,
        referer,
    }: {
        requestBody: ChatCompletionRequest,
        origin?: (string | null),
        referer?: (string | null),
    }): CancelablePromise<ChatCompletionResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/v1/chat/completions',
            headers: {
                'origin': origin,
                'referer': referer,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Site Chat Completion
     * 创建聊天补全 (专用接口) - 只有带有效 API Key 才能访问
     * @returns ChatCompletionResponse Successful Response
     * @throws ApiError
     */
    public createSiteChatCompletion({
        authorization,
        requestBody,
    }: {
        /**
         * Bearer <api_key>
         */
        authorization: string,
        requestBody: ChatCompletionRequest,
    }): CancelablePromise<ChatCompletionResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/v1/chat/site-completions',
            headers: {
                'authorization': authorization,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
