# PARTE 7: Árvore de Caminho: Recife → Porto Alegre e Manaus → São Paulo
import os
import sys
import csv
import heapq

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
        num_arestas = sum(len(v) for v in self.adj_list.values()) // 2
        return f"Grafo(nós={len(self.nodes)}, arestas={num_arestas})"


def ler_aeroportos(caminho_arquivo):
    grafo = Grafo()
    with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
        leitor_csv = csv.DictReader(f)
        for linha in leitor_csv:
            iata = linha.get('iata', '').strip()
            cidade = linha.get('cidade', '').strip()
            regiao = linha.get('regiao', '').strip()
            if iata:
                grafo.adicionar_no(iata, cidade=cidade, regiao=regiao)
    return grafo


def ler_adjacencias(grafo, caminho_arquivo):
    colunas_obrigatorias = {"origem", "destino", "tipo_conexao", "justificativa", "peso"}

    with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
        leitor_csv = csv.DictReader(f)

        if leitor_csv.fieldnames is None:
            raise ValueError("O arquivo de adjacências está vazio.")

        colunas_faltando = colunas_obrigatorias - set(leitor_csv.fieldnames)
        if colunas_faltando:
            raise ValueError(
                "Colunas obrigatórias ausentes em adjacencias_aeroportos.csv: "
                + ", ".join(sorted(colunas_faltando))
            )

        for numero_linha, linha in enumerate(leitor_csv, start=2):
            origem = linha.get('origem', '').strip().upper()
            destino = linha.get('destino', '').strip().upper()
            tipo_conexao = linha.get('tipo_conexao', '').strip()
            justificativa = linha.get('justificativa', '').strip()
            peso_texto = linha.get('peso', '').strip()

            if not origem:
                raise ValueError(f"Linha {numero_linha}: origem vazia.")
            if not destino:
                raise ValueError(f"Linha {numero_linha}: destino vazio.")
            if not tipo_conexao:
                raise ValueError(f"Linha {numero_linha}: tipo_conexao vazio.")
            if not justificativa:
                raise ValueError(f"Linha {numero_linha}: justificativa vazia.")
            if not peso_texto:
                raise ValueError(f"Linha {numero_linha}: peso vazio.")

            try:
                peso = float(peso_texto)
            except ValueError:
                raise ValueError(f"Linha {numero_linha}: peso inválido: {peso_texto}")

            if peso < 0:
                raise ValueError(f"Linha {numero_linha}: peso negativo não é permitido.")

            grafo.adicionar_aresta(
                origem=origem,
                destino=destino,
                peso=peso,
                tipo_conexao=tipo_conexao,
                justificativa=justificativa
            )



def dijkstra(grafo, origem):
    distancias = {no: float('inf') for no in grafo.get_nos()}
    predecessores = {no: None for no in grafo.get_nos()}
    distancias[origem] = 0.0
    heap = [(0.0, origem)]
    visitados = set()
    while heap:
        custo_atual, no_atual = heapq.heappop(heap)
        if no_atual in visitados:
            continue
        visitados.add(no_atual)
        for aresta in grafo.adj_list.get(no_atual, []):
            vizinho = aresta['vizinho']
            novo_custo = custo_atual + aresta['peso']
            if novo_custo < distancias[vizinho]:
                distancias[vizinho] = novo_custo
                predecessores[vizinho] = no_atual
                heapq.heappush(heap, (novo_custo, vizinho))
    return distancias, predecessores


def reconstruir_caminho(predecessores, origem, destino):
    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = predecessores[atual]
    caminho.reverse()
    return caminho if caminho and caminho[0] == origem else None


def caminho_para_arestas(caminho):

    return [(caminho[i], caminho[i + 1]) for i in range(len(caminho) - 1)]



def ler_metadados(caminho_nos):
    meta = {}
    with open(caminho_nos, encoding='utf-8') as f:
        for linha in csv.DictReader(f):
            meta[linha['iata']] = {
                'cidade': linha['cidade'],
                'regiao': linha['regiao']
            }
    return meta



