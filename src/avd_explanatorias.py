# Análise Explanatória
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

# --- NOVIDADE: Importando geopandas ---
import geopandas as gpd

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

def viz10_3_vulnerabilidade_hubs_barras():
    aeroportos_raw = ler_csv(os.path.join(DATA, "aeroportos_data.csv"))
    ego_raw        = ler_csv(os.path.join(OUT,  "ego_aeroportos.csv"))
    regiao_map     = {r["iata"]: r["regiao"] for r in aeroportos_raw}

    # Pegamos os 7 aeroportos mais conectados para análise limpa
    ego_sorted = sorted(ego_raw, key=lambda r: -int(r["grau"]))
    selecionados = [r for r in ego_sorted[:7]]
    
    # Inverter a lista para que o maior valor fique no topo do gráfico de barras horizontais
    selecionados.reverse()

    aeroportos = [r["aeroporto"] for r in selecionados]
    cores_barras = [COR_REGIAO.get(regiao_map.get(a, ""), "#888") for a in aeroportos]

    # Extração dos 4 parâmetros
    val_grau      = [int(r["grau"]) for r in selecionados]
    val_ordem     = [int(r["ordem_ego"]) for r in selecionados]
    val_tamanho   = [int(r["tamanho_ego"]) for r in selecionados]
    val_densidade = [float(r["densidade_ego"]) for r in selecionados]

    # Criação de um painel 2x2 (4 mini-gráficos)
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    fig.patch.set_facecolor("#F8F9FA")
    
    # Lista para iterar e construir os 4 gráficos magicamente
    metricas = [
        (val_grau, "Grau\n(Total de Conexões)", axs[0, 0]),
        (val_ordem, "Ordem da Ego-Rede\n(Nº de Vizinhos)", axs[0, 1]),
        (val_tamanho, "Tamanho da Ego-Rede\n(Conexões entre Vizinhos)", axs[1, 0]),
        (val_densidade, "Densidade da Ego-Rede\n(Nível de Coesão %)", axs[1, 1])
    ]

    for valores, titulo, ax in metricas:
        ax.set_facecolor("#FFFFFF")
        # Desenha as barras
        barras = ax.barh(aeroportos, valores, color=cores_barras, edgecolor="white", height=0.7)
        
        # Adiciona o número no final de cada barra para facilitar a leitura
        for barra in barras:
            largura = barra.get_width()
            formato = f"{largura:.2f}" if isinstance(largura, float) and largura < 2 else f"{int(largura)}"
            ax.text(
                largura + (max(valores) * 0.02), # Distância do texto pra barra
                barra.get_y() + barra.get_height() / 2,
                formato,
                va='center', ha='left', fontsize=9, fontweight='bold', color="#444"
            )

        # Estilização limpa
        ax.set_title(titulo, fontsize=11, fontweight="bold", color="#222", pad=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_color("#DDD")
        ax.tick_params(axis='x', bottom=False, labelbottom=False) # Esconde eixo X (já temos os números nas barras)
        ax.tick_params(axis='y', labelsize=10)

    # Legenda Global de Regiões
    legend_items = [mpatches.Patch(color=c, label=r) for r, c in COR_REGIAO.items()]
    fig.legend(handles=legend_items, title="Região", loc='upper center', 
               bbox_to_anchor=(0.5, 1.05), ncol=5, frameon=False, fontsize=10)

    fig.suptitle(
        "Perfil Multidimensional dos Hubs Principais",
        fontsize=16, fontweight="bold", y=1.12, color="#1A1A2E"
    )

    nota = "Mensagem: Gráficos de barras revelam instantaneamente a assimetria da rede. BSB domina conexões absolutas (Grau/Tamanho),\nmas aeroportos menores podem ter densidades diferentes dependendo de seus clusters."
    fig.text(0.5, -0.05, nota, ha="center", fontsize=9.5, color="#444", style="italic")

    plt.tight_layout()
    path = os.path.join(OUT, "viz10_3_vulnerabilidade_barras.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] {path}")
# Mapa Geográfico de Conectividade 
def viz10_4_mapa_conectividade():
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

    import warnings
    warnings.filterwarnings("ignore") 
    
    try:
        
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        world = gpd.read_file(url)
        
       
        brasil = world[(world["ADMIN"] == "Brazil") | (world["NAME"] == "Brazil")]
        brasil.plot(ax=ax, color="#ECF0F1", edgecolor="#BDC3C7", linewidth=0.8, zorder=0)
    except Exception as e:
        print(f"Aviso: Não foi possível carregar o mapa do Geopandas. Erro: {e}")
    
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
    viz10_3_vulnerabilidade_hubs_barras()
    viz10_4_mapa_conectividade()
    print("\nArquivos salvos em out/")
    print("viz10_3_vulnerabilidade_hubs.png")
    print("viz10_4_mapa_conectividade.png")

if __name__ == "__main__":
    main()