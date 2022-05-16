import re
from time import time


def on_success(data=None, message="success"):
    if data is not None:
        return {
            "message": message,
            "result": data
        }
    return {
        "message": message,
    }


def on_fail(message="fail"):
    return {
        "message": message,
    }


def read_text_from_input_to_one(input):
    sentences = input.sentences
    return sentences
