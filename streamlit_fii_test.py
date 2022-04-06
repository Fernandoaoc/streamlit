import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import streamlit.components.v1 as components
import datetime as dt

from operator import itemgetter
from networkx.algorithms import community
from networkx.linalg.graphmatrix import adjacency_matrix
from scipy.sparse.sputils import matrix
from pyvis.network import Network


st.set_page_config(layout="wide", page_icon="⛓️", page_title="Redes Complexas")


### IMPORTANDO DADOS ###

DATA_END = "redes_complexas_trab_final.csv"
COLUMN = "data_trimestre"

@st.cache
# Leitura dos dados
def load_data():
    data = pd.read_csv(DATA_END)
    data[COLUMN] = pd.to_datetime(data[COLUMN], format='%Y-%m-%d')
    return data

data = load_data()


### FUNÇÃO PPARA FILTRAR O DATAFRAME ORIGINAL -> retorna o DATAFRAME Filtrado ###

def filtro(inicial, final):
  df_filtered = data.loc[(data['data_trimestre'] >= pd.to_datetime(inicial)) & (data['data_trimestre'] <= pd.to_datetime(final))]
  df_filtered.reset_index(drop=True, inplace=True)
  return df_filtered

### CRIANDO A REDE PELO PyVis ###
def rede_forma_1(df_filtered, inicial, final):

    net = Network(height='600px', width='100%',notebook=True, heading=f"REDE DE FII'S: Período: {inicial} até {final}")

    G = nx.from_pandas_edgelist(df_filtered, source='fundo', target='nome_ativo')
    net.from_nx(G)

    #net.barnes_hut()
    net.show_buttons()
    net.show('Rede.html')

    return G

def colorido_no(data, nome):
    consulta = data.loc[(data['fundo'] == nome) | (data['nome_ativo'] == nome)]
    consulta.reset_index(drop=True, inplace=True)

    if consulta['segmento_atuacao'][0] == 'Titulos e Val. Mob.':
        cor = '#800080'
    elif consulta['segmento_atuacao'][0] == 'Outros':
        cor = '#0000FF'
    elif consulta['segmento_atuacao'][0] == 'Hibrido':
        cor = '#FF0000'
    elif consulta['segmento_atuacao'][0] == 'Lajes Corporativas':
        cor = '#008000'
    elif consulta['segmento_atuacao'][0] == 'Logistica':
        cor = '#DAA520'
    elif consulta['segmento_atuacao'][0] == 'Shoppings':
        cor = '#B0E0E6'
    elif consulta['segmento_atuacao'][0] == 'Hospital':
        cor = '#808000'
    else:
        cor = '#FFFF00' # Hotel

    return cor

