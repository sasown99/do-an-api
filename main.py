from html import entities
from typing import List
from fastapi import FastAPI, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from ultil import on_success, on_fail, read_text_from_input_to_one
import flair
from flair.models import SequenceTagger
import os
import json

app = FastAPI()
model = SequenceTagger.load('./model/best-model.pt')


class Sentence(BaseModel):
    text: str


class Input(BaseModel):
    sentences: List[Sentence]
    fileName: str

class Output:
    def __init__(self, result):
        self.reuslt = result


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/ner')
def get_ner(obj_input: Input):
    # Đọc input đầu vào
    try:
        sentences = obj_input.sentences
        fileName = obj_input.fileName.split('.')[0]+'.json'
        pathFolderData = './Data'
        pathFile = os.path.join(pathFolderData,fileName)
        if not os.path.exists(pathFile):
            f = open(pathFile,'w',encoding='utf-8')
            result = []
            for sentence in sentences:
                input_sentence = flair.data.Sentence(sentence.text)
                model.predict(input_sentence)
                obj = {}
                obj['text'] = sentence.text
                entities = []
                for ner in input_sentence.get_spans('ner'):
                    entity = {}
                    entity['text'] = ner.text
                    entity['tag'] = ner.get_label("ner").value
                    entity['start_position'] = ner.start_position
                    entity['end_position'] = ner.end_position
                    entities.append(entity)
                obj['entities'] = entities
                result.append(obj)
            json.dump(result,f,ensure_ascii=False)
            f.close()
            return on_success(result)
        else:
            return on_fail(message="File đã tồn tại trong CSDL")
    except Exception as err:
        print(err)
        return on_fail()

@app.get('/getAllFiles')
def get_All_Files():
    try:
        for root, dirs, files in os.walk('./Data',topdown=False):
            files.sort()
            lst_file_name = []
            for file_name in files:
                lst_file_name.append(file_name.split('.')[0])
            zip_index_fileName = zip(range(1,len(lst_file_name)+1),lst_file_name)
            index_fileName = list(zip_index_fileName)
            result = []
            for item in index_fileName:
                obj = {}
                obj['value'] = item[0]
                obj['label'] = item[1]
                result.append(obj)
            print(result)
        return on_success(result)
    except Exception as err:
        print(err)
        return on_fail()



@app.get('/loadFile')
async def get_File(fileName: str):
    try:
        pathFolderData = './Data'
        pathFile = os.path.join(pathFolderData,fileName+'.json')
        f = open(pathFile,'r',encoding='utf-8')
        result = json.load(f)
        f.close()
        return on_success(result)
    except Exception as err:
        print(err)
        return on_fail()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
