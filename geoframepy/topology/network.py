# -*- coding: utf-8 -*-
"""
Created on Tue August 10 2021

/*
 * GNU GPL v3 License (by, nc, nd, sa)
 *
 * Copyright 2024 GEOframe group
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

:author: GEOframe group
"""

import networkx as nx
import csv


def get_raw_network(topology_path):
    """
    Read a GEOFrame topology file and create a Graph object.

    :param topology_path:
    :return: a  graph

    :author: Daniele Andreis
    """
    edges = []
    with open(topology_path, 'r') as data:
        for line in data:
            p = line.split()
            edges.append([p[0], p[1]])
    G = nx.DiGraph()
    G.add_edges_from(edges)
    return G


def get_network(topology_path):
    """
    Read a GEOFrame topology file and create a Graph object.

    :param topology_path.
    :return: a  directed tree graph.

    :author: Daniele Andreis
    """
    net = get_raw_network(topology_path)
    if check_network(net):
        return net
    else:
        return None


def check_network(net):
    """
    Verify if the Graph is a directed acyclic tree. It perform the following test:
    * directed and acyclic graph
    * if it's connected
    * if it's a tree
    * if there is a weakly connected nodes.

    :param net: the Graph to check.
    :return: true if pass all test.

    :author: Daniele Andreis
    """
    if not nx.is_directed_acyclic_graph(net):
        print("Attention the graph isn't acycling graph")
        cycles = list(nx.find_cycle(net, orientation='original'))
        print("Cycles in the graph:")
        for cycle in cycles:
            print(cycle)
        return False
    if not nx.is_directed(net):
        print("Attention the graph isn't directed")
        if nx.is_connected(net):
            print("G is a connected graph but contains cycles.")
        else:
            print("G is not a connected graph, so it cannot be a tree.")
        return False
    if not nx.is_tree(net):
        print("Attention the graph isn't tree graph")
        print("The graph is not a tree.")
        print("The directed graph is not a tree.")
        weakly_connected_components = list(nx.weakly_connected_components(net))
        if len(weakly_connected_components) > 1:
            print("The directed graph has multiple weakly connected components." + str(weakly_connected_components))
        # Additional checks to determine why it's not a tree
        if not nx.is_weakly_connected(net):
            print("The directed graph is not weakly connected, so it cannot be a directed tree.")
        else:
            cycles = list(nx.simple_cycles(net))
            if cycles:
                print("The directed graph contains cycles:", cycles)
            else:
                print("The directed graph is weakly connected but does not meet the criteria of a directed tree.")
        return False
    return True


def get_up_streem_network(net, node):
    """
    Get the upstream network.

    :param net: the network.
    :param node: the node where break the network
    :return: the network from the node to the leaves.

    :author: Daniele Andreis

    """
    net_up = [n for n in nx.traversal.bfs_tree(net, node, reverse=True)]
    net_up = net.subgraph(net_up)
    return nx.DiGraph(net_up)


def filter_to_calibrate(net, nodes, outlet):
    """
    Filters the network to retain only the calibration nodes and their downstream nodes.

    This function modifies the input network `net` by removing nodes that are not part of the
    calibration set. For each node in `nodes`, it retains the node and its upstream nodes
    unless the node is the specified `outlet`. All other upstream nodes are removed from
    the network.

    :param net: A directed graph represented as a NetworkX DiGraph object.
    :param nodes: A list or set of nodes to be retained for calibration.
    :param outlet: The outlet node which should not be removed from the network.

    :return: The modified network with only the calibration nodes and their upstream nodes retained.

    :example:
        import networkx as nx
        net = nx.DiGraph()
        net.add_edges_from([(1, 2), (2, 3), (3, 4), (2, 5)])
        nodes = {2, 3}
        outlet = 2
        filtered_net = filter_to_calibrate(net, nodes, outlet)
        list(filtered_net.nodes)
    [2, 3, 4]

    :author: Daniele Andreis
    """
    for value in nodes:
        if value in net and value != outlet:
            to_delete = [n for n in nx.traversal.bfs_tree(net, value, reverse=True) if n != value]
            net.remove_nodes_from(to_delete)
    return net


