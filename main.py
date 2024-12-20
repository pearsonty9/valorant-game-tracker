import re

from videos import get_file_paths
from games import get_game_data, get_video_title
from api_client import append_sheet_data, authenticate_client_user, get_last_row_from_spreadsheet, update_sheet_data, initialize_upload

SPREADSHEET_ID = "1oV42lMxnIw2hfBfezyqv60j4Ps6Dfze_lvJWd9rz0Kw"
SPEADSHEET_NAME = "Episode 8 Act 2"

if __name__ == '__main__':
    credentials = authenticate_client_user()
    
    while (True):
        previous_game_metadata = get_last_row_from_spreadsheet(credentials, SPREADSHEET_ID)
        game_metadata = get_game_data(previous_game_metadata)
        inserted_data_response = append_sheet_data(credentials, SPREADSHEET_ID, SPEADSHEET_NAME, [game_metadata])
        # Find video file to upload
        files = get_file_paths("d:\\GameReplays")
        most_recent_video = files[-1]
        # Create title for video using game data
        title = get_video_title(game_metadata)
        # Upload video to youtube
        if game_metadata[-1] == "Yes":
            response = input(f'Upload \033[1m{most_recent_video}\033[0m with title "\033[1m{title}\033[0m" (y/N): ')
            if response == "y":
                try:
                    print("Uploading video to YouTube...")                
                    upload_response = initialize_upload(credentials, {"title": title, "description": "", "file": most_recent_video, "privacyStatus": "unlisted"})
                except Exception as e:
                    print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
                # Update game data spreadsheet with video link 
                p = re.compile('^.*![A-Z]+\\d+:([A-Z]+)(\\d+)$')
                match = p.match(inserted_data_response["tableRange"])
                lastcolumn = match.group(1)
                lastrow = match.group(2)
                update_sheet_data(credentials, SPREADSHEET_ID, f"{chr(ord(lastcolumn) - 3)}{int(lastrow)+1}", [[f"https://youtu.be/{upload_response["id"]}"]])