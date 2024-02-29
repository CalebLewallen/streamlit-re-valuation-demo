import json
from shapely.geometry import shape, Point
from geopy.distance import geodesic

### This logic is to find properties that fall within a specific polygon
def check_property_in_neighborhood(property_coorindates, neighborhood_polygon) -> bool:
    """
    Check if a property is in a neighborhood
    """
    # Create a point from the property's coordinates
    point = Point(property_coorindates[0], property_coorindates[1])

    # Create a polygon from the neighborhood's coordinates
    polygon = shape(neighborhood_polygon['features'][0]['geometry'])

    # Check if the point is within the polygon
    return polygon.contains(point)


def find_all_properties_in_neighborhood(propertyId: int, property_list, neighborhood) -> list:
    """
    Find all properties in a neighborhood
    """
    # Check to see if property is in the list
    target_property = next((property for property in property_list if property['id'] == propertyId), None)
    if not target_property:
        return "Property not found"
    
    # Check if the target is in the southend neighborhood boundaries
    target_coords = (target_property['long'], target_property['lat'])
    target_in_neighborhood = check_property_in_neighborhood(target_coords, neighborhood)
    if not target_in_neighborhood:
        return "Property not in neighborhood"

    # If target is in neighborhood, then find all other properties in the neighborhood
    properties_in_neighborhood = []
    for property in property_list:
        property_coords = (property['long'], property['lat'])
        if check_property_in_neighborhood(property_coords, neighborhood) and property['id'] != propertyId:
            properties_in_neighborhood.append(property)

    # print('Properties in neighborhood:', properties_in_neighborhood)

    return properties_in_neighborhood


### This logic is to find all properties with a specific distance of a target property
def find_properties_within_radius(target_property_id: int, property_list, neighborhood_to_exclude, radius_miles: int = 1) -> list:
    """
    Find all properties within a certain radius of the target property
    """
    # Check to see if property is in the list
    target_property = next((property for property in property_list if property['id'] == target_property_id), None)
    if not target_property:
        return "Property not found"
    
    # Create a point from the target property's coordinates
    target_point = (float(target_property['lat']), float(target_property['long']))

    # Find all properties that are within the radius of the target property
    properties_within_radius = []
    for property in property_list:

        #Check to see if the property is in the neighborhood of target. If so exclude it from the list
        target_in_neighborhood = check_property_in_neighborhood((property['long'], property['lat']), neighborhood_to_exclude)
        if not target_in_neighborhood: # property is not in the neighborhood, check to see if it's in a radius around it
            property_point = (float(property['lat']), float(property['long']))
            distance = geodesic(target_point, property_point).miles
            if distance <= radius_miles and property['id'] != target_property_id:
                properties_within_radius.append(property)

    return properties_within_radius