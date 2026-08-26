import bcrypt

class HashUtils:
    @staticmethod
    def generate_pwd(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def check_pwd(pwd: str, hash: str) -> bool:
        return bcrypt.checkpw(
            pwd.encode(),
            hash.encode()
        )

