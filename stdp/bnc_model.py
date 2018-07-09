# coding: utf-8

from __future__ import print_function, division
from gurobipy import Model, GRB, quicksum, LinExpr, GurobiError
import networkx as nx
from networkx.algorithms.flow import edmonds_karp
from timeit import default_timer as timer


class Cut_Finder(object):
    def __init__(self, ingraph_nnodes, ingraph_edges):
        G = nx.DiGraph()
        G.add_nodes_from(range(2*ingraph_nnodes))

        for i in range(ingraph_nnodes):
            G.add_edge(2*i, 2*i+1)
            G.add_edge(2*i+1, 2*i)

        for v1, v2 in ingraph_edges:
            G.add_edge(v1*2+1, v2*2) 
            G.add_edge(v2*2+1, v1*2)
        
        self.G = G
        self.in_nodes = ingraph_nnodes
        self.in_edges = set(ingraph_edges)
        self.capacity_edges =  [(2*i, 2*i+1) for i in range(ingraph_nnodes)]
        self.capacity_edges += [(2*i+1, 2*i) for i in range(ingraph_nnodes)]
        
    def update_capacities(self, ingraph_capacities):
        edge_capacities = dict(zip(self.capacity_edges, ingraph_capacities * 2))
        nx.set_edge_attributes(self.G, 'capacity', edge_capacities)        
    
    def find_cutset(self, in1, in2):
        try:
            _, (reachable, non_reachable) = nx.minimum_cut(self.G, 
                                                           in1*2+1, in2*2,
                                                           flow_func=edmonds_karp)
        except nx.NetworkXUnbounded:
            print('unbounded flow for nodes %d and %d'%(in1, in2))
        cutset = set()
        for u, nbrs in ((n, self.G[n]) for n in reachable):
            cutset.update((u, v) for v in nbrs if v in non_reachable)
        return [i//2 for (i, _) in cutset]
    
    def get_cutsets(self, ingraph_capacities):
        self.update_capacities(ingraph_capacities)
        
        cutsets = []
        for in1 in range(self.in_nodes):
            for in2 in range(in1+1, self.in_nodes):
                if (in1, in2) in self.in_edges: continue
                if ingraph_capacities[in1] + ingraph_capacities[in2] <= 1: continue
                    
                cutset = self.find_cutset(in1, in2)
                cut_csum = sum(ingraph_capacities[i] for i in cutset)
                if cut_csum < ingraph_capacities[in1] + ingraph_capacities[in2] -1:
                    cutsets.append((in1, in2, cutset))
        return cutsets


def mincut_callback(model, where):

    if model._impcounter < 10 and where == GRB.Callback.MIPNODE:
        if model.cbGet(GRB.Callback.MIPNODE_NODCNT) != 0: return
            
        start = timer()
        
        relaxation_objval = model.cbGet(GRB.Callback.MIPNODE_OBJBND)
        if model._relobj is not None and model._relobj != 0:
            imp = (model._relobj - relaxation_objval) / model._relobj
            if imp < 0.005: 
                model._impcounter += 1
            else:
                model._impcounter = 0
        model._relobj = relaxation_objval

        for i in range(model._k):
            capacities = model.cbGetNodeRel(model._vars[i])
            cutsets = model._cutfinder.get_cutsets(capacities)
            for (u, v, cutset) in cutsets:
                cutset_expr = quicksum(model._vars[i][j] for j in cutset)
                model.cbCut(cutset_expr >= model._vars[i][u] + model._vars[i][v] - 1)
            if model._single_cut and cutsets:
                break
        model._root_cuttime += timer() - start
        
    elif where == GRB.Callback.MIPSOL:
            
        start = timer()
        
        for i in range(model._k):
            capacities = model.cbGetSolution(model._vars[i])
            cutsets = model._cutfinder.get_cutsets(capacities)
            for (u, v, cutset) in cutsets:
                cutset_expr = quicksum(model._vars[i][j] for j in cutset)
                model.cbLazy(cutset_expr >= model._vars[i][u] + model._vars[i][v] - 1)
        model._tree_cuttime += timer() - start


class Bnc_Model(object):
    def __init__(self, distances, taxis, requests, timeout=None):
        self.distances = distances
        self.taxis = taxis
        self.requests = requests
        self.timeout = timeout
        
        model = Model('static_dispatching')
        model.params.OutputFlag = 0
        model.params.UpdateMode = 1
        model.Params.PreCrush = 1
        model.Params.LazyConstraints = 1        
        
        T = 1000000
        n_taxis = len(taxis)
        n_requests = len(requests)
        n = n_taxis + n_requests
        t = distances 
        x = []
        for i in range(n):
            u = []
            for j in range(n):
                v = model.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY)
                u.append(v)
            x.append(u)
        
        pick0 = []
        for i in range(n_requests):
            u = model.addVar(lb=0.0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)
            pick0.append(u)
            
        # constraint (2)
        for v in range(n):
            model.addConstr(quicksum([x[u][v] for u in range(n)]),
                            GRB.EQUAL, 1)
        
        # constraint (3)
        for u in range(n):
            model.addConstr(quicksum([x[u][v] for v in range(n)]),
                            GRB.EQUAL, 1)
        
        # constraint (5)
        for i in range(n_requests):
            model.addConstr(pick0[i] - quicksum([(taxis[k][0] + t[taxis[k][1]][requests[i][1]]) * x[k][n_taxis + i] for k in range(n_taxis)]), 
                            GRB.GREATER_EQUAL, 0)                                 
        
        # constraint (6)
        for i in range(n_requests):
            for j in range(n_requests):
                model.addConstr(pick0[j] - pick0[i] - 
                                t[requests[i][1]][requests[i][2]] - 
                                t[requests[i][2]][requests[j][1]] +
                                T * (1 - x[n_taxis + i][n_taxis + j]),
                                GRB.GREATER_EQUAL, 0)
        
        # constraint (7)
        for i in range(n_requests):
            model.addConstr(pick0[i], 
                            GRB.GREATER_EQUAL, requests[i][0])

        objective = quicksum(pick0[i] - requests[i][0] for i in range(n_requests))
        model.setObjective(objective, GRB.MINIMIZE)
        
        #model._cutfinder = Cut_Finder(n_vertices, edges)
        model._x = x
        model._pick0 = pick0
        #model._k = k
        #model._relobj = None
        #model._impcounter = 0
        #model._single_cut = single_cut
        
        # runtime information
        #model._root_cuttime = 0
        #model._tree_cuttime = 0
        
        self.model = model
               
    def solve(self):
        self.model.optimize()
        self._x = self.model._x
        self._pick0 = self.model._pick0
#         if self.timeout:
#             self.model.Params.TimeLimit = self.timeout        
#         try:
#             self.model.optimize(mincut_callback)
#         except GurobiError:
#             print(GurobiError.message)
#          
#         self.objective = None
#         self.clusters = None
#         self.optimal = (self.model.Status == GRB.OPTIMAL)
#         self.runtime = self.model.Runtime
#         self.node_count = self.model.nodecount
#         self.mip_gap = self.model.mipgap
#         self.objective = self.model.ObjVal
#          
#         if self.model.solcount > 0:
#             clusters = []
#             for i in range(self.k):
#                 cluster = []
#                 for j in range(self.n_vertices):
#                     if abs(self.model._vars[i][j].x) > 1e-4:
#                         cluster.append(j)
#                 clusters.append(cluster)
#             self.clusters = clusters
        
    def print_stat(self):

        print('separation time in root: %f' %self.model._root_cuttime)
        print('separation time in tree: %f' %self.model._tree_cuttime)
