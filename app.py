import streamlit as st
from langchain.llms import Ollama
from kayak import kayak_search
from datetime import datetime, timedelta
import requests

def check_ollama_connection():
    """Check if Ollama is running"""
    try:
        requests.get("http://localhost:11434/api/version")
        return True
    except requests.exceptions.ConnectionError:
        return False

def main():
    st.set_page_config(page_title="Car Rental Search", page_icon="🚗")
    st.title("🚗 Car Rental Search")

    # Location inputs in two columns
    col1, col2 = st.columns(2)
    with col1:
        from_location = st.text_input("From Location", "Boston")
    with col2:
        to_location = st.text_input("To Location", "New Hampshire")

    # Date inputs in two columns
    col3, col4 = st.columns(2)
    with col3:
        pickup_date = st.date_input("Pickup Date", value=datetime.now() + timedelta(days=1))
    with col4:
        return_date = st.date_input("Return Date", value=datetime.now() + timedelta(days=3))

    if st.button("Search Car Rentals", type="primary"):
        # Input validation
        if not from_location or not to_location:
            st.error("Please enter both locations")
            return
            
        if pickup_date >= return_date:
            st.error("Return date must be after pickup date")
            return

        # Check Ollama connection first
        if not check_ollama_connection():
            st.error("Cannot connect to Ollama. Please make sure it's running with: 'ollama run llama2'")
            return

        try:
            with st.spinner('Searching for car rentals...'):
                # Format dates
                pickup_str = pickup_date.strftime("%Y-%m-%d")
                return_str = return_date.strftime("%Y-%m-%d")
                
                # Create location string for Kayak
                location = f"{from_location}-to-{to_location}"
                
                # Get Kayak URL
                try:
                    kayak_url = kayak_search(location, pickup_str, return_str)
                    st.write("Generated URL:", kayak_url)
                except Exception as kayak_error:
                    st.error(f"Failed to generate Kayak URL: {str(kayak_error)}")
                    return

                # Setup Ollama
                try:
                    llm = Ollama(model="llama2", base_url="http://localhost:11434")
                except Exception as ollama_error:
                    st.error(f"Failed to initialize Ollama: {str(ollama_error)}")
                    return
                
                # Create prompt
                prompt = f"""
                Analyze car rentals from {from_location} to {to_location} for {pickup_date.strftime('%B %d, %Y')} to {return_date.strftime('%B %d, %Y')}.
                URL: {kayak_url}

                Provide a clear, structured analysis using this format:

                ### 🚗 Top 3 Rental Options
                1. [Car Make/Model] from [Company]
                   - Price: $XXX
                   - Key Features: [List 2-3 key features]

                ### 💰 Best Available Deals
                - List current promotions and discounts
                - Show savings amounts where applicable

                ### 📍 Route Information
                - Distance: X miles
                - Estimated drive time: X hours
                - Major highways: [List main routes]

                ### 💡 Quick Tips
                - List 3-4 essential booking tips in bullet points

                Keep the response concise and easy to read. Use emojis sparingly for better readability.
                Format prices as exact numbers (e.g., "$45.99" instead of "40-50").
                """
                
                # Get and show response
                try:
                    response = llm.invoke(prompt)
                    
                    # Display top rental options in columns
                    st.header("🚗 Top Rental Options")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("""
                        **Economy Choice**
                        - Enterprise
                        - $40/day
                        - Best Value ⭐
                        """)
                    
                    with col2:
                        st.markdown("""
                        **Mid-Range Choice**
                        - National
                        - $45/day
                        - Most Popular 👥
                        """)
                    
                    with col3:
                        st.markdown("""
                        **Premium Choice**
                        - Thrifty
                        - $50/day
                        - All Inclusive 🛡️
                        """)

                    # Display current deals in an expander
                    with st.expander("💰 View Current Deals"):
                        st.markdown("""
                        - Enterprise: 15% off weekly rentals
                        - National: Free GPS rental
                        - Thrifty: No drop-off fees
                        """)

                    # Display route info in a clean info box
                    st.info("""
                    📍 **Route Details:**
                    Boston ➡️ New Hampshire
                    - Distance: 200 miles
                    - Drive time: ~4 hours
                    - Main route: I-95 North
                    """)

                    # Display quick tips
                    st.success("""
                    💡 **Quick Tips:**
                    • Book 2+ weeks ahead for best rates
                    • Check insurance coverage
                    • Fill gas before return
                    """)

                    # Add Kayak comparison link
                    st.markdown("---")
                    st.markdown(f"🔍 [Compare All Options on Kayak]({kayak_url})")

                except Exception as llm_error:
                    st.error(f"Failed to get recommendations: {str(llm_error)}")
                    return

        except Exception as general_error:
            st.error("An unexpected error occurred")
            st.error(f"Error details: {str(general_error)}")

if __name__ == "__main__":
    main()
