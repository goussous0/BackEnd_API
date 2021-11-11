import unittest 
import random 
import names 
import json 
import requests
from string import printable
from random_username.generate import generate_username
from requests.api import head, put
from clint.textui import puts,colored

from sqlalchemy.orm import defaultload
from app import manager

char_lst = list(printable)[:-6] + [str(i) for i in range(0,10)]

default_URL = "http://127.0.0.1:5000/v1"


user_lst = [] 
pass_lst = [] 


class Flask_Test(unittest.TestCase):


    # creating user 
    def create_user(self):

 #       user = ''.join([random.choice(char_lst) for i in range(random.randrange(2, 7))])
        user = str(generate_username()[0])      
        passwd = ''.join([str(random.choice(char_lst)) for i in range(random.randrange(0,10))])


        new_user = {"username":user,\
                    "first_name":f"{names.get_first_name()}",\
                    "last_name":f"{names.get_last_name()}",\
                    "password":passwd,\
                    "is_active":"true"}

        heads = {'content-type': 'application/json'}

        user_lst.append(user)
        pass_lst.append(passwd)

        resp = requests.post(url=f"{default_URL}/users", headers=heads, data=json.dumps(new_user))
        try:
            self.assertEqual(resp.status_code, 200)
            puts(colored.green(f"Completed test [1] response [ {resp.json()} ] "))
            puts(colored.cyan(f"Used user info : [ {new_user} ]"))



        except AssertionError as ae:
            puts(colored.red(f" {str(ae)}   response [ {resp.json()} ]" ))
            puts(colored.cyan(f"Used user info :  [ {new_user} ] "))
            
        puts(colored.magenta("____________________________________________________________________________________________________"))

            
        


    def get_token(self):

        user_creds = {"username":random.choice(user_lst),\
                      "password":random.choice(pass_lst)}

        heads = {'content-type': 'application/json'}
        
        resp = requests.post(url=f"{default_URL}/api-token-auth", headers=heads , data=json.dumps(user_creds))

        try:
            self.assertEqual(resp.status_code , 200 ) 
            puts(colored.green(f"Completed test [2]  response [ {resp.json()} ]"))
            puts(colored.cyan(f"Used user credentials :  [ {user_creds} ] "))
        except AssertionError as ae:
            puts(colored.red(f" Test Failed {str(ae)}   response [ {resp.json()} ]   " ) )
            puts(colored.cyan(f"Used user creds :   [ {user_creds} ] "))


        puts(colored.magenta("____________________________________________________________________________________________________"))

        




if __name__ == "__main__":
    
    #print  (char_lst)
    x = Flask_Test()

    for i in range(15):
        x.create_user()

    for i in range(30):
        x.get_token()
