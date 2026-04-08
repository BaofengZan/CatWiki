/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiResponse_dict_ } from '../models/ApiResponse_dict_';
import type { ApiResponse_NoneType_ } from '../models/ApiResponse_NoneType_';
import type { ApiResponse_PaginatedResponse_dict__ } from '../models/ApiResponse_PaginatedResponse_dict__';
import type { Body_batchUploadAdminFiles } from '../models/Body_batchUploadAdminFiles';
import type { Body_uploadAdminFile } from '../models/Body_uploadAdminFile';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AdminFilesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Upload File
     * 上传文件到 RustFS
     * @returns ApiResponse_dict_ Successful Response
     * @throws ApiError
     */
    public uploadAdminFile({
        formData,
        folder = 'uploads',
    }: {
        formData: Body_uploadAdminFile,
        /**
         * 存储文件夹
         */
        folder?: string,
    }): CancelablePromise<ApiResponse_dict_> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/admin/v1/files:upload',
            query: {
                'folder': folder,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Upload Multiple Files
     * 批量上传文件到 RustFS
     * @returns ApiResponse_dict_ Successful Response
     * @throws ApiError
     */
    public batchUploadAdminFiles({
        formData,
        folder = 'uploads',
    }: {
        formData: Body_batchUploadAdminFiles,
        /**
         * 存储文件夹
         */
        folder?: string,
    }): CancelablePromise<ApiResponse_dict_> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/admin/v1/files:batchUpload',
            query: {
                'folder': folder,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Download File
     * 下载文件
     * @returns any Successful Response
     * @throws ApiError
     */
    public downloadAdminFile({
        objectName,
    }: {
        objectName: string,
    }): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/files/{object_name}:download',
            path: {
                'object_name': objectName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete File
     * 删除文件
     * @returns ApiResponse_NoneType_ Successful Response
     * @throws ApiError
     */
    public deleteAdminFile({
        objectName,
    }: {
        objectName: string,
    }): CancelablePromise<ApiResponse_NoneType_> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/admin/v1/files/{object_name}',
            path: {
                'object_name': objectName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Files
     * 列出文件
     * @returns ApiResponse_PaginatedResponse_dict__ Successful Response
     * @throws ApiError
     */
    public listAdminFiles({
        prefix = '',
        recursive = true,
        page = 1,
        size = 20,
        isPager = 1,
    }: {
        /**
         * 文件路径前缀
         */
        prefix?: string,
        /**
         * 是否递归列出
         */
        recursive?: boolean,
        /**
         * 页码
         */
        page?: number,
        /**
         * 每页数量
         */
        size?: number,
        /**
         * 是否分页，0=返回全部，1=分页
         */
        isPager?: number,
    }): CancelablePromise<ApiResponse_PaginatedResponse_dict__> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/files',
            query: {
                'prefix': prefix,
                'recursive': recursive,
                'page': page,
                'size': size,
                'is_pager': isPager,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get File Info
     * 获取文件信息
     * @returns ApiResponse_dict_ Successful Response
     * @throws ApiError
     */
    public getAdminFileInfo({
        objectName,
    }: {
        objectName: string,
    }): CancelablePromise<ApiResponse_dict_> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/files/{object_name}:info',
            path: {
                'object_name': objectName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Presigned Url
     * 获取文件的预签名 URL
     * @returns ApiResponse_dict_ Successful Response
     * @throws ApiError
     */
    public getAdminPresignedUrl({
        objectName,
        expiresHours = 1,
    }: {
        objectName: string,
        /**
         * URL 有效期（小时）
         */
        expiresHours?: number,
    }): CancelablePromise<ApiResponse_dict_> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/admin/v1/files/{object_name}:presignedUrl',
            path: {
                'object_name': objectName,
            },
            query: {
                'expires_hours': expiresHours,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
