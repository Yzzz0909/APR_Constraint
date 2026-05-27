# 常见 bug 与修改方式

本文记录约束提取流程中常见问题、定位方式和推荐修改点。

## 快速定位顺序

```text
1. 看 report.json 的 status 和 risks
2. 看 type_summary.missing
3. 看 pair_candidates
4. 看 constraint_validation.errors / warnings
5. 看 debug/constraints_debug.txt
6. 看 debug/match_*.txt
7. 决定改 config、parser、模板、map 还是规则
```

## C++ 引擎无法启动

现象：

```text
无法启动匹配引擎
Permission denied
No such file or directory
WinError 193
```

常见原因：

```text
subgraphmatchexe 路径错误
C++ 引擎未编译
Linux .out 在 Windows 本地执行
文件没有执行权限
```

修改方式：

```bash
cd ~/work
make build SubgraphMatching-master
chmod +x place/SubgraphMatching-master/build/matching/SubgraphMatching.out
```

检查 `circuit.json`：

```json
{
  "subgraphmatchexe": "/home/yangzhe/work/place/SubgraphMatching-master/build/matching/SubgraphMatching.out"
}
```

## 没有生成任何约束

report 特征：

```text
status = fail
risks 包含 no_constraints_generated
constraint_line_count = 0
```

常见原因：

```text
query_path 错误
模板文件缺失
C++ 匹配失败
parser 没有正确解析网表
```

修改方式：

```text
1. 检查 output/<circuit>/debug/ 是否有 target.graph
2. 检查 debug/match_*.txt 是否存在且非空
3. 检查终端是否打印 query_path 缺少模板文件
4. 检查 circuit.json 中 netlist 是否指向正确文件
```

## 顶层器件未覆盖

report 特征：

```text
risks 包含 unconstrained_top_level_devices
type_summary.*.missing 非空
```

常见原因：

```text
缺少模板
模板匹配到了但被拓扑过滤掉
规则没有覆盖该结构
子电路实例没有被保护
```

修改方式：

```text
1. 如果 missing 是 MOS，优先看 pair_candidates
2. 如果 missing 是 cap/res/instance，检查是否需要保护约束或补偿网络规则
3. 如果 missing 是子电路实例，检查 parser 是否正确识别 inst_type
4. 必要时在 ConstraintExtractor 增加通用规则
```

相关代码：

```text
ConstraintExtractor.infer_instance_constraints()
ConstraintExtractor.infer_uncovered_instance_protection()
ConstraintExtractor.audit_constraint_coverage()
```

## 子电路实例类型解析错误

现象：

```text
xr1 被解析成 segw=2e-6
实例端口包含 m=1、segl=... 等参数
```

原因：

```text
带参数的 x 实例没有正确识别子电路名。
```

正确示例：

```spice
xr1 net0239 net087 rpposab_pcell_0 m=1 segl=10e-6 segw=2e-6
```

期望解析：

```text
inst = xr1
inst_type = rpposab_pcell_0
ports = net0239, net087
```

修改位置：

```text
spice_parse2graph.py::_parse_inst()
```

修复原则：

```text
优先在已定义 .subckt 名称中查找子电路类型；
遇到第一个 key=value 参数后，不再把后续 token 当端口。
```

## 匹配结果存在但没有生成约束

现象：

```text
debug/match_*.txt 非空
constraints.txt 中没有对应约束
```

常见原因：

```text
_map.json 引用了 net/connect 节点，不是器件节点
模板名进入了错误的拓扑过滤逻辑
匹配中的器件已经被 constrained_devices 占用
```

修改方式：

```text
1. 看 constraints_debug.txt 中 valid_matches 数量
2. 如果 valid_matches=0，检查 _is_valid_template_match()
3. 如果 valid_matches>0 但没输出，检查 _map.json
4. 检查 _emit_template_constraints() 是否过滤掉已约束器件
```

## report 是 pass 但语义看起来怪

现象：

```text
status = pass
risks = []
但层次分组不符合人工直觉
```

原因：

```text
report 主要检查覆盖率、格式和基础拓扑证据；
它不会保证层次结构是唯一最优表达。
```

处理方式：

```text
如果后续流程能接受，先视为可用；
如果需要更好层次，增加专门的结构层次规则。
```

常见修改位置：

```text
infer_structured_group_hierarchy()
infer_hierarchy_groups()
```

## 当前电路输出覆盖旧结果

现象：

```text
output 下文件混乱，或者看到了旧 report
```

当前输出规则：

```text
output/<circuit_name>/
├── constraints.txt
├── report.json
└── debug/
```

修改方式：

```text
确认 circuit.json 的 netlist 字段；
同名电路会覆盖同一目录内的旧输出。
```

## 本地配置和服务器配置不一致

现象：

```text
以为跑的是 twoStageMiller，实际 netlist 还是 full_differential
```

检查：

```bash
cat place/Constraints_Extraction/circuit.json
cat place/Constraints_Extraction/circuit_local_test.json
```

重点字段：

```json
{
  "netlist": "twoStageMiller.sp"
}
```

