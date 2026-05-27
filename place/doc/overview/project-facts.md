# 项目事实

## 工程目标

本工程从 SPICE 网表中自动提取版图约束，并输出：

```text
constraints.txt
report.json
debug/*
```

## 当前黑盒逻辑

```text
SPICE netlist -> 解析 -> 三分图 -> 子图匹配 -> 模板映射 -> 规则补全 -> report
```

## 当前构建入口

```bash
cd ~/work
make setup
make run
```

## 当前输出结构

```text
output/<circuit_name>/
├── constraints.txt
├── report.json
└── debug/
```

## 关键目录

| 路径 | 作用 |
|---|---|
| `Constraints_Extraction/` | 主程序 |
| `SubgraphMatching-master/` | C++ 匹配引擎 |
| `doc/` | 文档 |

