@echo off
where gradle >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo Gradle is required to build the Android project. Install Gradle or run the CI workflow.
  exit /b 1
)
gradle %*
