/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccessConfigUpdate } from '../models/AccessConfigUpdate';
import type { ApiResponse_SiteEEConfigResponse_ } from '../models/ApiResponse_SiteEEConfigResponse_';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class EeAdminSiteAccessService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Site Ee Config
     * 获取站点 EE 配置
     * @returns ApiResponse_SiteEEConfigResponse_ Successful Response
     * @throws ApiError
     */
    public getSiteEeConfig({
        siteId,
    }: {
        siteId: number,
    }): CancelablePromise<ApiResponse_SiteEEConfigResponse_> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/sites/{site_id}/ee-config',
            path: {
                'site_id': siteId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Site Access Config
     * 更新站点访问控制配置
     * @returns ApiResponse_SiteEEConfigResponse_ Successful Response
     * @throws ApiError
     */
    public updateSiteAccessConfig({
        siteId,
        requestBody,
    }: {
        siteId: number,
        requestBody: AccessConfigUpdate,
    }): CancelablePromise<ApiResponse_SiteEEConfigResponse_> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/admin/v1/sites/{site_id}/ee-config/access',
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
