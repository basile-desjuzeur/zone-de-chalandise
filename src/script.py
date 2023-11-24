import pandas as pd
import argparse
from shapely.geometry import Polygon, Point
import lxml.etree as etree


parser = argparse.ArgumentParser(description='Given a kml file, outputs the population of the polygon in the kml file')

parser.add_argument('kml_file',help='Path to the kml file')
parser.add_argument('population_file',help='Path to the population file',default='Données nationales/population-par-commune.csv')

args = parser.parse_args()

# Get the polygon from the kml file
def kml_to_polygon(file_path):

    # parse the kml file
    from lxml import etree
    with open(file_path) as f:
        doc = etree.parse(f)

    # get the coordinates, file is as follow :       <Polygon><outerBoundaryIs><LinearRing><coordinates>
    coordinates = doc.findall('.//{http://www.opengis.net/kml/2.2}coordinates')

    # Parse the coordinates
    coordinates = coordinates[0].text.split()

    # Create a list of (longitude, latitude) pairs
    points = [tuple(map(float, coord.split(','))) for coord in coordinates]

    # reverse the order of coordinates in a tuple
    points = [(y, x) for x, y in points]

    # Create the polygon
    polygon = Polygon(points)
    return polygon

# check if a point is in a polygon
def is_in_polygon(polygon,point):
    return polygon.contains(point)

# get the population of a polygon
def get_population(polygon,file_path=args.population_file):


    try:
        df = pd.read_csv(file_path)
    except:
        print('Error: file not found : ' + file_path)
        return
    
    # get the population of the polygon
    df.est_dans_agriviva = df.apply(lambda x : is_in_polygon(polygon,Point(x.latitude,x.longitude)),axis=1)

    print("Population totale : "+str(df[df.est_dans_agriviva==True]['Population totale'].sum()))



if __name__ == "__main__":
    polygon = kml_to_polygon(args.kml_file)
    get_population(polygon)



