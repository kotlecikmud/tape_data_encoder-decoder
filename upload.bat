@echo off
TITLE Upload Repository Changes
echo Adding and committing changes...
git add .
git commit -m "Add KCS Waveform Analyzer to GUI, homogenize unified app in main.py, fix binary image formats and add run.bat"
echo Pushing to remote repository...
git push
pause
