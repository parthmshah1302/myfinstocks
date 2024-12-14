import streamlit as st
import pandas as pd

def metric_card(title: str, value: str, subtitle: str = None, color: str = None):
    """Display a metric in a card format"""
    color_class = f' {color}-return' if color else ''
    st.markdown(f"""
        <div class="metric-card">
            <p style="color: #666; font-size: 1.1em;">{title}</p>
            <p class="big-font{color_class}">{value}</p>
            {f'<p class="info-text">{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)

def format_currency(value: float) -> str:
    """Format value as Indian currency"""
    return f"₹{value:,.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage with color coding"""
    color = "positive" if value > 0 else "negative"
    return f'<span class="{color}-return">{value:+.2f}%</span>'

def display_holdings_table(holdings_df: pd.DataFrame):
    """Display holdings in a formatted table"""
    if holdings_df.empty:
        st.info("No holdings found.")
        return

    st.dataframe(
        holdings_df,
        column_config={
            "ticker": st.column_config.TextColumn("Ticker", width="medium"),
            "quantity": st.column_config.NumberColumn("Quantity", width="small"),
            "buy_price": st.column_config.NumberColumn(
                "Buy Price",
                width="medium",
                format="₹%.2f"
            ),
            "current_price": st.column_config.NumberColumn(
                "Current Price",
                width="medium",
                format="₹%.2f"
            ),
            "return_percentage": st.column_config.NumberColumn(
                "Return %",
                width="medium",
                format="%.2f%%"
            )
        },
        hide_index=True,
        use_container_width=True
    )