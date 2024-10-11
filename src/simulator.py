# src/simulator.py

class NetworkSimulator:
    def __init__(self, path_calculator):
        self.path_calculator = path_calculator

    def simulate_failure(self, edge):
        print(f"Simulating failure on edge: {edge}")
        
        if edge in self.path_calculator.G.edges:
            self.path_calculator.handle_failure(edge)
        else:
            print(f"Error: Edge {edge} does not exist in the graph.")

    def simulate_recovery(self, edge):
        # 确保之前的路径恢复
        if edge not in self.path_calculator.G.edges:
            print(f"Simulating recovery on edge: {edge}")
            self.path_calculator.recompute_backup_paths()
        else:
            print(f"Error: Edge {edge} is not in the failed state.")
