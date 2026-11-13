# Packages and environment

Select the project Python interpreter in Project → Configuration. The PIP wizard checks declared requirements and imports in that interpreter, installs missing packages, verifies the result and resumes the pending component action when ready. Automatic installation can be configured in the package settings.

Webcam components require NumPy, OpenCV and Pillow. PostgreSQL and MySQL require their respective drivers; SQLite is included with Python. Native dependencies such as VLC are separate from PIP. Read wizard output when an installation fails: interpreter compatibility, network access and native libraries may need attention. Tkinter cannot be installed using PIP.
