from Parameters import *
from datetime import date, time, datetime, timedelta
import re


plain_text_dic = {
    "red" : "{}",
    "blue" : "{}",
}



colored_text_dic = {
    "red" : "\033[31m{}\033[0m",
    "blue" : "\033[34m{}\033[0m",
}



html_text_dic = {
    "red" : '<span style="color:#f44336;">{}</span>',
    "blue" : '<span style="color:#2196f3;">{}</span>',
}



state = "plain"
text_dic = {}


try:
    import ui
    text_dic = html_text_dic
    state = "html"
except ImportError:
    text_dic = colored_text_dic
    state = "colored"



# color text with different methods
def color(text, color):
    return text_dic[color].format(text)



# make hour and minute number from minute value
def getHourMin(time : int):
    hour = time // 60
    minute = time % 60
    return hour, minute



# detect if elements in a list are all empty, if so return false
def listNotEmpty(my_list):
    for a in my_list:
        if a:
            return True
    return False



class Block():
    def __init__(self, block, date_obj : date = date.today()):
        self.id = block["id"]   # block id
        self.page_id = block["parent"]["page_id"]   #page_id

        self.text = ""   # block text
        self.time = 0   # duration of the task
        self.state = ""   # complete of not

        self.start_time = ""   # start time string, like 12:30
        self.start_datetime = None   # start date time object
        self.end_datetime = None   # end date time object

        self.name = ""   # text name without time data
        self.task_name = ""
        self.genre_name = ""

        self.date = date_obj
        self.getBlockContent(block)



    # get block text and linked page
    def getBlockContent(self, block):
        # get bullet list block text
        block_type = block["type"]
        block_content = block[block_type]

        if block_type == "bulleted_list_item":
            text_list = block_content["rich_text"]

            if len(text_list) > 0 and "text" in text_list[0]:
                self.text = text_list[0]["text"]["content"]
                if self.text.endswith(" "):
                    self.text = self.text[:-1]



    # get recorded time
    def getTime(self):
        self.name = self.text

        pattern = re.compile(r"(\d+)(分|小时|时|m|h)")
        matches = pattern.finditer(self.text)

        for match in matches:
            minutes = int(match.group(1))
            time_key = match.group(2)

            if time_key == "分" or time_key == "m":
                self.time += minutes
            elif time_key == "小时" or time_key == "时" or time_key == "h":
                self.time += minutes * 60

            self.name = self.name[:-len(match.group(0))]

        if self.name.endswith(" "):
            self.name = self.name[:-1]
        return self.time



    # get start and end time
    def evalTime(self, text = ""):
        if not text:
            text = self.text

        match = re.search(r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})", text)

        # complete time block
        if match:
            self.state = "complete"
            self.name = self.name[:-len(match.group(0))]
            if self.name.endswith(" "):
                self.name = self.name[:-1]

            start_hour = int(match.group(1))
            start_minute = int(match.group(2))
            end_hour = int(match.group(3))
            end_minute = int(match.group(4))

            self.start_datetime = datetime.combine(self.date, time(start_hour, start_minute))
            self.end_datetime = datetime.combine(self.date, time(end_hour, end_minute))

        else:
            match = re.search(r"(\d{1,2}):(\d{2})", text)
            # half time block, only when time is found and located at last of the block
            if match:
                self.state = "half"


                start_hour = int(match.group(1))
                start_minute = int(match.group(2))

                self.star_time = match.group(0)
                self.name = self.name[:-len(self.star_time)]
                if self.name.endswith(" "):
                    self.name = self.name[:-1]

                self.start_datetime = datetime.combine(self.date, time(start_hour, start_minute))



    def updateColor(self, color: str):
        updated_content = {'bulleted_list_item':{
            "rich_text":[{'type': 'text','text': {'content': self.text}}],
            "color" : color
        }}

        notion.blocks.update(
            block_id = self.id,
            **updated_content
        )



    # make or update calendar page
    def updateCalendar(self):
        if calendar_db_id:
            # I started to record time using siri
            if self.date >= date(2024,12,6):
                if not self.state:
                    self.evalTime()

                if not self.task_name:
                    self.task_name = "Misc"

                properties = None
                if self.start_datetime and self.end_datetime:
                    properties = {
                        "Name": {"title": [{"text": {"content": self.name}}]},
                        "Date Time": {"date": {
                            "start": self.start_datetime.isoformat(),
                            "end": self.end_datetime.isoformat(),
                            "time_zone": "EST"
                        }},
                        "Task": {"select": {"name": self.task_name}},
                        "Duration (minutes)": {"number": self.time},
                        "Relation": {"relation": [{"id": self.page_id}]}
                    }

                # all-day event
                elif not self.start_datetime and not self.end_datetime:
                    properties = {
                        "Name": {"title": [{"text": {"content": self.name}}]},
                        "Date Time": {"date": {
                            "start": self.date.isoformat()
                        }},
                        "Task": {"select": {"name": self.task_name}},
                        "Duration (minutes)": {"number": self.time},
                        "Relation": {"relation": [{"id": self.page_id}]}
                    }



                if properties:
                    if self.genre_name:
                        properties["Genre"] = {"select": {"name": self.genre_name}}

                    notion.pages.create(
                        parent={"database_id": calendar_db_id},
                        properties=properties
                    )

                    print(f'Page "{self.name}" created.')




