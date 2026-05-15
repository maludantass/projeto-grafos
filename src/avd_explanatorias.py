#Análise Explanatória
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT  = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)

def ler_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

COR_REGIAO = {
    "Norte":        "#2196F3",
    "Nordeste":     "#FF9800",
    "Centro-Oeste": "#9C27B0",
    "Sudeste":      "#F44336",
    "Sul":          "#4CAF50",
}

COORDS = {
    "MAO": (-60.05, -3.04),  "BEL": (-48.48, -1.38),
    "PVH": (-63.90, -8.71),  "RBR": (-67.90, -9.87),
    "FOR": (-38.53,  -3.78), "REC": (-34.92, -8.13),
    "SSA": (-38.33, -12.91), "NAT": (-35.24, -5.91),
    "JPA": (-34.95,  -7.15), "THE": (-42.82, -5.06),
    "BSB": (-47.92, -15.87), "GYN": (-49.22, -16.63),
    "GRU": (-46.47, -23.43), "CGH": (-46.65, -23.63),
    "GIG": (-43.24, -22.81), "CNF": (-43.97, -19.63),
    "VIX": (-40.29, -20.26), "CWB": (-49.17, -25.52),
    "FLN": (-48.55, -27.67), "POA": (-51.17, -29.99),
}

# Radar (spider chart): perfil dos principais aeroportos 

def viz10_3_vulnerabilidade_hubs():
    #pq dessa escolha para avd
    #O que mostra: Radar chart (spider) com 4 métricas normalizadas para cada aeroporto: grau, densidade ego-rede, 
    # ordem ego e tamanho ego. Cada aeroporto é uma linha colorida sobre os eixos radiais. Seleciona os 7 aeroportos
    #  mais relevantes para manter a leitura limpa.

    #Insight: O radar torna imediatamente visível que BSB tem perfil dominante em todas as dimensões, enquanto aeroportos
    #  periféricos como RBR e POA tem área mínima comunicando de forma intuitiva a assimetria da rede.

    #Por que radar: Ideal para comparar múltiplas dimensões de poucos itens. A área de cada polígono representa o "poder"
    #  do aeroporto na rede quanto maior a área, mais central e insubstituível ele é.

    aeroportos_raw = ler_csv(os.path.join(DATA, "aeroportos_data.csv"))
    ego_raw        = ler_csv(os.path.join(OUT,  "ego_aeroportos.csv"))
    regiao_map     = {r["iata"]: r["regiao"] for r in aeroportos_raw}

    ego_sorted  = sorted(ego_raw, key=lambda r: -int(r["grau"]))
    top5        = [r["aeroporto"] for r in ego_sorted[:5]]
    perifericos = [r["aeroporto"] for r in ego_sorted
                   if int(r["grau"]) == 1
                   and regiao_map.get(r["aeroporto"]) not in
                       [regiao_map.get(a) for a in top5]][:2]
    selecionados = top5 + perifericos

    dados = {r["aeroporto"]: r for r in ego_raw}

    metricas   = ["Grau", "Densidade\nEgo-Rede", "Ordem\nEgo", "Tamanho\nEgo"]
    max_grau   = max(int(r["grau"])           for r in ego_raw)
    max_ordem  = max(int(r["ordem_ego"])      for r in ego_raw)
    max_tam    = max(int(r["tamanho_ego"])    for r in ego_raw)

    def normaliza(no):
        r = dados[no]
        return [
            int(r["grau"])           / max_grau,
            float(r["densidade_ego"]),         
            int(r["ordem_ego"])      / max_ordem,
            int(r["tamanho_ego"])    / max_tam,
        ]

    N      = len(metricas)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  

    fig, ax = plt.subplots(figsize=(9, 9),
                           subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F0F4F8")

    # grade de fundo
    ax.set_yticks([0.25, 0.50, 0.75, 1.00])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"],
                       fontsize=8, color="#999")
    ax.set_ylim(0, 1.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metricas, fontsize=11, fontweight="bold", color="#333")
    ax.spines["polar"].set_color("#DDD")
    ax.grid(color="#DDD", linewidth=0.8)

    CORES_RADAR = [
        "#9C27B0",  # BSB - Centro-Oeste
        "#F44336",  # GRU 
        "#FF9800",  # FOR  
        "#E91E63",  # GIG  
        "#2196F3",  # BEL  
        "#607D8B",  # periférico 1 
        "#795548",  # periférico 2
    ]

    for i, no in enumerate(selecionados):
        vals   = normaliza(no)
        vals  += vals[:1]
        cor    = CORES_RADAR[i % len(CORES_RADAR)]
        reg    = regiao_map.get(no, "")

        ax.plot(angles, vals, color=cor, linewidth=2.2, zorder=3)
        ax.fill(angles, vals, color=cor, alpha=0.12)

        idx_max = np.argmax(vals[:-1])
        ax.annotate(
            no,
            xy=(angles[idx_max], vals[idx_max]),
            xytext=(angles[idx_max], vals[idx_max] + 0.10),
            fontsize=9, fontweight="bold", color=cor, ha="center",
        )

    ax.set_title(
        "Perfil Multidimensional dos Aeroportos\n"
        "(área maior = aeroporto mais central na rede)",
        fontsize=13, fontweight="bold", pad=24, color="#222"
    )

    legend_items = [
        mpatches.Patch(color=CORES_RADAR[i],
                       label=f"{no}  [{regiao_map.get(no,'')}]")
        for i, no in enumerate(selecionados)
    ]
    ax.legend(handles=legend_items, loc="upper right",
              bbox_to_anchor=(1.35, 1.10),
              fontsize=9, title="Aeroporto [Região]",
              title_fontsize=9, framealpha=0.9)

    nota = (
        "Mensagem principal: BSB domina todas as 4 dimensões é o aeroporto mais central e crítico da rede.\n"
        "Aeroportos periféricos (ex: RBR, POA) têm área mínima: dependem completamente de hubs para se conectar."
    )
    fig.text(0.5, -0.02, nota, ha="center", fontsize=8.5,
             color="#333", style="italic")

    plt.tight_layout()
    path = os.path.join(OUT, "viz10_3_vulnerabilidade_hubs.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] {path}")

