# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 11:22:01 2021

@author: JE58234
"""

from selenium import webdriver
import pandas as pd
from datetime import datetime
from selenium.webdriver.chrome.options import Options

#18/01/2021 widening search from price_to=200000 to price_to+300000
url = 'https://www.daft.ie/property-for-sale/galway-city?numBeds_from=2&salePrice_to=300000'

#installing add blocker to speed up the page load 
profile = webdriver.ChromeOptions()
adblockfile = 'adblock.crx'
profile.add_extension(adblockfile)

#set up selenium driver
# 18/01/2021 Left to its own devices chrome will auto update and make the downloaded chromedriver redundant. One way to handle this is
# a driver manager, from webdriver_manager.chrome import ChromeDriverManager, however as the drivers change some elements in the class name's also change.
# this might only be an issue if  you finding elements by class names, there might be better ways of doing this. However as I seem to be stuck with the
# class name the solution I've used is to turn off the chrome auto updates.
driver = webdriver.Chrome(chrome_options=profile)

driver.get(url)

driver.switch_to.active_element

button = driver.find_elements_by_class_name( "cc-modal__btn.cc-modal__btn--daft")

button[1].click()

driver.switch_to.active_element

button2 = driver.find_element_by_class_name('styles__CloseContainer-qea560-4.gUmMhe')

button2.click()

driver.switch_to.active_element


adds = driver.find_elements_by_class_name('Card__Content-x1sjdn-9.hqrqJL')
urlclass = driver.find_elements_by_css_selector('.SearchPage__Result-gg133s-2.hAooid [href]')

#data poitns from the search page
price = []
address =[]
beds =[]
baths = []
size = []
htype = []
urls =[]

for i in adds:
    text = i.text
    dlist = text.splitlines()
    price.append(dlist[0])
    address.append(dlist[1])
    beds.append(dlist[2])
    baths.append(dlist[3])
    if 'm²' not in dlist[4]:
        size.append(None)
        htype.append(dlist[4])
    else:
        size.append(dlist[4])
        htype.append(dlist[5])

for i in urlclass:
    urltext = i.get_attribute('href')
    urls.append(urltext)

df = pd.DataFrame( {'price' : price , 'address' : address , 'beds' : beds , 'baths': baths , 'size' : size , 'htype' : htype , 'urls' : urls} )  
#remove test adds  
df = df[( df['address'].str.contains('Testing ') == False)]
#format price
df['price'] = df['price'].str.extract('([0-9]+,[0-9]+)', expand=True)
df['price'] = df['price'].str.replace(',' , '').astype('int64')
#format beds
df['beds'] = df['beds'].str.replace('Bed' , '').astype('int64')
#format baths
df['baths'] = df['baths'].str.replace('Bath' , '').astype('int64')
#format size
df['size'] = df['size'].str.replace('m²' , '' ).astype('float')

#data points from the individual property page
pdesc = []
pprop = []
pgps = []
pber = []

dfurls = df['urls']
 
for i in dfurls:
    driver.get(i)

    try:
        desc= driver.find_element_by_class_name('PropertyPage__StandardParagraph-sc-14jmnho-8.kDFIyQ').text
        pdesc.append(desc)
    except:
        pdesc.append(None)
          
    try:
        prop= driver.find_element_by_class_name('PropertyDetailsList__PropertyDetailsListContainer-sc-1cjwtjz-0.iOxyyd').text
        pprop.append(prop)
    except:
        pprop.append(None)
          
    try:
        gps = driver.find_element_by_css_selector('.NewButton__ButtonContainer-yem86a-4.eIIlIm.button-container [href]')
        gpsurl = gps.get_attribute('href')
        pgps.append(gpsurl)
    except:
        pgps.append(None)
 
    try:
        ber = driver.find_element_by_class_name('BerDetails__BerImage-sc-14a3wii-0.etlFKB')
        ber = ber.get_attribute('alt')
        pber.append(ber)
    except:
        pber.append(None)
        

        
 
df['desc'] = pdesc
df['pprop'] = pprop
df['pgps'] = pgps
df['ber'] = pber

# format gps
df['pgps'] = df['pgps'].str.extract('(loc:.*)' )
df['pgps'] = df['pgps'].str.replace('loc:' , '')
#30/11/2021 correction , the negative symbol is needed - old replace('\+-' , ' ')
df['pgps'] = df['pgps'].str.replace('\+' , ' ')
df['lat'] = df['pgps'].str.extract('(^.*)\s').astype('float')
df['long'] = df['pgps'].str.extract('\s(.*)').astype('float')


#export df to csv
filename = datetime.today().strftime('%Y-%m-%d')
df.to_csv('./Data/'+filename+'.csv')


