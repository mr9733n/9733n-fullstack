from app.libs.japanese_name_generator import JapaneseNameGenerator

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
