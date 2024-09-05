"""
整合 Log 相关的输出函数。
"""


def show_config(**kwargs):
    """ 解析 key: value 形式的设定，逐个输出。 """
    print('Configurations:')
    print('-' * 70)
    print('|%25s | %40s|' % ('keys', 'values'))
    print('-' * 70)
    for key, value in kwargs.items():
        print('|%25s | %40s|' % (str(key), str(value)))
    print('-' * 70)
