# Packages and environment

Select the project Python interpreter in Project → Configuration. The PIP wizard checks declared requirements and imports in that interpreter, installs missing packages, verifies the result and resumes the pending component action when ready. Automatic installation can be configured in the package settings.

Webcam components require NumPy, OpenCV and Pillow. PostgreSQL and MySQL require their respective drivers; SQLite is included with Python. Native dependencies such as VLC are separate from PIP. Read wizard output when an installation fails: interpreter compatibility, network access and native libraries may need attention. Tkinter cannot be installed using PIP.


## In-app catalog (1.17)

Open PIP → Package catalog…: Recommended contains component packages, All PyPI searches the official project-name index and Installed lists the selected interpreter. Search and browse 100 results per page, select details/a compatible stable release, then install or add the project requirement. Exact name… avoids the full index download. Cached names work offline; descriptions/installation need network access. Refresh index retains the old cache if refresh fails. Full-description search is not available.
