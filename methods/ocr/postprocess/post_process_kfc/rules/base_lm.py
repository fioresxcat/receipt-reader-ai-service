import heapq
import math
import pdb

class Base_LM:
    def __init__(self):
        pass 

    
    def get_word_cands_num(self, cands, charset_list, max_word=100, max_char=100, k=10, charset='0123456789', max_char_cand=20):
        word_cands = []
        for w_cand in cands[:max_word]:
            best_cands = [(0, '')]
            for raw_char_cands in w_cand[:max_char]:
                char_cands = zip(charset_list, raw_char_cands)
                char_cands = sorted(char_cands, key=lambda x: -x[1])
                new_best_cans = []
                for i in range(len(char_cands[:max_char_cand])):
                    if char_cands[i][0] not in charset and char_cands[i][0] != '<nul>':
                        continue
                    for j in range(len(best_cands)):
                        prob = best_cands[j][0] + math.log(char_cands[i][1] + 1e-30)
                        if len(new_best_cans)<k:
                            heapq.heappush(new_best_cans, (prob, best_cands[j][1] + char_cands[i][0]))
                        else:
                            heapq.heappushpop(new_best_cans, (prob, best_cands[j][1] + char_cands[i][0]))
                best_cands = new_best_cans
            best_cands = heapq.nlargest(k, best_cands)
            word_cand = []
            for prob, list_char in best_cands:
                word = list_char.replace('<nul>', '')
                word_cand.append((word, prob))
            word_cands.append(word_cand)
        return word_cands

    def get_word_cands(self, cands, charset_list, max_word=100, max_char=100, k=10, max_char_cand=5):
        word_cands = []
        for w_cand in cands[:max_word]:
            best_cands = [(0, '')]
            for raw_char_cands in w_cand[:max_char]:
                char_cands = zip(charset_list, raw_char_cands)
                char_cands = sorted(char_cands, key=lambda x: -x[1])
                new_best_cans = []
                for i in range(len(char_cands[:max_char_cand])):
                    for j in range(len(best_cands)):
                        prob = best_cands[j][0] + math.log(char_cands[i][1] + 1e-30)
                        if len(new_best_cans)<k:
                            heapq.heappush(new_best_cans, (prob, best_cands[j][1] + char_cands[i][0]))
                        else:
                            heapq.heappushpop(new_best_cans, (prob, best_cands[j][1] + char_cands[i][0]))
                best_cands = new_best_cans
            best_cands = heapq.nlargest(k, best_cands)
            word_cand = []
            for prob, list_char in best_cands:
                word = list_char.replace('<nul>', '')
                word_cand.append((word, prob))
            word_cands.append(word_cand)
        return word_cands