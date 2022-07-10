### Starting Section
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}]
)

### Data Reading Section
df = pd.read_csv("cash-flow.csv",encoding="utf-8")

### Data Function Processsing Section
def category(month_year: str or int) -> pd.DataFrame:
    '''Return spent dataframe based on category'''

    columns = ['Out','Kategori','Tanggal']
    dff = df[df['Tipe']=="Pengeluaran"]
    dff = dff[columns]
    dff['Out'] = dff['Out'].apply(lambda d: d*-1 if d < 0 else d)
    dff['Tanggal'] = dff['Tanggal'].apply(lambda x: datetime.strptime(x,"%B %d, %Y"))
    dff['Month_Year'] = dff['Tanggal'].apply(lambda date: f"{date.month_name()} {date.year}")
    if month_year in dff.Month_Year.unique():
        dff = dff[dff['Month_Year']==month_year]
    min_date, max_date = dff['Tanggal'].min(), dff['Tanggal'].max()
    dff = dff[['Kategori','Out']].groupby('Kategori',as_index=False).sum()
    dff = dff.sort_values('Out')
    return dff,(min_date,max_date)

### Layout Section
app.layout = dbc.Container([
    html.H1("Dashboard Laporan Keuangan",className="text-center text-success mt-5"),
    dbc.Col([
        html.Label("Bulan dan tahun"),
        dcc.Dropdown(
            id='month-year-dpdown',
            options=['Sepanjang masa','May 2022','June 2022','July 2022'],
            value='Sepanjang masa'
        )
    ],width=3),
    dcc.Graph(id='pie-fig',figure={},style={'height':'500px'}),
    dcc.Graph(id='bar-fig',figure={})
])

### Callback Section
@app.callback(
    Output('bar-fig','figure'),
    Input('month-year-dpdown','value')
)
def barchart_category(value):
    dff,min_max_date = category(value)
    min_date, max_date = min_max_date
    barfig = px.bar(dff, x='Out',y='Kategori',labels={"Out":"Pengeluaran"},title="Kategori Pengeluaran " + value)
    return barfig

@app.callback(
    Output('pie-fig','figure'),
    Input('month-year-dpdown','value')
)
def piechart_category(value):
    dff,_ = category(value)
    fig = px.pie(dff, values='Out',names='Kategori',title="Kue Pengeluaran " + value)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True,port=5500)