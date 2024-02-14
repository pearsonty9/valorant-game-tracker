from api_client import get_sheets_data
from videos import get_created_by_date

from datetime import datetime, date

SPREADSHEET_ID = "1oV42lMxnIw2hfBfezyqv60j4Ps6Dfze_lvJWd9rz0Kw"
DATA_RANGE = "A1:K23"

def get_video_title(game_data):
    return f"{game_data[0]} {game_data[1]} {game_data[2]} {game_data[4]} {game_data[3]}"

def get_video_titles_from_spreadsheet():
    rows = get_sheets_data(SPREADSHEET_ID, DATA_RANGE)
    # Only add games that were recorded
    video_titles = [get_video_title(row) for row in rows if row[9] == "Yes"]
    # The header row is filtered our by the condition statement so no need to pop
    # video_titles.pop(0)
    return video_titles

def associate_titles_with_videos(video_paths, video_titles):
    associated_files = {}

    # Cases
    # 1: Video timestamp matches game date
    # 2: Video timestamp is a head of title date (doesn't happen due to the solution below)
        # A game was not recorded, title should be skipped
    # 3: Video timestamp is behind title date
        # There are more videos than rows, video should be skipped
    
    # Additionally there could be games that were not recorded that are not at the end of the date range
    # this would cause the video dates to match but be offset by 1 causing all following associations to be wrong
    # The above problem has been temporarily fixed by adding a column to say if the game was recorded until a better solution is found

    title_pointer = 0
    for path in video_paths:
        video_date = get_created_by_date(path).date()
        title_date = datetime.strptime(video_titles[title_pointer].split(" ")[0], '%m/%d/%Y').date()
        if video_date == title_date:
            associated_files[path] = video_titles[title_pointer]
            title_pointer += 1

    return associated_files

def get_game_data():
    _date = input('When was the game? (Default: Today): ')
    agent = input('What agent did you play?: ')
    map = input('What was the map?: ')
    score = input('What was the score?: ')
    rank = input('What is your current rank?: ')
    rr = input('What is your current rr?: ')
    rrDelta = input('How much rr did you win or lose?: ')
    group = input('Who did you play with?: ')
    notes = input('Any additional notes?: ')
    recorded = input('Did you record the game? (y/N): ')

    if _date == "":
        _date = date.today().strftime("%m/%d/%Y")
    if recorded == "y":
        recorded = "Yes"
    elif recorded == "n" or recorded == "":
        recorded = "No"

    return [_date, agent, map, score, rank, rr, rrDelta, group, "", notes, recorded]