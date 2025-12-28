# Google Calendar API Setup Guide

To allow the script to access your Google Calendar, you need to set up OAuth 2.0 credentials. This involves two main files: `credentials.json` (your app's identity) and `token.json` (your personal access grant).

## 1. Get `credentials.json`
This file identifies the application to Google.

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Create a Project**: Click the project dropdown and select "New Project".
3.  **Enable API**: Search for "Google Calendar API" and click **Enable**.
4.  **Configure Consent Screen**:
    - Go to **APIs & Services > OAuth consent screen**.
    - Choose **External** (unless you have a Google Workspace org, then Internal is easier).
    - Fill in the required app name and email fields.
    - Add the scope: `.../auth/calendar.events` (for creating events).
    - **Add Test Users**: Add your own email address as a test user.
5.  **Create Credentials**:
    - Go to **APIs & Services > Credentials**.
    - Click **Create Credentials > OAuth client ID**.
    - Select **Desktop app**.
    - Give it a name and click **Create**.
6.  **Download**: Click the download icon (JSON) for your new client ID. Rename this file to `credentials.json` and place it in your project root.

## 2. Generate `token.json`
The script will generate this automatically the first time it runs.

1.  When you run the script, it will open a browser window asking you to sign in.
2.  Once authorized, the script creates `token.json` in your project folder.
3.  This file contains a **Refresh Token**, which allows the script to run in the background without asking you to log in again.

## 3. Best Practices & Security

### `.gitignore`
**Never commit these files to GitHub.** They grant full access to your calendar.

Your `.gitignore` file should include:

```gitignore
# Google API Credentials
credentials.json
token.json
```

### File Storage
- **Local Development**: Keep them in the project root.
- **Production/Cloud**: Do not store these files in your code. Instead, use a Secrets Manager or encode the JSON as a Base64 string in an environment variable that the script can decode at runtime.

### Expiration
- Access tokens expire every hour, but the script uses the refresh token in `token.json` to get a new one automatically.
- If you change your Google password or revoke access, you'll need to delete `token.json` and re-run the script to generate a new one.
