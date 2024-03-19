import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from neo4j_driver import run_query
import math

from ui_utils import render_header_svg

st.set_page_config(
    page_title="SEC EDGAR Filings",
    page_icon="images/logo-mark-fullcolor-RGB-transBG.svg",
    layout="wide",
)


render_header_svg("images/main-top-header.svg", 350)

render_header_svg("images/bottom-header.svg", 200)


# @st.cache_data
def get_data() -> pd.DataFrame:
    return run_query("""
      MATCH (n:Manager) return n.managerName as Manager ORDER BY Manager""")

df_managers = get_data()

placeholder = st.empty()

with placeholder.container():
        df_companies = run_query("""MATCH (n:Company) return n.companyName as name""")
        assets_in_billions = math.floor(run_query("""MATCH (m:Manager)-[o:OWNS]->(c:Company) RETURN SUM(o.value)/1_000_000_000_000 as assetsInBillions""")['assetsInBillions'][0])

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(
            label="Managers",
            value=len(df_managers)
        )     
        kpi2.metric(
            label="Companies",
            value=len(df_companies)
        )
        kpi3.metric(
            label="Total Assets Managed (In Trillions)",
            value=assets_in_billions
        )
    
        sankey_col = st.columns(1)
        st.markdown("### Managers & Assets")
        df_1 = run_query("""
            MATCH (e:Manager)-[o:OWNS]->(c:Company)
            return e.managerName as id, c.cusip as target, SUM(o.value)/1_000_000_000_000 as value, 
                   e.managerName as label, '#33a02c' as color ORDER BY target DESC LIMIT 15""")
        df_2 = run_query("""
            MATCH (e:Manager)-[o:OWNS]->(c:Company)
            return c.cusip as id,
                   c.companyName as label, '#1f78b4' as color ORDER BY c.cusip DESC LIMIT 15""")
        df_3 = run_query("""
            MATCH (e:Manager)-[o:OWNS]->(c:Company)
            return o.reportCalendarOrQuarter as id, SUM(o.value)/1_000_000_000_000 as value,
                   o.reportCalendarOrQuarter as label, '#fdbf6f' as color ORDER BY value DESC LIMIT 15""")
        df_123 = pd.concat([df_1, df_2], ignore_index=True)
        df_123 = pd.concat([df_123, df_3], ignore_index=True)
        df_mgr_co = run_query("""
            MATCH (e:Manager)-[o:OWNS]->(c:Company)
            return e.managerName as source, c.cusip as target, SUM(o.value)/1_000_000_000_000 as value, 
                '#a6cee3' as link_color ORDER BY target DESC LIMIT 15""")
        df_co_date = run_query("""
            MATCH (e:Manager)-[o:OWNS]->(c:Company)
            return c.cusip as source, o.reportCalendarOrQuarter as target, SUM(o.value)/1_000_000_000_000 as value, 
                '#fdbf6f' as link_color ORDER BY source DESC LIMIT 15""")
        df_mgr_co_date = pd.concat([df_mgr_co, df_co_date], ignore_index=True)
        label_mapping = dict(zip(df_123['id'], df_123.index))
        df_mgr_co_date['src_id'] = df_mgr_co_date['source'].map(label_mapping)
        df_mgr_co_date['target_id'] = df_mgr_co_date['target'].map(label_mapping)
        
        sankey = go.Figure(data=[go.Sankey(
            arrangement="snap",
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(
                    color = "black",
                    width = 0.4
                ),
                label = df_123['label'].values.tolist(),
                color = df_123['color'].values.tolist(),
                ),
            link = dict(
                source = df_mgr_co_date['src_id'].values.tolist(),
                target = df_mgr_co_date['target_id'].values.tolist(),
                value = df_mgr_co_date['value'].values.tolist(),
                color = df_mgr_co_date['link_color'].values.tolist()
            )
        )])
        st.plotly_chart(sankey, use_container_width=True)

        assets_col = st.columns(1)
        st.markdown("### Popular Companies by Assets (In Billions)")
        df_assets = run_query("""
            MATCH (m:Manager)-[o:OWNS]->(c:Company) 
            RETURN c.companyName as company, 
                SUM(o.value)/1_000_000_000 as assets 
            ORDER BY assets DESC limit 10""")
        size_max_default = 7
        scaling_factor = 5
        fig_assets = px.scatter(df_assets, x="company", y="assets",
                    size="assets", color="company",
                        hover_name="company", log_y=False, 
                        size_max=size_max_default*scaling_factor)
        st.plotly_chart(fig_assets, use_container_width=True)

        
        st.markdown("### Top Managers by ownerships")
        df = run_query("""
            MATCH (m:Manager)-[o:OWNS]->(c:Company) 
            RETURN m.managerName as manager, 
                COUNT(c) as companies 
            ORDER BY companies DESC limit 10""")
        fig = px.scatter(df, x="manager", y="companies",
                    size="companies", color="manager",
                        hover_name="manager", log_y=False, 
                        size_max=size_max_default*scaling_factor)
        st.plotly_chart(fig, use_container_width=True)
        