import streamlit as st
import stock_search, portfolio

def main():
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    st.sidebar.title("Navigation")
    pages = ["Home", "Stock Search", "Portfolio"]
    st.session_state.page = st.sidebar.selectbox("Go to", pages, index=pages.index(st.session_state.page))

    if st.session_state.page == "Stock Search":
        stock_search.show()
    elif st.session_state.page == "Portfolio":
        portfolio.show()
    else:
        st.title("Welcome to My FinStocks! 💸")

if __name__ == "__main__":
    main()