# Mapa Geográfico de Conectividade 

def viz10_4_mapa_conectividade():
    #pq dessa escolha para avd
    #O que mostra: Representação geográfica do grafo com aeroportos posicionados por coordenadas reais. 
    # Rótulos deslocados manualmente para evitar sobreposição nos clusters densos (Nordeste, Sudeste).

    #Insight: O mapa evidencia a concentração de rotas no eixo BSB-GRU-FOR e a escassez de conexões diretas na região Norte.

    #Por que mapa geográfico: Dados com coordenadas reais ganham sentido espacial imediato, o leitor já tem o mapa do Brasil
    #  como referência mental, o que elimina a necessidade de explicar a disposição dos nós. 
    # Nenhum outro tipo de gráfico consegue comunicar disparidade territorial de forma tão direta para alguém que não conhece o projeto.

    aeroportos_raw = ler_csv(os.path.join(DATA, "aeroportos_data.csv"))
    adj_raw        = ler_csv(os.path.join(DATA, "adjacencias_aeroportos.csv"))
    graus_raw      = ler_csv(os.path.join(OUT,  "graus.csv"))
    regiao_map     = {r["iata"]: r["regiao"] for r in aeroportos_raw}
    grau_map       = {r["aeroporto"]: int(r["grau"]) for r in graus_raw}

    LABEL_OFFSET = {
        "MAO": (-1.5,  0.8),
        "BEL": ( 0.5,  0.8),
        "PVH": (-1.5,  0.5),
        "RBR": (-1.8,  0.0),
        "FOR": ( 1.2,  0.5),
        "REC": ( 1.2,  0.0),
        "SSA": ( 1.2,  0.0),
        "NAT": ( 1.2,  0.8),
        "JPA": ( 1.2, -0.5),
        "THE": ( 0.2,  0.9),
        "BSB": (-1.8,  0.5),
        "GYN": (-2.0, -0.5),
        "GRU": (-0.5, -1.2),
        "CGH": ( 1.2, -0.5),
        "GIG": ( 1.2,  0.5),
        "CNF": ( 1.2,  0.5),
        "VIX": ( 1.2,  0.0),
        "CWB": (-2.0,  0.0),
        "FLN": (-2.0,  0.0),
        "POA": (-2.0,  0.0),
    }

    fig, ax = plt.subplots(figsize=(13, 11))
    fig.patch.set_facecolor("#E8F4F8")
    ax.set_facecolor("#D6EAF8")

    brasil_lon = [
        -34, -35, -37, -39, -40, -43, -44, -46, -48, -49, -52, -53,
        -58, -60, -63, -68, -73, -74, -73, -70, -65, -60, -55, -51,
        -50, -48, -45, -40, -38, -35, -34
    ]
    brasil_lat = [
        -8,  -5,  -3,  -2,  -2,  -3,  -2,  -1,   0,  -1,  -3,  -5,
        -5,  -3,  -5,  -8, -10, -14, -18, -20, -20, -22, -23, -28,
        -29, -28, -26, -24, -14,  -8,  -8
    ]
    ax.fill(brasil_lon, brasil_lat, color="#ECF0F1", alpha=0.5, zorder=0)
    ax.plot(brasil_lon, brasil_lat, color="#BDC3C7", linewidth=0.8, zorder=1)

    desenhadas = set()
    for row in adj_raw:
        o, d = row["origem"], row["destino"]
        chave = tuple(sorted([o, d]))
        if chave in desenhadas:
            continue
        desenhadas.add(chave)
        if o not in COORDS or d not in COORDS:
            continue

        xo, yo = COORDS[o]
        xd, yd = COORDS[d]
        r_o = regiao_map.get(o, "")
        r_d = regiao_map.get(d, "")
        inter = (r_o != r_d)

        cor_aresta = "#E53935" if inter else "#78909C"
        lw         = 2.2 if inter else 1.0
        ls         = "-" if inter else "--"
        alpha      = 0.85 if inter else 0.50

        ax.plot([xo, xd], [yo, yd],
                color=cor_aresta, linewidth=lw, linestyle=ls,
                alpha=alpha, zorder=3 if inter else 2)

        peso = row.get("peso", "")
        if inter and peso:
            mx = (xo + xd) / 2 + 0.3
            my = (yo + yd) / 2 + 0.3
            ax.text(mx, my, peso, ha="center", va="center",
                    fontsize=7.5, color="#B71C1C", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white",
                              ec="none", alpha=0.8))

    # nós
    for no, (x, y) in COORDS.items():
        reg  = regiao_map.get(no, "")
        cor  = COR_REGIAO.get(reg, "#888")
        g    = grau_map.get(no, 1)
        raio = 55 + g * 50

        ax.scatter(x, y, s=raio, color=cor, zorder=5,
                   edgecolors="white", linewidths=1.5)

    for no, (x, y) in COORDS.items():
        dx, dy = LABEL_OFFSET.get(no, (0.5, 0.5))
        tx, ty = x + dx, y + dy

        ax.plot([x, tx], [y, ty], color="#999", linewidth=0.6,
                zorder=4, alpha=0.7)

        ax.text(tx, ty, no,
                ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="#1A1A2E", zorder=7,
                bbox=dict(boxstyle="round,pad=0.15", fc="white",
                          ec="none", alpha=0.75))

    leg_lines = [
        mpatches.Patch(color="#E53935", label="Conexão inter-regional"),
        mpatches.Patch(color="#78909C", label="Conexão intrarregional"),
    ]
    patches_reg = [mpatches.Patch(color=c, label=r) for r, c in COR_REGIAO.items()]

    leg1 = ax.legend(handles=leg_lines, title="Tipo de conexão",
                     fontsize=9, title_fontsize=9,
                     loc="lower left", framealpha=0.95)
    ax.add_artist(leg1)
    ax.legend(handles=patches_reg, title="Região",
              fontsize=9, title_fontsize=9,
              loc="lower right", framealpha=0.95)

    ax.set_xlim(-76, -28)
    ax.set_ylim(-35,  9)
    ax.set_xlabel("Longitude", fontsize=10, color="#555")
    ax.set_ylabel("Latitude",  fontsize=10, color="#555")
    ax.set_title(
        "Mapa de Conectividade da Rede de Aeroportos do Brasil\n"
        "(tamanho do nó proporcional ao grau  |  vermelho = rota inter-regional)",
        fontsize=13, fontweight="bold", pad=14
    )
    ax.grid(linestyle="--", alpha=0.25, color="#aaa")
    ax.tick_params(colors="#777")

    nota = (
        "Mensagem principal: O eixo BSB-GRU-FOR concentra a maioria das rotas inter-regionais (vermelho).\n"
        "A região Norte tem poucas conexões e depende de BEL/MAO para acessar o restante do país."
    )
    fig.text(0.5, -0.02, nota, ha="center", fontsize=9,
             color="#333", style="italic")

    plt.tight_layout()
    path = os.path.join(OUT, "viz10_4_mapa_conectividade.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] {path}")


def main():
    print("Visualizações Explanatórias")
    viz10_3_vulnerabilidade_hubs()
    viz10_4_mapa_conectividade()
    print("\nArquivos salvos em out/")
    print("viz10_3_vulnerabilidade_hubs.png")
    print("viz10_4_mapa_conectividade.png")

if __name__ == "__main__":
    main()