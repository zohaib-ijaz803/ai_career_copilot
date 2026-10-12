from flask import Flask, render_template, request, redirect, session
from db import Base, engine, sessionlocal
from ai import analyze_resume
import models
import PyPDF2
import docx
import json

app = Flask(__name__)
app.secret_key = "secret123"


# create tables
Base.metadata.create_all(bind=engine)


# home
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# signup
@app.route("/signup", methods=["GET", "POST"])
def signup():

    dp = sessionlocal()

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = dp.query(models.User).filter_by(email=email).first()

        if existing_user:
            return "User already exists."

        user = models.User(
            email=email,
            password=password
        )

        dp.add(user)
        dp.commit()

        return redirect("/login")

    return render_template("signup.html")



# login
@app.route("/login", methods=["GET", "POST"])
def login():

    dp = sessionlocal()

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = dp.query(models.User).filter_by(
            email=email,
            password=password
        ).first()


        if user:
            session["user"] = user.email
            return redirect("/dashboard")

        else:
            return "Invalid credentials."


    return render_template("login.html")



# dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect("/login")


    result = None
    resume_text = ""


    if request.method == "POST":

        user_goal = request.form.get("role")
        file = request.files.get("resume")


        # file handling

        if file and file.filename != "":


            if file.filename.endswith(".pdf"):

                try:

                    pdf_reader = PyPDF2.PdfReader(file)

                    for page in pdf_reader.pages:
                        resume_text += page.extract_text() or ""


                except Exception as e:

                    result = {
                        "error": f"PDF error: {str(e)}"
                    }



            elif file.filename.endswith(".docx"):

                try:

                    doc = docx.Document(file)

                    for para in doc.paragraphs:
                        resume_text += para.text + "\n"


                except Exception as e:

                    result = {
                        "error": f"DOCX error: {str(e)}"
                    }


            else:

                result = {
                    "error": "Only PDF and DOCX files allowed"
                }



        # AI analysis

        if resume_text and user_goal:

            try:

                result = analyze_resume(
                    resume_text,
                    user_goal
                )


                # save report

                dp = sessionlocal()

                user = dp.query(models.User).filter_by(
                    email=session["user"]
                ).first()


                report = models.Reports(
                    user_id=user.id,
                    resume_text=resume_text,
                    result=json.dumps(result)
                )


                dp.add(report)
                dp.commit()



            except Exception as e:

                result = {
                    "error": f"AI analysis error: {str(e)}"
                }



    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )





# history
@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")


    dp = sessionlocal()


    user = dp.query(models.User).filter_by(
        email=session["user"]
    ).first()


    reports = dp.query(models.Reports).filter_by(
        user_id=user.id
    ).all()



    parsed_reports = []


    for r in reports:

        try:

            parsed_result = json.loads(r.result)

        except:

            parsed_result = []


        parsed_reports.append({

            "resume_text": r.resume_text,

            "result": parsed_result

        })


    return render_template(
        "history.html",
        user=session["user"],
        reports=parsed_reports
    )





# logout
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")




if __name__ == "__main__":

    app.run(debug=True)