========================================================================
Project: Analog Circuit Layout Constraint Extraction (Auto-Annotation)
Date:    2025-12-19
========================================================================

[项目简介]
本项目实现了从模拟电路 SPICE 网表到版图约束的自动提取。
流程：SPICE 网表 -> 图结构转换 -> 子图匹配 (C++ Core) -> 约束生成。

核心算法基于 HKUST SubgraphMatching 开源库，经过调试确认，
必须使用 LFTJ 引擎配合 GQL 过滤顺序才能正确输出匹配结果文件。

========================================================================
1. 目录结构说明 (Directory Structure)
========================================================================

work/place/
├── .venv/                           # [环境] Python 虚拟环境
├── Constraints_Extraction/          # [主程序目录]
│   ├── spice_annotation.py          # 核心启动脚本 (已修正引擎参数)
│   ├── circuit.json                 # 配置文件
│   ├── output/                      # [输出] 存放生成的 .graph 和结果 .txt
│   └── Constraints_Extraction_data/ # [输入] 数据源
│       ├── circuit_data/            # 存放待测电路网表 (如 .sp 文件)
│       └── query_graph/             # 存放子电路模板 (CurrentMirror.graph)
└── SubgraphMatching-master/         # [算法引擎目录]
    ├── build/                       # 编译目录
    └── matching/                    # 存放编译好的二进制文件 SubgraphMatching.out

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

========================================================================
3. 运行指南 (Usage Guide)
========================================================================

[第一步] 准备数据
1. 将你的 SPICE 网表文件（例如 test_circuit.sp）放入：
   work/place/Constraints_Extraction/Constraints_Extraction_data/circuit_data/

2. 确保模板图文件（.graph）位于：
   work/place/Constraints_Extraction/Constraints_Extraction_data/query_graph/

[第二步] 修改配置文件
打开 work/place/Constraints_Extraction/circuit.json
修改 "circuit_path" 指向你的 .sp 文件名。

[第三步] 执行自动化脚本
指令：
    cd work/place/Constraints_Extraction
    python spice_annotation.py circuit.json

========================================================================
4. 关键技术细节 (Technical Details)
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

* 注意：不要使用 VF2++ 作为 engine 参数，它在该版本中不支持 result 输出。
* 注意：必须使用 LFTJ (Local Filtering based Join) 才能启用枚举输出模式。

========================================================================
5. 输出文件说明 (Outputs)
========================================================================

运行成功后，output/ 目录下会生成如下文件：

1. *_target.graph
   由 Python 解析 SPICE 网表生成的图数据文件。

2. match_*.txt (关键结果文件)
   包含两列数字，表示“模板节点”到“电路节点”的映射关系。
   
   格式示例 (DifferentialPair 结果)：
   0 17   <-- 模板节点 0 对应 电路节点 17
   1 11   <-- 模板节点 1 对应 电路节点 11
   2 12
   ...

========================================================================
6. 常见问题排查 (Troubleshooting)
========================================================================

Q1: 运行脚本后没有报错，但 output 目录下没有 match_*.txt 文件？
A1: 检查 spice_annotation.py 代码，确认 -engine 参数是否已改为 "LFTJ"。
    如果是 "GQL"，它只计数不输出文件。

Q2: 提示 "The specified engine type 'VF2++' is not supported"？
A2: 该版本的 C++ 库将 VF2++ 视为排序方法(order)而非枚举引擎(engine)。
    请将 -engine 参数改为 LFTJ。

Q3: 提示 "Permission denied"？
A3: 给二进制文件赋予执行权限：
    chmod +x ../SubgraphMatching-master/build/matching/SubgraphMatching.out

Q4: 提示 "ModuleNotFoundError: No module named 'networkx'"？
A4: 你忘记激活虚拟环境了。请运行 source .venv/bin/activate。

========================================================================