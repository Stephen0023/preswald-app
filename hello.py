from preswald import connect, get_df, query, text, table, slider, plotly
import pandas as pd
import plotly.express as px

# 1. Connect to Preswald and load dataset
connect()
df = get_df("finance_data")

if df is None:
    raise ValueError("Dataset not found. Ensure 'my_dataset.csv' is in the data/ folder.")

# 2. Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"])

# 3. Copy and convert Date back to string for displaying in tables
df_display = df.copy()
df_display["Date"] = df_display["Date"].astype(str)

# 4. Header and description
text("# 📈 Network Topology Dashboard")
text("Explore trends in stock markets and economic indicators across time.")

# 5. Show entire dataset in a table
table(df_display, title="📊 Full Dataset")

# 6. Slider to filter by Interest Rate
threshold = slider("📉 Minimum Interest Rate (%)", min_val=0, max_val=10, default=3.0)
filtered_df = df[df["Interest Rate (%)"] >= threshold]
filtered_df_display = filtered_df.copy()
filtered_df_display["Date"] = filtered_df_display["Date"].astype(str)
table(filtered_df_display, title=f"📌 Days with Interest Rate ≥ {threshold}%")

# 7. Visualization: Closing Price over Time by Stock Index
fig1 = px.line(df, x="Date", y="Close Price", color="Stock Index",
               title="📅 Stock Closing Prices Over Time")
plotly(fig1)

# 8. Visualization: GDP Growth vs. Inflation Rate
fig2 = px.scatter(df, x="GDP Growth (%)", y="Inflation Rate (%)", color="Stock Index",
                  size="Trading Volume", hover_name="Date",
                  title="💸 GDP Growth vs Inflation Rate (Bubble = Trading Volume)")
plotly(fig2)

# 9. Visualization: Oil vs. Gold Price (melted for multi-line chart)
melted = df.melt(id_vars=["Date"], 
                 value_vars=["Crude Oil Price (USD per Barrel)", "Gold Price (USD per Ounce)"],
                 var_name="Commodity", value_name="Price")
fig3 = px.line(melted, x="Date", y="Price", color="Commodity",
               title="🛢️ Oil vs Gold Prices Over Time")
plotly(fig3)
