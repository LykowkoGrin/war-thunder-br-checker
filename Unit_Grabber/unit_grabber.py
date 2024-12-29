from Levenshtein import distance as levenshtein_distance

class UnitGrabber:
    MAX_LEVENSHTEIN_DIST = 8
    def __init__(self,units : dict):
        self.__units = units

    def get_unit_br(self,unit_name : str,own_br : float) -> float:
        similar_words = self.__get_similar_words(unit_name,self.__units.keys(),UnitGrabber.MAX_LEVENSHTEIN_DIST)
        for word in similar_words:
            if(own_br - 1 <= self.__units[word] <= own_br + 1):
                #print(word)
                return self.__units[word]
        return None
    
    def __get_word_distance(self,word1 : str,word2 : str) -> int:
        return levenshtein_distance(word1, word2)
    
    def __get_similar_words(self, word : str, words : list, max_distance : int) -> list:
        similar_words = {} 
        for i in words:
            dist = self.__get_word_distance(word,i)
            if(dist <= max_distance):
                similar_words[i] = dist

        similar_words_list = [key for key,val in sorted(similar_words.items(),key=lambda item : item[1])]
        return similar_words_list

