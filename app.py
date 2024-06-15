from dotenv import load_dotenv
load_dotenv() ## load all the environemnt variables

import streamlit as st
import os
import google.generativeai as genai
import PIL.Image
from IPython.display import display, Image
from io import StringIO
import pandas as pd
import csv
import shutil
import gdown

## Configure our API key
genai.configure(api_key= os.getenv('GOOGLE_API_KEY'))

## Function to load Google Gemini model and provide SQL query as response
def get_gemini_response(prompt, img):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([prompt, img])
    return response.text

## Define your prompt
prompt = """
    According to the picture, answer these questions in a short answer, to-the-point, without adding words or sentences.
    \n1. What is the km odometer?
    \n2. What is the date time?
    Put all of the answers in an array format like this: [..., ...]
    """
## Streamlit App
st.set_page_config(page_title="Odometer Km and Datetime Extractor")
st.header("Gemini App To Extract Odometer Km and Datetime from Image")


## ALT 1: UPLOADING IMG FILE ONE-BY-ONE
# uploaded_file = st.file_uploader("Choose an image file")
# if uploaded_file is not None:
#     img = PIL.Image.open(uploaded_file)
#     st.image(img, caption='Input', use_column_width=True)

## ALT 2: MENTIONING IMG FOLDER PATH
# imgfolder_path = st.text_input("Your image folder name: ", key="input")
# imgfolder_full_path = os.path.join(os.getcwd(),imgfolder_path)

## ALT 3: PROVIDE LIST OF GDRIVE IMAGE URLs
input_imgurls = st.text_area("List of GDrive Image URLs (separated by line break, max. 50 images): ", key="input")

submit = st.button("Submit")

## If submit is clicked
if submit:
    with st.spinner('Wait for it...'):

        imgurls_list = input_imgurls.split('\n')
        file_ids = [ url.split('/')[-2] for url in imgurls_list]
        prefix = 'https://drive.google.com/uc?export=download&id='
        dlpath = 'download'
        if os.path.exists(dlpath):
            shutil.rmtree(dlpath)
        os.mkdir(dlpath)
        os.chdir(dlpath)
        [gdown.download(prefix + file_id) for file_id in file_ids]
        os.chdir('../')

        imgfolder_full_path = os.path.join(os.getcwd(),'download')
        imgfile_list = os.listdir(imgfolder_full_path)
        counter = 1
        filenumber_list = []
        odo_km_list = []
        datetime_list = []

        for imgfile in imgfile_list:
            img = PIL.Image.open(os.path.join(imgfolder_full_path, imgfile))
            response = get_gemini_response(prompt, img)

            mapping_replace_spechar = str.maketrans({'[': '', ']': ''})
            response = response.translate(mapping_replace_spechar)
            resp_arr = [x.strip() for x in response.split(',')]

            filenumber_list.extend([counter])
            odo_km_list.extend([resp_arr[0]])
            datetime_list.extend([resp_arr[1]])

            print(counter, imgfile, resp_arr[0], resp_arr[1])

            counter+=1

        
    # Create Dataframe & Output to CSV
    dict = {'No.': filenumber_list, 'Image Filename': imgfile_list, 'Odometer Km': odo_km_list, 'Date Time': datetime_list}
    df = pd.DataFrame(dict)
    output = df.to_csv(index=False)

    st.download_button(label= 'Download CSV', data= output, file_name= 'output.csv', mime= 'text/csv')



