import os
import json

import pandas as pd
import plotly.graph_objects as go

import geopandas as gpd

data_path_geo = './'

#### Set travel history ####
df = pd.read_pickle('db_raw.pkl')
df.loc[df['province'].isin(['河北省', '北京市', '天津市', '江苏省']), 'arrived']=True
df.loc[df['province']=='河北省', 'draw_level']='cid'
df.loc[df['city']=='南京市', 'draw_level']='did'


df.loc[df['city'].isin(['石家庄市', '成都市']), 'arrived']=True
df.loc[df['city'].isin(['石家庄市', '成都市']), 'draw_level']='cid'
df.loc[df['city'].isin(['石家庄市', '成都市']), 'label_level']='city'


#### Draw map ####
draw_level={
    "pid":1.0,
    "cid":2.0,
    "did":3.0,
}

colorscale = ["#f7fbff","#9ecae1","#4292c6", "#1361a9","#08306b",]

## Read db and select smallest regions
gpdf = gpd.read_file(os.path.join(data_path_geo,'CN_districts.json'))
gpdf = gpdf.loc[gpdf['childrenNum']==0]
gpdf['val']=0

## Get all regions to be colored
df_grpby = df.loc[df['arrived']].groupby('draw_level')
for v in ['pid', 'cid', 'did']:
    if v not in df['draw_level'].unique(): continue
    items = df_grpby[v].unique()[v]
    # print('level: {}, items: {}'.format(v, items))
    gpdf.loc[gpdf[v].isin(items), ['val']] = draw_level[v]

f = go.Choroplethmapbox(
    geojson=json.loads(gpdf.to_json()),
    locations=gpdf.adcode,
    featureidkey="properties.adcode",
    colorscale=colorscale,
    z=gpdf.val, zmin=0, zmax=4,
    marker_opacity=0.8, marker_line_width=0,
    text = gpdf.name,
)

l = go.Layout(
    mapbox_style="carto-positron",
    mapbox_zoom=2.5,
    mapbox_center = {'lat':38.4872, 'lon':106.2309},
    margin={"r":0, "t":0, "l":0, "b":0}
)

fig = go.Figure(data=f,layout=l)
fig.update_geos(fitbounds="locations", visible=True)

## Get all regions to be dotted
df_grpby = df.loc[df['arrived']].groupby('label_level')
for v in ['province', 'city', 'district']:
    if v not in df['label_level'].unique(): continue
    items = df_grpby[v].unique()[v]
    # print('level: {}, items: {}, '.format(v, items))
    cts = [gpdf.loc[gpdf[v]==item].dissolve().centroid for item in items]
    fig.add_trace(go.Scattermapbox(
        lon=[_.x.values[0] for _ in cts],
        lat=[_.y.values[0] for _ in cts],
        mode="markers",
        marker=go.scattermapbox.Marker(
            size=10,
            opacity=0.8,
            color='red',
        ),
    ))

fig.show()