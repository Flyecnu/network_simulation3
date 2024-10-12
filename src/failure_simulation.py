import json
import csv
from path_calculator import PathCalculator
from simulator import NetworkSimulator
import pickle
def tuple_to_string_key(data):
    """
    Recursively convert tuple keys in a dictionary to string keys for JSON serialization.
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if isinstance(key, tuple):
                key = str(key)  # Convert tuple to string
            new_data[key] = tuple_to_string_key(value)
        return new_data
    elif isinstance(data, list):
        return [tuple_to_string_key(item) for item in data]
    else:
        return data

def string_key_to_tuple(data):
    """
    Recursively convert string keys back to tuple keys for JSON deserialization.
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if isinstance(key, str) and key.startswith('(') and key.endswith(')'):
                key = eval(key)  # Convert string back to tuple
            new_data[key] = string_key_to_tuple(value)
        return new_data
    elif isinstance(data, list):
        return [string_key_to_tuple(item) for item in data]
    else:
        return data

def load_initial_data(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)

    data['paths_in_use'] = string_key_to_tuple(data['paths_in_use'])
    data['backup_paths'] = string_key_to_tuple(data['backup_paths'])
    data['edge_service_matrix'] = string_key_to_tuple(data['edge_service_matrix'])
    
    # 使用 get 方法，防止文件中没有 failed_edges 键时报错
    data['failed_edges'] = [eval(edge) for edge in data.get('failed_edges', [])]  # 将字符串转换回元组
    data['recovered_edges'] = [eval(edge) for edge in data.get('recovered_edges', [])]  # 同样转换

    return data


def save_simulation_data(path_calculator, failed_edges, recovered_edges, file_name):
    data = {
        'paths_in_use': tuple_to_string_key(path_calculator.paths_in_use),
        'backup_paths': tuple_to_string_key(path_calculator.backup_paths),
        'edge_service_matrix': tuple_to_string_key(path_calculator.edge_service_matrix),
        'failed_edges': [str(edge) for edge in failed_edges],  # 将元组转换为字符串
        'recovered_edges': [str(edge) for edge in recovered_edges]  # 同样转换
    }
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def save_simulation_to_csv(path_calculator, failed_edges, recovered_edges, paths_csv, backup_csv, failed_csv):
    """保存模拟状态到 CSV 文件"""
    # 保存 paths_in_use 到 CSV 文件
    with open(paths_csv, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Service Index', 'Path', 'Edges'])
        for service_index, data in path_calculator.paths_in_use.items():
            writer.writerow([service_index, data['path'], data['edges']])

    # 保存 backup_paths 到 CSV 文件
    with open(backup_csv, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Service Index', 'Failed Edge', 'Backup Path', 'Backup Edges'])
        for service_index, edge_paths in path_calculator.backup_paths.items():
            for edge, path_info in edge_paths.items():
                writer.writerow([service_index, edge, path_info['path'], path_info['edges']])

    # 保存失败和恢复的边信息到 CSV 文件
    with open(failed_csv, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Failed Edges', 'Recovered Edges'])
        writer.writerow([failed_edges, recovered_edges])


def failure_simulation():
    # 加载初始路径数据
    data = load_initial_data('results/initial_paths_data.json')
    
    # 加载图的结构
    with open('results/graph_structure.pkl', 'rb') as f:
        G = pickle.load(f)
    
    # 初始化 PathCalculator 并设置图
    path_calculator = PathCalculator([])
    path_calculator.G = G  # 使用已保存的图
    path_calculator.paths_in_use = data['paths_in_use']
    path_calculator.backup_paths = data['backup_paths']
    path_calculator.edge_service_matrix = data['edge_service_matrix']
    
    # with open('1.txt', 'a') as file:
    #     file.write(f"Edge Service Matrix: {path_calculator.edge_service_matrix}")

    
    simulator = NetworkSimulator(path_calculator)

    failed_edges = data.get('failed_edges', [])
    recovered_edges = data.get('recovered_edges', [])

    with open('results/current_edges.txt', 'w') as file:
        file.write(f"Current edges in graph: {list(path_calculator.G.edges)}\n")
        

    # 用户输入模拟
    while True:
        action = input("Enter 'f' to simulate failure, 'r' to recover a failed edge, or 'q' to quit: ").strip().lower()
        
        if action == 'f':
            edge = input("Enter the edge to fail (format: src,snk): ").strip()
            src, snk = map(int, edge.split(','))
            edge = (min(src, snk), max(src, snk))
            
            print(f"Attempting to fail edge: {edge}")
            
            # 检查该边是否存在于当前图中，并且不在已故障的边列表中
            if edge in path_calculator.G.edges and edge not in failed_edges:
                simulator.simulate_failure(edge)
                failed_edges.append(edge)
                print(f"Simulated failure on edge: {edge}")
            else:
                print(f"Edge {edge} does not exist or has already failed.")
        
        elif action == 'r':
            edge = input("Enter the edge to recover (format: src,snk): ").strip()
            src, snk = map(int, edge.split(','))
            edge = (min(src, snk), max(src, snk))
            
            print(f"Attempting to recover edge: {edge}")
            
            if edge in failed_edges:
                failed_edges.remove(edge)
                recovered_edges.append(edge)
                print(f"Simulated recovery on edge: {edge}")
            else:
                print(f"Edge {edge} is not currently in the failed state.")
        
        elif action == 'q':
            break

        save_simulation_data(path_calculator, failed_edges, recovered_edges, 'results/simulation_state.json')
        save_simulation_to_csv(path_calculator, failed_edges, recovered_edges,
                               paths_csv='results/simulation_paths.csv',
                               backup_csv='results/simulation_backup_paths.csv',
                               failed_csv='results/simulation_failed_edges.csv')

        print("Simulation state saved.")


if __name__ == "__main__":
    failure_simulation()
