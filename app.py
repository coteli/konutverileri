from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from datetime import timedelta

# Haritalar için GeoJson bilgilerini almak için gerekli kütüphaneler
from urllib.request import urlopen
import json

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dash Visualization"
server = app.server

# dataFramelerin düzenlenmesi
df = pd.read_csv("veriler.csv")
df["Dönem"] = pd.to_datetime(df["Dönem"])
df_uyruklar_toplam = pd.read_csv("uyruklar.csv")
df_cinsiyet_yıl_toplam = pd.read_csv("cinsiyet.csv")
df_cinsiyet_toplam = df_cinsiyet_yıl_toplam.drop(
    columns="Yıl").sum().to_frame().reset_index()
df_cinsiyet_toplam.rename(
    columns={"index": "Cinsiyet", 0: "Toplam Satış"}, inplace=True)
df_2021_eksik = pd.read_csv("harita.csv")

# Türkiye İller GeoJson verilerinin webden çekilemesi
with urlopen('https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geo/tr-cities-utf8.json') as response:
    geojson = json.load(response)  # Cihad Turhan'a teşekkürler
# Mevcut verilerle Geojson verilerinin eşleştirilmesi
geojson["features"][2]["properties"] = {'name': 'Afyonkarahisar'}

# Son 24 aya ait verilerin öne çıkarılarak grafiğin gösterilmesi
# Grafiğin x eksenini interaktif hale getirmek için başlangıç ve bitiş değerlerinin son 24 dönemi ifade edecek şekilde string olarak bir liste içerisine tanımlanması
range = [(df["Dönem"][-25:-24] + timedelta(days=15)).to_string().split("   ")
         [1], (df["Dönem"][-1:] + timedelta(days=15)).to_string().split("   ")[1]]

fig = px.bar(df, x="Dönem", y='Toplam Satış Adedi')
fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")
fig.update_layout(xaxis_rangeslider_visible=True, xaxis_range=range)

fig2 = px.bar(df, x="Dönem", y=["İpotekli Satışlar", "Diğer Satışlar"],
              barmode="group",
              labels={"value": "Adet", "variable": "Satış Şekli"})
fig2.update_xaxes(dtick="M1", tickformat="%b\n%Y")
fig2.update_layout(xaxis_rangeslider_visible=True, xaxis_range=range)
fig2.update_layout(legend=dict(
    yanchor="auto",
    y=1.25,
    xanchor="auto",
    x=0.5,
    title="",
))

fig3 = px.bar(df, x="Dönem", y=["İlk Satışlar", "İkinci El Satışlar"],
              barmode="group",
              labels={"value": "Adet", "variable": "Satış Durumu"})
fig3.update_xaxes(dtick="M1", tickformat="%b\n%Y")
fig3.update_layout(xaxis_rangeslider_visible=True, xaxis_range=range)
fig3.update_layout(legend=dict(
    yanchor="auto",
    y=1.25,
    xanchor="auto",
    x=0.5,
    title=""
))

fig4 = px.bar(df, x="Dönem", y="Yabancılara Yapılan Satışlar",
              labels={"value": "Adet", "variable": "Satış Şekli"})
fig4.update_xaxes(dtick="M1", tickformat="%b\n%Y")
fig4.update_layout(xaxis_rangeslider_visible=True, xaxis_range=range)


fig5 = px.bar(df, x="Dönem", y=["Yabancılara Yapılan Satışlar", "Toplam Satış Adedi"],
              barmode="group",
              labels={"value": "Adet", "variable": "Satış Şekli"})
fig5.update_xaxes(dtick="M1", tickformat="%b\n%Y")
fig5.update_layout(xaxis_rangeslider_visible=True, xaxis_range=range)
fig5.update_layout(legend=dict(
    yanchor="auto",
    y=1.25,
    xanchor="auto",
    x=0.5,
    title=""
))

fig6 = px.pie(df_uyruklar_toplam, values="Toplam", names="Ülke", hole=.3)
fig6.update_traces(textinfo='percent+label', textposition='inside')
fig6.update_layout(showlegend=False)

fig7 = px.bar(df_cinsiyet_yıl_toplam, x="Yıl", y=["Erkek", "Kadın", "Diğer", "Ortak"], barmode="group",
              labels={"value": "Adet", "variable": "Cinsiyet"})
