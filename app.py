import streamlit as st
import mysql.connector
from datetime import datetime

st.set_page_config(layout="wide")  # This will make the whole app wide

# Connect to MySQL
conn = mysql.connector.connect(
    host='investtrestore.cvmmgrjdemrn.ap-south-1.rds.amazonaws.com',
    user='admin',
    password='iNVESTT1729'
)
cursor = conn.cursor()


st.title("Fund User Input Form")

# Add label to remind the user that total allocation should equal 100%
st.markdown("**Note**: The total allocation should add up to exactly 100%. Please ensure that the sum of all allocations equals 100%.")
st.markdown("---")  # Horizontal line for separation

# Fetch fund names, codes, and categories
cursor.execute("SELECT fund_name, code as fund_code, Categ as category FROM advisor.new_master")
funds = cursor.fetchall()

# Create fund options dictionary with code and category
fund_options = {
    f[0]: {"code": f[1], "category": f[2]} for f in funds
}
fund_options = {'': {"code": '', "category": ''}} | fund_options  # Add empty select option

# Use a form to reset after submit
with st.form("fund_form"):
    # Layout for email and phone number side by side
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email")
    with col2:
        phonenumber = st.text_input("Phone Number")
    
    # Create inputs for 6 fund names and allocations side by side
    fund_name_inputs = []
    allocation_inputs = []
    for i in range(6):
        col1, col2 = st.columns(2)
        with col1:
            fund_name_input = st.selectbox(f"Select Fund Name {i + 1}", list(fund_options.keys()), key=f"fund_name_{i}")
        with col2:
            allocation_input = st.number_input(f"Allocation (%) {i + 1}", min_value=0, max_value=100, step=1, key=f"allocation_{i}", format="%d")
        
        fund_name_inputs.append(fund_name_input)
        allocation_inputs.append(allocation_input)

    # Layout for submit button on the right side
    col1, col2 = st.columns([8, 2])  # The right column is smaller
    with col2:
        submitted = st.form_submit_button("Submit Form")

    # Ensure all values are filled before allowing submission
    if submitted:
        if not email or not phonenumber:
            st.error("Please fill in both Email and Phone Number before submitting.")
        else:
            total_allocation = sum(allocation_inputs)
            if total_allocation != 100:
                st.error(f"The total allocation must be 100%. Current total: {total_allocation}%")
            else:
                data_inserted = False

                delete_query = """
                DELETE FROM whatsapp_crm.model_portfolios 
                WHERE email = %s AND phonenumber = %s
                """
                cursor.execute(delete_query, (email, phonenumber))
                
                for fund_name, allocation in zip(fund_name_inputs, allocation_inputs):
                    if fund_name and allocation > 0:
                        selected = fund_options.get(fund_name, {"code": "", "category": ""})
                        selected_fund_code = selected["code"]
                        selected_category = selected["category"]

                        
                        
                        insert_query = """
                        INSERT INTO whatsapp_crm.model_portfolios 
                        (email, phonenumber, fund_name, fund_code, allocation)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (
                            email, phonenumber, fund_name, selected_fund_code, allocation
                        ))

                        data_inserted = True
                
                if data_inserted:
                    conn.commit()
                    st.success("✅ Data inserted successfully!")
                else:
                    st.error("Please provide valid fund names and allocations to submit.")
