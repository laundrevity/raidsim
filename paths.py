# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 12:21:14 2018

@author: conor
"""

# this file contains the class definitions for paths and their logic

# todo: A. implement create_path using Djikstra, A*, or something else
#       B. incorporate the node finding methods into the Melee update method
#       C. determine conditions under which create_path is invoked

# B. if you are near node n and the next is n', then the unit should approach n'
# (so the initial node of course is the melee's position, and the final is the boss)
# m   n   n'  n''  B

def dist(p1,p2):
    x1 = p1[0]
    x2 = p2[0]
    y1 = p1[1]
    y2 = p2[1]
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

class Path():
    def __init__(self,unit,boss):
        self.unit = unit
        self.boss = boss
        self.create_path()
        
    def create_path(self):
        # generate a sequence of "nodes" corresponding to the optimal path from unit to boss
        nodes = [[0,0],[2,2],[4,4]]
        self.nodes = nodes
    
    def find_nearest_node(self):
        min_dist = 1000.
        min_node = None
        for node in self.nodes:
            d = dist(self.unit,node)
            if d < min_dist:
                min_dist = d
                min_node = node
        return min_node
    
    def find_next_node(self):
        min_node = self.find_nearest_node()
        min_index = self.nodes.index(min_node)
        if min_index <= len(self.nodes) - 2:
            return self.nodes[min_index+1]
        else:
            return self.nodes[-1]