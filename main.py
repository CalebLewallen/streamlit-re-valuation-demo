import streamlit as st
import pydeck as pdk
from components.map import map
from components.dataframes import properties_data
from logic.geospatial_calcs import find_all_properties_in_neighborhood, find_properties_within_radius
from logic.sales_comps import calculate_relative_property_value, calculate_total_property_value
import json
import pandas as pd

# Page settings
st.set_page_config(
    page_title='Using Geospatial Data to Appraise Real Estate',
    page_icon='🏠',
    layout='wide',

)

# Set page title
st.title('Using Geospatial Data to Appraise Real Estate')

st.markdown('''
            This app is a demo of how to use geospatial data to appraise real estate. While this will use a simplified example, the same principles can be applied to more complex scenarios.

            To begin, we'll first load the data and visualize the neighborhood. We'll explore a few multifamily properties in the Southend neighborhood of Charlotte, NC.
''')


# Display the map
st.header('Southend Neighborhood')
st.markdown('''
            Southend is a popular neighborhood in Charlotte, NC. It is known for its vibrant nightlife, art galleries, and breweries. It is also home to the Lynx Light Rail, which connects it to Uptown and the University area.

            We'll start by visualizing the neighborhood boundaries and the properties we're interested in.
            ''')

st.pydeck_chart(map)

st.markdown('''
        Let's take a closer look at the properties in the neighborhood. We'll start by looking at the property details and then use that information to appraise the properties.
        ''')

st.dataframe(properties_data, hide_index=True)

st.markdown('''
    It looks like we don't have a good property value for the Link Apartments Mint St. Let's use the information we know about the Southend neighborhood and surrounding areas to determine which properties we should use to appraise Link Apartments.
''')

st.markdown('''
    First thing we'll do is pass the property id into the 'check_property_in_neighborhood' function to see if the property is in the neighborhood. If it is, we'll then use the 'find_all_properties_in_neighborhood' function to find all properties in the neighborhood.
''')

st.markdown('Property Id = 4')

# Load neighborhood data
with open('data/features.geojson') as neighborhood_data:
    neighborhood_boundaries = json.load(neighborhood_data)

# Load property data
with open('data/properties.json') as properties_data:
    properties = json.load(properties_data)

target_property_id: int = 4

properties_in_neighborhood = find_all_properties_in_neighborhood(target_property_id, properties, neighborhood_boundaries)

st.markdown('Success! We did not return any errors, which means the property is in the neighborhood and we have found all the properties in the neighborhood. Let\'s take a look at the properties in the neighborhood.')
st.dataframe(pd.DataFrame(properties_in_neighborhood), hide_index=True)


st.markdown('''
    Now that we have the properties in the neighborhood, let's use the 'find_properties_within_radius' function to find all properties within a 1-mile radius of the Link Apartments Mint St.
''')
properties_in_radius = find_properties_within_radius(target_property_id, properties, neighborhood_boundaries, radius_miles=1)

st.dataframe(pd.DataFrame(properties_in_radius), hide_index=True)

st.markdown('''
    This is great! Now all that's left is to union these lists to get a common list of like properties.
            ''')

radius_properties = pd.DataFrame(properties_in_radius)
neighborhood_properties = pd.DataFrame(properties_in_neighborhood)

all_properties = pd.concat([radius_properties, neighborhood_properties]).drop_duplicates().reset_index(drop=True)

st.dataframe(all_properties, hide_index=True)

st.header('Valuing Properties')

st.markdown('''
    Now that we have identified our properties, we can apply several different valuation methods to arrive at an appraised value. For this exercise, we're going to assume that we have no knowledge of the specific economics of each of these properties.
    However, we can assume that we have some knowledge of different market averages and apply different valuation methods from there.
    
    We will derive our values using the following methods: \n - Replacement Cost \n - Gross Rent Multiplier \n - Capitalization Rate \n - Sales Comparison \n
    ''')

st.markdown('''
    Here's the market averages we'll use for our valuation: \n - Replacement Cost: $278/ft \n - Gross Rent Multiplier: 9.6 \n - Capitalization Rate: 6% \n
''')

st.markdown('''
    And the data we have for the Link Apartments Mint St: \n - Link's T12 Average Rent/Unit: $1,718/month \n - Link's T12 Expense Ratio: 40% \n
''')



