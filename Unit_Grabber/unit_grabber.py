from Levenshtein import distance as levenshtein_distance
import re

class UnitGrabber:
    MAX_LEVENSHTEIN_DIST = 4
    def __init__(self,units : dict):
        self.__units = units

    def get_unit_br(self,unit_name : str,own_br : float) -> float:
        similar_names = self.__get_similar_unit_names(unit_name)
        unit_metadata = self.__get_unit_metadata(unit_name)

        for name in similar_names:
            name_metadata = self.__get_unit_metadata(name)
            if name_metadata != unit_metadata:
                continue
            if own_br - 1 <= self.__units[name] <= own_br + 1:
                return self.__units[name]
        return None
    
    def __get_word_distance(self,word1 : str,word2 : str) -> int:
        return levenshtein_distance(word1, word2)
    
    def __get_similar_unit_names(self, src_name : str) -> list:
        src_name = self.__remove_metadata(src_name)
        similar_words = {}
        for unit_name in self.__units.keys():
            without_metadata = self.__remove_metadata(unit_name)

            dist = self.__get_word_distance(src_name, without_metadata)
            if(dist <= UnitGrabber.MAX_LEVENSHTEIN_DIST):
                similar_words[unit_name] = dist

        similar_words_list = [key for key,val in sorted(similar_words.items(),key=lambda item : item[1])]
        #print(similar_words_list)
        return similar_words_list

    def __remove_metadata(self,unit_name : str) -> str:
        unit_name = unit_name.replace('_prem','')
        unit_name = re.sub(r"\[.*?\]", "", unit_name)
        return unit_name
    
    def __get_unit_metadata(self,unit_name) -> tuple:
        logo = ''
        logo_data = re.findall(r"\[(.*?)\]", unit_name)
        if len(logo_data) > 0:
            logo = logo_data[0]

        is_prem = True if unit_name.find('_prem') else False
        
        return (logo, is_prem)