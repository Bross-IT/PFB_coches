import streamlit as st
import streamlit as st
import pandas as pd
import os
import pickle
import base64
import sklearn

st.set_page_config(
    page_title="Venta de Coches de Segunda Mano",
    page_icon="🚗",
    layout="wide",  
    initial_sidebar_state="expanded"  
)

st.title("🚗 Venta de Coches de Segunda Mano")
st.subheader("Encuentra el coche perfecto para ti al mejor precio.")