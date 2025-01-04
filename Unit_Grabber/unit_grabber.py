from Levenshtein import distance as levenshtein_distance
import re


class UnitGrabber:
    MAX_LEVENSHTEIN_DIST = 4

    def __init__(self, units: dict):
        self.__units = units

    def get_unit_br(self, unit_name: str, own_br: float) -> tuple[str, float]:
        similar_names = self.__get_similar_unit_names(unit_name)
        unit_logo = self.__get_unit_logo(unit_name)

        for name in similar_names:
            name_logo = self.__get_unit_logo(name)
            if name_logo != unit_logo:
                continue
            if self.__units[name] <= own_br + 1:
                return (name, self.__units[name])
        return (None, None)

    def __get_word_distance(self, word1: str, word2: str) -> int:
        return levenshtein_distance(word1, word2)

    def __get_similar_unit_names(self, src_name: str) -> list:
        src_name = self.__remove_logo(src_name)
        similar_words = {}
        for unit_name in self.__units.keys():
            without_logo = self.__remove_logo(unit_name)

            dist = self.__get_word_distance(src_name, without_logo)
            if (dist <= UnitGrabber.MAX_LEVENSHTEIN_DIST):
                similar_words[unit_name] = dist

        similar_words_list = [key for key, val in sorted(
            similar_words.items(), key=lambda item: item[1])]

        return similar_words_list

    def __remove_logo(self, unit_name: str) -> str:
        unit_name = re.sub(r"\[.*?\]", "", unit_name)
        return unit_name

    def __get_unit_logo(self, unit_name) -> str:
        logo = ''
        logo_data = re.findall(r"\[(.*?)\]", unit_name)
        if len(logo_data) > 0:
            logo = logo_data[0]

        return logo
