"""
只是一个样样例。
"""

class ErrorCodeMap:
    def __init__(self):
        # 初始化错误码与错误信息的映射
        self.error_map = {
            201: "No Cat Face Get",
            202: "Connection Timeout",
            403: "Access Denied",
            404: "Not Found",
            500: "Internal Server Error"
        }

    def get_error_message(self, code):
        # 获取错误码对应的错误信息
        return self.error_map.get(code, "Unknown Error")

# 使用示例
error_map = ErrorCodeMap()
print(error_map.get_error_message(201))  # 输出: No Cat Face Get
print(error_map.get_error_message(404))  # 输出: Not Found
print(error_map.get_error_message(999))  # 输出: Unknown Error