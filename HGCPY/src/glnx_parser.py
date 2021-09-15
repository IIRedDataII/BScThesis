import os
import networkx


#   helper
def _split_name(filename):
    name = filename
    ending = ''
    for index in range(len(filename)-1, -1, -1):
        if filename[index] == '.':
            name = filename[:index]
            ending = filename[index:]
    return name, ending


#   parse
def pull_graph(hgcdicodaged, graph_id):
    #   graph_data[0] = adjacency matrix, graph_data[1] = node labels, graph_data[2] = edge labels
    graph_data = hgcdicodaged.get_graph(graph_id)
    graph = networkx.Graph()
    for x in range(len(graph_data[1])):
        graph.add_node(x, hgc_node_label=graph_data[1][x])
    for x in range(len(graph_data[0])):
        for y in range(len(graph_data[0][x])):
            if graph_data[0][x][y] == 1:
                graph.add_edge(x, y, hgc_edge_label=graph_data[2][x, y])
    return graph


def push_graph(hgcdicodaged, graph, name, node_label_key, edge_label_key):
    wrong_node_format = False
    wrong_edge_format = False

    graph_id = hgcdicodaged.add_graph(name)

    for node in graph.nodes:  # here "node" is an ID and not a list, no clue why
        try:
            label = graph.nodes[node][node_label_key]
        except KeyError:
            label = 0
            wrong_node_format = True
        try:
            hgcdicodaged.add_node(graph_id, int(node), label if isinstance(label, int) else int(label))
        except ValueError:
            raise ValueError("Node " + node + " of graph \"" + name + "\" has an inconvertible value for key \"" + node_label_key + "\".")

    optimized = None
    if len(graph.edges) > 0:
        optimized = len(next(iter(graph.edges.keys()))) == 2
    for edge in graph.edges:
        try:
            label = graph.edges[edge[0], edge[1]][edge_label_key] if optimized else graph.edges[edge[0], edge[1], 0][edge_label_key]
        except KeyError:
            label = 0
            wrong_edge_format = True
        try:
            hgcdicodaged.add_edge(graph_id, int(edge[0]), int(edge[1]), label if isinstance(label, float) else float(label))
        except ValueError:
            raise ValueError("Edge (" + edge[0] + ", " + edge[1] + ") of graph \"" + name + "\" has an inconvertible value for key \"" + edge_label_key + "\".")

    hgcdicodaged.reinit_ged()

    if wrong_node_format:
        print("Warning: Couldn't find node label with key \"" + node_label_key + "\" for some nodes in graph \"" + name + "\". Setting them to 0.")
    if wrong_edge_format:
        print("Warning: Couldn't find edge label with key \"" + edge_label_key + "\" for some edges in graph \"" + name + "\". Setting them to 0.")

    return graph_id


def export_environment(hgcdicodaged, out_dir):
    try:
        os.mkdir(out_dir + 'export/')
    except FileExistsError:
        pass

    for graph_id in range(hgcdicodaged.get_number_of_graphs()):
        graph = pull_graph(hgcdicodaged, graph_id)
        networkx.write_graphml(graph, out_dir + 'export/' + hgcdicodaged.get_graph_name(graph_id) + ".gml")


def import_environment(hgcdicodaged, directory, node_label_key, edge_label_key):
    filenames = os.listdir(directory)
    for filename in filenames:
        name, ending = _split_name(filename)
        if ending == '.gml':
            graph = networkx.read_graphml(os.path.join(directory, filename))
            push_graph(hgcdicodaged, graph, name, node_label_key, edge_label_key)
