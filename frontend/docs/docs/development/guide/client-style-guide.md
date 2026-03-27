# Client 设计语言规范

本文档定义了客户端（对外展示）的视觉设计规范。Client 面向终端用户，风格比 Admin 更活泼、更有层次感。

---

## 🎨 Design Tokens

所有视觉属性通过 CSS 变量（`globals.css`）定义，并在 `tailwind.config.ts` 中映射为工具类。

### 圆角 Token

| Token | Tailwind 类 | 值 | 用途 |
|-------|------------|-----|------|
| `--radius-card` | `rounded-card` | 16px | 卡片容器 |
| `--radius-button` | `rounded-button` | 8px | Button |
| `--radius-input` | `rounded-input` | 8px | Input、搜索框 |
| `--radius-dropdown` | `rounded-dropdown` | 12px | DropdownMenu、Popover |
| `--radius-modal` | `rounded-modal` | 24px | Dialog、AI 对话弹窗 |
| `--radius-badge` | `rounded-badge` | 9999px | Badge、标签 |

### 阴影 Token

| Token | Tailwind 类 | 用途 |
|-------|------------|------|
| `--shadow-card` | `shadow-card` | 卡片静态状态 |
| `--shadow-card-hover` | `shadow-card-hover` | 卡片 hover 状态 |
| `--shadow-dropdown` | `shadow-dropdown` | 下拉菜单、搜索结果面板 |
| `--shadow-modal` | `shadow-modal` | Dialog、AI 对话弹窗 |

### 过渡 Token

| Token | Tailwind 类 | 值 | 用途 |
|-------|------------|-----|------|
| `--transition-fast` | `duration-fast` | 150ms | 颜色、透明度 |
| `--transition-normal` | `duration-normal` | 200ms | 阴影、布局 |

### 主题色

Client 支持动态主题色切换，通过 `--theme-primary` 系列变量控制：

```css
--theme-primary: hsl(217, 91%, 60%);       /* 主色 */
--theme-primary-hover: hsl(217, 91%, 55%);  /* hover 态 */
--theme-primary-light: hsl(217, 91%, 95%);  /* 浅色背景 */
--theme-primary-dark: hsl(217, 91%, 50%);   /* 深色强调 */
```

这些值由后端站点配置动态注入，前端通过 `ThemeProvider` 应用。

---

## 🧩 组件使用规范

### Button

通过 `variant` 和 `size` 控制，不在 className 中覆盖圆角和阴影：

```tsx
// ✅ 正确
<Button size="lg">开始对话</Button>
<Button variant="outline">取消</Button>
<Button variant="ghost" size="icon-sm"><X className="h-4 w-4" /></Button>

// ❌ 错误
<Button className="rounded-xl shadow-lg shadow-primary/20 hover:scale-[1.02]">
```

**尺寸参考：**

| size | 高度 | 用途 |
|------|------|------|
| `sm` | h-9 | 紧凑操作 |
| `default` | h-10 | 通用 |
| `lg` | h-11 | 主操作（发送、提交） |
| `icon` | h-10 w-10 | 标准图标按钮 |
| `icon-sm` | h-8 w-8 | 关闭、折叠 |
| `icon-xs` | h-7 w-7 | 紧凑图标 |

### 下拉菜单

组件已内置 `rounded-dropdown` 和 `shadow-dropdown`：

```tsx
// ✅ 正确
<DropdownMenuContent align="end" className="w-48">

// ❌ 错误
<DropdownMenuContent className="rounded-xl shadow-xl border-slate-100">
```

---

## ✨ 交互规范

### 与 Admin 的区别

Client 面向终端用户，允许更丰富的交互效果：

| 效果 | Client | Admin | 说明 |
|------|--------|-------|------|
| `active:scale-95` | ✅ 允许 | ❌ 禁止 | 按钮点击反馈 |
| `hover:scale-105` | ✅ 允许 | ❌ 禁止 | 发送按钮、CTA |
| `shadow-lg shadow-primary/20` | ✅ 允许 | ❌ 禁止 | 主操作按钮强调 |
| `glass-card` | ✅ 使用 | ❌ 不使用 | 毛玻璃效果 |

::: tip
这些效果仅在业务组件中使用（`SiteCard`、`ChatWidget`、`AIChatLanding` 等），不要加在 `components/ui/` 的基础组件上。
:::

### Loading 状态

统一使用 `Loader2` 图标，不使用 CSS border spinner：

```tsx
import { Loader2 } from "lucide-react"

// ✅ 正确
<Loader2 className="h-6 w-6 animate-spin text-primary" />

// ❌ 错误
<div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
```

---

## 📐 日期格式化

```tsx
// ✅ 正确 — 使用 locale 变量
const locale = useLocale()
new Date(date).toLocaleString(locale, { ... })

// ❌ 错误 — 硬编码
new Date(date).toLocaleString('zh-CN', { ... })
```

---

## 📚 相关文档

- [Client 前端开发](/development/guide/frontend-client)
- [Admin 设计规范](/development/guide/style-guide)
- [AI 对话与知识库检索](/development/tech/ai-chat-architecture)
