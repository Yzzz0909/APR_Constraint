========================================================================
Project: Analog Circuit Layout Constraint Extraction (Auto-Annotation)
Date:    2026-5-22
========================================================================

[项目简介]
本项目实现了从模拟电路 SPICE 网表到版图约束的自动提取。
流程：SPICE 网表 -> 图结构转换 -> 子图匹配 (C++ Core) -> 约束生成 -> 结果审计。

核心算法基于 HKUST SubgraphMatching 开源库，经过调试确认，
必须使用 LFTJ 引擎配合 GQL 过滤顺序才能正确输出匹配结果文件。

当前版本在原有“模板匹配 + 约束映射”的基础上，进一步加入了结构化规则推断
和 report 审计机制。工程目标不是让输出文本机械匹配某个 ideal 示例，而是根据
电路拓扑证据生成高置信度约束，并说明每条约束覆盖了哪些器件、为什么成立、
是否存在格式或拓扑风险。

========================================================================
1. 目录结构说明 (Directory Structure)
========================================================================

work/place/
├── .venv/                           # [环境] Python 虚拟环境
├── Constraints_Extraction/          # [主程序目录]
│   ├── spice_annotation.py          # 核心启动脚本
│   ├── spice_parse2graph.py         # SPICE 网表解析与电路图生成
│   ├── Tools.py                     # 图转换与 .graph 文件生成工具
│   ├── template_generator.py        # 半自动模板生成辅助工具
│   ├── circuit.json                 # 服务器运行配置文件
│   ├── circuit_local_test.json      # 本地测试配置文件
│   ├── output/                      # [输出] 生成 .graph、约束、debug、report
│   │   ├── real/                    # 当前测试电路的实际输出
│   │   ├── ideal/                   # 正确示例，仅作参考
│   │   └── local_test/              # 本地测试输出
│   └── Constraints_Extraction_data/ # [输入] 数据源
│       ├── circuit_data/            # 存放待测电路网表
│       ├── query_graph/             # 存放子电路模板 .graph
│       └── primitive_constraint_map/# 存放模板到约束的 map 文件
└── SubgraphMatching-master/         # [算法引擎目录]
    ├── build/                       # 编译目录
    └── matching/                    # 编译好的 SubgraphMatching.out

========================================================================
2. 环境准备 (Prerequisites)
========================================================================

[步骤 A] 激活 Python 虚拟环境 (每次运行前必做)
必须激活环境以加载 networkx 等依赖库。

指令：
    source .venv/bin/activate

验证：
    命令行提示符应显示 (.venv) 前缀。

[步骤 B] 编译 C++ 图匹配引擎 (首次运行必做)

指令：
    cd work/place/SubgraphMatching-master
    mkdir -p build
    cd build
    cmake ..
    make

验证：
    检查 work/place/SubgraphMatching-master/build/matching/ 目录下
    是否存在 SubgraphMatching.out 文件。

注意：
    Windows 本地环境通常不能直接运行服务器编译得到的 SubgraphMatching.out。
    如果出现 WinError 193，通常是执行环境问题，不代表 Python 主流程错误。

========================================================================
3. 运行指南 (Usage Guide)
========================================================================

[第一步] 准备数据
1. 将 SPICE 网表文件放入：
   work/place/Constraints_Extraction/Constraints_Extraction_data/circuit_data/

2. 确保模板图文件位于：
   work/place/Constraints_Extraction/Constraints_Extraction_data/query_graph/

3. 确保模板约束映射位于：
   work/place/Constraints_Extraction/Constraints_Extraction_data/primitive_constraint_map/

[第二步] 修改配置文件
打开：
    work/place/Constraints_Extraction/circuit.json

常用字段如下：
    "spice_path": 输入网表所在目录
    "netlist": 待处理网表文件名
    "out_dir": 输出目录
    "subgraphmatchexe": C++ 图匹配引擎路径
    "query_path": 模板图目录
    "query_path": 模板图目录

[第三步] 执行自动化脚本

指令：
    cd work/place/Constraints_Extraction
    python spice_annotation.py circuit.json

本地测试可使用：
    python spice_annotation.py circuit_local_test.json

========================================================================
4. 工作流程 (Pipeline)
========================================================================

主程序 spice_annotation.py 会执行以下步骤：

