import re, os, json, threading, io, time
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer

lock = threading.Lock()
ps = PorterStemmer()
file_numbers = {}
token_number = 0

def tokenize(text: str) -> list:
	pattern = re.compile(r"[a-zA-Z]+")
	return  [ps.stem(_.lower()) for _ in re.findall(pattern, text)]

def index_documents():
	current_index = defaultdict(lambda: defaultdict(int))
	create_file_numbers()
	t = threading.Thread()
	for domain in os.listdir("./sites"):
		start_threads(domain, current_index)
		tokens = update_token_numbers(current_index)
		if t.isAlive():
			t.join()
		t = threading.Thread(target = save_index, args = (current_index, tokens,))
		t.start()
		print('Finished sites in ' + domain + '.')
	t.join()
	encode_tokens()
	print('Finished encoding tokens')

def encode_tokens():
	tokens = []
	token_dict = {}
	with open('tokens.json', 'r') as file:
		tokens = [_.rstrip() for _ in file]
	with open('index.txt', 'r') as file:
		with open('tokens.json', 'w+') as destination:
			file.seek(0)
			for token in tokens:
				token_dict[token] = file.tell()
				file.readline()
			destination.write(json.dumps(token_dict))


def save_index(index: dict, tokens: list):
	current_line = 0
	with open('index.txt', 'r') as file:
		with open('index.temp', 'w+') as destination:
			for line in file:
				term = json.loads(line.rstrip())
				term = merge_dict(term, index[tokens.pop(0)])
				destination.write(json.dumps(term) + '\n')
			for token in tokens:
				destination.write(json.dumps(index[token]) + '\n')
	os.remove('index.txt')
	os.rename('index.temp', 'index.txt')

def create_file_numbers():
	global file_numbers
	file_number = 0
	for domain in os.listdir("./sites"):
		for filename in os.listdir("./sites/" + domain):
			file_numbers[domain + '/' + filename] = file_number
			file_number += 1
		with open("file_index.json", 'w+') as file:
			file.write(json.dumps({v: k for k, v in file_numbers.items()}))

def update_token_numbers(index: dict):
	tokens = []
	if os.path.isfile('tokens.json'):
		with open('tokens.json', 'r') as file:
			tokens = [_.rstrip() for _ in file]
	for token in index:
		if not token in tokens:
			tokens.append(token)
	with open('tokens.json', 'w+') as file:
		for token in tokens:
			file.write(token + '\n')
	return tokens

def start_threads(domain: str, index):
	threads = []
	for filename in os.listdir("./sites/" + domain):
		t = threading.Thread(target = process_document, args = (domain + '/' + filename, index,))
		threads.append(t)
	active_threads = []
	while(threads):
		if threading.active_count() < 64:
			t = threads.pop(0)
			active_threads.append(t)
			t.start()
	else:
		for thread in active_threads:
			thread.join()

def merge_dict(dict1, dict2):
	result = dict1
	for item in dict2:
		if item in dict1:
			if type(dict1[item]) is dict or defaultdict:
				result[item] = merge_dict(dict1[item], dict2[item])
			if type(dict1[item]) is int:
				result[item] = dict1[item] + dict2[item]
		else:
			result[item] = dict2[item]
	return result

def process_document(filepath: str, index: dict):
	with open("./sites/" + filepath) as file:
		site = json.load(file)
		token_counts = defaultdict(int)
		try:
			bs = BeautifulSoup(bytes(site['content'], 'utf-8').decode("unicode_escape"), 'lxml')
			text = ''
			if bs.h1 and bs.h1.string:
				text += bs.h1.string + ' '
			if bs.h2 and bs.h2.string:
				text += bs.h2.string + ' '
			if bs.h3 and bs.h3.string:
				text += bs.h3.string + ' '
			if bs.title and bs.title.string:
				text += bs.title.string + ' '
			if bs.strong and bs.strong.string:
				text += bs.strong.string + ' '
			for token in tokenize(text):
				token_counts[token] += 1
		except UnicodeDecodeError:
			for token in tokenize(BeautifulSoup(site['content'], 'lxml').text):
				token_counts[token] += 1
		lock.acquire()
		for token in token_counts:
			index[token][file_numbers[filepath]] = token_counts[token]
		lock.release()
	print('Finished indexing ' + filepath + '.')

index_documents()