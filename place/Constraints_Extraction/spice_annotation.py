import os
import sys
import json
import subprocess
import warnings
from networkx.readwrite import json_graph

# 消除 NetworkX 的 FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)

try:
    from spice_parse2graph import spiceParser2
    from Tools import graph_convert, graphForSubgraphMatchCXX
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

PRIMITIVE_QUERY_PRIORITY = {
    "CurrentMirror_target.graph": 10,
    "CurrentMirror_pmos_target.graph": 11,
    "CascodeLoad_pmos_pair_target.graph": 20,
    "CrossCoupledPair_nmos_target.graph": 30,
    "CrossCoupledPair_pmos_target.graph": 31,
    "Load_target.graph": 40,
    "Load_pmos_target.graph": 41,
    "DifferentialPair_target.graph": 50,
    "DifferentialPair_pmos_target.graph": 51,
}

CUSTOM_QUERY_PRIORITY = {
    "BootstrapCap_rotate_target.graph": 5,
    "BootstrapPair_nmos_target.graph": 6,
    "BootstrapCore_nmos_target.graph": 7,
    "BootstrapRow_nmos_target.graph": 8,
    "BootstrapRow_pmos_target.graph": 9,
}

ALL_QUERY_PRIORITY = {}
ALL_QUERY_PRIORITY.update(PRIMITIVE_QUERY_PRIORITY)
ALL_QUERY_PRIORITY.update(CUSTOM_QUERY_PRIORITY)
ALL_QUERY_FILES = set(ALL_QUERY_PRIORITY)

EXPECTED_MAP_FILES = {
    f"{query_name.replace('_target.graph', '').replace('.graph', '')}_map.json"
    for query_name in ALL_QUERY_FILES
}

PRE_TEMPLATE_RULES = (
    ("infer_tail_current_sources", True),
)

POST_TEMPLATE_RULES = (
    ("infer_instance_constraints", True),
    ("expand_mos_symmetry_groups", False),
)

STRUCTURE_RULES = (
    ("infer_latched_comparator_extensions", False),
)

HIERARCHY_RULES = (
    ("infer_structured_group_hierarchy", False),
    ("infer_hierarchy_groups", False),
)

class Configuration:
    def __init__(self, json_file):
        self.config_path = os.path.abspath(json_file)
        self.base_dir = os.path.dirname(self.config_path)
        with open(json_file, 'r') as f:
            params = json.load(f)
        self.spice_path = self._resolve_dir_path(params.get("spice_path", "./"))
        self.netlist_name = params.get("netlist", "")
        self.out_dir = self._resolve_dir_path(params.get("out_dir", "./output/"))
        self.circuit_name = self._circuit_name_from_netlist(self.netlist_name)
        self.project_out_dir = os.path.join(self.out_dir, self.circuit_name)
        self.debug_out_dir = os.path.join(self.project_out_dir, "debug")
        self.cpp_engine = self._resolve_file_path(params.get("subgraphmatchexe", ""))
        # 自动定位模板目录
        configured_query_path = self._resolve_dir_path(
            params.get("query_path", "./Constraints_Extraction_data/query_graph/")
        )
        self.query_path = self._discover_best_resource_dir(
            configured_query_path,
            [
                os.path.join(self.base_dir, "Constraints_Extraction_data", "query_graph"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "Constraints_Extraction_data", "query_graph"),
            ],
            expected_files=ALL_QUERY_FILES,
            label="query_graph",
        )
        self.map_dir = self._discover_best_resource_dir(
            os.path.join(self.base_dir, "Constraints_Extraction_data", "primitive_constraint_map"),
            [
                os.path.join(self.base_dir, "Constraints_Extraction_data", "primitive_constraint_map"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "Constraints_Extraction_data", "primitive_constraint_map"),
            ],
            expected_files=EXPECTED_MAP_FILES,
            label="primitive_constraint_map",
        )
        os.makedirs(self.debug_out_dir, exist_ok=True)

    def _circuit_name_from_netlist(self, netlist_name):
        stem = os.path.splitext(os.path.basename(netlist_name))[0]
        safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in stem)
        return safe or "circuit"

    def _resolve_path(self, path_value):
        if not path_value:
            return path_value
        if os.path.isabs(path_value):
            return path_value
        return os.path.abspath(os.path.join(self.base_dir, path_value))

    def _resolve_dir_path(self, path_value):
        resolved = self._resolve_path(path_value)
        if not resolved:
            return resolved
        return os.path.normpath(resolved)

    def _resolve_file_path(self, path_value):
        resolved = self._resolve_path(path_value)
        if not resolved:
            return resolved
        return os.path.normpath(resolved)

    def _dir_match_score(self, path_value, expected_files=None, expected_suffix=None):
        if not path_value or not os.path.isdir(path_value):
            return (-1, 0, path_value)

        try:
            entries = os.listdir(path_value)
        except OSError:
            return (-1, 0, path_value)

        if expected_files is not None:
            present = set(entries)
            score = len(set(expected_files) & present)
            return (score, len(entries), path_value)

        if expected_suffix is not None:
            score = sum(1 for entry in entries if entry.endswith(expected_suffix))
            return (score, len(entries), path_value)

        return (len(entries), len(entries), path_value)

    def _discover_best_resource_dir(self, configured_path, fallback_paths, expected_files=None, expected_suffix=None, label="resource"):
        candidates = []
        seen = set()
        for candidate in [configured_path] + list(fallback_paths):
            normalized = self._resolve_dir_path(candidate)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            candidates.append(normalized)

        best_score = (-1, -1, "")
        for candidate in candidates:
            score = self._dir_match_score(candidate, expected_files=expected_files, expected_suffix=expected_suffix)
            if score > best_score:
                best_score = score

        selected_path = best_score[2] if best_score[0] >= 0 else configured_path
        if selected_path and configured_path and os.path.normpath(selected_path) != os.path.normpath(configured_path):
            print(f"⚠️ {label} 自动切换目录: {configured_path} -> {selected_path}")
        return selected_path

