BREED_EN_TO_CN = {
    'milk': "奶牛猫",
    'black': "黑猫",
    'white': "白猫",
    'orange': "橘猫",
    'orgwhite': "橘白猫",
    'li': "狸花猫",
    'liwhite': "狸白猫",
    'flower': "三花猫",
    'tortoiseshell': "玳瑁猫",

    # TODO 之后优化 face_breed 模型再说。
    'jianzhou': "简州猫",
    'color': "彩狸猫"
}

BREED_CN_TO_EN = {v: k for k, v in BREED_EN_TO_CN.items()}

BREED_EN_TO_IDX = ["unknown", "orgwhite", "milk", "white", "black", "orange", "li", "liwhite", "flower",
                   "tortoiseshell", "jianzhou", "color", ]
