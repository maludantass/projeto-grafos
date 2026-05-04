"""
Parte 3 - Métricas Globais e por Grupo
"""
import os
import sys
import json
import csv

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_aeroportos, ler_adjacencias
from pathlib import Path


def calcular_densidade(num_nos, num_arestas):
    if num_nos < 2:
        return 0.0
    return (2 * num_arestas) / (num_nos * (num_nos - 1))


def metricas_subgrafo(grafo, nos_subset):
    nos_set = set(nos_subset)
    ordem = len(nos_set)
    arestas = 0
    for no in nos_set:
        for aresta in grafo.adj_list.get(no, []):
            if aresta['vizinho'] in nos_set:
                arestas += 1
    tamanho = arestas // 2
    densidade = calcular_densidade(ordem, tamanho)
    return ordem, tamanho, round(densidade, 6)


def grau_no(grafo, no):
    return len(grafo.adj_list.get(no, []))


def ego_network(grafo, no):
    vizinhos = [a['vizinho'] for a in grafo.adj_list.get(no, [])]
    return list(set([no] + vizinhos))


def calcular_metricas_globais(grafo):
    nos = grafo.get_nos()
    ordem = len(nos)
    tamanho = sum(len(v) for v in grafo.adj_list.values()) // 2
    densidade = calcular_densidade(ordem, tamanho)
    return {
        "ordem": ordem,
        "tamanho": tamanho,
        "densidade": round(densidade, 6)
    }


def calcular_metricas_regioes(grafo):
    regioes = {}
    for no in grafo.get_nos():
        attrs = grafo.get_atributos_no(no)
        regiao = attrs.get('regiao', 'Desconhecida') if attrs else 'Desconhecida'
        regioes.setdefault(regiao, []).append(no)

    resultado = []
    for regiao, nos in sorted(regioes.items()):
        ordem, tamanho, densidade = metricas_subgrafo(grafo, nos)
        resultado.append({
            "regiao": regiao,
            "nos": sorted(nos),
            "ordem": ordem,
            "tamanho": tamanho,
            "densidade": densidade
        })
    return resultado


def calcular_ego_aeroportos(grafo):
    resultado = []
    for no in sorted(grafo.get_nos()):
        grau = grau_no(grafo, no)
        nos_ego = ego_network(grafo, no)
        ordem_ego, tamanho_ego, densidade_ego = metricas_subgrafo(grafo, nos_ego)
        resultado.append({
            "aeroporto": no,
            "grau": grau,
            "ordem_ego": ordem_ego,
            "tamanho_ego": tamanho_ego,
            "densidade_ego": densidade_ego
        })
    return resultado

def calcular_grau_aeroporto(grafo, aeroporto):
    vizinhos = grafo.get_vizinhos(aeroporto)
    return len(vizinhos)

def calcular_graus(grafo):
    graus = {}

    for aeroporto in grafo.get_nos():
        graus[aeroporto] = calcular_grau_aeroporto(grafo, aeroporto)

    return graus

def salvar_graus_csv(graus, caminho_saida="out/graus.csv"):
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho_saida, mode="w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["aeroporto", "grau"])

        for aeroporto, grau in sorted(graus.items()):
            escritor.writerow([aeroporto, grau])

def encontrar_aeroporto_mais_conectado(graus):
    if not graus:
        return {
            "aeroporto": None,
            "grau": 0
        }

    aeroporto, grau = max(graus.items(), key=lambda item: item[1])

    return {
        "aeroporto": aeroporto,
        "grau": grau
    }


