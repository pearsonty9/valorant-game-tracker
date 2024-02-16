import re

from videos import group_files_by_created_date, sort_files_into_folders, get_file_paths
from games import associate_titles_with_videos, get_video_titles_from_spreadsheet, get_game_data, get_video_title
from api_client import upload_to_youtube, append_sheet_data, authenticate_client_user, get_last_row_from_spreadsheet, update_sheet_data

SPREADSHEET_ID = "1oV42lMxnIw2hfBfezyqv60j4Ps6Dfze_lvJWd9rz0Kw"

if __name__ == '__main__':
    credentials = authenticate_client_user()
    
    while (True):
        print("")
        print("add: create a new game entry")
        user_input = input("> ")

        if user_input == "add":
            previous_game_metadata = get_last_row_from_spreadsheet(credentials, "1oV42lMxnIw2hfBfezyqv60j4Ps6Dfze_lvJWd9rz0Kw")
            game_metadata = get_game_data(previous_game_metadata)
            inserted_data_response = append_sheet_data(credentials, "1oV42lMxnIw2hfBfezyqv60j4Ps6Dfze_lvJWd9rz0Kw", "Episode 8 Act 1", [game_metadata])
            # Find video file to upload
            files = get_file_paths("d:\\GameReplays")
            most_recent_video = files[-1]
            # Create title for video using game data
            title = get_video_title(game_metadata)
            # Upload video to youtube
            if game_metadata[-1] == "Yes":
                response = input(f'Upload \033[1m{most_recent_video}\033[0m with title "\033[1m{title}\033[0m" (y/n): ')
                if response == "y":
                    print("Uploading video to YouTube...")
                    upload_response = upload_to_youtube(credentials, most_recent_video, title, "", "private")
                    # Update game data spreadsheet with video link 
                    p = re.compile('^.*![A-Z]+\\d+:([A-Z]+)(\\d+)$')
                    match = p.match(inserted_data_response["tableRange"])
                    lastcolumn = match.group(1)
                    lastrow = match.group(2)
                    update_sheet_data(credentials, SPREADSHEET_ID, f"{chr(ord(lastcolumn) - 3)}{int(lastrow)+1}", [[f"https://youtu.be/{upload_response["id"]}"]])
        elif user_input == "test":
            pass
        else:
            exit()