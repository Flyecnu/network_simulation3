import json
from data_handler import load_nodes, load_oms_links, load_relays, load_services
from path_calculator import PathCalculator
import csv

def tuple_to_string_key(data):
    """
    Recursively convert tuple keys in a dictionary to string keys.
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if isinstance(key, tuple):
                key = str(key)
            new_data[key] = tuple_to_string_key(value)
        return new_data
    elif isinstance(data, list):
        return [tuple_to_string_key(item) for item in data]
    else:
        return data

def string_key_to_tuple(data):
    """
    Recursively convert string keys back to tuple keys.
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if isinstance(key, str) and key.startswith('(') and key.endswith(')'):
                key = eval(key)  # Convert string back to tuple
            new_data[key] = string_key_to_tuple(value)
        return new_data
    elif isinstance(data, list):
        return [string_key_to_tuple(item) for item in data]
    else:
        return data

def save_init_data(path_calculator, file_name):
    data = {
        'paths_in_use': tuple_to_string_key(path_calculator.paths_in_use),
        'backup_paths': tuple_to_string_key(path_calculator.backup_paths),
        'edge_service_matrix': tuple_to_string_key(path_calculator.edge_service_matrix)
    }
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    nodes = load_nodes('data/node.csv')
    oms_links = load_oms_links('data/oms.csv')
    relays = load_relays('data/relay.csv')
    services = load_services('data/service.csv')

    path_calculator = PathCalculator(oms_links)
    path_calculator.calculate_paths(services)

    path_calculator.recompute_backup_paths()

    save_init_data(path_calculator, 'results/paths_data.json')
    print("Initialization complete and data saved.")

if __name__ == "__main__":
    main()
