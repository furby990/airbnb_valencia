"""
app.py
======
Dashboard interactivo Valencia Airbnb Investment Intelligence
Ejecutar: python dashboard/app.py
Abrir:    http://127.0.0.1:8050
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, dash_table
import json
from pathlib import Path
import sys
import warnings

warnings.filterwarnings('ignore')

# ── Paths ─────────────────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import (
    SCORE_WEIGHTS, HIGH_SEASON_MONTHS,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT,
    COLOR_GOOD, COLOR_WARN, COLOR_BAD
)

PROCESSED_PATH = PROJECT_ROOT / 'data' / 'processed'
DATA_RAW_PATH  = PROJECT_ROOT / 'data' / 'raw'

# ── Load data ─────────────────────────────────────────────────
df       = pd.read_csv(PROCESSED_PATH / 'listings_clean.csv',   low_memory=False)
df_score = pd.read_csv(PROCESSED_PATH / 'investment_score.csv', low_memory=False)
df_seas  = pd.read_csv(PROCESSED_PATH / 'seasonality_by_hood.csv', index_col=0)
df_rev   = pd.read_csv(PROCESSED_PATH / 'reviews_clean.csv',    low_memory=False)

# GeoJSON
try:
    with open(DATA_RAW_PATH / 'neighbourhoods.geojson', 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    HAS_GEOJSON = True
except:
    HAS_GEOJSON = False

# Prep
df['superhost_num'] = pd.to_numeric(
    df['host_is_superhost'].map({True:1, False:0, 't':1, 'f':0}), errors='coerce'
)
df['host_is_superhost_bool'] = df['superhost_num'] == 1
hood_col = 'neighbourhood_group_cleansed'
df_score_indexed = df_score.set_index(
    df_score.columns[0] if df_score.columns[0] != 'Unnamed: 0' else df_score.columns[1]
) if 'neighbourhood_group_cleansed' not in df_score.columns else df_score.set_index('neighbourhood_group_cleansed')

# ── Color maps ────────────────────────────────────────────────
COLORS = {
    'bg':       '#F8F9FA',
    'card':     '#FFFFFF',
    'primary':  COLOR_PRIMARY,
    'accent':   COLOR_ACCENT,
    'text':     '#2C3E50',
    'muted':    '#7F8C8D',
    'border':   '#E9ECEF',
}

# ── Helpers ───────────────────────────────────────────────────
def kpi_card(title, value, subtitle='', color=COLOR_PRIMARY):
    return html.Div([
        html.P(title, style={'color': COLORS['muted'], 'fontSize': '12px',
                             'marginBottom': '4px', 'fontWeight': '500',
                             'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
        html.H3(value, style={'color': color, 'margin': '0',
                              'fontSize': '28px', 'fontWeight': '700'}),
        html.P(subtitle, style={'color': COLORS['muted'], 'fontSize': '12px',
                                'margin': '4px 0 0 0'}),
    ], style={
        'background': COLORS['card'], 'borderRadius': '12px',
        'padding': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.06)',
        'borderLeft': f'4px solid {color}', 'flex': '1', 'minWidth': '180px'
    })

# ── App ───────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    title='Valencia Airbnb Investment Intelligence',
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)

neighbourhoods = sorted(df[hood_col].dropna().unique().tolist())
room_types     = sorted(df['room_type'].unique().tolist())
segments       = ['Amateur', 'Semi-pro', 'Profesional']

# ── Layout ────────────────────────────────────────────────────
app.layout = html.Div(style={'backgroundColor': COLORS['bg'], 'minHeight': '100vh',
                              'fontFamily': "'Segoe UI', Arial, sans-serif"}, children=[

    # Header
    html.Div([
        html.Div([
            html.H1('Valencia Airbnb Investment Intelligence',
                    style={'color': 'white', 'margin': '0', 'fontSize': '24px', 'fontWeight': '700'}),
            html.P('Short-term rental market analysis · Where, when and how to invest',
                   style={'color': 'rgba(255,255,255,0.8)', 'margin': '4px 0 0 0', 'fontSize': '13px'}),
        ]),
        html.Div([
            html.Span('Data: Inside Airbnb Valencia · Sep 2025',
                      style={'color': 'rgba(255,255,255,0.7)', 'fontSize': '12px'}),
        ]),
    ], style={
        'background': f'linear-gradient(135deg, {COLOR_PRIMARY}, #C0392B)',
        'padding': '20px 32px', 'display': 'flex',
        'justifyContent': 'space-between', 'alignItems': 'center'
    }),

    # Tabs
    dcc.Tabs(id='tabs', value='tab-score', style={'margin': '0'},
             colors={'border': COLORS['border'], 'primary': COLOR_PRIMARY,
                     'background': COLORS['bg']},
    children=[

        # ── TAB 1: INVESTMENT SCORE ──────────────────────────
        dcc.Tab(label='Investment Score', value='tab-score',
                style={'padding': '12px 20px'}, children=[
            html.Div(style={'padding': '24px 32px'}, children=[

                # KPIs
                html.Div([
                    kpi_card('Total Listings', f"{len(df):,}", '7,780 active properties'),
                    kpi_card('Median Price', f"{df['price_eur'].median():.0f} EUR/night",
                             'Valencia market', COLOR_ACCENT),
                    kpi_card('Median Revenue', f"{df['estimated_revenue_l365d'].median():,.0f} EUR/year",
                             'Per active listing', COLOR_GOOD),
                    kpi_card('% Superhosts', f"{df['superhost_num'].mean()*100:.1f}%",
                             'Of all hosts', COLOR_WARN),
                    kpi_card('Neighbourhoods', '19', 'Analyzed', COLOR_BAD),
                ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '24px',
                          'flexWrap': 'wrap'}),

                # Score chart + table
                html.Div([
                    html.Div([
                        dcc.Graph(id='score-chart', style={'height': '520px'}),
                    ], style={'flex': '1', 'background': COLORS['card'],
                              'borderRadius': '12px', 'padding': '20px',
                              'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),

                    html.Div([
                        html.H4('Investment Ranking', style={'color': COLORS['text'],
                                'margin': '0 0 16px 0', 'fontSize': '16px'}),
                        dash_table.DataTable(
                            id='score-table',
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', 'padding': '10px 12px',
                                       'fontSize': '13px', 'fontFamily': 'inherit',
                                       'border': f'1px solid {COLORS["border"]}'},
                            style_header={'backgroundColor': COLOR_PRIMARY, 'color': 'white',
                                         'fontWeight': '600', 'fontSize': '12px'},
                            style_data_conditional=[
                                {'if': {'row_index': 0},
                                 'backgroundColor': '#FEF9E7', 'fontWeight': '600'},
                                {'if': {'row_index': 1},
                                 'backgroundColor': '#F0F3F4'},
                                {'if': {'row_index': 2},
                                 'backgroundColor': '#F9F9F9'},
                            ],
                        ),
                    ], style={'width': '360px', 'background': COLORS['card'],
                              'borderRadius': '12px', 'padding': '20px',
                              'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                ], style={'display': 'flex', 'gap': '20px'}),
            ]),
        ]),

        # ── TAB 2: MERCADO ────────────────────────────────────
        dcc.Tab(label='Market by Neighbourhood', value='tab-market',
                style={'padding': '12px 20px'}, children=[
            html.Div(style={'padding': '24px 32px'}, children=[

                # Filters
                html.Div([
                    html.Div([
                        html.Label('Room type', style={'fontSize': '13px',
                                   'fontWeight': '600', 'color': COLORS['text']}),
                        dcc.Dropdown(id='filter-room',
                            options=[{'label': r, 'value': r} for r in room_types],
                            value=[], multi=True,
                            placeholder='All room types',
                            style={'fontSize': '13px'}),
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Label('Neighbourhood (multi-select to compare)', style={'fontSize': '13px',
                                   'fontWeight': '600', 'color': COLORS['text']}),
                        dcc.Dropdown(id='filter-hood',
                            options=[{'label': n, 'value': n} for n in neighbourhoods],
                            value=[], multi=True,
                            placeholder='All neighbourhoods (select 2+ to compare)',
                            style={'fontSize': '13px'}),
                    ], style={'flex': '2'}),
                    html.Div([
                        html.Label('Host segment', style={'fontSize': '13px',
                                   'fontWeight': '600', 'color': COLORS['text']}),
                        dcc.Dropdown(id='filter-segment',
                            options=[{'label': s, 'value': s} for s in segments],
                            value=[], multi=True,
                            placeholder='All segments',
                            style={'fontSize': '13px'}),
                    ], style={'flex': '1'}),
                ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '20px',
                          'background': COLORS['card'], 'borderRadius': '12px',
                          'padding': '16px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),

                # Charts row 1
                html.Div([
                    html.Div([dcc.Graph(id='price-bar')],
                             style={'flex': '1', 'background': COLORS['card'],
                                    'borderRadius': '12px', 'padding': '16px',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                    html.Div([dcc.Graph(id='revenue-bar')],
                             style={'flex': '1', 'background': COLORS['card'],
                                    'borderRadius': '12px', 'padding': '16px',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '16px'}),

                # Charts row 2
                html.Div([
                    html.Div([dcc.Graph(id='scatter-market')],
                             style={'flex': '2', 'background': COLORS['card'],
                                    'borderRadius': '12px', 'padding': '16px',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                    html.Div([dcc.Graph(id='room-pie')],
                             style={'flex': '1', 'background': COLORS['card'],
                                    'borderRadius': '12px', 'padding': '16px',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                ], style={'display': 'flex', 'gap': '16px'}),
            ]),
        ]),

        # ── TAB 3: ESTACIONALIDAD ─────────────────────────────
        dcc.Tab(label='Seasonality', value='tab-season',
                style={'padding': '12px 20px'}, children=[
            html.Div(style={'padding': '24px 32px'}, children=[

                html.Div([
                    html.Label('Select neighbourhoods (multi-select to compare)', style={'fontSize': '13px',
                               'fontWeight': '600', 'color': COLORS['text']}),
                    dcc.Dropdown(id='season-hood',
                        options=[{'label': n, 'value': n} for n in neighbourhoods],
                        value=[], multi=True,
                        placeholder='All neighbourhoods (select 2+ to compare lines)',
                        style={'fontSize': '13px', 'maxWidth': '600px'}),
                ], style={'marginBottom': '20px', 'background': COLORS['card'],
                          'borderRadius': '12px', 'padding': '16px',
                          'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),

                html.Div([
                    html.Div([dcc.Graph(id='season-chart', style={'height': '400px'})],
                             style={'flex': '2', 'background': COLORS['card'],
                                    'borderRadius': '12px', 'padding': '16px',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                    html.Div([dcc.Graph(id='demand-trend', style={'height': '400px'})],
                             style={'flex': '2', 'background': COLORS['card'],
                                    'borderRadius': '12px', 'padding': '16px',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                ], style={'display': 'flex', 'gap': '16px'}),
            ]),
        ]),

        # ── TAB 4: HOSTS ──────────────────────────────────────
        dcc.Tab(label='Host Analysis', value='tab-hosts',
                style={'padding': '12px 20px'}, children=[
            html.Div(style={'padding': '24px 32px'}, children=[

                html.Div([
                    html.Div([dcc.Graph(id='host-segment-chart', style={'height': '380px'})],
                             style={'flex': '1', 'background': COLORS['card'],
                                    'borderRadius': '12px', 'padding': '16px',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                    html.Div([dcc.Graph(id='superhost-chart', style={'height': '380px'})],
                             style={'flex': '1', 'background': COLORS['card'],
                                    'borderRadius': '12px', 'padding': '16px',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '16px'}),

                html.Div([
                    html.Div([dcc.Graph(id='host-revenue-dist', style={'height': '380px'})],
                             style={'flex': '2', 'background': COLORS['card'],
                                    'borderRadius': '12px', 'padding': '16px',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                    html.Div([
                        html.H4('Investor Recommendations',
                                style={'color': COLORS['text'], 'margin': '0 0 16px 0'}),
                        html.Div([
                            html.Div([
                                html.Span('1', style={'background': COLOR_PRIMARY, 'color': 'white',
                                                      'borderRadius': '50%', 'width': '28px', 'height': '28px',
                                                      'display': 'inline-flex', 'alignItems': 'center',
                                                      'justifyContent': 'center', 'fontWeight': '700',
                                                      'marginRight': '12px', 'flexShrink': '0'}),
                                html.Div([
                                    html.Strong('Becoming a Superhost is priority #1',
                                                style={'fontSize': '14px', 'color': COLORS['text']}),
                                    html.P('+386% revenue vs regular hosts',
                                           style={'margin': '2px 0 0 0', 'fontSize': '12px',
                                                  'color': COLORS['muted']}),
                                ]),
                            ], style={'display': 'flex', 'alignItems': 'center',
                                      'marginBottom': '16px', 'padding': '12px',
                                      'background': '#FEF9E7', 'borderRadius': '8px'}),

                            html.Div([
                                html.Span('2', style={'background': COLOR_ACCENT, 'color': 'white',
                                                      'borderRadius': '50%', 'width': '28px', 'height': '28px',
                                                      'display': 'inline-flex', 'alignItems': 'center',
                                                      'justifyContent': 'center', 'fontWeight': '700',
                                                      'marginRight': '12px', 'flexShrink': '0'}),
                                html.Div([
                                    html.Strong('Enable Instant Booking',
                                                style={'fontSize': '14px', 'color': COLORS['text']}),
                                    html.P('Top 10% earners use it more',
                                           style={'margin': '2px 0 0 0', 'fontSize': '12px',
                                                  'color': COLORS['muted']}),
                                ]),
                            ], style={'display': 'flex', 'alignItems': 'center',
                                      'marginBottom': '16px', 'padding': '12px',
                                      'background': '#EBF5FB', 'borderRadius': '8px'}),

                            html.Div([
                                html.Span('3', style={'background': COLOR_GOOD, 'color': 'white',
                                                      'borderRadius': '50%', 'width': '28px', 'height': '28px',
                                                      'display': 'inline-flex', 'alignItems': 'center',
                                                      'justifyContent': 'center', 'fontWeight': '700',
                                                      'marginRight': '12px', 'flexShrink': '0'}),
                                html.Div([
                                    html.Strong('Prioritize capacity for 4+ guests',
                                                style={'fontSize': '14px', 'color': COLORS['text']}),
                                    html.P('Strongest correlation with price (rho=0.62)',
                                           style={'margin': '2px 0 0 0', 'fontSize': '12px',
                                                  'color': COLORS['muted']}),
                                ]),
                            ], style={'display': 'flex', 'alignItems': 'center',
                                      'marginBottom': '16px', 'padding': '12px',
                                      'background': '#EAFAF1', 'borderRadius': '8px'}),

                            html.Div([
                                html.Span('4', style={'background': COLOR_WARN, 'color': 'white',
                                                      'borderRadius': '50%', 'width': '28px', 'height': '28px',
                                                      'display': 'inline-flex', 'alignItems': 'center',
                                                      'justifyContent': 'center', 'fontWeight': '700',
                                                      'marginRight': '12px', 'flexShrink': '0'}),
                                html.Div([
                                    html.Strong('Invest in Ciutat Vella or Eixample',
                                                style={'fontSize': '14px', 'color': COLORS['text']}),
                                    html.P('Scores 74.5 and 68.9 - top 2 of the ranking',
                                           style={'margin': '2px 0 0 0', 'fontSize': '12px',
                                                  'color': COLORS['muted']}),
                                ]),
                            ], style={'display': 'flex', 'alignItems': 'center',
                                      'padding': '12px', 'background': '#FEF5E7',
                                      'borderRadius': '8px'}),
                        ]),
                    ], style={'flex': '1', 'background': COLORS['card'],
                              'borderRadius': '12px', 'padding': '20px',
                              'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                ], style={'display': 'flex', 'gap': '16px'}),
            ]),
        ]),
    ]),

    # Footer
    html.Div([
        html.P('Valencia Airbnb Investment Intelligence · Ironhack Data Analytics Bootcamp · Inside Airbnb Sep 2025',
               style={'color': COLORS['muted'], 'fontSize': '12px', 'margin': '0', 'textAlign': 'center'}),
    ], style={'padding': '16px 32px', 'borderTop': f'1px solid {COLORS["border"]}',
              'background': COLORS['card'], 'marginTop': '8px'}),
])


# ══════════════════════════════════════════════════════════════
# CALLBACKS
# ══════════════════════════════════════════════════════════════

# ── Tab 1: Score chart + table ────────────────────────────────
@app.callback(
    [Output('score-chart', 'figure'),
     Output('score-table', 'data'),
     Output('score-table', 'columns')],
    Input('tabs', 'value')
)
def update_score_tab(tab):
    score_data = df.groupby(hood_col).agg(
        investment_score = ('estimated_revenue_l365d', lambda x: x.median()),
        median_revenue   = ('estimated_revenue_l365d', 'median'),
        median_price     = ('price_eur', 'median'),
        median_occupancy = ('estimated_occupancy_l365d', 'median'),
        n_listings       = ('id', 'count'),
    ).reset_index()

    # Use pre-calculated scores if available
    if 'investment_score' in df_score.columns:
        hood_col_name = df_score.columns[0]
        score_data = df_score.copy()
        if hood_col_name != hood_col:
            score_data = score_data.rename(columns={hood_col_name: hood_col})
        score_data = score_data.sort_values('investment_score', ascending=True)
    else:
        score_data = score_data.sort_values('median_revenue', ascending=True)

    score_col = 'investment_score' if 'investment_score' in score_data.columns else 'median_revenue'

    fig = go.Figure()
    colors_bar = [
        f'rgba(231,76,60,{0.5 + 0.5*v/score_data[score_col].max()})'
        for v in score_data[score_col]
    ]
    fig.add_trace(go.Bar(
        y=score_data[hood_col],
        x=score_data[score_col],
        orientation='h',
        marker_color=colors_bar,
        text=[f'{v:.1f}' for v in score_data[score_col]],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<br><extra></extra>',
    ))
    fig.update_layout(
        title={'text': 'Investment Score by Neighbourhood', 'font': {'size': 16, 'color': '#2C3E50'}},
        xaxis_title='Investment Score (0-100)',
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=20, r=60, t=50, b=20),
        xaxis=dict(gridcolor='#F0F0F0'),
        font=dict(family='Segoe UI, Arial'),
    )

    table_data = score_data.sort_values(score_col, ascending=False).head(19)
    cols_show  = [hood_col, score_col, 'median_revenue', 'median_occupancy', 'median_price', 'n_listings']
    cols_show  = [c for c in cols_show if c in table_data.columns]
    table_data = table_data[cols_show].round(1)
    table_data.columns = ['Neighbourhood', 'Score', 'Revenue EUR', 'Occupancy', 'Price EUR', 'N Listings'][:len(cols_show)]

    columns = [{'name': c, 'id': c} for c in table_data.columns]
    return fig, table_data.to_dict('records'), columns


# ── Tab 2: Market charts ──────────────────────────────────────
@app.callback(
    [Output('price-bar', 'figure'),
     Output('revenue-bar', 'figure'),
     Output('scatter-market', 'figure'),
     Output('room-pie', 'figure')],
    [Input('filter-room', 'value'),
     Input('filter-hood', 'value'),
     Input('filter-segment', 'value')]
)
def update_market(room, hood, segment):
    dff = df.copy()
    # Multi-select: lista vacia o None = todos
    if room:
        room_list = room if isinstance(room, list) else [room]
        dff = dff[dff['room_type'].isin(room_list)]
    if hood:
        hood_list = hood if isinstance(hood, list) else [hood]
        dff = dff[dff[hood_col].isin(hood_list)]
    if segment:
        seg_list = segment if isinstance(segment, list) else [segment]
        dff = dff[dff['host_segment'].isin(seg_list)]

    # Price bar
    price_by_hood = dff.groupby(hood_col)['price_eur'].median().sort_values(ascending=False)
    fig_price = px.bar(
        x=price_by_hood.index, y=price_by_hood.values,
        color=price_by_hood.values, color_continuous_scale='RdYlGn',
        title='Median Price by Neighbourhood (EUR/night)',
        labels={'x': '', 'y': 'EUR/night', 'color': 'EUR'},
    )
    fig_price.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=20, r=20, t=50, b=80),
        xaxis_tickangle=-45, showlegend=False,
        coloraxis_showscale=False,
        font=dict(family='Segoe UI, Arial'),
    )

    # Revenue bar
    rev_by_hood = dff.groupby(hood_col)['estimated_revenue_l365d'].median().sort_values(ascending=False)
    fig_rev = px.bar(
        x=rev_by_hood.index, y=rev_by_hood.values,
        color=rev_by_hood.values, color_continuous_scale='RdYlGn',
        title='Median Revenue by Neighbourhood (EUR/year)',
        labels={'x': '', 'y': 'EUR/year', 'color': 'EUR'},
    )
    fig_rev.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=20, r=20, t=50, b=80),
        xaxis_tickangle=-45, showlegend=False,
        coloraxis_showscale=False,
        font=dict(family='Segoe UI, Arial'),
    )

    # Scatter
    scatter_data = dff.groupby(hood_col).agg(
        median_price    = ('price_eur', 'median'),
        median_revenue  = ('estimated_revenue_l365d', 'median'),
        median_occ      = ('estimated_occupancy_l365d', 'median'),
        n               = ('id', 'count'),
    ).reset_index()
    fig_scatter = px.scatter(
        scatter_data,
        x='median_price', y='median_revenue',
        size='n', color='median_occ',
        hover_name=hood_col,
        color_continuous_scale='RdYlGn',
        title='Price vs Revenue by Neighbourhood',
        labels={'median_price': 'Median price (EUR/night)',
                'median_revenue': 'Median revenue (EUR/year)',
                'median_occ': 'Occupancy (nights)',
                'n': 'N Listings'},
        size_max=40,
    )
    fig_scatter.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial'),
    )

    # Pie
    room_counts = dff['room_type'].value_counts()
    fig_pie = px.pie(
        values=room_counts.values, names=room_counts.index,
        title='Room Type Distribution',
        color_discrete_sequence=[COLOR_PRIMARY, COLOR_ACCENT, COLOR_SECONDARY, COLOR_WARN],
    )
    fig_pie.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial'),
        paper_bgcolor='white',
    )

    return fig_price, fig_rev, fig_scatter, fig_pie


# ── Tab 3: Seasonality ────────────────────────────────────────
@app.callback(
    [Output('season-chart', 'figure'),
     Output('demand-trend', 'figure')],
    Input('season-hood', 'value')
)
def update_seasonality(hood):
    MONTH_NAMES = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',
                   7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}
    MONTH_ORDER = list(MONTH_NAMES.values())

    rev_data = df_rev.merge(
        df[['id', hood_col]].rename(columns={'id': 'listing_id'}),
        on='listing_id', how='left'
    )

    hood_list = hood if isinstance(hood, list) else ([hood] if hood and hood != 'all' else [])

    fig_season = go.Figure()
    PALETTE = [COLOR_PRIMARY, COLOR_ACCENT, COLOR_GOOD, COLOR_WARN,
               COLOR_SECONDARY, COLOR_BAD, '#9B59B6', '#16A085']

    if len(hood_list) >= 2:
        # Comparativa: una linea por barrio seleccionado
        for i, h in enumerate(hood_list):
            sub = rev_data[rev_data[hood_col] == h]
            monthly_h = sub.groupby('month').size().reindex(range(1, 13), fill_value=0)
            fig_season.add_trace(go.Scatter(
                x=[MONTH_NAMES[m] for m in monthly_h.index],
                y=monthly_h.values,
                mode='lines+markers',
                name=h,
                line=dict(color=PALETTE[i % len(PALETTE)], width=2.5),
                marker=dict(size=7),
                hovertemplate=h + ' - %{x}: %{y:,} reviews<extra></extra>',
            ))
        title_season = f'Monthly demand compared ({len(hood_list)} neighbourhoods)'
    else:
        # Un barrio o todos: barras
        if len(hood_list) == 1:
            rev_data = rev_data[rev_data[hood_col] == hood_list[0]]
            title_season = f'Monthly demand - {hood_list[0]}'
        else:
            title_season = 'Monthly demand - All neighbourhoods'
        monthly = rev_data.groupby('month').size().reset_index(name='reviews')
        monthly['month_name'] = monthly['month'].map(MONTH_NAMES)
        monthly['is_high'] = monthly['month'].isin(HIGH_SEASON_MONTHS)
        colors_m = [COLOR_PRIMARY if h else COLOR_SECONDARY for h in monthly['is_high']]
        fig_season.add_trace(go.Bar(
            x=monthly['month_name'], y=monthly['reviews'],
            marker_color=colors_m,
            hovertemplate='%{x}: %{y:,} reviews<extra></extra>',
        ))
        fig_season.add_hline(y=monthly['reviews'].mean(), line_dash='dash',
                             line_color=COLOR_ACCENT,
                             annotation_text=f'Average: {monthly["reviews"].mean():,.0f}')

    fig_season.update_layout(
        title=title_season,
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis_title='Month', yaxis_title='Number of reviews',
        xaxis=dict(categoryorder='array', categoryarray=MONTH_ORDER),
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )

    # Filtrar para el trend anual tambien
    if hood_list:
        rev_data = rev_data if len(hood_list) >= 2 else rev_data
        rev_data_trend = df_rev.merge(
            df[['id', hood_col]].rename(columns={'id': 'listing_id'}),
            on='listing_id', how='left'
        )
        rev_data_trend = rev_data_trend[rev_data_trend[hood_col].isin(hood_list)]
        rev_data = rev_data_trend

    # Trend by year
    yearly = rev_data[rev_data['year'] >= 2015].groupby('year').size().reset_index(name='reviews')
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=yearly['year'], y=yearly['reviews'],
        mode='lines+markers',
        line=dict(color=COLOR_PRIMARY, width=2.5),
        marker=dict(size=8, color=COLOR_PRIMARY),
        fill='tozeroy',
        fillcolor=f'rgba(231,76,60,0.1)',
        hovertemplate='%{x}: %{y:,} reviews<extra></extra>',
    ))
    fig_trend.add_vrect(x0=2020, x1=2021, fillcolor='rgba(255,0,0,0.08)',
                        annotation_text='COVID', annotation_position='top left',
                        line_width=0)
    fig_trend.update_layout(
        title='Historical demand trend (2015-2025)',
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis_title='Year', yaxis_title='Reviews per year',
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial'),
    )

    return fig_season, fig_trend


# ── Tab 4: Hosts ──────────────────────────────────────────────
@app.callback(
    [Output('host-segment-chart', 'figure'),
     Output('superhost-chart', 'figure'),
     Output('host-revenue-dist', 'figure')],
    Input('tabs', 'value')
)
def update_hosts(tab):
    # Segment performance
    seg_data = df.groupby('host_segment').agg(
        median_revenue   = ('estimated_revenue_l365d', 'median'),
        median_price     = ('price_eur', 'median'),
        median_occupancy = ('estimated_occupancy_l365d', 'median'),
    ).reindex(['Amateur', 'Semi-pro', 'Profesional'])

    fig_seg = go.Figure()
    colors_seg = [COLOR_BAD, COLOR_WARN, COLOR_GOOD]
    for col, name in [('median_revenue','Revenue EUR/year'),
                       ('median_price','Price EUR/night'),
                       ('median_occupancy','Occupancy nights')]:
        fig_seg.add_trace(go.Bar(
            name=name, x=seg_data.index, y=seg_data[col],
            text=[f'{v:,.0f}' for v in seg_data[col]],
            textposition='outside',
        ))
    fig_seg.update_layout(
        title='Performance by Host Segment',
        barmode='group',
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )

    # Superhost comparison
    sh_data = df.groupby('host_is_superhost_bool').agg(
        median_revenue   = ('estimated_revenue_l365d', 'median'),
        median_rating    = ('review_scores_rating', 'median'),
        n                = ('id', 'count'),
    ).reset_index()
    sh_data['label'] = sh_data['host_is_superhost_bool'].map({True: 'Superhost', False: 'Regular'})

    fig_sh = go.Figure()
    fig_sh.add_trace(go.Bar(
        x=sh_data['label'],
        y=sh_data['median_revenue'],
        marker_color=[COLOR_PRIMARY, COLOR_SECONDARY],
        text=[f'{v:,.0f} EUR' for v in sh_data['median_revenue']],
        textposition='outside',
        hovertemplate='%{x}: %{y:,.0f} EUR/year<extra></extra>',
    ))
    fig_sh.update_layout(
        title='Median revenue: Superhost vs Regular',
        plot_bgcolor='white', paper_bgcolor='white',
        yaxis_title='Median revenue (EUR/year)',
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial'),
    )

    # Revenue distribution
    fig_dist = go.Figure()
    for seg, color in zip(['Amateur', 'Semi-pro', 'Profesional'],
                           [COLOR_BAD, COLOR_WARN, COLOR_GOOD]):
        data = df[df['host_segment'] == seg]['estimated_revenue_l365d'].dropna()
        data = data[data <= 40000]
        fig_dist.add_trace(go.Histogram(
            x=data, name=f'{seg} (med={data.median():,.0f})',
            opacity=0.65, nbinsx=40,
            marker_color=color,
            histnorm='probability density',
        ))
    fig_dist.update_layout(
        title='Revenue distribution by segment',
        barmode='overlay',
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis_title='Estimated revenue (EUR/year)',
        yaxis_title='Density',
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family='Segoe UI, Arial'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )

    return fig_seg, fig_sh, fig_dist


# ── Run ───────────────────────────────────────────────────────
if __name__ == '__main__':
    print('\nValencia Airbnb Investment Dashboard')
    print('Opening at: http://127.0.0.1:8050\n')
    app.run(debug=True, port=8050)