def encontrar_maior_densidade_local(caminho_ego="out/ego_aeroportos.csv"):
    caminho_ego = Path(caminho_ego)

    if not caminho_ego.exists():
        raise FileNotFoundError(
            f"Arquivo {caminho_ego} não encontrado. "
            "Gere primeiro as métricas de ego-network da Parte 3."
        )

    melhor_aeroporto = None
    maior_densidade = -1.0

    with open(caminho_ego, mode="r", newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            aeroporto = linha["aeroporto"]
            densidade_ego = float(linha["densidade_ego"])

            if densidade_ego > maior_densidade:
                maior_densidade = densidade_ego
                melhor_aeroporto = aeroporto

    return {
        "aeroporto": melhor_aeroporto,
        "densidade_ego": maior_densidade
    }


def salvar_rankings_json(
    aeroporto_mais_conectado,
    aeroporto_maior_densidade_local,
    caminho_saida="out/rankings.json"
):
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    dados = {
        "aeroporto_mais_conectado": aeroporto_mais_conectado,
        "aeroporto_maior_densidade_local": aeroporto_maior_densidade_local
    }

    with open(caminho_saida, mode="w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


def calcular_resumo_pesos(grafo):
    """
    Calcula um resumo da distribuição dos pesos das arestas.

    Como o grafo é não direcionado e cada aresta é armazenada nos dois sentidos,
    a função usa um conjunto para contar cada par apenas uma vez.
    """
    distribuicao = {}
    arestas_vistas = set()

    for origem in grafo.get_nos():
        for aresta in grafo.adj_list.get(origem, []):
            destino = aresta["vizinho"]
            peso = float(aresta["peso"])

            chave_aresta = tuple(sorted([origem, destino]))

            if chave_aresta in arestas_vistas:
                continue

            arestas_vistas.add(chave_aresta)
            distribuicao[peso] = distribuicao.get(peso, 0) + 1

    return {
        "regua_pesos": {
            "1.0": "Conexão regional intrarregional",
            "2.0": "Conexão inter-regional curta/média ou entre hubs próximos",
            "3.0": "Conexão inter-regional longa ou entre regiões distantes"
        },
        "distribuicao": {
            str(peso): quantidade
            for peso, quantidade in sorted(distribuicao.items())
        }
    }


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo_nos = os.path.join(base_dir, "data", "aeroportos_data.csv")
    arquivo_arestas = os.path.join(base_dir, "data", "adjacencias_aeroportos.csv")
    out_dir = os.path.join(base_dir, "out")

    os.makedirs(out_dir, exist_ok=True)

    print("Carregando grafo...")
    grafo = ler_aeroportos(arquivo_nos)
    ler_adjacencias(grafo, arquivo_arestas)
    print(grafo)

    print("\nCalculando métricas...")

    global_m = calcular_metricas_globais(grafo)
    regioes_m = calcular_metricas_regioes(grafo)
    ego_m = calcular_ego_aeroportos(grafo)

    graus = calcular_graus(grafo)
    aeroporto_mais_conectado = encontrar_aeroporto_mais_conectado(graus)

    resumo_pesos = calcular_resumo_pesos(grafo)

    print("\n" + "=" * 60)
    print("PARTE 3 — MÉTRICAS GLOBAIS E POR GRUPO")
    print("=" * 60)

    print("\n[1] Grafo Completo")
    print(f"    Ordem    : {global_m['ordem']} nós")
    print(f"    Tamanho  : {global_m['tamanho']} arestas")
    print(f"    Densidade: {global_m['densidade']:.6f}")

    print("\n[2] Subgrafos por Região")
    print(f"  {'Região':<15} {'Ordem':>6} {'Tamanho':>8} {'Densidade':>10}")
    print(f"  {'-' * 15} {'-' * 6} {'-' * 8} {'-' * 10}")

    for r in regioes_m:
        print(f"  {r['regiao']:<15} {r['ordem']:>6} {r['tamanho']:>8} {r['densidade']:>10.6f}")

    print("\n[3] Ego-Subrede por Aeroporto")
    print(f"  {'Aeroporto':<12} {'Grau':>5} {'Ord.Ego':>8} {'Tam.Ego':>8} {'Dens.Ego':>10}")
    print(f"  {'-' * 12} {'-' * 5} {'-' * 8} {'-' * 8} {'-' * 10}")

    for e in ego_m:
        print(
            f"  {e['aeroporto']:<12} "
            f"{e['grau']:>5} "
            f"{e['ordem_ego']:>8} "
            f"{e['tamanho_ego']:>8} "
            f"{e['densidade_ego']:>10.6f}"
        )

    print("\n" + "=" * 60)
    print("PARTE 4 — GRAUS E RANKINGS")
    print("=" * 60)
    print(
        f"Aeroporto mais conectado: "
        f"{aeroporto_mais_conectado['aeroporto']} "
        f"(grau {aeroporto_mais_conectado['grau']})"
    )

    print("\n" + "=" * 60)
    print("PARTE 5 — PESOS DAS ARESTAS")
    print("=" * 60)

    for peso, quantidade in resumo_pesos["distribuicao"].items():
        descricao = resumo_pesos["regua_pesos"].get(peso, "Sem descrição")
        print(f"Peso {peso}: {quantidade} arestas — {descricao}")

    print("\nSalvando arquivos...")

    with open(os.path.join(out_dir, "global.json"), mode="w", encoding="utf-8") as f:
        json.dump(global_m, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "regioes.json"), mode="w", encoding="utf-8") as f:
        json.dump(regioes_m, f, ensure_ascii=False, indent=2)

    campos = ["aeroporto", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"]

    with open(os.path.join(out_dir, "ego_aeroportos.csv"), mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(ego_m)

    salvar_graus_csv(graus, os.path.join(out_dir, "graus.csv"))

    aeroporto_maior_densidade_local = encontrar_maior_densidade_local(
        os.path.join(out_dir, "ego_aeroportos.csv")
    )

    salvar_rankings_json(
        aeroporto_mais_conectado,
        aeroporto_maior_densidade_local,
        os.path.join(out_dir, "rankings.json")
    )

    with open(os.path.join(out_dir, "pesos_arestas.json"), mode="w", encoding="utf-8") as f:
        json.dump(resumo_pesos, f, ensure_ascii=False, indent=2)

    print("Concluído! Arquivos salvos em out/")

    print(
        f"Aeroporto mais conectado: "
        f"{aeroporto_mais_conectado['aeroporto']} "
        f"(grau {aeroporto_mais_conectado['grau']})"
    )

    print(
        f"Aeroporto com maior densidade local: "
        f"{aeroporto_maior_densidade_local['aeroporto']} "
        f"(densidade {aeroporto_maior_densidade_local['densidade_ego']:.6f})"
    )

    print("Resumo dos pesos salvo em out/pesos_arestas.json")


if __name__ == "__main__":
    main()