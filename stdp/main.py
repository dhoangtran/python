#!/usr/bin/env python2.7
# coding: utf-8

from __future__ import print_function, division
import argparse
#from bnc_model import Bnc_Model

def read_file(n_rows, n_cols, distances_file, taxis_file, requests_file):
    n_regions = n_rows * n_cols

    distances = []
    with open(distances_file) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            d = float(line.strip().split(' '))
            distances.append(d)

    taxis = []
    with open(taxis_fname) as f:
        f.readline()
        for line in f:
            line = line.strip()
            if not line: continue
            [n1, n2] = line.strip().split(',')
            [v1, v2] = [get_id(i) for i in (n1, n2)]
            add_edge(v1, v2)

    requests = []
    
    with open(graph_fname) as f:
        f.readline()
        for line in f:
            line = line.strip()
            if not line: continue
            [n1, n2] = line.strip().split(',')
            [v1, v2] = [get_id(i) for i in (n1, n2)]
            add_edge(v1, v2)

    n_vertices = max(node_ids.keys()) + 1
    
    
    def get_constraints(cons_fname):    
        constraints = []
        if cons_fname is not None:
            with open(cons_fname) as f:
                f.readline()
                for line in f:
                    line = line.strip()
                    if not line: continue
                    [n1, n2, w] = line.split(',')
                    [v1, v2] = [get_id(i) for i in (n1, n2)]
                    w = float(w)
                    constraints.append((v1, v2, w))
        return constraints
    cl_constraints = get_constraints(cl_fname)
    ml_constraints = get_constraints(ml_fname)
    
    return n_vertices, list(edges), cl_constraints, ml_constraints, node_ids


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('distances_file', 
                        help='file containing distance matrix')
    parser.add_argument('taxis_file', 
                        help='file containing the list of taxis')
    parser.add_argument('requests_file', 
                        help='file containing the sequence of requests')
    parser.add_argument('--timeout', type=float,default=None, 
                        help='set a time limit')
    args = parser.parse_args()

    assert(args.gamma >= 0 and args.gamma <= 1)

    (distances, taxis, requests) = read_file(args.distances_file,
                                              args.taxis_file,
                                              args.requests_file)                      
    timeout = args.timeout
    
    kwargs = dict(distances=distances, 
                  taxis=taxis, 
                  requests=requests,
                  timeout=timeout)
    
    #m = Bnc_Model(**kwargs)
    #m.solve()
    #m.print_stat()
    
    #print('node count:', m.node_count)
    #print('mip gap:', m.mip_gap)
    #print('objective value:', m.objective)
    #print('runtime:', m.runtime)

    #if (m.optimal):
    #    print('OPTIMAL')
    #else:
    #    print('NOT OPTIMAL')
    
    # save clusters
    #f = open(args.out_file, 'w')
    #id = 0
    #for cluster in m.clusters:
    #    for node in cluster:
    #        f.write(node_ids[node] + ',' + str(id) + '\n')
    #    id += 1
    #f.close() 
