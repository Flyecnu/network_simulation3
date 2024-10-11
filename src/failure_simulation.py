import json
from path_calculator import PathCalculator
from simulator import NetworkSimulator

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
def failure_simulation():
    # 加载初始路径数据
    data = load_initial_data('results/initial_paths_data.json')
    
    # 初始化 PathCalculator 和 NetworkSimulator
    path_calculator = PathCalculator([])
    path_calculator.paths_in_use = data['paths_in_use']
    path_calculator.backup_paths = data['backup_paths']
    path_calculator.edge_service_matrix = data['edge_service_matrix']
    
    simulator = NetworkSimulator(path_calculator)

    failed_edges = data.get('failed_edges', [])
    recovered_edges = data.get('recovered_edges', [])

    # 用户输入模拟
    while True:
        action = input("Enter 'f' to simulate failure, 'r' to recover a failed edge, or 'q' to quit: ").strip().lower()
        
        if action == 'f':
            edge = input("Enter the edge to fail (format: src,snk): ").strip()
            src, snk = map(int, edge.split(','))
            edge = (min(src, snk), max(src, snk))
            
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
            
            # 只有在已故障的边中，才能进行恢复
            if edge in failed_edges:
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
