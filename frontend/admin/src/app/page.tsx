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

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getLastSiteDomain, setLastSiteDomain } from "@/lib/auth"
import { useSite } from "@/contexts/SiteContext"

export default function AdminHome() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)

  // 从 SiteContext 获取站点列表，避免重复请求
  const { sites, isLoadingSites } = useSite()

  // 动态获取第一个站点并重定向
  useEffect(() => {
    // 等待站点列表加载完成
    if (isLoadingSites) {
      return
    }

    const redirectToDefaultSite = () => {
      try {
        // 尝试获取最近访问的站点
        const lastDomain = getLastSiteDomain()
        if (lastDomain) {
          router.replace(`/${lastDomain}`)
          return
        }

        // 获取第一个激活的站点
        const activeSite = sites.find(site => site.status === "active")
        if (activeSite) {
          const domain = activeSite.domain || activeSite.id.toString()
          setLastSiteDomain(domain)
          router.replace(`/${domain}`)
          return
        }

        // 如果没有激活的站点，尝试获取任意站点
        if (sites.length > 0) {
          const firstSite = sites[0]
          const domain = firstSite.domain || firstSite.id.toString()
          setLastSiteDomain(domain)
          router.replace(`/${domain}`)
          return
        }

        // 如果没有任何站点，重定向到站点管理页面
        router.replace('/settings?tab=sites')
      } finally {
        setLoading(false)
      }
    }

    redirectToDefaultSite()
  }, [router, sites, isLoadingSites])

  return (
    <div className="h-screen flex items-center justify-center">
      <div className="text-slate-400">{loading ? "正在加载..." : "正在跳转..."}</div>
    </div>
  )
}
