import email
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, make_response, session, request
from datetime import timedelta, datetime
import random
import smtplib
from email.mime.text import MIMEText
app = Flask(__name__)
app.secret_key="JUNGL_WEEK00"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=5)

#client = MongoClient('localhost',27017)
client = MongoClient('mongodb://test:test@3.39.222.208',27017)
db = client.dbsparta
œ


def send_email(user_email, user_name):
    sendEmail = "kj0284@naver.com"
    password = "a20-11997@"
    recvEmail = user_email
    
    subject = user_name + "님 JUNGLE MENTAL가입을 환영합니다."

    smtpName = "smtp.naver.com"
    smtpPort = 587

    text = subject + "\nJUNGLE MENTAL 사이트 주소입니다.\nhttp://naverstop.shop"
    msg = MIMEText(text) 

    
    msg['Subject'] = subject
    msg['From'] = sendEmail
    msg['To'] = recvEmail
    print(msg.as_string())

    s=smtplib.SMTP(smtpName, smtpPort)
    s.starttls()
    s.login(sendEmail, password)
    s.sendmail(sendEmail, recvEmail, msg.as_string())
    s.close()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/sign_up')
def signup():
    return render_template('sign_up.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/mental_survey')
def post_pan():
    
    return render_template('mental_survey.html')
    

@app.route('/mental_result')
def result_page():
        return render_template('mental_result.html')

@app.route('/mental_before')
def result_page2():
        return render_template('mental_before.html')    

@app.route("/api/login", methods=['POST']) #로그인 기능
def member_login():
    if(request.method == "POST"):
        user_id = request.form["user_id"]
        user_pw = request.form["password"]
        print(user_id, user_pw)
        id_check = db.user_db.count_documents({"user_id":user_id})
        print(id_check)
        if(id_check == 0):
            print("존재하지 않는 id 입니다.")
            return jsonify({'result': 'fail'})
        elif(id_check == 1):
            user_info = db.user_db.find_one({"user_id":user_id})
            if(user_pw == user_info.get('password')):
                session['id'] = user_info.get('user_id')
                session['name'] = user_info.get('user_name')
                return jsonify({'result': 'success'})
            else:
                print("바말번호가 틀렸습니다!")
                return jsonify({'result': 'pwError'})

@app.route("/api/logout", methods=['GET','POST']) #로그아웃
def logout():
    session.pop('id', None)
    session.pop('name', None)
    return jsonify({'result': 'success'})

@app.route('/api/create', methods=['GET','POST']) # 회원가입 페이지
def create_user():
    # 1. 클라이언트로부터 데이터를 받기
    user_id = request.form['user_id']  # 클라이언트로부터 url을 받는 부분
    password = request.form['password']  # 클라이언트로부터 comment를 받는 부분
    user_name = request.form['user_name']
    user_email = request.form['e_mail']
    email_check = request.form['email_check']

    if(email_check == 'true'):
         send_email(user_email, user_name)
        
    user_info = {'user_id': user_id, 'password': password, 'user_name': user_name, 'e_mail':user_email}
    # 3. mongoDB에 데이터를 넣기
    id_check = db.user_db.count_documents({"user_id":user_id})
    
    if(id_check == 0):
        db.user_db.insert_one(user_info)
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'false'})

@app.route('/api/survey_commit', methods=['POST']) # 회원가입 페이지
def create_result():
    # 1. 클라이언트로부터 데이터를 받기
    user_id = request.form['user_id']  # 클라이언트로부터 url을 받는 부분
    t_point = request.form['t_point']  # 클라이언트로부터 comment를 받는 부분

    survey_result = {'user_id': user_id,'t_point': t_point, 'date': datetime.today().strftime("%m월%d일%H시%M분")}
    db.result_survey.insert_one(survey_result)
    return jsonify({'result': 'success'})
    
@app.route('/api/get', methods=['GET'])
def read_cards():
    question = []
    result = list(db.question.find({'np':'p'},{'_id': 0}))
    result1 = list(db.question.find({'np':'n'},{'_id': 0}))
    randomlist = random.sample(range(1, len(result1)), 10)
    for i in range(len(result1)):
        if(i in randomlist):
            question.append(result[i])
        if(i in randomlist):
            question.append(result1[i])
    print(len(question))
    return jsonify({'result': 'success', 'cards': question})
    #부정적인 질문을 랜덤으로 10개 출력하는 for문
@app.route('/api/post_result', methods=['POST'])
def get_survey_result():
    user_id = request.form['user_id']
    result = list(db.result_survey.find({'user_id': user_id},{'_id': 0}).sort("_id", -1).limit(7))
    return jsonify({'result': 'success', 'result_survey': result})

@app.route('/api/recent_score', methods=['POST'])
def get_score():
    user_id = request.form['user_id']
    result = list(db.result_survey.find({'user_id': user_id},{'_id': 0}).sort("_id", -1).limit(1))
    print(result)
    return jsonify({'result': 'success', 'recentscore': result})

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)