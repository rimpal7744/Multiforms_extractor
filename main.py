from fastapi import FastAPI, File, UploadFile
from paddleocr import PaddleOCR
from s26_scraper import mains26
from s30_scraper import mains30
from s33_scraper import main
import uvicorn
import numpy as np
from pdf2image import convert_from_path
import os

ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory

app = FastAPI()


@app.post("/upload-file/")
async def create_upload_file(file: UploadFile = File(...)):
    file_location = f"{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    images = convert_from_path(file_location,last_page=1)
    pix = np.array(images[0])
    result = ocr.ocr(pix, cls=True)
    result = result[0]
    for line in result:
        if ('STANDARD FORM 26' in str(line[1][0])) or ('STANDARD FORM26' in str(line[1][0])) or ('STANDARD FORM 25' in str(line[1][0])) or ('STANDARD FORM25' in str(line[1][0])):
            print('26form')
            result=mains26(file_location,result)
            break
        elif ('STANDARD FORM 30' in str(line[1][0])) or ('STANDARD FORM30' in str(line[1][0])):
            print('30form')
            result=mains30(result)
            break
        elif ('STANDARD FORM 33' in str(line[1][0])) or ('STANDARD FORM33' in str(line[1][0])):
            print('33form')
            result=main(file_location,result)
            break
        else:
            pass

    os.remove(file_location)
    return result



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)