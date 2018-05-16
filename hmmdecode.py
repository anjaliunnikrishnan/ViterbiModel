import math as m
import time
import sys

SMOOTHEN_VALUE = m.log(0.001)


def read_file_emission(file):
    dictionary = {}
    f = open(file,'r')
    data = f.read()
    data = data.strip().split("\n")
    count = 0
    for line in data:
        line = line.strip()
        line = line.split("\t")
        dictionary[line[0]] = dictionary.get(line[0],{})
        dictionary[line[0]][line[1]] = float(line[2])
        count += 1
    return dictionary


def read_file(file):
    dictionary = {}
    f = open(file, 'r')
    data = f.read()
    data = data.strip().split("\n")
    for line in data:
        line = line.strip().split("\t")
        dictionary[line[0]] = float(line[1])
    return dictionary


emission_prob = read_file_emission("hmmmodel_emission_prob.txt")
transition_prob = read_file("hmmmodel_transition_prob.txt")
tag_dict = read_file("hmmmodel_tags.txt")
file_output = open('hmmoutput.txt','w')


def smoothen(word, state):
    if word in emission_prob and  state in emission_prob[word]:
        return emission_prob[word][state]
    else: return SMOOTHEN_VALUE


def get_states(word):
    if word in emission_prob:
        return emission_prob[word]
    else:
        return tag_dict


def write_backpointer(words, backpointer):
    state = 'final'
    index = len(words)
    key = (state, index)
    final_states = []
    while index > 0:
        final_states.append(backpointer[key])
        state = backpointer[key]
        index = index - 1
        key = (state, index)
    final_states.reverse()
    for i in range(len(final_states)):
        file_output.write(words[i]+"/"+final_states[i]+" ")
    file_output.write("\n")


time1 = time.time()
with open(sys.argv[1], 'r') as f:
    for sentence in f:
        sentence = sentence.strip()
        words = sentence.split(" ")
        # Initialization step
        viterbi = {}
        backpointer = {}
        prev_states = []
        states = get_states(words[0])
        for state in states:
            if "start " + state in transition_prob:
                viterbi[state, 0] = transition_prob["start " + state] + smoothen(words[0],state)
                backpointer[state, 1] = 0
        prev_states = states
        for t in range(1, len(words)):
            states = get_states(words[t])
            for state in states:
                max_viterbi = float("-inf")
                max_backpointer = float("-inf")
                for s in prev_states:
                    x = viterbi[s, (t - 1)] + transition_prob[s + " " + state] + smoothen(words[t], state)
                    if x > max_viterbi:
                        max_viterbi = x
                        max_backpointer = s
                viterbi[state, t] = max_viterbi
                backpointer[state, t] = max_backpointer
            prev_states = states
        max_viterbi = float("-inf")
        max_backpointer = float("-inf")
        # Termination step
        for s in prev_states:
            x = viterbi[s, (len(words)-1)] + transition_prob[s + ' final']
            if x > max_viterbi:
                max_viterbi = x
                max_backpointer = s
        viterbi['final',len(words)] = max_viterbi
        backpointer['final', len(words)] = max_backpointer
        write_backpointer(words,backpointer)

file_output.close()
t2 = time.time()
#print(str(t2-time1))