1. 读取配置文件，确定网表、模板、输出目录和 C++ 匹配引擎路径。
2. 解析 SPICE 网表，生成电路图。
3. 将电路图转换为三分图，并输出 *_target.graph。
4. 默认选择所有正式模板参与匹配。
5. 调用 C++ 子图匹配引擎，生成 match_*.txt。
6. 读取模板 map 文件，将匹配结果转换为初始约束。
7. 执行补充规则，推断尾电流源、实例分组、电容约束和层次结构。
8. 执行 validate_final_constraints() 和覆盖率审计。
9. 输出最终约束文件、debug 文件和 report 文件。

本项目使用三分图作为匹配图表示。三分图将器件、线网和连接关系分开建模，
使 MOS 管 gate/source/drain 等端口关系能够被图匹配引擎识别。

========================================================================
5. 关键技术细节 (Technical Details)
========================================================================

[核心指令参数]
为了确保能正确生成包含节点映射的 result.txt 文件，Python 脚本内部调用的
C++ 指令必须使用 LFTJ 引擎。

正确指令范例：
./SubgraphMatching.out \
  -d [Target_Graph] \
  -q [Template_Graph] \
  -filter GQL \
  -order GQL \
  -engine LFTJ \
  -num MAX \
  -result [Output_Path]

注意：
    1. 不要使用 VF2++ 作为 engine 参数，它在该版本中不支持 result 输出。
    2. 必须使用 LFTJ (Local Filtering based Join) 才能启用枚举输出模式。
    3. query graph 中不应存在孤立节点。
    4. .graph 文件中每个节点声明的 degree 应与实际边数一致。

[自动化设计原则]
本项目不以“和 ideal 文件完全一致”为最终目标。ideal 文件只是正确示例之一。
真正的判断标准是：
    1. 底层约束是否符合电路拓扑。
    2. 关键器件是否全部覆盖。
    3. 是否存在疑似遗漏的对称或配对关系。
    4. 最终 report 是否为 pass。
    5. constraint_validation.errors 和 warnings 是否为空。

========================================================================
6. 输出文件说明 (Outputs)
========================================================================

运行成功后，output/ 目录下会生成如下文件：

1. *_target.graph
   由 Python 解析 SPICE 网表生成的目标三分图文件。

2. match_*.txt
   C++ 子图匹配结果，表示“模板节点”到“电路节点”的映射关系。

   格式示例：
       0 17
       1 11
       2 12

3. *_final_constraints.txt
   最终版图约束文件。

   示例：
       Group_1 11 c0 1
       Group_2 3 m21 m22
       2 m21 m21
       2 m22 m22
       Group_3 6 m11 m19 m18 m1 m17

4. *_final_constraints_debug.txt
   调试文件，记录模板匹配结果、结构推断过程和覆盖率摘要。

5. *_final_constraints_report.json
   审计报告，用于判断最终约束是否可以进入后续布局布线。

常见约束编号：

| 编号 | 含义 |
|---|---|
| 1 | 二器件匹配/成对约束 |
| 3 | 对称组约束 |
| 6 | 行约束 |
| 7 | 保护约束 |
| 8 | 电流镜约束 |
| 11 | 旋转约束 |

========================================================================
7. Report 文件阅读方法 (Report Guide)
========================================================================

report 文件用于回答四个问题：
    1. 这次输出能不能直接用？
    2. 每条约束覆盖了哪些器件？
    3. 每条约束有什么拓扑证据？
    4. 是否存在格式错误、重复使用或疑似遗漏？

[第一步] 看 status 和 risks

示例：
    "status": "pass",
    "risks": []

状态含义：
    pass        覆盖完整，未发现明显格式或拓扑风险。
    need_review 输出可能可用，但存在需要人工确认的风险。
    fail        输出不能直接使用，需要修复模板、规则或验证器。

常见 risks：
    unconstrained_top_level_devices     存在未覆盖顶层器件。
    possible_missing_symmetric_pairs    存在疑似遗漏的对称或配对候选。
    invalid_constraint_format_or_topology  约束格式或拓扑校验存在错误。
    constraint_validation_warnings      约束验证存在警告。

[第二步] 看覆盖率

示例：
    "total_top_level": 13,
    "constrained": 13,
    "unconstrained": 0,
    "coverage_ratio": 1.0

如果 unconstrained 大于 0，需要查看 type_summary 中的 missing 列表。

[第三步] 看 pair_candidates

如果 pair_candidates 为空，说明未约束器件中没有发现疑似遗漏的对称或配对关系。
如果出现 cross_coupled、same_gate、matched_supply_branches 等 reason，需要人工检查。

[第四步] 看 constraint_validation

示例：
    "constraint_validation": {
      "errors": [],
      "warnings": [],
      "groups": []
    }

