# miner_postprocessing

This app allows you to postprocess the results of `conditions_bugfix`. You have to save all txt files in **data/conditions_bugfix** folder.
The app will clean the data using different steps:
1. **remove_wrong_records** function will check all data to see if they are correct (sometimes may happen that the miner extracts wrong records)
2. **remove_longer_records** function will remove records whose length is greater than 100
3. **remove_duplicates** function will remove duplicates (it checks only the commit ID, we experimentally see that in that case the commit message is the same because developer applies the same edit to different branches)
4. **export_files_masked** will export txt files containing *id_internal* (GhArchive ID useful to merge information with other files), *id commit*, *repo*, *masked code* (where the condition changed is replaced by a **<x>** token), *mask before* and *mask after* (containing the condition changed with a **<z>** token at the end)