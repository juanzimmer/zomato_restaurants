#BIBLIOTECAS----------------------------------------------------------------------------
import pandas as pd
import numpy as np
import inflection
import plotly.express as px
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Visão Cidade',
    page_icon='🏢'
)

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

def grafico_cidades(df):
    
    df_aux = df.loc[:, ['city', 'restaurant_id', 'country']].groupby(['country', 'city']).count().reset_index().sort_values(by='restaurant_id', ascending=False).head(10)
    #grafico
    fig = px.bar(df_aux, x='city' ,y='restaurant_id', color='country', text_auto=True )
    return fig

def top_melhores(df):
            df_aux = df.loc[df['aggregate_rating'] > 4, ['city', 'restaurant_id']].groupby('city').count().reset_index().sort_values(by='restaurant_id', ascending=False).head(7)
            return df_aux

def top_piores(df):    
            df_aux = df.loc[df['aggregate_rating'] < 2.5, ['city', 'restaurant_id']].groupby('city').count().reset_index().sort_values(by='restaurant_id', ascending=False).head(7)
            return df_aux

def distinct_cuisines(df):
    df_aux = df.loc[:, ['country', 'unique_cuisines']].groupby('country').nunique().reset_index().sort_values(by='unique_cuisines', ascending=False).head(10)
    #grafico
    fig = px.bar(df_aux, x='country', y='unique_cuisines', color='country', text_auto=True)
    return fig

#TRATAMENTO DE DADOS -------------------------------------------------------------------

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


#TITULO PAGINA--------------------------------------------------------------------------
st.markdown('#  🏢Visão Cidade')


#BARRA LATERAL--------------------------------------------------------------------------
#anexando imagem
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

#criando barra lateral
#title
st.sidebar.markdown('# Fome Zero')
#subtitle
st.sidebar.markdown('## Bests Restaurants Here')
#barra separadora
st.sidebar.markdown("""___""")

#titulo barra interativa
st.sidebar.markdown('## Selecione uma data limite')

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


#LAYOUT STREAMLIT (GRÁFICOS)-------------------------------------------------------------------

st.markdown("""___""")

#1. top 10 cidade com mais restaurantes na Base de Dados
st.markdown('### Top 10 cidades com mais restaurantes na base de dados')
fig = grafico_cidades(df)
st.plotly_chart(fig, use_container_width=True)


#2. MULTGRAFICOS
with st.container():
    col1, col2 = st.columns(2)


    #2.1 Top 7 restaurantes com avaliação 4+
    with col1:
        st.markdown('#### Top cidades com maiores avaliações')
        df_aux = top_melhores(df)
        st.dataframe(data = df_aux, use_container_width=False)


    with col2:
        st.markdown('#### Top cidades com menores avaliações')
        df_aux = top_piores(df)
        st.dataframe(data=df_aux, use_container_width=False)


#3. Top 10 cidades com mais tipos distintos de culinária
st.markdown('### Top 10 cidades com mais tipos distintos de culinária')
fig = distinct_cuisines(df)
st.plotly_chart(fig, use_container_width=False)

