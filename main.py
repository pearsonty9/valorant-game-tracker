from videos import group_files_by_created_date, sort_files_into_folders, get_file_paths
from games import associate_titles_with_videos, get_video_titles_from_spreadsheet, get_game_data
from api_client import upload_to_youtube, append_sheet_data, authenticate_client_user

if __name__ == '__main__':
    # files = get_file_paths("d:\\GameReplays")
    # files_grouped_by_date = group_files_by_created_date(files)
    # video_titles = get_video_titles_from_spreadsheet()
    # video_metadata = associate_titles_with_videos(files, video_titles)

    # for video, title in video_metadata.items():
    #     response = input(f'Upload {video} with title "{title}" (y/n): ')
    #     if response == "y":
    #         upload_to_youtube(video, title, "", "unlisted")
    credentials = authenticate_client_user()
    
    while (True):
        print("")
        print("add: create a new game entry")
        user_input = input("> ")

        if user_input == "add":
            game_metadata = get_game_data()
            append_sheet_data(credentials, "1oV42lMxnIw2hfBfezyqv60j4Ps6Dfze_lvJWd9rz0Kw", "Episode 8 Act 1", [game_metadata])
    