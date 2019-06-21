# 100DaysOfFitness
Public version of the 100 Days of Fitness Kivy (KivyMD) app

Download this code using `git clone https://github.com/Dirk-Sandberg/100DaysOfFitness`, it will create a folder named 100DaysOfFitness. Go into that directory and run the code using `python3 main.py`.
You MUST use Python3 to run this code.

To fully use the app, you need to create a Firebase project and put the Web API Key inside the `main.kv` file of this code.
Need help creating a firebase project? Check out my tutorial: https://www.youtube.com/watch?v=pgpoQZN9G6M
The Web API key can be found by going to the Project Settings of your Firebase project, then the Web API Key field is what you want.
 
Once working, the app will automatically sign you in every time you start the app. If you want to disable that,
change `debug = True` in line 74 of `main.py`.