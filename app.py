import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash import dash_table

df = pd.read_csv("data/data.csv")

# KPI
del df['Unnamed: 0']
df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'], errors='coerce')
df = df.dropna()
df['Ca_Total']= df['Avg_Price'] * ((100 - df['Discount_pct'])/100) * df['Quantity']
df_dec=df[df['Month'] == 12]
df_nov=df[df['Month'] == 11]
ca_dec= df_dec['Ca_Total'].sum()
ca_nov= df_nov['Ca_Total'].sum()
variation_ca = (ca_dec - ca_nov) 
qty_dec=df_dec['Quantity'].sum()
qty_nov=df_nov['Quantity'].sum()  
variation_qty = (qty_dec - qty_nov)

# Graphique semaine
mois = {1:'Jan', 2:'Fév', 3:'Mar', 4:'Avr', 5:'Mai', 6:'Jun',
        7:'Jul', 8:'Aoû', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Déc'}
df_semaine = df.groupby('Month')['Ca_Total'].sum().reset_index()
df_semaine['Mois'] = df_semaine['Month'].map(mois)
fig_semaine = px.line(df_semaine, x='Mois', y='Ca_Total')
fig_semaine.update_layout(
    title={'text': 'Évolution du CA par mois', 'font': {'size': 13}},
    margin={'t': 30, 'b': 10, 'l': 10, 'r': 5},
    height=250
)

# Graphique barres
top10 = df.groupby('Product_Category')['Quantity'].sum().nlargest(10).index
df_bar = df[df['Product_Category'].isin(top10)]
df_bar = df_bar.groupby(['Product_Category', 'Gender'])['Quantity'].sum().reset_index()
fig_bar = px.bar(df_bar, x='Quantity', y='Product_Category', color='Gender',orientation='h', title='Quantité par catégorie de produit et genre', barmode='group')
fig_bar.update_yaxes(
    tickfont={'size': 10}, 
    title=None
)
fig_bar.update_xaxes(
    title=None
)
fig_bar.update_layout(
    title={'text': 'Quantité par catégorie', 'font': {'size': 12}},
    margin={'t': 50, 'b': 10, 'l': 10, 'r': 10}
)


# Table
df_table = df.sort_values('Transaction_Date', ascending=False).head(100)
df_table = df_table[['Transaction_Date', 'Gender', 'Location', 'Product_Category', 'Quantity', 'Avg_Price', 'Discount_pct']]
table = dash_table.DataTable(
    id='table',
    data=df_table.to_dict('records'),
    columns=[{"name": i, "id": i} for i in df_table.columns],
    page_size=10,
    page_action='native',
    page_current=0,
    style_table={'overflowX': 'auto'},
    style_cell={'textAlign': 'left', 'padding': '5px', 'fontSize': '12px'},
    style_header={'backgroundColor': '#f4f6f9', 'fontWeight': 'bold'},
)

app= dash.Dash(__name__)
def layout():
    return html.Div([
        # Header
        html.Div([
            html.H2("Dashboard Ecap", style={'color': 'white', 'fontFamily': 'Arial', 'margin': '0'}),
            dcc.Dropdown(
                id='filtre_localisation',
                options=[{'label': loc, 'value': loc} for loc in df['Location'].unique()],
                value=None,
                placeholder="Filtrer par localisation",
                style={'width': '300px', 'fontFamily': 'Arial'}
            )
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
                  'padding': '10px 30px', 'backgroundColor': "#3168c7"}),

        html.Div([
            # Colonne gauche
            html.Div([
                # KPIs
                html.Div([
                    html.Div([
                        html.P("Decembre - CA", style={'color': '#888', 'fontSize': '12px', 'margin': '0'}),
                        html.H2(id='ca-dec', children=f"{ca_dec/1000:.1f}K",
                                style={'fontSize': '36px', 'margin': '0'}),
                        html.P(id='variation-ca',
                               children=f"{'▲' if variation_ca > 0 else '▼'} {variation_ca/1000:+.1f}K",
                               style={'color': 'green' if variation_ca > 0 else 'red', 'fontSize': '16px', 'margin': '0'})
                    ], style={'flex': '1', 'backgroundColor': 'white', 'padding': '10px 15px',
                              'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'textAlign': 'center'}),
                    html.Div([
                        html.P("Decembre - Quantité", style={'color': '#888', 'fontSize': '12px', 'margin': '0'}),
                        html.H2(id='qty-dec', children=f"{int(qty_dec)}",
                                style={'fontSize': '36px', 'margin': '0'}),
                        html.P(id='variation-qty',
                               children=f"{'▲' if variation_qty > 0 else '▼'} {int(variation_qty)}",
                               style={'color': 'green' if variation_qty > 0 else 'red', 'fontSize': '16px', 'margin': '0'})
                    ], style={'flex': '1', 'backgroundColor': 'white', 'padding': '10px 15px',
                              'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)', 'textAlign': 'center'})
                ], style={'display': 'flex', 'gap': '15px', 'marginBottom': '15px'}),
                # Bar chart
                dcc.Graph(id='graph-bar', figure=fig_bar,
                          style={'flex': '1', 'minHeight': '300px'},
                          config={'responsive': True})
            ], style={'width': '40%', 'padding': '15px', 'boxSizing': 'border-box',
                      'display': 'flex', 'flexDirection': 'column'}),

            # Colonne droite
            html.Div([
                dcc.Graph(id='graph-semaine', figure=fig_semaine,
                          style={'height': '280px'},
                          config={'responsive': True}),
                html.Div([table], style={'maxHeight': '250px', 'overflowY': 'auto'})
            ], style={'width': '60%', 'padding': '15px', 'boxSizing': 'border-box'})

        ], style={'display': 'flex', 'backgroundColor': '#f4f6f9',
                  'height': 'calc(100vh - 60px)',
                  'overflow': 'hidden'})

    ], style={'margin': '0', 'padding': '0', 'fontFamily': 'Arial'})



@app.callback(
    [dash.dependencies.Output('ca-dec', 'children'),
     dash.dependencies.Output('variation-ca', 'children'),
     dash.dependencies.Output('qty-dec', 'children'),
     dash.dependencies.Output('variation-qty', 'children'),
     dash.dependencies.Output('graph-semaine', 'figure'),
     dash.dependencies.Output('graph-bar', 'figure'),
     dash.dependencies.Output('table', 'data'),
     dash.dependencies.Output('variation-ca', 'style'),
     dash.dependencies.Output('variation-qty', 'style')],
    [dash.dependencies.Input('filtre_localisation', 'value')]
)
def update_dashboard(loc):
    if loc:
        df_filtre = df[df['Location'] == loc]
    else:
        df_filtre = df

    ca_dec_filtre = df_filtre[df_filtre['Month'] == 12]['Ca_Total'].sum()
    ca_nov_filtre = df_filtre[df_filtre['Month'] == 11]['Ca_Total'].sum()
    variation_ca_filtre = ca_dec_filtre - ca_nov_filtre

    qty_dec_filtre = df_filtre[df_filtre['Month'] == 12]['Quantity'].sum()
    qty_nov_filtre = df_filtre[df_filtre['Month'] == 11]['Quantity'].sum()
    variation_qty_filtre = qty_dec_filtre - qty_nov_filtre

    df_semaine_filtre = df_filtre.groupby('Month')['Ca_Total'].sum().reset_index()
    df_semaine_filtre['Mois'] = df_semaine_filtre['Month'].map(mois)
    fig_semaine_filtre = px.line(df_semaine_filtre, x='Mois', y='Ca_Total')
    fig_semaine_filtre.update_layout(
        title={'text': 'Évolution du CA par mois', 'font': {'size': 12}},
        margin={'t': 30, 'b': 10, 'l': 10, 'r': 5},
        height=250
    )

    top10_filtre = df_filtre.groupby('Product_Category')['Quantity'].sum().nlargest(10).index
    df_bar_filtre = df_filtre[df_filtre['Product_Category'].isin(top10_filtre)]
    df_bar_filtre = df_bar_filtre.groupby(['Product_Category', 'Gender'])['Quantity'].sum().reset_index()
    fig_bar_filtre = px.bar(df_bar_filtre, x='Quantity', y='Product_Category', color='Gender',orientation='h', title='Quantité par catégorie de produit et genre', barmode='group')
    fig_bar_filtre.update_yaxes(
        tickangle=0,
        tickfont={'size': 10},
        title=None
    )
    fig_bar_filtre.update_xaxes(
        title=None
    )
    fig_bar_filtre.update_layout(
        title={'text': 'Quantité par catégorie', 'font': {'size': 12}},
        margin={'t': 50, 'b': 10, 'l': 10, 'r': 10}
    )
    return (
        f"{ca_dec_filtre/1000:.1f}K",
        f"{'▲' if variation_ca_filtre > 0 else '▼'} {variation_ca_filtre/1000:+.1f}K",
        f"{int(qty_dec_filtre)}",
        f"{'▲' if variation_qty_filtre > 0 else '▼'} {int(variation_qty_filtre)}",
        fig_semaine_filtre,
        fig_bar_filtre,
        df_filtre.sort_values('Transaction_Date', ascending=False).head(100).to_dict('records'),
        {'color': 'green' if variation_ca_filtre > 0 else 'red', 'fontSize': '16px', 'margin': '0'},
        {'color': 'green' if variation_qty_filtre > 0 else 'red', 'fontSize': '16px', 'margin': '0'}
    )
app.layout = layout
server = app.server

if __name__ == '__main__':
    app.run(debug=False)  