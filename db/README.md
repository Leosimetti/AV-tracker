# Database

Package responsible for interaction with sqlite database.

#### Content:

- \_\_init\_\_.py - necessary empty file to identify folder content as package

- singnals_db.py contains methods to initialize table and put data about user keyboard and mouse input

- timer.py - auxiliary static class that performs countdown to identify when the user is absent based on recent inactivity

- processed_signals_db.py contains methods to initialize table and put data about whether user is present or absent based on mouse and keyboard user interaction

- video_data_db.py contains methods to initialize table, put data about state of the user based on camera feed.

- signals.sqlite - sqlite database file storing all data in 3 tables:

  - images table contains images of user in transition state based on webcam data and additional information. State values: "Present", "Distracted", "Absent".
  - processed_signals table contains information about user state based on mouse and keyboard input. State values: "Present", "Absent".
  -  signals table contains information about user keyboard and mouse input. Device type values: "KEYBOARD" or "MOUSE". Action type values: "TYPING" and "NON-TYPING" for keyboard, "CLICK" and "MOVE" for mouse.

  