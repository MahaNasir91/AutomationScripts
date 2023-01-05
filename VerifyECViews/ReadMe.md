This script:
*Deletes folder in the given directory to free disk space
*Trigger job on jenkins to get & build Converter.
*Verifying that the required exe's are present.
*Convert the dgn files to .ibims's
*Sorts the Passing/Failing files in their respective folders after conversion
*Copying the passing bims from the Passing folder to the ibim folder
*Run the Gtest written for the view verification for the converted bims.
*Inserting the data in sql db.