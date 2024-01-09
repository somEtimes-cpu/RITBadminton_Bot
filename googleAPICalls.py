import json
import asyncio
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource
import datetime
import os

async def is_valid_RIT_username(people_client: Resource, ritUsername: str) -> (bool, set):
    rit_gmail = f"{ritUsername}@g.rit.edu"
    names = list()
    result = (people_client.people().searchDirectoryPeople(
        query=rit_gmail,
        readMask="emailAddresses",
        sources="DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE")).execute()
    if not result:
        return False, names
    
    for person in result.get('people', []):
        response = people_client.people().get(resourceName=person.get("resourceName"), personFields="names").execute()
    
    if "names" in response and response["names"]:
        names.append(response["names"][0].get("displayName"))
    
    return True, names

async def get_current_term() -> str:
    with open('private_files/discord_config.json', 'r') as f:
        data = json.load(f)
        dates = [datetime.datetime.today().strftime('%m/%d'), data['spring_start'], data['spring_end'], data['fall_start'], data['fall_end']]
    daysInYear = list()
    current_term = None
    if dates[0] == "02-29":
        dates[0] = "02-28"
    for date in dates:
        daysInYear.append(datetime.datetime.strptime(date, '%m/%d').timetuple().tm_yday)

    #For testing
    daysInYear[0] = datetime.datetime.strptime("11/29", '%m/%d').timetuple().tm_yday

    if daysInYear[0] >= daysInYear[1] and daysInYear[0] <= daysInYear[2]:
        current_term = "Spring"
    elif daysInYear[0] >= daysInYear[3] and daysInYear[0] <= daysInYear[4]:
        current_term = "Fall"
    return current_term
    
    
async def is_due_paid(gmail_client: Resource, name:str) -> bool:
    paid = False
    current_term = await get_current_term()
    current_year = datetime.datetime.today().year
    current_year = 2023 #For testing
    with open('private_files/discord_config.json', 'r') as f:
        data = json.load(f)
        gmail_query = data["gmail_filter_query"]
        dates = [data['spring_start'], data['spring_end'], data['fall_start'], data['fall_end']]
    gmail_query = gmail_query.replace("$NAME$", name)
    for n in range(len(dates)):
        dates[n] = f"{current_year}/{dates[n]}"
    if current_term == "Spring":
        gmail_query = f"{gmail_query} after:{dates[0]} before:{dates[1]}"
    elif current_term == "Fall":
        gmail_query = f"{gmail_query} after:{dates[2]} before:{dates[3]}"
    results = (gmail_client.users().messages().list(userId="me", q=gmail_query, includeSpamTrash=True)).execute()
    if results.get('resultSizeEstimate') > 0:
        paid = True
    return paid


async def main():
    """
    Testing Purpose
    """
    SCOPE = ["https://www.googleapis.com/auth/contacts.readonly", 
                        "https://www.googleapis.com/auth/directory.readonly",
                        "https://www.googleapis.com/auth/gmail.settings.basic",
                        "https://www.googleapis.com/auth/gmail.modify"
                        ]
    if os.path.exists("private_files/googleAPItoken.json"):
        APIcreds= Credentials.from_authorized_user_file("private_files/googleAPItoken.json", SCOPE)
        if not APIcreds or not APIcreds.valid:
            if APIcreds and APIcreds.expired and APIcreds.refresh_token:
                APIcreds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("private_files/client_secret.json", SCOPE)
                APIcreds = flow.run_local_server(port=0)
            with open("private_files/googleAPItoken.json", "w") as f:
                f.write(APIcreds.to_json())
    
    people_client = build("people", "v1", credentials=APIcreds)
    gmail_client = build("gmail", "v1", credentials=APIcreds)

    #print(await is_valid_RIT_username(people_client, "hc5474"))
    print(await is_due_paid(gmail_client, "Wei Cheng Ooh"))
    #print(await get_current_term())


if __name__ == '__main__':
    asyncio.run(main())