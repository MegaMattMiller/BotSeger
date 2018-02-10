import re
import random
import sys
import twitter
import markovify
import os.path as path
import time
import pronouncing
from random import shuffle

if (len(sys.argv) > 1):
    if (sys.argv[1] == "0"):
        okToTweet = False
    else:
        okToTweet = True
else:
    okToTweet = True

configFilePath = "config.txt"
configFile = open(configFilePath)
keys = configFile.read().split('|')
configFile.close()
corpusFileName = "corpus.txt"

def random_line(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)

def makeShortSentenceFromCorpus(numberOfSentences):
    sentences = []
    with open(corpusFileName, 'rb') as corpusFile:
        text = corpusFile.read().decode('utf-8')
        text_model = markovify.NewlineText(text)
        for i in range(numberOfSentences):
            shortSentence = str(text_model.make_short_sentence(140))
            shortSentence = re.sub(r"http\S+", "", shortSentence)
            shortSentence = re.sub(r"#\S+", "", shortSentence)
            while ("@" in shortSentence.split(' ',1)[0]):
                shortSentence = shortSentence.split(' ',1)[1]
            shortSentence = shortSentence.replace("@", "")
            shortSentence = shortSentence.replace("RT", "")
            sentences.append(shortSentence)
    return sentences

def getSentenceThatEndsWithRhyme(sentences):
    shuffle(sentences)
    for sentence in sentences:
        lastWordInSentence = sentence.split(" ")[-1]
        rhymingWords = pronouncing.rhymes(lastWordInSentence)
        for subSentence in sentences:
            lastWordInSubSentence = subSentence.split(" ")[-1]
            if (lastWordInSubSentence in rhymingWords):
                return [sentence, subSentence]
    return ""    
        
def tweetRandomSentence(sentences):
    
    rhymingSentencesA = getSentenceThatEndsWithRhyme(sentences)
    # rhymingSentencesB = getSentenceThatEndsWithRhyme(sentences)
    # sentenceToTweet = "{0}\n{1}\n{2}\n{3}".format(rhymingSentencesA[0], rhymingSentencesB[0], rhymingSentencesA[1], rhymingSentencesB[1])
    sentenceToTweet = "{0}\n{1}".format(rhymingSentencesA[0], rhymingSentencesA[1])
    
    print("Tweet text:\n--------\n" + sentenceToTweet)
    if (sentenceToTweet == ""):
        print("I couldn't think of anything clever.")
        global okToTweet
        okToTweet = False
    if (okToTweet):
        print("Tweeting that")
        try:
            twitterAPI = twitter.Api(consumer_key=keys[2],
                                     consumer_secret=keys[3],
                                     access_token_key=keys[0],
                                     access_token_secret=keys[1])
            twitterAPI.PostUpdate(sentenceToTweet)
        except twitter.error.TwitterError as err:
            print("Twitter is unhappy with us! {0}".format(err))
    else:
        print("--------\nNot tweeting that.")

tweetRandomSentence(makeShortSentenceFromCorpus(5000))
