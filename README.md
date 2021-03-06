# Basic Search Engine

Here's a basic search engine written in Python that runs on any command line interface, like Terminal on Mac. 

### Details:

- The data set used for this engine is a large collection of JSON files that each relate to a specific website within the UC Irvine computer science department's website domain. 
  - Here's the link to download it (it's a rather large folder): https://www.ics.uci.edu/~algol/teaching/informatics141cs121w2020/a3files/developer.zip
  - You must have these sets of folders under a bigger folder named "sites", and that folder must reside in the same directory as the rest of the repository

- The search engine includes an inverted index that maps a token to a corresponding posting describing the token. 
  - In this case, the token would be terms that the user inputted in their search, and the index's job is to help identify the term within a document and give it a TF-IDF score. This score is used to rank its relevancy to the overall user query and help find relevant documents most associated with that term.
  
- The engine also includes a script to implement the actual search component that requests input from the user via command line, then it utilizes the indexer to display the top 5 most meaningful URLs for the particular user query. Make sure the libraries listed in the import statements are installed onto your local machine, such as the "orjson" library.
