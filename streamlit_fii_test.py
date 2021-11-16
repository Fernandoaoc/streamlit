import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import streamlit.components.v1 as components
import datetime as dt
import csv

from pyvis.network import Network

st.title("FII'S")
data_end = 'df2_streamlit_test.csv'
date_column = 'data_trimestre'

@st.cache

# Leitura dos dados
def load_data():
    data = pd.read_csv(data_end)
    data[date_column] = pd.to_datetime(data[date_column], format='%Y-%m-%d')
    return data

data = load_data()

# checkbox de mostrar os dados como foram importados
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    #mostra a tabela
    st.table(data) 

# criação da tabela de quantidade geral de documentos por data
docs = data['data_trimestre'].value_counts().sort_index()
index = data['data_trimestre'].value_counts().sort_index().index
doc=[d for d in docs]
ind=[i for i in index]

table = pd.DataFrame(doc, index=ind, columns=["Nº de doc's"])

# checkbox de mostrar os dados da tabela de quantidade de documentos
if st.checkbox('Documentos'):
    st.subheader('Documentos por Trimestre')
    # mostra a tabela
    st.table(table)

#cria o gráfico
st.bar_chart(table)

# INICIO DA SEÇÃO DE REDES
st.sidebar.title("Manipulação da Rede")

# INPUT ESTILO CALENDARIO PARA DEFINIÇÃO DE DATAS INICIAL E FINAL PARA CONSULTA
inicial = st.sidebar.date_input("Data Inicial",min_value=dt.datetime(2016,1,1), max_value=dt.datetime.today(), value=dt.datetime(2016, 6, 6))
final = st.sidebar.date_input("Data Final",min_value=dt.datetime(2016,1,1), max_value=dt.datetime.today(), value=dt.datetime.today())

@st.cache
# FUNÇÃO PPARA FILTRAR O DF ORIGINAL -> retorna o DF Filtrado
def filtro(inicial, final):
  df_filtered = data.loc[(data['data_trimestre'] >= pd.to_datetime(inicial)) & (data['data_trimestre'] <= pd.to_datetime(final))]
  df_filtered.reset_index(drop=True, inplace=True)
  return df_filtered

df_filtrado = filtro(inicial=inicial, final=final)

@st.cache
def rede_forma_1(df_filtered, inicial, final):

    net = Network(height='700px', width='100%',notebook=True, heading=f"REDE DE FII'S: Período: {inicial} até {final}")

    Gpandas = nx.from_pandas_edgelist(df_filtered, source='fundo', target='nome_ativo')
    net.from_nx(Gpandas)

    #net.barnes_hut()
    net.show_buttons()
    net.show('Rede_forma_1.html')

    return Gpandas

@st.cache
def net_parameters(df_filtered):
   
    Gpandas = nx.from_pandas_edgelist(df_filtered, source='fundo', target='nome_ativo')
    
    info = nx.info(Gpandas)
    # aparece falso caso tenha mais de 1 componente na rede
    connect = nx.is_connected(Gpandas)

    #lista de componentes e o maior componente
    components = nx.connected_components(Gpandas)
    largest_component = max(components, key=len)

    #grafo do maior componente
    subgraph = Gpandas.subgraph(largest_component)
    #diametro da subrede
    diameter_subgraph = nx.diameter(subgraph)
    #transitividade
    transitivity = nx.transitivity(Gpandas)

    degree_dict = dict(Gpandas.degree(Gpandas.nodes()))
    nx.set_node_attributes(Gpandas, degree_dict, 'degree')
    return info, connect, transitivity, largest_component, subgraph, diameter_subgraph 



def rede_forma_2(df_filtered, inicial, final):
    
    G = nx.Graph()
    node = [n for n in df_filtered['fundo']]
    node_names = [n for n in df_filtered['fundo']]
    target = [t for t in df_filtered['nome_ativo']]
    edges = []
    for e in range(0, len(node)):
        edge = (node[e], target[e])
        edges.append(edge)

    G.add_nodes_from(node)
    G.add_edges_from(edges)

    net = Network(height='700px', width='100%',notebook=True, heading=f"REDE DE FII'S: Período: {inicial} até {final}")
    net.from_nx(G)
    #net.barnes_hut()
    net.show_buttons()

    return net.show('Rede_forma_2.html')

if st.checkbox('filtrado'):
    st.subheader('filtrado data')
    #mostra a tabela
    st.table(df_filtrado) 

st.subheader("Rede 1")

if st.sidebar.button('Calcular Rede 1'):
    net = rede_forma_1(df_filtered=df_filtrado, inicial=inicial, final=final)
    html_file_1 = open('Rede_forma_1.html')
    source_code_1 = html_file_1.read() 
    components.html(source_code_1, height = 700,width=700)

st.subheader("Parâmetros")

#if st.sidebar.button('Calcular Rede 2'):
#    net = rede_forma_2(df_filtered=df_filtrado, inicial=inicial, final=final)
#    html_file = open('Rede_forma_2.html')
#    source_code = html_file.read() 
if st.sidebar.button('Calcular parâmetros'):
    info, connect, transitivity, largest_component, subgraph, diameter_subgraph = net_parameters(df_filtered=df_filtrado)
    st.text(info)
    st.text(f'A rede possui apenas um componente? {connect}' )
    st.text(f'O maior componente da rede: {largest_component} ')
    st.text(f'transitividade: {transitivity}')
    st.text(f'Diâmetro da maior componente: {diameter_subgraph}')


#consulta dos documentos por data de cada fundo
st.subheader("Consulta por Fundo")

options = data['fundo'].unique()

fundos = st.selectbox("Selecione o nome do fundo",options=options)

#quantidade de documentos por FII
def fund(fii):
    b = data.loc[data['fundo'] == fii]
    df = b.sort_values(by='data_trimestre')

    docs = df['data_trimestre'].value_counts().sort_index()
    index = df['data_trimestre'].value_counts().sort_index().index
    doc=[d for d in docs]
    ind=[i for i in index]

    table = pd.DataFrame(doc, index=ind, columns=[f"{fii}"])

    return table

if st.checkbox('Fundo'):
    st.subheader('Documentos por Trimestre')
    st.table(fund(fii=fundos))
st.bar_chart(fund(fii=fundos))







