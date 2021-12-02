import datetime
import unittest
from base64 import b64encode
from unittest import  TestCase
from unittest.mock import patch

import json

import sqlalchemy
from flask_bcrypt import generate_password_hash

from all_func.app import app
from all_func.dbmodel import engine, Base, Session, User, Moderator, Article, State, UpdatedArticle
import  all_func.moderator
import  all_func.user

@patch("all_func.dbmodel.Session")
class TestAuth(TestCase):
    tester = app.test_client()
    creds = b64encode(b"user:1234567").decode("utf-8")
    moder_creds = b64encode(b"moder:somepassword").decode("utf-8")

    def setUp(self):
        self.data = {
            "username": "userok",
            "firstname": "GreatUser",
            "lastname": "Underwood",
            "email": "pres@gmail.com",
            "password": "741852369"
        }
        self.data_moder = {
            "moderator_id": 5,
            "moderatorname": "another",
            "firstname": "Dmytro",
            "lastname": "Gordon",
            "email": "gordon@email.com",
            "password": "suprsecretpass",
            "moderatorkey": "789456123"
        }
        self.user = {
            "username": "user",
            "firstname": "Francic",
            "lastname": "Underwood",
            "email": "user@email.com",
            "password": "1234567"
        }
        self.moder = {
            "moderatorname": "moder",
            "firstname": "John",
            "lastname": "Price",
            "email": "moderator@email.com",
            "password": "somepassword",
            "moderatorkey": "9876543"
        }
        self.articleData = {
            "article_id": 2,
            "name": "Cars",
            "body": "Smth about car",
            "version": "0.0.0.1"
        }
        self.UpdateArticle = {
            "updated_article_id": 1,
            "article_id": 2,
            "user_id": 2,
            "moderator_id": 1,
            "state_id": 1,
            "article_body": "Something",
            "date": "2015-05-12 12:20:10",
        }
        self.state = {
            "state_id": 1,
            "name": "About math"
        }

    # Tests auth
    def test_auth_moder(self, Session):
        moder_name = all_func.moderator.verify_password(self.moder["moderatorname"], self.moder["password"])
        self.assertEqual(moder_name, self.moder["moderatorname"])

    def test_non_auth_moder(self, Session):
        moder_name = all_func.moderator.verify_password(self.moder["moderatorname"], "invalid_pass")
        self.assertEqual(moder_name, None)

    def test_auth_user(self, Session):
        user_name = all_func.user.verify_password(self.user["username"], self.user["password"])
        self.assertEqual(user_name, self.user["username"])

    def test_non_auth_user(self, Session):

        user_name = all_func.user.verify_password(self.user["username"], "invalid_pass")
        self.assertEqual(user_name, None)

    # Tests user create
    def test_User_Creation_200(self, Session):
        response = self.tester.post("/api/v1/user", data=json.dumps(self.data), content_type="application/json")
        code = response.status_code
        self.assertEqual(200, code)

    def test_User_Creation_400(self, Session):
        response = self.tester.post("/api/v1/user", data={
            "username": True,
            "firstname": "GreatUser",
            "lastname": "Underwood",
            "email": "pres@gmail.com",
            "password": "741852369"
        }, content_type="application/json")
        code = response.status_code
        self.assertEqual(400, code)

    def test_User_Creation_404(self, Session):
        response = self.tester.post("/api/v1/user", data=json.dumps(self.data), content_type="application/json")
        code = response.status_code
        self.assertEqual(404, code)
        delete_user()
        insert_user()


    # Tests user get
    def test_get_user_by_id_code(self, Session):
        response = self.tester.get("/api/v1/user/2", headers = {"Authorization": f"Basic {self.creds}"})
        code = response.status_code
        self.assertEqual(200,code)

    def test_get_user_by_invalid_id(self, Session):
        response = self.tester.get("/api/v1/user/-5", headers = {"Authorization": f"Basic {self.creds}"})
        code = response.status_code
        self.assertEqual(400,code)

    def test_get_user_by_another_invalid_id(self, Session):
        response = self.tester.get("/api/v1/user/50", headers = {"Authorization": f"Basic {self.creds}"})
        code = response.status_code
        self.assertEqual(404,code)

    # Tests user delete
    def test_user_delete_invalidID(self, Session):
        response = self.tester.delete('/api/v1/user/1', headers = {"Authorization": f"Basic {self.creds}"})
        code = response.status_code
        self.assertEqual(401, code)

    def test_user_delete(self, Session):
        response = self.tester.delete('/api/v1/user/2', headers = {"Authorization": f"Basic {self.creds}"})
        code = response.status_code
        insert_user()
        self.assertEqual(401, code)



    # Tests article create
    def test_article_create(self, Session):
        responce = self.tester.post("/api/v1/article",
                                    data = json.dumps(self.articleData),
                                    content_type= "application/json",
                                    headers= {"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(200, code)

    def test_article_create_again(self, Session):
        responce = self.tester.post("/api/v1/article",
                                    data = json.dumps(self.articleData),
                                    content_type= "application/json",
                                    headers= {"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(404, code)

    def test_article_create_inv_data(self, Session):
        responce = self.tester.post("/api/v1/article",
                                    data = "invalid data",
                                    content_type= "application/json",
                                    headers= {"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(400, code)

    # Tests article get
    def test_article_get_data(self, Session):
        responce = self.tester.get("/api/v1/article/2")
        self.assertEqual(responce.json, self.articleData)

    def test_article_get_code(self, Session):
        responce = self.tester.get("/api/v1/article/2")
        code = responce.status_code
        self.assertEqual(200, code)

    def test_article_get_invID(self, Session):
        responce = self.tester.get("/api/v1/article/-1")
        code = responce.status_code
        self.assertEqual(400, code)

    def test_article_get_invID2(self, Session):
        responce = self.tester.get("/api/v1/article/1")
        code = responce.status_code
        self.assertEqual(404, code)

    # Tests article delete
    def test_article_delete_invID(self, Session):
        responce = self.tester.delete("/api/v1/article/-5", headers= {"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(400, code)

    def test_article_delete_invID2(self, Session):
        responce = self.tester.delete("/api/v1/article/10", headers= {"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(404, code)

    def test_article_delete(self, Session):
        responce = self.tester.delete("/api/v1/article/2", headers= {"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(200, code)
        create_article()


    # Tests state create
    def test_state_create(self, Session):
        responce = self.tester.post("/api/v1/state",
                                    data=json.dumps(self.state),
                                    content_type="application/json",
                                    headers={"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(200, code)

    def test_state_create_again(self, Session):
        responce = self.tester.post("/api/v1/state",
                                    data=json.dumps(self.state),
                                    content_type="application/json",
                                    headers={"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(404, code)

    def test_state_create_inv_info(self, Session):
        responce = self.tester.post("/api/v1/state",
                                    data="invalid info",
                                    content_type="application/json",
                                    headers={"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(400, code)

    # Tests state get
    def test_state_get_invID(self, Session):
        response = self.tester.get("/api/v1/state/-2")
        code = response.status_code
        self.assertEqual(400, code)

    def test_state_get_invID2(self, Session):
        response = self.tester.get("/api/v1/state/5")
        code = response.status_code
        self.assertEqual(404, code)

    def test_state_get_code(self, Session):
        response = self.tester.get("/api/v1/state/1")
        code = response.status_code
        self.assertEqual(200, code)

    def test_state_get_data(self, Session):
        response = self.tester.get("/api/v1/state/1")
        self.assertEqual(response.json, self.state)

    # Tests state delete
    def test_state_delete_invID(self, Session):
        response = self.tester.delete("/api/v1/state/-2", headers={"Authorization": f"Basic {self.creds}"})
        code = response.status_code
        self.assertEqual(400, code)

    def test_state_delete_invID2(self, Session):
        response = self.tester.delete("/api/v1/state/5", headers={"Authorization": f"Basic {self.creds}"})
        code = response.status_code
        self.assertEqual(404, code)

    def test_state_delete(self, Session):
        response = self.tester.delete("/api/v1/state/1", headers={"Authorization": f"Basic {self.creds}"})
        code = response.status_code
        self.assertEqual(200, code)
        create_state()

    # Tests update Article create
    def test_updateArticle_create(self, Session):
        responce = self.tester.post( '/api/v1/updateArticle',
                                    data = json.dumps(self.UpdateArticle),
                                    content_type= "application/json",
                                    headers= {"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(200, code)

    def test_updateArticle_create_again(self, Session):
        responce = self.tester.post( '/api/v1/updateArticle',
                                    data = json.dumps(self.UpdateArticle),
                                    content_type= "application/json",
                                    headers= {"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(500, code)

    def test_updateArticle_create_invDat(self, Session):
        responce = self.tester.post('/api/v1/updateArticle',
                                    data="Invalid data",
                                    content_type="application/json",
                                    headers={"Authorization": f"Basic {self.creds}"})
        code = responce.status_code
        self.assertEqual(401, code)

    #Tests moderator create
    def test_moderator_creation(self, Session):
        response = self.tester.post("/api/v1/moderator",
                                    data=json.dumps(self.data_moder),
                                    content_type="application/json",
                                    headers = {"Authorization": f"Basic {self.moder_creds}"})
        code = response.status_code
        self.assertEqual(200, code)

    def test_moderator_creation_inv_data(self, Session):
        response = self.tester.post("/api/v1/moderator",
                                    data= "Inv data",
                                    content_type="application/json",
                                    headers = {"Authorization": f"Basic {self.moder_creds}"})
        code = response.status_code
        self.assertEqual(400, code)

    def test_moderator_creation_again(self, Session):
        response = self.tester.post("/api/v1/moderator",
                                    data=json.dumps(self.data_moder),
                                    content_type="application/json",
                                    headers = {"Authorization": f"Basic {self.moder_creds}"})
        code = response.status_code
        self.assertEqual(404, code)

    # Tests update Article get
    def test_updateArticle_invDat(self, Session):
        responce = self.tester.get('/api/v1/updateArticle/-1')
        code = responce.status_code
        self.assertEqual(400, code)

    def test_updateArticle_get_again(self, Session):
        responce = self.tester.get('/api/v1/updateArticle/10')
        code = responce.status_code
        self.assertEqual(500, code)

    def test_updateArticle_get(self, Session):
        responce = self.tester.get('/api/v1/updateArticle/2')
        code = responce.status_code
        self.assertEqual(500, code)

def delete_user():
    file = open("C:\\Users\\sova\\Desktop\\SalabayRepo\\pp_project\\all_func\\clean.sql")
    clean = sqlalchemy.text(file.read())
    engine.execute(clean)
    file.close()

def insert_user():
    file = open("C:\\Users\\sova\\Desktop\\SalabayRepo\\pp_project\\all_func\\user_insert.sql")
    clean = sqlalchemy.text(file.read())
    engine.execute(clean)
    file.close()

def create_article():
    file = open("C:\\Users\\sova\\Desktop\\SalabayRepo\\pp_project\\all_func\\create_article.sql")
    clean = sqlalchemy.text(file.read())
    engine.execute(clean)
    file.close()

def create_state():
    file = open("C:\\Users\\sova\\Desktop\\SalabayRepo\\pp_project\\all_func\\create_state.sql")
    clean = sqlalchemy.text(file.read())
    engine.execute(clean)
    file.close()
