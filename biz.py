
import easyocr
import numpy as np
from PIL import Image
import re
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import io
import mysql.connector

def image_to_text(path):
    input_img = Image.open(path)
    image_arr = np.array(input_img)
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_arr, detail=0)
    return text, input_img

def extracted_text(texts):
    extracted_dict = {"name": [],
                      "designation": [],
                      "company_name": [],
                      "contact_details": [],
                      "email": [],
                      "website": [],
                      "address": [],
                      "pincode": []}

    extracted_dict["name"].append(texts[0])
    extracted_dict["designation"].append(texts[1])

    for i in range(2, len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-", "").isdigit() and "-" in texts[i]):
            extracted_dict["contact_details"].append(texts[i])
        elif "@" in texts[i] and ".com" in texts[i]:
            extracted_dict["email"].append(texts[i])
        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i] or ".com" in texts[i]:
            small = texts[i].lower()
            extracted_dict["website"].append(small)
        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
            extracted_dict["pincode"].append(texts[i])
        elif re.match(r'^[A-Za-z]', texts[i]):
            extracted_dict["company_name"].append(texts[i])
        else:
            remove_colon = re.sub(r'[,;]', '', texts[i])
            extracted_dict["address"].append(remove_colon)

    for key, value in extracted_dict.items():
        if len(value) > 0:
            concadenate = " ".join(value)
            extracted_dict[key] = [concadenate]
        else:
            value = "NA"
            extracted_dict[key] = [value]

    return extracted_dict

# Streamlit part:
st.set_page_config(layout="wide")
st.title("BizCard")

with st.sidebar:
    select = option_menu("Main Menu", ['HOME', 'UPLOAD & MODIFY', 'DELETE'])

if select == "HOME":
    st.markdown("## :green[**Technologies Used :**] Python, easy OCR, Streamlit, SQL, Pandas")
    st.markdown("## :green[**Overview :**] In this Streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")

