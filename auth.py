# ==========================================================
# LOGIN
# ==========================================================

import pandas as pd
import streamlit as st

# ----------------------------------------------------------
# CARREGA USUÁRIOS
# ----------------------------------------------------------

@st.cache_data
def carregar_usuarios():

    return pd.read_csv(
        "usuarios.csv"
    )

# ----------------------------------------------------------
# TELA LOGIN
# ----------------------------------------------------------

def login():

    usuarios = carregar_usuarios()

    st.title("🔐 Login")

    usuario = st.text_input(
        "Usuário"
    )

    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        filtro = usuarios[

            (usuarios["usuario"] == usuario)

            &

            (usuarios["senha"] == senha)

        ]

        if len(filtro):

            st.session_state["logado"] = True

            st.session_state["usuario"] = usuario

            st.rerun()

        else:

            st.error(
                "Usuário ou senha inválidos."
            )
