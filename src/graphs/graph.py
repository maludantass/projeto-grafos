class Grafo:
    """
    RÉGUA DE PESOS UTILIZADA:
    Peso 1.0 (Conexão Regional): Voos intrarregionais (dentro da mesma região). São mais curtos e com menor custo.
    Peso 2.0 (Conexão Inter-regional Curta/Média): Voos conectando Hubs de regiões próximas (ex: Sudeste-Sul, Sudeste-Centro-Oeste, Nordeste-Norte).
    Peso 3.0 (Conexão Inter-regional Longa): Voos conectando Hubs de regiões mais distantes (ex: Sudeste-Nordeste, Centro-Oeste-Norte).
    """
    def __init__(self):
        self.adj_list = {}
        self.nodes = {}

    def adicionar_no(self, rotulo, **kwargs):
        if rotulo not in self.adj_list:
            self.adj_list[rotulo] = []
            self.nodes[rotulo] = kwargs

    def adicionar_aresta(self, origem, destino, peso=1.0, tipo_conexao='', justificativa=''):
        """
        origem: Rótulo do nó de origem.
        destino: Rótulo do nó de destino.
        peso: Peso da aresta.
        tipo_conexao: Tipo da conexão (ex: regional, hub).
        justificativa: Justificativa para a existência da aresta.
        """
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
