import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.graph_objects as go
import json
import io
from modules import available, quoteTicker, infoTicker, sendQuestion

# Configuração da página Streamlit para layout largo
st.set_page_config(page_title="Análise de Ações", page_icon=":bar_chart:", layout="wide")

# Configuração de Autenticação de usuário
names = ["Giovanni G da Silva", "Priscila Colombo", "José Laercio da Silva"]
usernames = ["giovannigs", "ppriscila", "laercio"]

# Hashed passwords file
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(config['credentials'],
                                    config['cookie']['name'],
                                    config['cookie']['key'],
                                    config['cookie']['expiry_days'])

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Usuário/Senha estão incorretos")

if authentication_status == None:
    st.warning("Por favor insira o usuário e senha")

if authentication_status:

    # Carregando e normalizando dados de ações a partir de um arquivo JSON
    df_list_stocks = pd.read_json(io.StringIO(json.dumps(available())))
    df_list_stocks = df_list_stocks[~df_list_stocks[0].str.endswith('F')]
    df_list_stocks = df_list_stocks.sort_values(by=[0])

    # Seleção de ticker através da barra lateral
    option = st.selectbox("Selecione uma Ação:", df_list_stocks)

    # Filtrando o DataFrame pelo ticker selecionado
    df_quote = pd.read_json(io.StringIO(json.dumps(quoteTicker(option))))
    df_quote = df_quote[df_quote['volume'] > 0]

    # Pegar os dois últimos preços de fechamento
    ultimo_preco = df_quote['close'].iloc[-1]
    preco_anterior = df_quote['close'].iloc[-2]

    # Calcular a variação percentual
    var_percentual = ((ultimo_preco - preco_anterior) / preco_anterior) * 100

    df_info_json = infoTicker(option)
    df_info = pd.DataFrame([df_info_json])

    company = f"{option} - {df_info_json['longName']}"

    # Criação do gráfico de velas
    fig_quote = go.Figure(data=[go.Candlestick(x=df_quote['date'],
                        open=df_quote['open'],
                        high=df_quote['high'],
                        low=df_quote['low'],
                        close=df_quote['close'])])

    # Configuração do layout do gráfico
    fig_quote.update_layout(
        xaxis_rangeslider_visible=False,
        hovermode='x',
        xaxis=dict(
            showspikes=True, spikethickness=0.5, spikedash='dash', 
            spikecolor="#999999", spikemode='across'),
        yaxis=dict(
            side='right', tickformat=',.4f', showspikes=True, 
            spikethickness=0.5, spikedash='dash', spikecolor="#999999")
    )

    # Informações de login do usuário e botão de Logout
    authenticator.logout("Sair", "sidebar")
    st.sidebar.title(f"Bem vindo {name}")

    # Exibição da logo e nome da empresa
    col1, col2, col3, col4 = st.columns([0.15,1,1,0.25])
    col1.image(df_info_json['logourl'], width=50)
    col2.markdown(f"### {option} - {df_info_json['longName']}")
    col3.empty()
    col4.metric(label="Último preço", value=f"{ultimo_preco:.2f}", delta=f"{var_percentual:.2f}%")

    # Exibição do gráfico e análise do ChatGPT
    st.plotly_chart(fig_quote, use_container_width=True)
    st.subheader("Análise dos preços da Ação",divider="grey")


    if st.button("Clique para obter análise do ChatGPT-3.5"):
        with st.spinner("Aguardando resposta..."):
            st.markdown(sendQuestion(df_quote, company))