/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * 单条消息模型（OpenAI 格式）
 */
export type app__schemas__chat_session__ChatMessage = {
    /**
     * 角色: user/assistant/system
     */
    role: string;
    /**
     * 内容
     */
    content: string;
    /**
     * 消息ID
     */
    id?: (string | null);
};

