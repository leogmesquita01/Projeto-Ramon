import streamlit as st


def aplicar_estilos() -> None:
    """
    Aplica os estilos visuais modernos do aplicativo (Tema Escuro Floresta com Esmeralda).
    """
    st.markdown(
        """
        <style>
        /* Fonte e espaçamento global */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* Espaçamento superior otimizado (sem cabeçalho) */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
        }

        /* Cabeçalho transparente e não intrusivo (mantém o botão de reabrir a barra lateral acessível) */
        header[data-testid="stHeader"], [data-testid="stHeader"] {
            background: transparent !important;
            pointer-events: none;
        }

        [data-testid="stToolbar"] {
            background: transparent !important;
        }

        /* Ocultar elementos desnecessários (menu padrão, decorações, deploy e rodapé) */
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

        /* Botão de abrir/expandir a barra lateral quando recolhida (visível e destacado no tema do app) */
        [data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapsedControl"],
        header[data-testid="stHeader"] button {
            display: inline-flex !important;
            visibility: visible !important;
            pointer-events: auto !important;
        }

        [data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapsedControl"] {
            background-color: #152420 !important;
            border: 2px solid #10B981 !important;
            border-radius: 12px !important;
            color: #10B981 !important;
            padding: 6px 14px !important;
            margin-top: 10px !important;
            margin-left: 14px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6), 0 0 12px rgba(16, 185, 129, 0.3) !important;
            transition: all 0.25s ease !important;
            cursor: pointer !important;
            align-items: center !important;
        }

        [data-testid="stExpandSidebarButton"]::after,
        [data-testid="stSidebarCollapsedControl"]::after {
            content: " Abrir Menu";
            font-size: 0.9rem !important;
            font-weight: 700 !important;
            color: #10B981 !important;
            margin-left: 6px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        [data-testid="stExpandSidebarButton"]:hover::after,
        [data-testid="stSidebarCollapsedControl"]:hover::after {
            color: #FFFFFF !important;
        }

        [data-testid="stExpandSidebarButton"]:hover,
        [data-testid="stSidebarCollapsedControl"]:hover {
            background-color: #10B981 !important;
            border-color: #34D399 !important;
            transform: scale(1.04);
            box-shadow: 0 6px 25px rgba(16, 185, 129, 0.45) !important;
        }

        [data-testid="stExpandSidebarButton"] svg,
        [data-testid="stExpandSidebarButton"] span,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] span {
            color: #10B981 !important;
            fill: #10B981 !important;
        }

        [data-testid="stExpandSidebarButton"]:hover svg,
        [data-testid="stExpandSidebarButton"]:hover span,
        [data-testid="stSidebarCollapsedControl"]:hover svg,
        [data-testid="stSidebarCollapsedControl"]:hover span {
            color: #FFFFFF !important;
            fill: #FFFFFF !important;
        }

        /* Desativar e ocultar completamente o botão de recuar/fechar a barra lateral */
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }

        /* Cartão base estilo container escuro sofisticado */
        .agro-card {
            background: linear-gradient(145deg, #13221C 0%, #172B23 100%);
            border: 1px solid rgba(16, 185, 129, 0.22);
            border-radius: 18px;
            padding: 1.5rem;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
            margin-bottom: 1.2rem;
        }

        /* Cartão de Destaque da Carga (com borda e brilho dourado suave) */
        .agro-card-gold {
            background: linear-gradient(145deg, #1A281E 0%, #203325 100%);
            border: 1.5px solid rgba(245, 158, 11, 0.4);
            border-radius: 18px;
            padding: 1.6rem;
            box-shadow: 0 10px 30px rgba(245, 158, 11, 0.1);
            margin-bottom: 1.2rem;
            text-align: center;
        }

        /* Cartão de Lucro Real Máximo */
        .agro-card-lucro {
            background: linear-gradient(145deg, #064E3B 0%, #065F46 100%);
            border: 2px solid #10B981;
            border-radius: 20px;
            padding: 1.8rem;
            text-align: center;
            box-shadow: 0 12px 35px rgba(16, 185, 129, 0.25);
            margin-bottom: 1.5rem;
        }

        /* Pílulas de badges informativos */
        .agro-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .badge-verde {
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .badge-ouro {
            background: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        /* Botão primário grande, moderno e com gradiente (fácil de tocar no celular) */
        div.stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            color: #FFFFFF !important;
            border: none;
            border-radius: 14px;
            padding: 0.8rem 1.4rem;
            font-size: 1.1rem;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45);
        }
        div.stButton > button:active {
            transform: translateY(0);
        }

        /* Top banner elegante */
        .hero-banner {
            background: linear-gradient(90deg, #13221C 0%, #1A3327 100%);
            border-left: 5px solid #10B981;
            border-radius: 12px;
            padding: 1rem 1.4rem;
            margin-bottom: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
