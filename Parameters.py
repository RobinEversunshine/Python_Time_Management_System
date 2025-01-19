from notion_client import Client


# initialize
notion = Client(auth="secret_e5VwPByosWlI1dwF6i7WFabyAKodNUrOW5k1HDp6PKk")
record_db_id = "cca33204-66b7-4062-affa-a5fbb3805d39"
calendar_db_id = "15de227c997d80a095c2d4c71528ac82"



# used for text color
genre_data_list = [
    {"name": "Work & School",
     "class" : "Useful",
     "color" : "purple"},

    {"name": "Language",
     "class" : "Useful",
     "color" : "red"},

    {"name": "Primary Study",
     "class": "Useful",
     "color" : "orange"},

    {"name": "Secondary Study",
     "class": "Useful",
     "color" : "yellow"},

    {"name": "Housework",
     "class": "Housework",
     "color" : "green"},

    {"name": "Entertainment",
     "class": "Entertainment",
     "color" : "blue"},
]




# task names and key words. all key words should be lower case.
task_data_list = [

    {"name": "Main Projects",
     "keys" : ["lab"],
     "genre" : "Work & School"},

    {"name": "Side Projects",
     "keys" : ["side"],
     "genre" : "Work & School"},

    {"name": "Misc Work",
     "keys" : ["work"],
     "genre" : "Work & School"},



    {"name": "French",
     "keys" : ["french", "法语", "français"],
     "genre" : "Language"},

    {"name": "Japanese",
     "keys" : ["japanese", "日语", "日本語"],
     "genre" : "Language"},

    {"name": "English Speaking & Presentation",
     "keys" : ["english", "英语", "口语", "语料"],
     "genre" : "Language"},



    {"name": "Coding",
     "keys" : ["programm", "code"],
     "genre" : "Primary Study"},

    {"name": "Houdini Stuff",
     "keys" : ["hou"],
     "genre" : "Primary Study"},

    {"name": "Misc Study",
     "keys" : ["study"],
     "genre" : "Primary Study"},

    {"name": "Drawing",
     "keys": ["drawing", "绘画"],
     "genre": "Primary Study"},



    {"name": "Writing Emails",
     "keys" : ["mail"],
     "genre" : "Secondary Study"},

    {"name": "Read Books",
     "keys" : ["read"],
     "genre" : "Secondary Study"},

    {"name": "Misc Read & Write",
     "keys" : ["diaries", "writ", "rw"],
     "genre" : "Secondary Study"},

    {"name": "Piano",
     "keys": ["piano", "钢琴"],
     "genre": "Secondary Study"},

    {"name": "Exercise",
     "keys" : ["exercis", "gym", "健身", "锻炼"],
     "genre" : "Secondary Study"},



    {"name": "Animated Short Films",
     "keys": ["short film", "动画短片"],
     "genre": ""},



    {"name": "Cooking",
     "keys" : ["cooking", "ingredient", "做饭", "食材"],
     "genre" : "Housework"},

    {"name": "Washing",
     "keys" : ["wash", "laundry", "shower", "haircut", "tidy", "衣物", "洗"],
     "genre" : "Housework"},

    {"name": "Shopping",
     "keys": ["shop", "购物"],
     "genre": "Housework"},

    {"name": "Misc housework",
     "keys": ["housework", "rubbish"],
     "genre": "Housework"},



    {"name": "Film & Animation",
     "keys" : ["film"],
     "genre" : "Entertainment"},

    {"name": "Video Games",
     "keys" : ["game"],
     "genre" : "Entertainment"},

    {"name": "Activities",
     "keys" : ["act"],
     "genre" : "Entertainment"},

    {"name": "News",
     "keys": ["news"],
     "genre": "Entertainment"},

    {"name": "Cellphone",
     "keys": ["cellphone", "手机"],
     "genre": "Entertainment"},

    {"name": "Misc Entertainment",
     "keys": ["music", "video"],
     "genre": "Entertainment"},



    {"name": "Commute & Transportation",
     "keys" : ["commute", "walk", "car"],
     "genre" : ""},

    {"name": "Misc",
     "keys" : [],
     "genre" : ""},
]




def notionFormulaGenre():
    formula = "ifs("
    for task in task_data_list:
        formula += f'prop("Task")=="{task["name"]}", "{task["genre"]}",\n'

    formula = formula[:-2] + "\n)"
    print(formula)


def notionFormulaClass():
    formula = "ifs("
    for genre in genre_data_list:
        formula += f'prop("Genre (auto)")=="{genre["name"]}", "{genre["class"]}",\n'

    formula = formula[:-2] + "\n)"
    print(formula)


if __name__ == "__main__":
    notionFormulaGenre()
    print()
    notionFormulaClass()
