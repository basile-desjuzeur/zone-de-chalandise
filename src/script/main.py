#%%
import pandas as pd
from shapely.geometry import Polygon
import geopandas as gpd
import geojson
from lxml import etree
import simplekml

from map import colors_for_map,display_map,add_legend


def geo_json_to_polygon(file_path):
    """
    attribute : file_path : path to the geojson file of the area of interest
    """
    
    # convert geojson to polygon
    with open(file_path) as f:
        gj = geojson.load(f)

    polygon = Polygon(gj['features'][0]['geometry']['coordinates'][0])

    return polygon

# Get the polygon from the kml file
def kml_to_polygon(file_path):
    """
    attribute : file_path : path to the kml file of the area of interest
    
    """
   # parse the kml file
    with open(file_path) as f:
        doc = etree.parse(f)
    # get the coordinates, file is as follow :       <Polygon><outerBoundaryIs><LinearRing><coordinates>
    coordinates = doc.findall('.//{http://www.opengis.net/kml/2.2}coordinates')


    # Parse the coordinates
    coordinates = coordinates[0].text.split()

    # Create a list of (longitude, latitude) pairs
    points = [tuple(map(float, coord.split(','))) for coord in coordinates]


    # Create the polygon
    polygon = Polygon(points)

    return polygon

# Get the cities that are in the polygon
def get_cities_in_polygon(polygon,file_path = '../data/Données nationales/populationLocalisationCommunes.parquet'):
    """
    Gets the cities in the polygon
    attribute : polygon : polygon of the area of interest
    attribute : file_path : path to the file of the cities (source: INSEE)
                # columns : ["nomCommune", "codeCommune", "populationCommune", "geometryCommune"]

    return : filtered DataFrame of cities in the polygon
    """

    try:
        df = gpd.read_parquet(file_path)
        df.crs = 'EPSG:4326'
    except FileNotFoundError:
        print('Error: file not found : ' + file_path)
        return
    
    def get_intersection(x,polygon):

        try :
            intersection = x.geometryCommune.intersection(polygon)
            return intersection.area/x.geometryCommune.area
        except :
            return 0

    df["proportion_inter"] = df.apply(lambda x : get_intersection(x,polygon),axis=1)
    
    
    return df[df["proportion_inter"] > 0 ][["nomCommune", "codeCommune", "populationCommune","proportion_inter"]]
  

# get the population in the cities in the polygon
def get_population(df_cities_in_polygon):
    """
    Gets the population of the area covered by the 
    attribute : df_cities_in_polygon : DataFrame of cities in the polygon
                columns : ["nomCommune", "codeCommune", "populationCommune"
    return : population in the cities in the polygon
    """

    nb =  (df_cities_in_polygon['populationCommune']*df_cities_in_polygon.proportion_inter).sum()

    return round(nb)

def get_companies(naf, df_communes, path_entreprises = '../data/Données nationales/RNE_Sirene.parquet'):
    """
   
    Get the companies in the polygon
    attribute : naf : list of naf codes
    attribute : df_communes : DataFrame of cities in the polygon (only the column codeCommune)
    return : df_filtered : DataFrame of companies in the polygon
                columns = ['siret',
                            'qualite_xy',
                            'y_latitude',
                            'x_longitude',
                            'nomCommercial',
                            'adresse',
                            'codeInseeCommune',
                            'codeApe',
                            'diffusionCommerciale',
                            'qualite_xy']
    """

    
    # read the file
    try:
        df_siret = pd.read_parquet(path_entreprises)
    except FileNotFoundError:
        print('Error: file not found : ' + path_entreprises)
        return
    
    # get the commune codes
    codes_communes = df_communes['codeCommune'].unique()

    # get the companies with the naf codes
    df = df_siret[df_siret['codeApe'].isin(naf)]

    # get the companies in the polygon (i.e. with code)
    df_filtered = df[df['codeInseeCommune'].isin(codes_communes)]

    # lien pappers pour chaque entreprise
    df_filtered = df_filtered.copy()
    df_filtered.loc[:, 'lien_pappers'] = df_filtered['siret'].apply(lambda x: "https://www.pappers.fr/recherche?q=" + str(x))

    return df_filtered

def polygon_to_kml(polygon, output_path):
    kml = simplekml.Kml()
    pol = kml.newpolygon(name="Polygon Name", outerboundaryis=polygon.exterior.coords[:])
    pol.style.polystyle.color = simplekml.Color.changealphaint(200, 'ff0000')  # Set polygon color (red in this example)
    
    kml.savekmz(output_path)



def _main(kml_file_path,naf=["47.11B","47.11F"],population_file_path= '../../data/Données nationales/populationLocalisationCommunes.parquet',companies_file_path = '../../data/Données nationales/RNE_Sirene_localisé.parquet'):
    """
    kml_file_path : path to the kml file of the area of interest
    naf : list of naf codes to filter the companies
    population_file_path : path to the population file
    companies_file_path : path to the companies file
    """

    print('Lecture du fichier de surface...')

    # get the polygon

    if kml_file_path.split('.')[-1] == 'kml':
        polygon = kml_to_polygon(kml_file_path)
    elif kml_file_path.split('.')[-1] == 'geojson':
        polygon = geo_json_to_polygon(kml_file_path)


    print("Filtre des communes dans l'aire d'étude...")

    # get the cities in the polygon
    df_cities_in_polygon = get_cities_in_polygon(polygon,population_file_path)

    # get the population in the polygon
    population = get_population(df_cities_in_polygon)

    print("Filtre des entreprises dans l'aire d'étude...")

    # get the companies in the polygon
    df_filtered = get_companies(naf, df_cities_in_polygon, companies_file_path)

    print("Création de la carte...")

    colors = colors_for_map(naf)
    
    # display the map
    m = display_map(df_filtered,polygon,population,kml_file_path,colors)

    # add the legend
    m = add_legend(m,colors)

    return m,df_filtered,polygon,population


if __name__ == "__main__":

    kml_file_path = '../../data/Données sites/Zone de chalandise à une heure de Lille.geojson'
    naf = ["47.11B","47.11F"]
    population_file_path = '../../data/Données nationales/populationLocalisationCommunes.parquet'
    companies_file_path = '../../data/Données nationales/RNE_Sirene_localisé.parquet'

    m,df_filtered,polygon,population = _main(kml_file_path,naf,population_file_path,companies_file_path)

    m.save('../../data/test/test.html')
    print('Carte sauvegardée dans data/test/test.html')
# %%
