import streamlit as st
import sys

st.set_page_config(layout='centered')
st.title('?? TESTE INSTALA??O PACOTES PYTHON')

st.write(f'Python: {sys.version}')

# Testa pacotes Python
packages = [
    'streamlit',
    'yfinance', 
    'pandas',
    'numpy',
    'plotly',
    'openai',
    'langchain',
    'scipy',
    'matplotlib'
]

for pkg in packages:
    try:
        __import__(pkg)
        st.success(f'? {pkg}')
    except ImportError as e:
        st.error(f'? {pkg}: {str(e)[:50]}')

st.info('''
**SE VER ? OPENAI E LANGCHAIN:**
O Streamlit Cloud instalou corretamente via requirements.txt
''')
