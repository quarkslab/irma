:: Download and Install Chocolatey
powershell -NoProfile -ExecutionPolicy unrestricted -Command "iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))"

:: Define ChocolateyInstall and append to System PATH
:: NOTE: we should perform checks on environment variables before appending
set ChocolateyInstall="%ALLUSERSPROFILE%\chocolatey\bin"
setx /M PATH "%PATH%;%ChocolateyInstall%"
