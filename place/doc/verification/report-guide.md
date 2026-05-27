# report.json 分析方式

本文说明如何阅读 `output/<circuit_name>/report.json`。

## report 的定位

`report.json` 是自动审计结果，用于判断 `constraints.txt` 是否可进入后续布局布线。

它不是黄金答案对比工具，而是回答三个问题：

```text
1. 输出有没有约束？
2. 顶层器件有没有被覆盖？
3. 约束格式和拓扑证据是否可信？
```

## 第一眼看什么

先看：

```json
{
  "status": "pass",
  "risks": []
}
```

状态含义：

| status | 含义 | 处理方式 |
|---|---|---|
| `pass` | 当前规则下未发现明显问题 | 可进入后续流程 |
| `need_review` | 有风险，但不一定错误 | 读 risks 和 missing |
| `fail` | 输出不可直接使用 | 修模板、规则或输入配置 |

## risks 字段

常见风险：

| risk | 含义 |
|---|---|
| `no_constraints_generated` | 没有生成任何约束 |
| `unconstrained_top_level_devices` | 有顶层器件未被约束覆盖 |
| `possible_missing_symmetric_pairs` | 未覆盖器件中存在疑似对称/配对候选 |
| `invalid_constraint_format_or_topology` | 约束格式或拓扑校验错误 |
| `constraint_validation_warnings` | 有警告项，需要确认 |

## 覆盖率字段

示例：

```json
{
  "total_top_level": 13,
  "constrained": 13,
  "unconstrained": 0,
  "coverage_ratio": 1.0
}
```

判断方式：

```text
unconstrained = 0 通常是好信号。
unconstrained > 0 时，需要继续看 type_summary。
```

## type_summary

示例：

```json
{
  "nmos": {
    "total": 8,
    "unconstrained": 2,
    "missing": ["m7", "m8"]
  }
}
```

含义：

```text
nmos 一共有 8 个，其中 m7、m8 没被 constraints.txt 覆盖。
```

下一步通常是检查：

```text
1. 是否缺少模板
2. 模板是否匹配失败
3. 规则是否没有覆盖该结构
4. 这些器件是否本来不需要约束
```

## pair_candidates

示例：

```json
[
  {
    "left": "m7",
    "right": "m8",
    "type": "nmos",
    "reason": "same_gate+matched_supply_branches"
  }
]
```

含义：

```text
未覆盖器件中，m7 和 m8 有拓扑相似性，可能遗漏了配对或对称约束。
```

如果 `pair_candidates` 不为空，优先检查模板和规则。

## constraint_validation

结构：

```json
{
  "constraint_validation": {
    "errors": [],
    "warnings": [],
    "groups": []
  }
}
```

字段含义：

| 字段 | 含义 |
|---|---|
| `errors` | 明确错误，通常导致 `fail` |
| `warnings` | 可疑项，通常导致 `need_review` |
| `groups` | 每个约束组的详细解释 |

## groups 怎么读

每个 group 示例：

```json
{
  "group": "Group_2",
  "rule": "3",
  "members": ["m1", "m2"],
  "covers": ["m1", "m2"],
  "evidence": ["explicit_pair_lines"],
  "pairs": [
    {
      "left": "m1",
      "right": "m2",
      "evidence": ["same_type:nmos", "shared_source"]
    }
  ],
  "issues": []
}
```

重点看：

```text
issues 是否为空
pairs.evidence 是否能解释 pair 的合理性
covers 是否覆盖预期器件
```

## 常见问题定位

| 现象 | 优先检查 |
|---|---|
| `fail + no_constraints_generated` | C++ 引擎路径、query_path、模板是否存在 |
| `need_review + unconstrained_top_level_devices` | `type_summary.missing` |
| `need_review + possible_missing_symmetric_pairs` | `pair_candidates` |
| `fail + invalid_constraint_format_or_topology` | `constraint_validation.errors` |
| report 存在但 constraints 为空 | 模板未匹配或规则未生成 |

## 建议修复流程

```text
1. 看 status
2. 看 risks
3. 看 type_summary.missing
4. 看 pair_candidates
5. 看 constraint_validation.errors/warnings
6. 看 debug/constraints_debug.txt
7. 看 debug/match_*.txt
8. 决定是改模板、map、规则还是输入配置
```

## 注意

`pass` 不代表唯一正确解。只要生成的约束符合当前约束语义，且 report 未发现风险，就可以作为后续流程输入。

更多具体问题和修改位置见 [common-bugs.md](common-bugs.md)。
