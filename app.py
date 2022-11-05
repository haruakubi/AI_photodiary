# app.py　として格納

# 必要なライブラリのインポート
import pprint
import requests
import json
import MeCab
import os
import requests
import pprint
import subprocess # pythonプログラム上でコマンドラインを実行するモジュール
import streamlit as st


# streamlitのシークレット情報を変数に格納
## GCPのサービスアカウント鍵情報
type2 = st.secrets["type2"]
project_id = st.secrets["project_id"]
private_key_id = st.secrets["private_key_id"]
private_key = st.secrets["private_key"]
client_email = st.secrets["client_email"]
client_id = st.secrets["client_id"]
auth_uri = st.secrets["auth_uri"]
token_uri = st.secrets["token_uri"]
auth_provider_x509_cert_url = st.secrets["auth_provider_x509_cert_url"]
client_x509_cert_url = st.secrets["client_x509_cert_url"]

## jsonに再変換
service_account_key = {
  "type": type2,
  "project_id": project_id,
  "private_key_id": private_key_id,
  "private_key": private_key,
  "client_email": client_email,
  "client_id": client_id,
  "auth_uri": auth_uri,
  "token_uri": token_uri,
  "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
  "client_x509_cert_url": client_x509_cert_url
}


## Natural Language AIのAPIキー。確認方法はこちら）
### https://cloud.google.com/docs/authentication/api-keys?hl=ja
key = st.secrets["key"]

## WEBページへのログインPW
password = st.secrets["password"]

## vertexAI＞エンドポイント＞APIの例　からENDPOINT_IDをコピペ
ENDPOINT_ID = st.secrets["ENDPOINT_ID"]

## vertexAI＞エンドポイント＞APIの例　からPROJECT_IDをコピペ
#PROJECT_ID = st.secrets["PROJECT_ID"]




# ↑の情報をkey.jsonとしてファイルで保存
with open("./key.json", "w") as f:
    json.dump(service_account_key, f, indent=2, ensure_ascii=False)

# 鍵情報を使ってGCPに認証
command = "gcloud auth activate-service-account  --key-file='./key.json'"
ret = subprocess.run(command, shell=True)


# vertwxAIにアクセスするためのトークンを発行
command2 = "gcloud auth print-access-token"
token2 = subprocess.getoutput(command2)

# GCPのNatural Language AI を使用するための変数定義
## APIのアクセス先（エンドポイント）
senurl = 'https://language.googleapis.com/v1beta2/documents:analyzeSentiment'
## header情報
header = {'Content-type': 'application/json'}






##　関数定義
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == password :
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


##　先ほど定義したcheck_password()関数を使う。if文の最初は==TrueとわざわざやらなくてOK
if check_password():
    st.title('写メ日記判定AI') #タイトルの作成
    st.caption('写メ日記の文章をあげるだけで、優良嬢かどうかをAIが判定します') #サブタイトルの作成
    with st.form(key='submit_form'): #フォームの箱を作成
      diary = st.text_input('写メ日記') #写メ日記というタイトルの入力フォームの作成
      submit_btn = st.form_submit_button('判定') #入力フォームのテキストを送信するボタンを作成
      if submit_btn:
        diary_str = str(diary)  # 入力した文章をstr型として変数格納。str型にしてあげないと、mecab食べられない
        diary_w = MeCab.Tagger("-Owakati").parse(diary_str) #mecabにより単語に分けて、かつ空白でワカチをしてあげる。こうしないとAIが食べられない

      ### APIで感情情報取得
        senbody = {
          "document":{
              "type": "PLAIN_TEXT",
              "language": "JA",
              "content": diary_w #先ほどの入力したテキストがここに格納される
          }
        }

      ### 取得した感情情報を変数に格納 
        senres = requests.post(senurl, headers=header, json=senbody, params={'key': key}) # RESTAPIによってNatural Language AIにPOASTする。
        senresults = senres.json() #結果をjsonで格納

      ### たまに Natural Language AIから返ってきた値がエラーになることが。その際のエラーハンドリング。エラーになったら強制的に0を返すプログラム
        status = senresults.get('status')
        try:
          documentmagnitude = senresults['documentSentiment']['magnitude']
          documentscore = senresults['documentSentiment']['score']
        except KeyError:
          print(items[0])
          print('KeyError')
          documentmagnitude = 0
          documentscore = 0

      ## vertexAI用の変数定義
      ### vertexAIにて定義した、特徴量全てをjsonで投げる。つまり、ターゲット列以外全て投げる必要あり
        input = {
          "instances": [
            {"diary":diary_w, "documentmagnitude":documentmagnitude, "documentscore":documentscore},
          ]
        }
        #一時的
        st.text(token2)
        st.text(ret)
