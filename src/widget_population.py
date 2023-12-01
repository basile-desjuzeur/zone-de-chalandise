import os
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from src.script import kml_to_polygon,get_population

# Function to get the list of files in the specified directory
def get_files_list(directory):
    return os.listdir(directory)

# Specify the directory
directory_path = "./Données sites"

# Dropdown widget to select a file
dropdown = widgets.Dropdown(
    options=get_files_list(directory_path),
    value=None,
    description='Select a file:',
)

# Display the dropdown widget
display(dropdown)

# Create a button to run the script and display the output
button_run_script = widgets.Button(description="Calculer la population")
output_script = widgets.Output()

# Function to handle button click event for running the script
def on_button_run_script_click(b):
    with output_script:
        clear_output(wait=True)
        # Check if a file is selected in the dropdown
        selected_file = dropdown.value
        if selected_file:
            script_path = "./src/script.py"
            file_path = f'./Données sites/{selected_file}'
            population_path = "./Données nationales/population-par-commune.csv"
            

            polygon = kml_to_polygon(file_path)

            get_population(polygon,population_path)
            
        else:
            print("Please select a file from the dropdown.")

# Attach the button click event for running the script
button_run_script.on_click(on_button_run_script_click)

# Display the buttons and output widgets
display(button_run_script, output_script)
