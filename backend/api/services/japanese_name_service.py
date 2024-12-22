import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from backend.api.libs.japanese_name_generator import JapaneseNameGenerator

class JapaneseNameService:
    @staticmethod
    def generate_names(num_names: int = 1, sex: str = "male", firstname_rarity: str = "very_rare", lastname_rarity: str = "very_rare"):
        generator = JapaneseNameGenerator(
            num_names=num_names,
            sex=sex,
            firstname_rarity=firstname_rarity,
            lastname_rarity=lastname_rarity
        )
        return generator.generate_names()
