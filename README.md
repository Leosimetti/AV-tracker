# AV-tracker
Lean Software Development course project that determines the user's current state by processing the video feed and mouse/video signals. 

### UI

User interface is implemented as a web page. User can adjust FPS of the webcam, timer control as well as turn off/on mouse, keyboard and video tracking. In addition, user can also change camera that is being used. Web page shows user state based on keyboard&mouse input and video feed.

![image](https://user-images.githubusercontent.com/42554566/110464381-a51ea280-8105-11eb-977d-fea3c3e76523.png)

### Stored information

The end product of the program is the sqlite database that stores information about user state(based on webcam feed and user keyboard&mouse input) and gifs that shows user in transition state.

### Additional information

To crate binaries for windows use the following:
```
pyinstaller main.py --noconsole --onefile --add-data "GUI;GUI" --exclude-module tensorflow --hidden-import=pynput
```


For additional details about implementation of internal packages, check the readme file in folder with the package.

### Team members:

Vitaliy Korbashev (Leosimonetti)

Mihail Olokin (nikololiahim)

Muravev Ruslan (supersloy)











