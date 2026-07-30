# Microsys 部署与发布指南

> 服务端同时支持两种交付形态：① Docker 容器部署；② Linux 宿主机一键脚本部署。
> 架构基准：`docs/ARCHITECTURE.md`；MVP 工程：`microsys/`。

---

## 1. 部署方式一：Docker（推荐）

### 1.1 快速启动
```bash
cd microsys
docker compose up -d
```
- 服务端口：默认 `8080`（由 `MS_PORT` 环境变量 / 配置覆盖）
- 数据卷：`/opt/microsys`（SQLite 元数据、文件管理沙箱根、日志、备份）
- 健康检查：镜像内置纯 Go 探针 `/usr/local/bin/healthcheck`，`HEALTHCHECK` 与 compose `healthcheck` 均指向它（替代 distroless 中不可用的 wget）

### 1.2 升级
```bash
docker compose pull && docker compose up -d
```

### 1.3 自定义
- 端口 / 数据目录 / 日志级别：通过 `docker-compose.yml` 的 `environment` 与 `volumes` 调整。
- 反向代理（HTTPS / 自定义域名）：前置 Nginx / Caddy，将 `/api/v1` 与静态资源反代到容器。

---

## 2. 部署方式二：Linux 宿主机一键脚本

### 2.1 安装
```bash
curl -sSL https://get.microsys.io/install.sh | bash
# 或离线：bash install.sh
```
脚本行为（`server/install.sh`）：
1. **root 检查**：非 root 退出并提示。
2. **架构检测**：识别 `x86_64` / `ARM64`，下载对应二进制（纯 Go 静态编译，无 cgo 依赖，单文件分发）。
3. **依赖检测**：确认基础命令；数据库用内置 SQLite，无需外部依赖。
4. **幂等**：已安装则进入「升级 / 重装 / 退出」引导，不重复写入。
5. **注册 systemd 服务**：`microsys.service`，开机自启。
6. **初始账号**：`admin / microsys`，首次登录强制改密。

### 2.2 升级 / 卸载
```bash
bash install.sh      # 选择升级
bash uninstall.sh    # 卸载（仅删除安装目录与服务；数据目录 /opt/microsys 默认保留，需显式确认才清理）
```
> 安全说明：`uninstall.sh` 的 `rm -rf` 仅作用于硬编码常量安装目录，且对变量做非空兜底校验，不会拼接用户输入路径，避免误删。

---

## 3. 安全基线（部署后必做）

- 首次登录强制修改 `admin` 默认口令（当前 `microsys`）。
- 自定义服务端口，避免暴露在常见扫描端口。
- 启用 **HTTPS / TLS**（反代或面板内置），禁用明文 HTTP 管理口。
- 建议开启 **双因素 TOTP**（模型已预留 `totp_secret` 字段，MVP 登录流程支持扩展）。
- 升级通道校验签名，防止二进制被篡改。

---

## 4. 发布清单（Release Checklist）

- [ ] 版本号与 Changelog（`v0.1.0` 起，语义化版本）
- [ ] 后端 `go build`（CGO_ENABLED=0，x86_64 + ARM64 双架构）
- [ ] 前端 `npm run build` 产出 `web/dist/`
- [ ] 镜像构建并打 tag，推送至镜像仓库（如 Harbor / 腾讯云 TCR）
- [ ] `docker-compose.yml` 与 `install.sh` / `uninstall.sh` 随版本回归
- [ ] 升级通道签名（公钥内置，安装脚本校验）
- [ ] 文档：PRD / ARCHITECTURE / DESIGN_SYSTEM / DEPLOY 随包提供
- [ ] GPL-3.0 许可声明与源码获取方式（清洁室重实现义务）

---

## 5. 已知限制（MVP 阶段）

- 容器真实启停 / 日志需在带 Docker 守护进程的环境验收（无守护进程时 API 优雅返回 `code=3001`）。
- 网站 / 数据库 / 终端 / 计划任务 / 应用商店模块仅占位返回 `501`，列入 P1 实现。
- iOS App 仅预留 REST 边界，客户端实现列入后续迭代。
- 白标定制（Logo / 主题 / 水印）P1 提供，MVP 仅预留入口与 `ms-` token 体系。
