# 三分图结构说明

本文说明工程中使用的二分图、三分图和 C++ `.graph` 文件格式。

## 原始电路图

`spice_parse2graph.py` 会先构建二分图：

```text
device node <-> net node
```

器件节点包含：

```text
inst_type: nmos / pmos / cap / res / inductor / subckt type
values: 器件参数
```

边上的 `weight` 表示端口类型。MOS 常用权重：

| weight | 含义 |
|---|---|
| `1` | drain |
| `2` | gate |
| `4` | source |

无源器件和子电路端口会使用其它权重或组合权重。

## 为什么转换成三分图

直接做 `device-net` 二分图匹配时，端口角色容易丢失。工程会把每条带权边拆成一个中间连接节点：

```text
device -- connect(weight/port role) -- net
```

这样形成三类节点：

```text
device node
connect node
net node
```

这就是三分图。

## 三分图节点含义

| 节点类型 | 来源 | 作用 |
|---|---|---|
| device | MOS、电容、电阻、电感、实例 | 表示电路实体 |
| connect | 原始边权重 | 显式表达端口角色 |
| net | 原始网络 | 表示电气连接 |

`Tools.graph_convert()` 负责该转换。

## C++ `.graph` 格式

`.graph` 文件示例：

```text
t 13 12
v 0 9 3
v 1 0 1
v 2 0 1
e 0 7
e 1 7
```

头行：

```text
t <node_count> <edge_count>
```

节点行：

```text
v <node_id> <label_id> <degree>
```

边行：

```text
e <src_id> <dst_id>
```

## label_id 约定

`Tools.graphForSubgraphMatchCXX()` 会把节点类型转为整数 label：

| 节点类型 | label 规则 |
|---|---|
| connect | 使用端口权重作为 label |
| net | 固定为 `0` |
| device | 从 `9` 开始按器件类型分配 |

因此同一个模板中的 label 不只是“节点名字”，而是匹配时的类型约束。

## 模板图和目标图

目标图：

```text
output/<circuit_name>/debug/<circuit_name>_target.graph
```

模板图：

```text
Constraints_Extraction_data/query_graph/*_target.graph
```

C++ 匹配引擎会在目标图中寻找与模板图同构的子图，并输出模板节点到目标节点的映射。

## 常见错误

| 现象 | 常见原因 |
|---|---|
| `visited_vertices` 断言失败 | query graph 有孤立节点或不连通 |
| `checkEdgeExistence` 断言失败 | `.graph` 里的 degree 或边关系不一致 |
| 没有 `match_*.txt` | 匹配失败，或 engine 参数不正确 |

## 设计建议

模板图应尽量小而有辨识度：

```text
只包含判断该结构必须依赖的器件、端口和网络关系。
```

不要把非必要网络或器件塞进模板，否则泛化能力会下降。
