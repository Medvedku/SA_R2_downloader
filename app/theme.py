VHS_PURPLE = "#531a46"
VHS_RED = "#9f1e34"
VHS_CRIMSON = "#d82b2c"
VHS_ORANGE = "#e4532e"
VHS_YELLOW = "#eea83a"

DARK_BG = "#001E2B"
DARK_TEXT = "#FFFFFF"

STRIPE_GRADIENT = (
    "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
    f"stop:0 {VHS_PURPLE}, stop:0.25 {VHS_RED}, stop:0.5 {VHS_CRIMSON}, "
    f"stop:0.75 {VHS_ORANGE}, stop:1 {VHS_YELLOW})"
)

def get_stylesheet():
    bg = DARK_BG
    text = DARK_TEXT
    
    return f"""
        QMainWindow {{
            background-color: {bg};
        }}
        
        QWidget {{
            background-color: {bg};
            color: {text};
            font-family: 'Courier New', Courier, monospace;
        }}
        
        QLabel#appTitle {{
            font-size: 20px;
            font-weight: bold;
            color: #FFFFFF;
            letter-spacing: 2px;
        }}
        
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {VHS_RED}, stop:1 {VHS_ORANGE});
            color: #FFFFFF;
            border: 2px solid {VHS_PURPLE};
            border-bottom: 2px solid {VHS_PURPLE};
            border-right: 2px solid {VHS_PURPLE};
            border-radius: 0px;
            height: 44px;
            padding: 0px 20px;
            font-weight: bold;
            font-size: 14px;
            letter-spacing: 1px;
            margin-bottom: 2px;
            margin-right: 2px;
        }}
        
        QPushButton:hover {{
            background: {VHS_RED};
        }}
        
        QPushButton:pressed {{
            background: {VHS_PURPLE};
            border-bottom: 1px solid {VHS_PURPLE};
            border-right: 1px solid {VHS_PURPLE};
            margin-top: 1px;
            margin-left: 1px;
            margin-bottom: 1px;
            margin-right: 1px;
        }}
        
        QPushButton:disabled {{
            background: #888888;
            border-color: #666666;
            color: #AAAAAA;
        }}
        
        /* Flat Navigation Arrows */
        QPushButton#yearNavBtn {{
            background: transparent;
            border: none;
            color: {text};
            font-size: 24px;
            font-weight: bold;
            margin: 0;
            padding: 0;
        }}
        
        QPushButton#yearNavBtn:hover {{
            color: {VHS_YELLOW};
            background: transparent;
        }}
        
        QPushButton#yearNavBtn:pressed {{
            color: {VHS_ORANGE};
            background: transparent;
            margin: 0;
            padding: 0;
        }}

        /* Year Display */
        QLabel#yearLabel {{
            font-size: 28px;
            font-weight: bold;
            color: {text};
            letter-spacing: 4px;
        }}

        /* Calendar Styles */
        QLabel {{
            color: {text};
        }}

        QFrame#dayCell {{
            border-radius: 2px;
        }}
        
        QLineEdit {{
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid {VHS_PURPLE};
            color: {text};
            padding: 8px;
            font-size: 14px;
            border-radius: 0px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {VHS_YELLOW};
            background-color: rgba(255, 255, 255, 0.1);
        }}
        
        /* Legend Styles */
        QLabel.legendItem {{
            padding: 4px 8px;
            border-radius: 0px;
            color: #FFFFFF;
            font-size: 11px;
            border: 1px solid {VHS_PURPLE};
        }}
    """
