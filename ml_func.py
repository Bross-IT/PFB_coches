import streamlit as st
import pandas as pd
import os
import pickle
import base64
import sklearn

PAGE_CONFIG = {
    "page_title"             : "Venta de Coches de Segunda Mano - Streamlit",
    "page_icon"              : "🚗",
    "layout"                 : "wide",
    "initial_sidebar_state"  : "expanded"
}
