# ==========================================================
# SISTEMA DE DENGUE OURINHOS - V3
#
# Funcionalidades:
# ✅ Histórico
# ✅ Pontos
# ✅ Heatmap suave
# ✅ Comparação Ano A x Ano B
# ✅ Evolução Temporal
# ✅ Predição 2026
# ✅ Limite Municipal (GeoJSON)
# ✅ Encerrar Sistema
# ✅ Tratamento de dados vazios
# ==========================================================

# ----------------------------------------------------------
# IMPORTAÇÕES
# ----------------------------------------------------------

import os
import json
import time
import signal

import pandas as pd
import pydeck as pdk
import streamlit as st
from auth import login

# ----------------------------------------------------------
# CONFIGURAÇÃO
# ----------------------------------------------------------

st.set_page_config(
    page_title="Dengue Ourinhos",
    page_icon="🦟",
    layout="wide"
)
# ----------------------------------------------------------
# CONTROLE DE LOGIN
# ----------------------------------------------------------

if "logado" not in st.session_state:

    st.session_state["logado"] = False

if not st.session_state["logado"]:

    login()

    st.stop()

# ----------------------------------------------------------
# DADOS
# ----------------------------------------------------------

@st.cache_data
def carregar_historico():
    """
    Carrega a base histórica.
    """

    df = pd.read_csv(
        "dados/dataset_geo.csv"
    )

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    return df


@st.cache_data
def carregar_predicao():
    """
    Carrega a predição para 2026.
    """

    df = pd.read_csv(
        "dados/mapa_predicao_2026.csv"
    )

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    return df


@st.cache_data
def carregar_geojson():
    """
    Carrega limite municipal.
    """

    with open(
        "ourinhos.geojson",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ----------------------------------------------------------
# LEITURA
# ----------------------------------------------------------

historico = carregar_historico()
predicao = carregar_predicao()
geojson = carregar_geojson()

# ----------------------------------------------------------
# TÍTULO
# ----------------------------------------------------------

st.title(
    "🦟 Sistema de Monitoramento da Dengue - Ourinhos"
)

st.caption(
    "Histórico 2015-2025 e Predição 2026"
)

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------

st.sidebar.title(
    "Painel"
)

modo = st.sidebar.radio(

    "Modo",

    [
        "Histórico",
        "Comparação",
        "Evolução Temporal",
        "Predição 2026"
    ]

)

# ----------------------------------------------------------
# ENCERRA SERVIDOR
# ----------------------------------------------------------

if st.sidebar.button(
    "Logout"
):

    st.session_state["logado"] = False

    st.rerun()

# ==========================================================
# FUNÇÃO MAPA
# ==========================================================

def desenhar_mapa(
    dados,
    camada,
    tooltip
):
    """
    Renderiza mapa padrão.
    """

    if len(dados) == 0:

        st.warning(
            "Nenhum registro encontrado para os filtros selecionados."
        )

        return

    limite = pdk.Layer(

        "GeoJsonLayer",

        data=geojson,

        stroked=True,

        filled=False,

        line_width_min_pixels=1,

        get_line_color=[120, 120, 120]

    )

    deck = pdk.Deck(

        map_style="light",

        layers=[
            limite,
            camada
        ],

        initial_view_state=pdk.ViewState(

            latitude=float(
                dados["latitude"].mean()
            ),

            longitude=float(
                dados["longitude"].mean()
            ),

            zoom=12

        ),

        tooltip=tooltip

    )

    st.pydeck_chart(
    deck,
    use_container_width=True,
    height=720)

# ==========================================================
# HISTÓRICO
# ==========================================================

if modo == "Histórico":

    anos = sorted(
        historico["ano"].unique()
    )

    ano = st.sidebar.selectbox(
        "Ano",
        anos
    )

    visualizacao = st.sidebar.radio(

        "Visualização",

        [
            "Pontos",
            "Heatmap"
        ]

    )

    ceps = sorted(
        historico["cep"]
        .astype(str)
        .unique()
    )

    cep = st.sidebar.selectbox(

        "CEP",

        ["TODOS"] + list(ceps)

    )

    # ------------------------------------------------------
    # FILTRO
    # ------------------------------------------------------

    dados = historico[
        historico["ano"] == ano
    ].copy()

    if cep != "TODOS":

        dados = dados[
            dados["cep"].astype(str)
            == cep
        ]

    # ------------------------------------------------------
    # MÉTRICAS
    # ------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "📍 Ocorrências",
        len(dados)
    )

    c2.metric(
        "📮 CEPs",
        dados["cep"].nunique()
    )

    c3.metric(
        "📅 Ano",
        ano
    )

    # ------------------------------------------------------
    # PONTOS
    # ------------------------------------------------------

    if visualizacao == "Pontos":

        camada = pdk.Layer(

            "ScatterplotLayer",

            data=dados,

            get_position='[longitude, latitude]',

            get_radius=8,

            get_fill_color=[40, 110, 255],

            opacity=0.45,

            pickable=True

        )

    # ------------------------------------------------------
    # HEATMAP
    # ------------------------------------------------------

    else:

        camada = pdk.Layer(

            "HeatmapLayer",

            data=dados,

            get_position='[longitude, latitude]',

            get_weight=1,

            radiusPixels=25,

            intensity=0.40,

            threshold=0.10

        )

    desenhar_mapa(

        dados,

        camada,

        {
            "text":
            "CEP: {cep}\nBairro: {bairro}"
        }

    )

