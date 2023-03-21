#BIBLIOTECAS
import inflection
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import numpy as np

#for show all columns
pd.set_option('display.max_columns', None)

#DATAFRAME------------------------------------------------------------------------------
dataframe = pd.read_csv('zomato.csv')


#FUNÇÕES--------------------------------------------------------------------------------
#renomear colunas do dataframe
def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

#criação de função para preencher paises
COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}
def country_name(country_code):
    return COUNTRIES[country_code]


#crianção do tipo de categoria de comida
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"
    

#criação do nome das cores
COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

def plotagem_map(df):
    map = folium.Map([42 ,29], zoom_start=2,width="%100",height="%100")
    locations = list(zip(df.latitude, df.longitude))
    cluster = folium.plugins.MarkerCluster(locations=locations,                     
                popups=df['city'].tolist())  
    map.add_child(cluster)
    return map



#TRATAMENTO DE DADOS ---------------------------------------------------------------------

#renomeando colunas
df = rename_columns(dataframe)

#coluna de paises com função
df['country'] = df['country_code'].apply(country_name)

#tipo de categoria de comida
df['price_range'] = df['price_range'].apply(create_price_tye)

#criação do nome das cores
df['rating_color'] = df['rating_color'].apply(color_name)

#nova coluna com a apenas um tipo de cozinha por restaurante
df['unique_cuisines'] = df['cuisines'].str.split(',', expand=True)[0]

#tratando nulo de uma coluna
df = df.loc[df['cuisines'].notna()]

#dropando nulos da coluna restaurant_id
df['restaurant_id'] = df['restaurant_id'].drop_duplicates()

#configurações visuais do titulo da página
st.set_page_config(
    page_title="Home",
    layout="wide"
)

#image_path = '/Users/55819/Desktop/comunidade_DS/dados/repos/FTC_analise_com_python/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

#SIDE BAR------------------------------------------------------------------------------------
#title
st.sidebar.markdown('# Fome Zero!')
#barra separadora
st.sidebar.markdown("""___""")
#titulo barra interativa
st.sidebar.markdown('## Selecione um país')

#multseleção PAISES
country_options = st.sidebar.multiselect(
    'Selecione os países',
    ['Philippines', 'Brazil', 'Australia', 'United States of America',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
       'Sri Lanka', 'Turkey'],
    default=['Brazil', 'Australia', 'United States of America', 'New Zeland', 'England', 'Qatar'])

#barra separadora
st.sidebar.markdown("""___""")



#multseleção Culinaria
lista = list(df['unique_cuisines'].unique())
cuisines_options = st.sidebar.multiselect(
    'Tipos de culinária',
    lista,
    default=['Italian', 'American', 'Sushi', 'Pizza', 'Arabian', 'Coffee'])

#barra separadora
st.sidebar.markdown("""___""")
#assinatura
st.sidebar.markdown('### Powered by Juan Zimmermann')


#INTERAÇÃO NO FILTRO---------------------------------------------------------------------------

#filtro pais
linhas_selecionadas = df['country'].isin(country_options)
df = df.loc[linhas_selecionadas, :]

# filtro comida
linhas_selecionadas = df['unique_cuisines'].isin(cuisines_options)
df = df.loc[linhas_selecionadas, :]


#CORPO DE PAGINA------------------------------------------------------------------------------
st.write("# Fome Zero!")
st.markdown('## O Melhor lugar para encontrar seu mais novo restaurante favorito!')
st.markdown('___')


#1. multcolunas
with st.container():
    st.markdown('### Temos as seguintes marcas em nossa plataforma:')
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        df_aux = len(df['restaurant_id'].unique())
        col1.metric('Restaurantes cadastrados', df_aux)

    with col2:
        df_aux = len(df['country'].unique())
        col2.metric('Países cadastrados', df_aux)
                  
    with col3:
        df_aux = len(df['city'].unique())
        col3.metric('Cidades cadastradas', df_aux)

    with col4:
        df_aux = df['votes'].sum()
        col4.metric('Avaliações feitas na plataforma', df_aux)

    with col5:
        df_aux = len(df['unique_cuisines'].unique())
        col5.metric('Tipos de culinária', df_aux)

#2. PLOTANDO MAPA
map = plotagem_map(df)
folium_static(map, width=1024, height=600)

st.markdown(
    """
    Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    
    ### Ask for Help
        - LinkedIn: Juan Zimmermann
        - Git Hub: juanzimmer
        - Discord: Juan Zimmermann
""")




