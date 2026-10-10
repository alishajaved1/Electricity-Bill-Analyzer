import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PALETTE = ["#3b4de0", "#22b573", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#64748b", "#ec4899"]
LAYOUT = dict(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
              font=dict(family="Inter, Segoe UI, Arial", size=13, color="#141a3a"),
              margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.2),
              transition=dict(duration=500, easing="cubic-in-out"))


def show(fig):
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "responsive": True})


def trend_line(df: pd.DataFrame, y: str, title: str, ylabel: str):
    fig = go.Figure(go.Scatter(x=df["month"], y=df[y], mode="lines+markers", line=dict(color="#3b4de0", width=3, shape="spline"),
                               marker=dict(size=9), fill="tozeroy", fillcolor="rgba(59,77,224,.08)",
                               hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
    fig.update_layout(title=title, yaxis_title=ylabel, xaxis_title="Month", **LAYOUT)
    return fig


def bar(df: pd.DataFrame, y: str, title: str, ylabel: str, color="#22b573"):
    fig = px.bar(df, x="month", y=y, title=title, text_auto=".0f")
    fig.update_traces(marker_color=color, hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>")
    fig.update_layout(yaxis_title=ylabel, xaxis_title="Month", **LAYOUT)
    return fig


def donut(df: pd.DataFrame, title: str, center: str = ""):
    fig = go.Figure(go.Pie(labels=df["category"], values=df["amount"], hole=.62, marker=dict(colors=PALETTE),
                           hovertemplate="%{label}<br>Rs. %{value:,.2f} (%{percent})<extra></extra>"))
    fig.update_layout(title=title, annotations=[dict(text=center, showarrow=False, font=dict(size=16, color="#141a3a"))], **LAYOUT)
    return fig


def change_bar(df: pd.DataFrame, col: str, title: str, ylabel: str):
    d = df.dropna(subset=[col])
    colors = ["#ef4444" if v > 0 else "#22b573" for v in d[col]]
    fig = go.Figure(go.Bar(x=d["month"], y=d[col], marker_color=colors, hovertemplate="%{x}<br>%{y:+,.1f}<extra></extra>"))
    fig.update_layout(title=title, yaxis_title=ylabel, xaxis_title="Month", **LAYOUT)
    return fig
