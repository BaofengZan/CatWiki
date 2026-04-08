/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiResponse_Union_TenantSchema__NoneType__ } from '../models/ApiResponse_Union_TenantSchema__NoneType__';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AdminTenantsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * 获取当前生效租户
     * 根据 Token 和 X-Selected-Tenant-ID Header 获取当前生效的租户详情
     * @returns ApiResponse_Union_TenantSchema__NoneType__ Successful Response
     * @throws ApiError
     */
    public getAdminCurrentTenant(): CancelablePromise<ApiResponse_Union_TenantSchema__NoneType__> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/tenants/current',
        });
    }
}
