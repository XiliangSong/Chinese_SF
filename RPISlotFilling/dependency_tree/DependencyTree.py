__author__ = 'boliangzhang'

# import pygraphviz as PG

from RPISlotFilling.dependency_tree.Graph import Graph
from RPISlotFilling.dependency_tree.Graph import dijsktra
from RPISlotFilling.dependency_tree.Node import Node


class DependenceTree(object):
    # def __init__(self, typed_dependency_string=None):
    #     self.root = Node()
    #     lines = typed_dependency_string.strip().split('\n')
    #     nodes = dict()
    #     for line in lines:
    #         try:
    #             dependency = line.split('(')[0]
    #             arg1 = line.split('(')[1].split(',')[0]
    #             arg1_index = int(arg1.split('-')[-1])
    #             arg1_value = arg1.replace('-' + str(arg1_index), '').strip()
    #             arg2 = line.split('(')[1].split(',')[1].replace(')', '')
    #             arg2_index = int(arg2.split('-')[-1])
    #             arg2_value = arg2.replace('-' + str(arg2_index), '').strip()
    #             if arg1_index not in nodes.keys():
    #                 nodes[arg1_index] = Node(value=arg1_value, index=arg1_index)
    #             if arg2_index not in nodes.keys():
    #                 nodes[arg2_index] = Node(value=arg2_value, index=arg2_index, upper_dependency=dependency)
    #             else:
    #                 nodes[arg2_index].set_upper_dependency(dependency)
    #             nodes[arg1_index].add_child(nodes[arg2_index])
    #             nodes[arg2_index].set_parent(nodes[arg1_index])
    #             if dependency == 'root':
    #                 self.root = nodes[arg1_index]
    #         except ValueError:
    #             # print('problem occurred in constructing tree: ' + typed_dependency_string)
    #             continue
    #         except IndexError:
    #             continue

    def __init__(self, dependency_tuples):
        self.root = Node()
        nodes = dict()
        for t in dependency_tuples:
            dependency = t[0]
            arg1_value = '-'.join(t[1].split('-')[:-1])
            arg1_index = t[1].split('-')[-1]
            arg2_value = '-'.join(t[2].split('-')[:-1])
            arg2_index = t[2].split('-')[-1]
            if arg1_index not in nodes.keys():
                nodes[arg1_index] = Node(value=arg1_value, index=arg1_index)
            if arg2_index not in nodes.keys():
                nodes[arg2_index] = Node(value=arg2_value, index=arg2_index, upper_dependency=dependency)
            else:
                nodes[arg2_index].set_upper_dependency(dependency)
            nodes[arg1_index].add_child(nodes[arg2_index])
            nodes[arg2_index].set_parent(nodes[arg1_index])
            if dependency == 'root':
                self.root = nodes[arg1_index]

    def find_node(self, arg_text):
        # traverse tree recursively
        traversed_node = set()

        def depth_first_traverse(node, arg_text):
            traversed_node.add(node)
            found_nodes = list()
            try:
                arg_text = arg_text.encode('utf-8')
            except UnicodeDecodeError:
                pass
            if arg_text in node.value.encode('utf-8'):
                found_nodes.append(node)
            if len(node.children) == 0:
                return found_nodes
            else:
                for child in node.children:
                    if child in traversed_node:
                        continue
                    found_nodes += depth_first_traverse(child, arg_text)
                return found_nodes

        found_nodes = depth_first_traverse(self.root, arg_text)  # circle in dp raises runtime error

        return found_nodes

    def find_undirected_path(self, node1, node2):  # return path of list, list[0] is node1 and list[-1] is node2
        g = dict()

        # represent dpt as graph in dict
        traversed_node = set()

        def traverse(n):
            traversed_node.add(n)
            g[n] = list()
            g[n] += n.children
            if n.parent is not None:
                g[n] += [n.parent]
            if len(n.children) == 0:
                return
            for c in n.children:
                if c in traversed_node:
                    continue
                traverse(c)

        traverse(self.root)

        def find_all_paths(graph, start, end, path=[]):
            # print('s: ' + start.value + ' e: ' + end.value)   # output searching path for debugging
            path = path + [start]
            if start == end:
                return [path]
            if not graph.has_key(start):
                return []
            paths = []
            for node in graph[start]:
                if node not in path:
                    newpaths = find_all_paths(graph, node, end, path)
                    for newpath in newpaths:
                        paths.append(newpath)
            return paths

        paths = find_all_paths(g, node1, node2)

        return paths

    def draw_dpt(self, label, output_path):
        # get dependency edges
        traversed_node = set()

        def traverse(node):
            traversed_node.add(node)
            if node.value == 'ROOT':
                return traverse(node.children[0])
            else:
                dependency_edges = list()
                edge = (node.parent.value + '-' + str(node.parent.index),
                        node.value + '-' + str(node.index),
                        node.upper_dependency)
                dependency_edges.append(edge)
                if len(node.children) == 0:
                    return dependency_edges
                else:
                    for child in node.children:
                        if child in traversed_node:
                            continue
                        dependency_edges += traverse(child)
                    return dependency_edges

        # find all edges from tree
        try:
            edges = traverse(self.root)
        except:
            return
        graph = PG.AGraph(directed=True, strict=True, encoding='UTF-8', label=label)
        for e in edges:
            graph.add_edge(e[0], e[1], label=e[2])
        graph.layout(prog='dot')
        graph.draw(output_path, format='png')

    def construct_graph_from_tree(self):
        traversed_node = set()

        def traverse(node, dependency_graph):
            traversed_node.add(node)
            if node.value == 'ROOT':
                return traverse(node.children[0], dependency_graph)
            else:
                dependency_graph.add_edge(node.parent, node, 1)
                dependency_graph.add_node(node)
                dependency_graph.add_node(node.parent)
                if len(node.children) == 0:
                    return
                else:
                    for child in node.children:
                        if child in traversed_node:
                            continue
                        traverse(child, dependency_graph)
                    return

        # find all edges from tree
        dependency_graph = Graph()
        traverse(self.root, dependency_graph)  # circle in dp raises runtime error

        return dependency_graph

    # given a node, return nodes that within k step far from the node
    def k_step_node(self, node, k):
        # construct graph from dependency tree
        dependency_graph = self.construct_graph_from_tree()

        if dependency_graph is None:
            return []

        k_step_nodes = list()
        distance = dijsktra(dependency_graph, node)[0]
        for n in distance:
            if distance[n] <= k:
                k_step_nodes.append(n)
        return k_step_nodes

    def get_subtree_nodes(self, node):
        traverse_node = set()
        # get all nodes
        def traverse(node):
            traverse_node.add(node)
            if node.value == 'ROOT':
                return traverse(node.children[0])
            else:
                nodes = list()
                nodes.append(node)
                if len(node.children) == 0:
                    return nodes
                else:
                    for child in node.children:
                        if child in traverse_node:
                            continue
                        nodes += traverse(child)
                    return nodes

        return traverse(node)


    '''
    # this function combines two nodes if the dependency between them is nn, and if one node is 'of' another node
    def phrase_combination(self):
        # combine 'nn'
        def combine_NN_node_by_traversing(node):
            if len(node.children) == 0:
                return
            nodes_to_combine = list()
            for child in node.children:
                if child.upper_dependency == 'nn':
                    nodes_to_combine.append(child)
                    for child_child in child.children:
                        child_child.set_parent(node)
            if len(nodes_to_combine) > 0:
                nodes_to_combine.append(node)
                sorted_nodes_to_combine = sorted(nodes_to_combine, key=operator.attrgetter('index'))
                combined_value = ""
                for n in sorted_nodes_to_combine:
                    combined_value += n.value + ' '
                node.set_value(combined_value.strip())
                nodes_to_combine.remove(node)
                for c in nodes_to_combine:
                    node.remove_child(c)
                    del c
            for child in node.children:
                combine_NN_node_by_traversing(child)

        combine_NN_node_by_traversing(self.root)

        # combine 'of'
        def combine_OF_node_by_traversing(node):
            nodes_to_combine = list()
            if node.value == 'of' and len(node.children) == 1:
                nodes_to_combine.append(node.parent)
                nodes_to_combine.append(node)
                nodes_to_combine.append(node.children[0])
                sorted_nodes_to_combine = sorted(nodes_to_combine, key=operator.attrgetter('index'))
                combined_value = ""
                for n in sorted_nodes_to_combine:
                    combined_value += n.value + ' '
                if len(combined_value.split(' ')) < 5:
                    node.parent.set_value(combined_value.strip())
                    node.parent.remove_child(node)
                    for child_child in node.children[0].children:
                        node.parent.add_child(child_child)
                        child_child.set_parent(node.parent)
                    start = node.parent
                    del node
                    combine_OF_node_by_traversing(start)
                else:
                    for child in node.children:
                        combine_OF_node_by_traversing(child)
            else:
                for child in node.children:
                    combine_OF_node_by_traversing(child)

        combine_OF_node_by_traversing(self.root)
    '''