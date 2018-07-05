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
            d = [float(i) for i in line.strip().split(' ')]
            distances.append(d)

    taxis = []
    with open(taxis_file) as f:
        f.readline()
        for line in f:
            line = line.strip()
            if not line: continue
            t = int(line)
            taxis.append(t)

    requests = []
    with open(requests_file) as f:
        f.readline()
        for line in f:
            line = line.strip()
            if not line: continue
            r = [int(i) for i in line.strip().split(' ')]
            requests.append(r)

    return distances, taxis, requests


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('n_rows', 
                        help='number of rows')
    parser.add_argument('n_cols', 
                        help='number of cols')
    parser.add_argument('distances_file', 
                        help='file containing distance matrix')
    parser.add_argument('taxis_file', 
                        help='file containing the list of taxis')
    parser.add_argument('requests_file', 
                        help='file containing the sequence of requests')
    parser.add_argument('--timeout', type=float,default=None, 
                        help='set a time limit')
    args = parser.parse_args()

    (distances, taxis, requests) = read_file(int(args.n_rows),
                                             int(args.n_cols),
                                             args.distances_file,
                                             args.taxis_file,
                                             args.requests_file)                      
    timeout = args.timeout
    
    print(distances)
    print(taxis)
    print(requests)
    
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
