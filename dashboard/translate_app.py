"""Traduce el dashboard app.py de espanol a ingles. Correr una sola vez."""
from pathlib import Path

APP = Path(r'C:\Users\User\Desktop\GitHub\PROYECTO FINAL FINAL\airbnb_valencia\dashboard\app.py')
content = APP.read_text(encoding='utf-8')

T = [
    ("'Analisis del mercado de alquiler turistico · Donde, cuando y como invertir'",
     "'Short-term rental market analysis · Where, when and how to invest'"),
    ("'Datos: Inside Airbnb Valencia · Sep 2025'", "'Data: Inside Airbnb Valencia · Sep 2025'"),
    ("'7.780 propiedades activas'", "'7,780 active properties'"),
    ("kpi_card('Precio Mediano'", "kpi_card('Median Price'"),
    ("EUR/noche\",", "EUR/night\","),
    ("'Mercado Valencia'", "'Valencia market'"),
    ("kpi_card('Ingresos Medianos'", "kpi_card('Median Revenue'"),
    ("EUR/año\",", "EUR/year\","),
    ("'Por listing activo'", "'Per active listing'"),
    ("'Del total de hosts'", "'Of all hosts'"),
    ("kpi_card('Barrios', '19', 'Analizados'", "kpi_card('Neighbourhoods', '19', 'Analyzed'"),
    ("label='Mercado por Barrio'", "label='Market by Neighbourhood'"),
    ("label='Estacionalidad'", "label='Seasonality'"),
    ("label='Analisis de Hosts'", "label='Host Analysis'"),
    ("'Ranking de Inversion'", "'Investment Ranking'"),
    ("'Investment Score por Barrio'", "'Investment Score by Neighbourhood'"),
    ("['Barrio', 'Score', 'Ingresos EUR', 'Ocupacion', 'Precio EUR', 'N Listings']",
     "['Neighbourhood', 'Score', 'Revenue EUR', 'Occupancy', 'Price EUR', 'N Listings']"),
    ("'Tipo de alojamiento'", "'Room type'"),
    ("'Todos los tipos'", "'All room types'"),
    ("'Barrio (multi-seleccion para comparar)'", "'Neighbourhood (multi-select to compare)'"),
    ("'Todos los barrios (selecciona 2+ para comparar)'", "'All neighbourhoods (select 2+ to compare)'"),
    ("'Segmento de host'", "'Host segment'"),
    ("'Todos los segmentos'", "'All segments'"),
    ("'Precio Mediano por Barrio (EUR/noche)'", "'Median Price by Neighbourhood (EUR/night)'"),
    ("'y': 'EUR/noche'", "'y': 'EUR/night'"),
    ("'Ingresos Medianos por Barrio (EUR/año)'", "'Median Revenue by Neighbourhood (EUR/year)'"),
    ("'y': 'EUR/año'", "'y': 'EUR/year'"),
    ("'Precio vs Ingresos por Barrio'", "'Price vs Revenue by Neighbourhood'"),
    ("'Precio mediano (EUR/noche)'", "'Median price (EUR/night)'"),
    ("'Ingresos medianos (EUR/año)'", "'Median revenue (EUR/year)'"),
    ("'Ocupacion (noches)'", "'Occupancy (nights)'"),
    ("'Distribucion por Tipo'", "'Room Type Distribution'"),
    ("'Seleccionar barrio'", "'Select neighbourhood'"),
    ("'Seleccionar barrios (multi-seleccion para comparar)'", "'Select neighbourhoods (multi-select to compare)'"),
    ("'Todos los barrios (selecciona 2+ para comparar lineas)'", "'All neighbourhoods (select 2+ to compare lines)'"),
    ("'Todos (promedio)'", "'All (average)'"),
    ("f'Demanda mensual comparada ({len(hood_list)} barrios)'", "f'Monthly demand compared ({len(hood_list)} neighbourhoods)'"),
    ("f'Demanda mensual - {hood_list[0]}'", "f'Monthly demand - {hood_list[0]}'"),
    ("'Demanda mensual - Todos los barrios'", "'Monthly demand - All neighbourhoods'"),
    ('f\'Demanda mensual - {"Todos los barrios" if hood == "all" else hood}\'',
     'f\'Monthly demand - {"All neighbourhoods" if hood == "all" else hood}\''),
    ("f'Media: {monthly[\"reviews\"].mean():,.0f}'", "f'Average: {monthly[\"reviews\"].mean():,.0f}'"),
    ("xaxis_title='Mes'", "xaxis_title='Month'"),
    ("yaxis_title='Numero de resenas'", "yaxis_title='Number of reviews'"),
    ("resenas<extra>", "reviews<extra>"),
    (": %{y:,} resenas<extra></extra>", ": %{y:,} reviews<extra></extra>"),
    ("'Evolucion historica de la demanda (2015-2025)'", "'Historical demand trend (2015-2025)'"),
    ("xaxis_title='Año'", "xaxis_title='Year'"),
    ("yaxis_title='Resenas por año'", "yaxis_title='Reviews per year'"),
    ("'Rendimiento por Segmento de Host'", "'Performance by Host Segment'"),
    ("'Ingresos EUR/año'", "'Revenue EUR/year'"),
    ("'Precio EUR/noche'", "'Price EUR/night'"),
    ("'Ocupacion noches'", "'Occupancy nights'"),
    ("'Ingresos medianos: Superhost vs Regular'", "'Median revenue: Superhost vs Regular'"),
    ("yaxis_title='Ingresos medianos (EUR/año)'", "yaxis_title='Median revenue (EUR/year)'"),
    ("EUR/año<extra></extra>", "EUR/year<extra></extra>"),
    ("'Distribucion de ingresos por segmento'", "'Revenue distribution by segment'"),
    ("xaxis_title='Ingresos estimados (EUR/año)'", "xaxis_title='Estimated revenue (EUR/year)'"),
    ("yaxis_title='Densidad'", "yaxis_title='Density'"),
    ("'Recomendaciones para el Inversor'", "'Investor Recommendations'"),
    ("'Ser Superhost es prioridad'", "'Becoming a Superhost is priority #1'"),
    ("'+386% ingresos vs host regular'", "'+386% revenue vs regular hosts'"),
    ("'Activar Instant Booking'", "'Enable Instant Booking'"),
    ("'Los top 10% por ingresos lo usan mas'", "'Top 10% earners use it more'"),
    ("'Priorizar capacidad 4+ personas'", "'Prioritize capacity for 4+ guests'"),
    ("'Correlacion mas fuerte con ingresos (rho=0.62)'", "'Strongest correlation with price (rho=0.62)'"),
    ("'Invertir en Ciutat Vella o Eixample'", "'Invest in Ciutat Vella or Eixample'"),
    ("'Score 74.5 y 68.9 - top 1 y 2 del ranking'", "'Scores 74.5 and 68.9 - top 2 of the ranking'"),
    ("'Abriendo en: http://127.0.0.1:8050\\n'", "'Opening at: http://127.0.0.1:8050\\n'"),
]

count = 0
for old, new in T:
    if old in content:
        content = content.replace(old, new)
        count += 1

APP.write_text(content, encoding='utf-8')
print(f'{count}/{len(T)} traducciones aplicadas')
print('Listo. Relanza el dashboard con: python dashboard/app.py')