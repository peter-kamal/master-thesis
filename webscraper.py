# Webscrape Weather Data from climate.weather.gc.ca

# Setup
from selenium import webdriver
from selenium.webdriver.support.ui import Select

chromeOptions = webdriver.ChromeOptions()
driver = webdriver.Chrome()

# Specify URL
url = 'https://climate.weather.gc.ca/prods_servs/cdn_climate_summary_e.html'
driver.get(url)

# Select BC fixed
province = 'BC'
sel_prov = Select(driver.find_element('id','prov'))
sel_prov.select_by_value(province)

# Specify selectors for Year and Month
sel_year = Select(driver.find_element('id', 'intYear'))
sel_month = Select(driver.find_element('id', 'intMonth'))

#Loop over years and months
for i in range(1988,2023):
    # select the year
    sel_year.select_by_value(str(i))
    for j in range(1,13):
       # select the month 
       sel_month.select_by_value(str(j)) 
       # click on download button
       driver.find_element('name', 'btnSubmit').click()
       print('Completed',j,'-',i)


    