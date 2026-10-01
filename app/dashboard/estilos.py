import streamlit as st


def aplicar_estilos() -> None:
    """
    Aplica os estilos visuais inspirados no DevLeads (Tema Ultra Dark com Verde Lima #B8F22D,
    tipografia Manrope + Montserrat + JetBrains Mono e barra lateral estilo SaaS),
    preservando rigorosamente a renderização dos ícones do Streamlit (Material Symbols).
    """
    st.markdown(
        """
        <style>
        /* Importação das fontes do DevLeads */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&family=Montserrat:wght@500;600;700;800;900&display=swap');
        
        /* Tipografia Base Global (herança limpa, sem sobrescrever ícones) */
        html, body, .stApp {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: #EDEDED;
            background-color: #050505 !important;
        }

        p, label, input, textarea, select, button, .stMarkdown p {
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
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

        /* ------------------------------------------------------------- */
        /* PRESERVAÇÃO TOTAL DOS ÍCONES MATERIAL SYMBOLS DO STREAMLIT    */
        /* (Garante que setas, chevrons e ícones nunca virem texto puro) */
        /* ------------------------------------------------------------- */
        [data-testid*="Icon"],
        [data-testid*="icon"],
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-symbols-sharp,
        [class*="material-symbols"],
        [class*="material-icons"] {
            font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
            font-feature-settings: "liga" 1, "dlig" 1 !important;
            text-transform: none !important;
            direction: ltr !important;
            -webkit-font-smoothing: antialiased !important;
            font-style: normal !important;
            display: inline-block !important;
            line-height: 1 !important;
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

        /* Ocultar elementos desnecessários padrão do Streamlit */
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
        /* BARRA LATERAL EM ILHA FLUTUANTE (DEVLEADS FLOATING ISLAND)   */
        /* ------------------------------------------------------------- */
        section[data-testid="stSidebar"] {
            background-color: transparent !important;
            border: none !important;
            padding: 14px 0 14px 14px !important;
            box-sizing: border-box !important;
            overflow: visible !important;
            z-index: 100 !important;
        }

        /* O corpo da ilha flutuante com cantos arredondados */
        section[data-testid="stSidebar"] > div:first-child,
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background-color: #0A0A0A !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 24px !important;
            height: calc(100vh - 28px) !important;
            max-height: calc(100vh - 28px) !important;
            box-shadow: 0 16px 45px rgba(0, 0, 0, 0.8), 0 0 25px rgba(184, 242, 45, 0.03) !important;
            display: flex !important;
            flex-direction: column !important;
            position: relative !important;
            overflow: visible !important;
        }

        /* Header da sidebar (contém o botão de recuo) */
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            overflow: visible !important;
            position: relative !important;
        }

        /* Conteúdo interno da ilha */
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding: 1.2rem 1rem !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }

        /* Scrollbar elegante e discreta */
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]::-webkit-scrollbar {
            width: 4px;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }

        /* ------------------------------------------------------------- */
        /* SETINHA DE RECUO CIRCULAR (COLLAPSE BUTTON ESTILO DEVLEADS)   */
        /* ------------------------------------------------------------- */
        [data-testid="stSidebarCollapseButton"],
        section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"],
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button {
            display: inline-flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            position: absolute !important;
            right: -13px !important;
            top: 24px !important;
            z-index: 999999 !important;
            background-color: #0E0E0E !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 50% !important;
            width: 26px !important;
            height: 26px !important;
            min-width: 26px !important;
            min-height: 26px !important;
            max-width: 26px !important;
            max-height: 26px !important;
            padding: 0 !important;
            margin: 0 !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        [data-testid="stSidebarCollapseButton"]:hover,
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button:hover {
            background-color: #181818 !important;
            border-color: #B8F22D !important;
            transform: scale(1.1);
            box-shadow: 0 0 16px rgba(184, 242, 45, 0.35) !important;
        }

        [data-testid="stSidebarCollapseButton"] svg,
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button svg {
            width: 14px !important;
            height: 14px !important;
            fill: #A1A1AA !important;
            color: #A1A1AA !important;
            transition: all 0.18s ease !important;
        }

        [data-testid="stSidebarCollapseButton"]:hover svg,
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button:hover svg {
            fill: #B8F22D !important;
            color: #B8F22D !important;
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

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label p {
            font-family: 'Manrope', sans-serif !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            color: #94A3B8 !important;
            transition: color 0.18s ease-in-out !important;
            margin: 0 !important;
        }

        /* Hover no item inativo */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background: rgba(255, 255, 255, 0.05) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p {
            color: #FFFFFF !important;
        }

        /* Item Ativo / Selecionado no menu (Pill com Verde Lima DevLeads) */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: rgba(184, 242, 45, 0.1) !important;
            border: 1px solid rgba(184, 242, 45, 0.3) !important;
            box-shadow: 0 0 16px rgba(184, 242, 45, 0.06) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
            color: #B8F22D !important;
            font-weight: 700 !important;
        }

        /* Botão flutuante para reabrir a ilha quando recuada */
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stExpandSidebarButton"] {
            display: inline-flex !important;
            visibility: visible !important;
            pointer-events: auto !important;
            position: fixed !important;
            left: 14px !important;
            top: 24px !important;
            z-index: 99999 !important;
            background-color: #0E0E0E !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 50% !important;
            width: 32px !important;
            height: 32px !important;
            min-width: 32px !important;
            min-height: 32px !important;
            padding: 0 !important;
            margin: 0 !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.8) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        [data-testid="stSidebarCollapsedControl"]:hover,
        [data-testid="stExpandSidebarButton"]:hover {
            background-color: #1A1A1A !important;
            border-color: #B8F22D !important;
            transform: scale(1.12);
            box-shadow: 0 0 18px rgba(184, 242, 45, 0.4) !important;
        }

        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stExpandSidebarButton"] svg {
            width: 16px !important;
            height: 16px !important;
            fill: #B8F22D !important;
            color: #B8F22D !important;
        }

        [data-testid="stSidebarCollapsedControl"]::after,
        [data-testid="stExpandSidebarButton"]::after {
            display: none !important;
            content: "" !important;
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
