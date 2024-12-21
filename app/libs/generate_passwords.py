import random
import string

def generate_password(
    length,
    character_pool,
    secret="",
    decorate=False,
    separator="-"
):
    """
    Core function to generate a single password.

    :param length: Length of the password
    :param character_pool: Allowed characters for the password
    :param secret: Additional secret for unique variation
    :param decorate: Whether to add separators in the password
    :param separator: Character to use for decoration
    :return: Generated password
    """
    random.seed(secret + str(random.random()))  # Add unique variation
    password = "".join(random.choices(character_pool, k=length))

    if decorate:
        password = separator.join(
            [password[i:i + 4] for i in range(0, len(password), 4)]
        )

    return password


def generate_passwords(
    num_passwords=1,
    length=8,
    use_uppercase=True,
    use_lowercase=True,
    use_digits=True,
    use_symbols=True,
    secret="",
    decorate=False,
    separator="-"
):
    """
    Generate random passwords based on the given criteria.

    :param num_passwords: Number of passwords to generate
    :param length: Length of each password
    :param use_uppercase: Include uppercase letters
    :param use_lowercase: Include lowercase letters
    :param use_digits: Include digits
    :param use_symbols: Include symbols
    :param secret: Additional secret for unique variation
    :param decorate: Whether to add separators in the password
    :param separator: Character to use for decoration
    :return: List of generated passwords
    """
    if length < 4:
        raise ValueError("Password length must be at least 4 characters.")

    character_pool = ""
    if use_uppercase:
        character_pool += string.ascii_uppercase
    if use_lowercase:
        character_pool += string.ascii_lowercase
    if use_digits:
        character_pool += string.digits
    if use_symbols:
        character_pool += string.punctuation

    if not character_pool:
        raise ValueError("At least one character type must be enabled.")

    return [
        generate_password(
            length=length,
            character_pool=character_pool,
            secret=f"{secret}{i}",
            decorate=decorate,
            separator=separator
        )
        for i in range(num_passwords)
    ]


