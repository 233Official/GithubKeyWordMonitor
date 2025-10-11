# GithubKeyWordMonitor

Github 关键词仓库监控

## 功能说明

通过 GitHub API 搜索指定关键词的仓库，按最近更新时间降序排序，自动过滤确保关键词出现在仓库名称或描述中，追踪新出现的仓库并生成 RSS 订阅源（包含全量聚合 feed 与按关键词拆分的 feed）。

## 环境要求

- Python >= 3.11
- uv (用于依赖管理)

## 安装

1. 安装 uv:
```bash
pip install uv
```

2. 克隆仓库:
```bash
git clone https://github.com/233Official/GithubKeyWordMonitor.git
cd GithubKeyWordMonitor
```

3. 安装依赖:
```bash
uv sync
```

## 配置

1. 复制配置文件模板:
```bash
cp config.toml.example config.toml
```

2. 编辑 `config.toml`:
   - 填写你的 GitHub Token (从 https://github.com/settings/tokens 获取)
   - 配置要监控的关键词列表

示例配置:
```toml
github_token = "ghp_your_token_here"
keywords = [
    "星痕共鸣",
    "example keyword",
]
```

## 使用

运行监控程序:
```bash
uv run main.py
```

程序会:
1. 搜索配置的每个关键词
2. 过滤结果确保关键词在仓库名称或描述中
3. 与之前的数据对比，找出新出现的仓库
4. 生成 RSS 订阅源：
   - 聚合 feed (`feed.xml`)
   - 按关键词拆分的 feed (`feeds/<URL 编码后的关键词>.xml`)
5. 保存已见过的仓库数据到 `data/` 目录

## 自动化

建议使用 cron 或 GitHub Actions 定时运行，例如每天更新一次:

### Cron 示例 (每天 00:00 运行)
```bash
0 0 * * * cd /path/to/GithubKeyWordMonitor && uv run main.py
```

### GitHub Actions 示例

本仓库已包含 `.github/workflows/monitor.yml` 工作流文件。要启用自动化监控：

1. **准备数据分支**：创建一个用于持久化结果的 `data` 分支，并允许 GitHub Actions 向该分支推送。
   ```bash
   git checkout --orphan data
   git rm -rf .
   touch .gitkeep
   git add .gitkeep
   git commit -m "chore: init data branch"
   git push origin data
   git checkout main
   ```

2. **配置关键词变量**：在仓库设置中添加 Actions 变量 `MONITOR_KEYWORDS`，步骤如下：
   1. 打开仓库页面，点击右上角的 `Settings`。
   2. 左侧菜单选择 `Secrets and variables` > `Actions`。
   3. 切换到 `Variables` 标签，点击 `New repository variable`。
   4. Name 填写 `MONITOR_KEYWORDS`，Value 输入要监控的关键词（可用逗号分隔，如 `"星痕共鸣","Star Resonance"`，或直接填写 JSON 数组 `["星痕共鸣", "Star Resonance"]`）。
   5. 点击 `Add variable` 保存。

3. （可选）如需更高的请求配额，可以修改工作流手动指定 PAT；默认情况下，工作流会使用 GitHub 自动提供的 `GITHUB_TOKEN`。

4. 工作流将每天自动运行，或者你可以在 `Actions` 标签页手动触发 `GitHub Keyword Monitor`。

工作流会把生成的 `feed.xml`、`feeds/*.xml` 和 `data/*.json` 推送到 `data` 分支。

## 订阅 RSS

将生成的 `feed.xml`（聚合订阅源）添加到你的 RSS 阅读器中即可接收所有关键词的新仓库通知。

如果你只关注某个关键词，可以订阅 `feeds/<URL 编码后的关键词>.xml`。例如关键词为 `星痕共鸣`，可订阅:
```
https://your-username.github.io/GithubKeyWordMonitor/feeds/%E6%98%9F%E7%97%95%E5%85%B1%E9%B8%A3.xml
```

如果使用 GitHub Pages，可以直接订阅上述路径；启用 Actions 后，最新 RSS 会出现在 `data` 分支，可通过 raw 链接订阅:
```
https://raw.githubusercontent.com/your-username/GithubKeyWordMonitor/data/feed.xml
https://raw.githubusercontent.com/your-username/GithubKeyWordMonitor/data/feeds/%E6%98%9F%E7%97%95%E5%85%B1%E9%B8%A3.xml
```

## 示例输出

运行后，会在控制台看到类似以下输出:

```
2025-10-11 00:00:00,000 - INFO - Starting GitHub Keyword Monitor
2025-10-11 00:00:01,000 - INFO - Processing keyword: 星痕共鸣
2025-10-11 00:00:01,100 - INFO - Previously seen 0 repositories for keyword '星痕共鸣'
2025-10-11 00:00:02,000 - INFO - Found 5 repositories matching keyword '星痕共鸣' (filtered from 12 total results)
2025-10-11 00:00:02,100 - INFO - New repository found: user/repo-name
2025-10-11 00:00:02,200 - INFO - Found 1 new repositories across all keywords
2025-10-11 00:00:02,300 - INFO - RSS feed generated: feed.xml
2025-10-11 00:00:02,400 - INFO - GitHub Keyword Monitor completed
```

## 许可证

MIT License

