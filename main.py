import json
import requests
from typing import List, Dict
from bs4 import BeautifulSoup


class PageParser:
    def __init__(self, url: str):
        self.html_src = requests.get(url).text
        self.soup = BeautifulSoup(self.html_src, "html.parser")

    def get_name(self) -> str:
        return self.soup.find("h1", {"class": "header__title heading-1"}).text

    def get_difficulty(self) -> str:
        return self.soup.find("div", {
            "class": "icon-with-text header__skill-level body-copy-small body-copy-bold icon-with-text--aligned"}).text

    def get_durations(self) -> Dict[str, str]:
        div = self.soup.find("div",
                             {"class": "icon-with-text time-range-list cook-and-prep-time header__cook-and-prep-time"})
        time = div.find_all(lambda tag: tag.name == "span" and not tag.has_attr("class"))
        return {"prep": time[0].text, "cook": time[1].text}

    def get_serves(self) -> str:
        return self.soup.find("div", {
            "class": "icon-with-text header__servings body-copy-small body-copy-bold icon-with-text--aligned"}).text

    def get_rating(self):
        rating_block = self.soup.find("div", {"class": "rating__stars"})
        filled_stars = 0
        for star in rating_block.find_all("use"):
            if "fill" in star["xlink:href"]:
                filled_stars += 1
        votes = self.soup.find("span", {"class": "rating__count-text body-copy-small"}).text
        return {"stars": filled_stars, "votes": votes}

    def get_description(self) -> str:
        return self.soup.find("div", {"class": "editor-content"}).text

    def get_nutritions(self) -> Dict[str, str]:
        table = self.soup.find("table", {"class": "key-value-blocks hidden-print"})
        nutritions = {}
        for tbodys in table.find_all("tbody"):
            for nutrition in tbodys.find_all("tr"):
                prefix_tag = nutrition.find("td", {"class": "key-value-blocks__prefix "})
                prefix = '' if prefix_tag is None else prefix_tag.text
                key = nutrition.find("td", {"class": "key-value-blocks__key"}).text
                value = nutrition.find("td", {"class": "key-value-blocks__value"}).text
                nutritions[f"{prefix}{' ' if prefix else ''}{key}"] = value
        return nutritions

    def get_steps(self) -> List[str]:
        steps = self.soup.find("section", {"class": "recipe__method-steps"})
        return [step.div.text for step in steps.find_all("li")]

    def get_ingredients(self) -> Dict[str, list]:
        ingredient_sections = self.soup.find("section", {"class": "recipe__ingredients"})
        result = dict()
        for section in ingredient_sections.find_all("section"):
            section_name = section.h3.text if section.h3 else "For the dish"
            result[section_name] = [ingredient.text for ingredient in section.find_all("li")]
        return result

    def get_recipe_tips(self) -> Dict[str, str]:
        end_block = self.soup.find("div", {"class": "post__content-end row hidden-print"})
        result = dict()
        if end_block:
            tips_block = end_block.find("div", {"class": "editor-content"})
            if tips_block:
                for section in tips_block.find_all("section"):
                    tip_name = section.find("h6").text
                    content_text = section.text
                    tip_name_end = content_text.find(tip_name) + len(tip_name)
                    while not (content_text[tip_name_end].isalpha() or content_text[tip_name_end].isdigit()):
                        tip_name_end += 1

                    tip_content = section.text[tip_name_end:]
                    result[tip_name] = tip_content
        # Tips can have different html structure:
        #   https://www.bbcgoodfood.com/recipes/one-pan-thai-green-salmon
        #   https://www.bbcgoodfood.com/recipes/meatball-black-bean-chilli
        return result

    def get_dict(self):
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "difficulty": self.get_difficulty(),
            "durations": self.get_durations(),
            "serves": self.get_serves(),
            "rating": self.get_rating(),
            "nutritions": self.get_nutritions(),
            "ingredients": self.get_ingredients(),
            "steps": self.get_steps(),
            "tips": self.get_recipe_tips()
        }

    def get_json(self):
        return json.dumps(self.get_dict(), ensure_ascii=False, indent=4)


def main():
    parser = PageParser("https://www.bbcgoodfood.com/recipes/meatball-black-bean-chilli")
    print(parser.get_json())


if __name__ == "__main__":
    main()
