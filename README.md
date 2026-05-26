# Analog Circuit Layout Constraint Extraction

从模拟电路 SPICE 网表中自动提取版图约束的工具链。  
流程覆盖网表解析、三分图建模、C++ 子图匹配、模板约束映射、结构化规则推断以及最终 report 审计。

> 当前版本的目标不是让输出逐字匹配某个 `ideal` 示例，而是基于电路拓扑证据生成高置信度约束，并通过 report 说明每条约束覆盖了什么、为什么成立、是否存在风险。

## 功能概览

- 从 SPICE 网表自动生成电路图与三分图。
- 调用 `SubgraphMatching.out` 识别差分对、电流镜、负载、交叉耦合对等结构。
- 根据 `.graph` 模板和 `_map.json` 映射生成版图约束。
- 使用结构化规则补充比较器、bootstrap、全差分等高层结构约束。
- 生成 `*_report.json`，用于判断结果是否可直接进入后续布局布线。

## 目录结构

```text
work/
├── .venv/
├── Makefile
├── requirements.txt
└── place/
    ├── Constraints_Extraction/
│   ├── spice_annotation.py
│   ├── spice_parse2graph.py
│   ├── Tools.py
│   ├── template_generator.py
│   ├── circuit.json
│   ├── circuit_local_test.json
│   ├── output/
│   │   ├── real/
│   │   ├── ideal/
│   │   └── local_test/
│   └── Constraints_Extraction_data/
│       ├── circuit_data/
│       ├── query_graph/
│       └── primitive_constraint_map/
    └── SubgraphMatching-master/
        └── build/matching/SubgraphMatching.out
```

| 路径 | 说明 |
|---|---|
| `Constraints_Extraction/spice_annotation.py` | 主流程脚本 |
| `Constraints_Extraction/spice_parse2graph.py` | SPICE 网表解析 |
| `Constraints_Extraction/Tools.py` | 图转换与 `.graph` 写出 |
| `Constraints_Extraction/template_generator.py` | 半自动模板生成工具 |
| `Constraints_Extraction_data/circuit_data/` | 待处理网表 |
| `Constraints_Extraction_data/query_graph/` | 子图匹配模板 |
| `Constraints_Extraction_data/primitive_constraint_map/` | 模板到约束的映射 |
| `output/real/` | 当前真实输出 |
| `output/ideal/` | 正确参考示例 |

## 环境准备

### 1. 激活 Python 环境

```bash
cd work
make shell
```

进入后会自动切到 `work/place` 并激活 `.venv`。

### 2. 编译 C++ 图匹配引擎

首次运行前需要编译 `SubgraphMatching-master`：

```bash
cd work/place/SubgraphMatching-master
mkdir -p build
cd build
cmake ..
make
```

确认以下文件存在：

```text
work/place/SubgraphMatching-master/build/matching/SubgraphMatching.out
```

> Windows 本地环境通常不能直接运行服务器编译得到的 `.out` 文件。如果出现 `WinError 193`，一般是执行环境问题，不代表 Python 主流程错误。

### 3. 一键构建

在 `work/` 目录下可以直接使用 `make` 完成常用环境准备：

```bash
cd work
make build all
```

可选命令：

```bash
make build SubgraphMatching-master
make build Constraints_Extraction
```

说明：

- `make build SubgraphMatching-master` 仅编译 C++ 图匹配引擎。
- `make build Constraints_Extraction` 仅准备 Python 虚拟环境并安装依赖。
- `make build all` 会同时执行两者。
- 默认会尝试在 `work/.venv/` 下创建 Python 环境。
- 进入虚拟环境推荐使用 `make shell`。
- Python 依赖由 `work/requirements.txt` 管理。

## 使用方法

### 1. 准备输入网表

将 SPICE 网表放入：

```text
Constraints_Extraction/Constraints_Extraction_data/circuit_data/
```

### 2. 修改配置

编辑：

```text
Constraints_Extraction/circuit.json
```

常用字段：

```json
{
  "spice_path": "./Constraints_Extraction_data/circuit_data/",
  "netlist": "bootstrap.sp",
  "out_dir": "./output/",
  "subgraphmatchexe": "../SubgraphMatching-master/build/matching/SubgraphMatching.out",
  "query_path": "./Constraints_Extraction_data/query_graph/"
}
```

| 字段 | 含义 |
|---|---|
| `spice_path` | 输入网表目录 |
| `netlist` | 待处理网表文件名 |
| `out_dir` | 输出目录 |
| `subgraphmatchexe` | C++ 匹配引擎路径 |
| `query_path` | 模板 `.graph` 目录 |

### 3. 运行

```bash
cd work/place/Constraints_Extraction
python spice_annotation.py circuit.json
```

本地测试配置：

```bash
python spice_annotation.py circuit_local_test.json
```

## 工作流程

```text
SPICE 网表
  -> 网表解析与展平
  -> 电路图建模
  -> 三分图转换
  -> C++ 子图匹配
  -> 模板约束映射
  -> 结构化规则推断
  -> 约束合法性与覆盖率审计
  -> 最终约束文件与 report
```

主流程会默认尝试所有正式模板。模板是否真正生效由子图匹配结果、拓扑过滤规则和最终 report 共同决定，而不是依赖用户提前指定电路类型。

## C++ 匹配参数

Python 主流程内部调用 C++ 引擎时使用：

```bash
./SubgraphMatching.out \
  -d [Target_Graph] \
  -q [Template_Graph] \
  -filter GQL \
  -order GQL \
  -engine LFTJ \
  -num MAX \
  -result [Output_Path]
```

注意事项：

- `-engine` 必须使用 `LFTJ`，否则可能无法输出完整匹配结果。
- 不要将 `VF2++` 作为 engine 参数。
- query graph 中不应存在孤立节点。
- `.graph` 文件中的节点 degree 应与实际边数一致。

