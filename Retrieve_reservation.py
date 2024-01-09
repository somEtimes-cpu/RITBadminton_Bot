from email.encoders import encode_7or8bit
from http.server import executable
from re import I, L, X
from subprocess import STARTUPINFO
from tracemalloc import start
from xml.dom import HierarchyRequestErr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from dataclasses import dataclass
import datetime
from object_classes import reserved_event

    
    

def retreive_reservations():
    driver = webdriver.Edge()
    driver.get('https://reserve.rit.edu/')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "rit-shib-login-link"))).click()

    print(f"I'm at {driver.current_url}")
    driver.switch_to.window(driver.window_handles[-1])
    print(f"I'm at {driver.current_url}")
    
    with open('.gitignore/RIT_credentials.json') as f:
        f.data = json.load(f)
    username = f.data.get('username')
    password = f.data.get('password')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "ritUsername"))).send_keys(username)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "ritPassword"))).send_keys(password)

    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, "_eventId_proceed"))).click()

    print(f"I'm at {driver.current_url}")
    #driver.find_element(By.XPATH, "(//a[@title='Locations'])[1]").click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "(//a[@title='Locations'])[1]"))).click()
    time.sleep(2)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Add/Remove Locations']"))).click()
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@aria-label='Hale-Andrews Student Life Center (023)']"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(@class,'btn btn-primary')])[1]"))).click()
    time.sleep(3)
    gymCourt2_id = driver.find_element(By.XPATH, "//div[@title='HAC-A450 Main Gym Court 2']").get_attribute('data-room-id')
    gymCourt3_id = driver.find_element(By.XPATH, "//div[@title='HAC-A450 Main Gym Court 3']").get_attribute('data-room-id')
    gymCourt4_id = driver.find_element(By.XPATH, "//div[@title='HAC-A450 Main Gym Court 4']").get_attribute('data-room-id')
    gymCourt5_id = driver.find_element(By.XPATH, "//div[@title='HAC-A450 Main Gym Court 5']").get_attribute('data-room-id')
    Court_2 = []
    Court_3 = []
    Court_4 = []
    Court_5 = []
    print(gymCourt2_id, gymCourt3_id, gymCourt4_id, gymCourt5_id)
    gymcourts = {gymCourt2_id:Court_2, gymCourt3_id:Court_3, gymCourt4_id:Court_4, gymCourt5_id:Court_5}
    events = driver.find_elements(By.CLASS_NAME, "event-container")
    for event in events:
        roomID = event.get_attribute('data-room-id')
        if roomID in gymcourts.keys():
            starting_timez = 'AM'
            ending_timez = 'AM'
            is_private = True if event.get_attribute('title') == 'Private' else False
            starting_px = int(event.get_attribute('style').split('px')[0].split(':')[1].strip())
            width = int(event.find_element(By.CLASS_NAME, 'event').get_attribute('style').split('px')[0].split(':')[1].strip())
            ending_px = starting_px + width
            starting_hr, starting_min = starting_px // 60, starting_px % 60
            ending_hr, ending_min = ending_px // 60, ending_px % 60
            if starting_hr >= 12:
                if starting_hr != 12:
                    starting_hr -= 12
                    starting_timez = 'PM'
            if ending_hr >= 12:
                if ending_hr != 12:
                    ending_hr -= 12
                    ending_timez = 'PM'
                    
            if starting_min == 0:
                starting_min = '00'
            if ending_min == 0:
                ending_min = '00'
                
            event_name = 'Private'
            if not is_private:
                driver.execute_script("arguments[0].scrollIntoView();", event)
                driver.execute_script("arguments[0].click();", event)
                element = WebDriverWait(driver, 20).until((EC.visibility_of_element_located((By.ID, "detailsContainer"))))
                event_element = WebDriverWait(element, 20).until((EC.presence_of_element_located((By.ID, "event-name"))))
                event_name = element.find_element(By.ID, "event-name").get_attribute('aria-label').split('Event Name')[1].strip()
                time.sleep(2)
                WebDriverWait(driver, 20).until((EC.element_to_be_clickable((By.ID, "close-btn")))).click()
                time.sleep(2)
            gymcourts.get(roomID).append(reserved_event(event_name=event_name, starting_hr=str(starting_hr), ending_hr=str(ending_hr), 
                                                        starting_min=str(starting_min), ending_min=str(ending_min), starting_timez=starting_timez, 
                                                        ending_timez=ending_timez, starting_px=starting_px))
            print(f"{starting_hr}:{starting_min} {starting_timez} - {ending_hr}:{ending_min} {ending_timez}, {event.get_attribute('data-room-id')}, {event_name}")
    
    driver.maximize_window()
    time.sleep(2)
    driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.XPATH, "//div[@title='HAC-A450 Main Gym Court 5']"))
    driver.save_screenshot(f"Reservations_files/reservations_{datetime.datetime.today().strftime('%Y-%m-%d')}.png")
    time.sleep(2)
    
    return gymcourts
    
    
   # write_file(gymcourts, gymCourt2_id, gymCourt3_id, gymCourt4_id, gymCourt5_id)


if __name__ == "__main__":
    retreive_reservations()