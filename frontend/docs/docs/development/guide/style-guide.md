# Admin 设计语言规范

本文档定义了管理后台的视觉设计规范。所有新增页面和组件应遵循此规范。

---

## 🎨 Design Tokens

所有视觉属性通过 CSS 变量（`globals.css`）定义，并在 `tailwind.config.ts` 中映射为工具类。
修改视觉风格时，**只需改变量值**，不要在业务代码中硬编码。

### 圆角 Token

| Token | Tailwind 类 | 值 | 用途 |
|-------|------------|-----|------|
| `--radius-card` | `rounded-card` | 16px | Card、面板容器 |
| `--radius-button` | `rounded-button` | 8px | Button、表单控件 |
| `--radius-input` | `rounded-input` | 6px | Input、Textarea、Select trigger |
| `--radius-dropdown` | `rounded-dropdown` | 12px | DropdownMenu、Popover、Select content |
| `--radius-modal` | `rounded-modal` | 16px | Dialog、Sheet |
| `--radius-badge` | `rounded-badge` | 9999px | Badge、Tag、状态指示器 |

### 阴影 Token

| Token | Tailwind 类 | 用途 |
|-------|------------|------|
| `--shadow-card` | `shadow-card` | Card 静态状态 |
| `--shadow-card-hover` | `shadow-card-hover` | Card hover 状态 |
| `--shadow-dropdown` | `shadow-dropdown` | 下拉菜单、Popover、Select |
| `--shadow-modal` | `shadow-modal` | Dialog、全屏 Modal |

### 过渡 Token

| Token | Tailwind 类 | 值 | 用途 |
|-------|------------|-----|------|
| `--transition-fast` | `duration-fast` | 150ms | 颜色、透明度变化 |
| `--transition-normal` | `duration-normal` | 200ms | 阴影、布局变化 |

### 修改示例

如果想让所有 Card 更圆，只需修改一行：

```css
/* globals.css */
:root {
  --radius-card: 1.25rem; /* 从 1rem 改为 1.25rem */
}
```

---

## 🎨 颜色使用规则

### 文本颜色

| 场景 | 正确 ✅ | 错误 ❌ |
|------|---------|---------|
| 页面标题 | `text-foreground` | `text-slate-900` |
| 正文 | `text-foreground` | `text-slate-800` |
| 次要文本 | `text-muted-foreground` | `text-slate-500` |
| 禁用文本 | `text-muted-foreground/50` | `text-slate-300` |

::: tip 原则
优先使用语义化 token（`foreground`、`muted-foreground`），它们会自动适配暗色模式。
仅在组件内部的装饰性元素（如图标、分隔线）上允许使用 `text-slate-*`。
:::

### 背景颜色

| 场景 | 推荐写法 |
|------|---------|
| 页面背景 | `bg-slate-50/50` |
| 卡片背景 | `bg-card`（组件默认） |
| 表头/区域背景 | `bg-muted/20` |
| hover 行 | `hover:bg-muted/30` |

### 边框颜色

| 场景 | 正确 ✅ | 错误 ❌ |
|------|---------|---------|
| 默认边框 | `border-border` | `border-slate-200` |
| 弱化边框 | `border-border/50` | `border-slate-200/60`、`border-border/40` |
| 分隔线 | `border-border/50` | `border-slate-100` |

---

## 🧩 组件使用规范

### Button

使用 `variant` 和 `size` 控制样式，**不要在 className 中覆盖**。

```tsx
// ✅ 正确
<Button variant="outline" size="sm">取消</Button>
<Button size="lg">保存</Button>
<Button variant="ghost" size="icon-sm">
  <X className="h-4 w-4" />
</Button>

// ❌ 错误 — 不要覆盖组件已定义的样式
<Button className="rounded-xl shadow-lg h-12 font-bold">保存</Button>
```

**尺寸参考：**

| size | 高度 | 用途 |
|------|------|------|
| `sm` | h-9 | 表格操作、紧凑区域 |
| `default` | h-10 | 通用 |
| `lg` | h-11 | 页面主操作（发布、保存） |
| `icon` | h-10 w-10 | 标准图标按钮 |
| `icon-sm` | h-8 w-8 | 表格行操作、面板关闭 |
| `icon-xs` | h-7 w-7 | 紧凑图标按钮 |

### Card

直接使用，不覆盖圆角和阴影：

```tsx
// ✅ 正确
<Card>
<Card className="overflow-hidden">
<Card className="hover:shadow-card-hover transition-shadow">

// ❌ 错误
<Card className="rounded-2xl shadow-xl border-slate-200/60">
```

### 下拉菜单 / Popover

组件已内置 `rounded-dropdown` 和 `shadow-dropdown`，不需要覆盖：

```tsx
// ✅ 正确
<DropdownMenuContent align="end" className="w-56">
<PopoverContent className="w-64 p-0">

// ❌ 错误
<DropdownMenuContent className="rounded-2xl shadow-xl border-border/40">
```

---

## ✨ 交互规范

### 允许的 hover 效果

| 效果 | 用途 | 示例 |
|------|------|------|
| `hover:bg-*` | 所有可点击元素 | 按钮、菜单项、表格行 |
| `hover:shadow-card-hover` | 可点击的 Card | 站点卡片、文档卡片 |
| `hover:text-primary` | 链接、图标按钮 | header 工具栏 |

### 禁止的效果

| 效果 | 原因 |
|------|------|
| `hover:scale-*` | 管理后台应保持克制，不使用缩放 |
| `active:scale-*` | 同上，Button 组件不带此效果 |
| `hover:-translate-y-*` | 浮起效果过于花哨 |
| `animate-in zoom-in` | 仅用于 Modal/Dropdown 的进入动画，不用于普通元素 |

::: warning 例外
`ChatWidgetPreview` 是面向终端用户的预览组件，允许更丰富的交互效果。
:::

### 过渡属性

```tsx
// ✅ 精确指定变化的属性
className="transition-colors"    // 仅颜色变化
className="transition-shadow"    // 仅阴影变化
className="transition-opacity"   // 仅透明度变化

// ⚠️ 仅在多个属性同时变化时使用
className="transition-all"       // 颜色 + 阴影 + 边框同时变化
```

---

## 📐 页面布局规范

### 页面标题

```tsx
// 统一格式
<h1 className="text-3xl font-bold tracking-tight text-foreground">
  {title}
</h1>
<p className="text-muted-foreground mt-2">{description}</p>
```

### 全屏页面背景

所有独立页面（登录、404、空状态）统一使用 `bg-slate-50/50`。

### 日期格式化

```tsx
// ✅ 正确 — 使用 locale 变量
const locale = useLocale()
new Date(date).toLocaleString(locale, { ... })

// ❌ 错误 — 硬编码 locale
new Date(date).toLocaleString('zh-CN', { ... })
```

---

## ✅ 快速检查清单

新增页面/组件时，对照以下清单：

- [ ] 文本颜色使用 `text-foreground` / `text-muted-foreground`，而非 `text-slate-*`
- [ ] 边框使用 `border-border`，而非 `border-slate-200`
- [ ] Card 不覆盖 `rounded-*` 和 `shadow-*`
- [ ] Button 通过 `variant` + `size` 控制，不在 className 中覆盖
- [ ] 日期格式化使用 `useLocale()` 获取的 locale
- [ ] 无 `hover:scale-*` 或 `active:scale-*`
- [ ] `transition-*` 精确到实际变化的属性

---

## 📚 相关文档

- [Admin 前端开发](/development/guide/frontend-admin)
- [SDK 使用指南](/development/tech/sdk-usage)