# ==========================================================
# COMPARAÇÃO
# ==========================================================

elif modo == "Comparação":

    anos = sorted(
        historico["ano"].unique()
    )

    ano_a = st.sidebar.selectbox(
        "Ano A",
        anos,
        index=max(0, len(anos)-2)
    )

    ano_b = st.sidebar.selectbox(
        "Ano B",
        anos,
        index=max(0, len(anos)-1)
    )

    dados_a = historico[
        historico["ano"] == ano_a
    ]

    dados_b = historico[
        historico["ano"] == ano_b
    ]

    col_a, col_b = st.columns(2)

    with col_a:

        st.subheader(
            f"Ano {ano_a}"
        )

        camada_a = pdk.Layer(

            "HeatmapLayer",

            data=dados_a,

            get_position='[longitude, latitude]',

            radiusPixels=25,

            intensity=0.40,

            threshold=0.10

        )

        desenhar_mapa(

            dados_a,

            camada_a,

            {
                "text":
                f"{ano_a}"
            }

        )

    with col_b:

        st.subheader(
            f"Ano {ano_b}"
        )

        camada_b = pdk.Layer(

            "HeatmapLayer",

            data=dados_b,

            get_position='[longitude, latitude]',

            radiusPixels=25,

            intensity=0.40,

            threshold=0.10

        )

        desenhar_mapa(

            dados_b,

            camada_b,

            {
                "text":
                f"{ano_b}"
            }

        )

# ==========================================================
# EVOLUÇÃO TEMPORAL
# ==========================================================

elif modo == "Evolução Temporal":

    years = sorted(
        historico["ano"].unique()
    )
    velocidade = st.sidebar.selectbox(

    "Velocidade",

    [
        0.2,
        0.5,
        1.0,
        2.0
    ],

    index=1

    )

    if st.button(
        "▶ Reproduzir 2015-2025"
    ):

        placeholder = st.empty()

        for ano in years:

            dados = historico[
                historico["ano"] == ano
            ]

            camada = pdk.Layer(

                "HeatmapLayer",

                data=dados,

                get_position='[longitude, latitude]',

                radiusPixels=35,

                intensity=0.8,

                threshold=0.05

            )

            with placeholder.container():

                st.subheader(
                    f"Ano {ano}"
                )

                desenhar_mapa(

                    dados,

                    camada,

                    {
                        "text":
                        f"{ano}"
                    }

                )

            time.sleep(velocidade)

# ==========================================================
# PREDIÇÃO
# ==========================================================

else:

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "📮 CEPs previstos",
        len(predicao)
    )

    c2.metric(
        "🔥 Máx Previsto",
        round(
            predicao[
                "casos_previstos_2026"
            ].max(),
            1
        )
    )

    c3.metric(
        "📈 Média Prevista",
        round(
            predicao[
                "casos_previstos_2026"
            ].mean(),
            1
        )
    )

    camada = pdk.Layer(

        "HeatmapLayer",

        data=predicao,

        get_position='[longitude, latitude]',

        get_weight="casos_previstos_2026",

        radiusPixels=35,

        intensity=0.8,

        threshold=0.05

    )

    desenhar_mapa(

        predicao,

        camada,

        {
            "text":
            "CEP: {cep}\nPrevisto: {casos_previstos_2026}"
        }

    )
