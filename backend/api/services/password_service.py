import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from backend.api.libs.generate_passwords import generate_passwords


class PasswordService:
    used_passwords = set()

    @staticmethod
    def generate_passwords(
        count: int = 1,
        length: int = 8,
        use_uppercase: bool = False,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = False,
        decorate: bool = False,
        secret: str = "",
    ):
        """
        Generate random passwords with the specified parameters.

        :param count: Number of passwords to generate
        :param length: Length of each password
        :param use_uppercase: Include uppercase letters
        :param use_lowercase: Include lowercase letters
        :param use_digits: Include digits
        :param use_symbols: Include symbols
        :param decorate: Add decorative separators (e.g., hyphens)
        :param secret: Additional secret phrase for unique variation
        :return: List of generated passwords
        """
        passwords = []
        while len(passwords) < count:
            password = generate_passwords(
                num_passwords=1,
                length=length,
                use_uppercase=int(use_uppercase),
                use_lowercase=int(use_lowercase),
                use_digits=int(use_digits),
                use_symbols=int(use_symbols),
                secret=secret,
                decorate=decorate,
            )[0]
            if password not in PasswordService.used_passwords:
                passwords.append(password)
                PasswordService.used_passwords.add(password)
        return passwords

