from preswald import (
    connect, get_df, text, table, plotly, selectbox, separator, checkbox
)
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

connect()
df_raw = get_df("finance_data")



df_raw["Date"] = pd.to_datetime(df_raw["Date"])
df_raw = df_raw.sort_values("Date")
df_raw["DateStr"] = df_raw["Date"].astype(str)
df_raw["Year"] = df_raw["Date"].dt.year
df_raw["Month"] = df_raw["Date"].dt.month
df_raw["Month_Name"] = df_raw["Date"].dt.strftime("%B")


def filter_by_range(df, selected_label):
    years = sorted(df["Year"].unique().tolist())
    selected_year = selectbox("Choose a Year", options=years)
    df_year = df[df["Year"] == selected_year]

    if selected_label == "1 Month":
        month_options = df_year["Month_Name"].unique().tolist()
        selected_month = selectbox("Choose a Month", options=month_options)
        filtered = df_year[df_year["Month_Name"] == selected_month]
        return filtered, f"1 Month - {selected_month} {selected_year}", selected_year

    elif selected_label == "3 Months":
        quarter_options = {
            "Jan - Mar": [1, 2, 3],
            "Apr - Jun": [4, 5, 6],
            "Jul - Sep": [7, 8, 9],
            "Oct - Dec": [10, 11, 12],
        }
        selected_quarter = selectbox("Choose a Quarter", options=list(quarter_options.keys()))
        months = quarter_options[selected_quarter]
        filtered = df_year[df_year["Month"].isin(months)]
        return filtered, f"3 Months - {selected_quarter} {selected_year}", selected_year

    elif selected_label == "6 Months":
        half_options = {
            "Jan - Jun": [1, 2, 3, 4, 5, 6],
            "Jul - Dec": [7, 8, 9, 10, 11, 12],
        }
        selected_half = selectbox("Choose a 6-Month Period", options=list(half_options.keys()))
        months = half_options[selected_half]
        filtered = df_year[df_year["Month"].isin(months)]
        return filtered, f"6 Months - {selected_half} {selected_year}", selected_year

    elif selected_label == "1 Year":
        return df_year, f"1 Year - {selected_year}", selected_year

    elif selected_label == "View All":
        return df, "All Data", None

    return df.head(0), "", None



text("# Financial Dashboard")
text("Explore macro and stock trends with precise time filters and chart-specific stock comparisons.")

separator()


stock_options = df_raw["Stock Index"].unique().tolist()
selected_stock = selectbox("Choose Main Stock Index", options=stock_options)

separator()


text("## Select Time Range")
range_labels = ["1 Month", "3 Months", "6 Months", "1 Year", "View All"]
selected_range = selectbox("⏱️ Choose Time Range", options=range_labels)


filtered_df, title_suffix, selected_year = filter_by_range(df_raw, selected_range)


main_df = filtered_df[filtered_df["Stock Index"] == selected_stock]


compare_candidates = [s for s in stock_options if s != selected_stock]


if not filtered_df.empty:
    display_df = filtered_df[["DateStr", "Stock Index"] + 
                             [col for col in filtered_df.columns if col not in ["Date", "DateStr", "Stock Index"]]]
    table(display_df, title=f"📋 Data for {selected_stock} - {title_suffix}")

separator()


text("### Closing Price - Compare With:")
price_comp_df = main_df.copy()

for stock in compare_candidates:
    if checkbox(f"Add {stock} to Closing Price Chart"):
        price_comp_df = pd.concat([price_comp_df, filtered_df[filtered_df["Stock Index"] == stock]])


price_comp_df = price_comp_df.sort_values("DateStr")

fig1 = px.line(
    price_comp_df,
    x="DateStr",  # must be string in Preswald (for JSON safety)
    y="Close Price",
    color="Stock Index",
    title="Closing Price Comparison",
)

plotly(fig1)

separator()

text("### GDP vs Inflation - Compare With:")
gdp_comp_df = main_df.copy()


gdp_comp_df = gdp_comp_df[gdp_comp_df["Trading Volume"] > 0]

fig2 = px.scatter(
    gdp_comp_df,
    x="GDP Growth (%)",
    y="Inflation Rate (%)",
    color="Stock Index",
    hover_name="DateStr",
    title=f"GDP vs Inflation {title_suffix}"
)

plotly(fig2)

separator()

text("### Oil vs Gold (Global)")


melted = filtered_df.melt(
    id_vars=["DateStr"],
    value_vars=["Crude Oil Price (USD per Barrel)", "Gold Price (USD per Ounce)"],
    var_name="Commodity",
    value_name="Price"
)

melted = melted.sort_values("DateStr")


fig3 = go.Figure()


for commodity in melted["Commodity"].unique():
    sub_df = melted[melted["Commodity"] == commodity]
    fig3.add_trace(go.Scatter(
        x=sub_df["DateStr"],
        y=sub_df["Price"],  # critical for tooltip to work
        name=commodity,
        hovertemplate=(
            "<b>%{fullData.name}</b><br>" +
            "Date: %{x}<br>" +
            "Price: $%{y:.2f}<extra></extra>"
        )
    ))

fig3.update_layout(
    title=f"Oil vs Gold Prices {title_suffix}",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
)

plotly(fig3)

separator()

text(f"### Candlestick Chart for {selected_stock} Only")

candle_df = main_df.copy()
fig4 = go.Figure(data=[go.Candlestick(
    x=candle_df["DateStr"],
    open=candle_df["Open Price"],
    high=candle_df["Daily High"],
    low=candle_df["Daily Low"],
    close=candle_df["Close Price"],
    increasing_line_color='green',
    decreasing_line_color='red'
)])
fig4.update_layout(title=f"Candlestick Chart for {selected_stock} {title_suffix}",
                   xaxis_title="Date", yaxis_title="Price")
plotly(fig4)
