# 快速上手

本文说明服务器上如何从零构建环境、运行主程序和检查输出。

## 目录假设

服务器目录应保持：

```text
~/work/
├── Makefile
├── requirements.txt
├── .venv/
└── place/
    ├── Constraints_Extraction/
    └── SubgraphMatching-master/
```

`.venv/` 由 `make setup` 或 `make build all` 自动创建，不需要手工移动。

## 一步初始化

```bash
cd ~/work
make setup
```

该命令会执行：

```text
1. 编译 place/SubgraphMatching-master
2. 创建或修复 ~/work/.venv
3. 安装 requirements.txt 中的 Python 依赖
4. 进入已激活 .venv 的 shell
```

如果只想构建环境，不进入 shell：

```bash
make build all
```

## 运行主流程

推荐从 `~/work` 运行：

```bash
make run
```

等价于：

```bash
cd ~/work/place/Constraints_Extraction
~/work/.venv/bin/python spice_annotation.py circuit.json
```

## 修改输入电路

编辑：

```text
place/Constraints_Extraction/circuit.json
```

关键字段：

```json
{
  "spice_path": "./Constraints_Extraction_data/circuit_data/",
  "netlist": "comparator.sp",
  "out_dir": "./output/",
  "subgraphmatchexe": "../SubgraphMatching-master/build/matching/SubgraphMatching.out",
  "query_path": "./Constraints_Extraction_data/query_graph/"
}
```

## 输出位置

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

同名电路再次运行会覆盖该目录内同名文件。

## 成功标志

终端中应看到：

```text
成功! 约束文件已保存至: ...
审计报告已保存至: ...
status: pass
```

如果 `status` 是 `need_review` 或 `fail`，先阅读 [report-guide.md](../verification/report-guide.md)。
