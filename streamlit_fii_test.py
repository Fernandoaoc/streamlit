import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import streamlit.components.v1 as components
import datetime as dt

from pyvis.network import Network

st.title("FII'S")
data_end = 'df2_streamlit_test.csv'
date_column = 'data_trimestre'

@st.cache
def load_data():
    data = pd.read_csv(data_end)
    data[date_column] = pd.to_datetime(data[date_column], format='%Y-%m-%d')
    #data[date_column] = data[date_column].apply(lambda x: dt.datetime.strptime(x, '%Y/%m'))
    return data

data_load_state = st.text('Loading data...')

data = load_data()

data_load_state.text("Done! (using st.cache)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

docs = data['data_trimestre'].value_counts().sort_index()
index = data['data_trimestre'].value_counts().sort_index().index
doc=[]
ind=[]
for d in docs:
    doc.append(d)
for i in index:
    ind.append(i)

table = pd.DataFrame(doc, index=ind, columns=["Nº de doc's"])

if st.checkbox('Show Number of Documents'):
    st.subheader('Documentos por Trimestre')
    st.table(table)

st.bar_chart(table)


st.sidebar.title("Manipulação da Rede")

inicial = st.sidebar.date_input("Data Inicial",min_value=dt.datetime(2016,1,1), max_value=dt.datetime.today(), value=dt.datetime(2016, 7, 6))
final = st.sidebar.date_input("Data Final",min_value=dt.datetime(2016,1,1), max_value=dt.datetime.today(), value=dt.datetime.today())

def filtro(inicial, final):
  df_filtered = data.loc[(data['data_trimestre'] >= pd.to_datetime(inicial)) & (data['data_trimestre'] <= pd.to_datetime(final))]
  df_filtered.reset_index(drop=True, inplace=True)
  return df_filtered

df_filtrado = filtro(inicial=inicial, final=final)

def rede(df_filtered, inicial, final):
  net = Network(height='700px', width='100%',notebook=True, heading=f"REDE DE FII'S: Período: {inicial} até {final}")

  for i in range(0,len(df_filtered)):
      ativo = df_filtered['quantidade_ativo'][i]
      net.add_node(df_filtered['fundo'][i], value=df_filtered['Qdade_cotas_emitidas'][i]/max(df_filtered['Qdade_cotas_emitidas']), title=df_filtered['fundo'][i])
      net.add_node(df_filtered['nome_ativo'][i], value=0.2 , title=df_filtered['nome_ativo'][i], color='#FFA07A')
      net.add_edge(df_filtered['fundo'][i], df_filtered['nome_ativo'][i], value=df_filtered['quantidade_ativo'][i]/max(df_filtered['quantidade_ativo']), title=f'Nº de Ativos: {ativo}')

  #net.barnes_hut()
  net.show_buttons()
  return net.show('Rede.html')

st.subheader("Rede")
if st.sidebar.button('Calcular Rede'):
  net = rede(df_filtered=df_filtrado, inicial=inicial, final=final)
  html_file = open('Rede.html')
  source_code = html_file.read() 
  components.html(source_code, height = 700,width=700)


