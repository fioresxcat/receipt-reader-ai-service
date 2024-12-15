import pdb
import numpy as np
from .base_lm import Base_LM

# class Node:
#     def __init__(self, value, parent, length):
#         self.value = value
#         self.parent = parent
#         self.children = {}
#         self.length = length

#     def add_child(self, value, parent, length):
#         if value.lower() not in self.children.keys():
#             new_node = Node(value, parent, length)
#             self.children[value.lower()] = new_node
#         return self.children[value.lower()]

#     def get_value(self):
#         return self.value

#     def get_length(self):
#         return self.length

#     def find_child(self, value):
#         children = []
#         if value in self.children.keys():
#             children.append(self.children[value])
#         return children


# class FWTREE:
#     def __init__(self, dictionary_path):
#         self.product_names = []
#         with open(dictionary_path, 'r') as f:
#             for row in f:
#                 self.product_names.append(row[:-1].split(' '))
#         self.root = Node('', None, 0)

#     def load_tree(self):
#         for product_name in self.product_names:
#             current_node = self.root
#             for word in product_name:
#                 current_node = current_node.add_child(word, current_node, current_node.length + 1)


class ProductName_LM(Base_LM):
    def __init__(self, max_words):
        super(ProductName_LM, self).__init__()
        self.max_words = max_words
   

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
        result = ' '.join(raw_result)
        result = result.strip()
        if len (result) > 0 and result [0].isnumeric():
            result = result [1:]
        result = result.strip()
        return key, index, sub_key, result

