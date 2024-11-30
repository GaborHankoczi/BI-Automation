import codecs
import os
import isodate
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Path to your OAuth 2.0 client secrets JSON file
CLIENT_SECRETS_FILE = "client_secret.json"

# Scopes required for accessing YouTube Analytics
SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly","https://www.googleapis.com/auth/youtube.readonly"]

def authenticate_with_oauth():
    """Authenticate and get OAuth credentials."""
    creds = None
    token_file = "yt_token.json"

    # Load existing credentials
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # If no valid credentials, initiate the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return creds



def get_video_duration(youtube, video_id):
    """Get the duration of a video in ISO 8601 format (PT#M#S)."""
    response = youtube.videos().list(
        part="contentDetails",
        id=video_id
    ).execute()
    
    duration = response["items"][0]["contentDetails"]["duration"]
    return duration

def parse_duration(duration):
    """Parse the ISO 8601 duration format and return the duration in seconds."""
    parsed_duration = isodate.parse_duration(duration)
    return parsed_duration.total_seconds()

def does_title_match_any_search_term(title, search_terms):
    """Check if the video title contains any of the search terms."""
    for search_term in search_terms:
        if search_term.lower() in title.lower():
            return True
    return False

# Replace with your API key and credentials file
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
def get_search_terms():
    with codecs.open("search_terms.txt", "r", "utf-8") as file:
        search_terms = file.read().splitlines()
        return search_terms

def get_channel_videos(credentials):
    authenticated_service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    # Step 1: Get the channel's uploads playlist ID
    channel_response = authenticated_service.channels().list(
        part="contentDetails",
        mine=True
    ).execute()

    uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Step 2: Get videos from the uploads playlist
    videos = []
    next_page_token = None

    while True:
        playlist_response = authenticated_service.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,  # Adjust if needed
            pageToken=next_page_token
        ).execute()

        for item in playlist_response["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            videos.append(video_id)

        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break

    # Step 3: Get video details (titles and views)
    video_details = []
    for i in range(0, len(videos), 50):  # You can query up to 50 video IDs at a time
        video_response = authenticated_service.videos().list(
            part="snippet,contentDetails,statistics,status",
            id=",".join(videos[i:i+50])
        ).execute()

        for video in video_response["items"]:
            duration = video["contentDetails"]["duration"]
            duration_seconds = parse_duration(duration)
            #Include only videos with status "public"
            if video["status"]["privacyStatus"] != "public":
                continue

            # Only include videos with durations greater than 60 seconds
            if duration_seconds <= 60:
                continue
            title = video["snippet"]["title"]

            search_terms = get_search_terms()
            # Filter videos by title containing the search term (case-insensitive)
            if does_title_match_any_search_term(title, search_terms):
                # Store remaining video details
                video_details.append({
                    "title": title,
                    "views": video["statistics"].get("viewCount", "0"),
                    "publishedAt": video["snippet"]["publishedAt"],

                })
            

    return video_details

if __name__ == "__main__":
    # Authenticate with OAuth 2.0
    credentials = authenticate_with_oauth()
    
    channel_videos = get_channel_videos(credentials)
    print("Videos in response:" + str(len(channel_videos)))
    # Write to csv file
    with codecs.open("youtube_analytics.csv", "w", "utf-8") as file:
        file.write("title|views|publishedAt\n")
        for video in channel_videos:
            file.write(f"{video['title']}|{video['views']}|{video['publishedAt']}\n")
