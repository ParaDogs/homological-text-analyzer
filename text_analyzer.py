import collections
import functools
import pymorphy2
import numpy

END_SENTENCE_MARKS = ['...', '.', '?', '!']
END_PARAGRAPH = ['\n', '\t', '    ', '  ']
PUNCTUATION_MARKS = [',', ';', '"', ':', '—', '\n', '«', '»'] + END_SENTENCE_MARKS
MORPH = pymorphy2.MorphAnalyzer()

def angular_distance(v1, v2):
    a = numpy.asfarray(v1, float)
    b = numpy.asfarray(v2, float)
    numerator = numpy.dot(a,b)
    denominator = numpy.linalg.norm(v1)*numpy.linalg.norm(v2)
    return numpy.arccos(numerator/denominator)

class Token:
    def __init__(self, string, text):
        self.text = text
        self.data = string
        self.words = Text(self.data, text.split_method).words
        self.word_counter = collections.Counter(self.words)

    def vector(self):
        v = []
        text_unique_words = list(self.text.word_counter)
        for e in text_unique_words:
            v += [self.word_counter[e]]
        return v

    def __str__(self):
        return self.data

    def __repr__(self):
        return self.data

    def __hash__(self):
        return hash(self.data)

class Text:
    def __init__(self, string, split_method):
        self.data = string
        self.split_method = split_method
        prewords = self.data.split(' ')
        prewords = list(map(lambda w: w.lower(), prewords))
        for i in range(len(prewords)):
            for mark in PUNCTUATION_MARKS: prewords[i] = prewords[i].replace(mark, '')
        prewords = list(map(lambda w: MORPH.parse(w)[0].normal_form, prewords))
        self.words = prewords
        self.word_counter = collections.Counter(self.words)
        self.dim = len(self.word_counter)

    def tokenize(self):
        text = self.data
        TEMP_MARK = '$$$'
        if self.split_method == "sentence":
            for mark in END_SENTENCE_MARKS: text = text.replace(mark, mark+TEMP_MARK)
        elif self.split_method == "paragraph":
            for mark in END_PARAGRAPH: text = text.replace(mark, mark+TEMP_MARK)
        text_parts = text.split(TEMP_MARK)
        tokens = [Token(part, self) for part in text_parts if part != '']
        return tokens

class TokenSpace:
    def __init__(self, token_list, metric, diameter):
        self.token_list = token_list
        self.metric = metric
        self.diameter = diameter
        self.connectivity_list = self.get_connectivity_list()
        self.betti_number_0 = self.get_betti_number_0()
        self.betti_number_1 = self.get_betti_number_1()

    def get_connectivity_list(self):
        connectivity_list = []
        for token in self.token_list:
            connectivity_token = [token, []]
            for vertex in self.token_list:
                if vertex.data != token.data:
                    if self.metric(token.vector(), vertex.vector()) <= self.diameter:
                        connectivity_token[1] += [vertex]
            connectivity_list += [connectivity_token]
        return connectivity_list

    def get_simplexes_0(self):
        return self.token_list

    def get_simplexes_1(self):
        simplexes = []
        for e in self.connectivity_list:
            for vert in e[1]:
                s = {e[0], vert}
                if s not in simplexes:
                    simplexes += [s]
        if (self.diameter == 1.5):
            print(simplexes)
        return simplexes

    def get_simplexes_2(self):
        simplexes = []
        simplexes_1 = self.get_simplexes_1()
        for simplex_1 in simplexes_1:
            vert_list = list(simplex_1)
            connected_vertices = set(self.connectivity_list[self.token_list.index(vert_list[0])][1]).intersection(set(self.connectivity_list[self.token_list.index(vert_list[1])][1]))
            if len(connected_vertices) != 0:
                for vert in connected_vertices:
                    new_simplex_2 = set(simplex_1.union({vert})) 
                    if new_simplex_2 not in simplexes: simplexes += [new_simplex_2]
        return simplexes

    def border_operator_1(self, simplex_1):
        simplex_list = list(simplex_1)
        vert_0 = simplex_list[0]
        vert_1 = simplex_list[1]
        simplexes_0 = self.get_simplexes_0()
        res = [0 for s in simplexes_0]
        res[simplexes_0.index(vert_0)] = 1
        res[simplexes_0.index(vert_1)] = -1
        return res

    def border_operator_2(self, simplex_2):
        simplex_list = list(simplex_2)
        simplex1_0 = {simplex_list[1], simplex_list[2]}
        simplex1_1 = {simplex_list[0], simplex_list[2]}
        simplex1_2 = {simplex_list[0], simplex_list[1]}
        simplexes_1 = self.get_simplexes_1()
        res = [0 for s in simplexes_1]
        res[simplexes_1.index(simplex1_0)] = 1
        res[simplexes_1.index(simplex1_1)] = -1
        res[simplexes_1.index(simplex1_2)] = 1
        return res

    def get_betti_number_0(self):
        dim_C0 = len(self.get_simplexes_0())
        simplexes_1 = self.get_simplexes_1()
        border_1_matrix = numpy.array([self.border_operator_1(s1) for s1 in simplexes_1])
        rank_1 = numpy.linalg.matrix_rank(border_1_matrix)
        return dim_C0 - rank_1

    def get_betti_number_1(self):
        dim_C1 = len(self.get_simplexes_1())
        simplexes_2 = self.get_simplexes_2()
        border_2_matrix = numpy.array([self.border_operator_2(s2) for s2 in simplexes_2])
        rank_2 = numpy.linalg.matrix_rank(border_2_matrix)
        #simplexes_1 = self.get_simplexes_1()
        #border_1_matrix = numpy.array([self.border_operator_1(s1) for s1 in simplexes_1])
        #rank_1 = numpy.linalg.matrix_rank(border_1_matrix)
        return dim_C1 - rank_2 #- rank_1