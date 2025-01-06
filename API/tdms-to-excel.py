from nptdms import TdmsFile
import pandas as pd
import sys
import os

# Get TDMS file path and output Excel path from the command-line arguments
tdms_file_path = sys.argv[1]
output_file_path = sys.argv[2]

# Check if the TDMS file exists
if not os.path.exists(tdms_file_path):
    print(f"TDMS file '{tdms_file_path}' not found.")
    sys.exit(1)

# Read the TDMS file
tdms_file = TdmsFile.read(tdms_file_path)

# Create an Excel writer object
with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
    # Loop over each group in the TDMS file
    for group in tdms_file.groups():
        group_name = group.name  # Use the group name for the sheet name
        
        # Create a DataFrame to store group data
        group_data = pd.DataFrame()
        
        # Loop over each channel in the group
        for channel in group.channels():
            # Add the channel data to the DataFrame with channel name as the column header
            group_data[channel.name] = channel.data
        
        # Write the group data to a separate sheet in the Excel file
        group_data.to_excel(writer, sheet_name=group_name, index=False)

print(f"TDMS file '{tdms_file_path}' successfully converted to '{output_file_path}'.")