class Genre():
    def __init__(self, name: str):
        self.name = name
        self.children = []   # list of task objects
        self.daytime = {}   # dictionary of date and everyday's minute value
        self.weektime = {}   # dictionary of first day of a week and every week's overall minute value
        self.alltime = 0   # all time accumulated
        self.Class = ""   # bigger version of genre
        self.color = ""   # block text color

        for genre_dict in genre_data_list:
            if genre_dict["name"] == self.name:
                self.Class = genre_dict["class"]
                self.color = genre_dict["color"]


    def appendChild(self, task):
        self.children.append(task)


    #add time to corresponding day and week
    def addTime(self, time_cal: int, date_str: str, week_str: str):
        # update if there's no such day
        if date_str not in self.daytime:
            self.daytime[date_str] = 0

        # update if there's no such week
        if week_str not in self.weektime:
            self.weektime[week_str] = 0


        self.daytime[date_str] += time_cal
        self.weektime[week_str] += time_cal
        self.alltime += time_cal




class Task():
    #initinal properties
    def __init__(self, name : str, key_words : list, genre : str):
        self.name = name
        self.key_words = key_words
        self.genre = genre
        self.daytime = {}   # dictionary of date and everyday's minute value
        self.weektime = {}   # dictionary of first day of a week and every week's overall minute value
        self.alltime = 0   # all time accumulated
        self.text = {}   # dictionary of date and everyday's text list on this task



    #find key words and add time to it
    def find(self, block : Block):
        #get values and assign
        for key in self.key_words:
            if key in block.text.lower():
                block.task_name = self.name  # update block object task
                return self.name



    #add time found (minute, hour) to value
    def addTime(self, block : Block, date_str: str, week_str: str):
        # update if there's no such day
        if date_str not in self.daytime:
            self.daytime[date_str] = 0
            self.text[date_str] = []

        # update if there's no such week
        if week_str not in self.weektime:
            self.weektime[week_str] = 0

        self.text[date_str].append(block.text)

        time_cal = block.getTime()
        if time_cal:
            self.daytime[date_str] += time_cal
            self.weektime[week_str] += time_cal
            self.alltime += time_cal
            return time_cal



    #print out time for every day
    def printDailyData(self):
        data = []
        for date, time in self.daytime.items():
            #get more readable time
            hour, minute = getHourMin(time)
            data.append({"date" : date,
                         "hour" : hour,
                         "minute" : minute,
                         "text" : self.text[date]})

        return data




