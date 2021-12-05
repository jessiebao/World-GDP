"""
Project for Week 4 of "Python Data Visualization".
Unify data via common country codes.

Be sure to read the project description page for further information
about the expected behavior of the program.
"""

import csv
import math
import pygal

gdpinfo = {
        "gdpfile": "isp_gdp.csv",        # Name of the GDP CSV file
        "separator": ",",                # Separator character in CSV file
        "quote": '"',                    # Quote character in CSV file
        "min_year": 1960,                # Oldest year of GDP data in CSV file
        "max_year": 2015,                # Latest year of GDP data in CSV file
        "country_name": "Country Name",  # Country name field name
        "country_code": "Country Code"   # Country code field name
    }

codeinfo = {
    "codefile": "isp_country_codes.csv",
    "separator": ",",
    "quote": '"',
    "plot_codes": "ISO3166-1-Alpha-2",   # Plot code field name
    "data_codes": "ISO3166-1-Alpha-3"    # GDP data code field name
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

def build_country_code_converter(codeinfo):
    """
    Inputs:
      codeinfo      - A country code information dictionary

    Output:
      A dictionary whose keys are plot country codes and values
      are world bank country codes, where the code fields in the
      code file are specified in codeinfo.
    """
    return read_csv_as_dict(codeinfo["codefile"], codeinfo["plot_codes"], codeinfo["data_codes"],
                            codeinfo["separator"], codeinfo["quote"])


def reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries):
    """
    Inputs:
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country codes used in GDP data

    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country codes from
      gdp_countries.  The set contains the country codes from
      plot_countries that did not have a country with a corresponding
      code in gdp_countries.

      Note that all codes should be compared in a case-insensitive
      way.  However, the returned dictionary and set should include
      the codes with the exact same case as they have in
      plot_countries and gdp_countries.
    """
    result = {}
    result_set = set()
    plot_gdp_code_dict = build_country_code_converter(codeinfo) # map code in plot to code in gdp
    key_upper = {}  # transform all keys in plot to uppercase
    for key, value in plot_gdp_code_dict.items():
        key_upper[key.upper()] = value
        
    for key, value in plot_countries.items(): # loop through code in plot
        # find code in gdp_countries through plot_gdp_code_dict
        print(key)
        if key.upper() in key_upper.keys():
            gdp_code = key_upper[key.upper()]
            find = False
            for key_gdp in gdp_countries.keys():
                if gdp_code.upper() == key_gdp.upper():
                    result[key] = key_gdp
                    find = True
            if not find: result_set.add(key)
        else: result_set.add(key)
    return (result, result_set)

#plot_countries = read_csv_as_dict("pygal_country_list.csv", "code", "Country", ",", '"')

def build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year for which to create GDP mapping

    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    gdp_countries = read_csv_as_nested_dict(gdpinfo["gdpfile"],gdpinfo["country_code"], gdpinfo['separator'], gdpinfo['quote'])
    (result, result_set) = reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries)
    result1 = {}
    set2 = set() # missing gdp in this year
    for key in result.keys():
        if result[key] not in gdp_countries.keys():
            result_set.add(key)
        else:
            if gdp_countries[result[key]][year] == '':
                set2.add(key)
            else:
                result1[key] = math.log(float(gdp_countries[result[key]][year]),10)
        
    return (result1, result_set, set2)

def render_world_map(gdpinfo, codeinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year of data
      map_file       - String that is the output map file name

    Output:
      Returns None.

    Action:
      Creates a world map plot of the GDP data in gdp_mapping and outputs
      it to a file named by svg_filename.
    """
    (result1, set1, set2) = build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year)
    worldmap_chart = pygal.maps.world.World()
    worldmap_chart.title = 'GDP by Country for ' + year + ' in log scale'
    worldmap_chart.add('In ' + year, result1)
    worldmap_chart.add('Missing from World Bank', set1)
    worldmap_chart.add('No GDP data', set2)
    worldmap_chart.render_to_file(map_file)

#render_world_map(gdpinfo, codeinfo, plot_countries, '2010', 'GDP_Countries_Year.svg')