import streamlit as st


def aplicar_estilos() -> None:
    """
    Aplica os estilos visuais inspirados no DevLeads (Tema Ultra Dark com Verde Lima #B8F22D,
    tipografia Manrope + Montserrat + JetBrains Mono e barra lateral estilo SaaS).
    """
    st.markdown(
        """
        <style>
        /* Importação das fontes do DevLeads */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&family=Montserrat:wght@500;600;700;800;900&display=swap');
        
        /* Tipografia Base Global */
        html, body, [class*="css"], .stMarkdown, p, span, div {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: #EDEDED;
        }

        /* Títulos com Montserrat marcante */
        h1, h2, h3, h4, h5, h6, .montserrat-title {
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
            color: #FFFFFF !important;
        }

        /* Números, Métricas e Códigos com JetBrains Mono */
        .metric-mono, [data-testid="stMetricValue"], code, .jetbrains-mono {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
        }

        /* Fundo da Aplicação */
        .stApp {
            background-color: #050505 !important;
        }

        /* Espaçamento superior da área principal */
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 3rem !important;
            max-width: 1400px !important;
        }

        /* Cabeçalho transparente */
        header[data-testid="stHeader"], [data-testid="stHeader"] {
            background: transparent !important;
            pointer-events: none;
        }

        [data-testid="stToolbar"] {
            background: transparent !important;
        }

        /* Ocultar elementos padrão do Streamlit */
        #MainMenu, 
        [data-testid="stMainMenu"], 
        footer, 
        [data-testid="stDecoration"], 
        [data-testid="stStatusWidget"],
        .stDeployButton,
        [data-testid="stAppDeployButton"],
        [data-testid="stToolbarActions"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* ------------------------------------------------------------- */
        /* BARRA LATERAL ESTILO DEVLEADS */
        /* ------------------------------------------------------------- */
        section[data-testid="stSidebar"] {
            background-color: #080808 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
            padding-top: 1rem !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding-top: 0.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Transforma o st.radio da sidebar em botões modernos estilo DevLeads */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            gap: 4px !important;
            display: flex !important;
            flex-direction: column !important;
        }

        /* Remove o círculo de radio padrão */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label span[data-testid="stRadioButtonCustomObject"] {
            display: none !important;
        }

        /* Estilo de cada item do menu */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
            width: 100% !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 10px !important;
            padding: 8px 12px !important;
            margin: 0 !important;
            cursor: pointer !important;
            transition: all 0.18s ease-in-out !important;
            display: flex !important;
            align-items: center !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label span {
            font-family: 'Manrope', sans-serif !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            color: #94A3B8 !important;
            transition: color 0.18s ease-in-out !important;
        }

        /* Hover no item inativo */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background: rgba(255, 255, 255, 0.05) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p,
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover span {
            color: #FFFFFF !important;
        }

        /* Item Ativo / Selecionado no menu (Pill com Verde Lima DevLeads) */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: rgba(184, 242, 45, 0.1) !important;
            border: 1px solid rgba(184, 242, 45, 0.3) !important;
            box-shadow: 0 0 16px rgba(184, 242, 45, 0.06) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p,
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) span {
            color: #B8F22D !important;
            font-weight: 700 !important;
        }

        /* Botão de reabrir sidebar recolhida */
        [data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapsedControl"],
        header[data-testid="stHeader"] button {
            display: inline-flex !important;
            visibility: visible !important;
            pointer-events: auto !important;
        }

        [data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapsedControl"] {
            background-color: #0E0E0E !important;
            border: 1.5px solid #B8F22D !important;
            border-radius: 12px !important;
            color: #B8F22D !important;
            padding: 6px 14px !important;
            margin-top: 10px !important;
            margin-left: 14px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6), 0 0 12px rgba(184, 242, 45, 0.25) !important;
            transition: all 0.25s ease !important;
            cursor: pointer !important;
            align-items: center !important;
        }

        [data-testid="stExpandSidebarButton"]::after,
        [data-testid="stSidebarCollapsedControl"]::after {
            content: " Menu";
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            color: #B8F22D !important;
            margin-left: 6px !important;
            font-family: 'Manrope', sans-serif !important;
        }

        [data-testid="stExpandSidebarButton"]:hover,
        [data-testid="stSidebarCollapsedControl"]:hover {
            background-color: #B8F22D !important;
            color: #050505 !important;
            transform: scale(1.03);
            box-shadow: 0 6px 25px rgba(184, 242, 45, 0.4) !important;
        }

        [data-testid="stExpandSidebarButton"]:hover::after,
        [data-testid="stSidebarCollapsedControl"]:hover::after {
            color: #050505 !important;
        }

        [data-testid="stExpandSidebarButton"] svg,
        [data-testid="stExpandSidebarButton"] span,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] span {
            color: #B8F22D !important;
            fill: #B8F22D !important;
        }

        [data-testid="stExpandSidebarButton"]:hover svg,
        [data-testid="stExpandSidebarButton"]:hover span,
        [data-testid="stSidebarCollapsedControl"]:hover svg,
        [data-testid="stSidebarCollapsedControl"]:hover span {
            color: #050505 !important;
            fill: #050505 !important;
        }

        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }

        /* ------------------------------------------------------------- */
        /* CARTÕES & CONTAINERS (DARK TECH COM BORDAS SUTIS) */
        /* ------------------------------------------------------------- */
        .agro-card {
            background: #0E0E0E;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 1.4rem;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
            margin-bottom: 1.2rem;
            transition: border-color 0.2s ease, transform 0.2s ease;
        }

        .agro-card:hover {
            border-color: rgba(255, 255, 255, 0.15);
        }

        /* Cartão de Destaque / Faturamento (Borda Verde Lima DevLeads) */
        .agro-card-gold {
            background: linear-gradient(145deg, #0F120A 0%, #151C0E 100%);
            border: 1.5px solid rgba(184, 242, 45, 0.35);
            border-radius: 16px;
            padding: 1.6rem;
            box-shadow: 0 10px 35px rgba(184, 242, 45, 0.08);
            margin-bottom: 1.2rem;
            text-align: center;
        }

        /* Cartão de Lucro */
        .agro-card-lucro {
            background: linear-gradient(145deg, #0D160A 0%, #12210E 100%);
            border: 2px solid #B8F22D;
            border-radius: 18px;
            padding: 1.8rem;
            text-align: center;
            box-shadow: 0 12px 35px rgba(184, 242, 45, 0.2);
            margin-bottom: 1.5rem;
        }

        /* ------------------------------------------------------------- */
        /* BADGES & PÍLULAS */
        /* ------------------------------------------------------------- */
        .agro-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-family: 'JetBrains Mono', monospace;
        }

        .badge-verde {
            background: rgba(184, 242, 45, 0.12);
            color: #B8F22D;
            border: 1px solid rgba(184, 242, 45, 0.3);
        }

        .badge-ouro {
            background: rgba(245, 158, 11, 0.12);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .badge-azul {
            background: rgba(59, 130, 246, 0.12);
            color: #60A5FA;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        .badge-vermelho {
            background: rgba(239, 68, 68, 0.12);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .badge-cinza {
            background: rgba(148, 163, 184, 0.12);
            color: #94A3B8;
            border: 1px solid rgba(148, 163, 184, 0.3);
        }

        /* ------------------------------------------------------------- */
        /* BOTÕES PRINCIPAIS ESTILO DEVLEADS (VERDE LIMA COM TEXTO PRETO) */
        /* ------------------------------------------------------------- */
        div.stButton > button {
            width: 100%;
            background: #B8F22D !important;
            color: #050505 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.4rem !important;
            font-size: 0.95rem !important;
            font-weight: 800 !important;
            font-family: 'Manrope', sans-serif !important;
            box-shadow: 0 4px 18px rgba(184, 242, 45, 0.25) !important;
            transition: all 0.18s ease-in-out !important;
            letter-spacing: -0.2px;
        }

        div.stButton > button:hover {
            background: #C8F750 !important;
            color: #000000 !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(184, 242, 45, 0.4) !important;
        }

        div.stButton > button:active {
            transform: translateY(0);
        }

        /* Top banner elegante */
        .hero-banner {
            background: #0E0E0E;
            border-left: 4px solid #B8F22D;
            border-radius: 12px;
            padding: 1rem 1.4rem;
            margin-bottom: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
