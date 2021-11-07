"""
Project for Week 3 of "Python Data Visualization".
Unify data via common country name.

Be sure to read the project description page for further information
about the expected behavior of the program.
"""

import csv
import math
import pygal
import re

gdpinfo = {
        "gdpfile": "isp_gdp.csv",        # Name of the GDP CSV file
        "separator": ",",                # Separator character in CSV file
        "quote": '"',                    # Quote character in CSV file
        "min_year": 1960,                # Oldest year of GDP data in CSV file
        "max_year": 2015,                # Latest year of GDP data in CSV file
        "country_name": "Country Name",  # Country name field name
        "country_code": "Country Code"   # Country code field name
    }

def read_csv_as_dict(filename, keyfield, valuefield, separator, quote):
    """
    Parameters
    ----------
    csv_file : a string that represents a csv file
    key_column : the key of the output dictionary
    separator: character to separate columns
    quote: character to quote special characters
    Returns
    -------
    A dictionary that maps the field names 
    to the field values for that row
    """
    result = {}
    with open(filename, newline = '') as file:
        reader = csv.DictReader(file, delimiter = separator, quotechar = quote)
        for row in reader: 
            result[row[keyfield]] = row[valuefield]
    return result

def read_csv_as_nested_dict(filename, keyfield, separator, quote):
    """
    Parameters
    ----------
    csv_file : a string that represents a csv file
    key_column : the key of the output dictionary
    separator: character to separate columns
    quote: character to quote special characters
    Returns
    -------
    A nested dictionary where the outer dictionary maps the values in the key field to
    the corresponding row in the CSV file and the inner dictionary maps the field names 
    to the field values for that row
    """
    result = {}
    with open(filename, newline = '') as file:
        reader = csv.DictReader(file, delimiter = separator, quotechar = quote)
        for row in reader: 
            result[row[keyfield]] = row
    return result

def build_plot_values(gdpinfo, gdpdata):
    """
    Parameters
    ----------
    gdpinfo : a gdp information dictionary
    gdpdata : a dictionary that contains a single country's GDP data

    Returns
    -------
    A list of tuples and the tuple should be of the form (year, gdp) where the year
    is an integer between the min year and max year in the gdpinfo file and the gdp
    should be a float
    """
    result = []
    year_list = list(gdpdata.keys())
    
    # remove nonnumeric keys
    year_to_remove = []
    for year in year_list:
        if re.search('[a-zA-Z]', year):
            year_to_remove.append(year)
    for item in year_to_remove:
        year_list.remove(item)
        
    year_int_list = list(map(int, year_list))
    year_int_list_sorted = sorted(year_int_list)
    for year in year_int_list_sorted:
        if re.search('[a-zA-Z]', str(year)):
            return []
        if year >= gdpinfo["min_year"] and year <= gdpinfo["max_year"]:
            if gdpdata[str(year)] != "":
                result.append((year, float(gdpdata[str(year)])))
    return result
#gap_values = build_plot_values(gdpinfo, gdp_dict["Zimbabwe"])

def build_plot_dict(gdpinfo, country_list):
    """
    Parameters
    ----------
    gdpinfo : a dictionary of country GDP data
    country_list : a list of country names

    Returns
    -------
    A dictionary that maps all the country names in country_list to lists of
    GDP values of that country

    """        
    result = {}
    gdp_dict = read_csv_as_nested_dict(gdpinfo['gdpfile'], gdpinfo['country_name'],
                                       gdpinfo['separator'], gdpinfo['quote'])
    for key in country_list:
        if key in gdp_dict.keys():
            key_dict = gdp_dict[key]
            gdp_plot_values = build_plot_values(gdpinfo, key_dict)
            result[key] = gdp_plot_values
        else:
            result[key] = []
    return result

def reconcile_countries_by_name(plot_countries, gdp_countries):
    """
    Inputs:
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country names used in GDP data

    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country names from
      gdp_countries The set contains the country codes from
      plot_countries that were not found in gdp_countries.
    """
    inner_join_dict = {}
    left_outer_join = set()
    for country_code, country_name in plot_countries.items():
        if country_name in gdp_countries.keys():
            inner_join_dict[country_code] = country_name
        if country_name not in gdp_countries.keys():
            left_outer_join.add(country_code)
    return inner_join_dict, left_outer_join

#inner, left_outer = reconcile_countries_by_name(plot_countries, gdp_countries)

def build_map_dict_by_name(gdpinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      year           - String year to create GDP mapping for

    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    gdp_dict = read_csv_as_nested_dict(gdpinfo['gdpfile'], gdpinfo['country_name'],
                                   gdpinfo['separator'], gdpinfo['quote']) 
    gdp_countries = build_plot_dict(gdpinfo, gdp_dict.keys())
    inner, left_outer = reconcile_countries_by_name(plot_countries,  gdp_countries)
    result = {}
    non_gdp_info = set()
    for code, name in inner.items():
        gdp = gdp_dict[name][year]
        if gdp == '':
            non_gdp_info.add(code)
        else:
            #print(gdp_dict[name])
            result[code] = math.log(float(gdp), 10)
    return result, left_outer, non_gdp_info
#result, left_outer, non_gdp_info = build_map_dict_by_name(build.gdpinfo,plot_countries,'2013')

def render_world_map(gdpinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      year           - String year to create GDP mapping for
      map_file       - Name of output file to create

    Output:
      Returns None.

    Action:
      Creates a world map plot of the GDP data for the given year and
      writes it to a file named by map_file.
    """
    worldmap_chart = pygal.maps.world.World()
    worldmap_chart.title = 'Log(GDP) of Countries'
    result, left_outer, non_gdp_info = build_map_dict_by_name(gdpinfo,plot_countries,year)
    worldmap_chart.add('In '+year, result)
    worldmap_chart.add('Countries without GDP information', left_outer)
    worldmap_chart.add('Countries with GDP information but no data for the given year', non_gdp_info)
    worldmap_chart.render_to_file(map_file)

plot_countries = read_csv_as_dict("pygal_country_list.csv", 'code','Country', ',', '"')

render_world_map(gdpinfo,plot_countries,'2013', "world_gdp.svg")
    

def test_render_world_map():
    """
    Test the project code for several years.
    """
    gdpinfo = {
        "gdpfile": "isp_gdp.csv",
        "separator": ",",
        "quote": '"',
        "min_year": 1960,
        "max_year": 2015,
        "country_name": "Country Name",
        "country_code": "Country Code"
    }

    # Get pygal country code map
    pygal_countries = pygal.maps.world.COUNTRIES

    # 1960
    render_world_map(gdpinfo, pygal_countries, "1960", "isp_gdp_world_name_1960.svg")

    # 1980
    render_world_map(gdpinfo, pygal_countries, "1980", "isp_gdp_world_name_1980.svg")

    # 2000
    render_world_map(gdpinfo, pygal_countries, "2000", "isp_gdp_world_name_2000.svg")

    # 2010
    render_world_map(gdpinfo, pygal_countries, "2010", "isp_gdp_world_name_2010.svg")


# Make sure the following call to test_render_world_map is commented
# out when submitting to OwlTest/CourseraTest.

#test_render_world_map()