def get_subgraph(net, gauge, gauge_id, is_calibration):
    """
    Generates a subgraph of the network starting from a specified gauge node.

    This function creates a subgraph of the input network `net` starting from the node
    specified by `gauge_id` in the `gauge` dictionary. It first obtains the upstream
    network from the specified outlet node and then processes this subgraph to optionally
    filter it for calibration purposes. It sets attributes on the nodes of the subgraph
    and ensures that it is properly structured as a directed graph.

    :param net: A directed graph represented as a NetworkX DiGraph object.
                The original network from which the subgraph will be derived.
    :param gauge: A dictionary mapping gauge IDs to node IDs in the graph.
                  The keys are gauge IDs and the values are node IDs in the network.
    :param gauge_id: The ID of the gauge from which to start generating the subgraph.
    :param is_calibration: A boolean flag indicating whether to apply calibration filtering
                           to the subgraph.

    :return: A subgraph of the original graph starting from the specified gauge node.
             The subgraph includes nodes upstream from the specified gauge node and sets
             appropriate attributes for calibration and gauge IDs.

    :raises KeyError: If the specified gauge_id is not found in the gauge dictionary.
    :raises NetworkXError: If the subgraph is not properly structured as a directed graph.

    :example:
        import networkx as nx
        net = nx.DiGraph()
        net.add_edges_from([(1, 2), (2, 3), (3, 4), (2, 5)])
        gauge = {'g1': 1, 'g2': 2, 'g3': 3}
        gauge_id = 'g2'
        is_calibration = False
        subgraph = get_subgraph(net, gauge, gauge_id, is_calibration)
        list(subgraph.nodes)
    [2, 3, 4, '0']

    :author: Daniele Andreis
    """
    outlet = gauge[gauge_id]
    net_up = get_up_streem_network(net, outlet)
    reversed_dict = dict((v, k) for k, v in gauge.items())

    keys_to_remove = [key for key, value in reversed_dict.items() if not net_up.has_node(key)]
    for key in keys_to_remove:
        value = reversed_dict.pop(key)
        gauge.pop(value)

    if is_calibration:
        net_up = filter_to_calibrate(net_up, reversed_dict, outlet)

    net_up.add_edges_from([(outlet, "0")])
    if not nx.is_directed(net_up):
        print("Attention the graph isn't directed")

    nx.set_node_attributes(net_up, gauge_id, 'gauge')
    nx.set_node_attributes(net_up, 'True', 'calibrate')
    for node in nx.topological_sort(net_up):
        if node in gauge.values():
            g = reversed_dict[node]
            if node == outlet:
                calibrate = 'True'
            else:
                calibrate = 'False'
        else:
            parent = list(net_up.predecessors(node))
            if parent:
                calibrate = net_up.nodes[parent[0]]["calibrate"]
                g = net_up.nodes[parent[0]]["gauge"]
            else:
                g = None
                calibrate = 'False'
        nx.set_node_attributes(net_up, {node: {'gauge': g, 'calibrate': calibrate}})

    if '0' not in net_up:
        print("error")

    return net_up


def get_downstream_network(net, node):
    """
       Get the downstream network from a specified node in a directed tree graph.

       This function takes a directed tree graph `net` and a starting `node`, and returns a subgraph
       that includes all nodes except for those in the upstream network from the specified node to the
       leaves. Essentially, it returns the downstream network by subtracting the upstream nodes from
       the entire graph.

       :param net: A directed tree graph represented as a NetworkX DiGraph object.
                   This graph should represent a tree structure.
       :param node: The node from which to determine the upstream network to be removed.
       :return: A subgraph of the original graph that represents the downstream network from the specified node.

       :raises NetworkXError: If the specified node is not in the graph.

       :example:
        node = "2"
        downstream_net = get_downstream_network(net, node)
        list(downstream_net.nodes)
       [1, 5, 6]

       :author: Daniele Andreis
       """
    if node not in net:
        raise nx.NetworkXError(f"The node {node} is not in the graph.")
    # Get the upstream network from the specified node
    upstream_nodes = get_up_streem_network(net, node)
    # Create the downstream network by removing the upstream nodes
    downstream_nodes = set(net.nodes) - upstream_nodes
    downstream_net = net.subgraph(downstream_nodes)
    return nx.DiGraph(downstream_net)


def write_network(net, topology_path):
    """
       Writes the network topology to a file.

       This function takes a directed graph `net` and writes its topology to a specified file.
       For each node in the graph (except for the node '0'), it records the node and one of its
       neighbors. If a node has no neighbors, it records '0' as the neighbor. The output is written
       to a file in a space-separated format as GEOframe standard.

       :param net: A directed graph represented as a NetworkX DiGraph object. The graph should contain
                   nodes and edges representing the network topology.
       :param topology_path: The path to the file where the network topology will be written. Each line
                             in the file will contain a node and one of its neighbors, separated by a space.

       :return: None. The function writes the network topology to the specified file.

       :raises IOError: If there is an issue writing to the file specified by `topology_path`.

       :example:
           import networkx as nx
           net = nx.DiGraph()
           net.add_edges_from([(1, 2), (2, 3), (3, 4)])
           topology_path = 'path/to/topology_file.txt'
           write_network(net, topology_path)
       # This will write the following lines to 'path/to/topology_file.txt':
       # 1 2
       # 2 3
       # 3 4

       :author: Daniele Andreis
       """
    node_to_plot = [[n, next(net.neighbors(n)) if len(list(net.neighbors(n))) > 0 else "0"] for n in net if n != '0']
    with open(topology_path, 'w') as f:
        csv.writer(f, delimiter=' ').writerows(node_to_plot)


def plot_network(net, path=None):
    """

    :param net:
    :param path:
    :return:
    """
    return None


