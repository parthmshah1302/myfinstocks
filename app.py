import streamlit as st
import logging.config
from pathlib import Path
from config.settings import APP_NAME, UI_SETTINGS, LOG_SETTINGS, FEATURES
from database.db_manager import DatabaseManager
from ui.styles import apply_custom_css
from ui.pages.client_management import client_management_tab
from ui.pages.portfolio_management import portfolio_management_tab
from ui.pages.portfolio_dashboard import portfolio_visualization_tab

# Configure logging
logging.config.dictConfig(LOG_SETTINGS)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initialize session state variables"""
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    apply_custom_css()

def render_sidebar():
    """Render the sidebar navigation"""
    with st.sidebar:
        st.title(APP_NAME)
        st.markdown("---")
        
        # Navigation
        selected_page = st.radio(
            "Navigation",
            ["Dashboard", "Portfolio Management", "Client Management"],
            key="navigation"
        )
        
        st.markdown("---")
        
        # System Status
        st.markdown("### System Status")
        st.success("Database Connected") if st.session_state.db else st.error("Database Error")
        
        if FEATURES['enable_real_time_updates']:
            st.info("Real-time updates enabled")
        
        # Version Info
        st.markdown("---")
        st.markdown("#### About")
        st.text(f"Version: {st.session_state.get('version', '1.0.0')}")
        
        return selected_page

def show_notifications():
    """Display any pending notifications"""
    for msg, msg_type in st.session_state.notifications:
        if msg_type == "success":
            st.success(msg)
        elif msg_type == "error":
            st.error(msg)
        elif msg_type == "warning":
            st.warning(msg)
        else:
            st.info(msg)
    
    # Clear notifications after showing them
    st.session_state.notifications = []

def main():
    try:
        # Initialize application
        logger.info("Starting Portfolio Management System")
        initialize_session_state()
        setup_page_config()
        
        # Render sidebar and get selected page
        selected_page = render_sidebar()
        
        # Show any pending notifications
        show_notifications()
        
        # Main content area
        if selected_page == "Dashboard":
            try:
                portfolio_visualization_tab()
            except Exception as e:
                logger.error(f"Error in dashboard: {str(e)}")
                st.error("Error loading dashboard. Please try again later.")
        
        elif selected_page == "Portfolio Management":
            try:
                portfolio_management_tab()
            except Exception as e:
                logger.error(f"Error in portfolio management: {str(e)}")
                st.error("Error in portfolio management. Please try again later.")
        
        elif selected_page == "Client Management":
            try:
                client_management_tab()
            except Exception as e:
                logger.error(f"Error in client management: {str(e)}")
                st.error("Error in client management. Please try again later.")
        
        # Footer
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("Made with ❤️ by Your Company")
        with col2:
            st.markdown("Need help? [Documentation](https://docs.example.com)")
        with col3:
            if st.button("Clear Cache"):
                st.cache_data.clear()
                st.session_state.notifications.append(
                    ("Cache cleared successfully!", "success")
                )
                st.rerun()

    except Exception as e:
        logger.critical(f"Critical application error: {str(e)}")
        st.error("An unexpected error occurred. Please contact support.")
        
        if UI_SETTINGS.get('show_error_details', False):
            st.exception(e)

if __name__ == "__main__":
    main()