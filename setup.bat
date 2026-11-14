@echo off
TITLE Setup Tape Data Encoder & Decoder Suite
echo Checking Python version...
python --version

echo Checking for Git repository updates...
git pull

echo Ensuring pip is installed and up to date...
python -m ensurepip --default-pip
python -m pip install --upgrade pip

echo Installing required libraries from requirements.txt...
python -m pip install -r requirements.txt

echo Setup completed successfully!
pause
