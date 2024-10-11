# src/load_and_simulate.py

import json
import csv
from path_calculator import PathCalculator
from simulator import NetworkSimulator

def tuple_to_string_key(data):
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

def load_init_data(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)

    data['paths_in_use'] = string_key_to_tuple(data['paths_in_use'])
    data['backup_paths'] = string_key_to_tuple(data['backup_paths'])
    data['edge_service_matrix'] = string_key_to_tuple(data['edge_service_matrix'])

    return data

def save_paths_to_csv(paths, file_name):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Service Index", "Path", "Edges"])
        for service_index, path_info in paths.items():
            writer.writerow([service_index, path_info['path'], path_info['edges']])

def save_failed_and_recovered_edges_to_csv(failed_edges, recovered_edges, file_name):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Edge", "Status"])
        for edge in failed_edges:
            writer.writerow([str(edge), "Failed"])
        for edge in recovered_edges:
            writer.writerow([str(edge), "Recovered"])

def save_simulation_data(path_calculator, failed_edges, recovered_edges, file_name):
    data = {
        'paths_in_use': tuple_to_string_key(path_calculator.paths_in_use),
        'backup_paths': tuple_to_string_key(path_calculator.backup_paths),
        'edge_service_matrix': tuple_to_string_key(path_calculator.edge_service_matrix),
        'failed_edges': failed_edges,
        'recovered_edges': recovered_edges
    }
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

    # Save paths and edges to CSV
    save_paths_to_csv(path_calculator.paths_in_use, 'results/paths.csv')
    save_failed_and_recovered_edges_to_csv(failed_edges, recovered_edges, 'results/edges_status.csv')

def manual_input_failure_or_recovery(simulator, failed_edges, recovered_edges):
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
        return False
    return True

def main():
    data = load_init_data('results/paths_data.json')
    
    path_calculator = PathCalculator([])
    path_calculator.paths_in_use = data['paths_in_use']
    path_calculator.backup_paths = data['backup_paths']
    path_calculator.edge_service_matrix = data['edge_service_matrix']
    
    simulator = NetworkSimulator(path_calculator)

    failed_edges = data.get('failed_edges', [])
    recovered_edges = data.get('recovered_edges', [])

    while True:
        if not manual_input_failure_or_recovery(simulator, failed_edges, recovered_edges):
            break

        save_simulation_data(path_calculator, failed_edges, recovered_edges, 'results/simulation_state.json')
        print("Simulation state saved.")

if __name__ == "__main__":
    main()
