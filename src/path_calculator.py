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
            
    def build_edge_service_matrix(self):
        """构建边和经过它的业务的映射关系"""
        for service_index, data in self.paths_in_use.items():
            edges = data['edges']
            for edge in edges:
                if edge not in self.edge_service_matrix:
                    self.edge_service_matrix[edge] = []
                self.edge_service_matrix[edge].append(service_index)
                
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
        """将未使用的路径添加到缓存池中"""
        if service_index not in self.path_cache:
            self.path_cache[service_index] = []
        self.path_cache[service_index].append(path_info)

    def get_from_cache(self, service_index, edge):
        """尝试从缓存池中获取路径"""
        if service_index in self.path_cache:
            for path_info in self.path_cache[service_index]:
                # 确保缓存的路径不使用故障边
                if edge not in path_info['edges']:
                    return path_info
        return None

    def recompute_backup_paths_for_service(self, service_index):
        """
        为某个业务重新计算所有边故障时的备用路径，并存储到 backup_paths 字典中。
        """
        original_edges = self.paths_in_use[service_index]['edges']
        src, snk = self.paths_in_use[service_index]['path'][0], self.paths_in_use[service_index]['path'][-1]
        self.backup_paths[service_index] = {}

        for edge in original_edges:
            # 移除当前边并计算不经过此边的备用路径
            self.G.remove_edge(*edge)  # 临时移除这条边来模拟故障
            try:
                # 使用 Dijkstra 算法计算备用路径
                backup_path = nx.shortest_path(self.G, source=src, target=snk, weight='weight')
                backup_edges = [(backup_path[i], backup_path[i + 1]) for i in range(len(backup_path) - 1)]
                self.backup_paths[service_index][edge] = {'path': backup_path, 'edges': backup_edges}
            except nx.NetworkXNoPath:
                print(f"No backup path found for service {service_index} when edge {edge} fails.")
            finally:
                # 恢复被移除的边
                self.G.add_edge(*edge)

    def recompute_backup_paths(self):
        """
        为所有服务重新计算备用路径，并存储在 backup_paths 中。
        """
        for service_index in self.paths_in_use.keys():
            self.recompute_backup_paths_for_service(service_index)

    def handle_failure(self, edge):
        """
        处理链路故障，根据策略进行路径切换。
        """
        affected_services = self.edge_service_matrix.get(edge, [])
        for service_index in affected_services:
            print(f"Service {service_index} affected by edge failure: {edge}")

            # 优先使用已计算好的备用路径
            backup_path_info = self.backup_paths.get(service_index, {}).get(edge)
            if backup_path_info:
                print(f"Switching service {service_index} to backup path for edge {edge}")
                self.paths_in_use[service_index] = backup_path_info
                continue

            # 尝试局部路径重计算
            src, snk = self.paths_in_use[service_index]['path'][0], self.paths_in_use[service_index]['path'][-1]
            local_path = self.local_recompute_path(src, snk)
            if local_path:
                print(f"Switching service {service_index} to locally recomputed path.")
                self.paths_in_use[service_index] = local_path
                continue

            # 检查缓存池中的路径
            cached_path = self.get_from_cache(service_index, edge)
            if cached_path:
                print(f"Switching service {service_index} to cached path.")
                self.paths_in_use[service_index] = cached_path
                continue

            # 使用 Dijkstra 重新计算路径
            try:
                new_path = nx.shortest_path(self.G, source=src, target=snk, weight='weight')
                new_edges = [(new_path[i], new_path[i + 1]) for i in range(len(new_path) - 1)]
                self.paths_in_use[service_index] = {'path': new_path, 'edges': new_edges}
                print(f"Switching service {service_index} to newly computed path using Dijkstra.")
            except nx.NetworkXNoPath:
                print(f"Failed to find any path for service {service_index} after edge {edge} failed.")