def create_stream_gauge_dictionary(dictionary_stream_gauge_subbasin_file_path):
    """
    Creates a dictionary mapping stream gauges to subbasin IDs from a given file.

    This function reads a file containing stream gauge IDs and subbasin IDs, where each line
    contains a stream gauge ID and a subbasin ID separated by whitespace. It constructs and
    returns a dictionary where the keys are stream gauge IDs and the values are subbasin IDs.

    :param dictionary_stream_gauge_subbasin_file_path: The path to the file containing stream
                                                       gauge and subbasin IDs. Each line in the
                                                       file should have a stream gauge ID and a
                                                       subbasin ID separated by whitespace.

    :return: A dictionary where keys are stream gauge IDs and values are subbasin IDs.

    :raises IOError: If there is an issue reading the file specified by `dictionary_stream_gauge_subbasin_file_path`.

    :example:
         dictionary_path = 'path/to/dictionary_file.txt'
        create_stream_gauge_dictionary(dictionary_path)
    {'gauge1': 'subbasin1', 'gauge2': 'subbasin2', 'gauge3': 'subbasin3'}

    :author: Daniele Andreis
    """
    gauge = {}
    with open(dictionary_stream_gauge_subbasin_file_path, 'r') as data:
        for line in data:
            p = line.split()
            gauge[p[0]] = p[1]


def sort_node(net, nodes):
    """
    Sorts a list of nodes based on their topological order within a directed graph.

    This function takes a directed graph `net` and a list of nodes `nodes`, and returns
    the list of nodes sorted according to their topological order in the graph.
    Topological sorting is used for ordering nodes in a way that for every directed edge
    u -> v, node u comes before node v.

    :param net: A directed graph represented as a NetworkX DiGraph object.
                This graph should be acyclic for the topological sort to be valid.
    :param nodes: A list of nodes to be sorted. Each node should be present in the graph `net`.

    :return: A list of nodes sorted according to their topological order in the graph `net`.
             If the graph is not a Directed Acyclic Graph (DAG), a NetworkXUnfeasible exception
             will be raised

    :example:
     import networkx as nx
     net = nx.DiGraph()
     net.add_edges_from([(1, 2), (2, 3), (1, 3)])
     nodes = [3, 2, 1]
     sort_node(net, nodes)
    [1, 2, 3]

    :author: Daniele Andreis

    """
    topological_order = list(nx.topological_sort(net))
    return sorted(nodes, key=lambda x: topological_order.index(x))


def get_order_node(topo_pat, dict_path):
    """
       Retrieves the ordered list of stream gauges based on the topological order of subbasins.

       This function reads a dictionary file containing stream gauge and subbasin IDs, constructs
       a directed graph from the topology pattern file, and then sorts the subbasin IDs according to
       their topological order. Finally, it returns the list of stream gauges ordered according to
       this topological sorting of subbasins.

       :param topo_pat: The path to the file containing the topology pattern. This file is used to
                        construct the directed graph representing the subbasin network.
       :param dict_path: The path to the dictionary file containing stream gauge IDs and subbasin IDs.
                         Each line in this file should contain a stream gauge ID and a subbasin ID,
                         separated by whitespace.

       :return: A list of stream gauges ordered according to the topological sorting of subbasins.
                The order of gauges corresponds to the topological order of their respective subbasins.

       :raises IOError: If there is an issue reading the files specified by `topo_pat` or `dict_path`.
       :raises NetworkXUnfeasible: If the graph constructed from `topo_pat` is not a Directed Acyclic Graph (DAG)
                                   and therefore cannot be topologically sorted.

       :example:
        topo_pat = 'path/to/topology_pattern.txt'
        dict_path = 'path/to/dictionary_file.txt'
        get_order_node(topo_pat, dict_path)
       ['gauge1', 'gauge2', 'gauge3']

        :author: Daniele Andreis

       """
    gauge = {}
    sub_id = []
    with open(dict_path, 'r') as data:
        for line in data:
            p = line.split()
            gauge[p[1]] = p[0]
            sub_id.append(p[1])
    net = get_network(topo_pat)
    sub_id = sort_node(net, sub_id)
    return [gauge[i] for i in sub_id]


def simplify_network(topology_path, output_path):
    """
    Creates a dummy network where all nodes, except the node "0", point to node "0".

    This function reads a network from the given topology file and modifies it so that all nodes
    have a directed edge towards node "0". Node "0" acts as a central hub in the modified network.
    The modified network is then written to the specified output file.

    :param topology_path: The path to the file containing the original network topology. The file
                          should be readable by the `get_network` function.
    :param output_path: The path to the file where the modified network topology will be written.

    :return: None. The function writes the modified network to the specified output file.

    :example:
        topology_path = 'path/to/original_topology_file.txt'
        output_path = 'path/to/modified_topology_file.txt'
        create_dummy_network(topology_path, output_path)
    # This will create a modified network where all nodes (except "0") point to node "0"
    # and write it to 'path/to/modified_topology_file.txt'.

    :author: Daniele Andreis
    """
    # Read the original network
    net = get_network(topology_path)

    # Create a new directed graph for the dummy network
    dummy_net = nx.DiGraph()

    # Add nodes and edges to the dummy network
    for node in net.nodes:
        if node != '0':
            dummy_net.add_edge(node, '0')

    # Write the dummy network to the output file
    write_network(dummy_net, output_path)