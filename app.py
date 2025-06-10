from flask import Flask, render_template, request, make_response
import spacy
import csv
import io
import json
import requests
import os,uuid
app = Flask(__name__)
table = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    table.clear()
    for file in request.files.getlist('resume'):
        filename = str(uuid.uuid4()) + '.pdf'
        file_path = os.path.join('uploads', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create directory if it doesn't exist
        file.save(file_path)

        files = {"file": open(file_path, "rb")}
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjM1ZGYxZGYtMzc4Ny00NDY3LWFlNWEtYzFjYjJkODU0MWU5IiwidHlwZSI6ImFwaV90b2tlbiJ9.cDnAxB_SI-aLqpm6HqHKBHmzq5BJ91yqpzuhVOzs6fo"
        }

        url = "https://api.edenai.run/v2/ocr/resume_parser"
        data = {"providers": "hireability"}

        response = requests.post(url, data=data, files=files, headers=headers)
        result = json.loads(response.text)
        print(json.dumps(result, indent=4))

        extracteddata = data_extraction(result)

    data_into_csv(table)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "name",
            "phones",
            "mail",
            "college",
            "description",
            "gpa",
            "work_Experience",
            "skills",
            "links"
        ]
    )

    # write each row of data
    for row in extracteddata:
        writer.writerow(row)
    output.seek(0)
    return output_csv(output, "resume_data.csv")


def save_data(data):
    with open("resume_data.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "name",
                "phones",
                "mail",
                "college",
                "description",
                "gpa",
                "work_Experience",
                "skills",
            ]
        )
        writer.writerows(data)


def data_extraction(result):
    try:
        n = result['hireability']['extracted_data']['personal_infos']['name']['raw_name']
    except:
        n= None
    try:
        p = result['hireability']['extracted_data']['personal_infos']['phones']
    except:
        p= None
    try:
        m = result['hireability']['extracted_data']['personal_infos']['mails']
    except:
        m= None
    try:
        l = result['hireability']['extracted_data']['personal_infos']['urls']
    except:
        l= None
    try:

        e = result['hireability']['extracted_data']['education']['entries'][0]['establishment']
    except:
        e= None
    try:
        d = result['hireability']['extracted_data']['education']['entries'][0]['description']
    except:
        d= None
    try:
        g = result['hireability']['extracted_data']['education']['entries'][0]['gpa']
    except:
        g= None
    try:
        w = result['hireability']['extracted_data']['work_experience']['total_years_experience']
    except:
        w= None
    try:
        data = result['hireability']['extracted_data']
        skills_list = []
        for skill in data['skills']:
            skills_list.append(skill['name'])
        s = skills_list
    except:
        s= None
    
    rows = []
    rows.append(n)
    rows.append(p)
    rows.append(m)
    rows.append(e)
    rows.append(d)
    rows.append(g)
    rows.append(w)
    rows.append(s)
    rows.append(l)

    table.append(rows)
    return table


def data_into_csv(data):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "name",
            "phones",
            "mail",
            "college",
            "description",
            "gpa",
            "work_Experience",
            "skills",
            "links",
        ]
    )

    # write each row of data
    for row in data:
        writer.writerow(row)


from flask import make_response


def output_csv(output, filename):
    csv_output = output.getvalue().encode("utf-8")
    response = make_response(csv_output)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv"
    return response

def email_phone(text):
    import re

    phone_regex = re.compile(r"\+\d{2}\s?\d{3}\s?\d{3}\s?\d{3}|\+\d{2}\s?\d{5}\s?\d{5}")
    matches = phone_regex.findall(text)
    phone_numbers = []
    for match in matches:
        phone_numbers.append(match.replace(" ", ""))

    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    email_matches = re.findall(email_regex, text)
    email = email_matches[0] if email_matches else None

    print(email, phone_numbers)

if __name__ == "__main__":
    app.run(debug=True)