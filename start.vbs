Dim wshShell
Set wshShell = CreateObject("WScript.Shell")
do
WScript.Sleep(600000)
wshShell.Run("crontab.bat")
loop