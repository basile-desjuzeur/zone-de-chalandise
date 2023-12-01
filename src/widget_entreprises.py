import pandas as pd
import ipywidgets as widgets
from IPython.display import display

# Read the Excel file
file_path = "./Données nationales/NAF.xlsx"
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
naf = []

# Function to handle selection change
def on_dropdown_change(change):
    naf.clear()
    naf.extend(change.new)

# Attach the function to the change event
naf_dropdown.observe(on_dropdown_change, names='value')


