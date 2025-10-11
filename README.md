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
创建 `.github/workflows/monitor.yml`:
```yaml
name: Monitor Keywords
on:
  schedule:
    - cron: '0 0 * * *'  # 每天 00:00 UTC
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install uv
        run: pip install uv
      - name: Run monitor
        env:
          GITHUB_TOKEN: ${{ secrets.GH_TOKEN }}
        run: |
          echo "github_token = \"$GITHUB_TOKEN\"" > config.toml
          echo "keywords = [\"星痕共鸣\"]" >> config.toml
          uv run main.py
      - name: Commit feed
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add feed.xml data/
          git commit -m "Update feed" || true
          git push
```

## 订阅 RSS

将生成的 `feed.xml` 文件添加到你的 RSS 阅读器中即可接收新仓库的通知。

## 许可证

MIT License

