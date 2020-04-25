from __future__ import division
from nltk.stem import PorterStemmer
from scipy import spatial
import os, math, orjson
#import time

class QueryError(Exception):
	pass

def stem(query):
	""" Takes in a query as a string, returns a list of stemmed words that derive
		the query terms """
		
	new_words = list()
	ps = PorterStemmer()
	terms = query.lower().strip().split()
	for term in terms:
		root_word = ps.stem(term)
		if (root_word not in new_words):
			new_words.append(root_word)
	return new_words


def doc_list(query, tokens, index):
	""" Creates a list of documents that are relevant to the query terms """

	result = []
	for word in query:
		index.seek(tokens[word], os.SEEK_SET)
		token = orjson.loads(index.readline())
		for doc in list(token.keys()):
			if doc not in result:
				result.append(doc)
	return result


def docTFIDF(token, doc):
	""" Takes a token dictionary and a specific document, computes the document's tf_idf score in relation to that token """

	tf = token[doc]
	idf = math.log10(1644 / len(token))

	return tf * idf
	

def queryTFIDF(query, word, docs):
	""" Takes the query and a specific word in the query, computes the tf_idf score in relation to
		that word """

	tf = query.count(word)
	idf = math.log10(1644 / len(docs))
	
	return tf * idf
	
	
def doc_vector(query, tokens, index, doc):
	""" Creates the document vector containing the tf-idf scores for each term in the query """

	dv = []
	for word in query:
		index.seek(tokens[word], os.SEEK_SET)
		token = orjson.loads(index.readline())
		dv.append(docTFIDF(token, doc) if doc in token.keys() else 0)
	return dv
	
	
def query_vector(query, tokens, index):
	""" Creates the query vector containing the tf-idf scores for each term in the query """

	qv = []
	for word in query:
		index.seek(tokens[word], os.SEEK_SET)
		token = orjson.loads(index.readline())
		qv.append(queryTFIDF(query, word, list(token.keys())))
	return qv
	
	
def cosine_similarity(vector1, vector2):
	""" Computes the cosine similarity given two vectors of equal size """
	
	return 1 - spatial.distance.cosine(vector1, vector2)
 
 
def find_URLs(ranked_list, file_index):
	""" Given the ranked list of documents based on cosine similarity, find the URLs associated with
		each document and return them """
		
	urls = []
	searched = []
	
	for item in ranked_list:
		doc = item[1]
		if doc not in searched:
			searched.append(doc)
			j = orjson.loads(open("sites/" + file_index[doc]).read())
			urls.append(j["url"])
		if (len(urls) == 5):
			break
	return urls
	
def check_query(query, tokens):
	result = []
	for word in query:
		if word in tokens:
			result.append(word)
	if not result:
		raise QueryError
	return result
	
def main():
	#start_time = time.time()
	file_index = orjson.loads(open("file_index.json").read())
	tokens = orjson.loads(open("tokens.json").read())
	index = open("index.txt", "r")
	while True:
		query = input("Enter a query: ")
		ranked_list = []
		query = stem(query)
		try:
			query = check_query(query, tokens)
		except QueryError:
			print('Your terms are not in the corpus.')
			continue
		qv = query_vector(query, tokens, index)	# query vector of tf-idf scores

		docs = doc_list(query, tokens, index)	# creates list of relevant documents

		for doc in docs:
			dv = doc_vector(query, tokens, index, doc)   # document vector of tf-idf scores
			doc_rank = (cosine_similarity(qv, dv), doc)   # cosine similarity score
			if doc_rank not in ranked_list:
				ranked_list.append(doc_rank) # not ranked yet
		
		ranked_list = sorted(ranked_list, key = lambda x : x[0], reverse = True)  # ranked
		
		for url in find_URLs(ranked_list, file_index):
			print(url)
		
	index.close()
		#print(time.time() - start_time)
			
			
### cos(q,d) after normalization = sum of [(tf-idf score of term in query) * (tf-idf score of term in document)] across all terms
	

if __name__ == "__main__":
	main()
