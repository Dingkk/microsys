# Microsys 品牌与设计系统

> 科技蓝 · 专业运维风。清洁室重实现，自有品牌，不使用 1Panel 商标素材。

## Logo 资产

| 文件 | 用途 |
|------|------|
| `web/public/logo.svg` | 主图标（favicon、侧边栏折叠态、登录页图标） |
| `brand/microsys-logo-full.svg` | 横版组合标（登录页、文档、页头） |
| `brand/microsys-logo-mono.svg` | 单色版（`currentColor` 驱动，深浅底/水印/白标场景） |

### 设计理念
- **容器**：圆角方块 + 科技蓝对角渐变（`#3A8BDC → #0B6BCB → #0B4FA0`），顶部高光模拟金属质感。
- **字母 M**：由服务器机架/走线笔画抽象而成，一笔连续，象征"一站式集中运维"。
- **右下绿点**：`#21A366` 状态点，代表"节点在线 / 健康"，呼应运维监控主题。

### 使用规范
- 最小尺寸：图标 ≥ 24px，横版 ≥ 120px 宽。
- 安全间距：四周留白 ≥ 图标高度的 1/4。
- 禁止：拉伸变形、替换品牌色、给横版加描边、在低对比背景直接使用（改用 mono 版）。

## 色彩体系（与 `web/src/theme.css` 一致）

| 角色 | 色值 | Token |
|------|------|-------|
| 主色 Primary | `#0B6BCB` | `--ms-color-primary` |
| 主色深 | `#0B4FA0` | `--ms-color-primary-dark` |
| 主色浅 | `#3A8BDC` | `--ms-color-primary-light` |
| 成功 | `#21A366` | `--ms-color-success` |
| 警告 | `#E3A008` | `--ms-color-warning` |
| 危险 | `#D83A3A` | `--ms-color-danger` |
| 中性灰 | `#FFFFFF → #161C26`（0–900 十级） | `--ms-color-neutral-*` |

## 主题
- 默认 **深色主题**（`data-theme="dark"`），运维长时间使用护眼、数据密度优先。
- 提供 **浅色主题**（`data-theme="light"`）一键切换。
- 所有 token 以 `ms-` 前缀命名，便于后续「白标定制」整体替换。

## 规范尺度
- 圆角：`4 / 8 / 12 px`（sm/md/lg）
- 间距：`8 / 16 / 24 px`
- 卡片阴影：`0 2px 12px rgba(0,0,0,.08)`
- 字体：Inter / PingFang SC / Microsoft YaHei，正文 14px
