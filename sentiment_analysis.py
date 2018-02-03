#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 17:26:50 2018

@author: mashex
"""

import nltk
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from nltk import pos_tag
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk.chunk import conlltags2tree
from nltk.tree import Tree
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sentiment_mod as s

style.use('fivethirtyeight')

# Process text  
def process_text(txt_file):
	token_text = word_tokenize(txt_file)
	return token_text

# Stanford NER tagger    
def stanford_tagger(token_text):
	st = StanfordNERTagger('/usr/share/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
							'/usr/share/stanford-ner/stanford-ner.jar',
							encoding='utf-8')   
	ne_tagged = st.tag(token_text)
	return(ne_tagged)
 
# NLTK POS and NER taggers   
def nltk_tagger(token_text):
	tagged_words = nltk.pos_tag(token_text)
	ne_tagged = nltk.ne_chunk(tagged_words)
	return(ne_tagged)

# Tag tokens with standard NLP BIO tags
def bio_tagger(ne_tagged):
		bio_tagged = []
		prev_tag = "O"
		for token, tag in ne_tagged:
			if tag == "O": #O
				bio_tagged.append((token, tag))
				prev_tag = tag
				continue
			if tag != "O" and prev_tag == "O": # Begin NE
				bio_tagged.append((token, "B-"+tag))
				prev_tag = tag
			elif prev_tag != "O" and prev_tag == tag: # Inside NE
				bio_tagged.append((token, "I-"+tag))
				prev_tag = tag
			elif prev_tag != "O" and prev_tag != tag: # Adjacent NE
				bio_tagged.append((token, "B-"+tag))
				prev_tag = tag
		return bio_tagged
    
    
    
# Create tree       
def stanford_tree(bio_tagged):
	tokens, ne_tags = zip(*bio_tagged)
	pos_tags = [pos for token, pos in pos_tag(tokens)]

	conlltags = [(token, pos, ne) for token, pos, ne in zip(tokens, pos_tags, ne_tags)]
	ne_tree = conlltags2tree(conlltags)
	return ne_tree

def structure_ne(ne_tree):
	ne = []
	for subtree in ne_tree:
		if type(subtree) == Tree: # If subtree is a noun chunk, i.e. NE != "O"
			ne_label = subtree.label()
			ne_string = " ".join([token for token, pos in subtree.leaves()])
			ne.append((ne_string, ne_label))
	return ne

def stanford_main(tweet):
	print(structure_ne(stanford_tree(bio_tagger(stanford_tagger(process_text(tweet))))))

def nltk_main(tweet):
	print(structure_ne(nltk_tagger(process_text(tweet))))
    
'''if __name__ == '__main__':
	stanford_main()
	nltk_main()'''
    



#consumer key, consumer secret, access token, access secret.
ckey="Rid5cdQhSvpqKI9O3Mjv2oOFp"
csecret="TY5QQciIyx86oMzttVvl3LbgJCfDQnjm5NAT4tcRDYKjZw8pwz"
atoken="73582111-oHpkBJftMKHJj0NzKtMXE8NOGo1GRBuH1QugYjqR7"
asecret="iRoLWPcb1fp64fW7UJt25YLFi1v6isPlCGOFfYvGM78FW"

import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

class listener(StreamListener):

    def on_data(self, data):

        all_data = json.loads(data)
        tweet = all_data["text"]
        sentiment_value, confidence = s.sentiment(tweet)
        
        print (tweet,sentiment_value)
        #print(tweet, sentiment_value, confidence)
        nltk_main(tweet)
        '''if confidence*100 >= 80:
            output = open("twitter-out.txt","a")
            output.write(sentiment_value)
            output.write('\n')
            output.close()'''

        return True

    def on_error(self, status):
        print(status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["Donald Trump"])

