import streamlit as st
import time

st.set_page_config(page_title="Equity Research - Carregando", layout="centered")

st.title("📈 Equity Research Pro")
st.markdown("---")

# Animação
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown('<div style="text-align:center; font-size: 48px;">⚡</div>', unsafe_allow_html=True)

st.info("**Inicializando sistema de análise financeira...**")

# Barra de progresso
progress_text = st.empty()
progress_bar = st.progress(0)

for i in range(100):
    progress_bar.progress(i + 1)
    progress_text.text(f"Carregando: {i + 1}%")
    time.sleep(0.02)

st.success("✅ Sistema carregado com sucesso!")

if st.button("🚀 Acessar Análise Completa", type="primary", use_container_width=True):
    st.switch_page("app.py")
