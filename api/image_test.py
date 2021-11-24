import pyautogui 
import time
import base64
from io import BytesIO
import requests 


default_url = "http://127.0.0.1:5000/v1/live/1"


def screenshot_base64file():
	
	screen = pyautogui.screenshot()

	buffered = BytesIO()
	screen.save(buffered, format="PNG")
	img_str = base64.b64encode(buffered.getvalue())


	heads = {"Content-Type":"application/json"}
	data = {"data":img_str}

	resp  = requests.post(default_url, headers=heads, json=data)

	#with open ("tmp.txt", "w") as f:
	#	f.write(str(img_str))

		
while True:
	time.sleep(2)
	screenshot_base64file()