import numpy as np
import matplotlib.pyplot as plt
import random

def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0,14)]
    return "#"+color

def draw_result(acc_list, loss_list, test_acc = None,  fig_path = "./train_result.jpg"):
    fig = plt.figure()
    loss_fig = fig.add_subplot(311)
    acc_fig = fig.add_subplot(312)
    test_acc_fig  = fig.add_subplot(313)
    loss_fig.plot(np.arange(1, len(loss_list)+1), loss_list)
    acc_fig.plot(np.arange(1, len(acc_list)+1), acc_list)
    test_acc_fig.plot(np.arange(1, len(test_acc)+1), test_acc)
    loss_fig.set_ylabel('train loss')
    acc_fig.set_ylabel('train accuracy')
    test_acc_fig.set_ylabel('Test accuracy')
    loss_fig.set_xlabel('epoch')
    acc_fig.set_xlabel('epoch')
    acc_fig.set_ylim(0,1.0)
    test_acc_fig.set_xlabel('epoch')
    test_acc_fig.set_ylim(0,1.0)
    plt.savefig(fig_path)

# convert bipart-graph to simple graph
def graph_convert(graph):
    new_links = []
    index = len(graph['nodes']) + 1
    new_nodes = list(graph['nodes'])
    for link in graph['links']:
        ll = {}
        nn = {}
        nn['inst_type'] = 'connect'
        nn['net_type'] = link['weight']
        nn['id'] = 'connect_%d'%index
        new_nodes.append(nn)
        index += 1
        ll['source'] = link['source']
        ll['target'] = nn['id']
        ll['weight'] = 0
        new_links.append(ll)
        ll = {}
        ll['source'] = link['target']
        ll['target'] = nn['id']
        ll['weight'] = 0
        new_links.append(ll)
    graph['nodes'] = new_nodes
    graph['links'] = new_links
    return graph

types = {'nmos': 0, 'pmos' : 1, 'cap':2, 'res' : 3, 'inductor' : 4}

def graphForSubgraphMatchCXX(graph,out_path='./', name = 'pattern_graph'):
    with open(out_path + name + '.graph', 'w', encoding='utf-8') as f:
        f.write('t %d %d\n'%(len(graph['nodes']),len(graph['links'])))
        i=0
        typeId = 0
        nodeId2Index = {}
        nodes = []
        links = []
        for node in graph['nodes']:
            if node['inst_type'] == 'connect':
                typeId = node['net_type']
            elif node['inst_type'] == 'net':
                typeId = 0
            else:
                if node['inst_type'] in types.keys():
                    typeId = 9 + types[node['inst_type']]
                else:
                    types[node['inst_type']] = len(types.keys())
                    typeId = 9 + types[node['inst_type']]
            nodeId2Index[node['id']] = i
            nodes.append([i, typeId, 0])
            i+=1
        
        for link in graph['links']:
            links.append([nodeId2Index[link['source']], nodeId2Index[link['target']]])
            nodes[nodeId2Index[link['source']]][2] += 1
            nodes[nodeId2Index[link['target']]][2] += 1
        
        for node in nodes:
            f.write('v %d %d %d\n'%(node[0],node[1],node[2]))
        for link in links:
            f.write('e %d %d\n'%(link[0],link[1]))
        f.close()