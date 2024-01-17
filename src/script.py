
# %%

import pandas as pd
from shapely.geometry import Polygon, Point
import lxml.etree as etree
from lxml import etree
import geopandas as gpd
from tqdm.notebook import tqdm
import folium



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
    #points = [(y, x) for x, y in points]

    # Create the polygon
    polygon = Polygon(points)

    return polygon



# Get the cities that are in the polygon
def get_cities_in_polygon(polygon,file_path = '../Données nationales/populationLocalisationCommunes.parquet'):
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
    
    df['in_polygon']=df.apply(lambda x : x.geometryCommune.within(polygon),axis=1)


    return df[df["in_polygon"]==True][["nomCommune", "codeCommune", "populationCommune"]]


# get the population in the cities in the polygon
def get_population(df_cities_in_polygon):
    """
    Gets the population in the cities in the polygon
    attribute : df_cities_in_polygon : DataFrame of cities in the polygon
                columns : ["nomCommune", "codeCommune", "populationCommune"
    return : population in the cities in the polygon
    """

    return df_cities_in_polygon['populationCommune'].sum()



def get_companies(naf, df_communes, path_entreprises = '../Données nationales/RegistreNationalEtablissementsActifsRneSirene.parquet'):
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
                            'adresseEtablissement',
                            'codeInseecommune',
                            'codeApe',
                            'diffusionCommerciale',
                            'confiance']
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
    df_filtered = df[df['codeInseecommune'].isin(codes_communes)]

    # lien pappers 
    #df_filtered['lien_pappers'] = df_filtered.siret.apply(lambda x : "https://www.pappers.fr/recherche?q="+str(x))

    df_filtered = df_filtered.copy()
    df_filtered.loc[:, 'lien_pappers'] = df_filtered['siret'].apply(lambda x: "https://www.pappers.fr/recherche?q=" + str(x))

    return df_filtered

def display_map(df_filtered,polygon,population,kml_file_path):
    """
    df_filtered : DataFrame of companies in the polygon
                columns = ['siret',
                            'qualite_xy',
                            'y_latitude',
                            'x_longitude',
                            'nomCommercial',
                            'adresseEtablissement',
                            'codeInseecommune',
                            'codeApe',
                            'diffusionCommerciale',
                            'confiance']
    polygon : polygon of the area of interest
    population : population in the polygon
    """
    
   

    # create a GeoDataFrame
    gdf = gpd.GeoDataFrame(df_filtered, geometry=gpd.points_from_xy(df_filtered.x_longitude, df_filtered.y_latitude))

    # set the crs
    gdf.crs = 'EPSG:4326'

    # create the map and locate it at the center of the polygon
    m = folium.Map(location=[polygon.centroid.y, polygon.centroid.x], zoom_start=10)

    # add the polygon
    folium.GeoJson(polygon).add_to(m)

    # add the companies to the map with all the information
    for i in range(0,len(gdf)):
        folium.Marker(
            location=[gdf.iloc[i]['y_latitude'], gdf.iloc[i]['x_longitude']],
            popup=folium.Popup(
                '<b>'+gdf.iloc[i]['nomCommercial']+'</b><br>'
                +"Adresse : "+'<br>'+gdf.iloc[i]['adresseEtablissement']+'<br>'
                +'Code APE : '+'<br>'+str(gdf.iloc[i]['codeApe'])+'<br>'
                +'SIRET : '+'<br>'+str(gdf.iloc[i]['siret'])+'<br>'
                +'Diffusion Commerciale : '+'<br>'+str(gdf.iloc[i]['diffusionCommerciale'])+'<br>'

                # display confidence score as percentage rather than /5
                +"Confiance dans l'adresse: "+'<br>'+str(int(gdf.iloc[i]['confiance']/5*100))+'%<br>'
                +'<a href="'+gdf.iloc[i]['lien_pappers']+'">Lien Pappers</a>'
            ),
            tooltip=gdf.iloc[i]['nomCommercial']
        ).add_to(m)


        
    # title in bold
    title = 'Cartograhie des entreprises : '+ kml_file_path.split('/')[-1].split('.')[0].capitalize() 

    # subtitle
    subtitle_1 = 'Population du bassin considéré : '+ "{:,}".format(population).replace(',',' ')+' habitants'

    # subtitle smaller and in italic
    subtitle_2 = "Source : INSEE, Registre national des Entreprises, La Poste"


    # add the title
    title_html = '''
        <h3 align="center" style="font-size:16px"><b>{}</b></h3>
        '''.format(title)
    
    # add the subtitle
    subtitle_1_html = '''
        <h4 align="center" style="font-size:12px"><i>{}</i></h4>
        '''.format(subtitle_1)
    
    # add the subtitle
    subtitle_2_html = '''
        <h4 align="center" style="font-size:10px"><i>{}</i></h4>
        '''.format(subtitle_2)
    
    # add the title
    m.get_root().html.add_child(folium.Element(title_html))

    # add the subtitle
    m.get_root().html.add_child(folium.Element(subtitle_1_html))

    # add the subtitle
    m.get_root().html.add_child(folium.Element(subtitle_2_html))

    # change zoom to see the whole polygon
    m.fit_bounds(m.get_bounds())


    return m


def _main(kml_file_path,naf,population_file_path= '../Données nationales/populationLocalisationCommunes.parquet',companies_file_path = '../Données nationales/RegistreNationalEtablissementsActifsRneSirene.parquet'):
    """
    kml_file_path : path to the kml file of the area of interest
    naf : list of naf codes to filter the companies
    population_file_path : path to the population file
    companies_file_path : path to the companies file
    """

    print('Lecture du fichier de surface...')

    # get the polygon
    polygon = kml_to_polygon(kml_file_path)


    print("Filtre des communes dans l'aire d'étude...")

    # get the cities in the polygon
    df_cities_in_polygon = get_cities_in_polygon(polygon,population_file_path)

    # get the population in the polygon
    population = get_population(df_cities_in_polygon)

    print("Filtre des entreprises dans l'aire d'étude...")

    # get the companies in the polygon
    df_filtered = get_companies(naf, df_cities_in_polygon, companies_file_path)

    print("Création de la carte...")
    
    # display the map
    m = display_map(df_filtered,polygon,population,kml_file_path)

    return m


m =_main('../Données sites/agriviva.kml',['47.11F'])








# %%
