# src/initial_path_calculation.py
import pickle
import json
import csv
from data_handler import load_nodes, load_oms_links, load_relays, load_services
from path_calculator import PathCalculator

def tuple_to_string_key(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if isinstance(key, tuple):
                key = str(key)
            new_data[key] = tuple_to_string_key(value)
        return new_data
    elif isinstance(data, list):
        return [tuple_to_string_key(item) for item in data]
    else:
        return data

def save_initial_data(path_calculator, file_name):
    data = {
        # 'paths_in_use': tuple_to_string_key(path_calculator.paths_in_use),
        # 'backup_paths': tuple_to_string_key(path_calculator.backup_paths),
        'edge_service_matrix': tuple_to_string_key(path_calculator.edge_service_matrix)
    }
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def save_to_csv(path_calculator, paths_csv, backup_csv):
    """保存 paths_in_use 和 backup_paths 到 CSV 文件"""
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

def initial_path_calculation():
    # 加载数据
    nodes = load_nodes('data/node.csv')
    oms_links = load_oms_links('data/oms.csv')
    relays = load_relays('data/relay.csv')
    services = load_services('data/service.csv')

    # 初始化路径计算器并计算路径
    path_calculator = PathCalculator(oms_links)
    path_calculator.calculate_paths(services)

    # 计算备用路径
    path_calculator.recompute_backup_paths()

    # 保存初始路径计算结果到 JSON 文件
    save_initial_data(path_calculator, 'results/initial_paths_data.json')

    # 保存初始路径计算结果到 CSV 文件
    save_to_csv(path_calculator, 'results/paths.csv', 'results/backup_paths.csv')
    
    # 保存图的结构到 pickle 文件
    with open('results/graph_structure.pkl', 'wb') as f:
        pickle.dump(path_calculator.G, f)
        
        
    print("Initial path calculation complete and data saved.")

if __name__ == "__main__":
    initial_path_calculation()
