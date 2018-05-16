from __future__ import division
import math as m
import time
import sys


CONSTANT = 10000
file = open(sys.argv[1], 'r')
#file = open('sampleData.txt','r')

training_file = file.read()
training_file = training_file.strip()
training_file = training_file.split("\n")

# length of words in training file
num_of_sentences = len(training_file)  #
# print (num_of_sentences)

# stores all the starting tags
start_tag = {}
final_tag = {}
# stores the words and all the tags associated with that word
word_dict = {}

# stores the tags and the tag count
tag_dict = {}

tag_list = []
# store the prev tags
prev_tag_dict = {}
tag_count = 0
t0 = time.time()
for i in range(num_of_sentences):
    temp_sentence = training_file[i].strip()
    temp_sentence = temp_sentence.split(" ")
    temp_sen_len = len(temp_sentence)
    tag_list.append("start")
    for k in range(temp_sen_len):
        # store all the words and tags in seperate arrays and store them in dictionaries with it's count'
        temp = temp_sentence[k].strip(" ")
        temp = temp.rsplit("/", 1)
        if k == 0:
            if temp[1] in start_tag:
                start_tag[temp[1]] += 1
            else:
                start_tag[temp[1]] = 1
        if k == temp_sen_len-1:
            if temp[1] in final_tag:
                final_tag[temp[1]] += 1
            else:
                final_tag[temp[1]] = 1
        tag_list.append(temp[1])
        if temp[0] in word_dict and temp[1] in word_dict[temp[0]]:
            word_dict[temp[0]][temp[1]] += 1
        else:
            word_dict[temp[0]] = word_dict.get(temp[0], {})
            word_dict[temp[0]][temp[1]] = 1
        if temp[1] in tag_dict:
            tag_dict[temp[1]] += 1
        else:
            tag_dict[temp[1]] = 1
    tag_list.append('finish')
file2 = open('hmmmodel_tags.txt','w')
for key in tag_dict:
    file2.write("%s\t%s\n"%(key,tag_dict[key]))
file2.close()
file2 = open('hmmmodel_emission_prob.txt','w')
# Emission Probability
prob_tag_given_word = {}
for key in word_dict:
    for value in word_dict[key]:
        prob_tag_given_word[key] = prob_tag_given_word.get(key, {})
        # prob_tag_given_word[key][value] = ((word_dict[key][value]) / (float(tag_dict[value])))*CONSTANT
        prob_tag_given_word[key][value] = m.log((word_dict[key][value]) / (float(tag_dict[value])))
        file2.write("%s\t%s\t%s\n" % (key,value,prob_tag_given_word[key][value]))
file2.close()
# --------------------------- TRANSITION ------------------------------------
file2 = open('hmmmodel_transition_prob.txt','w')
tag_list_length = len(tag_list)
for tag_index in range(tag_list_length):
    if tag_list[tag_index] == "start":
        continue
    elif tag_list[tag_index-1] in prev_tag_dict and tag_list[tag_index] in prev_tag_dict[tag_list[tag_index-1]]:
        prev_tag_dict[tag_list[tag_index-1]][tag_list[tag_index]] += 1
    else:
        prev_tag_dict[tag_list[tag_index-1]] = prev_tag_dict.get(tag_list[tag_index-1], {})
        prev_tag_dict[tag_list[tag_index-1]][tag_list[tag_index]] = 1
# Storing data to calculate Transition Probability

transition_probability = {}
for key in tag_dict:
    if key in start_tag:
        transition_probability["start "+key] = m.log((start_tag[key])/ (float(num_of_sentences)))
        # transition_probability["start " + key] = ((start_tag[key]) / (float(num_of_sentences)))*CONSTANT
    else:
        transition_probability["start "+key] = m.log(1 / (float(num_of_sentences)))
        # transition_probability["start " + key] = (1 / (float(num_of_sentences)))*CONSTANT
    file2.write("%s\t%s\n" % ('start ' + key, transition_probability["start " + key]))
for key in tag_dict:
    transition_probability[key] = transition_probability.get(key,{})
    prob = sum(prev_tag_dict[key].values())
    for value in tag_dict:
        if key in prev_tag_dict and value in prev_tag_dict[key]:
            transition_probability[key+' '+value] = m.log((prev_tag_dict[key][value])/(float(prob)))
            # transition_probability[key + ' ' + value] = ((prev_tag_dict[key][value]) / (float(prob)))*CONSTANT
        else:
            transition_probability[key+' '+value] = m.log(1/(float(prob)))
            # transition_probability[key + ' ' + value] = (1 / (float(prob)))*CONSTANT
        file2.write("%s\t%s\n" % (key + ' ' + value, transition_probability[key + " " + value]))
for key in tag_dict:
    if key in final_tag:
        transition_probability[key+" final"] = m.log((final_tag[key])/(float(num_of_sentences)))
        # transition_probability[key + " final"] = ((final_tag[key]) / (float(num_of_sentences)))*CONSTANT
    else:
        transition_probability[key+" final"] = m.log(1 / (float(num_of_sentences)))
        # transition_probability[key + " final"] = (1 / (float(num_of_sentences)))*CONSTANT
    file2.write("%s\t%s\n" % (key + ' final', transition_probability[key+" final"]))
file2.close()
t1 = time.time()
#print("Time taken: "+str(t1-t0))