# get all blocks from the page
def getPageBlocks(page_id):
    blocks = []

    #query page's children blocks
    result = notion.blocks.children.list(block_id=page_id)
    blocks.extend(result['results'])

    #if has more blocks
    while result["has_more"]:
        result = notion.blocks.children.list(block_id=page_id, start_cursor=result["next_cursor"])
        blocks.extend(result['results'])

    return blocks




class Statistics():
    # get overall data
    def __init__(self):
        self.makeTasks()   # make genre and task list


    # add time data to the print_text
    def addText(self, text : str = ""):
        if state != "html":
            self.print_text += text + "\n"
        else:
            lines = text.split('\n')  # Split by newline
            converted = ''

            for line in lines:
                if not line:
                    line = "&nbsp;"

                converted += f"<pre>{line}</pre>"

            self.print_text += converted + "\n"



    # print out all the time data based on PC or Pythonista on iPhone
    def printText(self):
        if state != "html":
            print(self.print_text)
        else:
            webview = ui.WebView()
            webview.load_html(self.print_text)
            webview.present()



    # get pages from date range input
    def initialize(self, start_date : str = None, end_date : str = None, week = 0, day = 0):
        self.print_text = "" if state != "html" else "<style> body {font-size: 20px; font-family: Arial, sans-serif;} </style>"
        self.weekstart_list = []  # list of every week's start date string
        self.getPages(start_date, end_date, week, day)

        for page in self.pages:
            #generate date object
            date_string = page["properties"]["Day"]["date"]["start"]
            date_obj = date.fromisoformat(date_string)
            self.calculate(page, date_obj)



    #make task list from task data list
    def makeTasks(self):
        self.key_words_dict = {}
        self.key_words = []
        self.Tasks = []
        self.Genres = []
        self.class_dict = {}
        self.Blocks = []

        for item in task_data_list:
            # make tasks
            new_task = Task(item["name"], item["keys"], item["genre"])
            self.Tasks.append(new_task)

            if item["name"] == "Misc":
                self.misc_task = new_task


            # make key word list
            for key in item["keys"]:
                self.key_words_dict[key] = item["name"]
                self.key_words.append(key)




            # make genres
            if item["genre"] != "":
                for genre in self.Genres:
                    if item["genre"] == genre.name:
                        genre.appendChild(new_task)
                        break
                else:
                    new_genre = Genre(item["genre"])
                    self.Genres.append(new_genre)
                    new_genre.appendChild(new_task)

                    if new_genre.Class:
                        self.class_dict[new_genre.Class] = 0

        self.key_words.sort(key=len, reverse=True)



    #find task by name
    def findTask(self, name):
        for task in self.Tasks:
            if task.name == name:
                return task


    # find genre by name
    def findGenre(self, name):
        for genre in self.Genres:
            if genre.name == name:
                return genre



    # get pages from specific time range
    def getPages(self, start_date : str = None, end_date : str = None, week = 0, day = 0):
        if not start_date:
            start_date_obj = date.today()
        else:
            start_date_obj = date.fromisoformat(start_date)

        # 1 is only this week, 2 includes last week
        if week:
            start_date_obj = start_date_obj - timedelta(days=(start_date_obj.weekday() + 1) % 7) - timedelta(7 * (week - 1))

        # 1 is today, 2 includes yesterday
        if day:
            start_date_obj = start_date_obj - timedelta(days = day - 1)


        # make start & end date value
        if not start_date and not week and not day:
            # date on or after the day I start to write down time spent on tasks
            self.start_date = date.fromisoformat("2024-11-03")
        else:
            self.start_date = start_date_obj


        if end_date:
            self.end_date = date.fromisoformat(end_date)
        else:
            self.end_date = date.today()



        start = self.start_date.isoformat()
        end = self.end_date.isoformat()

        self.addText(f"Date range from {color(start,'blue')} to {color(end, 'blue')}.\n")


        filter_properties = {
            "and": [
                {"property": "Day", "date": {"on_or_after": start}},
                {"property": "Day", "date": {"on_or_before": end}}
            ]
        }


        # get page list found
        response = notion.databases.query(
            **{"database_id": record_db_id,
               "filter": filter_properties}
        )

        if len(response["results"]) > 0:
            self.pages = response["results"]
        else:
            raise ValueError("No pages in the time range.")



    # found key word in block text and assign values
    def keyFound(self, block, block_obj, date_str, week_str, key):
        task_name = self.key_words_dict[key]
        block_obj.task_name = task_name  # update block object task

        task = self.findTask(task_name)
        time_cal = task.addTime(block_obj, date_str, week_str)

        if time_cal:
            # if genre exists, add time to it
            if task.genre:
                block_obj.genre_name = task.genre  # update block object genre
                genre = self.findGenre(task.genre)
                genre.addTime(time_cal, date_str, week_str)

                # update block color
                if genre.color and block["bulleted_list_item"]["color"] != genre.color:
                    block_obj.updateColor(genre.color)



    #get data from blocks
    def calculate(self, page, date_obj : date):
        # get Sunday as start of a week
        week_start = date_obj - timedelta(days=(date_obj.weekday() + 1) % 7)
        date_str = date_obj.isoformat()
        week_str = week_start.isoformat()

        # new week
        if week_str not in self.weekstart_list:
            self.weekstart_list.append(week_str)


        # loop every block
        blocks = getPageBlocks(page["id"])
        for block in blocks:
            block_obj = Block(block, date_obj)


            # find by key words
            if block_obj.text:
                # key words that has multiple words
                for key in self.key_words:
                    if len(key.split()) > 1 and key in block_obj.text:
                        self.keyFound(block, block_obj, date_str, week_str, key)
                        break
                else:
                    # key words that has only single word
                    block_texts = block_obj.text.lower().split()

                    for text in block_texts:
                        for key in self.key_words:
                            if key in text:
                                self.keyFound(block, block_obj, date_str, week_str, key)
                                break
                        else:
                            continue   # didn't find the key, continue the next text
                        break   # found the key, break the outer loop
                    else:
                        self.misc_task.addTime(block_obj, date_str, week_str)


            # add to block list if it's valid block
            if block_obj.time:
                self.Blocks.append(block_obj)


        # # add name to pages
        # if not page["properties"]["Name"]["title"]:
        #     notion.pages.update(
        #         page_id=page["id"],
        #         properties={"Name": {"title": [{"text": {"content": date_str}}]}}
        #     )



    # get data from weekly, daily or task & genre list all the time
    def getData(self, genre_list, task_list):
        # get combined list
        combined_list = genre_list + task_list
        combined_list.sort(key=lambda pair: pair[1], reverse=True)

        # split tasks with or without a genre
        children_all = []
        for genre in genre_list:
            children_all += genre[0].children

        children_list = [i for i in combined_list if i[0] in children_all]
        combined_list = [i for i in combined_list if i[0] not in children_all]


        class_dict = self.class_dict.copy()
        all_time = 0

        for item, item_time in combined_list:
            # statistics of all time
            all_time += item_time


            # print out tasks that do not have a genre
            if isinstance(item, Task):
                hour, minute = getHourMin(item_time)
                self.addText(f"\n  •{item.name}: {color(hour,'red')} hours {color(minute,'red')} minutes")


            # print out genre time
            elif isinstance(item, Genre):
                # statistics of every class's time
                if item.Class in class_dict:
                    class_dict[item.Class] += item_time

                hour, minute = getHourMin(item_time)
                self.addText(f"\n•{item.name}: {color(hour,'red')} hours {color(minute,'red')} minutes")

                for task in children_list:
                    if task[0] in item.children:
                        task_time = task[1]
                        hour, minute = getHourMin(task_time)
                        self.addText(f"    --{task[0].name}: {color(hour,'red')} hours {color(minute,'red')} minutes")


        self.addText()
        for class_name in class_dict:
            hour, minute = getHourMin(class_dict[class_name])
            self.addText(f"{color(f'{class_name} Time Recorded:','blue')}  {color(hour,'red')} hours {color(minute,'red')} minutes")

        hour, minute = getHourMin(all_time)
        self.addText(f"\n{color('All Time Recorded:','blue')}  {color(hour,'red')} hours {color(minute,'red')} minutes")
        self.addText("\n\n//////////////////////////////////////////////////\n")



    # print overall time of every week
    def printAllData(self):
        # title
        self.addText(f"\nAll Time Recorded Data:")

        # get genre data
        genre_list = []
        for genre in self.Genres:
            all_time = genre.alltime
            if all_time != 0:
                genre_list.append([genre, all_time])

        # get task data
        task_list = []
        for task in self.Tasks:
            all_time = task.alltime
            if all_time != 0:
                task_list.append([task, all_time])

        self.getData(genre_list, task_list)



    # print overall time of every week
    def printWeeklyData(self):
        weekly_data_rev = self.weekstart_list
        weekly_data_rev.reverse()

        for week_str in weekly_data_rev:

            #title
            self.addText(f"\nWeek starting {color(week_str,'blue')}:")

            # get genre data
            genre_list = []
            for genre in self.Genres:
                if week_str in genre.weektime:
                    weekly_time = genre.weektime[week_str]
                    if weekly_time != 0:
                        genre_list.append([genre, weekly_time])

            #get task data
            task_list = []
            for task in self.Tasks:
                if week_str in task.weektime:
                    weekly_time = task.weektime[week_str]
                    if weekly_time != 0:
                        task_list.append([task, weekly_time])

            self.getData(genre_list, task_list)



    # print overall time of every week
    def printDailyData(self):
        # make reversed day list
        days = self.end_date - self.start_date

        day_list = [(self.start_date + timedelta(days=i)).isoformat() for i in range(days.days + 1)]


        for day_str in day_list:

            #title
            self.addText(f"\nDay {color(day_str,'blue')}:")

            # get genre data
            genre_list = []
            for genre in self.Genres:
                if day_str in genre.daytime:
                    day_time = genre.daytime[day_str]
                    if day_time != 0:
                        genre_list.append([genre, day_time])

            #get task data
            task_list = []
            for task in self.Tasks:
                if day_str in task.daytime:
                    day_time = task.daytime[day_str]
                    if day_time != 0:
                        task_list.append([task, day_time])

            self.getData(genre_list, task_list)



    def printFromData(self, data : list):
        # print out
        for line in data:
            date = line["date"]
            hour = line["hour"]
            minute = line["minute"]
            text_list = line["text"]


            if listNotEmpty(text_list):
                if hour == 0:
                    self.addText(f"\n•{color(date, 'blue')}: {color(minute,'red')} minutes")
                else:
                    self.addText(f"\n•{color(date, 'blue')}: {color(hour,'red')} hours {color(minute,'red')} minutes")

                for text in text_list:
                    if text:
                        self.addText(f"    --{text}")



    #print time of a certain task or genre every day
    def printSingleTaskData(self, name : str):
        data = []
        #if is genre
        genre = self.findGenre(name)
        if genre:
            tasks = genre.children
            for task in tasks:
                data += task.printDailyData()

            data.sort(key=lambda x: x["date"], reverse = True)
            self.printFromData(data)

        #if is task
        else:
            task = self.findTask(name)
            if task:
                data = task.printDailyData()
                self.printFromData(data)



    def updateCalendar(self):
        # delete related pages
        filter_properties = {"or": []}

        for page in self.pages:
            filter_properties["or"].append({"property": "Relation","relation": {"contains": page["id"]}})

        all_results = []
        start_cursor = None


        while True:
            # Query database with filter and pagination
            response = notion.databases.query(
                database_id = calendar_db_id,
                filter = filter_properties,
                start_cursor = start_cursor  # Pagination cursor
            )

            # Append results
            all_results.extend(response["results"])

            # Check if there are more pages to fetch
            if response.get("has_more"):
                start_cursor = response["next_cursor"]  # Update cursor for the next request
            else:
                break

        print(f"Found {len(all_results)} pages.")


        if len(all_results) > 0:
            pages = all_results

            # delete pages found
            deleted_count = 0
            for page in pages:
                # if not page["archived"]:
                notion.pages.update(page["id"], archived=True)
                print(f"Deleted page {page['id']}")
                deleted_count += 1

            print(f"Deleted {deleted_count} pages.")


        # add new pages
        for block in self.Blocks:
            block.updateCalendar()