elif select == "UPLOAD & MODIFY":
    img = st.file_uploader("UPLOAD AN IMAGE", type=["png", "jpg", "jpeg"])

    if img is not None:
        st.image(img, width=300)
        text_image, input_img = image_to_text(img)
        text_dict = extracted_text(text_image)

        if text_dict:
            st.success("Text extracted successfully")

        df = pd.DataFrame(text_dict)
        st.dataframe(df)

        button_1 = st.button("Save")

        if button_1:
            # Connect to MySQL
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Sagar72427',
                port=3306,
                database='bizcard',
                auth_plugin='mysql_native_password')

            cursor = mydb.cursor()

            # Table creation with unique constraint
            create_query = '''CREATE TABLE IF NOT EXISTS bizcard (
                                name VARCHAR(225),
                                designation VARCHAR(225),
                                company_name VARCHAR(225),
                                contact_details VARCHAR(225),
                                email VARCHAR(225),
                                website VARCHAR(225),
                                address VARCHAR(225),
                                pincode VARCHAR(225)
                               
                              )'''
            cursor.execute(create_query)
            mydb.commit()

            # Check for duplicates
            check_query = '''SELECT * FROM bizcard WHERE name=%s AND designation=%s AND company_name=%s'''
            values_to_check = (df['name'][0], df['designation'][0], df['company_name'][0])
            cursor.execute(check_query, values_to_check)
            result = cursor.fetchone()

            if result:
                st.warning("Record already present in the database")
            else:
                # Insert query
                insert_query = '''INSERT INTO bizcard (name, designation, company_name, contact_details, email, website, address, pincode)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
                values = (df['name'][0],
                          df['designation'][0],
                          df['company_name'][0],
                          df['contact_details'][0],
                          df['email'][0],
                          df['website'][0],
                          df['address'][0],
                          df['pincode'][0])
                cursor.execute(insert_query, values)
                mydb.commit()

                st.success("Successfully saved")

    method = st.radio('Select the method', ["preview", "modify"])



    if method == "preview":
        # Connect to MySQL
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Sagar72427',
            port=3306,
            database='bizcard',
            auth_plugin='mysql_native_password')
        cursor = mydb.cursor()

        select_query = '''SELECT * FROM bizcard'''
        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()
        table_df = pd.DataFrame(table, columns=['name', 'designation', 'company_name', 'contact_details', 'email', 'website', 'address', 'pincode'])
        st.dataframe(table_df)

    elif method == "modify":
        # Connect to MySQL
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Sagar72427',
            port=3306,
            database='bizcard',
            auth_plugin='mysql_native_password')
        cursor = mydb.cursor()

        select_query = '''SELECT * FROM bizcard'''
        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()
        table_df = pd.DataFrame(table, columns=['name', 'designation', 'company_name', 'contact_details', 'email', 'website', 'address', 'pincode'])

        col1, col2 = st.columns(2)
        with col1:
            selected_name = st.selectbox("Select the name", table_df['name'])
        with col2:
            selected_mail = st.selectbox("Select the email", table_df['email'])
            
        df_3 = table_df[table_df['name'] == selected_name]
        df_4 = df_3.copy()

        col1, col2 = st.columns(2)
        with col1:
            mo_name = st.text_input("Name", df_3["name"].unique()[0])
            mo_desi = st.text_input("Designation", df_3["designation"].unique()[0])
            mo_com_name = st.text_input("Company Name", df_3["company_name"].unique()[0])
            mo_contact = st.text_input("Contact Details", df_3["contact_details"].unique()[0])
            mo_email = st.text_input("Email", df_3["email"].unique()[0])

            df_4["name"] = mo_name
            df_4["designation"] = mo_desi
            df_4["company_name"] = mo_com_name
            df_4["contact_details"] = mo_contact
            df_4["email"] = mo_email

        with col2:
            mo_website = st.text_input("Website", df_3["website"].unique()[0])
            mo_addre = st.text_input("Address", df_3["address"].unique()[0])
            mo_pincode = st.text_input("Pincode", df_3["pincode"].unique()[0])

            df_4["website"] = mo_website
            df_4["address"] = mo_addre
            df_4["pincode"] = mo_pincode

        st.dataframe(df_4)

        col1, col2 = st.columns(2)

        with col1:
            button_2 = st.button("Modify")

        if button_2:
            # Connect to MySQL
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Sagar72427',
                port=3306,
                database='bizcard',
                auth_plugin='mysql_native_password')
            cursor = mydb.cursor()

            cursor.execute(f"DELETE FROM bizcard WHERE name = '{selected_name}'")
            mydb.commit()

            # Insert query
            for index, row in df_4.iterrows():
                insert_query = '''INSERT INTO bizcard (name, designation, company_name, contact_details, email, website

, address, pincode)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
                values = (row['name'],
                          row['designation'],
                          row['company_name'],
                          row['contact_details'],
                          row['email'],
                          row['website'],
                          row['address'],
                          row['pincode'])
                cursor.execute(insert_query, values)
                mydb.commit()

                st.success("Modification saved")

elif select == "DELETE":
    # Connect to MySQL
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Sagar72427',
        port=3306,
        database='bizcard',
        auth_plugin='mysql_native_password')
    cursor = mydb.cursor()

    col1, col2 = st.columns(2)
    with col1:
        select_query = "SELECT name FROM bizcard"
        cursor.execute(select_query)
        table1 = cursor.fetchall()
        mydb.commit()

        names = [i[0] for i in table1]
        name_select = st.selectbox("Select the name", names)

    with col2:
        select_query = f"SELECT designation FROM bizcard WHERE name ='{name_select}'"
        cursor.execute(select_query)
        table2 = cursor.fetchall()
        mydb.commit()

        designations = [j[0] for j in table2]
        designation_select = st.selectbox("Select the designation", options=designations)

    if name_select and designation_select:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"Selected Name : {name_select}")
            st.write("")
            st.write("")
            st.write("")
            st.write(f"Selected Designation : {designation_select}")

        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")

        remove = st.button("Delete", use_container_width=True)

        if remove:
            cursor.execute(f"DELETE FROM bizcard WHERE name ='{name_select}' AND designation = '{designation_select}'")
            mydb.commit()

            st.warning("Deleted")
