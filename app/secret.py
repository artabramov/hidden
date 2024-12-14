import random
import string

SECRET_KEY_LENGTH = 64


def generate_random_string():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(SECRET_KEY_LENGTH))


if __name__ == "__main__":
    print(generate_random_string())
