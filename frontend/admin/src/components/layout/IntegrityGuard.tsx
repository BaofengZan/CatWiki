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

"use client"

import { useEffect } from "react"

/**
 * 核心系统集成完整性卫士
 * 负责验证系统节点是否正常初始化并同步状态
 */
export function IntegrityGuard() {
  useEffect(() => {
    // 核心迁移：完整性校验已整合至 api-client.ts 的 CustomHttpRequest 中
    // 此处保持为空，确保不与 SDK 内部拦截逻辑冲突
  }, [])

  return null
}