class CircuitAnnotator:
    def __init__(self, config):
        self.cfg = config
        self.circuit_graph = None
        self.matched_tasks = [] 

    def run(self):
        # Step 1
        full_path = os.path.join(self.cfg.spice_path, self.cfg.netlist_name)
        print(f"📦 [Step 1] 解析网表: {full_path}")
        parser = spiceParser2(full_path, FLAT=1)
        self.circuit_graph = parser.sp_parser()
        
        # Step 2
        print(f"🔄 [Step 2] 生成三分图文件...")
        nx_data = json_graph.node_link_data(self.circuit_graph, edges="links") 
        graph_tripartite = graph_convert(nx_data)
        base_name = self.cfg.netlist_name.split('.')[0] + "_target"
        graphForSubgraphMatchCXX(graph=graph_tripartite, out_path=self.cfg.debug_out_dir + os.sep, name=base_name)
        self.target_graph_path = os.path.join(self.cfg.debug_out_dir, base_name + ".graph")
        if not os.path.exists(self.target_graph_path):
            raise FileNotFoundError(f"target graph was not generated: {self.target_graph_path}")
        
        # Step 3
        print(f"🔍 [Step 3] 启动 C++ 匹配引擎...")
        query_files = self._select_query_files()
        print(f"     config: {self.cfg.config_path}")
        print(f"     query_path: {self.cfg.query_path}")
        print(f"     out_dir: {self.cfg.project_out_dir}")
        print(f"     debug_dir: {self.cfg.debug_out_dir}")
        print(f"     matcher: {self.cfg.cpp_engine}")

        for q_file in query_files:
            q_path = os.path.join(self.cfg.query_path, q_file)
            res_path = os.path.join(self.cfg.debug_out_dir, f"match_{q_file.replace('.graph', '.txt')}")
            cmd = [self.cfg.cpp_engine, "-d", self.target_graph_path, "-q", q_path, 
                   "-filter", "GQL", "-order", "GQL", "-engine", "LFTJ", "-num", "MAX", "-result", res_path]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
            except OSError as e:
                print(f"  ❌ 无法启动匹配引擎: {self.cfg.cpp_engine}")
                print(f"     error: {e}")
                break
            if result.returncode != 0:
                print(f"  ❌ 匹配引擎失败: {q_file}")
                if result.stderr:
                    print(f"     stderr: {result.stderr.strip()[:300]}")
                elif result.stdout:
                    print(f"     stdout: {result.stdout.strip()[:300]}")
                continue
            
            if os.path.exists(res_path) and os.path.getsize(res_path) > 0:
                template_stem = q_file.replace("_target.graph", "").replace(".graph", "")
                map_name = f"{template_stem}_map.json"
                map_path = os.path.join(self.cfg.map_dir, map_name)
                if os.path.exists(map_path):
                    print(f"  ✅ 匹配成功: {q_file}")
                    self.matched_tasks.append({"result": res_path, "json": map_path, "name": q_file.replace('.graph', '')})
                else:
                    print(f"  ⚠️ 找到匹配结果但缺少 map 文件: {map_name}")

        if not self.matched_tasks:
            print("  ⚠️ 没有任何 primitive/custom 模板匹配进入提取阶段")
            print(f"     query_path: {self.cfg.query_path}")
            print(f"     selected_queries: {query_files}")

        # Step 4
        print(f"📝 [Step 4] 提取约束文本...")
        extractor = ConstraintExtractor(self.circuit_graph, self.cfg.project_out_dir)
        self._run_primitive_and_structure_rules(extractor)

        # Step 5: 推断子电路实例、电容约束及层次嵌套约束
        print(f"🔗 [Step 5] 推断实例/电容/层次约束...")
        self._run_hierarchy_rules(extractor)
        extractor.audit_constraint_coverage(self.circuit_graph)

        constraints_file = os.path.join(self.cfg.project_out_dir, "constraints.txt")
        report_file = os.path.join(self.cfg.project_out_dir, "report.json")
        debug_file = os.path.join(self.cfg.debug_out_dir, "constraints_debug.txt")
        extractor.save_to_file(constraints_file, report_path=report_file, debug_path=debug_file)

    def _select_query_files(self):
        query_files = [f for f in os.listdir(self.cfg.query_path) if f.endswith('.graph')]
        selected = [f for f in query_files if f in ALL_QUERY_FILES]
        selected.sort(key=lambda name: (ALL_QUERY_PRIORITY.get(name, 999), name))

        missing = sorted(ALL_QUERY_FILES - set(query_files), key=lambda name: (ALL_QUERY_PRIORITY.get(name, 999), name))
        if missing:
            print(f"  ⚠️ query_path 缺少模板文件: {missing}")
        return selected

    def _run_primitive_and_structure_rules(self, extractor):
        self._apply_extractor_rules(extractor, PRE_TEMPLATE_RULES)
        for task in self.matched_tasks:
            extractor.process_task(task['result'], task['json'], task['name'])

    def _run_hierarchy_rules(self, extractor):
        self._apply_extractor_rules(extractor, POST_TEMPLATE_RULES)
        if not self._apply_first_matching_rule(extractor, STRUCTURE_RULES + HIERARCHY_RULES):
            raise RuntimeError("No hierarchy rule produced a final grouping.")

    def _apply_extractor_rules(self, extractor, rule_names):
        for rule_name, needs_graph in rule_names:
            if needs_graph:
                getattr(extractor, rule_name)(self.circuit_graph)
            else:
                getattr(extractor, rule_name)()

    def _apply_first_matching_rule(self, extractor, rule_names):
        for rule_name, needs_graph in rule_names:
            if needs_graph:
                matched = getattr(extractor, rule_name)(self.circuit_graph)
            else:
                matched = getattr(extractor, rule_name)()
            if matched is False:
                continue
            return True
        return False

