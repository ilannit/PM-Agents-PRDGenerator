import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents"]

import streamlit as st
import json

def get_creds():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    
    # 1. Try Streamlit Secrets (Preferred for Cloud)
    # expected format: GOOGLE_TOKEN = '{"token": "...", "refresh_token": "...", ...}'
    if "GOOGLE_TOKEN" in st.secrets:
        try:
            token_info = json.loads(st.secrets["GOOGLE_TOKEN"])
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except Exception as e:
            st.warning(f"Failed to load GOOGLE_TOKEN from secrets: {e}")

    # 2. Try Local File (Preferred for Local Dev)
    if not creds and os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
    # 3. Validate or Refresh
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        # 4. Initial Login (Only works locally)
        if not creds:
            if not os.path.exists("credentials.json"):
                return None
                
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
            except OSError:
                 st.error("Authentication failed: Cannot open browser for login. If running in the cloud, please ensure 'GOOGLE_TOKEN' is set in Streamlit Secrets.")
                 return None

    return creds

def create_google_doc(title, content):
    """Creates a new Google Doc and populates it with content."""
    creds = get_creds()
    if not creds:
        return "Error: `credentials.json` not found. Please place it in the project directory."

    try:
        service = build("docs", "v1", credentials=creds)

        # Create a blank document
        document = service.documents().create(body={"title": title}).execute()
        document_id = document.get("documentId")
        
        # Simple content insertion (inserting at index 1)
        # Note: A more robust implementation would parse markdown headers and format accordingly.
        # For now, we'll dump the text.
        requests = [
            {
                "insertText": {
                    "location": {
                        "index": 1,
                    },
                    "text": content
                }
            }
        ]

        result = service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()

        return f"https://docs.google.com/document/d/{document_id}/edit"

    except HttpError as err:
        return f"An error occurred: {err}"
