# import libraries
import os
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import datetime

metals = ['Aluminium', 
          'Copper',
          'Lead',
          'Nickel',
          'Tin',
          'Zinc']
metals_url = ['https://www.lme.com/en/Market-data/Reports-and-data/Commitments-of-traders/Aluminium',
              'https://www.lme.com/en/Market-data/Reports-and-data/Commitments-of-traders/Copper',
              'https://www.lme.com/en/Market-data/Reports-and-data/Commitments-of-traders/LME-Lead',
              'https://www.lme.com/en/Market-data/Reports-and-data/Commitments-of-traders/LME-Nickel',
              'https://www.lme.com/en/Market-data/Reports-and-data/Commitments-of-traders/LME-Tin',
              'https://www.lme.com/en/Market-data/Reports-and-data/Commitments-of-traders/LME-Zinc']

for i, metal in enumerate(metals): # loop through each metal  
    html_text = requests.get(metals_url[i]).text    
    soup = BeautifulSoup(html_text, 'lxml')
    body = soup.find_all(class_ = "link-download" )

    match_string = re.search("Commitments of Traders Report -(.*)", str(body[0])).group(1) 
    date = re.search("(\d{2})", match_string).group(1).strip()
    month = re.search("\d{2}\s(\w*)", match_string).group(1).strip()
    year = re.search("(\d{4})", match_string).group(1).strip()

    date_on_report = datetime.datetime.strptime(f"{date}-{month}-{year}","%d-%B-%Y").date()

    less_four_days = datetime.timedelta(days=4)
    last_friday = datetime.date.today() - less_four_days

    if last_friday == date_on_report: # check if the file date is last friday or not
        download_link = f"https://www.lme.com{body[0]['href']}" # download link for latest file    
        r = requests.get(download_link, allow_redirects=True) # download the excel file
        open('file.xls', 'wb').write(r.content)
        report_data = pd.read_excel('file.xls')
        relevant_data = report_data.iloc[8:17, 3:11].T
        relevant_data_in_one_row = pd.DataFrame(relevant_data.to_numpy().flatten()).T
        relevant_data_in_one_row.insert(0, 'Date', date_on_report) #add the report date         
        relevant_data_in_one_row.to_csv(f"{metal}_LME.csv", mode='a', index=False, header = False) # write to csv

        os.remove('file.xls')
