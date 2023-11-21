# -*- coding: utf-8 -*-
"""
Created on Tue August 10 2021

/*
 * GNU GPL v3 License (by, nc, nd, sa)
 *
 * Copyright 2021 GEOframe group
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

@author: GEOframe group
"""

import networkx as nx
import csv


def get_raw_network(topology_path):
    """
    Read a GEOFrame topology file and create a Graph object.

    :param topology_path:
    :return: a  graph

    @author: Daniele Andreis
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

    @author: Daniele Andreis
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

    @author: Daniele Andreis
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
    """
    net_up = [n for n in nx.traversal.bfs_tree(net, node, reverse=True)]
    net_up = net.subgraph(net_up)
    return nx.DiGraph(net_up)


def filter_to_calibrate(net, nodes, outlet):
    for value in nodes:
        if value in net and value != outlet:
            to_delete = [n for n in nx.traversal.bfs_tree(net, value, reverse=True) if n != value]
            net.remove_nodes_from(to_delete)
    return net


def get_subgraph(net, gauge, gauge_id, is_calibration):
    outlet = gauge[gauge_id]
    net_up = get_up_streem_network(net, outlet)
    reversed_dict = dict((v, k) for k, v in gauge.iteritems())
    for key, value in reversed_dict:
        if not net_up.has_node(key):
            reversed_dict.pop(key)
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
            gauge = reversed_dict[node]
            if node == outlet:
                calibrate = 'True'
            else:
                calibrate = 'False'
        else:
            parent = list(net_up.predecessors(node))
            if parent:
                calibrate = net_up.nodes[parent]["calibrate"]
                gauge = net_up.nodes[parent]["gauge"]
            else:
                gauge = None
        nx.set_node_attributes(net_up, {node: {'gauge': gauge, 'calibrate': calibrate}})

    if '0' not in net_up:
        print("error")

    return net_up


def get_downstream_network(net, basin_id):
    """

    :param net:
    :param basin_id:
    :return:
    """
    return None


def write_network(net, topology_path):
    """

    :param net:
    :param G:
    :param topology_path:
    :return:
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

    :param dictionary_stream_gauge_subbasin_file_path:
    """
    gauge = {}
    with open(dictionary_stream_gauge_subbasin_file_path, 'r') as data:
        for line in data:
            p = line.split()
            gauge[p[0]] = p[1]


def sort_node(net, nodes):
    """

    :param dictionary_stream_gauge_subbasin_file_path:
    """
    topological_order = list(nx.topological_sort(net))
    return sorted(nodes, key=lambda x: topological_order.index(x))


def get_order_node(topo_pat, dict_path):
    """

    :param dictionary_stream_gauge_subbasin_file_path:
    """
    gauge = {}
    sub_id = []
    with open(dict_path, 'r') as data:
        for line in data:
            p = line.split()
            gauge[p[1]] = p[0]
            sub_id.append(p[1])
    sub_id = order_node(topo_pat, sub_id)
    return [gauge[i] for i in sub_id]
