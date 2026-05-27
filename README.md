# APR Constraint Extraction Workspace

这是服务器工作区入口。新人通常只需要从本目录开始操作，不需要手动进入 C++ 引擎目录或手动创建 Python 虚拟环境。

## 快速启动

首次部署或环境重建：

```bash
cd ~/work
make setup
```

日常运行：

```bash
make run
```

如果当前不在 `~/work`，也可以从任意目录运行：

```bash
make -C ~/work run
```

## 目录结构

```text
work/
├── Makefile
├── README.md
├── requirements.txt
├── .venv/
└── place/
    ├── Makefile
    ├── README.md
    ├── Constraints_Extraction/
    │   ├── spice_annotation.py
    │   ├── spice_parse2graph.py
    │   ├── Tools.py
    │   ├── circuit.json
    │   ├── output/
    │   │   └── <circuit_name>/
    │   │       ├── constraints.txt
    │   │       ├── report.json
    │   │       └── debug/
    │   └── Constraints_Extraction_data/
    │       ├── circuit_data/
    │       ├── query_graph/
    │       └── primitive_constraint_map/
    ├── SubgraphMatching-master/
    └── doc/
        ├── README.md
        ├── overview/
        ├── workflow/
        ├── reference/
        ├── verification/
        └── archive/
```

## 常用命令

| 命令 | 作用 |
|---|---|
| `make setup` | 构建 C++ 引擎、创建 Python 环境并进入 shell |
| `make build all` | 只构建全部环境，不进入 shell |
| `make build SubgraphMatching-master` | 只编译 C++ 子图匹配引擎 |
| `make build Constraints_Extraction` | 只准备 Python 虚拟环境 |
| `make shell` | 进入已有 `.venv` |
| `make run` | 运行约束提取主流程 |
| `make -C ~/work run` | 从任意目录运行主流程 |

## 输入配置

主配置文件：

```text
place/Constraints_Extraction/circuit.json
```

常用字段：

```json
{
  "spice_path": "./Constraints_Extraction_data/circuit_data/",
  "netlist": "twoStageMiller.sp",
  "out_dir": "./output/",
  "subgraphmatchexe": "../SubgraphMatching-master/build/matching/SubgraphMatching.out",
  "query_path": "./Constraints_Extraction_data/query_graph/"
}
```

这些路径相对于 `circuit.json` 所在目录解析，因此不依赖当前 shell 所在路径。

## 输出结构

每个电路会输出到独立目录：

```text
place/Constraints_Extraction/output/<circuit_name>/
├── constraints.txt
├── report.json
└── debug/
    ├── <circuit_name>_target.graph
    ├── match_*.txt
    └── constraints_debug.txt
```

同名电路再次运行会覆盖该电路目录内的同名文件。

## 文档导航

详细文档在：

```text
place/doc/
```

推荐入口：

| 文档 | 内容 |
|---|---|
| [`place/doc/README.md`](place/doc/README.md) | 文档总索引 |
| [`place/doc/overview/README.md`](place/doc/overview/README.md) | 项目目标与算法架构 |
| [`place/doc/workflow/README.md`](place/doc/workflow/README.md) | 部署、运行、模板编写 |
| [`place/doc/reference/README.md`](place/doc/reference/README.md) | 三分图与格式约定 |
| [`place/doc/verification/README.md`](place/doc/verification/README.md) | report 解读、常见 bug 与验证 |

## 验收标准

一个电路输出可进入后续流程，通常需要满足：

```text
report.json:
  status = pass
  risks = []
  unconstrained = 0
  constraint_validation.errors = []
```

如果不是 `pass`，优先阅读：

```text
place/doc/verification/report-guide.md
place/doc/verification/common-bugs.md
```
