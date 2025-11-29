# 去掉空格、统一小写
def normalize(name: str) -> str:
    return "".join(str(name).split()).lower()