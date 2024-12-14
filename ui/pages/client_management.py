import streamlit as st
from services.family_service import FamilyService
from services.client_service import ClientService

def client_management_tab():
    st.header("Client Management")
    
    # Initialize services
    family_service = FamilyService(st.session_state.db)
    client_service = ClientService(st.session_state.db)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New Family")
        new_family = st.text_input("Enter Family Name", key="new_family")
        if st.button("Add Family"):
            if new_family:
                success, message = family_service.create_family(new_family)
                if success:
                    st.success(message)
                    # Clear the input
                    st.session_state.new_family = ""
                else:
                    st.error(message)
    
    with col2:
        st.subheader("Create New Client")
        families = family_service.get_all_families()
        
        if families.empty:
            st.warning("Please create a family first!")
        else:
            new_client = st.text_input("Enter Client Name", key="new_client")
            selected_family = st.selectbox(
                "Select Family",
                options=families['id'].tolist(),
                format_func=lambda x: families.loc[families['id'] == x, 'name'].iloc[0]
            )
            
            if st.button("Add Client"):
                if new_client and selected_family:
                    success, message = client_service.create_client(new_client, selected_family)
                    if success:
                        st.success(message)
                        # Clear the input
                        st.session_state.new_client = ""
                    else:
                        st.error(message)
    
    st.markdown("---")
    
    # Display existing families and clients
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Existing Families")
        families = family_service.get_all_families()
        if not families.empty:
            st.dataframe(
                families[['name']],
                column_config={"name": "Family Name"},
                hide_index=True
            )
    
    with col2:
        st.subheader("Existing Clients")
        clients = client_service.get_all_clients()
        if not clients.empty:
            st.dataframe(
                clients[['name', 'family_name']],
                column_config={
                    "name": "Client Name",
                    "family_name": "Family Name"
                },
                hide_index=True
            )