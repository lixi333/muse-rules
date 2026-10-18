# muse-rules

Meta Muse AI 分流规则订阅（自动合并、每日更新）。

## 规则来源

- [juner922/muse-loon-rules](https://github.com/juner922/muse-loon-rules)（`MuseAI.list`）
- [VPSDance/ai-proxy-rules](https://github.com/VPSDance/ai-proxy-rules)（`meta-ai.list`）

GitHub Actions 每天 02:00 UTC 自动抓取两份规则、合并去重后提交，
`MuseAI-merged.list` 和 `MuseAI.arrs` 永远是最新版。

## 订阅方式

### Anywhere（iOS）

把下面任一 URL 加为远程规则集（`.arrs` 为 Anywhere 专用格式），
导入后手动把该规则集指向你的美国节点策略组：

- GitHub Raw：`https://raw.githubusercontent.com/lixi333/muse-rules/main/MuseAI.arrs`
- jsDelivr CDN（国内访问更快）：`https://cdn.jsdelivr.net/gh/lixi333/muse-rules@main/MuseAI.arrs`

### Loon / Surge（通用格式）

把下面任一 URL 加为远程规则集：

- GitHub Raw：`https://raw.githubusercontent.com/lixi333/muse-rules/main/MuseAI-merged.list`
- jsDelivr CDN（国内访问更快）：`https://cdn.jsdelivr.net/gh/lixi333/muse-rules@main/MuseAI-merged.list`

将规则指向你的美国节点策略组。

## 注意事项

Muse 有地区限制：即使域名全部走代理，若出口 IP 不是美区原生/家宽 IP，
仍会提示"尚未在你的国家或地区开放"。请使用美区家宽节点。
