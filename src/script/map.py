import folium 
import geopandas as gpd
import pandas as pd
from branca.element import Template,MacroElement

def colors_for_map(naf):
    """
    Each naf code has a color for the map, this function returns the color for each naf code
    attribute : naf : list of naf codes

    return : colors : dictionary of colors for each naf code
    """
    color_names_dict = {
        'red': '#ff0000',
        'orange': '#ffa500',
        'cadetblue': '#5f9ea0',
        'beige': '#f5f5dc',
        'lightred': '#ffcccb',
        'darkred': '#8b0000',  
        'green': '#008000',
        'darkgreen': '#006400',
        'lightgreen': '#90ee90',
        'blue': '#0000ff',
        'darkblue': '#00008b',
        'lightblue': '#add8e6',
        'purple': '#800080',
        'darkpurple': '#483d8b',
        'pink': '#ffc0cb',
        'white': '#ffffff',
        'gray': '#808080',
        'lightgray': '#d3d3d3',
        'black': '#000000'
    }


    # dictionary of colors for each naf code
    colors = { naf_code : list(color_names_dict.items())[i] for i,naf_code in enumerate(naf)}

    return colors

def display_map(df_filtered,polygon,population,kml_file_path,colors):
    """
    df_filtered : DataFrame of companies in the polygon
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
    folium.GeoJson(polygon,style_function=lambda x: {'opacity':'1',
                                                     'fillColor':'#cd982a',
                                                     'color':'#cd982a'}).add_to(m)

    # add the companies to the map with all the information
    for i in range(0,len(gdf)):

         # code for the color (e.g. "gray")
        color = colors[gdf.iloc[i]['codeApe']][0]

        # parameters for the marker
        folium.Marker(
            

            location=[gdf.iloc[i]['y_latitude'], gdf.iloc[i]['x_longitude']],

            popup=folium.Popup(
                '<b>'+gdf.iloc[i]['nomCommercial']+'</b><br>'
                +"Adresse : "+'<br>'+gdf.iloc[i]['adresse']+'<br>'
                +'Code NAF : '+'<br>'+str(gdf.iloc[i]['codeApe'])+'<br>'
                +'SIRET : '+'<br>'+str(gdf.iloc[i]['siret'])+'<br>'
                +'Diffusion Commerciale : '+'<br>'+str(gdf.iloc[i]['diffusionCommerciale'])+'<br>'

                # display confidence score as percentage rather than /5
                +"Confiance dans la localisation : "+'<br>'+str(int(gdf.iloc[i]['confiance']/5*100))+'%<br>'
                +'<a href="'+gdf.iloc[i]['lien_pappers']+'">Lien Pappers</a>'
            ),
    

            icon=folium.Icon(color = color,icon = 'industry', prefix='fa')
        ).add_to(m)


    # title in bold
    title = 'Cartographie des entreprises : '+ kml_file_path.split('/')[-1].split('.')[0].capitalize() 
    subtitle_1 = 'Population du bassin considéré : '+ "{:,}".format(population).replace(',',' ')+' habitants'
    subtitle_2 = "Source : INSEE, Registre national des Entreprises, La Poste"
    subtitle_3 ="NB : les informations sont données à titres indicatifs"

    # Create a single HTML element 
    html_content = '''
        <div>
            <h3 align="center" style="font-size:16px"><b>{}</b></h3>
            <h4 align="center" style="font-size:12px">{}</h4>
            <h4 align="center" style="font-size:10px"><i>{}</i></h4>
            <h4 align="center" style="font-size:8px"><i>{}</i></h4>
        </div>
    '''.format(title, subtitle_1, subtitle_2,subtitle_3)
    
    # add the title
    m.get_root().html.add_child(folium.Element(html_content))

    # change zoom to see the whole polygon
    m.fit_bounds(m.get_bounds())


    return m

# template for legend
template_start = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cartographie zone de chalandise </title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            right: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>

 
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>
     
<div class='legend-title'>Légende </div>
<div class='legend-scale'>
  <ul class='legend-labels'>"""
    
template_end = """


  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""

def add_legend(m,colors,naf_file = '../../data/Données nationales/NAF.parquet'):

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

    try :
        df_naf.shape[1] == len(colors)
    except Exception as e:
        print("Le fichier de Naf est incomplet, merci de le vérifier")

    # fonction qui ajoute une ligne par code NAF à la légende
    legende = ''
    
    for code_naf in df_naf.codeNaf :
        
        # hex code of the color corresponding to naf
        hex = colors[code_naf][1]

        # intitulé du code naf
        inti = df_naf[df_naf.codeNaf == code_naf].libelleNaf.values[0]

        text =  "<li><span style='background:{};opacity:0.7;'></span>{}</li>".format(hex,inti)

        legende += text

    # code principal pour la légende
   
    macro = MacroElement()
    macro._template = Template(template_start+legende+template_end)

    m.get_root().add_child(macro)

    return m

