## 项目结构

```bash
.
├── src/
│   ├── initial_path_calculation.py      # 处理初始路径计算和备用路径生成
│   ├── failure_simulation.py            # 模拟边故障和恢复
│   ├── path_calculator.py               # 核心逻辑：路径计算、故障处理和恢复
│   ├── simulator.py                     # 用于模拟网络事件（故障、恢复）的接口
│   ├── data_handler.py                  # 处理从 CSV 文件加载数据（节点、链路、服务）
│   ├── model.py                         # 定义网络中的链路、节点和服务等数据结构
├── data/
│   ├── node.csv                         # 节点数据（网络节点）
│   ├── oms.csv                          # 链路数据（网络边）
│   ├── service.csv                      # 服务数据（服务路径）
│   ├── relay.csv                        # 中继数据（可选）
├── results/
│   ├── initial_paths_data.json          # 保存初始路径和备用路径
│   ├── simulation_log.txt               # 记录链路故障和恢复事件的日志
│   ├── simulation_paths.csv             # 当前服务路径的 CSV 输出
│   ├── simulation_backup_paths.csv      # 当前备用路径的 CSV 输出
│   ├── simulation_failed_edges.csv      # 故障边和恢复边的 CSV 输出
│   └── graph_structure.pkl              # 保存网络图的 Pickle 文件，便于快速重载
└── README.md                            # 项目文档

```



## 安装步骤

1.克隆项目仓库：

```bash
https://github.com/Flyecnu/network_simulation3.git
cd network_simulation3
```

2.安装依赖：

```bash
pip install -r requirements.txt
```

3.确保在 `data/` 目录中存在所需的输入数据（节点、链路、服务的 CSV 文件）。

## 使用说明

### 初始路径计算

运行以下命令，执行初始路径计算并生成备用路径：

```
python src/initial_path_calculation.py

```

此脚本根据输入的网络数据计算所有服务的路径，并将结果保存到 `results/initial_paths_data.json` 文件中。

### 模拟链路故障和恢复

运行以下命令，模拟链路故障和恢复：

```
python src/failure_simulation.py
```

在运行过程中，用户可以：

- 输入 **'f'** 模拟指定边的故障（例如 `src,snk` 格式的输入）。
- 输入 **'r'** 恢复之前故障的边。
- 输入 **'q'** 退出模拟。

系统会记录故障，更新相应的路径，并保存当前的模拟状态。

### 查看结果

模拟结束后，结果会保存在以下文件中：

- **`simulation_paths.csv`**：当前服务正在使用的路径。
- **`simulation_backup_paths.csv`**：当前服务的备用路径。
- **`simulation_failed_edges.csv`**：故障边和恢复边的列表。
- **`simulation_log.txt`**：模拟事件的详细日志。