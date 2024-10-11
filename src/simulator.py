# src/simulator.py
import csv

class NetworkSimulator:
    def __init__(self, path_calculator):
        self.path_calculator = path_calculator

    def simulate_failure(self, edge):
        print(f"Simulating failure on edge: {edge}")
        
        # Check if the edge exists before attempting to remove it
        if edge in self.path_calculator.G.edges:
            self.path_calculator.handle_failure(edge)
            self.path_calculator.recompute_backup_paths()
        else:
            print(f"Error: Edge {edge} does not exist in the graph.")

    def simulate_recovery(self, edge):
        # Ensure the edge was previously marked as failed
        if edge not in self.path_calculator.G.edges:
            print(f"Simulating recovery on edge: {edge}")
            self.path_calculator.recompute_backup_paths()
        else:
            print(f"Error: Edge {edge} is not in the failed state.")

    def random_event(self, failed_edges, recovered_edges):
        edges = list(self.path_calculator.edge_service_matrix.keys())
        if edges:
            edge = random.choice(edges)
            if random.choice([True, False]):
                if edge not in failed_edges:
                    self.simulate_failure(edge)
                    failed_edges.append(edge)
            else:
                if edge in failed_edges:
                    self.simulate_recovery(edge)
                    failed_edges.remove(edge)
                    recovered_edges.append(edge)
