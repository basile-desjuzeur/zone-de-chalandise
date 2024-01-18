
#%%


import pandas as pd
from shapely.geometry import Polygon
import geopandas as gpd
import folium
import geojson
from lxml import etree



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

    # lien pappers pour chaque entreprise
    df_filtered = df_filtered.copy()
    df_filtered.loc[:, 'lien_pappers'] = df_filtered['siret'].apply(lambda x: "https://www.pappers.fr/recherche?q=" + str(x))

    return df_filtered

#%%

def colors_for_map(naf):
    """
    Each naf code has a color for the map, this function returns the color for each naf code
    attribute : naf : list of naf codes

    return : colors : dictionary of colors for each naf code
    """
  
    # dictionary of foodbiome colors
    foodbiome_colors = [
    'red',
    'blue',
    'gray',
    'darkred',
    'lightred',
    'orange',
    'beige',
    'green',
    'darkgreen',
    'lightgreen',
    'darkblue',
    'lightblue',
    'purple',
    'darkpurple',
    'pink',
    'cadetblue',
    'lightgray',
    'black'
    ]

    # dictionary of colors for each naf code
    colors = { naf[i] : foodbiome_colors[i] for i in range(len(naf))}


    return colors

#%%

def display_map(df_filtered,polygon,population,kml_file_path,colors):
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
    kml_file_path : path to the kml file of the area of interest
    colors_for_map : function that returns the colors for each naf code
    """
    
   

    # create a GeoDataFrame
    gdf = gpd.GeoDataFrame(df_filtered, geometry=gpd.points_from_xy(df_filtered.x_longitude, df_filtered.y_latitude))

    # set the crs
    gdf.crs = 'EPSG:4326'

    # create the map and locate it at the center of the polygon
    m = folium.Map(location=[polygon.centroid.y, polygon.centroid.x], zoom_start=10)

    # add the polygon
    folium.GeoJson(polygon,style_function=lambda x: {'opacity':'1'}).add_to(m)

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
                +"Confiance dans la localisation : "+'<br>'+str(int(gdf.iloc[i]['confiance']/5*100))+'%<br>'
                +'<a href="'+gdf.iloc[i]['lien_pappers']+'">Lien Pappers</a>'
            ),
            icon=folium.Icon(color = colors[gdf.iloc[i]['codeApe']],icon = 'industry', prefix='fa')
        ).add_to(m)


    # title in bold
    title = 'Cartographie des entreprises : '+ kml_file_path.split('/')[-1].split('.')[0].capitalize() 

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
#%%

def add_legend(m,colors,naf_file = '../Données nationales/NAF.parquet'):
    """
    Adds a legend to the map with a color for each naf code  
    
    Attribute : m : map
    Attribute : colors : dictionary of colors for each naf code {naf_code : color}
    Attribute : naf_file : path to the naf file (source : INSEE), columns : ['codeNaf','libelleNaf']
    
    Returns : m : map with the legend
    """

    # read the naf file
    try:
        df_naf = pd.read_parquet(naf_file)
    except FileNotFoundError:
        print('Error: file not found : ' + naf_file)
        return

    # gets the libelle for each naf code
    df_naf = df_naf[df_naf['codeNaf'].isin(colors.keys())]

    # Calculate the height of the legend based on the number of items
    legend_height = 30 + 20 * len(df_naf)

    # Calculate the width of the legend based on the longest item
    font_size = 12
    width_factor = 0.6

    # get the longest item
    longest_item = df_naf['libelleNaf'].apply(lambda x : len(x)).max()

    # calculate the width
    legend_width = int(longest_item * font_size * width_factor)
    color_names_dict = {
        'red': '#ff0000',
        'darkred': '#8b0000',
        'lightred': '#ffcccb',
        'orange': '#ffa500',
        'beige': '#f5f5dc',
        'green': '#008000',
        'darkgreen': '#006400',
        'lightgreen': '#90ee90',
        'blue': '#0000ff',
        'darkblue': '#00008b',
        'lightblue': '#add8e6',
        'purple': '#800080',
        'darkpurple': '#483d8b',
        'pink': '#ffc0cb',
        'cadetblue': '#5f9ea0',
        'white': '#ffffff',
        'gray': '#808080',
        'lightgray': '#d3d3d3',
        'black': '#000000'
    }


    # create the legend in bottom left corner
    legend_html_base = '''
        <div style="position: fixed;
                    bottom: 10px; left: 10px; width: {}px; height: {}px;
                    border:2px solid grey; z-index:9999; font-size:{}px;font-color:black;background-color:white;font-family:Arial, Helvetica, sans-serif;
                    ">&nbsp; <b> Légende </b>  <br>
                    '''.format(str(legend_width),str(legend_height),str(font_size))
    
    # add 5px of margin
    legend_html_base += '<div style="margin:5px">'

    # add the legend for each naf code
    for i in range(len(df_naf)):

        # get the color
        naf_color = colors[df_naf.iloc[i]['codeNaf']]

        # get the hex color from the color (item))
        hex_color = color_names_dict[naf_color]

        # add the legend
        legend_html_base += '&nbsp; <i class="fa fa-circle" style="color:{}"></i> {} <br>'.format(hex_color,df_naf.iloc[i]['libelleNaf'])

    # close the legend
    legend_html_base += '</div>'

    # add the legend to the map
    m.get_root().html.add_child(folium.Element(legend_html_base))

    return m

#%%
def _main(kml_file_path,naf,population_file_path= '../Données nationales/populationLocalisationCommunes.parquet',companies_file_path = '../Données nationales/RegistreNationalEtablissementsActifsRneSirene.parquet'):
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
    #m = add_legend(m,colors)

    return m



m = _main(kml_file_path='../Données sites/agriviva.kml',naf = ['47.11D','47.11F','10.71C'])
m.save('./temp.html')
# %%
