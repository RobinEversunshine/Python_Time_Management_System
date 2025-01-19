from Parameters import notion, record_db_id, genre_data_list
from TimeStatistics import Block, Statistics
from datetime import date, datetime, timedelta
import httpx



def is_connected():
    try:
        # Try connecting to a reliable host with a timeout
        response = httpx.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except httpx.RequestError:
        return False



class Timer():
    def __init__(self):
        self.block = None
        self.orig_block = None

        self.findTodayDiary()
        self.getLastBullet()

        if self.block:
            self.block.evalTime()

        # add one minute when second is larger than 40
        now = datetime.now()
        if now.second > 40:
            now += timedelta(minutes = 1)

        self.now_time = now.strftime("%H:%M")



    # find today's diary page
    def findTodayDiary(self):
        # Get today's date in ISO format
        today = date.today().isoformat()

        # Query the database for today's page
        response = notion.databases.query(
            **{"database_id": record_db_id,
               "filter": {"property": "Day", "date": {"equals": today}}}
        )


        #if no page today, create an empty page
        if len(response["results"]) > 0:
            self.page = response["results"][0]
        else:
            new_page = notion.pages.create(
                parent={"database_id": record_db_id},
                properties = {
                    "Name": {"title": [{"text": {"content": date.today().isoformat()}}]},
                    "Day": {"type": "date", "date": {"start": today}}
                },
                #children = notion.blocks.children.list(block_id = template_id)["results"]
            )

            self.page = new_page
            print("No page found, create new page.")



    # get last bullet block's content and id
    def getLastBullet(self):
        #  Retrieve all child blocks of the page
        all_blocks = notion.blocks.children.list(block_id = self.page['id'])
        blocks = all_blocks.get("results", [])

        if blocks:
            blocks.reverse()

            for block in blocks:
                block_obj = Block(block)

                if block_obj.text:
                    self.block = block_obj
                    self.orig_block = block
                    break



    def endTimer(self):
        if self.block.state == "half":
            start_time_str = self.block.star_time
            text = self.block.text

            start_time = datetime.strptime(start_time_str, "%H:%M")
            end_time = datetime.strptime(self.now_time, "%H:%M")

            #calculate time difference
            time_difference = end_time - start_time
            hour = time_difference.seconds // 3600
            minute = round(time_difference.seconds // 60) - hour * 60


            #update last block
            if hour != 0:
                updated_content = text + f"-{self.now_time} {hour}h{minute}m"
                time_str = f"{hour} hours {minute} minutes"
            else:
                updated_content = text + f"-{self.now_time} {minute}m"
                time_str = f"{minute} minutes"


            notion.blocks.update(
                block_id = self.block.id,
                **{"bulleted_list_item": {"rich_text": [
                            {"type": "text", "text": {"content": updated_content}}
                ]}}
            )


            task_name = text[:-len(start_time_str) - 1]

            print(f'"{task_name}" ended. Total time: {time_str}.')

            self.block.time = round(time_difference.seconds // 60)
            self.block.evalTime(updated_content)
            self.block.name = task_name
            self.block.text = updated_content


            # update block's task, genre and color
            st = Statistics()

            # find by key words
            if self.block.text:
                block_text = self.block.text.lower()


                for key in st.key_words:
                    if len(key.split()) > 1 and key in block_text:
                        self.keyFound(st, key)
                        break
                else:
                    block_texts = block_text.split()
                    for text in block_texts:
                        for key in st.key_words:
                            if key in text:
                                self.keyFound(st, key)
                                break
                        else:
                            continue  # didn't find the key, continue the next text
                        break  # found the key, break the outer loop



            # for task in st.Tasks:
            #     if task.find(self.block):
            #         # if genre exists, add time to it
            #         if task.genre:
            #             self.block.genre_name = task.genre  # update block object genre
            #
            #             # update block color
            #             if self.orig_block["bulleted_list_item"]["color"] == "default":
            #                 for genre_dict in genre_data_list:
            #                     if genre_dict["name"] == task.genre:
            #                         self.block.updateColor(genre_dict["color"])
            #                         break
            #         break

            # make a new page in calendar
            self.block.updateCalendar()

        elif self.block.state == "complete":
            print("Timer has already ended.")
        else:
            print("There is no timer.")




    def keyFound(self, st, key):
        task_name = st.key_words_dict[key]
        self.block.task_name = task_name  # update block object task

        task = st.findTask(task_name)

        # if genre exists, add time to it
        if task.genre:
            self.block.genre_name = task.genre  # update block object genre

            # update block color
            if self.orig_block["bulleted_list_item"]["color"] == "default":
                for genre_dict in genre_data_list:
                    if genre_dict["name"] == task.genre:
                        self.block.updateColor(genre_dict["color"])



    def startTimer(self, input_str : str = "new_task"):
        if self.block and self.block.state == "half":
            self.endTimer()

        # make new timer block content
        block_content = input_str + f" {self.now_time}"

        new_block = [
            {"object": "block", "type": "bulleted_list_item",
             "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": block_content}}]}},
        ]


        #append new block
        notion.blocks.children.append(
            block_id = self.page['id'],
            children = new_block,
        )

        print(f'New timer "{input_str}" started.')
