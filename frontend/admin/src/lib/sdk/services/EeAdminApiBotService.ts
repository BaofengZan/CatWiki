/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiBotConfigUpdate } from '../models/ApiBotConfigUpdate';
import type { ApiResponse_ApiBotConfigResponse_ } from '../models/ApiResponse_ApiBotConfigResponse_';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class EeAdminApiBotService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Api Bot Config
     * 获取问答机器人配置
     * @returns ApiResponse_ApiBotConfigResponse_ Successful Response
     * @throws ApiError
     */
    public getApiBotConfig({
        siteId,
    }: {
        siteId: number,
    }): CancelablePromise<ApiResponse_ApiBotConfigResponse_> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/sites/{site_id}/ee-config/api-bot',
            path: {
                'site_id': siteId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Api Bot Config
     * 更新问答机器人配置
     * @returns ApiResponse_ApiBotConfigResponse_ Successful Response
     * @throws ApiError
     */
    public updateApiBotConfig({
        siteId,
        requestBody,
    }: {
        siteId: number,
        requestBody: ApiBotConfigUpdate,
    }): CancelablePromise<ApiResponse_ApiBotConfigResponse_> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/admin/v1/sites/{site_id}/ee-config/api-bot',
            path: {
                'site_id': siteId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
