
BREED_EN_TO_CN = {
    'milk': "奶牛猫",
    'black': "黑猫",
    'white': "白猫",
    'orange': "橘猫",
    'orgwhite': "橘白猫",
    'li': "狸花猫",
    'liwhite': "狸白猫",
    'flower': "三花猫",
    'hawksbill': "玳瑁猫"
}

BREED_CN_TO_EN = { v: k for k, v in BREED_EN_TO_CN.items() }

BREED_EN_TO_IDX = {
    "unknown": 1,
    "orgwhite": 2,
    "cow": 3,
    "white": 4,
    "black": 5,
    "orange": 6,
    "li": 7,
    "liwhite": 8,
    "jianzhong": 9,  # TODO
    "flower": 10,
    "li": 11,
    'hawksbill': 12
}
