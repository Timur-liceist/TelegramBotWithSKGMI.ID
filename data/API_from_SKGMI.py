import json

import requests


def addRecord(tx, header, skgmiId, using_file=False):
    if using_file:
        path = "diplom.png"
        file = open(path, 'rb')
        response = requests.post(
            f"""http://my.expasys.group/DesktopModules/Expasys/BotApi/API/UserData/AddRecord?text={tx}&title={header}&skgmiId={skgmiId}""",
            files={'logo': file})
        return response.text
    else:
        response = requests.post(
            f"""http://my.expasys.group/DesktopModules/Expasys/BotApi/API/UserData/AddRecord?text={tx}&title={header}&skgmiId={skgmiId}""")
        return response.text



def getSession(skgmiId):
    response = requests.get(
        f"https://my.expasys.group/DesktopModules/Expasys/BotApi/API/Performance/GetSession?skgmiId={skgmiId}")
    print(response)
    return json.loads(response.json())


def getRating(skgmiID):
    response = requests.get(
        f"https://my.expasys.group/DesktopModules/Expasys/BotApi/API/Performance/GetRating?skgmiId={skgmiID}")
    # return json.loads(response.json())
    return json.loads(response.json())


def getSkgmiIdFIO(fio):
    response = requests.get(
        f'https://my.expasys.group/DesktopModules/Expasys/BotApi/API/UserData/ByDisplayName?name={fio}')
    return json.loads(response.json())


def ValidateCode(skgmiId, code, telegram_id):
    response = requests.get(f"https://my.expasys.group/DesktopModules/Expasys/BotApi/API/Confirmation/ValidateCode"
                            f"?skgmiId={skgmiId}&code={code}&telegramId={telegram_id}")
    return response.json()


def genarateCodeAndSendOnEmail(name_user):
    # code = requests.post(f"{name_user}/DesktopModules/Expasys/BotApi/API/Confirmation/GenerateCode")
    code = requests.post(
        f"https://my.expasys.group/DesktopModules/Expasys/BotApi/API/Confirmation/GenerateCode?skgmiId={name_user}")
    print(code)
    return code.json()


def getLessonsForStudent(skgmiId, month, day, year):
    if len(str(month)) == 1:
        month = "0" + str(month)
    if len(str(day)) == 1:
        month = "0" + str(day)
    response = requests.get(
        # f"https://my.expasys.group/DesktopModules/Expasys/BotApi/API/Schedule/GetSchedule?skgmiId=timur@skgmi.id&date=2022-04-11%2014:58:22.5633333")
    f"https://my.expasys.group/DesktopModules/Expasys/BotApi/API/Schedule/GetSchedule?skgmiId=timur@skgmi.id&date={year}-{month}-{day}")

    return json.loads(response.json())


def getUserName(skgmiId):  # ByUsername
    response = requests.get(
        f"https://my.expasys.group/DesktopModules/Expasys/BotApi/API/UserData/ByUsername?skgmiId={skgmiId}")
    return json.loads(response.json())
