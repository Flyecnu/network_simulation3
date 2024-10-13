# src/path_calculator.py

import networkx as nx
import csv
import time

class PathCalculator:
    def __init__(self, oms_links):
        self.G = nx.Graph()
        self.edge_service_matrix = {}
        self.paths_in_use = {}
        self.backup_paths = {}
        self.path_cache = {}  # 路径缓存池
        self.failed_edges = []  # 初始化失败的边
        self.initialize_graph(oms_links)

    def initialize_graph(self, oms_links):
        for link in oms_links:
            # 直接使用 src 和 snk 作为图的边
            edge = (min(link.src, link.snk), max(link.src, link.snk))  # 规范化边的顺序
            self.G.add_edge(edge[0], edge[1], weight=link.cost, distance=link.distance)


    def build_edge_service_matrix(self):
        """构建边和经过它的业务的映射关系"""
        for service_index, data in self.paths_in_use.items():
            edges = data['edges']
            for edge in edges:
                # 规范化边的顺序为 (min, max)
                edge = (min(edge[0], edge[1]), max(edge[0], edge[1]))
                
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

    def handle_failure(self, edge, log_file='simulation_log.txt'):
        """
        处理链路故障，根据策略进行路径切换，并记录更新的路径数和时间。
        """
        start_time = time.time()
        
        # 规范化故障边的顺序
        edge = (min(edge[0], edge[1]), max(edge[0], edge[1]))

        # 打印 Edge Service Matrix 到文件
        with open('1.txt', 'a') as file:
            file.write(f"Edge Service Matrix: {self.edge_service_matrix}\n")

        # Step 1: 查找当前路径经过故障边的服务
        affected_services_current = self.edge_service_matrix.get(edge, [])
        print(f"Affected services for edge {edge}: {affected_services_current}")

        updated_paths_count = 0  # 用于记录更新的路径数量

        # Step 2: 更新当前路径经过故障边的服务
        for service_index in affected_services_current:
            print(f"Service {service_index} affected by edge failure: {edge}")
            # 按优先级顺序处理路径切换逻辑（备用路径 -> 局部路径重计算 -> 缓存路径 -> Dijkstra）
            if self.update_service_path(service_index, edge):
                updated_paths_count += 1  # 记录成功更新的路径
                # 仅更新该业务受故障边影响的备用路径
                self.update_service_backup_path(service_index)

        # Step 3: 查找备用路径中包含故障边的服务
        affected_services_backup = []
        for service_index, backup_paths in self.backup_paths.items():
            for backup_edge in backup_paths.keys():
                # 将备用路径中的边进行规范化
                if isinstance(backup_edge, str):
                    backup_edge = eval(backup_edge)  # 将字符串形式的边转换为 tuple
                backup_edge = (min(backup_edge[0], backup_edge[1]), max(backup_edge[0], backup_edge[1]))
                if edge == backup_edge:
                    affected_services_backup.append(service_index)

        # Step 4: 更新包含故障边的备用路径
        for service_index in affected_services_backup:
            if edge in self.backup_paths[service_index]:
                print(f"Service {service_index}'s backup path contains the failed edge: {edge}")
                # 覆盖失效的备用路径并更新
                self.update_service_backup_path_for_edge(service_index, edge)
                updated_paths_count += 1

        # 记录结束时间
        end_time = time.time()
        elapsed_time = end_time - start_time

        # 将更新的数量和时间记录写入文件
        with open(log_file, 'a') as log:
            log.write(f"Edge {edge} failure processed.\n")
            log.write(f"Updated paths: {updated_paths_count}\n")
            log.write(f"Time taken: {elapsed_time:.4f} seconds\n\n")


    def update_service_backup_path_for_edge(self, service_index, edge):
        """
        仅更新该业务受故障边影响的备用路径。
        """
        # 获取当前业务路径的起点和终点
        src, snk = self.paths_in_use[service_index]['path'][0], self.paths_in_use[service_index]['path'][-1]

        # 获取旧的备用路径并加入缓存池
        old_backup_path = self.backup_paths.get(service_index, {}).get(edge)
        if old_backup_path:
            print(f"Adding old backup path of service {service_index} for edge {edge} to cache.")
            self.add_to_cache(service_index, old_backup_path)

        # Step 1: 局部路径重计算
        local_path = self.local_recompute_path(src, snk)
        if local_path:
            print(f"Recomputed backup path for service {service_index} and edge {edge} using local search.")
            if service_index not in self.backup_paths:
                self.backup_paths[service_index] = {}
            self.backup_paths[service_index][edge] = local_path
            return

        # Step 2: 检查缓存池中的备用路径
        cached_path = self.get_from_cache(service_index, edge)
        if cached_path:
            print(f"Recomputed backup path for service {service_index} and edge {edge} using cached path.")
            if service_index not in self.backup_paths:
                self.backup_paths[service_index] = {}
            self.backup_paths[service_index][edge] = cached_path
            return

        # Step 3: 使用 Dijkstra 重新计算备用路径
        try:
            backup_path = nx.shortest_path(self.G, source=src, target=snk, weight='weight')
            backup_edges = [(backup_path[i], backup_path[i + 1]) for i in range(len(backup_path) - 1)]
            if service_index not in self.backup_paths:
                self.backup_paths[service_index] = {}
            self.backup_paths[service_index][edge] = {'path': backup_path, 'edges': backup_edges}
            print(f"Recomputed backup path for service {service_index} and edge {edge} using Dijkstra.")
        except nx.NetworkXNoPath:
            print(f"Failed to find a new backup path for service {service_index} and edge {edge}.")

    def update_service_backup_path(self, service_index):
        """
        为业务的每条边生成备用路径，更新业务的备用路径矩阵。
        """
        # 获取该业务的路径
        service_path = self.paths_in_use.get(service_index)
        if not service_path:
            print(f"Service {service_index} has no path in use.")
            return False

        # 获取该业务的所有边
        service_edges = service_path['edges']

        # 遍历业务的每条边，并为每条边故障生成备用路径
        for edge in service_edges:
            edge = (min(edge[0], edge[1]), max(edge[0], edge[1]))  # 规范化边的顺序

            # 获取源和目标节点
            src, snk = service_path['path'][0], service_path['path'][-1]

            # Step 1: 将旧的备用路径加入缓存池
            old_backup_path = self.backup_paths.get(service_index, {}).get(edge)
            if old_backup_path:
                print(f"Adding old backup path of service {service_index} for edge {edge} to cache.")
                self.add_to_cache(service_index, old_backup_path)

            # Step 2: 局部路径重计算
            local_path = self.local_recompute_path(src, snk)
            if local_path:
                print(f"Recomputed backup path for service {service_index} and edge {edge} using local search.")
                if service_index not in self.backup_paths:
                    self.backup_paths[service_index] = {}
                self.backup_paths[service_index][edge] = local_path
                continue  # 继续为下一个边生成备用路径

            # Step 3: 检查缓存池中的备用路径
            cached_path = self.get_from_cache(service_index, edge)
            if cached_path:
                print(f"Recomputed backup path for service {service_index} and edge {edge} using cached path.")
                if service_index not in self.backup_paths:
                    self.backup_paths[service_index] = {}
                self.backup_paths[service_index][edge] = cached_path
                continue

            # Step 4: 使用 Dijkstra 重新计算备用路径
            try:
                backup_path = nx.shortest_path(self.G, source=src, target=snk, weight='weight')
                backup_edges = [(backup_path[i], backup_path[i + 1]) for i in range(len(backup_path) - 1)]
                if service_index not in self.backup_paths:
                    self.backup_paths[service_index] = {}
                self.backup_paths[service_index][edge] = {'path': backup_path, 'edges': backup_edges}
                print(f"Recomputed backup path for service {service_index} and edge {edge} using Dijkstra.")
            except nx.NetworkXNoPath:
                print(f"Failed to find a new backup path for service {service_index} and edge {edge}.")


    def update_service_path(self, service_index, edge):
        """
        更新服务的路径，优先使用备用路径，如果没有则重新计算路径，并将旧的路径加入缓存池。
        """
        # 将当前路径加入缓存池
        old_path = self.paths_in_use.get(service_index)
        if old_path:
            print(f"Adding old path of service {service_index} to cache.")
            self.add_to_cache(service_index, old_path)

        # 优先使用已计算好的备用路径
        backup_path_info = self.backup_paths.get(service_index, {}).get(edge)
        if backup_path_info:
            print(f"Switching service {service_index} to backup path for edge {edge}")
            self.paths_in_use[service_index] = backup_path_info
        else:
            # 尝试局部路径重计算
            src, snk = self.paths_in_use[service_index]['path'][0], self.paths_in_use[service_index]['path'][-1]
            local_path = self.local_recompute_path(src, snk)
            if local_path:
                print(f"Switching service {service_index} to locally recomputed path.")
                self.paths_in_use[service_index] = local_path
            else:
                # 检查缓存池中的路径
                cached_path = self.get_from_cache(service_index, edge)
                if cached_path:
                    print(f"Switching service {service_index} to cached path.")
                    self.paths_in_use[service_index] = cached_path
                else:
                    # 使用 Dijkstra 重新计算路径
                    try:
                        new_path = nx.shortest_path(self.G, source=src, target=snk, weight='weight')
                        new_edges = [(new_path[i], new_path[i + 1]) for i in range(len(new_path) - 1)]
                        self.paths_in_use[service_index] = {'path': new_path, 'edges': new_edges}
                        print(f"Switching service {service_index} to newly computed path using Dijkstra.")
                    except nx.NetworkXNoPath:
                        print(f"Failed to find any path for service {service_index} after edge {edge} failed.")

    def save_to_csv(self, paths_csv, backup_csv):
        """保存 paths_in_use 和 backup_paths 到 CSV 文件"""
        # 保存 paths_in_use 到 CSV 文件
        with open(paths_csv, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Service Index', 'Path', 'Edges'])
            for service_index, data in self.paths_in_use.items():
                writer.writerow([service_index, data['path'], data['edges']])

        # 保存 backup_paths 到 CSV 文件
        with open(backup_csv, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Service Index', 'Failed Edge', 'Backup Path', 'Backup Edges'])
            for service_index, edge_paths in self.backup_paths.items():
                for edge, path_info in edge_paths.items():
                    writer.writerow([service_index, edge, path_info['path'], path_info['edges']])
