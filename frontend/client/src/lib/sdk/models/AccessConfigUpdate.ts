/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 更新站点访问控制 (管理端请求)
 */
export type AccessConfigUpdate = {
    is_public?: (boolean | null);
    /**
     * 明文密码，后端自动哈希
     */
    password?: (string | null);
};

