
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
    text = reader.readtext(image_arr, detail= 0)
    return text, input_img


def extracted_text(texts):

    extracted_dict = {"name":[],
                      "designation":[],
                      "company_name":[],
                      "contact_details":[],
                      "email":[],
                      "website":[],
                      "address":[],
                      "pincode":[]}
    
    extracted_dict["name"].append(texts[0])
    extracted_dict["designation"].append(texts[1])

    for i in range(2, len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-", "").isdigit() and "-" in texts[i]):

            extracted_dict["contact_details"].append(texts[i])

        elif "@" in texts[i] and ".com" in texts[i]:
            extracted_dict["email"].append(texts[i])

        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i] :
            small = texts[i].lower()
            extracted_dict["website"].append(small)

        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
            extracted_dict["pincode"].append(texts[i])

        elif re.match(r'^[A-Za-z]', texts[i]):
            extracted_dict["company_name"].append(texts[i])

        else:
            remove_colon= re.sub(r'[,;]','',texts[i])
            extracted_dict["address"].append(remove_colon)


    for key,value in extracted_dict.items():
        if len(value)>0:
            concadenate= " ".join(value)
            extracted_dict[key] = [concadenate]

        else:
            value = "NA"
            extracted_dict[key] = [value]

    return extracted_dict


#streamlit part:
st.set_page_config(layout = "wide")
st.title("BizCard")

with st.sidebar:
    select = option_menu("Main Menu", ['HOME', 'UPLOAD & MODIFY', 'DELETE'])

if select == "HOME":
    if select == "HOME":
        st.markdown("## :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        st.markdown("## :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")



elif select == "UPLOAD & MODIFY":
    img = st.file_uploader("UPLOAD A IMAGE", type= ["png", "jpg", "jpeg"])

    if img is not None:
        st.image(img, width= 300)

        text_image, input_img = image_to_text(img)

        text_dict = extracted_text(text_image)

        if text_dict:
            st.success("Text is extracted successfullt")

        df = pd.DataFrame(text_dict)
        st.dataframe(df)

        button_1 = st.button("save")

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


            # table_creation

            create_query = '''create table if not exists bizcard(
                            name varchar (225),
                            designation varchar (225),
                            company_name varchar (225),
                            contact_details varchar (225),
                            email varchar (225),
                            website varchar (225),
                            address varchar (225),
                            pincode varchar (225)
                            )'''
            cursor.execute(create_query)
            mydb.commit()


            # insert_query
            for index, row in df.iterrows():
                insert_query = '''insert into bizcard(name, designation, company_name, contact_details, email, website, address, pincode)
                                                    values (%s,%s,%s,%s,%s,%s,%s,%s)'''

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

                st.success("Successfully Saved")

    

    method = st.radio('select the method', ["none", "preview", "modify"])

    if method == 'none':
        st.write("")

    elif method == "preview":

        # Connect to MySQL
        mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Sagar72427',
        port=3306,
        database='bizcard',
        auth_plugin='mysql_native_password')
        cursor = mydb.cursor()

        select_query = '''select * from bizcard'''
        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()
        table_df = pd.DataFrame(table, columns= ['name', 'designation', 'company_name', 'contact_details', 'email', 'website', 'address', 'pincode'])
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

        select_query = '''select * from bizcard'''
        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()
        table_df = pd.DataFrame(table, columns= ['name', 'designation', 'company_name', 'contact_details', 'email', 'website', 'address', 'pincode'])

        col1, col2 = st.columns(2)
        with col1:
            selected_name = st.selectbox("select the name", table_df['name'])
            
        df_3 = table_df[table_df['name'] == selected_name]
        df_4 = df_3.copy()
        

        col1, col2 = st.columns(2)
        with col1:
            mo_name = st.text_input("name", df_3["name"].unique()[0])
            mo_desi = st.text_input("designation", df_3["designation"].unique()[0])
            mo_com_name = st.text_input("company_name", df_3["company_name"].unique()[0])
            mo_contact = st.text_input("contact_details", df_3["contact_details"].unique()[0])
            mo_email = st.text_input("email", df_3["email"].unique()[0])

            df_4["name"] = mo_name
            df_4["designation"] = mo_desi
            df_4["company_name"] = mo_com_name
            df_4["contact_details"] = mo_contact
            df_4["email"] = mo_email

        with col2:
            mo_website = st.text_input("website", df_3["website"].unique()[0])
            mo_addre = st.text_input("address", df_3["address"].unique()[0])
            mo_pincode = st.text_input("pincode", df_3["pincode"].unique()[0])


            df_4["website"] = mo_website
            df_4["address"] = mo_addre
            df_4["pincode"] = mo_pincode

        st.dataframe(df_4)

        col1, col2 = st.columns(2)

        with col1:
            button_2 = st.button("modify")
        
        if button_2 :
            # Connect to MySQL
            mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Sagar72427',
            port=3306,
            database='bizcard',
            auth_plugin='mysql_native_password')
            cursor = mydb.cursor()

            cursor.execute(f"delete from bizcard where name = '{selected_name}'")
            mydb.commit()


            # insert_query
            for index, row in df_4.iterrows():
                insert_query = '''insert into bizcard(name, designation, company_name, contact_details, email, website, address, pincode)
                                                    values (%s,%s,%s,%s,%s,%s,%s,%s)'''

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

                st.success("modified Saved")




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

    col1,col2 = st.columns(2)
    with col1:

        select_query = "select name from bizcard"

        cursor.execute(select_query)
        table1 = cursor.fetchall()
        mydb.commit()

        names = []

        for i in table1:
            names.append(i[0])

        name_select = st.selectbox("Select the name", names)

    with col2:

        select_query = f"select designation from bizcard where name ='{name_select}'"

        cursor.execute(select_query)
        table2 = cursor.fetchall()
        mydb.commit()

        designations = []

        for j in table2:
            designations.append(j[0])

        designation_select = st.selectbox("Select the designation", options = designations)

    if name_select and designation_select:
        col1,col2,col3 = st.columns(3)

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

        remove = st.button("Delete", use_container_width= True)

        if remove:

            cursor.execute(f"delete from bizcard where name ='{name_select}' and designation = '{designation_select}'")
            mydb.commit()

            st.warning("DELETED")


    