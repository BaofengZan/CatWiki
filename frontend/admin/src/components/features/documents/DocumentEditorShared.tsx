// Copyright 2026 CatWiki Authors
//
// Licensed under the CatWiki Open Source License (Modified Apache 2.0);
// you may not use this file except in compliance with the License.

"use client"

import { useState, useEffect } from "react"
import { useTranslations, useLocale } from "next-intl"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Save, Send, Image as ImageIcon, Settings as SettingsIcon,
  Tags, Hash, User, Info, Clock, Plus, Loader2
} from "lucide-react"
import { LazyMarkdownEditor } from "@/components/editor"
import { CreateCollectionDialog } from "@/components/features/documents/CreateCollectionDialog"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import { TagsInput } from "@/components/ui/TagsInput"
import { ImageUpload } from "@/components/ui/ImageUpload"
import type { CollectionTree } from "@/lib/api-client"
import { DocumentStatus } from "@/lib/api-client"
import { cn } from "@/lib/utils"
import { getUserInfo } from "@/lib/auth"

type CollectionTreeWithLevel = CollectionTree & { level?: number }

export function flattenCollections(tree: CollectionTree[]): CollectionTreeWithLevel[] {
  const result: CollectionTreeWithLevel[] = []
  const flatten = (items: CollectionTree[], level = 0) => {
    items.forEach(item => {
      result.push({ ...item, level })
      if (item.children?.length) flatten(item.children, level + 1)
    })
  }
  flatten(tree)
  return result
}

export interface DocumentFormData {
  title: string
  summary: string
  tags: string[]
  coverImage: string | null
  collectionId: string
  content: string
}

interface DocumentEditorContentProps {
  form: DocumentFormData
  onChange: <K extends keyof DocumentFormData>(field: K, value: DocumentFormData[K]) => void
  collections: CollectionTreeWithLevel[]
  collectionsLoading: boolean
  siteId: number
  isPending: boolean
}

/** 左侧编辑器区域 */
export function DocumentEditorContent({
  form, onChange,
}: Pick<DocumentEditorContentProps, 'form' | 'onChange'>) {
  const t = useTranslations("Documents")

  return (
    <Card className="border-border/50 shadow-sm overflow-hidden">
      <CardHeader className="pb-6 px-8 pt-8 space-y-4">
        <Input
          type="text"
          placeholder={t("newDoc.placeholderTitle")}
          className="text-3xl font-extrabold border-none focus-visible:ring-0 px-0 h-auto placeholder:text-slate-300 bg-transparent"
          value={form.title}
          onChange={(e) => onChange('title', e.target.value)}
        />
        <div className="space-y-2 pt-2">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <Info className="h-3.5 w-3.5" />
            <span className="text-[11px] font-bold uppercase tracking-wider">{t("newDoc.summary")}</span>
          </div>
          <Textarea
            placeholder={t("newDoc.placeholderSummary")}
            className="resize-none min-h-[80px] text-sm leading-relaxed text-slate-600 border-none bg-slate-50/50 focus-visible:ring-1 focus-visible:ring-primary/20 rounded-xl px-4 py-3 placeholder:text-slate-400"
            value={form.summary}
            onChange={(e) => onChange('summary', e.target.value)}
          />
        </div>
      </CardHeader>
      <CardContent className="p-0 border-t border-slate-100">
        <div className="md-editor-container">
          <LazyMarkdownEditor
            value={form.content}
            onChange={(v) => onChange('content', v)}
            placeholder={t("newDoc.placeholderContent")}
          />
        </div>
      </CardContent>
    </Card>
  )
}

/** 右侧配置侧边栏 */
export function DocumentEditorSidebar({
  form, onChange, collections, collectionsLoading, siteId, isPending, children,
}: DocumentEditorContentProps & { children?: React.ReactNode }) {
  const t = useTranslations("Documents")
  const [isCreateCollectionOpen, setIsCreateCollectionOpen] = useState(false)

  return (
    <>
      <CreateCollectionDialog
        siteId={siteId}
        open={isCreateCollectionOpen}
        onOpenChange={setIsCreateCollectionOpen}
        onSuccess={(id) => onChange('collectionId', id.toString())}
        collections={collections}
      />
      <Card className="border-border/50 shadow-sm overflow-hidden">
        <CardHeader className="border-b border-border/40 bg-muted/20 py-5 px-6">
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <div className="p-1.5 bg-white rounded-lg shadow-sm">
              <SettingsIcon className="h-4 w-4 text-primary" />
            </div>
            {t("config.title")}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          {/* 所属合集 */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-slate-500">
              <Hash className="h-4 w-4" />
              <label className="text-sm font-bold">{t("config.collection")}</label>
              <span className="text-red-500">*</span>
            </div>
            <div className="flex items-center gap-2">
              <Select value={form.collectionId} onValueChange={(v) => onChange('collectionId', v)} disabled={collectionsLoading}>
                <SelectTrigger className="flex-1 bg-slate-50/50 border-slate-200 h-10 rounded-xl">
                  <SelectValue placeholder={collectionsLoading ? t("config.collectionsLoading") : (collections.length === 0 ? t("config.noCollection") : t("config.collectionPlaceholder"))} />
                </SelectTrigger>
                <SelectContent className="rounded-xl">
                  {collections.map((col) => (
                    <SelectItem key={col.id} value={col.id.toString()} className="text-sm">
                      <span style={{ paddingLeft: `${(col.level || 0) * 12}px` }}>{col.title}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                type="button" variant="outline" size="icon"
                className="h-10 w-10 shrink-0 rounded-xl border-slate-200 hover:bg-slate-50 transition-colors"
                onClick={() => setIsCreateCollectionOpen(true)}
                title={t("config.createCollection")}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {collections.length === 0 && !collectionsLoading && (
              <p className="text-[10px] text-amber-600 font-medium">{t("config.noCollection")}</p>
            )}
          </div>

          {/* 标签 */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-slate-500">
              <Tags className="h-4 w-4" />
              <label className="text-sm font-bold">{t("config.tags")}</label>
            </div>
            <TagsInput value={form.tags} onChange={(v) => onChange('tags', v)} placeholder={t("config.tagsPlaceholder")} />
          </div>

          {/* 封面图 */}
          <div className="space-y-3 pt-2">
            <div className="flex items-center gap-2 text-slate-500">
              <ImageIcon className="h-4 w-4" />
              <label className="text-sm font-bold">{t("config.coverImage")}</label>
            </div>
            <ImageUpload value={form.coverImage} onChange={(v) => onChange('coverImage', v)} disabled={isPending} />
          </div>

          {/* 附加信息（由调用方注入） */}
          {children && (
            <div className="pt-6 border-t border-slate-100 space-y-4">
              {children}
            </div>
          )}
        </CardContent>
      </Card>
    </>
  )
}

/** 附加信息行 */
export function MetaRow({ icon: Icon, label, children }: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="flex justify-between items-center bg-slate-50/50 p-3 rounded-xl">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon className="h-3.5 w-3.5" />
        <span className="text-xs font-medium">{label}</span>
      </div>
      {children}
    </div>
  )
}

/** Markdown 编辑器样式 */
export function EditorStyles() {
  return null // 样式已移至 globals.css
}
