/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiResponse_NoneType_ } from '../models/ApiResponse_NoneType_';
import type { ApiResponse_PaginatedResponse_Site__ } from '../models/ApiResponse_PaginatedResponse_Site__';
import type { ApiResponse_Site_ } from '../models/ApiResponse_Site_';
import type { SiteCreate } from '../models/SiteCreate';
import type { SiteUpdate } from '../models/SiteUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AdminSitesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Sites
     * @returns ApiResponse_PaginatedResponse_Site__ Successful Response
     * @throws ApiError
     */
    public listAdminSites({
        page = 1,
        size = 10,
        isPager = 1,
        status,
    }: {
        page?: number,
        size?: number,
        /**
         * 是否分页，0=返回全部，1=分页
         */
        isPager?: number,
        status?: (string | null),
    }): CancelablePromise<ApiResponse_PaginatedResponse_Site__> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/sites',
            query: {
                'page': page,
                'size': size,
                'is_pager': isPager,
                'status': status,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Site
     * @returns ApiResponse_Site_ Successful Response
     * @throws ApiError
     */
    public createAdminSite({
        requestBody,
    }: {
        requestBody: SiteCreate,
    }): CancelablePromise<ApiResponse_Site_> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/admin/v1/sites',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Site
     * @returns ApiResponse_Site_ Successful Response
     * @throws ApiError
     */
    public getAdminSite({
        siteId,
    }: {
        siteId: number,
    }): CancelablePromise<ApiResponse_Site_> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/sites/{site_id}',
            path: {
                'site_id': siteId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Site
     * @returns ApiResponse_Site_ Successful Response
     * @throws ApiError
     */
    public updateAdminSite({
        siteId,
        requestBody,
    }: {
        siteId: number,
        requestBody: SiteUpdate,
    }): CancelablePromise<ApiResponse_Site_> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/admin/v1/sites/{site_id}',
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
    /**
     * Delete Site
     * @returns ApiResponse_NoneType_ Successful Response
     * @throws ApiError
     */
    public deleteAdminSite({
        siteId,
    }: {
        siteId: number,
    }): CancelablePromise<ApiResponse_NoneType_> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/admin/v1/sites/{site_id}',
            path: {
                'site_id': siteId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Site By Slug
     * @returns ApiResponse_Site_ Successful Response
     * @throws ApiError
     */
    public getAdminSiteBySlug({
        slug,
    }: {
        slug: string,
    }): CancelablePromise<ApiResponse_Site_> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/sites:bySlug/{slug}',
            path: {
                'slug': slug,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