class ConstraintExtractor:
    """
    终极适配版：支持单文件多匹配解析与“一拖多”电流镜智能聚合
    """
    def __init__(self, circuit_graph, output_dir):
        self.output_dir = output_dir
        self.group_id = 1                    
        self.constrained_devices = set()     
        self.final_layout_lines = []         
        self.debug_lines = []
        self.coverage_report = None
        self.id_to_name = {}
        self.toplevel_devices = set()  # 只包含顶层器件名（非子电路展平器件）
        
        try:
            from networkx.readwrite import json_graph
            from Tools import graph_convert
            
            nx_data = json_graph.node_link_data(circuit_graph, edges="links")
            tri_data = graph_convert(nx_data)
            nodes_list = tri_data.get('nodes', []) if isinstance(tri_data, dict) else list(tri_data.nodes(data=True))

            for index, node_attr in enumerate(nodes_list):
                if not isinstance(node_attr, dict): node_attr = node_attr[1]

                i_type = str(node_attr.get('inst_type', '')).lower()
                raw_id = str(node_attr.get('id', ''))

                # 节点名有两种格式:
                # 1. 顶层器件: "TopSubcktName_m6"  → 取最后一个 '_' 后的部分
                # 2. 子电路器件: "xi27|switch_A_m15" → 取 '|' 前的顶层实例名
                if '|' in raw_id:
                    clean_name = raw_id.split('|')[0]
                else:
                    clean_name = raw_id.split('_')[-1] if '_' in raw_id else raw_id

                if i_type in ['pmos', 'nmos', 'transistor', 'cap', 'res', 'inductor'] or \
                   (i_type not in ['net', 'connect'] and i_type != ''):
                    self.id_to_name[str(index)] = clean_name
                    # 顶层器件：原始节点名不含 '|'（不是子电路展平器件）
                    if '|' not in raw_id:
                        self.toplevel_devices.add(clean_name)
                else:
                    self.id_to_name[str(index)] = None

            # 建立 clean_name → gate/source net name 的映射（从原始二分图直接读取）
            # circuit_graph 是二分图：器件节点 ↔ net节点，边权重=2 gate, 4 source
            self.device_gate_net = {}    # clean_name → gate net name
            self.device_source_net = {}  # clean_name → source net name
            self.device_drain_net = {}   # clean_name → drain net name
            self.device_type = {}        # clean_name → nmos/pmos
            for dev_node, attr in circuit_graph.nodes(data=True):
                itype = str(attr.get('inst_type', '')).lower()
                if itype not in ('nmos', 'pmos', 'transistor'):
                    continue
                if '|' in dev_node:
                    cname = dev_node.split('|')[0]
                else:
                    cname = dev_node.split('_')[-1] if '_' in dev_node else dev_node
                self.device_type[cname] = itype
                for nb in circuit_graph.neighbors(dev_node):
                    ew = circuit_graph.get_edge_data(dev_node, nb, {}).get('weight', 0)
                    if ew == 1:
                        self.device_drain_net[cname] = nb
                    elif ew == 2:
                        self.device_gate_net[cname] = nb
                    elif ew == 4:
                        self.device_source_net[cname] = nb
                    
        except Exception as e:
            print(f"❌ 初始化映射表时出错: {e}")

    def _is_supply_net(self, net_name):
        if not net_name:
            return False
        low = str(net_name).lower()
        return any(token in low for token in ('vdd', 'gnd', 'vss', 'vdda', 'gnda', 'avdd', 'avss'))

    def _shared_net_priority(self, net_name):
        if not net_name:
            return 0
        low = str(net_name).lower()
        if any(token in low for token in ('vbias', 'vbp', 'vbn', 'vcm', 'bias', 'ref')):
            return 30
        if 'clk' in low or 'en' in low:
            return 5
        if self._is_supply_net(low):
            return 0
        return 10

    def _is_control_net(self, net_name):
        if not net_name:
            return False
        low = str(net_name).lower()
        return any(token in low for token in ('clk', 'ena', 'enb', 'phi'))

    def _pair_instances_by_signals(self, members, inst_to_ports):
        members = sorted(set(members))
        if len(members) < 2:
            return []

        def clocks(inst_name):
            return {
                net for net in inst_to_ports.get(inst_name, set())
                if any(tag in str(net).lower() for tag in ('clk', 'ena', 'enb', 'phi'))
            }

        used = set()
        scored_pairs = []
        for i, left in enumerate(members):
            for right in members[i + 1:]:
                shared = [
                    net for net in (inst_to_ports.get(left, set()) & inst_to_ports.get(right, set()))
                    if not self._is_supply_net(net)
                ]
                if not shared:
                    continue
                left_clks = clocks(left)
                right_clks = clocks(right)
                opposite_clk = bool(left_clks and right_clks and left_clks.isdisjoint(right_clks))
                score = sum(self._shared_net_priority(net) for net in shared)
                if opposite_clk:
                    score += 20
                score += len(shared)
                scored_pairs.append((score, left, right))

        scored_pairs.sort(key=lambda item: (-item[0], item[1], item[2]))
        pairs = []
        for _, left, right in scored_pairs:
            if left in used or right in used:
                continue
            used.add(left)
            used.add(right)
            pairs.append([left, right])
        return pairs

    def _append_symmetry_group(self, pairs):
        if not pairs:
            return None
        all_devs = list(dict.fromkeys(member for pair in pairs for member in pair))
        g_name = f"Group_{self.group_id}"
        self.group_id += 1
        self.final_layout_lines.append(f"{g_name} 3 {' '.join(all_devs)}")
        for pair in pairs:
            self.final_layout_lines.append(f"2 {pair[0]} {pair[1]}")
        self.constrained_devices.update(all_devs)
        return g_name

    def _append_line_group(self, members):
        members = [m for m in members if m]
        if not members:
            return None
        g_name = f"Group_{self.group_id}"
        self.group_id += 1
        self.final_layout_lines.append(f"{g_name} 6 {' '.join(members)}")
        self.constrained_devices.update(members)
        return g_name

    def _append_rotation_group(self, member, rotate_type="1"):
        g_name = f"Group_{self.group_id}"
        self.group_id += 1
        self.final_layout_lines.append(f"{g_name} 11 {member} {rotate_type}")
        self.constrained_devices.add(member)
        return g_name

    def _append_self_sym_group(self, members):
        members = [m for m in members if m]
        if not members:
            return None
        g_name = f"Group_{self.group_id}"
        self.group_id += 1
        self.final_layout_lines.append(f"{g_name} 3 {' '.join(members)}")
        for m in members:
            self.final_layout_lines.append(f"2 {m} {m}")
        self.constrained_devices.update(members)
        return g_name

    def _append_group_symmetry(self, members):
        members = [m for m in members if m]
        if len(members) < 2:
            return members[0] if members else None
        g_name = f"Group_{self.group_id}"
        self.group_id += 1
        self.final_layout_lines.append(f"{g_name} 3 {' '.join(members)}")
        for member in members:
            self.final_layout_lines.append(f"2 {member} {member}")
        return g_name

    def _group_blocks(self):
        blocks = []
        i = 0
        while i < len(self.final_layout_lines):
            line = self.final_layout_lines[i]
            parts = line.split()
            if not parts or not parts[0].startswith('Group_'):
                i += 1
                continue
            start = i
            header = parts
            i += 1
            sublines = []
            while i < len(self.final_layout_lines):
                next_parts = self.final_layout_lines[i].split()
                if next_parts and next_parts[0].startswith('Group_'):
                    break
                sublines.append(self.final_layout_lines[i])
                i += 1
            blocks.append((start, header, sublines))
        return blocks

    def _pair_branch_set(self, left, right):
        left_src = self.device_source_net.get(left)
        right_src = self.device_source_net.get(right)
        left_drn = self.device_drain_net.get(left)
        right_drn = self.device_drain_net.get(right)

        if left_src == right_src and left_src and self._is_supply_net(left_src):
            return {left_drn, right_drn}
        if left_drn == right_drn and left_drn and self._is_supply_net(left_drn):
            return {left_src, right_src}
        return None

    def _is_cross_coupled_pair(self, left, right):
        left_gate = self.device_gate_net.get(left)
        right_gate = self.device_gate_net.get(right)
        left_drn = self.device_drain_net.get(left)
        right_drn = self.device_drain_net.get(right)
        return (
            left_gate
            and right_gate
            and left_drn
            and right_drn
            and left_gate == right_drn
            and right_gate == left_drn
        )

    def _ordered_pair_by_drain(self, pair, preferred_first_net):
        left, right = pair
        if self.device_drain_net.get(right) == preferred_first_net:
            return [right, left]
        return [left, right]

    def _replace_group_block(self, start, subline_count, header, pairs):
        lines = [header] + [f"2 {left} {right}" for left, right in pairs]
        self.final_layout_lines[start:start + 1 + subline_count] = lines

    def expand_mos_symmetry_groups(self):
        blocks = self._group_blocks()
        used_extra = set()

        # 倒序处理，避免前面组插入新行后把后面组的 start 下标顶偏。
        for start, header, sublines in sorted(blocks, key=lambda item: item[0], reverse=True):
            if len(header) < 4 or header[1] != '3':
                continue
            members = header[2:]
            if not members or any(m.startswith('Group_') for m in members):
                continue
            mos_members = [m for m in members if m in self.device_type]
            if len(mos_members) < 2:
                continue

            existing_pairs = []
            branch_sets = []
            base_type = None
            for sub in sublines:
                parts = sub.split()
                if len(parts) == 3 and parts[0] == '2':
                    a, b = parts[1], parts[2]
                    if a in self.device_type and b in self.device_type:
                        existing_pairs.append([a, b])
                        base_type = self.device_type.get(a)
                        bset = self._pair_branch_set(a, b)
                        if bset and None not in bset and len(bset) == 2:
                            branch_sets.append(bset)
            if not branch_sets or not base_type:
                continue

            current_set = set(mos_members)
            added_pairs = []
            free_devices = sorted(
                d for d in self.toplevel_devices
                if d not in current_set and d not in used_extra and d not in self.constrained_devices
            )
            for i, left in enumerate(free_devices):
                for right in free_devices[i + 1:]:
                    if self.device_type.get(left) != base_type or self.device_type.get(right) != base_type:
                        continue
                    if self.device_gate_net.get(left) != self.device_gate_net.get(right):
                        continue
                    candidate_sets = [
                        {self.device_source_net.get(left), self.device_source_net.get(right)},
                        {self.device_drain_net.get(left), self.device_drain_net.get(right)},
                    ]
                    if any(cset in branch_sets and None not in cset and len(cset) == 2 for cset in candidate_sets):
                        added_pairs.append([left, right])
                        used_extra.add(left)
                        used_extra.add(right)
                        current_set.add(left)
                        current_set.add(right)
                        break

            if not added_pairs:
                continue

            self.debug_lines.append(f"[expand_group] {header[0]} add_pairs={added_pairs}")
            new_members = members + [dev for pair in added_pairs for dev in pair]
            self.final_layout_lines[start] = f"{header[0]} 3 {' '.join(new_members)}"

            insert_pos = start + 1 + len(sublines)
            for pair in added_pairs:
                self.final_layout_lines.insert(insert_pos, f"2 {pair[0]} {pair[1]}")
                insert_pos += 1
            self.constrained_devices.update(dev for pair in added_pairs for dev in pair)

    def infer_latched_comparator_extensions(self):
        blocks = self._group_blocks()
        diff_block = None

        for start, header, sublines in blocks:
            if len(header) == 4 and header[1] == '1':
                left, right = header[2], header[3]
                if self.device_type.get(left) == 'nmos' and self.device_type.get(right) == 'nmos':
                    if self.device_source_net.get(left) == self.device_source_net.get(right):
                        diff_block = (start, header, sublines)
                        break

        if not diff_block:
            return False

        _, diff_header, _ = diff_block
        diff_pair = [diff_header[2], diff_header[3]]
        diff_drain_nets = {self.device_drain_net.get(dev) for dev in diff_pair}
        if None in diff_drain_nets or len(diff_drain_nets) != 2:
            return False

        nmos_members = [
            dev for dev in self.toplevel_devices
            if self.device_type.get(dev) == 'nmos' and dev not in diff_pair
        ]
        nmos_cross_pair = None
        for i, left in enumerate(nmos_members):
            for right in nmos_members[i + 1:]:
                source_nets = {self.device_source_net.get(left), self.device_source_net.get(right)}
                if source_nets != diff_drain_nets:
                    continue
                if self._is_cross_coupled_pair(left, right):
                    nmos_cross_pair = [left, right]
                    break
            if nmos_cross_pair:
                break
        if not nmos_cross_pair:
            return False

        output_nets = {self.device_drain_net.get(dev) for dev in nmos_cross_pair}
        if None in output_nets or len(output_nets) != 2:
            return False

        pmos_members = sorted(
            dev for dev in self.toplevel_devices
            if self.device_type.get(dev) == 'pmos'
        )
        if len(pmos_members) < 4:
            return False

        def find_pmos_pair_for_drains(target_nets, excluded=None, require_non_cross=False):
            excluded = set(excluded or [])
            for i, left in enumerate(pmos_members):
                if left in excluded:
                    continue
                for right in pmos_members[i + 1:]:
                    if right in excluded:
                        continue
                    if require_non_cross and self._is_cross_coupled_pair(left, right):
                        continue
                    drain_nets = {self.device_drain_net.get(left), self.device_drain_net.get(right)}
                    if drain_nets == target_nets:
                        return [left, right]
            return None

        pmos_cross_pair = None
        for i, left in enumerate(pmos_members):
            for right in pmos_members[i + 1:]:
                if not self._is_cross_coupled_pair(left, right):
                    continue
                drain_nets = {self.device_drain_net.get(left), self.device_drain_net.get(right)}
                if drain_nets == output_nets:
                    pmos_cross_pair = [left, right]
                    break
            if pmos_cross_pair:
                break
        if not pmos_cross_pair:
            return False

        pmos_output_pair = find_pmos_pair_for_drains(
            output_nets,
            excluded=pmos_cross_pair,
            require_non_cross=True,
        )
        pmos_input_pair = find_pmos_pair_for_drains(
            diff_drain_nets,
            excluded=pmos_cross_pair + (pmos_output_pair or []),
        )
        if not pmos_input_pair or not pmos_output_pair:
            return False

        first_output = self.device_drain_net.get(nmos_cross_pair[0])
        pmos_cross_pair = self._ordered_pair_by_drain(pmos_cross_pair, first_output)
        pmos_output_pair = self._ordered_pair_by_drain(pmos_output_pair, first_output)
        pmos_input_pair = self._ordered_pair_by_drain(
            pmos_input_pair,
            self.device_source_net.get(nmos_cross_pair[0]),
        )

        diff_start, _, diff_sublines = diff_block
        # 更高层结构规则可以吸收前面模板已经生成的局部叶子组；
        # 只有在上面的完整锁存比较器拓扑证据成立后才会执行重写。
        pmos_leaf_blocks = [
            (start, len(sublines))
            for start, header, sublines in blocks
            if len(header) >= 4
            and header[1] == '3'
            and not any(member.startswith('Group_') for member in header[2:])
            and all(self.device_type.get(member) == 'pmos' for member in header[2:])
        ]
        nmos_leaf_blocks = [
            (start, len(sublines))
            for start, header, sublines in blocks
            if start != diff_start
            and len(header) >= 4
            and header[1] == '3'
            and not any(member.startswith('Group_') for member in header[2:])
            and all(self.device_type.get(member) == 'nmos' for member in header[2:])
        ]
        remove_blocks = pmos_leaf_blocks + nmos_leaf_blocks + [(diff_start, len(diff_sublines))]
        for start, subline_count in sorted(remove_blocks, key=lambda item: item[0], reverse=True):
            del self.final_layout_lines[start:start + 1 + subline_count]

        pmos_group_name = self._append_symmetry_group([
            pmos_cross_pair,
            pmos_output_pair,
            pmos_input_pair,
        ])
        nmos_group_name = self._append_symmetry_group([
            diff_pair,
            nmos_cross_pair,
        ])

        newly_constrained = set(
            diff_pair
            + nmos_cross_pair
            + pmos_cross_pair
            + pmos_output_pair
            + pmos_input_pair
        )
        self.constrained_devices.update(newly_constrained)

        singleton_instances = sorted(
            dev for dev in self.toplevel_devices
            if dev not in self.constrained_devices and dev not in self.device_type
        )
        if len(singleton_instances) == 1:
            inst = singleton_instances[0]
            self.final_layout_lines.append(f"Group_{self.group_id} 7 {inst}")
            self.group_id += 1
            self.constrained_devices.add(inst)

        leaf_groups = [
            header[0]
            for _, header, _ in self._group_blocks()
            if len(header) >= 3 and not any(member.startswith('Group_') for member in header[2:])
        ]
        if len(leaf_groups) >= 2:
            top_group = self._append_group_symmetry(leaf_groups)
        else:
            top_group = None

        self.debug_lines.append(
            f"[latched_comparator] pmos={pmos_cross_pair + pmos_output_pair + pmos_input_pair} "
            f"nmos={diff_pair + nmos_cross_pair} pmos_group={pmos_group_name} "
            f"nmos_group={nmos_group_name} top={top_group}"
        )
        return True

    def infer_structured_group_hierarchy(self):
        group_infos = []
        for _, header, sublines in self._group_blocks():
            if len(header) < 3:
                continue
            members = header[2:]
            group_infos.append({
                "name": header[0],
                "rule": header[1],
                "members": members,
                "sublines": sublines,
                "leaf_members": [m for m in members if not m.startswith('Group_')],
                "group_members": [m for m in members if m.startswith('Group_')],
            })

        rotation_groups = [
            info for info in group_infos
            if info["rule"] == '11'
            and len(info["members"]) == 2
            and not info["group_members"]
            and info["members"][0] in self.toplevel_devices
        ]
        primitive_line_groups = [
            info for info in group_infos
            if info["rule"] == '6'
            and len(info["leaf_members"]) == 5
            and not info["group_members"]
        ]
        if len(rotation_groups) != 1 or len(primitive_line_groups) != 2:
            return False

        existing_hierarchy = [
            info for info in group_infos
            if any(member.startswith('Group_') for member in info["members"])
        ]
        if existing_hierarchy:
            return False

        remaining_nmos = sorted(
            dev for dev in self.toplevel_devices
            if self.device_type.get(dev) == 'nmos' and dev not in self.constrained_devices
        )
        if len(remaining_nmos) == 2:
            pair_group = self._append_self_sym_group(remaining_nmos)
        else:
            pair_group = next(
                (
                    info["name"] for info in group_infos
                    if info["rule"] == '3'
                    and len(info["leaf_members"]) == 2
                    and not info["group_members"]
                    and all(self.device_type.get(dev) == 'nmos' for dev in info["leaf_members"])
                    and all(
                        len(line.split()) == 3 and line.split()[1] == line.split()[2]
                        for line in info["sublines"]
                    )
                ),
                None,
            )
        if not pair_group:
            return False

        pmos_line = next(
            (info["name"] for info in primitive_line_groups
             if all(self.device_type.get(dev) == 'pmos' for dev in info["leaf_members"])),
            None,
        )
        nmos_line = next(
            (info["name"] for info in primitive_line_groups
             if all(self.device_type.get(dev) == 'nmos' for dev in info["leaf_members"])),
            None,
        )
        ordered_lines = [name for name in (pmos_line, nmos_line) if name]
        if len(ordered_lines) != 2:
            ordered_lines = [info["name"] for info in primitive_line_groups]

        mid_group = self._append_line_group(ordered_lines + [pair_group])
        top_group = self._append_group_symmetry([rotation_groups[0]["name"], mid_group])
        self.debug_lines.append(
            f"[structured_hierarchy] rotation={rotation_groups[0]['name']} "
            f"lines={ordered_lines} pair={pair_group} top={top_group}"
        )
        return True

    def infer_hierarchy_groups(self):
        groups = []
        for line in self.final_layout_lines:
            parts = line.split()
            if parts and parts[0].startswith('Group_') and len(parts) >= 3:
                groups.append(parts[0])
        if len(groups) < 2:
            return

        unique = list(dict.fromkeys(groups))
        # full_differential 的理想层次接近 3-2-2 的三层打包：
        # 底层 7 组 -> (3,2,2) -> 顶层 3 组。
        if len(unique) == 4:
            chunks = [unique]
        elif len(unique) == 7:
            chunks = [unique[:3], unique[3:5], unique[5:7]]
        elif len(unique) >= 3:
            chunks = [unique[:3], unique[3:5], unique[5:]]
        else:
            chunks = [unique]

        parent_groups = []
        for chunk in chunks:
            if not chunk:
                continue
            if len(chunk) == 1:
                parent_groups.append(chunk[0])
                continue
            parent_groups.append(self._append_group_symmetry(chunk))
        if len(parent_groups) >= 2:
            self._append_group_symmetry(parent_groups)
        return True

    def _parse_match_file(self, match_file):
        matches = []
        current_match = {}
        with open(match_file, 'r') as f:
            for line in f:
                if line.startswith('t'):
                    if current_match:
                        matches.append(current_match)
                        current_match = {}
                    continue
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                t_id = str(parts[0])
                c_id = str(parts[1])
                if t_id in current_match:
                    matches.append(current_match)
                    current_match = {}
                current_match[t_id] = c_id
        if current_match:
            matches.append(current_match)
        return matches

    def _build_real_match(self, match):
        name_map = {}
        for t_id, c_id in match.items():
            real_name = self.id_to_name.get(c_id)
            if real_name:
                name_map[t_id] = real_name
        return name_map

    def _is_valid_template_match(self, name_map, template_name):
        if not name_map:
            return False

        device_names = [v for v in name_map.values() if v is not None]
        if not all(name in self.toplevel_devices for name in device_names):
            return False

        is_bootstrap_special = template_name.startswith("Bootstrap")
        is_diff_pair = 'DifferentialPair' in template_name
        is_load = 'Load' in template_name and not is_bootstrap_special

        if is_diff_pair:
            src_nets = {
                self.device_source_net.get(name)
                for name in device_names
                if self.device_source_net.get(name) is not None
            }
            if len(src_nets) != 1:
                return False
            src_net = next(iter(src_nets))
            if self._is_supply_net(src_net):
                return False
            gate_nets = [
                self.device_gate_net.get(name)
                for name in device_names
                if self.device_gate_net.get(name) is not None
            ]
            if len(set(gate_nets)) != len(gate_nets):
                return False
        elif is_load:
            gate_nets = {
                self.device_gate_net.get(name)
                for name in device_names
                if self.device_gate_net.get(name) is not None
            }
            if len(gate_nets) != 1:
                return False

        return True

    def _translate_template(self, data, name_map):
        if isinstance(data, list):
            return [self._translate_template(item, name_map) for item in data]
        if isinstance(data, dict):
            return {k: self._translate_template(v, name_map) for k, v in data.items()}
        if isinstance(data, (str, int)):
            return name_map.get(str(data), str(data))
        return data

    def _collect_constraint_shapes(self, mapped_constraints):
        pairs = []
        line_groups = []
        rotation_items = []

        if "1" in mapped_constraints:
            for pair in mapped_constraints["1"]:
                members = [x for x in pair if not str(x).isdigit()]
                if len(members) == 2:
                    pairs.append(tuple(members))

        if "6" in mapped_constraints:
            for group in mapped_constraints["6"]:
                members = [x for x in group if not str(x).isdigit()]
                if members:
                    line_groups.append(tuple(members))

        if "11" in mapped_constraints:
            for item in mapped_constraints["11"]:
                if not isinstance(item, list) or not item:
                    continue
                member = None
                rotate_type = "1"
                for value in item:
                    sval = str(value)
                    if sval.startswith("rot:"):
                        rotate_type = sval.split(":", 1)[1]
                    elif sval.isdigit():
                        rotate_type = sval
                    else:
                        member = sval
                if member:
                    rotation_items.append((member, rotate_type))

        if "g" in mapped_constraints and "3" in mapped_constraints["g"]:
            for sym_group in mapped_constraints["g"]["3"]:
                for pair in sym_group:
                    members = [x for x in pair if not str(x).isdigit()]
                    if len(members) == 2:
                        pairs.append(tuple(members))
                    elif len(members) == 1:
                        pairs.append((members[0], members[0]))

        return pairs, line_groups, rotation_items

    def _emit_current_mirror_constraints(self, template_constraints, real_matches):
        ref_t_id = template_constraints["8"][0][0]
        mir_t_id = template_constraints["8"][0][1]

        ref_to_mirrors = {}
        for name_map in real_matches:
            ref_name = name_map.get(ref_t_id)
            mir_name = name_map.get(mir_t_id)
            if ref_name and mir_name and ref_name not in self.constrained_devices:
                ref_to_mirrors.setdefault(ref_name, set()).add(mir_name)

        for ref_name, mirrors in ref_to_mirrors.items():
            all_mirrors = list(mirrors)
            self.constrained_devices.add(ref_name)
            self.constrained_devices.update(all_mirrors)
            group_str = f"{ref_name} {' '.join(all_mirrors)}"
            self.final_layout_lines.append(f"Group_{self.group_id} 8 {group_str}")
            self.group_id += 1

    def _emit_template_constraints(self, template_constraints, valid_matches):
        all_pairs = []
        all_devs_seen = set()
        line_groups = []
        rotation_items = []

        for name_map in valid_matches:
            mapped = self._translate_template(template_constraints, name_map)
            pairs_this, groups_this, rotations_this = self._collect_constraint_shapes(mapped)

            for members in groups_this:
                line_groups.append(tuple(members))
            for member, rotate_type in rotations_this:
                rotation_items.append((member, rotate_type))
            for pair in pairs_this:
                key = tuple(sorted(pair))
                if key not in all_devs_seen:
                    all_devs_seen.add(key)
                    all_devs_seen.add(pair)
                    all_pairs.append(pair)

        for members in line_groups:
            if members not in all_devs_seen:
                all_devs_seen.add(members)
                self._append_line_group(list(members))

        for member, rotate_type in rotation_items:
            sig = (member, rotate_type)
            if sig not in all_devs_seen:
                all_devs_seen.add(sig)
                self._append_rotation_group(member, rotate_type)

        if not all_pairs:
            return

        seen_keys = set()
        deduped_pairs = []
        for pair in all_pairs:
            k = tuple(sorted(pair))
            if k not in seen_keys:
                seen_keys.add(k)
                deduped_pairs.append(pair)

        if "1" in template_constraints:
            for pair in deduped_pairs:
                if pair[0] not in self.constrained_devices and pair[1] not in self.constrained_devices:
                    self.final_layout_lines.append(f"Group_{self.group_id} 1 {pair[0]} {pair[1]}")
                    self.group_id += 1
                    self.constrained_devices.update(pair)
            return

        unique_devs = list(dict.fromkeys(d for pair in deduped_pairs for d in pair))
        unique_devs = [d for d in unique_devs if d not in self.constrained_devices]
        if len(unique_devs) >= 2:
            kept_pairs = []
            for pair in deduped_pairs:
                if pair[0] in unique_devs and pair[1] in unique_devs:
                    kept_pairs.append([pair[0], pair[1]])
            self._append_symmetry_group(kept_pairs)

    def process_task(self, match_file, template_json_file, template_name):
        if not os.path.exists(match_file) or not os.path.exists(template_json_file):
            return

        matches = self._parse_match_file(match_file)
        real_matches = []
        for match in matches:
            name_map = self._build_real_match(match)
            if self._is_valid_template_match(name_map, template_name):
                real_matches.append(name_map)

        if not real_matches:
            return

        self.debug_lines.append(f"[{template_name}] valid_matches={len(real_matches)}")
        for idx, item in enumerate(real_matches, 1):
            self.debug_lines.append(f"  match{idx}: {item}")

        with open(template_json_file, 'r') as f:
            template_constraints = json.load(f)

        if "8" in template_constraints:
            self._emit_current_mirror_constraints(template_constraints, real_matches)
            return

        valid_matches = [
            m for m in real_matches
            if not all(dev in self.constrained_devices for dev in m.values())
        ]
        if not valid_matches:
            return

        self._emit_template_constraints(template_constraints, valid_matches)

    def infer_instance_constraints(self, circuit_graph):
        """
        基于电路图直接推断：
        1. 相同子电路类型的实例（从展平节点名前缀反推）→ 按共享信号分组，生成对称组约束(3)
        2. 相同值的电容 → 按连接关系配对，生成对称组约束(3)
        3. 将已生成的底层约束组打包成高层对称组(层次嵌套)
        """
        from collections import defaultdict

        def clean_node(name):
            """
            节点名两种格式:
            1. 顶层器件: "TopSubcktName_m6"  → 取最后一个 '_' 后的部分
            2. 子电路器件: "xi27|switch_A_m15" → 取 '|' 前的顶层实例名
            """
            if '|' in name:
                return name.split('|')[0]
            return name.split('_')[-1] if '_' in name else name

        def inst_prefix(flat_name):
            """子电路器件返回顶层实例名，顶层器件返回 None"""
            if '|' in flat_name:
                return flat_name.split('|')[0]
            return None

        # ── 1. 子电路实例分组 ──────────────────────────────────────────
        # 从展平节点名里提取顶层实例前缀，按 (实例前缀, 子电路类型) 聚合
        # 同时收集每个实例连接的外部信号（用于分组）
        inst_to_ports = defaultdict(set)   # inst_name → 连接的外部 net 集合
        inst_to_type  = {}                 # inst_name → subckt_type

        for n, attr in circuit_graph.nodes(data=True):
            itype = attr.get('inst_type', '')
            if itype in ('net', ''):
                continue
            ip = inst_prefix(n)
            if ip is None:
                continue
            # 子电路类型从原始节点名提取: "xi27|switch_A_m1" → "switch_A"
            if '|' in n:
                after_pipe = n.split('|')[1]          # "switch_A_m1"
                subckt_name = '_'.join(after_pipe.split('_')[:-1])  # "switch_A"
            else:
                subckt_name = itype
            inst_to_type[ip] = subckt_name
            # 收集该实例连接的外部 net（电路图里与该节点相邻的 net 节点）
            for neighbor in circuit_graph.neighbors(n):
                nb_attr = circuit_graph.nodes[neighbor]
                if nb_attr.get('inst_type', '') == 'net':
                    inst_to_ports[ip].add(neighbor)

        # 按子电路类型分组
        type_to_insts = defaultdict(list)
        for ip, stype in inst_to_type.items():
            type_to_insts[stype].append(ip)

        for stype, insts in type_to_insts.items():
            if len(insts) < 2:
                continue
            free = [i for i in insts if i not in self.constrained_devices]
            if len(free) < 2:
                continue

            # 改成按“共享非电源信号”连通分量划分，再在每个分量里做配对。
            # 这样 switch_A 这类实例能自然形成 4 个或 8 个成员的局部对称组。
            signal_graph = {inst: set() for inst in free}
            for i, left in enumerate(free):
                left_nets = {
                    net for net in inst_to_ports[left]
                    if not self._is_supply_net(net) and not self._is_control_net(net)
                }
                for right in free[i + 1:]:
                    right_nets = {
                        net for net in inst_to_ports[right]
                        if not self._is_supply_net(net) and not self._is_control_net(net)
                    }
                    if left_nets & right_nets:
                        signal_graph[left].add(right)
                        signal_graph[right].add(left)

            visited = set()
            components = []
            for inst in free:
                if inst in visited:
                    continue
                stack = [inst]
                visited.add(inst)
                comp = []
                while stack:
                    cur = stack.pop()
                    comp.append(cur)
                    for nb in signal_graph[cur]:
                        if nb not in visited:
                            visited.add(nb)
                            stack.append(nb)
                components.append(sorted(comp))

            for members in components:
                if len(members) < 2:
                    continue
                self.debug_lines.append(f"[{stype}] component={members}")
                pairs = self._pair_instances_by_signals(members, inst_to_ports)
                if pairs:
                    self._append_symmetry_group(pairs)

        # 对只有一个顶层实例、且其内部器件已经被约束覆盖的子电路，
        # 补一个实例级保护约束。这样 comparator 里像 xi1 这类
        # “单个锁存单元”可以保留下来，同时不会误报尚未成形的实例。
        for stype, insts in type_to_insts.items():
            if len(insts) != 1:
                continue
            inst_name = insts[0]
            if inst_name in self.constrained_devices:
                continue
            if not str(inst_name).lower().startswith('xi'):
                continue

            self.final_layout_lines.append(f"Group_{self.group_id} 7 {inst_name}")
            self.group_id += 1
            self.constrained_devices.add(inst_name)
            self.debug_lines.append(f"[singleton_instance] {stype} -> {inst_name}")

        # ── 2. 电容分组 ────────────────────────────────────────────────
        cap_by_value = defaultdict(list)
        for n, attr in circuit_graph.nodes(data=True):
            if attr.get('inst_type', '') == 'cap':
                val = attr.get('values', None)
                cname = clean_node(n)
                if cname not in self.constrained_devices:
                    cap_by_value[val].append(cname)

        for val, caps in cap_by_value.items():
            if len(caps) < 2:
                continue
            sorted_caps = sorted(caps)
            pairs = []
            for i in range(0, len(sorted_caps) - 1, 2):
                pairs.append([sorted_caps[i], sorted_caps[i+1]])
            if not pairs:
                continue
            self._append_symmetry_group(pairs)

        # ── 3. 约束7：独立保护环（尾电流源识别）─────────────────────────
        # 尾电流源特征：drain 连接到已约束差分对的 source 共享节点，
        # 且自身 source 接 gnd/vss，gate 接偏置。
        # 策略：找所有已约束器件共享的 net，若该 net 只连接一个未约束器件，
        # 则该器件为尾电流源，加保护环约束(7)。
        constrained_snapshot = set(self.constrained_devices)

        # 收集已约束器件连接的所有 net
        constrained_nets = set()
        for n, attr in circuit_graph.nodes(data=True):
            cname = clean_node(n)
            if cname in constrained_snapshot:
                for nb in circuit_graph.neighbors(n):
                    if circuit_graph.nodes[nb].get('inst_type', '') == 'net':
                        constrained_nets.add(nb)

        # 对每个被已约束器件共享的 net，找连接的未约束器件
        for net_node in constrained_nets:
            unconstrained_neighbors = []
            for nb in circuit_graph.neighbors(net_node):
                nb_attr = circuit_graph.nodes[nb]
                itype = nb_attr.get('inst_type', '')
                if itype in ('nmos', 'pmos'):
                    cname = clean_node(nb)
                    if cname not in constrained_snapshot:
                        unconstrained_neighbors.append((nb, cname))
            # 只有唯一一个未约束器件连接到该 net → 候选尾电流源
            if len(unconstrained_neighbors) == 1:
                node_n, cname = unconstrained_neighbors[0]
                # 进一步确认：该器件有接 gnd/vss 的连接
                has_gnd = any(
                    any(g in nb2.lower() for g in ('gnd', 'vss', 'gnda'))
                    for nb2 in circuit_graph.neighbors(node_n)
                    if circuit_graph.nodes[nb2].get('inst_type', '') == 'net'
                )
                if has_gnd and cname not in self.constrained_devices:
                    self.final_layout_lines.append(f"Group_{self.group_id} 7 {cname}")
                    self.group_id += 1
                    self.constrained_devices.add(cname)

    def infer_tail_current_sources(self, circuit_graph):
        """
        提前识别尾电流源，加约束7，并加入 constrained_devices。
        特征：drain 连接到差分对的 source 共享节点（该 net 只连接少量器件），
              且自身 source 接 gnd/vss。
        """
        def clean_node(name):
            if '|' in name:
                return name.split('|')[0]
            return name.split('_')[-1] if '_' in name else name

        # 找所有 nmos/pmos 器件，检查是否为尾电流源
        # 策略：找 source 接 gnd/vss 且 drain 接的 net 只连接少量（<=3）器件的管
        for n, attr in circuit_graph.nodes(data=True):
            itype = attr.get('inst_type', '')
            if itype not in ('nmos', 'pmos'):
                continue
            cname = clean_node(n)
            if cname in self.constrained_devices:
                continue
            if cname not in self.toplevel_devices:
                continue

            has_gnd_source = False
            drain_net = None
            for nb in circuit_graph.neighbors(n):
                nb_attr = circuit_graph.nodes[nb]
                if nb_attr.get('inst_type', '') != 'net':
                    continue
                ew = circuit_graph.get_edge_data(n, nb, {}).get('weight', 0)
                if ew == 4:  # source
                    nb_name = nb.lower()
                    if any(g in nb_name for g in ('gnd', 'vss', 'gnda')):
                        has_gnd_source = True
                elif ew == 1:  # drain
                    drain_net = nb

            if not has_gnd_source or drain_net is None:
                continue

            gate_net = self.device_gate_net.get(cname)
            if self._is_control_net(gate_net):
                continue

            # 真正的尾电流源通常连接在差分对的公共 source 节点上。
            # 在 full_differential 这类结构里，该节点通常连着 3 个 MOS：
            # 尾管本身 + 差分对左右两管。若条件放宽，m4/m6 这类偏置支路也会被误报。
            drain_neighbors = [
                nb for nb in circuit_graph.neighbors(drain_net)
                if circuit_graph.nodes[nb].get('inst_type', '') in ('nmos', 'pmos')
            ]
            if len(drain_neighbors) == 3:
                others = []
                for nb in drain_neighbors:
                    oname = clean_node(nb)
                    if oname == cname:
                        continue
                    others.append(oname)
                if len(others) != 2:
                    continue
                if not all(self.device_type.get(o) == itype for o in others):
                    continue
                other_sources = [self.device_source_net.get(o) for o in others]
                if len(set(other_sources)) != 1 or other_sources[0] != drain_net:
                    continue
                self.final_layout_lines.append(f"Group_{self.group_id} 7 {cname}")
                self.group_id += 1
                self.constrained_devices.add(cname)

    def audit_constraint_coverage(self, circuit_graph):
        """
        只做覆盖率审计，不生成新约束。
        目标是评估基础模板和通用规则对当前电路的自动覆盖情况。
        """
        from collections import defaultdict

        self.constrained_devices = self._collect_devices_from_output()
        validation_report = self.validate_final_constraints()

        type_to_devices = defaultdict(list)
        for device in sorted(self.toplevel_devices):
            dtype = self.device_type.get(device, "instance_or_passive")
            type_to_devices[dtype].append(device)

        unconstrained = [
            device for device in sorted(self.toplevel_devices)
            if device not in self.constrained_devices
        ]
        unconstrained_by_type = defaultdict(list)
        for device in unconstrained:
            unconstrained_by_type[self.device_type.get(device, "instance_or_passive")].append(device)

        total = len(self.toplevel_devices)
        covered = total - len(unconstrained)
        ratio = covered / total if total else 1.0
        candidates = self._find_unconstrained_pair_candidates(unconstrained)

        type_summary = {}
        for dtype in sorted(type_to_devices):
            devices = type_to_devices[dtype]
            missing = [device for device in devices if device in unconstrained]
            type_summary[dtype] = {
                "total": len(devices),
                "unconstrained": len(missing),
                "missing": missing,
            }

        risks = []
        if not self.final_layout_lines:
            risks.append("no_constraints_generated")
        if unconstrained:
            risks.append("unconstrained_top_level_devices")
        if candidates:
            risks.append("possible_missing_symmetric_pairs")
        if validation_report["errors"]:
            risks.append("invalid_constraint_format_or_topology")
        elif validation_report["warnings"]:
            risks.append("constraint_validation_warnings")

        if not self.final_layout_lines:
            status = "fail"
        elif validation_report["errors"]:
            status = "fail"
        elif risks:
            status = "need_review"
        else:
            status = "pass"

        self.coverage_report = {
            "status": status,
            "risks": risks,
            "total_top_level": total,
            "constrained": covered,
            "unconstrained": len(unconstrained),
            "coverage_ratio": ratio,
            "type_summary": type_summary,
            "pair_candidates": candidates,
            "constraint_line_count": len(self.final_layout_lines),
            "constraint_validation": validation_report,
        }

        self.debug_lines.append("[coverage_audit]")
        self.debug_lines.append(f"  status={status}")
        self.debug_lines.append(f"  risks={risks}")
        self.debug_lines.append(f"  total_top_level={total}")
        self.debug_lines.append(f"  constrained={covered}")
        self.debug_lines.append(f"  unconstrained={len(unconstrained)}")
        self.debug_lines.append(f"  coverage_ratio={ratio:.2%}")

        for dtype in sorted(type_summary):
            info = type_summary[dtype]
            self.debug_lines.append(
                f"  type={dtype} total={info['total']} unconstrained={info['unconstrained']}"
            )
            if info["missing"]:
                self.debug_lines.append(f"    missing={info['missing']}")

        if candidates:
            self.debug_lines.append("  pair_candidates:")
            for item in candidates:
                self.debug_lines.append(
                    f"    {item['left']} {item['right']} "
                    f"type={item['type']} reason={item['reason']}"
                )
        if validation_report["errors"] or validation_report["warnings"]:
            self.debug_lines.append("  constraint_validation:")
            for issue in validation_report["errors"]:
                self.debug_lines.append(f"    error: {issue}")
            for issue in validation_report["warnings"]:
                self.debug_lines.append(f"    warning: {issue}")

    def validate_final_constraints(self):
        """
        对最终输出做通用自检：格式是否可解析、引用是否有效、每个约束覆盖了哪些器件，
        以及 MOS pair 是否能找到基本拓扑证据。这里只审计，不生成新约束。
        """
        blocks = self._group_blocks()
        group_names = {header[0] for _, header, _ in blocks}
        known_leaf_members = set(self.toplevel_devices) | set(self.device_type)
        known_leaf_members.update(name for name in self.id_to_name.values() if name)
        errors = []
        warnings = []
        group_reports = []

        for _, header, sublines in blocks:
            group_name = header[0]
            rule = header[1] if len(header) > 1 else None
            members = header[2:] if len(header) > 2 else []
            member_refs = members
            if rule == '11' and members:
                member_refs = members[:1]
            covered_devices = sorted({member for member in member_refs if member in known_leaf_members})
            referenced_groups = [member for member in member_refs if member.startswith('Group_')]
            unknown_members = [
                member for member in member_refs
                if member not in known_leaf_members and member not in group_names and not member.startswith('Group_')
            ]
            duplicate_members = sorted({member for member in member_refs if member_refs.count(member) > 1})
            group_issues = []
            evidence = []
            pair_reports = []

            if rule is None:
                group_issues.append("missing_rule_type")
            if unknown_members:
                group_issues.append(f"unknown_members={unknown_members}")
            missing_group_refs = [member for member in referenced_groups if member not in group_names]
            if missing_group_refs:
                group_issues.append(f"missing_group_refs={missing_group_refs}")
            if duplicate_members:
                group_issues.append(f"duplicate_members={duplicate_members}")

            if rule == '1':
                if len(members) != 2:
                    group_issues.append("pair_constraint_should_have_two_members")
                elif all(member in self.device_type for member in members):
                    pair_evidence = self._pair_topology_evidence(members[0], members[1])
                    pair_reports.append({
                        "left": members[0],
                        "right": members[1],
                        "evidence": pair_evidence,
                    })
                    if not pair_evidence:
                        group_issues.append(f"mos_pair_without_topology_evidence={members[0]},{members[1]}")
                evidence.append("pair_constraint")
            elif rule == '3':
                if len(members) < 2:
                    group_issues.append("symmetry_group_has_too_few_members")
                pair_lines = [line for line in sublines if line.split()[:1] == ['2']]
                if not pair_lines:
                    group_issues.append("symmetry_group_missing_pair_lines")
                for line in pair_lines:
                    parts = line.split()
                    if len(parts) != 3:
                        group_issues.append(f"invalid_pair_line={line}")
                        continue
                    left, right = parts[1], parts[2]
                    if left not in members or right not in members:
                        group_issues.append(f"pair_member_not_in_header={line}")
                    pair_evidence = self._pair_topology_evidence(left, right)
                    pair_reports.append({
                        "left": left,
                        "right": right,
                        "evidence": pair_evidence,
                    })
                    if left in self.device_type and right in self.device_type and not pair_evidence:
                        group_issues.append(f"mos_pair_without_topology_evidence={left},{right}")
                evidence.append("explicit_pair_lines")
            elif rule == '6':
                if len(members) < 2:
                    group_issues.append("line_group_has_too_few_members")
                leaf_types = sorted({self.device_type.get(member, "group_or_passive") for member in members})
                evidence.append(f"line_members={len(members)}")
                evidence.append(f"member_types={leaf_types}")
            elif rule == '7':
                if len(members) != 1:
                    group_issues.append("protection_constraint_should_have_one_member")
                evidence.append("single_device_or_instance_protection")
            elif rule == '8':
                if len(members) < 2:
                    group_issues.append("current_mirror_has_too_few_members")
                if members and all(member in self.device_gate_net for member in members):
                    gates = {self.device_gate_net.get(member) for member in members}
                    if len(gates) == 1:
                        evidence.append("shared_gate")
                    else:
                        group_issues.append("current_mirror_members_do_not_share_gate")
            elif rule == '11':
                if len(members) != 2:
                    group_issues.append("rotation_constraint_should_have_member_and_type")
                target = members[0] if members else None
                if target and target in self.device_type:
                    warnings.append(f"{group_name}: rotation target is MOS device {target}")
                evidence.append("rotation_directive")
            else:
                group_issues.append(f"unknown_rule_type={rule}")

            for issue in group_issues:
                if issue.startswith("unknown_rule_type") or "missing" in issue or "invalid" in issue:
                    errors.append(f"{group_name}: {issue}")
                else:
                    warnings.append(f"{group_name}: {issue}")

            group_reports.append({
                "group": group_name,
                "rule": rule,
                "members": members,
                "covers": covered_devices,
                "referenced_groups": referenced_groups,
                "evidence": evidence,
                "pairs": pair_reports,
                "issues": group_issues,
            })

        return {
            "errors": errors,
            "warnings": warnings,
            "groups": group_reports,
        }

    def _pair_topology_evidence(self, left, right):
        evidence = []
        if left == right:
            evidence.append("self_pair")
            return evidence
        if left.startswith('Group_') and right.startswith('Group_'):
            evidence.append("group_self_symmetry" if left == right else "group_level_pair")
            return evidence
        if left not in self.device_type or right not in self.device_type:
            return evidence
        if self.device_type.get(left) == self.device_type.get(right):
            evidence.append(f"same_type:{self.device_type.get(left)}")
        if self.device_gate_net.get(left) == self.device_gate_net.get(right):
            evidence.append("shared_gate")
        if self.device_source_net.get(left) == self.device_source_net.get(right):
            evidence.append("shared_source")
        if self.device_drain_net.get(left) == self.device_drain_net.get(right):
            evidence.append("shared_drain")
        if self._pair_branch_set(left, right):
            evidence.append("matched_supply_branches")
        if self._is_cross_coupled_pair(left, right):
            evidence.append("cross_coupled")
        return evidence

    def _find_unconstrained_pair_candidates(self, unconstrained):
        candidates = []
        mos_devices = [
            device for device in unconstrained
            if self.device_type.get(device) in ("nmos", "pmos", "transistor")
        ]

        for i, left in enumerate(sorted(mos_devices)):
            for right in sorted(mos_devices)[i + 1:]:
                if self.device_type.get(left) != self.device_type.get(right):
                    continue

                reasons = []
                if self.device_gate_net.get(left) == self.device_gate_net.get(right):
                    reasons.append("same_gate")
                if self.device_source_net.get(left) == self.device_source_net.get(right):
                    reasons.append("same_source")
                if self.device_drain_net.get(left) == self.device_drain_net.get(right):
                    reasons.append("same_drain")
                if self._pair_branch_set(left, right):
                    reasons.append("matched_supply_branches")
                if self._is_cross_coupled_pair(left, right):
                    reasons.append("cross_coupled")

                if reasons:
                    candidates.append({
                        "left": left,
                        "right": right,
                        "type": self.device_type.get(left),
                        "reason": "+".join(reasons),
                    })

        return candidates[:20]

    def _collect_devices_from_output(self):
        devices = set()
        for line in self.final_layout_lines:
            parts = line.split()
            if not parts:
                continue
            if parts[0].startswith('Group_'):
                members = parts[2:] if len(parts) >= 3 else []
            else:
                members = parts[1:]
            for member in members:
                if member in self.toplevel_devices:
                    devices.add(member)
        return devices

    def save_to_file(self, output_path, report_path=None, debug_path=None):
        with open(output_path, 'w', encoding='utf-8') as f:
            if self.final_layout_lines:
                f.write('\n'.join(self.final_layout_lines) + '\n')
        if self.debug_lines:
            debug_path = debug_path or output_path.replace('.txt', '_debug.txt')
            os.makedirs(os.path.dirname(debug_path), exist_ok=True)
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.debug_lines) + '\n')
        if self.coverage_report:
            report_path = report_path or output_path.replace('.txt', '_report.json')
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.coverage_report, f, indent=2, ensure_ascii=False)
        print(f"✅ 成功! 约束文件已保存至: {output_path}")
        if report_path:
            print(f"🧭 审计报告已保存至: {report_path}")
            print(f"   status: {self.coverage_report.get('status')}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_arg = sys.argv[1] if len(sys.argv) > 1 else 'circuit.json'
    config = Configuration(os.path.join(script_dir, config_arg) if not os.path.isabs(config_arg) else config_arg)
    CircuitAnnotator(config).run()
