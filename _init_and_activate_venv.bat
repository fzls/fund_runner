python -m venv .venv_dev
call .venv_dev\Scripts\activate.bat

python -m pip install -i https://pypi.doubanio.com/simple --upgrade pip setuptools wheel
pip install -i https://pypi.doubanio.com/simple --upgrade -r requirements.txt