def rede_colorida(df_filtered, inicial, final):
    options = {
        "edges": {
            "arrows": {
            "middle": {
                "enabled": True
            }
            },
        "color": {
            "inherit": True
            },
        "smooth": False
        },
        "interaction": {
            "navigationButtons": True
        },
        "physics": {
            "minVelocity": 0.75
        }
        }

    nt = Network(width='100%', notebook=True, heading=f"REDE DE FII'S: Período: {inicial} até {final}")

    G = nx.Graph(name=f"FII's de: {inicial} até {final}")

    nodes = list(df_filtered['fundo'].unique()) + list(df_filtered['nome_ativo'].unique())

    mandato_dict = {}
    tipo_gestao_dict = {}
    segmento_atuacao_dict ={}
    cnpj_fundo_dict = {}
    Qdade_cotas_emitidas_dict = {}

    for n in nodes:
        fundo = df_filtered.loc[df_filtered['fundo'] == n]
        ativo = df_filtered.loc[df_filtered['nome_ativo'] == n]

        if fundo.empty == False:
            fundo.reset_index(inplace=True, drop=True)
            G.add_node(n, label=n, color= colorido_no(df_filtered,n), size= fundo['size'][0])
            
            mandato_dict[fundo['fundo'][0]] = fundo['mandato'][0]
            tipo_gestao_dict[fundo['fundo'][0]] = fundo['tipo_gestao'][0]
            segmento_atuacao_dict[fundo['fundo'][0]] = fundo['segmento_atuacao'][0]
            cnpj_fundo_dict[fundo['fundo'][0]] = fundo['cnpj_fundo'][0]
            Qdade_cotas_emitidas_dict[fundo['fundo'][0]] = fundo['Qdade_cotas_emitidas'][0]        

        if ativo.empty == False:
            ativo.reset_index(inplace=True, drop=True)
            G.add_node(n, label=n, color= colorido_no(df_filtered,n), size=ativo['size'][0])

            mandato_dict[ativo['nome_ativo'][0]] = ativo['mandato'][0]
            tipo_gestao_dict[ativo['nome_ativo'][0]] = ativo['tipo_gestao'][0]
            segmento_atuacao_dict[ativo['nome_ativo'][0]] = ativo['segmento_atuacao'][0]
            cnpj_fundo_dict[ativo['nome_ativo'][0]] = ativo['cnpj_fundo'][0]
            Qdade_cotas_emitidas_dict[ativo['nome_ativo'][0]] = ativo['Qdade_cotas_emitidas'][0]        

    for e in range(0, len(df_filtered['nome_ativo'])):
        G.add_edge(df_filtered['fundo'][e], df_filtered['nome_ativo'][e])

    nx.set_node_attributes(G, mandato_dict, 'mandato')
    nx.set_node_attributes(G, tipo_gestao_dict, 'tipo_gestao')
    nx.set_node_attributes(G, segmento_atuacao_dict, 'segmento_atuacao')
    nx.set_node_attributes(G, cnpj_fundo_dict, 'cnpj_fundo')
    nx.set_node_attributes(G, Qdade_cotas_emitidas_dict, 'Qdade_cotas_emitidas')

    nt.from_nx(G)
    #nt.show_buttons()
    nt.set_options(
        """
        var options = {
            "edges": {
                "arrows": {
                "middle": {
                    "enabled": true
                }
                },
                "color": {
                "inherit": true
                },
                "smooth": false
            },
            "interaction": {
                "hover": true,
                "navigationButtons": true
            },
            "manipulation": {
                "enabled": true
            },
            "physics": {
                "minVelocity": 0.75
            }
            }
        """
    )
    nt.show('nt_colorida_tamanho.html')
    fig = plt.figure(figsize=(20,20))
    fig.savefig('imagem_rede.svg')
    nx.write_gexf(G,'arquivo_gephi_imagem.gexf')
    return G

def subnet(rede):

    net = Network(height='600px', width='100%',notebook=True, heading=f"REDE DE FII'S: Período: {inicial} até {final}")

    Gcc = rede.subgraph(sorted(nx.connected_components(rede), key=len, reverse=True)[0])
    #pos = nx.spring_layout(Gcc)
    net.from_nx(Gcc)
    net.show_buttons()
    net.show('subrede.html')

    return Gcc

def measueres(rede):

    degree_dict = dict(rede.degree(rede.nodes()))
    nx.set_node_attributes(rede, degree_dict, 'grau')

    betweenness_dict = nx.betweenness_centrality(rede)
    nx.set_node_attributes(rede, betweenness_dict, 'betweenness')
    
    centrality_dict = nx.degree_centrality(rede)
    nx.set_node_attributes(rede, centrality_dict, 'centralidade')

def comunidade(rede):    
    communities = community.greedy_modularity_communities(rede)
    modularity_dict = {} # Create a blank dictionary
    for i,c in enumerate(communities): # Loop through the list of communities, keeping track of the number for the community
        for name in c: # Loop through each person in a community
            modularity_dict[name] = i # Create an entry in the dictionary for the person, where the value is which group they belong to.

    # Now you can add modularity information like we did the other metrics
    nx.set_node_attributes(rede, modularity_dict, 'modularidade')

def legenda():
    col = {'Titulos e Val. Mob.' : ['Titulos e Val. Mob.'],
            'Logistica' : ['Logistica'],
            'Hibrido' : ['Hibrido'],
            'Lajes Corporativas' : ['Lajes Corporativas'],
            'Shoppings'	: ['Shoppings'],
            'Hospital'	: ['Hospital'],
            'Outros'	: ['Outros'],
            'Hotel'	: ['Hotel']}    
    titulos = pd.DataFrame(col)
    return titulos

def cor_legenda(val):
    if val == 'Titulos e Val. Mob.':
        cor = '#800080'
    elif val == 'Outros':
        cor = '#0000FF'
    elif val == 'Hibrido':
        cor = '#FF0000'
    elif val == 'Lajes Corporativas':
        cor = '#008000'
    elif val == 'Logistica':
        cor = '#DAA520'
    elif val == 'Shoppings':
        cor = '#B0E0E6'
    elif val == 'Hospital':
        cor = '#808000'
    else:
        cor = '#FFFF00' # Hotel

    return f'background-color: {cor}; color: {cor}'

