import streamlit as st

st.set_page_config(layout="centered")
st.title("🧪 TESTE INSTALAÇÃO")

# Testa OpenAI
try:
    import openai
    st.success(f"✅ OpenAI: {getattr(openai, '__version__', '0.28.1')}")
except Exception as e:
    st.error(f"❌ OpenAI: {e}")

# Testa LangChain  
try:
    import langchain
    st.success(f"✅ LangChain: {langchain.__version__}")
except Exception as e:
    st.error(f"❌ LangChain: {e}")

# Testa yfinance
try:
    import yfinance as yf
    st.success(f"✅ yfinance: {yf.__version__}")
except Exception as e:
    st.error(f"❌ yfinance: {e}")

st.info("""
**SE VER ERROS:**
1. Verifique packages.txt na raiz
2. Streamlit Cloud instala automaticamente
3. Aguarde 3-5 minutos após upload
""")
