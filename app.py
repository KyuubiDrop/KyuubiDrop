import streamlit as st
import sqlite3
import pandas as pd
import random
import string
import hashlib
import json
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
import numpy as np
import plotly.express as px
import pyperclip
import time
import asyncio
import aiohttp
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import base64

st.set_page_config(
    page_title="Kyuubi-Drop",
    page_icon="🦊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verstecke alle Streamlit-Elemente und setze grundlegendes Layout
st.markdown("""
    <style>
    /* Reset und Grundeinstellungen */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hauptcontainer */
    .stApp {
        background-color: rgb(24, 25, 28) !important;
        margin: 0;
        padding: 0;
        overflow: hidden;  /* Verhindert Scrolling im Hauptcontainer */
    }
    
    /* Layout-Container */
    .app-container {
        display: flex;
        height: 100vh;  /* Volle Viewport-Höhe */
        width: 100vw;  /* Volle Viewport-Breite */
        position: fixed;  /* Fixierte Position */
        top: 0;
        left: 0;
        overflow: hidden;
    }
    
    /* Menü-Container */
    [data-testid="stSidebar"] {
        background-color: rgb(31, 32, 35);
        width: 280px !important;
        padding: 20px;
    }
    
    /* Logo-Container */
    .logo-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding: 10px;
    }
    
    /* Content-Bereich */
    .main .block-container {
        margin-left: 280px;
        padding: 2rem 1rem;
        max-width: calc(100vw - 280px);
    }
    
    /* Menü-Buttons */
    .stButton button {
        width: 100%;
        background-color: rgb(43, 45, 49);
        color: white;
        border: none;
        padding: 12px;
        margin: 4px 0;
        text-align: left;
        border-radius: 4px;
    }
    
    .stButton button:hover {
        background-color: rgb(55, 57, 62);
    }
    
    /* Metriken-Karten */
    .metric-card {
        background: rgba(43, 45, 49, 0.9);
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        height: 100%;  /* Volle Höhe */
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #FF4B4B;
        margin-bottom: 5px;
    }
    
    .metric-label {
        color: #ffffff;
        font-size: 16px;
    }
    
    /* Entferne Standard-Streamlit Padding */
    .element-container {padding: 0 !important;}
    .stMarkdown {padding: 0 !important;}
    div[data-testid="stVerticalBlock"] {gap: 0 !important;}
    
    /* Scrollbar-Anpassungen */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgb(31, 32, 35);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgb(55, 57, 62);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgb(75, 77, 82);
    }
    
    /* Zusätzliche Fixes */
    .stButton button {
        width: 100%;
        background-color: rgb(43, 45, 49);
        color: white;
        border: none;
        padding: 12px;
        margin: 4px 0;
    }
    
    .stButton button:hover {
        background-color: rgb(55, 57, 62);
        color: white;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# Außerdem müssen wir den Session State initialisieren
if 'username' not in st.session_state:
    st.session_state.username = None

# Datenbank-Tabellen für:
# - Produkte
# - Bestellungen
# - Umsätze
# - Profit-Tracking

def init_db():
    """Initialisiert die Datenbank"""
    conn = sqlite3.connect('kyuubi_drop.db')
    c = conn.cursor()
    
    try:
        # Erstelle die products Tabelle mit allen notwendigen Spalten
        c.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                amazon_price REAL,
                selling_price REAL,
                image_url TEXT,
                amazon_url TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("Datenbank erfolgreich initialisiert!")
        
    except Exception as e:
        print(f"Fehler bei der Datenbankinitialisierung: {e}")
        
    finally:
        conn.close()

def get_db_connection():
    """Erstellt eine Datenbankverbindung"""
    return sqlite3.connect('kyuubi_drop.db')

def show_dashboard():
    """Zeigt das Dashboard mit Übersicht und Statistiken"""
    st.markdown("# Willkommen zurück, Boss!")
    
    # Metriken in der oberen Reihe
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gesamtprofit", "€0.00")
    with col2:
        st.metric("Bestellungen", "0")
    with col3:
        st.metric("Gesamtumsatz", "€0.00")
    
    # Diagramm mit allen drei Metriken
    chart_data = pd.DataFrame({
        'Datum': pd.date_range(start='2024-01-01', periods=30),
        'Umsatz': np.random.randn(30).cumsum(),
        'Profit': np.random.randn(30).cumsum(),
        'Bestellungen': np.abs(np.random.randn(30) * 3).cumsum()
    })
    
    # Konfiguration für das Diagramm
    st.markdown("""
        <style>
        [data-testid="stChart"] {
            background-color: #141414;
            border-radius: 8px;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Diagramm mit stark kontrastierenden Farben
    st.line_chart(
        chart_data.set_index('Datum'),
        color=['#FF6B6B', '#4ECDC4', '#FFE66D']  # Rot, Türkis, Gelb
    )

def main():
    """Hauptfunktion der Anwendung"""
    # Initialisiere die Datenbank beim ersten Start
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # Prüfe ob die Tabellen existieren
        c.execute(''' SELECT count(name) FROM sqlite_master 
                     WHERE type='table' AND (name='products' OR name='orders') ''')
        
        if c.fetchone()[0] < 2:  # Wenn nicht beide Tabellen existieren
            init_db()  # Initialisiere die Datenbank neu
    finally:
        conn.close()
    
    # Zeige das Dashboard
    show_dashboard()

def save_changes(edited_df):
    """Speichert die Änderungen an den Produkten in der Datenbank"""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = 0
    
    try:
        for _, row in edited_df.iterrows():
            try:
                cursor.execute("""
                    UPDATE products 
                    SET selling_price = ?,
                        amazon_price = ?
                    WHERE id = ?
                """, (
                    row['Verkaufspreis'],
                    row['Amazon Preis'],
                    row['ID']
                ))
                updates += 1
            except Exception as e:
                st.error(f"Fehler beim Speichern von {row['Produkt']}: {str(e)}")
        
        conn.commit()
        st.success(f"✅ {updates} Produkte aktualisiert!")
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Speichern: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    # Initialisiere die Datenbank beim ersten Start
    conn = get_db_connection()
    c = conn.cursor()
    
    # Prüfe ob die Tabellen existieren
    c.execute(''' SELECT count(name) FROM sqlite_master 
                 WHERE type='table' AND (name='products' OR name='orders') ''')
    
    if c.fetchone()[0] < 2:  # Wenn nicht beide Tabellen existieren
        init_db()  # Initialisiere die Datenbank neu
    
    conn.close()
    
    # Dann normal fortfahren
    main()