import pandas as pd
import plotly.express as px
import dash
from dash import dash_table


df = pd.read_csv("data/data.csv")
del df['Unnamed: 0']
df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'], errors='coerce')
df.head()
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

df['week'] = df['Transaction_Date'].dt.isocalendar().week
df_semaine = df.groupby('week')['Ca_Total'].sum()
fig_semaine = px.line(df_semaine, x=df_semaine.index, y='Ca_Total', title='Chiffre d\'affaires par semaine')



top10 = df.groupby('Product_Category')['Quantity'].sum().nlargest(10).index
df_bar = df[df['Product_Category'].isin(top10)]
df_bar = df_bar.groupby(['Product_Category', 'Gender'])['Quantity'].sum().reset_index()
fig_bar = px.bar(df_bar, x='Quantity', y='Product_Category', color='Gender',orientation='h', title='Quantité par catégorie de produit et genre', barmode='group')

df_table = df.sort_values('Transaction_Date', ascending=False).head(100)
df_table = df_table[['Transaction_Date', 'Gender', 'Location', 'Product_Category', 'Quantity', 'Avg_Price', 'Discount_pct']]
table = dash_table.DataTable(
    data=df_table.to_dict('records'),
    columns=[{"name": i, "id": i} for i in df_table.columns]
)