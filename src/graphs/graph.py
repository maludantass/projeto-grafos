class Grafo:

    def __init__(self):
        self.adj_list = {}
        self.nodes = {}

    def adicionar_no(self, rotulo, **kwargs):
        if rotulo not in self.adj_list:
            self.adj_list[rotulo] = []
            self.nodes[rotulo] = kwargs

    def adicionar_aresta(self, origem, destino, peso=1.0, tipo_conexao='', justificativa=''):

        if origem not in self.adj_list:
            self.adicionar_no(origem)
        if destino not in self.adj_list:
            self.adicionar_no(destino)
        
        self.adj_list[origem].append({
            'vizinho': destino, 
            'peso': float(peso), 
            'tipo_conexao': tipo_conexao, 
            'justificativa': justificativa
        })
        self.adj_list[destino].append({
            'vizinho': origem, 
            'peso': float(peso), 
            'tipo_conexao': tipo_conexao, 
            'justificativa': justificativa
        })

    def get_nos(self):
        return list(self.adj_list.keys())

    def get_atributos_no(self, rotulo):
        return self.nodes.get(rotulo)
    
    def get_vizinhos(self, no):
        if no not in self.adj_list:
            return []

        return [aresta["vizinho"] for aresta in self.adj_list[no]]

    def get_arestas(self, no):
        return self.adj_list.get(no, [])

    def __str__(self):
        # grafo é não direcionado
        num_arestas = sum(len(v) for v in self.adj_list.values()) // 2
        return f"Grafo(nós={len(self.nodes)}, arestas={num_arestas})"