## 输出文件

运行后会在 `output/` 下生成：

| 文件 | 说明 |
|---|---|
| `*_target.graph` | 当前电路的目标三分图 |
| `match_*.txt` | 模板节点到电路节点的匹配结果 |
| `*_final_constraints.txt` | 最终版图约束 |
| `*_final_constraints_debug.txt` | 匹配和规则推断调试信息 |
| `*_final_constraints_report.json` | 自动审计报告 |

约束示例：

```text
Group_1 11 c0 1
Group_2 3 m21 m22
2 m21 m21
2 m22 m22
Group_3 6 m11 m19 m18 m1 m17
```

常见约束编号：

| 编号 | 含义 |
|---|---|
| `1` | 二器件匹配/成对约束 |
| `3` | 对称组约束 |
| `6` | 行约束 |
| `7` | 保护约束 |
| `8` | 电流镜约束 |
| `11` | 旋转约束 |

## Report 阅读方法

`*_report.json` 用于判断约束是否可直接进入后续布局布线。

### 1. 看 `status` 和 `risks`

```json
{
  "status": "pass",
  "risks": []
}
```

| 状态 | 含义 |
|---|---|
| `pass` | 覆盖完整，未发现明显格式或拓扑风险 |
| `need_review` | 输出可能可用，但需要人工确认 |
| `fail` | 输出不能直接使用，需要修复模板、规则或验证器 |

常见风险：

| 风险 | 含义 |
|---|---|
| `unconstrained_top_level_devices` | 存在未覆盖顶层器件 |
| `possible_missing_symmetric_pairs` | 存在疑似遗漏对称/配对关系 |
| `invalid_constraint_format_or_topology` | 约束格式或拓扑校验错误 |
| `constraint_validation_warnings` | 约束验证存在警告 |

### 2. 看覆盖率

```json
{
  "total_top_level": 13,
  "constrained": 13,
  "unconstrained": 0,
  "coverage_ratio": 1.0
}
```

如果 `unconstrained > 0`，查看 `type_summary.missing` 定位未覆盖器件。

### 3. 看 `pair_candidates`

```json
"pair_candidates": []
```

如果不为空，说明未覆盖器件中存在疑似对称或配对候选，需要检查模板或规则是否遗漏。

### 4. 看 `constraint_validation`

```json
{
  "constraint_validation": {
    "errors": [],
    "warnings": [],
    "groups": []
  }
}
```

| 字段 | 含义 |
|---|---|
| `errors` | 明确错误，存在时通常不能直接使用 |
| `warnings` | 可疑项，需要确认 |
| `groups` | 每个约束组的解释信息 |

每个 group 会记录：

| 字段 | 含义 |
|---|---|
| `group` | 约束组名称 |
| `rule` | 约束类型 |
| `members` | 约束成员 |
| `covers` | 覆盖的器件或实例 |
| `referenced_groups` | 引用的子 group |
| `evidence` | 约束成立证据 |
| `pairs` | pair 及其拓扑证据 |
| `issues` | 当前 group 内部问题 |

## 基准测试电路

当前 `output/real/` 中维护三组稳定测试：

| 电路 | 说明 | 期望状态 |
|---|---|---|
| `full_differential` | 全差分结构测试 | `pass` |
| `comparator` | 锁存比较器结构测试 | `pass` |
| `bootstrap` | Bootstrap switch 结构测试 | `pass` |

开发建议：

```text
修改模板、map、规则或验证器
  -> 重跑当前问题电路
  -> 重跑三组基准电路
  -> 所有 report 保持 pass
```

## 模板扩展

当基础模板无法覆盖新结构时，可以使用：

```text
Constraints_Extraction/template_generator.py
```

示例：

```bash
cd work/place/Constraints_Extraction
python template_generator.py \
  --netlist Constraints_Extraction_data/circuit_data/new_circuit.sp \
  --devices m12,m13 \
  --name BiasPair_nmos \
  --constraint symmetry
```

会生成：

```text
Constraints_Extraction_data/query_graph/BiasPair_nmos_target.graph
Constraints_Extraction_data/primitive_constraint_map/BiasPair_nmos_map.json
```

常用 constraint 类型：

| 类型 | 说明 |
|---|---|
| `pair` | 生成约束 `1` |
| `symmetry` | 生成约束 `3` |
| `self_symmetry` | 生成自对称约束 |
| `row` | 生成约束 `6` |
| `rotation` | 生成约束 `11` |
| `current_mirror` | 生成约束 `8` |

> 模板生成工具只用于辅助扩展。生成的 graph 和 map 仍需检查后再纳入正式模板库。

## 常见问题

### 没有生成 `match_*.txt`

检查 `-engine` 是否为 `LFTJ`。如果使用 `GQL` 作为 engine，可能只计数不输出结果。

### `VF2++` 不支持

该版本 C++ 库将 `VF2++` 视为排序方法，而不是枚举引擎。请使用 `LFTJ`。

### `Permission denied`

```bash
chmod +x ../SubgraphMatching-master/build/matching/SubgraphMatching.out
```

### 缺少 Python 依赖

确认已经激活虚拟环境：

```bash
cd work
source .venv/bin/activate
```

### `visited_vertices` 断言失败

通常说明 query graph 中存在孤立节点或图结构不连通。

### `checkEdgeExistence` 断言失败

通常说明 `.graph` 文件中的 degree、边关系或 query plan 所需结构不一致。

### `real` 与 `ideal` 不完全一致

不一定是错误。`ideal` 只是正确参考之一。只要底层约束语义正确、report 为 `pass`、validation 无错误和警告，就可以认为输出可用。
