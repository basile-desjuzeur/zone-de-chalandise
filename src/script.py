import pandas as pd
from shapely.geometry import Polygon, Point
import lxml.etree as etree
from lxml import etree
from tqdm.notebook import tqdm



# Get the polygon from the kml file
def kml_to_polygon(file_path):

    # parse the kml file
    
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
def get_population(polygon,file_path):

    tqdm.pandas()

    print('Lecture du fichier source')
  
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print('Error: file not found : ' + file_path)
        return

    print('Calcul de la population')

    df['in_polygon']=df.progress_apply(lambda x : is_in_polygon(polygon,Point(x.latitude,x.longitude)),axis=1)
  
    total = df[df["in_polygon"]==True]['Population totale'].sum()

    print("Population totale : "+str(int(total))+" habitants (source:  INSEE 2023)")

def get_companies(naf, polygon, df_siret):
    """
    Get the companies in the polygon
    attribute : naf : list of naf codes
    attribute : polygon : polygon of the area of interest
    return : Dask DataFrame of companies in the polygon
    """

    # get the companies with the naf codes
    df = df_siret[df_siret['activitePrincipaleEtablissement'].isin(naf)]

    # create a valid meta for the apply function
    meta = pd.Series(name='in_polygon', dtype=bool)

    # filter companies in the polygon without computing
    df_filtered = df[df.apply(lambda x: is_in_polygon(polygon, Point(x.y_latitude, x.x_longitude)), axis=1,
                              meta=meta)]

 
    return df_filtered[['siret', 'y_latitude', 'x_longitude']],df_filtered

def get_summary(dict_naf,df_filtered):
    """
    Create a summary of the companies in the polygon with the number of companies per NAF (described by its libellé in the dict_naf)
    attribute : dict_naf : dict of naf codes and libellé
    attribute : df Dask DataFrame of companies in the polygon
                columns : siret,plg_code_commune,y_latitude,x_longitude,codeCommuneEtablissement,activitePrincipaleEtablissement
    return : DataFrame of the summary
    """

    
    # get the number of companies per naf
    df_summary = df_filtered.groupby('activitePrincipaleEtablissement').count().compute()
    df_summary.reset_index(inplace=True)
    df_summary.rename(columns={'activitePrincipaleEtablissement': 'NAF', 'siret': 'Nombre d\'entreprises'}, inplace=True)

    # sort the dataframe
    df_summary.sort_values(by=['Nombre d\'entreprises'], ascending=False, inplace=True)

    return df_summary[['NAF', 'Nombre d\'entreprises']]