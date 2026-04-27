# Magic-QC

![PyPI version](https://img.shields.io/pypi/v/magic_qc.svg)
![Python versions](https://img.shields.io/pypi/pyversions/magic_qc.svg)
![License](https://img.shields.io/github/license/wxd123/magic-qc.svg)

自动化质量检测与筛选工具 - 通用的数据质量检查与智能筛选解决方案

* [GitHub](https://github.com/wxd123/magic-qc/) | [PyPI](https://pypi.org/project/magic_qc/) | [Documentation](https://wxd123.github.io/magic-qc/)
* Created by  GitHub [@wxd123](https://github.com/wxd123)
* MIT License

## Features

- **多维度质量检测** - 支持完整性、一致性、准确性、唯一性、及时性等质量维度检查
- **灵活的规则引擎** - 可配置的检测规则，支持正则表达式、范围校验、枚举值、依赖关系等
- **智能筛选** - 基于质量评分的自动筛选，支持阈值、优先级、标签等多种策略
- **批量处理** - 高效处理大规模数据集，支持分块、并行处理
- **多数据源支持** - JSON、CSV、Excel、Parquet、数据库等
- **可扩展架构** - 自定义检测器、筛选器和规则函数
- **多格式报告** - HTML、JSON、Markdown、Excel 报告输出

## 快速开始

### 安装

```bash
# 使用 pip 安装
pip install magic_qc

# 使用 uv 安装
uv pip install magic_qc


## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://wxd123.github.io/magic_qc/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/magic_qc.git
cd magic_qc

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `magic_qc`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```
## 代码规范
本项目遵循以下基本原则：

1. 单文件不超过 200 行：超过时请拆分为多个模块
2. 单函数不超过 200 行：超过时请拆分为多个小函数
3. 注释尽量完整：关键逻辑、复杂算法、非显而易见的代码必须有注释说明
4. 如有特殊场景确实需要突破（如纯数据定义文件），可在 PR 中说明。

这些规则旨在保证代码的可读性和可维护性，便于合作，请尽量遵守。

## 针对 AI 辅助工具的提示
本项目使用 AI 辅助开发，请在生成代码时尽量遵守上述代码规范。

## 许可证
MIT License - 详见 LICENSE 文件

## 作者
Magic-QC 由 jackson wang 创建于 2026 年。

项目使用 Cookiecutter 和 audreyfeldroy/cookiecutter-pypackage 模板生成。


