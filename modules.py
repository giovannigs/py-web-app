from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
import streamlit as st
import requests
import os

load_dotenv()

def logError(status_code, filePath='logError.txt'):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = open(filePath,'a')
    f.write(f"{now} - Request failed with status code {status_code}\n")

#############################
# brAPI endpoints functions #
#############################

@st.cache_data
def available(select='stocks') -> dict:
    url = "https://brapi.dev/api/available"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()[f'{select}']
        # st.success("Fetched data from API!")
        return data
    else:
        logError(response.status_code)

def quoteList(select='stocks') -> dict:
    url = "https://brapi.dev/api/quote/list"
    params = {
        'token': os.getenv('BRAPITOKEN'),
    }
 
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()[f'{select}']
        return data
    else:
        logError(response.status_code)

@st.cache_data
def quoteTicker(ticker,range='3mo') -> dict:
    url = f"https://brapi.dev/api/quote/{ticker}"
    params = {
        'range': range,
        'interval': '1d',
        'token': os.getenv('BRAPITOKEN'),
    }
    
    response = requests.get(url, params=params, timeout=30)
    
    if response.status_code == 200:
        data = response.json()['results'][0]['historicalDataPrice']
        # st.success("Fetched data from API!")
        return data
    else:
        logError(response.status_code)

@st.cache_data
def infoTicker(ticker,range='3mo') -> dict:
    url = f"https://brapi.dev/api/quote/{ticker}"
    params = {
        'range': range,
        'interval': '1d',
        'token': os.getenv('BRAPITOKEN'),
    }
    
    response = requests.get(url, params=params, timeout=30)
    
    if response.status_code == 200:
        data = response.json()['results'][0]
        data.pop("historicalDataPrice")
        data.pop("validIntervals")
        data.pop("validRanges")
        data.pop("usedInterval")
        # st.success("Fetched data from API!")
        return data
    else:
        logError(response.status_code)


############################
# ChatGPT OpenAI endpoints #
############################

def sendQuestion(data,company):
    # df = pd.DataFrame(data)

    # Convertendo o DataFrame para uma string formatada
    df_string = data.to_string()

    client = OpenAI(
        api_key=os.getenv('CHATGPTTOKEN'),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Você irá receber dados de preço de uma determinada ação e sua tarefa será resumir os dados recebidos em tendências, médias e possíveis preços futuros."
            },
            {
                "role":"user",
                "content":f"Ação:\n{company}. Dados:\n{df_string}"
                # "content":f"Com base nos dados a seguir, realize uma análise dos preços de abertura, máxima, mínima e fechamento da ação {company}, além de verificar tendências de alta ou queda, médias dos últimos dias, etc. Por favor não retorne os mesmos dados fornecidos em formato de uma tabela. Dados:\n{df_string}"
            }
        ],
        model="gpt-3.5-turbo",
        max_tokens=456,
        temperature=0.7
    )

    return chat_completion.choices[0].message.content