def updateToday():
    st = Statistics()
    st.initialize(day=1)
    st.printDailyData()
    st.printText()
    st.updateCalendar()



if __name__ == "__main__":
    st = Statistics()
    st.initialize(week=2)
    # st.initialize(start_date="2024-12-01", end_date="2024-12-31")
    # st.printAllData()
    st.printWeeklyData()
    # st.printDailyData()
    # st.printSingleTaskData("Commute & Transportation")
    st.printText()
    # st.updateCalendar()
# updateToday()



#                              #%=                    *%%%%%
#                            -+*              .#%%%%#:. .-++ #@*
#                           %. %        -#%@%%   :          %=  @%
#                   @%:     %  %    *@@+          %          #.   #@
#                   %  %%%%%%%%%%%#:              ::          -   # %%
#                   @                             % :#             = @:
#                   @                            %:  #                *
#                    *             @.           %   @           %#   .%
#                @%@%:             *%         %   %@%           .@*   %
#                -%               @.%  %    =  %@.@              .%%  %
#                 %:         -%@%%#% .#     @% %%       #        + :- @
#                  @*    %@%  +* %   %   #@  #@    .   =        .@  @ %:
#                   #% %@   @  %=   %   @   +         % %      #%  @   @#
#                 %    %  @.  @        %%  %@@@@@@@@@        +@  @-   %%
#                %        @  %     -@@#              %@@@%#%@##%%@@ @%
#                @           %   @@    #%@%%%*:           *%= #   *
#                 @         #* @.             .        %=         %%
#                  %         @ =.%#@@@@@@%@ %%@           @@@@@@@%@#
#                   @ @- %@*  @   %   %:%-%   @          -@%:%    -.
#                    % #   %  @       %%%%-   @          %@+*%   =@-
#                    %=%   %  @     %% .%%    +       %    @@  % @ %
#                     @ @ :%  %%    % %               %       *- @ %
#                   %@   % %   @     -@                       @  @ +-
#                 .%%%% %  @   :@   %   @             @*    % * @:* @
#                       %  @    @#   @*  @           +     =#%  %**.%*
#                      %  @% %   @     .        .=+*+=-.       @+#+% @
#                     @  %#  %   @             %%     @+      @. %*  @:             .
#                     @.@:   %   =%             *#.%@:      %% @#.   %=           ++@
#                      %     #%   @ @%                    #@     @   @              @
#                       %@   #%   % % @@@#              @@        =%%*         .@   =
#                         %@+ %   @  % .@#@@@@%      @@%           @           %+       *@
#                           %%%  -%  @      #   %@@@                           @=:       %
#                             @  @   @      #% -                              - ==%
#                              #=@%-%     .   -%%@@@%%##                      @:. :#%-
#                          @@  @@    #%      %*      : @ *                   % %       @
#                      %@@%  :#+       %@  :%     +=%@    @.                 @  % -@  @
#                     -     -*-*%%%%+    @% @ -%%@@=       %%               *%  --- .%
#                      =            -#%%@    :          @    @#           .%% *  % @=
#                     %    :           #  %@@@         %       %%          #+% @%%%
#                    %      .%      :% : %  -:=%@      :*                  @ #=
#                   *-        %   -%  =.  %  @ # =@     @                 # . %
#                  %          %#  #   =   %   % *  @    @                 % #+.
#                 #-           *  :+    %%    ##  + @   :               .@ @ %
#                                  @   %+      *@    @.                .%  - .
#                                  @  @          :@@% %%
#                                 = %%                .%@%
#                                 @@



