from __future__ import annotations
from abc import abstractmethod
import sys
from typing import Set
from pymjc.back import assem, flowgraph, graph
from pymjc.front import frame, temp


class RegAlloc (temp.TempMap):
    def __init__(self, frame: frame.Frame, instr_list: assem.InstrList):
        self.frame: frame.Frame = frame
        self.instrs: assem.InstrList = instr_list
        
        self.preColoredNodes: graph.Node = {}
        self.normalColoredNodes: graph.Node = {}

        self.initialNodes: graph.Node = {}
        self.spillNodess: graph.Node = {}
        self.coalesceNodes: graph.Node = {}

        self.nodeStack: graph.Node = []

        self.simplifyWorklist: graph.Node = {}
        self.freezeWorklist: graph.Node = {}
        self.spillWorklist: graph.Node = {}

        self.coalesceMoveNodes: graph.Node = {}
        self.constrainMoveNodes: graph.Node = {}
        self.freezeMoveNodes: graph.Node = {}
        self.worklistMoveNodes: graph.Node = {}
        self.activeMoveNodes: graph.Node = {}
        
        self.spillCost = {}
        
        self.adjacenceSets: graph.Node.adj() = {}
        self.adjacenceList = {}

        self.livenessOutput: Liveness.out
        self.assemFlowGraph: flowgraph.AssemFlowGraph
        
        self.moveNodesList = {}
        
        self.nodeDegreeTable = {}
        self.nodeAliasTable = {}
        self.nodeColorTable = {}
    
        self.generatedSpillTemps: temp.Temp = {}

        #TODO
    
    def simplify (self):
        temporaryIterator: iter(graph.Node)  = self.simplifyWorklist.iter()

    # // let n ∈ simplifyWorklist
        n: graph.Node = temporaryIterator.next()
    # // simplifyWorklist ← simplifyWorklist \ {n}
        temporaryIterator.remove()
    # // push(n, selectStack)
        self.nodeStack.append(n)

    # // forall m ∈ Adjacent(n)
        m: graph.Node
        for m in graph.Node.adj(n):
    #   // DecrementDegree(m)
            self.decrementDegree(m)     

    def coalesce(self):
        pass

    def freeze(self):
        temporaryNodeIterator: iter(graph.Node) = self.freezeWorklist.iter()

    # // let u ∈ freezeWorklist
        u: graph.Node = temporaryNodeIterator.next()
        temporaryNodeIterator.remove()
    # // freezeWorklist ← freezeWorklist \ {u}
        self.freezeWorklist.remove(u)

    # // simplifyWorklist ← simplifyWorklist ∪ {u}
        self.simplifyWorklist.append(u)
    # // FreezeMoves(u)
        self.freezeMoves(u)

    def selectSpill(self):
        m: iter(graph.Node) = self.spillWorklist.iter().next()
        v = InterferenceGraph.spill_cost(m)

        a = graph.Node
        for a in self.spillWorklist:
           if (InterferenceGraph.spill_cost(a) < v): 
                m = a

    # // spillWorklist ← spillWorklist \ {m}
        self.spillWorklist.remove(m)
    # // simplifyWorklist ← simplifyWorklist ∪ {m}
        self.simplifyWorklist.append(m)
    # // FreezeMoves(m)
        self.freezeMoves(m)

    def livenessAnalysis(self):
        assemFlowGraph = flowgraph.AssemFlowGraph.instr(self.instrs)
        livenessOutput = assemFlowGraph
    
    def build(self):
        pass

    def make_work_list(self):
        k = self.preColoredNodes.len()
    # // forall n ∈ initial
        nodeIterator: iter(graph.Node) = self.initialNodes
        for nodeIterator in nodeIterator.next():
    #   // Iniciando nosso n como no pseudocódigo
            n: graph.Node = nodeIterator.next()
    #   // initial ← initial \ {n}
            nodeIterator.remove()

    #   // if degree[n] ≥ K then
        if self.nodeDegreeTable(n) >= k:
    #     // spillWorklist ← spillWorklist ∪ {n}
            self.spillWorklist.append(n)
    #   }
    #   // else if MoveRelated(n) then
        else: 
            if flowgraph.AssemFlowGraph.is_move(n):
    #     // freezeWorklist ← freezeWorklist ∪ {n}
                self.freezeWorklist.append(n)
            else:
    #     // simplifyWorklist ← simplifyWorklist ∪ {n}
                self.simplifyWorklist.append(n)

    def coalesce_aux_first_check(self):
        pass

    def ok(self):
        pass

    def coalesce_aux_second_check(self):
        pass

    def freezeMoves(self):
        pass

    def assignColors(self):
        pass

    def rewriteProgram(self):
        pass

    def decrementDegree(self):
        pass
        
    def temp_map(self, temp: temp.Temp) -> str:
        str: temp  = frame.TempMap(temp)

        if str == None:
            str = frame.TempMap(InterferenceGraph.gtemp(self.nodeColorTable.get(InterferenceGraph.tnode(temp))))
        return temp.to_string()

