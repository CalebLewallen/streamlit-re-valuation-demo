from datetime import datetime, timedelta

from logic.geospatial_calcs import check_property_in_neighborhood


def time_since_sales_date(sales_date: str) -> float:

    sales_date_as_datetime = datetime.strptime(sales_date, '%Y-%m-%d')

    time_since_sale = (datetime.now() - sales_date_as_datetime).days / 365.25

    return time_since_sale


def calculate_weighted_value_per_foot(property_obj, group_weighting):
    
    years_since_sale = time_since_sales_date(property_obj['lastSaleDate'])
    if years_since_sale > 5:
        return 0
    
    calc_weighting = 1 # - (years_since_sale / 5) # Linearly decrease the weight of the property as it gets older
    weighted_value = (property_obj['lastSalePrice'] * calc_weighting * group_weighting) / property_obj['squarefeet']

    return weighted_value


def calculate_relative_property_value(neighborhood_properties, radius_properties, neighborhood_weight: float = 0.7, radius_weight: float = 0.3):

    total_weighted_value = 0
    total_weight = 0

    calc_values = []

    # Assign weights
    if neighborhood_properties: 
        count = 1
        for property in neighborhood_properties:
            count += 1
            # print(f'property{count}:', property)
            weighted_value = calculate_weighted_value_per_foot(property, neighborhood_weight) # Get this property's weighted value
            total_weighted_value += weighted_value # Add it to the total
            if weighted_value > 0:
                total_weight += neighborhood_weight # Accrue the total weighting

            property_value = {
                "property": property['name'],
                "value": weighted_value,
                "weight": neighborhood_weight
            }
            calc_values.append(property_value)


    if radius_properties:
        for property in radius_properties:

            weighted_value = calculate_weighted_value_per_foot(property, radius_weight) # Get weighted value
            total_weighted_value += weighted_value # Keep adding to the total
            if weighted_value > 0:
                total_weight += radius_weight # Keep adding weights

            property_value = {
                "property": property['name'],
                "value": weighted_value,
                "weight": radius_weight
            }
            calc_values.append(property_value)

    if total_weight == 0: # Make sure we're not dividing by zero and blowing up Streamlit
        return 0
    else:
        print(calc_values)
        return total_weighted_value / total_weight
    

def calculate_total_property_value(target_property_id, property_list, price_per_foot):
    
    target_property = next((property for property in property_list if property['id'] == target_property_id), None)
    
    return target_property['squarefeet'] * price_per_foot