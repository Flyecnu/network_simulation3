# src/failure_simulation.py

import json
from path_calculator import PathCalculator
from simulator import NetworkSimulator

def string_key_to_tuple(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if isinstance(key, str) and key.startswith('(') and key.endswith(')'):
                key = eval(key)
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

    return data

def save_simulation_data(path_calculator, failed_edges, recovered_edges, file_name):
    data = {
        'paths_in_use': string_key_to_tuple(path_calculator.paths_in_use),
        'backup_paths': string_key_to_tuple(path_calculator.backup_paths),
        'edge_service_matrix': string_key_to_tuple(path_calculator.edge_service_matrix),
        'failed_edges': failed_edges,
        'recovered_edges': recovered_edges
    }
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def failure_simulation():
    # 加载初始路径数据
    data = load_initial_data('results/initial_paths_data.json')
    
    # 初始化 PathCalculator 和 NetworkSimulator
    path_calculator = PathCalculator([])
    path_calculator.paths_in_use = data['paths_in_use']
    path_calculator.backup_paths = data['backup_paths']
    path_calculator.edge_service_matrix = data['edge_service_matrix']
    
    simulator = NetworkSimulator(path_calculator)

    failed_edges = []
    recovered_edges = []

    # 用户输入模拟
    while True:
        action = input("Enter 'f' to simulate failure, 'r' to recover a failed edge, or 'q' to quit: ").strip().lower()
        if action == 'f':
            edge = input("Enter the edge to fail (format: src,snk): ").strip()
            src, snk = map(int, edge.split(','))
            edge = (min(src, snk), max(src, snk))
            if edge not in failed_edges:
                simulator.simulate_failure(edge)
                failed_edges.append(edge)
                print(f"Simulated failure on edge: {edge}")
            else:
                print(f"Edge {edge} has already failed.")
        elif action == 'r':
            edge = input("Enter the edge to recover (format: src,snk): ").strip()
            src, snk = map(int, edge.split(','))
            edge = (min(src, snk), max(src, snk))
            if edge in failed_edges:
                simulator.simulate_recovery(edge)
                failed_edges.remove(edge)
                recovered_edges.append(edge)
                print(f"Simulated recovery on edge: {edge}")
            else:
                print(f"Edge {edge} is not currently in the failed state.")
        elif action == 'q':
            break

        # 每次保存状态
        save_simulation_data(path_calculator, failed_edges, recovered_edges, 'results/simulation_state.json')
        print("Simulation state saved.")

if __name__ == "__main__":
    failure_simulation()