字段说明：
    errors    明确错误，存在时通常不能直接使用。
    warnings  可疑项，不一定错误，但需要确认。
    groups    每个约束组的详细说明。

每个 group 中常见字段：
    group             约束组名称。
    rule              约束类型编号。
    members           约束成员。
    covers            该约束覆盖的器件或实例。
    referenced_groups 引用的子 group。
    evidence          该约束成立的证据。
    pairs             对称 pair 及其拓扑证据。
    issues            该 group 内部发现的问题。

示例解释：
    "evidence": ["same_type:pmos", "shared_source", "cross_coupled"]

表示该 pair 是同类型 PMOS，source 共享，并且存在交叉耦合拓扑证据。

========================================================================
8. 半自动模板扩展工具 (Template Generator)
========================================================================

当基础模板无法覆盖某个新结构时，可以使用
Constraints_Extraction/template_generator.py 辅助生成新的模板 graph 和 map。
该工具适合少量扩展，不建议用来替代人工确认设计意图。

基本用法：
    cd work/place/Constraints_Extraction
    python template_generator.py \
      --netlist Constraints_Extraction_data/circuit_data/new_circuit.sp \
      --devices m12,m13 \
      --name BiasPair_nmos \
      --constraint symmetry

工具会生成：
    Constraints_Extraction_data/query_graph/BiasPair_nmos_target.graph
    Constraints_Extraction_data/primitive_constraint_map/BiasPair_nmos_map.json

常用 constraint 类型：
    pair            生成成对约束 1
    symmetry        生成对称组约束 3
    self_symmetry   生成自对称组约束 3
    row             生成行约束 6
    rotation        生成旋转约束 11
    current_mirror  生成电流镜约束 8

注意：
    1. 程序可以自动生成 graph 和候选 map，但不能完全判断设计意图。
    2. 生成的 map 需要人工检查后再纳入正式模板库。
    3. 新模板如果要被主流程自动选择，需要加入 spice_annotation.py 的模板优先级表。

========================================================================
9. 当前测试电路 (Current Test Cases)
========================================================================

当前 output/real/ 中主要保存三个测试电路输出：

| 电路 | 说明 | 期望状态 |
|---|---|---|
| full_differential | 全差分结构测试 | pass |
| comparator | 锁存比较器结构测试 | pass |
| bootstrap | Bootstrap switch 结构测试 | pass |

说明：
    1. output/ideal/ 中的文件只是正确参考，不要求 real 在顺序和 group 编号上完全一致。
    2. 如果底层约束语义一致，report 为 pass，且 validation 无错误和警告，则可认为输出可用。
    3. 如果 report 显示 fail 或 need_review，应优先查看 risks 和 constraint_validation。

========================================================================
10. 常见问题排查 (Troubleshooting)
========================================================================

Q1: 运行脚本后没有报错，但 output 目录下没有 match_*.txt 文件？
A1: 检查 spice_annotation.py 代码，确认 -engine 参数是否为 "LFTJ"。
    如果是 "GQL"，它只计数不输出文件。

Q2: 提示 "The specified engine type 'VF2++' is not supported"？
A2: 该版本的 C++ 库将 VF2++ 视为排序方法(order)而非枚举引擎(engine)。
    请将 -engine 参数改为 LFTJ。

Q3: 提示 "Permission denied"？
A3: 给二进制文件赋予执行权限：
    chmod +x ../SubgraphMatching-master/build/matching/SubgraphMatching.out

Q4: 提示 "ModuleNotFoundError: No module named 'networkx'"？
A4: 你忘记激活虚拟环境了。请运行：
    source .venv/bin/activate

Q5: 匹配引擎出现 visited_vertices 断言失败？
A5: 通常说明 query graph 中存在孤立节点或图结构不连通，需要检查模板 .graph。

Q6: 匹配引擎出现 checkEdgeExistence 断言失败？
A6: 通常说明 .graph 文件中的节点 degree、边关系或 query plan 所需结构不一致。

Q7: report 显示 need_review？
A7: 按顺序查看 risks、unconstrained、pair_candidates、constraint_validation.errors、
    constraint_validation.warnings。若只是验证器不认识某个合法 rule，应补充
    validate_final_constraints()；若有器件遗漏，通常需要检查模板匹配和结构规则。

Q8: real 与 ideal 不完全一致是否一定错误？
A8: 不一定。ideal 只是正确示例之一。group 编号、group 顺序、成员顺序通常不要求完全一致。
    应优先检查底层约束语义和 report 状态。

========================================================================
