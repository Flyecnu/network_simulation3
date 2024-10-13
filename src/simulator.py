# src/simulator.py

class NetworkSimulator:
    def __init__(self, path_calculator):
        self.path_calculator = path_calculator

    def simulate_failure(self, edge):
        print(f"Simulating failure on edge: {edge}")
        
        # 先将故障边加入 path_calculator 的 failed_edges 列表
        if edge not in self.path_calculator.failed_edges:
            self.path_calculator.failed_edges.append(edge)
            print(f"Edge {edge} added to failed edges.")
        else:
            print(f"Edge {edge} is already in failed edges.")
        
        # 处理故障，影响路径和图结构
        if edge in self.path_calculator.G.edges:
            self.path_calculator.handle_failure(edge)
        else:
            print(f"Error: Edge {edge} does not exist in the graph.")

    def simulate_recovery(self, edge):
        """
        模拟恢复边，但不立即重新计算路径，只更新状态，表明这条边可以使用。
        """
        # 从 failed_edges 中移除故障边
        if edge in self.path_calculator.failed_edges:
            self.path_calculator.failed_edges.remove(edge)
            print(f"Edge {edge} marked as recovered and is now available for use.")
        else:
            print(f"Edge {edge} was not in the failed edges list.")
        # 这里只是标记边可用，不需要重新计算路径
