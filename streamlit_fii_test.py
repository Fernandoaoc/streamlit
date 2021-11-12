import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import streamlit.components.v1 as components

from pyvis.network import Network

st.title("FII'S")

data_end = 'df2_streamlit_test.csv'
date_column = 'data_trimestre'

@st.cache
def load_data():
    data = pd.read_csv(data_end)
    data[date_column] = pd.to_datetime(data[date_column], format='%Y-%m-%d')
    return data

data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
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

if st.checkbox('Show Numeber of Documents'):
    st.subheader('Documentos por Trimestre')
    st.table(table)

st.bar_chart(table)


st.sidebar.title('Select the year of Network')
option=st.sidebar.selectbox('select graph',('CVM 2016', 'CVM 2017', 'CVM 2018', 'CVM 2019', 'CVM 2020', 'CVM 2021'))
physics=st.sidebar.checkbox('add physics interactivity?')

if option=='CVM 2016':
  HtmlFile = open("html\INSIGHTS_FIIS_2016.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 700,width=700)

if option=='CVM 2017':
  HtmlFile = open("html\INSIGHTS_FIIS_2017.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 700,width=700)

if option=='CVM 2018':
  HtmlFile = open("html\INSIGHTS_FIIS_2018.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 700,width=700)

if option=='CVM 2019':
  HtmlFile = open("html\INSIGHTS_FIIS_2019.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 700,width=700)

if option=='CVM 2020':
  HtmlFile = open("html\INSIGHTS_FIIS_2020.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 700,width=700)

if option=='CVM 2021':
  HtmlFile = open("html\INSIGHTS_FIIS_2021.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 700,width=700)
