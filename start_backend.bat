@echo off
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server...
echo The API will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
echo To start the React frontend, open another terminal and run:
echo   cd frontend
echo   npm install
echo   npm start
echo.

uvicorn main:app --reload
