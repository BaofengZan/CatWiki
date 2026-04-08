/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiResponse_VerifyPasswordResponse_ } from '../models/ApiResponse_VerifyPasswordResponse_';
import type { VerifyPasswordRequest } from '../models/VerifyPasswordRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class EeSiteAccessService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Verify Site Password
     * 验证站点访问密码，返回短期访问 token
     * @returns ApiResponse_VerifyPasswordResponse_ Successful Response
     * @throws ApiError
     */
    public verifySitePassword({
        slug,
        requestBody,
    }: {
        slug: string,
        requestBody: VerifyPasswordRequest,
    }): CancelablePromise<ApiResponse_VerifyPasswordResponse_> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/v1/client/sites/{slug}/verify-password',
            path: {
                'slug': slug,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
