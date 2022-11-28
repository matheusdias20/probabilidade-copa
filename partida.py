import streamlit as st
import pandas as pd
import numpy as np
# import random
from scipy.stats import poisson

st.markdown("<h1 style='text-align: center'>Previsões estatísticas para Copa do Mundo 2022 - Qatar</h1>", unsafe_allow_html=True)




selecoes = pd.read_excel('data\DadosCopaDoMundoQatar2022.xlsx', sheet_name = 'selecoes', index_col = 0)


fifa = selecoes['PontosRankingFIFA']
a, b = min(fifa), max(fifa)

fa, fb = 0.15, 1

b1 = (fb - fa)/(b-a)
b0 = fb - b*b1
forca = b0 + b1*fifa


def MediasPoisson(selecao1, selecao2):
  forca1 = forca[selecao1]
  forca2 = forca[selecao2]

  mgols = 2.75
  l1 = mgols*forca1/(forca1 + forca2)
  l2 = mgols - l1

  return [l1, l2]


def Resultado (gols1, gols2):
  if gols1 > gols2:
    resultado = 'V'
  elif gols2 > gols1:
    resultado = 'D'
  else:
    resultado = 'E'
  return resultado


def Distribuicao(media):
  probs = []
  for i in range(7):
    probs.append(poisson.pmf(i, media))
  probs.append(1 - sum(probs))
  return pd.Series(probs, index = ['0', '1', '2', '3', '4', '5', '6', '7+'])

def ProbabilidadesPartida(selecao1, selecao2):
  l1, l2 = MediasPoisson(selecao1, selecao2)
  d1, d2 = Distribuicao(l1), Distribuicao(l2) 

  matriz = np.outer(d1, d2)

  vitoria = np.tril(matriz).sum()-np.trace(matriz) # Soma triangulo inferior
  derrota = np.triu(matriz).sum()-np.trace(matriz) # Soma triangulo superior
  empate = 1 - (vitoria + derrota)

  probs = np.around([vitoria, empate, derrota], 3)
  probsp = [f'{100 * i:.1f}%' for i in probs]

  nomes = ['0', '1', '2', '3', '4', '5', '6', '7+']
  matriz = pd.DataFrame(matriz, columns = nomes, index = nomes)
  matriz.index = pd.MultiIndex.from_product([[selecao1], matriz.index])
  matriz.columns = pd.MultiIndex.from_product([[selecao2], matriz.columns])

  output = {'selecao1': selecao1, 'selecao2': selecao2,
            'f1': forca[selecao1], 'f2': forca[selecao2],
            'media1': l1, 'media2': l2,
            'probabilidades': probsp, 'matriz': matriz}

  return output



def Pontos (gols1, gols2):
  resultado = Resultado(gols1, gols2)
  if resultado == 'V':
    pontos1, pontos2 = 3, 0
  elif resultado == 'D':
    pontos1, pontos2 = 0, 3
  else:
    pontos1, pontos2 = 1, 1
  return [pontos1, pontos2, resultado]


def Jogo(selecao1, selecao2):
  l1, l2 = MediasPoisson(selecao1, selecao2)
  gols1 = int(np.random.poisson(lam = l1, size = 1))
  gols2 = int(np.random.poisson(lam = l2, size = 1))

  saldo1 = gols1 - gols2
  saldo2 = -saldo1
  pontos1, pontos2, resultado  =  Pontos (gols1, gols2)
  placar = '{}x{}'.format(gols1, gols2)
  return [gols1, gols2, saldo1, saldo2, pontos1, pontos2, resultado, placar]

st.markdown('----')
st.markdown("## ⚽ Probabilidades de Jogos")

listaselecoes1 = selecoes.index.tolist()
listaselecoes1.sort()
listaselecoes2 = listaselecoes1.copy()

j1, j2 = st.columns(2)
selecao1 = j1.selectbox('Escolha a primeira Seleção', listaselecoes1)
listaselecoes2.remove(selecao1)
selecao2 = j2.selectbox('Escolha a segunda Seleção', listaselecoes2, index = 1)
st.markdown('---')


jogo = ProbabilidadesPartida(selecao1, selecao2)
prob = jogo['probabilidades']
matriz = jogo['matriz']


col1, col2, col3, col4, col5 = st.columns(5)
col1.image(selecoes.loc[selecao1, 'LinkBandeiraGrande'])
col2.metric(selecao1, prob[0])
col3.metric('Empate', prob[1])
col4.metric(selecao2, prob[2])
col5.image(selecoes.loc[selecao2, 'LinkBandeiraGrande'])


st.markdown('----')
st.markdown("## 📊 Probabilidades dos Placares")

def aux(x):
    return f'{str(round(100*x,1))}%'

st.table(matriz.applymap(aux))


st.markdown('----')
st.markdown("## 🌎 Probabilidades dos Placares")

jogoscopa = pd.read_excel('data\output.xlsx')
st.table(jogoscopa[['Grupo', 'Seleção 1', 'Seleção 2', 'Vitoria', 'Empate', 'Derrota']])