# 常用命令

## 初始化

```bash
cd ~/work
make setup
```

## 只构建环境

```bash
make build all
```

## 进入虚拟环境

```bash
make shell
```

## 运行约束提取

```bash
make run
```

如果当前不在 `~/work`，也可以从任意路径执行：

```bash
make -C ~/work run
```

## 运行单个电路

编辑 `Constraints_Extraction/circuit.json` 中的 `netlist`，然后执行：

```bash
make run
```
