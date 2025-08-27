Set oShell = CreateObject("Wscript.shell")
Dim strArgs
strArgs = "cmd /c run_all.bat"
oShell.Run strArgs, 0, false
