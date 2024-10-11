# src/models.py

class Node:
    def __init__(self, node_id):
        self.node_id = node_id

class OmsLink:
    def __init__(self, oms_id, remote_oms_id, src, snk, cost, distance, ots, osnr, slice, colors):
        self.oms_id = oms_id
        self.remote_oms_id = remote_oms_id
        self.src = src
        self.snk = snk
        self.cost = cost
        self.distance = distance
        self.ots = ots
        self.osnr = osnr
        self.slice = slice
        self.colors = self.parse_colors(colors)
    
    def parse_colors(self, colors_str):
        available_colors = []
        if isinstance(colors_str, str) and colors_str:
            ranges = colors_str.split(":")
            for color_range in ranges:
                if color_range.strip() == '':
                    continue
                if '-' in color_range:
                    start, end = map(int, color_range.split('-'))
                    available_colors.extend(range(start, end + 1))
                else:
                    available_colors.append(int(color_range))
        return available_colors

class Relay:
    def __init__(self, relay_id, related_relay_id, node_id, local_id, related_local_id, dim_colors):
        self.relay_id = relay_id
        self.related_relay_id = related_relay_id
        self.node_id = node_id
        self.local_id = local_id
        self.related_local_id = related_local_id
        self.dim_colors = self.parse_colors(dim_colors)

    def parse_colors(self, colors_str):
        available_colors = []
        if isinstance(colors_str, str) and colors_str:
            ranges = colors_str.split(":")
            for color_range in ranges:
                if color_range.strip() == '':
                    continue
                if '-' in color_range:
                    start, end = map(int, color_range.split('-'))
                    available_colors.extend(range(start, end + 1))
                else:
                    available_colors.append(int(color_range))
        return available_colors

class Service:
    def __init__(self, src, snk, source_otu, target_otu, m_width, band_type, source_dim_colors, target_dim_colors):
        self.src = src
        self.snk = snk
        self.source_otu = source_otu
        self.target_otu = target_otu
        self.m_width = m_width
        self.band_type = band_type
        self.source_dim_colors = self.parse_colors(source_dim_colors)
        self.target_dim_colors = self.parse_colors(target_dim_colors)
    
    def parse_colors(self, colors_str):
        available_colors = []
        if isinstance(colors_str, str) and colors_str:
            ranges = colors_str.split(":")
            for color_range in ranges:
                if color_range.strip() == '':
                    continue
                if '-' in color_range:
                    start, end = map(int, color_range.split('-'))
                    available_colors.extend(range(start, end + 1))
                else:
                    available_colors.append(int(color_range))
        return available_colors
