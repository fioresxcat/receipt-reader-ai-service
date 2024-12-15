import pdb
import math
import numpy as np
from .base_lm import Base_LM

class Node:
    def __init__(self, value, parent, length):
        self.value = value
        self.parent = parent
        self.children = {}
        self.length = length

    def add_child(self, value, parent, length):
        if value.lower() not in self.children.keys():
            new_node = Node(value, parent, length)
            self.children[value.lower()] = new_node
        return self.children[value.lower()]

    def get_value(self):
        return self.value

    def get_length(self):
        return self.length

    def find_child(self, value):
        children = []
        if value in self.children.keys():
            children.append(self.children[value])
        return children


class FWTREE:
    def __init__(self, dictionary_path):
        self.product_names = []
        with open(dictionary_path, 'r') as f:
            for row in f:
                self.product_names.append(row[:-1].split(' '))
        self.root = Node('', None, 0)

    def load_tree(self):
        for product_name in self.product_names:
            current_node = self.root
            for word in product_name:
                current_node = current_node.add_child(word, current_node, current_node.length + 1)


class ProductName_LM(Base_LM):
    def __init__(self, dict_path, max_words):
        super(ProductName_LM, self).__init__()
        self.fwtree = FWTREE(dict_path)
        self.fwtree.load_tree()
        self.similar_threshold = 1.0
        self.groups = []
        self.groups.append(set(['a', 'á', 'à', 'ả', 'ã', 'ạ', 'ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ', '4']))
        self.groups.append(set(['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ', 'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', '0', 'c']))
        self.groups.append(set(['u', 'ù', 'ú', 'ủ', 'ũ', 'ụ', 'o', 'ò', 'ó', 'ỏ', 'õ', 'ọ']))
        self.groups.append(set(['u', 'ù', 'ú', 'ủ', 'ũ', 'ụ', 'ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự']))
        self.groups.append(set(['á', 'ắ', 'ấ', 'ó', 'ố', 'ớ', 'ú', 'ứ']))
        self.groups.append(set(['à', 'ằ', 'ầ', 'ò', 'ồ', 'ờ', 'ù', 'ừ']))
        self.groups.append(set(['ả', 'ẳ', 'ẩ', 'ỏ', 'ổ', 'ở', 'ủ', 'ử']))
        self.groups.append(set(['ã', 'ẵ', 'ẫ', 'õ', 'ỗ', 'ỡ', 'ũ', 'ữ']))
        self.groups.append(set(['ạ', 'ặ', 'ậ', 'ọ', 'ộ', 'ợ', 'ụ', 'ự']))
        self.groups.append(set(['â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ', 'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ']))
        self.groups.append(set(['i', 'l', '1', 't', 'r']))
        self.groups.append(set(['ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'd', 'đ', 'q', 'g']))
        self.groups.append(set(['b', 'p', 'd', 'đ', 'q']))
        self.groups.append(set(['h', 'n', 'm', 'w']))
        self.groups.append(set(['i', 'í', 'ì', 'ỉ', 'ĩ', 'ị', 'l', '1']))
        self.groups.append(set(['y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ']))
        self.groups.append(set(['9', 'g']))
        self.groups.append(set(['f', 't', '+']))
        self.groups.append(set(['b', 'e']))
        self.groups.append(set(['2', 'z']))


    def near(self, a, b):
        ok = False
        for group in self.groups:
            if a in group and b in group:
                ok = True
            if ok:
                break
        return ok


    def edit_distance(self, s1, s2):#levenshtein
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                elif self.near(c1, c2):
                    distances_.append(0.5 + min((distances[i1], distances[i1 + 1], distances_[-1])))
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]


    def find_similar_child(self, node, word):
        similar_nodes = []
        for child_name in node.children.keys():
            score = self.edit_distance(word, child_name)
            if score <= math.ceil(0.2*len(word)):
                similar_nodes.append(node.children[child_name])
        return similar_nodes


    def search(self, current_node, word, words):
        current_value = current_node.get_value()
        if len(words) == 0:
            return current_value, current_node.length
        next_nodes = current_node.find_child(words[0].lower())
        if len(next_nodes) == 0:
            next_nodes = self.find_similar_child(current_node, words[0].lower())
        if len(next_nodes) != 0:
            best_length = current_node.length
            best_res = ''
            for next_node in next_nodes:
                res, length = self.search(next_node, words[0], words[1:])
                if res != None:
                    res = current_value + ' ' + res
                else:
                    res = ''
                    for i in range(len(words)):
                        res += words[i] + ' '
                    res += current_value
                if length > best_length:
                    best_length = length
                    best_res = res
            return best_res, best_length
        else:
            res = current_value
            for i in range(len(words)):
                res += ' ' + words[i]
            return res, current_node.length


    def predict(self, key, index, sub_key, char_cands, charset_list):
        raw_result = []
        for w_cand in char_cands:
            word = ''
            for char_cand in w_cand:
                char = charset_list[np.argmax(char_cand)]
                if char == '<nul>':
                    break
                word += char
            raw_result.append(word)
        raw_result = ' '.join(raw_result).strip().split(' ')
        result, best_length = self.search(self.fwtree.root, '', raw_result)
        if best_length < 2:
            result = ' '.join(raw_result)
        result = result.strip()
        return key, index, sub_key, result
