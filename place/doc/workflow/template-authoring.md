# 模板文件撰写方式

本文说明如何新增或修改子图匹配模板。

## 模板由两部分组成

每个模板通常需要两个文件：

```text
query_graph/<TemplateName>_target.graph
primitive_constraint_map/<TemplateName>_map.json
```

示例：

```text
query_graph/DifferentialPair_target.graph
primitive_constraint_map/DifferentialPair_map.json
```

## `.graph` 文件作用

`.graph` 描述要匹配的拓扑结构。C++ 引擎根据它在目标三分图中找子图。

示例：

```text
t 13 12
v 0 9 3
v 1 0 1
v 2 0 1
e 0 7
e 1 7
```

格式说明见 [tripartite-graph.md](../reference/tripartite-graph.md)。

## `_map.json` 文件作用

`_map.json` 描述模板节点匹配到真实器件后，要生成什么约束。

示例：

```json
{
  "1": [["0", "4"]]
}
```

含义：

```text
模板节点 0 和模板节点 4 匹配到的真实器件，生成约束类型 1。
```

## 支持的约束类型

| 编号 | 含义 | map 示例 |
|---|---|---|
| `1` | 二器件配对约束 | `"1": [["0", "4"]]` |
| `3` | 对称组约束 | 通常放在 `"g"` 分组内 |
| `6` | 行约束 | `"6": [["0", "1", "2"]]` |
| `8` | 电流镜约束 | `"8": [["0", "4"]]` |
| `11` | 旋转约束 | `"11": [["0", "rot:1"]]` |

当前主流程还会用 Python 规则生成 `7` 保护约束和部分层次组。

## 对称组 map 写法

对称组常见写法：

```json
{
  "g": {
    "3": [
      [["0", "4"], ["1", "5"]]
    ]
  }
}
```

含义：

```text
生成一个 symmetry group，并在组内写 pair line。
```

实际处理逻辑在：

```text
ConstraintExtractor._collect_constraint_shapes()
ConstraintExtractor._emit_template_constraints()
```

## 命名约定

推荐命名：

```text
<StructureName>_<device_type>_target.graph
<StructureName>_<device_type>_map.json
```

示例：

```text
CrossCoupledPair_nmos_target.graph
CrossCoupledPair_nmos_map.json
BootstrapRow_pmos_target.graph
BootstrapRow_pmos_map.json
```

新增正式模板后，需要把文件名加入 `spice_annotation.py` 中的优先级表：

```python
PRIMITIVE_QUERY_PRIORITY
CUSTOM_QUERY_PRIORITY
```

优先级数字越小，越早匹配。

## 编写流程

推荐流程：

```text
1. 选一个已知 netlist
2. 运行主流程生成 target.graph
3. 从 target.graph 中抽取目标结构相关节点
4. 写 query_graph/*.graph
5. 写 primitive_constraint_map/*_map.json
6. 运行 make run
7. 检查 output/<circuit>/debug/match_*.txt
8. 检查 constraints.txt 和 report.json
```

也可以使用辅助工具：

```bash
cd ~/work/place/Constraints_Extraction
python template_generator.py \
  --netlist Constraints_Extraction_data/circuit_data/new_circuit.sp \
  --devices m12,m13 \
  --name BiasPair_nmos \
  --constraint symmetry
```

生成后仍需人工检查 `.graph` 和 `_map.json`。

## 调试建议

如果模板匹配过多：

```text
增加必要端口角色、器件类型或网络关系。
```

如果模板匹配不到：

```text
检查 label_id、degree、边关系和是否包含了非必要约束。
```

如果匹配到了但没有生成约束：

```text
检查 _map.json 中引用的模板节点是否是器件节点，而不是 net/connect 节点。
```
