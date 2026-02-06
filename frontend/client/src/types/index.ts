// Copyright 2024 CatWiki Authors
// 
// Licensed under the CatWiki Open Source License (Modified Apache 2.0);
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// 
//     https://github.com/CatWiki/CatWiki/blob/main/LICENSE
// 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * Client 端类型定义
 */

// 菜单项类型（用于侧边栏，轻量）
export interface MenuItem {
  id: string
  title: string
  type: "collection" | "article"
  children?: MenuItem[]
  views?: number
  tags?: string[]
}

// 文档详情类型（用于文档展示页面，完整）
export interface DocumentDetail {
  id: string
  title: string
  content?: string
  summary?: string
  views?: number
  readingTime?: number
  tags?: string[]
}

// 引用来源类型
export interface Source {
  id: string
  title: string
  siteName?: string
  siteDomain?: string
  siteId?: number
  documentId?: number
}

// 消息类型（AI 对话）
export interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  sources?: Source[]
}

