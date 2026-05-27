# 算法架构设计说明

本文说明约束提取工程的整体架构、模块职责和数据流。

## 目标

本工程将模拟电路 SPICE 网表转换为版图约束。输出不是为了逐字匹配某个 `ideal` 文件，而是通过拓扑证据生成可解释约束，并用 `report.json` 判断结果是否可用。

## 主流程

```text
spice_annotation.py
  -> Configuration
  -> CircuitAnnotator.run()
  -> ConstraintExtractor
```

主流程分为 5 步：

| 步骤 | 位置 | 说明 |
|---|---|---|
| Step 1 | `spiceParser2.sp_parser()` | 解析 SPICE 网表并展平子电路 |
| Step 2 | `graph_convert()` + `graphForSubgraphMatchCXX()` | 转换为三分图并写出 C++ `.graph` |
| Step 3 | `SubgraphMatching.out` | 对每个模板做子图匹配 |
| Step 4 | `ConstraintExtractor.process_task()` | 将匹配结果映射为约束 |
| Step 5 | 规则函数 + `audit_constraint_coverage()` | 补充结构约束并生成审计报告 |

## 主要模块

| 文件 | 职责 |
|---|---|
| `spice_annotation.py` | 主控流程、模板选择、约束生成、报告审计 |
| `spice_parse2graph.py` | SPICE 解析、子电路识别、展平、电路图构建 |
| `Tools.py` | 二分图转三分图、写出 C++ 子图匹配格式 |
| `template_generator.py` | 辅助生成 query graph 和 map 文件 |
| `SubgraphMatching-master/` | C++ 子图匹配引擎 |

## 输入与输出

输入：

```text
SPICE netlist
query_graph/*.graph
primitive_constraint_map/*_map.json
circuit.json
```

输出：

```text
output/<circuit_name>/constraints.txt
output/<circuit_name>/report.json
output/<circuit_name>/debug/*
```

## 模板匹配策略

当前版本默认尝试所有正式模板：

```text
PRIMITIVE_QUERY_PRIORITY + CUSTOM_QUERY_PRIORITY
```

不再依赖 `structure_specs` 或按网表名手动选择模板。模板是否生效由三层逻辑共同决定：

```text
1. C++ 子图匹配是否找到结果
2. Python 拓扑过滤是否认可匹配
3. report 审计是否认为最终约束可用
```

## 约束生成策略

约束来源分两类：

| 来源 | 说明 |
|---|---|
| 模板约束 | 由 `.graph` 匹配结果和 `_map.json` 直接生成 |
| 规则约束 | 由 Python 基于拓扑补充，例如尾电流源、实例约束、层次组 |

规则执行顺序：

```text
PRE_TEMPLATE_RULES
  -> template tasks
  -> POST_TEMPLATE_RULES
  -> STRUCTURE_RULES / HIERARCHY_RULES
  -> audit_constraint_coverage
```

## 设计边界

当前系统是黑盒自动流程，不要求用户指定电路类型。输出是否可用主要看 `report.json`：

```text
pass        -> 当前规则下可直接使用
need_review -> 有风险，需要分析 report
fail        -> 不应直接使用
```

`pass` 不代表数学意义上绝对唯一，只代表当前约束格式、覆盖率和拓扑证据未发现问题。