fig7.update_layout(legend=dict(
    title=""
))

fig8 = px.pie(df_cinsiyet_toplam, values="Toplam Satış",
              names="Cinsiyet", hole=.3)
fig8.update_traces(textinfo='percent+label')
fig8.update_layout(showlegend=False)

fig9 = px.choropleth_mapbox(df_2021_eksik, geojson=geojson, color="value",
                            locations="variable", featureidkey="properties.name",
                            center={"lat": 39, "lon": 35.5},
                            opacity=.6,
                            mapbox_style="carto-positron", zoom=4.7,
                            color_continuous_scale=[
                                "Darkgreen", "Yellow", "Red"],
                            labels={"variable": "Şehir", "value": "Satış Adedi"})
fig9.update_layout(margin={"r": 0, "t": 5, "l": 0, "b": 0})

app.layout = dbc.Container(html.Div(children=[
    html.H1(children='Türkiye Konut Satış Verileri - Görselleştirme',
            className="mt-5"),
    html.Hr(),

    html.H3(children="Toplam Konut Satışları"),
    dcc.Graph(
        id='toplam-satislar',
        figure=fig
    ),

    html.Hr(),

    html.H3(children="Satış Durumu ve Satış Şekline Göre Konut Satışları"),

    html.Br(),
    dbc.Row([

        dbc.Col([
            html.H5(children="Satış Durumuna Göre Konut Satışları"),
            dcc.Graph(id='satis-durumu', figure=fig3)
        ], md=6, className="text-center"),

        dbc.Col([
            html.H5(children="Satış Şekline Göre Konut Satışları"),
            dcc.Graph(id='satis-sekli', figure=fig2)
        ], md=6, className="text-center"),
    ], align="center"),

    html.Hr(),

    html.H3(children="Yabancılara Yapılan Konut Satışları"),
    dcc.Graph(
        id='yabancilara',
        figure=fig4
    ),

    dbc.Row([

        dbc.Col([
            html.H5(
                children="Toplam Satışlara Oranla Yabancılara Yapılan Konut Satışları"),
            dcc.Graph(
                id='yabancilar-toplam',
                figure=fig5
            )
        ], md=6, className="text-center"),

        dbc.Col([
            html.H5(
                children="Yabancıların Konut Edinim Oranları (2015 - 2022 Mayıs)"),
            dcc.Graph(id='uyruklar-toplam', figure=fig6)
        ], md=6,  className="text-center"),
    ], align="center"),

    html.Hr(),
    html.H3(children="Cinsiyete Göre Konut Satışları"),
    html.P(children='Grafiklerde "Ortak" olarak isimlendirilen alan edinim sahiplerinin en az bir erkek ve bir kadından oluştuğunu, "Diğer" olarak isimlendirilen alan ise edinimin tüzel kişi veya yabancı kişi tarafından gerçekleştirildiğini ifade etmektedir.'),
    html.Br(),

    dbc.Row([

        dbc.Col([
            html.H5(children="Cinsiyete Göre Konut Edinim Oranları (2014 - 2021)"),
            dcc.Graph(
                id='cinsiyet-toplam',
                figure=fig8
            )
        ], md=6, className="text-center"),

        dbc.Col([
            html.H5(children="Cinsiyet ve Yıllara Göre Konut Edinim Oranları"),
            dcc.Graph(id='cinsiyet-yıllar', figure=fig7)
        ], md=6,  className="text-center"),
    ], align="center"),

    html.Hr(),
    html.H3(children="Harita"),
    html.P(children="Türkiye'de yapılan konut satışlarının %30'undan fazlası İstanbul, Ankara ve İzmir illerinde yapılmaktadır. Haritanın daha anlamlı görülebilmesi için bu üç büyük ile ait rakamlar haritada gösterilmemiştir. (İstanbul: 276.223 Adet, Ankara: 144.104 Adet, İzmir: 86.722 Adet)"),
    html.H5(children="2021 Yılı İl Bazında Yapılan Satışlar"),

    dcc.Graph(
        id='harita',
        figure=fig9,
        className="mb-5"
    ),
]))

if __name__ == '__main__':
    app.run_server()
