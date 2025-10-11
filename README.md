# GithubKeyWordMonitor

Github 关键词仓库监控

## 功能说明

通过 GitHub API 搜索指定关键词的仓库，按最近更新时间降序排序，自动过滤确保关键词出现在仓库名称或描述中，追踪新出现的仓库并生成 RSS 订阅源。

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
4. 生成 RSS 订阅源 (`feed.xml`)
5. 保存已见过的仓库数据到 `data/` 目录

## 自动化

建议使用 cron 或 GitHub Actions 定时运行，例如每天更新一次:

### Cron 示例 (每天 00:00 运行)
```bash
0 0 * * * cd /path/to/GithubKeyWordMonitor && uv run main.py
```

### GitHub Actions 示例

本仓库已包含 `.github/workflows/monitor.yml` 工作流文件。要启用自动化监控:

1. 在 GitHub 仓库设置中添加 Secret:
   - 进入 `Settings` > `Secrets and variables` > `Actions`
   - 点击 `New repository secret`
   - Name: `GH_MONITOR_TOKEN`
   - Value: 你的 GitHub Personal Access Token

2. 编辑 `.github/workflows/monitor.yml` 中的 keywords 列表

3. 工作流将每天自动运行，或者你可以手动触发:
   - 进入 `Actions` 标签页
   - 选择 `GitHub Keyword Monitor` 工作流
   - 点击 `Run workflow`

工作流会自动提交更新的 RSS feed 和数据文件到仓库。

## 订阅 RSS

将生成的 `feed.xml` 文件添加到你的 RSS 阅读器中即可接收新仓库的通知。

如果使用 GitHub Pages，可以直接订阅:
```
https://your-username.github.io/GithubKeyWordMonitor/feed.xml
```

或者如果你使用 GitHub Actions 自动提交，可以通过 GitHub raw 链接订阅:
```
https://raw.githubusercontent.com/your-username/GithubKeyWordMonitor/main/feed.xml
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