def gerar_html(caminhos_info, grafo, meta, caminho_saida):
    from pyvis.network import Network

    ROTAS = [
        {"label": "Recife → Porto Alegre", "cor_no": "#e74c3c", "cor_aresta": "#e74c3c"},
        {"label": "Manaus → São Paulo",    "cor_no": "#2980b9", "cor_aresta": "#2980b9"},
    ]
    COR_COMPARTILHADO = "#8e44ad"
    COR_FUNDO_NO      = "#ecf0f1"
    COR_ARESTA_FUNDO  = "#bdc3c7"

    net = Network(
        height="700px", width="100%",
        bgcolor="#1a1a2e", font_color="white",
        heading=""
    )
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
          "gravitationalConstant": -80,
          "springLength": 120,
          "springConstant": 0.08
        },
        "stabilization": { "iterations": 200 }
      },
      "edges": {
        "smooth": { "type": "continuous" }
      }
    }
    """)

    nos_por_rota     = [set(info['caminho']) for info in caminhos_info]
    arestas_por_rota = [set(map(tuple, info['arestas'])) for info in caminhos_info]

    todos_nos = set(grafo.get_nos())

    def cor_no(no):
        em = [i for i, s in enumerate(nos_por_rota) if no in s]
        if len(em) >= 2: return COR_COMPARTILHADO
        if len(em) == 1: return ROTAS[em[0]]["cor_no"]
        return COR_FUNDO_NO

    def cor_aresta(u, v):
        par  = (u, v)
        par2 = (v, u)
        em = [i for i, s in enumerate(arestas_por_rota) if par in s or par2 in s]
        if len(em) >= 2: return COR_COMPARTILHADO
        if len(em) == 1: return ROTAS[em[0]]["cor_aresta"]
        return COR_ARESTA_FUNDO

    for no in todos_nos:
        cidade = meta.get(no, {}).get('cidade', no)
        regiao = meta.get(no, {}).get('regiao', '')
        c = cor_no(no)
        em_rota = c != COR_FUNDO_NO
        net.add_node(
            no,
            label=f"{no}\n{cidade}",
            title=f"<b>{no}</b> — {cidade}<br>Região: {regiao}",
            color=c,
            size=28 if em_rota else 18,
            font={"size": 14 if em_rota else 11, "color": "white"},
            borderWidth=3 if em_rota else 1,
            shape="dot"
        )

    arestas_adicionadas = set()
    for origem_no in todos_nos:
        for aresta in grafo.adj_list.get(origem_no, []):
            destino_no = aresta['vizinho']
            chave = tuple(sorted([origem_no, destino_no]))
            if chave in arestas_adicionadas:
                continue
            arestas_adicionadas.add(chave)

            c = cor_aresta(origem_no, destino_no)
            em_rota = c != COR_ARESTA_FUNDO
            net.add_edge(
                origem_no, destino_no,
                color=c,
                width=4 if em_rota else 1,
                title=f"Peso: {aresta['peso']} | {aresta['tipo_conexao']}",
                label=str(int(aresta['peso'])) if em_rota else "",
                font={"size": 12, "color": "#f1c40f", "strokeWidth": 3, "strokeColor": "#1a1a2e"}
            )

    html_titulo = """
    <div style="position:fixed;top:10px;left:50%;transform:translateX(-50%);
                background:#16213e;color:white;padding:10px 24px;border-radius:8px;
                font-family:Arial;font-size:15px;font-weight:bold;z-index:9999;
                border:1px solid #444;">
        Árvores de Percurso — Dijkstra
        <span style='margin-left:24px;font-size:12px;font-weight:normal;color:#aaa'>
          <span style='color:#e74c3c'>●</span> REC→POA &nbsp;
          <span style='color:#2980b9'>●</span> MAO→GRU &nbsp;
          <span style='color:#8e44ad'>●</span> Compartilhado
        </span>
    </div>
    """

    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    net.save_graph(str(caminho_saida))

    with open(caminho_saida, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    conteudo = conteudo.replace('<body>', f'<body>{html_titulo}', 1)
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    print(f"HTML salvo em: {caminho_saida}")



def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo_nos     = os.path.join(base_dir, "data", "aeroportos_data.csv")
    arquivo_arestas = os.path.join(base_dir, "data", "adjacencias_aeroportos.csv")
    out_dir         = os.path.join(base_dir, "out")

    print("Carregando grafo...")
    grafo = ler_aeroportos(arquivo_nos)
    ler_adjacencias(grafo, arquivo_arestas)
    print(grafo)

    meta = ler_metadados(arquivo_nos)

    PARES = [("REC", "POA"), ("MAO", "GRU")]

    print("\nCalculando caminhos mínimos com Dijkstra...")
    caminhos_info = []
    for origem, destino in PARES:
        distancias, predecessores = dijkstra(grafo, origem)
        caminho = reconstruir_caminho(predecessores, origem, destino)
        custo   = round(distancias[destino], 2)
        arestas = caminho_para_arestas(caminho)
        print(f"  {origem} → {destino}: custo={custo}  caminho={' -> '.join(caminho)}")
        caminhos_info.append({"caminho": caminho, "arestas": arestas, "custo": custo})

    print("\nGerando visualização...")
    gerar_html(
        caminhos_info, grafo, meta,
        os.path.join(out_dir, "arvore_percurso.html")
    )
    print("\nConcluído")


if __name__ == "__main__":
    main()