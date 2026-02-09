import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents"]

def get_creds():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
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
