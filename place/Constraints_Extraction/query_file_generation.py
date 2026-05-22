import os
from Tools import graph_convert, graphForSubgraphMatchCXX
import json
import networkx as nx
from networkx.readwrite import json_graph

circuit_type = {'ota_data_generator':['bias','ota_unbiased'] 
                , 'rf_data_generator':['lna','mixer', 'oscillator', 'ota']}

src_dir = './circuit_data/query_files/'

#if __name__ == '__main__':
for key in circuit_type.keys():
    for key1 in circuit_type[key]:
        #print(file, file_data)
        for netlist in os.listdir(src_dir + key + '/' + key1 + '/'):
            # file = src_dir + key + '/' + key1 + '/' + netlist
            file_data = src_dir + key + '/' + key1 + '_data/' + netlist.split('.')[0] + '_graph.json'
            graph = graph_convert(json.load(open(file_data)))
            graphForSubgraphMatchCXX(graph=graph, out_path='./queryfiles/', name=netlist.split('.')[0]+'query')
