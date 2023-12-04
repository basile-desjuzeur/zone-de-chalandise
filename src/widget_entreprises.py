import pandas as pd
import dask.dataframe as dd
import ipywidgets as widgets
from IPython.display import display
import os
from script import kml_to_polygon,get_companies
import csv



#1. Sélection de l'aire géographique


# Function to get the list of files in the specified directory
def get_files_list(directory):

    list = os.listdir(directory)
    list_only_kml = [file for file in list if file.endswith('.kml')]

    return list_only_kml

# Specify the directory
directory_path = "../Données sites"

# Dropdown widget to select a file
dropdown = widgets.Dropdown(
    options=get_files_list(directory_path),
    value=None,
    description='Select a file:',
)

# Display the dropdown widget
display(dropdown)

# variable to store the selected file
selected_file = None

# Function to handle selection change
def on_dropdown_change(change):
    global selected_file
    selected_file = change.new

# Attach the function to the change event
dropdown.observe(on_dropdown_change, names='value')




#2. Sélection des secteurs d'activité

# Read the Excel file
file_path = "../Données nationales/NAF.xlsx"
df = pd.read_excel(file_path)

# Get unique elements in the 'libellé' column
naf_options = sorted(df['Libellé'].unique())


# Create a dropdown menu with checkboxes
naf_dropdown = widgets.SelectMultiple(
    options=naf_options,
    value=[],
    description='Select NAF:',
    disabled=False,
    layout=widgets.Layout(width='50%')
)

# Display the dropdown menu
display(naf_dropdown)

# Store the selected options in a list 'naf'
selected_naf = []

# Function to handle selection change
def on_dropdown_change(change):
    selected_naf.clear()
    selected_naf.extend(change.new)

# Attach the function to the change event
naf_dropdown.observe(on_dropdown_change, names='value')




#3. Validation de la sélection

# Button widget to validate the selection
button = widgets.Button(
    description='Valider',
    disabled=False,
    button_style='success', 
    tooltip='Valider la sélection',
    icon='check'
)

# Display the button widget
display(button)

# Function to handle button click

def on_button_clicked(b):
    # Check if a file is selected
    if selected_file is None:
        print('Veuillez sélectionner un fichier')
        return
    # Check if at least one NAF is selected
    if len(selected_naf) == 0:
        print('Veuillez sélectionner au moins un secteur d\'activité')
        return
    
    # converts the selected libelle in 'selected_naf' to naf codes
    df = pd.read_excel('../Données nationales/NAF.xlsx')

    naf = df[df['Libellé'].isin(selected_naf)]['NAF'].tolist()

    # Get the polygon from the kml file
    polygon = kml_to_polygon(directory_path + '/' + selected_file)

    # load the dataframe
    print('Chargement du fichier source ...')


    df_siret = dd.read_csv('../Données nationales/localisation_et_naf_siret.csv', sep=',', on_bad_lines='skip',
                       dtype={'siret': 'object', 'plg_code_commune': 'object', 'y_latitude': 'object',
                              'x_longitude': 'object', 'codeCommuneEtablissement': 'object',
                              'activitePrincipaleEtablissement': 'object'},quoting=csv.QUOTE_NONE)


    


    # Get the companies in the polygon
    df = get_companies(naf, polygon, df_siret)


    print('Nombre d\'entreprises trouvées: ' + str(len(df)))

    output_path = "../Données sites/"+selected_file[:-4]+"_entreprises.csv"

    df.to_csv(output_path,index=False,single_file=True,errors='ignore')    

    print("Les informations relatives à la localisation des entreprises ont été enregistrées dans le fichier ./Données sites/"+selected_file[:-4]+"_entreprises.csv")

# Attach the function to the button click event
button.on_click(on_button_clicked)

