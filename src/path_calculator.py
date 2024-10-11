# src/path_calculator.py

import networkx as nx

class PathCalculator:
    def __init__(self, oms_links):
        self.G = nx.Graph()
        self.edge_service_matrix = {}
        self.paths_in_use = {}
        self.backup_paths = {}
        self.path_cache = {}  # 路径缓存池
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

    def local_recompute_path(self, src, snk):
        try:
            # 使用 BFS 进行双向搜索
            path = nx.bidirectional_shortest_path(self.G, source=src, target=snk)
            edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            return {'path': path, 'edges': edges}
        except nx.NetworkXNoPath:
            print(f"No local path found from {src} to {snk}")
            return None

    def add_to_cache(self, service_index, path_info):
        if service_index not in self.path_cache:
            self.path_cache[service_index] = []
        self.path_cache[service_index].append(path_info)

    def get_from_cache(self, service_index, edge):
        if service_index in self.path_cache:
            for path_info in self.path_cache[service_index]:
                if edge not in path_info['edges']:
                    return path_info
        return None

    def recompute_backup_paths_for_service(self, service_index):
        """重新计算某个业务的备用路径"""
        original_edges = self.paths_in_use[service_index]['edges']
        src, snk = self.paths_in_use[service_index]['path'][0], self.paths_in_use[service_index]['path'][-1]
        self.backup_paths[service_index] = {}

        for edge in original_edges:
            self.G.remove_edge(*edge)  # 移除边来模拟故障
            backup_path = self.local_recompute_path(src, snk) or self.recompute_path_dijkstra(src, snk)
            if backup_path:
                self.backup_paths[service_index][edge] = backup_path
            self.G.add_edge(*edge)  # 恢复边

    def recompute_backup_paths(self):
        for service_index, data in self.paths_in_use.items():
            original_edges = data['edges']
            src, snk = data['path'][0], data['path'][-1]
            self.backup_paths[service_index] = {}

            for edge in original_edges:
                self.G.remove_edge(*edge)  # 临时移除边
                backup_path = self.local_recompute_path(src, snk) or self.recompute_path_dijkstra(src, snk)
                if backup_path:
                    self.backup_paths[service_index][edge] = backup_path
                else:
                    # 没有备用路径，将当前路径加入缓存池
                    self.add_to_cache(service_index, data)
                self.G.add_edge(*edge)  # 恢复边

    def handle_failure(self, edge):
        affected_services = self.edge_service_matrix.get(edge, [])
        for service_index in affected_services:
            print(f"Service {service_index} affected by edge failure: {edge}")

            src, snk = self.paths_in_use[service_index]['path'][0], self.paths_in_use[service_index]['path'][-1]

            # 优先使用局部路径重计算
            local_path = self.local_recompute_path(src, snk)
            if local_path:
                self.paths_in_use[service_index] = local_path
                continue

            # 检查缓存池中的路径
            cached_path = self.get_from_cache(service_index, edge)
            if cached_path:
                self.paths_in_use[service_index] = cached_path
                continue

            # 使用备用路径
            backup_path = self.backup_paths.get(service_index, {}).get(edge)
            if backup_path:
                self.paths_in_use[service_index] = backup_path
            else:
                print(f"No backup path available for service {service_index}")

        # 重新计算备用路径，确保备用路径矩阵没有故障的边
        self.recompute_backup_paths()
