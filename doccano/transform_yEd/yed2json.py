import networkx as nx
import os
import re
import json

dir_processed = "data\\graph_data_yed_processed"
dir_save = "data\\graph_data_polina"

def extract_label_and_tag(G, node):
    # pattern = r"^(.*?)\(([^)]+)\)\s*$"

    node_label = G.nodes[node].get('label', node)

    match = re.search(r"^(.*)\s*\(([^)]+)\)$", node_label)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return node, None


for i, filename in enumerate(os.listdir(dir_processed)):
    if filename.endswith(".graphml"):

        G = nx.read_graphml(f"{dir_processed}\\{filename}")

        json_filename = filename.split(".")[0]+'.json'
        main_prepare = [] 

        G_for_json = nx.DiGraph()

        for node in G.nodes():
            node_name, node_tag = extract_label_and_tag(G, node)
            G_for_json.add_node(node_name, label = node_tag, weight = 5)

            parents = G.predecessors(node)
            parent_tags = [extract_label_and_tag(G, parent)[1] for parent in parents]
            if parents and any(tag == 'group' for tag in parent_tags) and node_tag == 'prepare':
                label, tag = extract_label_and_tag(G, node)
                main_prepare.append(label)

        for node in G.nodes():
            node_name, node_tag = extract_label_and_tag(G, node)
            parents = G.predecessors(node)
            # parent_tags = [extract_label_and_tag(G, parent)[1] for parent in parents]
            # if node_tag == 'side_e':
            #     print(node_name, node_tag, list(parents) == [], main_prepare)

            if list(parents) == [] and node_tag == 'side_e':
                for prepare in main_prepare:
                    print(prepare, node_name, node_tag, list(parents) == [])
                    G_for_json.add_edge(prepare, node_name)

        for target, source in G.edges():
            label_t, tag_t = extract_label_and_tag(G, target)
            label_s, tag_s = extract_label_and_tag(G, source)
            G_for_json.add_edge(label_t, label_s)

        

        data = nx.node_link_data(G_for_json, edges="links")  # Преобразуем граф в формат, совместимый с JSON

        data["name"] = main_prepare
        # if len(main_prepare) == 2:
        #     if "амлодипин" in main_prepare:
        #         data["name"] = "амлодипин"
        #     else:
        #         data["name"] = main_prepare[0]   
        # else:
        # if "ацетилсалициловый кислота" in main_prepare:
        #     for prepare in main_prepare:
        #         prepare = "ацетилсалициловая кислота"
        # else:
        #     data["name"] = main_prepare[0]
            

        # data["name"] = main_prepare
        with open(f"{dir_save}\\{json_filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


