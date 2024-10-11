# src/data_handler.py
from models import Node, OmsLink, Relay, Service
# src/data_handler.py

import pandas as pd
from models import Node, OmsLink, Relay, Service

def load_nodes(file_path):
    df = pd.read_csv(file_path)
    nodes = [Node(row['nodeId']) for idx, row in df.iterrows()]
    return nodes

def load_oms_links(file_path):
    df = pd.read_csv(file_path)
    oms_links = [OmsLink(row['omsId'], row['remoteOmsId'], row['src'], row['snk'], 
                         row['cost'], row['distance'], row['ots'], row['osnr'], 
                         row['slice'], row['colors']) for idx, row in df.iterrows()]
    return oms_links

def load_relays(file_path):
    df = pd.read_csv(file_path)
    relays = [Relay(row['relayId'], row['relatedRelayId'], row['nodeId'], 
                    row['localId'], row['relatedLocalId'], row['dimColors']) for idx, row in df.iterrows()]
    return relays

def load_services(file_path):
    df = pd.read_csv(file_path)
    services = [Service(row['src'], row['snk'], row['sourceOtu'], row['targetOtu'], 
                        row['m_width'], row['bandType'], row['sourceDimColors'], 
                        row['targetDimColors']) for idx, row in df.iterrows()]
    return services
