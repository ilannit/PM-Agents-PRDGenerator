# PRD Generator with Streamlit & Gemini

This tool generates a Product Requirements Document (PRD) from a text description and optional design screenshots, then exports it directly to a Google Doc.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **API Keys**:
    - **Gemini API**: Get a key from [Google AI Studio](https://aistudio.google.com/).
      - Create a `.env` file and add `GEMINI_API_KEY=your_key`.
    - **Google Docs API**:
      - Create a project in [Google Cloud Console](https://console.cloud.google.com/).
      - Enable the **Google Docs API**.
      - Create **OAuth 2.0 Client IDs** (Desktop App).
      - Download the JSON file, rename it to `credentials.json`, and place it in this directory.

3.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## Usage

1.  Enter your product context/idea in the text area.
2.  (Optional) Upload UI screenshots or mockups.
3.  Click **Generate PRD**.
4.  Once generated, enter a title and click **Create Google Doc**.
5.  Click the link to open your new document.
