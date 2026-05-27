# 文档总索引

这是约束提取工程的文档入口。建议按目录读，而不是一次性读完整个工程说明。

## 目录结构

| 目录 | 主题 |
|---|---|
| [overview/](overview/README.md) | 项目目标、架构、工程事实 |
| [workflow/](workflow/README.md) | 部署、运行、模板编写 |
| [reference/](reference/README.md) | 三分图、格式和约定 |
| [verification/](verification/README.md) | report 解读、验证策略 |
| [archive/](archive/) | 历史 PDF 资料 |

## 建议阅读顺序

1. [overview/README.md](overview/README.md)
2. [workflow/README.md](workflow/README.md)
3. [reference/README.md](reference/README.md)
4. [verification/README.md](verification/README.md)

## 核心文件

| 文件 | 作用 |
|---|---|
| `../Constraints_Extraction/spice_annotation.py` | 主流程 |
| `../Constraints_Extraction/spice_parse2graph.py` | SPICE 解析 |
| `../Constraints_Extraction/Tools.py` | 图转换与 `.graph` 写出 |
| `../Constraints_Extraction/Constraints_Extraction_data/query_graph/` | 模板 |
| `../Constraints_Extraction/Constraints_Extraction_data/primitive_constraint_map/` | 模板映射 |

