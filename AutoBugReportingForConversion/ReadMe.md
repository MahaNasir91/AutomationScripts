Against a Csv file provided by the user(after Conversion):
*Reads te csv file
*Locates the failing Dgn file(a 2D/3D drawing file) from the dataset
*Copies them to a seperate csv
*Read the csv file for bug reporting
*Creates a VSTS item for each failing dgn
*Sets the fields for the vsts item
*Upload an issue file for the respective Dgn
*Adds steps to reproduce the failure
*Assigns it to the person responsible for fixing it.