import streamlit as st

import os
from google_docs_utils import create_google_doc
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI PRD Generator", layout="wide")

st.title("🚀 AI PRD Generator")
st.markdown("Generate a comprehensive Product Requirements Document from context and designs.")

# Sidebar for API Configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Gemini API Key", value=st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")), type="password")
    if api_key:
        # genai.configure no longer needed. API key is passed to function.
        pass
    
    st.info("To generate Google Docs, ensure `credentials.json` is in the project root.")

# Main Input Area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Context & Input")
    context_text = st.text_area("Product Context / Description", height=300, placeholder="Describe the feature, user problem, goals, and any specific requirements...")
    uploaded_files = st.file_uploader("Upload Designs / Screenshots (Optional)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

with col2:
    st.subheader("Generated PRD")
    if st.button("Generate PRD", type="primary"):
        if not api_key:
            st.error("Please enter a Gemini API Key in the sidebar.")
        elif not context_text and not uploaded_files:
            st.warning("Please provide context text or upload images.")
        else:
            result_placeholder = st.empty()
            result_placeholder.info("Generating PRD... this may take a moment.")
            
            try:
                # Use the custom REST function to bypass library version issues
                from gemini_utils import generate_content_rest
                
                final_parts = []
                image_parts = []
                
                if context_text:
                    prompt = f"Generate a detailed Product Requirements Document (PRD) based on the following context. Use standard PRD sections like Problem Statement, Goals, User Stories, Functional Requirements, and Non-Functional Requirements. Format it in Markdown.\n\nContext:\n{context_text}"
                    final_parts.append(prompt)
                
                if uploaded_files:
                    prompt += "\n\nAlso consider the attached design mockups/screenshots for UI/UX requirements."
                    for uploaded_file in uploaded_files:
                        # Convert to bytes for Gemini
                        bytes_data = uploaded_file.getvalue()
                        mime_type = uploaded_file.type
                        image_parts.append((bytes_data, mime_type))

                # Combine text logic: `generate_content_rest` expects text and optional images
                generated_prd = generate_content_rest(
                    api_key=api_key, 
                    text=prompt if context_text else "Please analyze these images and create a PRD.",
                    images=image_parts,
                    model_name="gemini-1.5-flash"
                )
                
                result_placeholder.markdown(generated_prd)
                st.session_state['generated_prd'] = generated_prd
                
            except Exception as e:
                result_placeholder.error(f"Error generating content: {e}")

    # Export Options
    if 'generated_prd' in st.session_state:
        st.divider()
        st.subheader("Export")
        doc_title = st.text_input("Document Title", value="Generated PRD")
        
        if st.button("Create Google Doc"):
            with st.spinner("Creating Google Doc..."):
                link = create_google_doc(doc_title, st.session_state['generated_prd'])
                if link.startswith("http"):
                    st.success(f"Successfully created! [Open Google Doc]({link})")
                else:
                    st.error(link)
