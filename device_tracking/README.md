# Device tracking

Package responsible for tracking user state and recent activity. Use database(db) package to store data.

#### Content:

- \_\_init\_\_.py - necessary empty file to identify folder content as package
- keyboard_tracker.py contains classes responsible for tracking keyboard input, identifying type(typing or non-typing) of input and requesting to store data about it.
- mouse_tracker.py contains classes responsible for tracking mouse input, identifying type(click or move) of input and requesting to store data about it.
- pythonic_video_tracker.py contains methods for getting camera feed, identifying user state via machine learning models, preprocessing image data before showing it  to include additional information and recording state changes. 