#################
### SELECTION ###
#################

st.sidebar.text('')
st.sidebar.text('')
st.sidebar.text('')

### SEASON RANGE ###
st.sidebar.markdown("**Selecione o Período de Análise:** 👇")

### INPUT ESTILO CALENDARIO PARA DEFINIÇÃO DE DATAS INICIAL E FINAL PARA CONSULTA ###

inicial = st.sidebar.date_input("Data Inicial",min_value=dt.datetime(2016,1,1), max_value=dt.datetime.today(), value=dt.datetime(2016, 6, 6))
final = st.sidebar.date_input("Data Final",min_value=dt.datetime(2016,1,1), max_value=dt.datetime.today(), value=dt.datetime.today())


df_filtrado = filtro(inicial=inicial, final=final)




####################
### INTRODUCTION ###
####################

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title("Rede de FII's")
with row0_2:
    st.text("")
    st.markdown('<span style="font-size: 1.15em;">**Discente:** </span> <span style="font-size: 1em;">Fernando Coelho</span>', unsafe_allow_html=True)
row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
with row3_1:
    #st.markdown("**Resumo:** Aqui vai conter o resumo do trabalho, o pq e como dos dados entre outras coisas.")
    st.markdown("")

###################
### MAIS LINHAS ###
###################

row6_spacer1, row6_1, row6_spacer2 = st.columns((.2, 7.1, .2))
with row6_1:
    st.subheader("Dados")

row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3, row2_3, row2_spacer4  = st.columns((.2, 1.6, .2, 1.6, .2, 1.6, .2))
with row2_1:
    st.markdown(f"🗓️ Inicial:  {inicial}")
with row2_2:
    st.markdown(f"🗓️ Final:  {final}")
with row2_3:
    documentos = filtro(inicial=inicial, final=final)
    st.markdown(f"💼 {len(documentos)} Documentos")


row2_4_spacer1, row2_4, row2_4_spacer2 = st.columns((.2, 7.1, .2))

with row2_4:
    st.text("")
    st.write("**LEGENDA**", legenda().style.applymap(cor_legenda))
    st.text("")

row12_spacer1, row12_1, row12_spacer2 = st.columns((.2, 7.1, .2))

with row12_1:
    st.subheader('Topologia da Rede')

    if st.sidebar.button('Desenhar Rede'):
        
        net = rede_colorida(df_filtered=df_filtrado, inicial=inicial, final=final)
        html_file_1 = open('nt_colorida_tamanho.html')
        sub = subnet(net)
        html_file_2 = open('subrede.html')
        source_code_1 = html_file_1.read()
        source_code_2 = html_file_2.read() 
        components.html(source_code_1, height = 600)
        components.html(source_code_2, height = 600)

    st.text("")
    st.markdown(f"Rede criada com os {len(filtro(inicial=inicial, final=final))} documentos ")
    st.text("")
    net = rede_colorida(df_filtered=df_filtrado, inicial=inicial, final=final)
    measueres(net)
    comunidade(net)
    st.markdown("**Informações:**")
    st.text(nx.info(net))


row13_spacer1, row13_1, row13_spacer2, row13_2, row13_spacer3, row13_3, row13_spacer4 = st.columns((.2, 2., .2, 2., .2, 2., .2))
with row13_1:
    st.markdown(f"**Densidade:** {nx.density(net)} ")

with row13_2:
    st.markdown(f"**transitividade:** {nx.transitivity(net)}")

with row13_3:
    components = nx.connected_components(net)
    largest_component = max(components, key=len)
    st.markdown(f"**Número de componentes:** {len(largest_component)}")

row13_4_spacer1, row13_4, row13_4_spacer2 = st.columns((.2, 7.1, .2))

