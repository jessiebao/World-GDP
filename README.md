# World-GDP
This project plots the GDP by country for a specified year on a world map. 

This project includes three data sets:
- isp_gdp.csv (It includes GDP information from differnt countries in different years. I will call it GDP dataset. )
- pygal_country_list.csv (It maps country codes to country names. It is used by Pygal package. I will call it pygal dataset.)
- isp_country_codes.csv (It includes country codes used by different systems.)

isp_gdp.csv provides all the detailed GDP data and pygal_country_list.csv is used by pygal to map data in the world map. 
However, country codes used by pygapl are different from country codes from GDP dataset. Therefore, isp_country_codes.csv
includes all the codes used by different systems. I will use it as a bridge to map codes from pygal dataset to codes from GDP dataset. 
