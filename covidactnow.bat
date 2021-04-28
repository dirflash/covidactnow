# covidactnow.bat file
# windows solution

call C:/code/covidactnow/.env/Scripts/activate.bat

cd C:/code/covidactnow/

py covidactnow.py

call C:/code/covidactnow/.env/Scripts/deactivate.bat

exit /B 1