with row13_4:
    st.subheader("Selecione o Nó")
    option = st.selectbox("",df_filtrado['fundo'].unique())
    node_info = net.nodes[option]
    st.markdown(f"<span> **Grau: **</span><span>{node_info['grau']}</span> <br>", unsafe_allow_html=True)
    st.markdown(f"<span> **CNPJ: **</span> <span>{node_info['cnpj_fundo']}</span> <br>", unsafe_allow_html=True)
    st.markdown(f"<span> **Tamanho do Nó: **</span> <span>{node_info['size']}</span> <br>", unsafe_allow_html=True)
    st.markdown(f"<span> **Segmento de Gestão: **</span> <span>{node_info['segmento_atuacao']}</span> <br>", unsafe_allow_html=True)
    st.markdown(f"<span> **Mandato: **</span><span>{node_info['mandato']}</span> <br>", unsafe_allow_html=True)
    st.markdown(f"<span> **Tipo de Gestão: **</span> <span>{node_info['tipo_gestao']}</span> <br>", unsafe_allow_html=True)
    st.markdown(f"<span> **Cotas Emitidas: **</span> <span>{node_info['Qdade_cotas_emitidas']}</span> <br>", unsafe_allow_html=True)
    st.markdown(f"<span> **Betweenness: **</span> <span>{node_info['betweenness']}</span> <br>", unsafe_allow_html=True)
    st.markdown(f"<span> **Centralidade: **</span> <span>{node_info['centralidade']}</span> <br>", unsafe_allow_html=True)
    st.markdown(f"<span> **Modularidade: **</span> <span>{node_info['modularidade']}</span> <br>", unsafe_allow_html=True)

row14_spacer1, row14_1, row14_spacer2 = st.columns((.2, 7.1, .2))

with row14_1:
    st.subheader('Comunidades')

    #st.markdown("**row14_1:** Topologia da Subrede")


row15_spacer1, row15_1, row15_2, row15_3, row15_4, row15_spacer2  = st.columns((0.5, 2, 2, 2, 2, 0.5))

with row15_1:
    st.markdown(" Modularidade da Classe 0 Ordenada por betweenness:")
    classe = [n for n in net.nodes() if net.nodes[n]['modularidade'] == 0]

    class_betweenness = {n:net.nodes[n]['betweenness'] for n in classe}

    class_sorted_by_betweenness = sorted(class_betweenness.items(), key=itemgetter(1), reverse=True)

    for node in class_sorted_by_betweenness[:3]:
        st.write('**Name: **', node[0])
        st.write('**Betweenness: **', str(node[1])) 

with row15_2:
    st.markdown("Modularidade da Classe 1 Ordenada por betweenness:")
    classe = [n for n in net.nodes() if net.nodes[n]['modularidade'] == 1]

    class_betweenness = {n:net.nodes[n]['betweenness'] for n in classe}

    class_sorted_by_betweenness = sorted(class_betweenness.items(), key=itemgetter(1), reverse=True)

    for node in class_sorted_by_betweenness[:3]:
        st.write('**Name: **', node[0])
        st.write('**Betweenness: **', str(node[1])) 

with row15_3:
    st.markdown("Modularidade da Classe 2 Ordenada por betweenness:")
    classe = [n for n in net.nodes() if net.nodes[n]['modularidade'] == 2]

    class_betweenness = {n:net.nodes[n]['betweenness'] for n in classe}

    class_sorted_by_betweenness = sorted(class_betweenness.items(), key=itemgetter(1), reverse=True)

    for node in class_sorted_by_betweenness[:3]:
        st.write('**Name: **', node[0])
        st.write('**Betweenness: **', str(node[1])) 

with row15_4:
    st.markdown("Modularidade da Classe 3 Ordenada por betweenness:")
    classe = [n for n in net.nodes() if net.nodes[n]['modularidade'] == 3]

    class_betweenness = {n:net.nodes[n]['betweenness'] for n in classe}

    class_sorted_by_betweenness = sorted(class_betweenness.items(), key=itemgetter(1), reverse=True)

    for node in class_sorted_by_betweenness[:3]:
        st.write('**Name: **', node[0])
        st.write('**Betweenness: **', str(node[1])) 


row17_spacer1, row17_1, row17_spacer2 = st.columns((.2, 7.1, .2))
with row17_1:
    st.markdown("Aqui vai conter o resumo do trabalho, o pq e como dos dados entre outras coisas.")


row16_spacer1, row16_1, row16_2, row16_3, row16_4, row16_spacer2  = st.columns((0.5, 1.5, 1.5, 1, 2, 0.5))

"""
with row16_1:
    st.markdown("row16_1 "+ " 👟 Shots on Goal ")
    st.markdown("🏃‍♂️ Distance (in km)")
    st.markdown("🔁 Passes")
    st.markdown("🤹‍♂️ Possession")
    st.markdown("🤕 Fouls")
    st.markdown("🚫 Offside")
    st.markdown("📐 Corners")
with row16_2:
    st.markdown("**row16_2:** Aqui vai conter o resumo do trabalho, o pq e como dos dados entre outras coisas.")
with row16_4:
    st.markdown("**row16_4:** Aqui vai conter o resumo do trabalho, o pq e como dos dados entre outras coisas.")

"""


    
