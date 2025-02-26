

from csv2graph import csv2graph
from graph2drawio import graph2drawio
from Устарело.graph2yEd import graph2yEd

if __name__ == "__main__":

    import os
    import sys
    sys.path.append("")

    dir_drug_data = "data\\drug_links"
    dir_output_data_drawio = "data\\graph_data_drawio"
    dir_output_data_yEd = "data\\graph_data_yEd"

    for i, filename in enumerate(os.listdir(dir_drug_data)):
        G = csv2graph(f"{dir_drug_data}\\{filename}")
        drawio = graph2drawio(G)
        yEd = graph2yEd(G)

        filename_drawio = "".join(filename.split(".")[:-1])+ ".drawio"
        # Записываем в файл
        with open(f"{dir_output_data_drawio}\\{filename_drawio}", "w", encoding="utf-8") as f:
            f.write(drawio)
        
        filename_yEd = "".join(filename.split(".")[:-1])+ ".graphml"
        # Записываем в файл
        with open(f"{dir_output_data_yEd}\\{filename_yEd}", "w", encoding="utf-8") as f:
            f.write(yEd)


    import networkx as nx

    dir_output_data_drawio = "data\\graph_data_drawio_edit"
    dir_output_data_yEd = "data\\graph_data_yEd_edit"

    G = nx.read_gexf("data\\graph_data_gexf_edit\\drug_karvedilol.gexf")
    drawio = graph2drawio(G)
    # Записываем в файл
    with open(f"{dir_output_data_drawio}\\drug_karvedilol.drawio", "w", encoding="utf-8") as f:
        f.write(drawio)
        
    yEd = graph2yEd(G)
    # Записываем в файл
    with open(f"{dir_output_data_yEd}\\drug_karvedilol.graphml", "w", encoding="utf-8") as f:
        f.write(yEd)


    G = nx.read_gexf("data\\graph_data_gexf_edit\\drug_amlodipin_perindopril.gexf")
    drawio = graph2drawio(G)
    # Записываем в файл
    with open(f"{dir_output_data_drawio}\\drug_amlodipin_perindopril.drawio", "w", encoding="utf-8") as f:
        f.write(drawio)

    yEd = graph2yEd(G)
    # Записываем в файл
    with open(f"{dir_output_data_yEd}\\drug_amlodipin_perindopril.graphml", "w", encoding="utf-8") as f:
        f.write(yEd)





