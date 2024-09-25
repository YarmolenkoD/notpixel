@echo off

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)


echo Activating virtual environment...
call venv\Scripts\activate

if not exist venv\Lib\site-packages\installed (
    if exist requirements.txt (
		echo installing wheel for faster installing
		pip install wheel
        echo Installing dependencies...
        pip install -r requirements.txt
        echo. > venv\Lib\site-packages\installed
    ) else (
        echo requirements.txt not found, skipping dependency installation.
    )
) else (
    echo Dependencies already installed, skipping installation.
)

if not exist .env (
	echo Copying configuration file
	copy .env-example .env
) else (
	echo Skipping .env copying
)

::Обновление локального репозитория без удаления изменений
git stash
git pull
git stash pop

echo Starting the bot...
python main.py

echo done
echo PLEASE EDIT .ENV FILE
pause
