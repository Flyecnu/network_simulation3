# src/load_and_simulate.py

import json
from path_calculator import PathCalculator
from simulator import NetworkSimulator

def load_init_data(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def save_simulation_data(path_calculator, failed_edges, recovered_edges, file_name):
    data = {
        'paths_in_use': path_calculator.paths_in_use,
        'backup_paths': path_calculator.backup_paths,
        'edge_service_matrix': path_calculator.edge_service_matrix,
        'failed_edges': failed_edges,
        'recovered_edges': recovered_edges
    }
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

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
