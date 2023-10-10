# Genre analysis with Spotify data

This project uses Python to open listening history data obtained from Spotify, pull artist genres using the Spotify API, and then export the cleaned dataset with genres as a .csv file to be used for further analysis.

I show one way an interested user could look at their listening history by graphing the frequency of genres listened to over the course of an average day using ggplot2 in R. The resulting graphs for my data are included in the project.

## Using the project

1. Request your listening data from spotify. Information on how to do this can be found here: https://support.spotify.com/ca-en/article/data-rights-and-privacy-settings/.
2. Download the spotify_dataset_creation.py and genre_analysis.Rmd files
3. Replace file paths and other user-dependent variables at the top of the files as instructed.
4. Run the python file first to generate the .csv, then run the Rmarkdown file to generate the graphs.


Credit to Vlad Gheorghe and his piece on towardsdatascience.com which inspired and helped me with this project. Article can be found here: https://towardsdatascience.com/get-your-spotify-streaming-history-with-python-d5a208bbcbd3.
