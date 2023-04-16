from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

from math import ceil
import time
import pandas as pd

from webdriver_manager.chrome import ChromeDriverManager 

# instantiate options 
options = webdriver.ChromeOptions()  
# run browser in headless mode 
options.headless = True 
 


column_names = ['STT', 'Ngay', 'KLGD - Khop lenh', 'KLGD - Thoa thuan', 'KGLD - Tong', 'GTGD - Khop lenh', 'GTGD - Thoa Thuan', 'GTGD - Tong', 'Thi truong - % KGLD', r'Thi truong - % GTGD', 'NTD nuoc ngoai - KL mua', 'NTD nuoc ngoai - GT mua', 'NTD nuoc ngoai - KL ban', 'NTD nuoc ngoai - GT ban', 'NTD nuoc ngoai - KL con duoc phep nam giu']


def find_number_of_pages(table, records_per_page):
    records_str = table.find_element(By.ID, 'd_total_rec').text
    records = [int(s) for s in records_str.split(' ') if s.isdigit()][0]

    number_of_pages = ceil(records/records_per_page) 
    
    return number_of_pages


def switch_to_page_4(wait, driver):
    page4 = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="_TabLi_4"]')) #_TabLi_4
        )
    driver.execute_script("arguments[0].click()", page4)
    

def select_number_of_records(wait, number_of_records = 50):
    select = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="ThongTinTongHopdivNumberRecordOnPage"]')) #ThongTinTongHopdivNumberRecordOnPage
    )
    select = Select(select)
    select.select_by_value(str(number_of_records))
    
    
def get_rows(table):
    body = WebDriverWait(table, 30, ignored_exceptions=ignored_exceptions).until(
        EC.visibility_of_element_located((By.TAG_NAME, 'tbody'))
    )
    
    rows = WebDriverWait(body, 30, ignored_exceptions=ignored_exceptions).until(
        EC.visibility_of_all_elements_located((By.TAG_NAME, 'tr'))
    )
    
    return rows


def row_to_record(row):
    
    record = row.text.split(' ')
    record = [v.replace('.', '').replace(',','.') for v in record] # reformat number
    return record


def turn_pages(driver, table, current_page):
    pages = table.find_element(By.ID,'d_number_of_page').find_elements(By.TAG_NAME, 'li')
    
    next_page_num = str(current_page + 1)
    next_page_button = [p for p in pages if p.text == next_page_num][0]
    
    driver.execute_script("arguments[0].click()", next_page_button)
    print('switch to page', next_page_num)


with open('list_of_stocks.txt', 'r') as f:
    stocks = f.read()   
list_of_stocks = stocks.split(',\n')



driver = webdriver.Chrome(service=ChromeService( 
    ChromeDriverManager().install()), options=options) 
wait = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions)

for stock in list_of_stocks:
    url = f'https://hnx.vn/cophieu-etfs/chi-tiet-chung-khoan-ny-{stock}.html'
    print(url)
    
    driver.get(url)

    # switch to page 4
    switch_to_page_4(wait, driver)
    
    # show 50 records per page
    select_number_of_records(wait, number_of_records = 50)
    time.sleep(3)
    
    # table =  driver.find_element(By.ID,'ThongTinTongHop_divDataTables')
    # number_of_pages = find_number_of_pages(table, 50)
    
    number_of_pages = 2 # as of April: there's 60 records -> 2 pages
    
    # get the table rows
    all_records = []

    for page in range(1, number_of_pages+1):
        table =  wait.until(
            EC.visibility_of_element_located((By.ID,'ThongTinTongHop_divDataTables'))
        )
        
        rows = get_rows(table)
        
        for r in rows:
            record = row_to_record(r)
            all_records.append(record)
            print(record)
            
        if page < number_of_pages: # if not last page: turn page
            turn_pages(driver, table, current_page = page)
            time.sleep(10) # wait 10 seconds for the new page to load
        
    # save result as csv
    df = pd.DataFrame(all_records, columns=column_names)
    df.to_csv(f'data\{stock}.csv', index = False)

# agg = driver.find_element(By.ID, "div_chartdata_thongtintonghop").find_elements(By.TAG_NAME, "td")

# for i in agg:
#     print(i.text)