class Color(temp.TempMap):
    def __init__(self, ig: InterferenceGraph, initial: temp.TempMap, registers: temp.TempList):
        #TODO
        pass
    
    def spills(self) -> temp.TempList:
        #TODO
        return None

    def temp_map(self, temp: temp.Temp) -> str:
        #TODO
        return temp.to_string()

    

class InterferenceGraph(graph.Graph):
    
    @abstractmethod
    def tnode(self, temp:temp.Temp) -> graph.Node:
        pass

    @abstractmethod
    def gtemp(self, node: graph.Node) -> temp.Temp:
        pass

    @abstractmethod
    def moves(self) -> MoveList:
        pass
    
    def spill_cost(self, node: graph.Node) -> int:
      return 1


class Liveness (InterferenceGraph):

    def __init__(self, flow: flowgraph.FlowGraph):
        self.live_map = {}
        
        #Flow Graph
        self.flowgraph: flowgraph.FlowGraph = flow
        
        #IN, OUT, GEN, and KILL map tables
        #The table maps complies with: <Node, Set[Temp]>
        self.in_node_table = {}
        self.out_node_table = {}
        self.gen_node_table = {}
        self.kill_node_table = {}

        #Util map tables
        #<Node, Temp>
        self.rev_node_table = {}
        #<Temp, Node>
        self.map_node_table = {}
        
        #Move list
        self.move_list: MoveList = None

        self.build_gen_and_kill()
        self.build_in_and_out()
        self.build_interference_graph()
    
    def add_ndge(self, source_node: graph.Node, destiny_node: graph.Node):
        if (source_node is not destiny_node and not destiny_node.comes_from(source_node) and not source_node.comes_from(destiny_node)):
            super.add_edge(source_node, destiny_node)

    def show(self, out_path: str) -> None:
        if out_path is not None:
            sys.stdout = open(out_path, 'w')   
        node_list: graph.NodeList = self.nodes()
        while(node_list is not None):
            temp: temp.Temp = self.rev_node_table.get(node_list.head)
            print(temp + ": [ ")
            adjs: graph.NodeList = node_list.head.adj()
            while(adjs is not None):
                print(self.rev_node_table.get(adjs.head) + " ")
                adjs = adjs.tail

            print("]")
            node_list = node_list.tail
    
    def get_node(self, temp: temp.Temp) -> graph.Node:
      requested_node: graph.Node = self.map_node_table.get(temp)
      if (requested_node is None):
          requested_node = self.new_node()
          self.map_node_table[temp] = requested_node
          self.rev_node_table[requested_node] = temp

      return requested_node

    def node_handler(self, node: graph.Node):
        def_temp_list: temp.TempList = self.flowgraph.deff(node)
        while(def_temp_list is not None):
            got_node: graph.Node  = self.get_node(def_temp_list.head)

            for live_out in self.out_node_table.get(node):
                current_live_out = self.get_node(live_out)
                self.add_edge(got_node, current_live_out)

            def_temp_list = def_temp_list.tail

  
    def move_handler(self, node: graph.Node):
        source_node: graph.Node  = self.get_node(self.flowgraph.use(node).head)
        destiny_node: graph.Node = self.get_node(self.flowgraph.deff(node).head)

        self.move_list = MoveList(source_node, destiny_node, self.move_list)
    
        for temp in self.out_node_table.get(node):
            got_node: graph.Node = self.get_node(temp)
            if (got_node is not source_node ):
                self.addEdge(destiny_node, got_node)


    def out(self, node: graph.Node) -> Set[temp.Temp]:
        temp_set = self.out_node_table.get(node)
        return temp_set


    def tnode(self, temp:temp.Temp) -> graph.Node:
        node: graph.Node = self.map_node_table.get(temp)
        if (node is None ):
            node = self.new_node()
            self.map_node_table[temp] = node
            self.rev_node_table[node] = temp
        
        return node

    def gtemp(self, node: graph.Node) -> temp.Temp:
        temp: temp.Temp = self.rev_node_table.get(node)
        return temp

    def moves(self) -> MoveList:
        return self.move_list

    def build_gen_and_kill(self):
        #TODO
        pass

    def build_in_and_out(self):
        node: graph.Node = None
        node_list: graph.NodeList = self.flowgraph.nodes()
        in_node_table_aux = {}
        out_node_table_aux = {}
        
        for node in node_list:
            self.in_node_table[node] = set()
            in_node_table_aux[node] = set()
            self.out_node_table[node] = set()
            out_node_table_aux[node] = set()

        cond = False
        while(not cond):
            for node in node_list:
                in_node_table_aux[node].update(self.in_node_table[node])
                out_node_table_aux[node].update(self.out_node_table[node])
                
                for succ_node in node.succ():
                    self.out_node_table[node].update(self.in_node_table[succ_node])
                
                diff: Set[temp.Temp] = self.out_node_table[node].difference(set(self.flowgraph.deff(node)))
                self.in_node_table[node].update(set(self.flowgraph.use(node)) | diff)
            
            # Verificar se in'[n] == in[n] e out'[n] == out[n] para todo n
            for node in node_list:
                if(self.in_node_table[node].difference(in_node_table_aux[node]) != None or
                   self.out_node_table[node].difference(out_node_table_aux[node]) != None):
                   cond = False
                   break

                cond = True

    def build_interference_graph(self):
        node_list: graph.NodeList = self.flowgraph.nodes()
        #interferenceGraph: graph.Graph = None
        
        # para cada nó de atribuição(a = ?), avaliar o tipo da instrução utilizada
        # se a intrução não for MOVE, considerar variaveis live-out
            # fazer a aresta da variavel do no para cada variavel live-out
        # se for MOVE(a = c), considerar variaveis live-out
            # fazer a aresta da variavel do no para cada variavel live-out diferente de c
        
        for node in node_list:
            deff_vars: temp.TempList = self.flowgraph.deff(node)
            
            if deff_vars != None:
                vars_out: temp.Temp = None
                for vars_out in self.out_node_table[node]:
                    self.add_ndge(node, self.get_node(vars_out))
                    #interferenceGraph.add_edge(node, self.get_node(vars_out))

        #return interferenceGraph

class Edge():

    edges_table = {}

    def __init__(self):
        super.__init__()
    
    def get_edge(self, origin_node: graph.Node, destiny_node: graph.Node) -> Edge:
        
        origin_table = Edge.edges_table.get(origin_node)
        destiny_table = Edge.edges_table.get(destiny_node)
        
        if (origin_table is None):
            origin_table = {}
            Edge.edges_table[origin_node] = origin_table

        if (destiny_table is None):
            destiny_table = {}
            Edge.edges_table[destiny_node] = destiny_table
        
        requested_edge: Edge  = origin_table.get(destiny_node)

        if(requested_edge is None):
            requested_edge = Edge()
            origin_table[destiny_node] = requested_edge
            destiny_table[origin_node] = requested_edge

        return requested_edge



class MoveList():

   def __init__(self, s: graph.Node, d: graph.Node, t: MoveList):
      self.src: graph.Node = s
      self.dst: graph.Node = d
      self.tail: MoveList = t
