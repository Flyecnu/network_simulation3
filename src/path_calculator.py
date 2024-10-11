# src/path_calculator.py

import networkx as nx
import csv

class PathCalculator:
    def __init__(self, oms_links):
        self.G = nx.Graph()
        self.edge_service_matrix = {}
        self.paths_in_use = {}
        self.backup_paths = {}
        self.initialize_graph(oms_links)

    def initialize_graph(self, oms_links):
        for link in oms_links:
            edge = (min(link.oms_id, link.remote_oms_id), max(link.oms_id, link.remote_oms_id))
            self.G.add_edge(link.src, link.snk, weight=link.cost, distance=link.distance)

    def calculate_paths(self, services):
        for service_index, service in enumerate(services):
            try:
                path = nx.shortest_path(self.G, source=service.src, target=service.snk, weight='weight')
                edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
                self.record_service_path(service_index, path, edges)
            except nx.NetworkXNoPath:
                print(f"No available path from {service.src} to {service.snk}")

        self.build_edge_service_matrix()

    def record_service_path(self, service_index, path, edges):
        self.paths_in_use[service_index] = {'path': path, 'edges': edges}

    def build_edge_service_matrix(self):
        for service_index, data in self.paths_in_use.items():
            edges = data['edges']
            for edge in edges:
                if edge not in self.edge_service_matrix:
                    self.edge_service_matrix[edge] = []
                self.edge_service_matrix[edge].append(service_index)

    def handle_failure(self, edge):
        affected_services = self.edge_service_matrix.get(edge, [])
        for service_index in affected_services:
            print(f"Service {service_index} affected by edge failure: {edge}")
            backup_path = self.backup_paths.get(service_index, {}).get(edge)
            if backup_path:
                print(f"Switching service {service_index} to backup path: {backup_path}")
                self.paths_in_use[service_index]['path'] = backup_path['path']
                self.paths_in_use[service_index]['edges'] = backup_path['edges']
            else:
                print(f"No backup path available for service {service_index}")

    def recompute_backup_paths(self):
        for service_index, data in self.paths_in_use.items():
            original_edges = data['edges']
            src, snk = data['path'][0], data['path'][-1]
            self.backup_paths[service_index] = {}
            for edge in original_edges:
                self.G.remove_edge(*edge)
                backup_path = self.recompute_path_dijkstra(src, snk)
                if backup_path:
                    self.backup_paths[service_index][edge] = backup_path
                self.G.add_edge(*edge)

    def recompute_path_dijkstra(self, src, snk):
        try:
            path = nx.shortest_path(self.G, source=src, target=snk, weight='weight')
            edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            return {'path': path, 'edges': edges}
        except nx.NetworkXNoPath:
            print(f"No path found from {src} to {snk}")
            return None
