# Microsys 设计系统（Design System）

> 科技蓝 · 专业运维风。数据密度优先，深浅双主题。
> 清洁室重实现，自有品牌，不使用 1Panel 商标素材。
> 与 `web/src/theme.css` token 一一对应；所有 token 以 `ms-` 前缀命名，便于白标替换。

---

## 1. 设计理念

- **一站式集中运维**：以「一屏尽览」为最高优先级，高密度表格 + 指标卡片为主，减少无效留白。
- **专业可信**：科技蓝主色传递稳定、技术感；中性灰承载信息层级。
- **双主题护眼**：默认深色（长时间盯盘护眼），一键切浅色；运维场景优先深色。
- **双端一致**：Web 与 iOS 共用同一套色彩 / 字体 / 组件语义，信息在移动端降维呈现。

---

## 2. 品牌资产

| 文件 | 用途 |
|------|------|
| `web/public/logo.svg` | 主图标（favicon、侧边栏折叠态、登录页图标） |
| `brand/microsys-logo-full.svg` | 横版组合标（登录页、文档、页头） |
| `brand/microsys-logo-mono.svg` | 单色版（`currentColor` 驱动，深浅底 / 水印 / 白标） |

**Logo 构成**：圆角方块 + 科技蓝对角渐变（`#3A8BDC → #0B6BCB → #0B4FA0`），顶部高光模拟金属质感；字母 M 由服务器机架走线抽象而成，一笔连续；右下 `#21A366` 绿点为「节点在线 / 健康」状态点。

**使用规范**：图标最小 24px、横版最小 120px 宽；四周留白 ≥ 图标高度 1/4；禁止拉伸变形、替换品牌色、给横版加描边、在低对比背景直接使用（改用 mono 版）。

---

## 3. 色彩 Token

### 3.1 品牌与主色
| 角色 | 色值 | Token |
|------|------|-------|
| Primary 主色 | `#0B6BCB` | `--ms-color-primary` |
| Primary 深 | `#0B4FA0` | `--ms-color-primary-dark` |
| Primary 浅 | `#3A8BDC` | `--ms-color-primary-light` |

### 3.2 语义色
| 角色 | 色值 | Token |
|------|------|-------|
| 成功 Success | `#21A366` | `--ms-color-success` |
| 警告 Warning | `#E3A008` | `--ms-color-warning` |
| 危险 Danger | `#D83A3A` | `--ms-color-danger` |

### 3.3 中性灰（0–900）
`#FFFFFF`(0) → `#F2F5F9`(100) → `#E3E9F1`(200) → `#C8D2DF`(300) → `#97A4B6`(400) → `#6B7889`(500) → `#4A5568`(600) → `#333D4D`(700) → `#222A36`(800) → `#161C26`(900)
Token：`--ms-color-neutral-{0,100,...,900}`

### 3.4 主题表面（按 `data-theme` 切换）
| 表面 | 深色 `dark` | 浅色 `light` |
|------|------|------|
| 页面底 `--ms-bg-page` | `#0F141C` | `#F2F5F9` |
| 卡片面 `--ms-bg-surface` | `#161C26` | `#FFFFFF` |
| 浮起面 `--ms-bg-elevated` | `#222A36` | `#FFFFFF` |
| 侧边栏 `--ms-bg-sidebar` | `#11161F` | `#0F1A2B` |
| 悬停 `--ms-bg-hover` | `#2A3340` | `#E3E9F1` |
| 主文字 `--ms-text-primary` | `#E8EDF3` | `#1C2530` |
| 次文字 `--ms-text-secondary` | `#97A4B6` | `#6B7889` |
| 描边 `--ms-border` | `#2A3340` | `#E3E9F1` |

---

## 4. 字体排版

- **字体栈**：`Inter, 'PingFang SC', 'Microsoft YaHei', system-ui, -apple-system, sans-serif`
- **正文**：14px / 行高 1.5
- **字阶**：Display 28/700 · H1 22/600 · H2 18/600 · Body 14/400 · Caption 12/400

---

## 5. 间距 / 圆角 / 阴影

- **间距**：`--ms-space-sm:8` / `--ms-space-md:16` / `--ms-space-lg:24`（px）
- **圆角**：`--ms-radius-sm:4` / `--ms-radius-md:8` / `--ms-radius-lg:12`（px）
- **卡片阴影**：`--ms-shadow-card: 0 2px 12px rgba(0,0,0,.08)`

---

## 6. 核心组件规范

### 6.1 Button
- **变体**：Primary（填充主色）/ Secondary（描边）/ Ghost（文字）/ Danger（填充危险色）
- **尺寸**：sm（高度 28）/ md（高度 34，默认）
- **状态**：default / hover（亮度+8%）/ active（亮度-6%）/ disabled（40% 透明、禁点）/ loading（旋转图标 + 禁用）
- **规则**：主操作每屏 ≤ 1 个 Primary；危险操作需二次确认。

### 6.2 Input
- **状态**：default（描边 `--ms-border`）/ focus（描边主色 + 0 0 0 3px 主色 15% 光晕）/ error（描边危险色 + 错误文案）/ disabled。
- 支持前/后置图标与单位。

### 6.3 Table（数据密度优先）
- 行高 40px（紧凑）/ 48px（常规）；表头 `--ms-bg-elevated` + 次文字色。
- 行 hover 切换 `--ms-bg-hover`；可选斑马纹。
- 支持排序、筛选、分页、行内操作（启停/日志/编辑）。

### 6.4 Card
- 默认 `--ms-bg-surface`；浮起用 `--ms-bg-elevated`；统一 lg 圆角 + 卡片阴影。
- 结构：标题区（左标题 + 右操作）/ 内容区（padding md-lg）。

### 6.5 Tag / Badge
- 语义色映射：success / warning / danger / info / neutral。
- 圆角 sm；小字号；可用于状态（运行中 / 已停止 / 异常）。

### 6.6 Alert
- 4 级：info（主色）/ success（绿）/ warning（黄）/ danger（红）；含图标 + 标题 + 描述 + 关闭。

### 6.7 StatusDot（状态点）
- online `#21A366` / offline `#97A4B6` / warn `#E3A008` / error `#D83A3A`；常用于节点 / 容器 / 服务健康。

### 6.8 导航
- **Sidebar**：深色固定宽 220px（折叠 64px）；分组 + 图标 + 选中主色高亮。
- **Topbar**：面包屑 + 全局搜索 + 主题切换 + 告警铃 + 用户菜单。

---

## 7. 图标与可视化

- 图标库：线性图标，1.5px 描边，24px 栅格；复用同一套主色 / 中性色。
- 图表（ECharts）：折线（监控趋势）、环形（资源占比）、条形（TOP 进程）、地图（访客 / 拦截，P1）。
- 可视化配色遵循语义色与中性灰，避免高饱和干扰读数。

---

## 8. 白标与主题定制

- 所有视觉变量以 `ms-` 前缀集中定义，白标时仅需替换 token 文件（`theme.css`）+ Logo 三件套，无需改业务组件。
- 多主题：`<html data-theme="dark|light">` 全局切换；用户偏好持久化到 localStorage。

---

## 9. 交付物索引

| 类型 | 路径 |
|------|------|
| 主题 token（落地） | `web/src/theme.css` |
| 品牌说明 | `brand/README.md` |
| Logo 资产 | `web/public/logo.svg`、`brand/*.svg` |
| 界面设计稿（可预览） | `brand/design-showcase.html` |
| 设计系统文档 | `docs/DESIGN_SYSTEM.md` |
