# Register Windows Scheduled Task for Plato the Archivist
# Runs daily at 5:00 AM and 3:00 PM

$taskName = "PlatoCaseStudyUploader"
$scriptPath = Join-Path $PSScriptRoot "run_upload.bat"
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`""
$trigger1 = New-ScheduledTaskTrigger -Daily -At "05:00AM"
$trigger2 = New-ScheduledTaskTrigger -Daily -At "03:00PM"
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger1, $trigger2 `
    -Principal $principal `
    -Description "Plato the Archivist - Checks for new case studies and uploads to MySQL (twice daily)"

Write-Host "Scheduled task '$taskName' created successfully."
Write-Host "Runs daily at 5:00 AM and 3:00 PM"
