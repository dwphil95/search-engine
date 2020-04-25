# Basic Search Engine

Here's a basic search engine written in Python that runs on any command line interface, like Terminal on Mac. 

### Details:

- The data set used for this engine is a large collection of JSON files that each relate to a specific website within the UC Irvine computer science department's website domain.

- The search engine includes an inverted index that maps a token to a corresponding posting describing the token. 
  - In this case, the token would be terms that the user inputted in their search, and the index's job is to help identify the term within a document and give it a TF-IDF score. This score is used to rank its relevancy to the overall user query and help find relevant documents most associated with that term.
  
- The engine also includes a script to implement the actual search interface that utilizes the indexer and displays the top 5 most meaningful URLs for the particular user query.
