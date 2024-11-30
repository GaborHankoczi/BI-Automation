import codecs
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
import argparse
import re



# proces cli parameters
parser = argparse.ArgumentParser()
parser.add_argument("--deanonymize", type=bool, default=False, help="deanonymize")
args = parser.parse_args()



# Path to your OAuth 2.0 client JSON key file
CLIENT_SECRETS_FILE = "client_secret.json"

# GA4 Property ID
PROPERTY_ID = "356357890"

# The scopes required for the API
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


def authenticate_without_tokens():
    """Authenticate and get credentials without tokens."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    return flow.run_local_server(port=0)

def authenticate_with_oauth():
    """Authenticate and get credentials using OAuth 2.0."""
    creds = None
    token_file = "token.json"

    # Check if the token file exists (previously authenticated)
    try:
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    except Exception:
        pass

    # If no valid credentials, start the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = authenticate_without_tokens()
        else:
            creds = authenticate_without_tokens()

        # Save the credentials for future use
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return creds

def get_ga4_page_view_data(creds):
    """Retrieve page view data from GA4."""
    client = BetaAnalyticsDataClient(credentials=creds)
    current_date = datetime.datetime.now()
    start_date = current_date - datetime.timedelta(days=6)
    current_date_str = current_date.strftime("%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")
    current_year_str = current_date.strftime("%Y")
    current_week = current_date.isocalendar().week
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=current_date_str, end_date=current_date_str)],
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[Metric(name="screenPageViews")],
    )
    # print data ranges
    print(request.date_ranges)

    response = client.run_report(request)

    print("Page Title | Page Views | Year | Week")
    print("-" * 30)
    # order by page views descending
    response.rows.sort(key=lambda x: int(x.metric_values[0].value), reverse=True)
    # display top 10 pages with view counts while only counting pages with paths matching the regex
    processed_pages = 0
    i = 0
    # store data and save to csv
    with codecs.open("page_views.csv", "w", "utf-8") as f:
        f.write("Page Title|Page Views|Year|Week\n")
        while processed_pages < 10:
            row = response.rows[i]
            match = re.match(r'\/[^\/]+\/(\d{5})-.*', row.dimension_values[0].value)
            if match:
                displayPageName = match.groups()[0] if not args.deanonymize else row.dimension_values[1].value
                print(f"{displayPageName} | {row.metric_values[0].value}")
                f.write(f"{displayPageName}|{row.metric_values[0].value}|{current_year_str}|{current_week}\n")
                processed_pages += 1
            i += 1

if __name__ == "__main__":
    # Authenticate using OAuth 2.0
    credentials = authenticate_with_oauth()
    
    # Fetch and display page view data
    get_ga4_page_view_data(credentials)
