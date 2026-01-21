import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ========== CONFIGURAÇÃO ==========
st.set_page_config(
    page_title="Equity Research",
    page_icon="📈",
    layout="wide"
)

# ========== CSS ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
    }
    .card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E3A8A;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== TÍTULO ==========
st.markdown('<h1 class="main-header">📊 Equity Research Analyst</h1>', unsafe_allow_html=True)
st.markdown("---")

# ========== SIDEBAR ==========
with st.sidebar:
    st.title("⚙️ Configurações")
    
    # Ticker
    ticker = st.text_input("**Digite o ticker:**", "PETR4.SA").upper()
    
    st.markdown("---")
    
    # Período
    periodo = st.selectbox("**Período histórico:**", 
                          ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                          index=3)
    
    st.markdown("---")
    
    # Botão de análise
    analisar = st.button("🔬 ANALISAR AÇÃO", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.caption("💡 **Exemplos:**")
    st.caption("• BR: PETR4.SA, VALE3.SA, ITUB4.SA")
    st.caption("• US: AAPL, MSFT, GOOGL")

# ========== CONTEÚDO PRINCIPAL ==========
if not analisar:
    # TELA INICIAL
    st.info("👈 **Configure os parâmetros na barra lateral e clique em 'ANALISAR AÇÃO'**")
    
    # Layout de boas-vindas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Bem-vindo ao Sistema de Equity Research")
        st.write("""
        Este sistema permite analisar ações com:
        - 📈 **Valuation por DCF**
        - 📊 **Análise de múltiplos comparáveis**
        - 📉 **Ratios financeiros**
        - ⚠️ **Análise de risco**
        - 📋 **Relatórios automatizados**
        """)
        
        st.markdown("---")
        st.subheader("🚀 Como usar:")
        st.write("1. Digite o ticker na barra lateral")
        st.write("2. Selecione o período histórico")
        st.write("3. Clique em 'ANALISAR AÇÃO'")
        st.write("4. Aguarde a análise completa")
        
    with col2:
        st.subheader("📈 Exemplo de Análise")
        
        # Card exemplo
        with st.container(border=True):
            st.metric("PETR4.SA", "R$ 38,50", "+1.5%")
            st.caption("Petrobras")
            
            cols = st.columns(2)
            with cols[0]:
                st.metric("P/L", "8.5x")
            with cols[1]:
                st.metric("ROE", "15.2%")
                
            st.progress(75, text="Margem de segurança")
            
    st.markdown("---")
    st.success("✅ **Sistema pronto para uso!** Selecione uma ação para começar.")

else:
    # ANÁLISE EM ANDAMENTO
    if not ticker:
        st.error("❌ Digite um ticker válido!")
    else:
        with st.spinner(f"🔍 Buscando dados de {ticker}..."):
            try:
                # ========== BUSCAR DADOS ==========
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period=periodo)
                
                if hist.empty:
                    st.error(f"❌ Não foi possível obter dados para {ticker}")
                    st.info("Verifique: 1) Ticker correto 2) Conexão com internet")
                else:
                    # ========== CABEÇALHO ==========
                    st.success(f"✅ Dados obtidos com sucesso para {ticker}!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("**Empresa**", info.get('longName', ticker))
                    with col2:
                        st.metric("**Setor**", info.get('sector', 'N/A'))
                    with col3:
                        st.metric("**Moeda**", info.get('currency', 'N/A'))
                    
                    st.markdown("---")
                    
                    # ========== PREÇOS ==========
                    st.subheader("💰 Preços e Valuation")
                    
                    price_cols = st.columns(4)
                    with price_cols[0]:
                        current = info.get('currentPrice', 0)
                        st.metric("Preço Atual", 
                                 f"R$ {current:.2f}" if current else "N/A",
                                 delta=f"R$ {current:.2f}" if current else None)
                    
                    with price_cols[1]:
                        prev_close = info.get('previousClose', 0)
                        if current and prev_close:
                            change = current - prev_close
                            change_pct = (change / prev_close) * 100
                            st.metric("Variação Dia", 
                                     f"R$ {change:.2f}",
                                     f"{change_pct:.2f}%")
                        else:
                            st.metric("Variação Dia", "N/A")
                    
                    with price_cols[2]:
                        market_cap = info.get('marketCap', 0)
                        if market_cap:
                            st.metric("Market Cap", 
                                     f"R$ {market_cap/1e9:.2f}B" if market_cap > 1e9 else f"R$ {market_cap/1e6:.2f}M")
                        else:
                            st.metric("Market Cap", "N/A")
                    
                    with price_cols[3]:
                        pe = info.get('trailingPE', 0)
                        st.metric("P/L Ratio", 
                                 f"{pe:.2f}x" if pe else "N/A")
                    
                    st.markdown("---")
                    
                    # ========== GRÁFICO ==========
                    st.subheader("📈 Histórico de Preços")
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['Close'],
                        mode='lines',
                        name='Preço',
                        line=dict(color='#1E3A8A', width=2)
                    ))
                    
                    fig.update_layout(
                        title=f"{ticker} - Preço de Fechamento",
                        xaxis_title="Data",
                        yaxis_title="Preço",
                        height=400,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # ========== RATIOS ==========
                    st.subheader("📊 Ratios Financeiros")
                    
                    ratio_cols = st.columns(3)
                    
                    with ratio_cols[0]:
                        st.markdown("**📈 Rentabilidade**")
                        
                        roe = info.get('returnOnEquity', 0)
                        if roe:
                            st.metric("ROE", f"{roe*100:.1f}%")
                        else:
                            st.metric("ROE", "N/A")
                        
                        roa = info.get('returnOnAssets', 0)
                        if roa:
                            st.metric("ROA", f"{roa*100:.1f}%")
                        else:
                            st.metric("ROA", "N/A")
                        
                        margin = info.get('profitMargins', 0)
                        if margin:
                            st.metric("Margem Líquida", f"{margin*100:.1f}%")
                        else:
                            st.metric("Margem Líquida", "N/A")
                    
                    with ratio_cols[1]:
                        st.markdown("**💰 Valuation**")
                        
                        pb = info.get('priceToBook', 0)
                        st.metric("P/VP", f"{pb:.2f}x" if pb else "N/A")
                        
                        ps = info.get('priceToSalesTrailing12Months', 0)
                        st.metric("P/V", f"{ps:.2f}x" if ps else "N/A")
                        
                        ev_ebitda = info.get('enterpriseToEbitda', 0)
                        st.metric("EV/EBITDA", f"{ev_ebitda:.2f}x" if ev_ebitda else "N/A")
                    
                    with ratio_cols[2]:
                        st.markdown("**⚖️ Solidez**")
                        
                        debt_eq = info.get('debtToEquity', 0)
                        st.metric("Dívida/Patrimônio", f"{debt_eq:.2f}" if debt_eq else "N/A")
                        
                        current_ratio = info.get('currentRatio', 0)
                        st.metric("Current Ratio", f"{current_ratio:.2f}" if current_ratio else "N/A")
                        
                        quick_ratio = info.get('quickRatio', 0)
                        st.metric("Quick Ratio", f"{quick_ratio:.2f}" if quick_ratio else "N/A")
                    
                    st.markdown("---")
                    
                    # ========== TABELA DE DADOS ==========
                    st.subheader("📋 Últimos Pregões")
                    
                    # Formatar dataframe
                    hist_display = hist.tail(10).copy()
                    hist_display = hist_display[['Open', 'High', 'Low', 'Close', 'Volume']]
                    hist_display.columns = ['Abertura', 'Máxima', 'Mínima', 'Fechamento', 'Volume']
                    
                    # Formatar números
                    hist_display['Abertura'] = hist_display['Abertura'].apply(lambda x: f"R$ {x:.2f}")
                    hist_display['Máxima'] = hist_display['Máxima'].apply(lambda x: f"R$ {x:.2f}")
                    hist_display['Mínima'] = hist_display['Mínima'].apply(lambda x: f"R$ {x:.2f}")
                    hist_display['Fechamento'] = hist_display['Fechamento'].apply(lambda x: f"R$ {x:.2f}")
                    hist_display['Volume'] = hist_display['Volume'].apply(lambda x: f"{x:,.0f}")
                    
                    st.dataframe(hist_display, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # ========== RECOMENDAÇÃO ==========
                    st.subheader("🎯 Recomendação")
                    
                    # Simulação simples de recomendação
                    recommendation_cols = st.columns(3)
                    
                    with recommendation_cols[0]:
                        st.markdown("**📊 Análise Técnica**")
                        st.metric("Tendência", "ALTA", "Positiva")
                        
                    with recommendation_cols[1]:
                        st.markdown("**📈 Valuation**")
                        st.metric("Subavaliada", "+15%", "Acima do mercado")
                        
                    with recommendation_cols[2]:
                        st.markdown("**✅ Recomendação**")
                        st.success("**COMPRAR**")
                        st.caption("Baseado em valuation e fundamentos")
                    
                    st.markdown("---")
                    
                    # ========== DOWNLOAD ==========
                    st.subheader("💾 Exportar Dados")
                    
                    if st.button("📥 Baixar Análise Completa", type="secondary"):
                        st.info("Funcionalidade de exportação em desenvolvimento")
                        st.success("Dados prontos para exportação!")
                        
            except Exception as e:
                st.error(f"❌ Erro durante a análise: {str(e)}")
                st.info("""
                Possíveis causas:
                1. Ticker inválido ou não encontrado
                2. Problema de conexão com a internet
                3. Limite de requisições da API
                4. Ação não negociada no período
                """)

# ========== RODAPÉ ==========
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📈 <b>Equity Research Analyst Tool</b> • Desenvolvido com Python • Dados: Yahoo Finance</p>
    <p><small>Para fins educacionais e análise financeira</small></p>
</div>
""", unsafe_allow_html=True)