st.header('Replacement Cost')
st.markdown('''
    This is one of the simplest methods to apply. To apply it, we first need some data about construction costs for our area. This data will vary by location,
    the type of construction, the finishes appied, how amny stories there will be, codes for that particular area, material cost, etc. Since this isn't a demonstration
    of how to arrive at those costs, we'll wave a magic wand at our data and assume that the replacement cost for our area is $278/ft.
            ''')

st.markdown('''
    With this knowledge in hand, we can now calculate the replacement cost for the Link Apartments Mint St. We know through public records that the total finished
    area is 242,843 square feet.
    
    Multiplying this by our replacement cost, we get: 242,843 * \$278 = \$67,510,354
''')



st.header('Gross Rent Multiplier')
st.markdown('''
        This next method relies relies on the idea that there is some relationship between the cashflow of a property and its value. The GRM (Gross Rent Multiplier)
        is about as simple as it gets. It's simply a ratio of a property's value to it's total rental income. Like all valuation methods, data is king here, and relies on
        us having a good set of data about rental incomes and property values for surrounding assets. For our purposes, we'll go ahead and assume that we have this data
        for our surrounding properties and found that the average GRM is 9.6.
''')

st.markdown('''
    The next step in our calculation is to figure out the rental income for the Link Apartments. Since we know that the average T12 rental income across ALL units is \$1,718/month,
    we can multiply this by the total number of units and then by 12 to get the annual rental income. This gives us: \$2,535 * 259 * 12 = \$7,878,780.
            ''')

st.markdown('''
    Before we get to our value, when was the last time you've ever seen a building at 100\% occupancy? We need to account for this. Let's be conservative and assume that
    our occupancy should average 90\%. This gives us: \$5,339,544 * 0.9 = \$7,090,902.
''')

st.markdown('''
    Finally, we mulitply this by our GRM to get our value: \$7,090,902 * 9.6 = \$68,072,659.
            ''')



st.header('Capitalization Rate')

st.markdown('''
    Next up in our tour are cap rates. This method is the sophisticated older sibling of GRM, as it takes into account the financial performance of the asset, rather than relying on rental revenue alone, which can leave out a lot of informatin about the health of the project.
            
    The cap rate is the ratio of the net operating income (NOI) to the value of the property. The NOI is the income left over after all operating expenses have been paid. For our purposes, we'll assume that we have this data for our surrounding properties and found that the average cap rate is 6%, and we have an expense ratio 40%.
            
    We can start with the revenue value we derived in our example above, of \$7,090,902. We can then calculate the NOI by multiplying this by 1 - the expense ratio, which gives us: \$7,090,902 * 0.6 = \$4,254,541.
            
    Our final step is to divide this by our cap rate to get our value: \$4,254,541 / 0.06 = \$70,909,020.
''')

st.caption('One thing to point out is that cap rates are outputs, not inputs. They should not be relied on to determine the value of a property. However, they can be used as a proxy measure to estimate value.')



st.header('Sales Comparison')

st.markdown('''
    The last method we'll use is the sales comparison method. Also referred to as comps, this method is based on the idea that similar properties with similar physical characteristics in similar locations should all price around the same ***relative*** valuation.
            
    While there's several ways to approach this idea, a common relative measure is price per square foot. We'll use the data we collected from our neighborhood and radius properties to calculate this value. You can view the source code to see how we're going to accmplish this.
            
    This example uses a pretty simple methodology, but more sophisticated weighting can be applied to give more recent sales a larger bias.
    
''')


comp_per_foot = calculate_relative_property_value(properties_in_neighborhood, properties_in_radius) # use default weights

property_value = calculate_total_property_value(target_property_id, properties, comp_per_foot)


st.markdown('''
    Out final value for the Link Apartments Mint St using comps data is:
            ''')
st.text('${:,.2f}'.format(property_value))


st.header('Conclusion')

st.markdown('''
    We've explored how to use geospatial data to appraise real estate. We've used a simplified example to demonstrate how to use different valuation methods to arrive at an appraised value. We've also seen how to use geospatial data to find properties in a neighborhood and within a certain radius of a target property. This is just the tip of the iceberg, and there are many more ways to use geospatial data to appraise real estate.
            ''')

with open('data/valuations.json', 'r') as file:
    valuation_summary = json.load(file)

valuation_df = pd.DataFrame(valuation_summary)

st.dataframe(valuation_df, hide_index=True)