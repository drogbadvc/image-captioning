import requests
import streamlit as st
from PIL import Image
from io import BytesIO


def card(title, context):
    return f"""
        <div class ="card">
            <div class ="card-body">
                <h5 class ="card-title">{title}</h5>
                {context}
            </div>      
        </div>"""


def dashboard():
    st.title('Generator Image to Description')

    col1, col2 = st.columns([1, 1])

    with col1:
        with st.form(key='image_form'):
            uploaded_file = st.file_uploader("Choose an image to download", type=['png', 'jpg', 'jpeg'])

            url = st.text_input('Or enter the URL of the image')

            tags = st.text_input('Enter tags (separated by commas) #optional')

            submit_button = st.form_submit_button(label='Analyse')

    with col2:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
        elif url != '':
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
            else:
                st.write("Unable to download the image from the specified URL.")
                image = None
        else:
            image = None

        if image is not None:
            st.image(image, caption='Downloaded image', use_column_width='auto')

    if submit_button:
        with st.spinner(''):
            if uploaded_file is not None:
                files = {"file": uploaded_file.getvalue()}
                params = {"specified_tags": tags}
            elif url != '':
                params = {'image_url': url, "specified_tags": tags}
            else:
                st.write("Please upload an image or enter an image URL.")

            response = requests.post('http://localhost:8000/img2text', params=params,
                                     files=files if 'files' in locals() else None)
            if response.status_code == 200:
                res = response.json()
                text = "<p><h5 class=\"card-title\">Tags identified :</h5> <blockquote class=\"blockquote\">" + res[
                    'Model Identified Tags'] + "</blockquote></p><p><h5 class=\"card-title\">Image caption:</h5> <blockquote class=\"blockquote\">" + \
                       res['Image Caption'] + "</div></p>"
                st.markdown(card("Result", text), unsafe_allow_html=True)

            else:
                st.write("An error occurred during the request.")
