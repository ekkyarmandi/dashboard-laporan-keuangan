### Import Libraries
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html
import dash

from datetime import datetime, timedelta
from math import ceil
import pandas as pd
import numpy as np

# ignore pandas warnings message
import warnings
warnings.filterwarnings("ignore")

# define dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}] # html meta tags
)

### Data Reading Section
bulan = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "Novermber",
    "Desember"
]
df = pd.read_csv("cash-flow.csv",encoding="utf-8")
dff = df[df.Tipe=="Pengeluaran"]
dff = dff[['Tanggal','Kategori','Out']]
dff['Out'] = dff['Out'].apply(lambda n: n*-1)
dff['date'] = dff['Tanggal'].apply(lambda d: datetime.strptime(d,"%B %d, %Y"))
dff = dff.rename(columns={'Tanggal':'date_str','Out':'out','Kategori':'kategori'})

# fill the missing date with zero
td = dff.date.max() - dff.date.min()
for i in range(td.days+1):
    date = dff.date.min() + timedelta(days=i)
    if date not in dff.date.to_list():
        dff = dff.append({
            'date_str': date.strftime("%B %d, %Y"),
            'date': date,
            'kategori': 'Lainnya',
            'out': 0
        }, ignore_index=True)
dff['month_year'] = dff.date.apply(lambda d: f"{bulan[d.month-1]} {d.year}")
dff = dff.sort_values('date')

### Data Function Processsing Section
def daily_spent(month_year: str or int = None) -> pd.DataFrame:
    '''Group the dataframe by dates and filter it by month_year if specified'''

    data = dff[['date','out','month_year']]
    if month_year in data.month_year.unique():
        data = data[data.month_year==month_year]
    data = data.groupby('date',as_index=False).sum()
    data['idr'] = data.out.apply(lambda n: f"Rp{n:,d}")
    data['date_str'] = data.date.apply(lambda d: d.strftime("%Y-%m-%d"))
    return data

def category_spent(month_year: str or int = None) -> pd.DataFrame:
    '''Group the dataframe by kategori variable and filter it by month_year if specified'''

    data = dff[['kategori','out','month_year']]
    if month_year in data.month_year.unique():
        data = data[data.month_year==month_year]
    data = data.groupby('kategori',as_index=False).sum()
    data['idr'] = data.out.apply(lambda n: f"Rp{n:,d}")
    return data

### Layout Section

# dropdown options
options = ['Semua Bulan']
for my in dff.month_year.unique():
    options.append(my)

# bootstrap container
app.layout = dbc.Container([
    html.H1("Dashboard Laporan Keuangan",className="text-center text-success mt-5"),
    dbc.Col([
        html.Label("Bulan dan tahun"),
        dcc.Dropdown(
            id='month-year-dpdown',
            options=options,
            value='Semua Bulan'
        )
    ],width=3),
    dcc.Graph(id='pie-chart',figure={},style={'height':'500px'}),
    dcc.Graph(id='bar-chart',figure={}),
    dcc.Graph(id='daily-spent',figure={})
])

### Callback Section
@app.callback(
    Output('bar-chart','figure'),
    Input('month-year-dpdown','value')
)
def barchart_category(month_year):
    data = category_spent(month_year)
    data = data.sort_values('out')
    fig = px.bar(
        data,
        x='out',
        y='kategori',
        text='idr',
        labels={"out":"Pengeluaran"},
        title="Pengeluara Berdasarkan Kategori"
    )
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('pie-chart','figure'),
    Input('month-year-dpdown','value')
)
def piechart_category(month_year):
    data = category_spent(month_year)
    fig = px.pie(
        data,
        values='out',
        names='kategori',
        title="Pie Chart Kategori Pengeluaran"
    )
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('daily-spent','figure'),
    Input('month-year-dpdown','value')
)
def daily_spent_barchart(month_year):
    data = daily_spent(month_year)

    # customize y axis
    value = data.out.max()/1e6
    value = int(ceil(value)*1e6)
    n = int(value/5e5)
    values = [i*5e5 for i in range(n)]
    value_str = [f"Rp{int(i):,d}" for i in values]

    # plot
    fig = px.bar(
        data,
        x='date',
        y='out',
        text='idr',
        labels={'out':'Pengeluaran','date':'Tanggal'},
        title='Pengeluaran Harian'
    )
    fig.update_yaxes(tickvals=values,ticktext=value_str)
    fig.update_xaxes(tickvals=data.date,ticktext=data.date_str)
    fig.update_traces(marker_color="orange")
    fig.update_layout(title_x=0.5)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True,port=5500)