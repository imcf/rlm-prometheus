# example script to restart the RLM service and rotate its log files


#### adjust settings here ####
$LogPath = "D:\RLM_Logs"
$IsvName = "bitplane"
#### adjust settings here ####


$Service = Get-Service $IsvName -ErrorAction Stop
Stop-Service $Service

$FileNames = @(
    "$($IsvName)_report_std",
    "$($IsvName)_debug_std"
)

$TimeStamp = Get-Date -Format "yyyy-MM-dd"

foreach ($FileName in $FileNames) {
    $Orig = "$LogPath\$($FileName).log"
    $Target = "$LogPath\$($FileName)__$($TimeStamp).log"

    if (! (Test-Path $Orig)) {
        Write-Host "Can't find log file [$Orig], skipping!"
        continue
    }

    if (Test-Path $Target) {
        Write-Host "Target [$Target] already existing, not renaming current log file!"
        continue
    }
    Rename-Item -Path $Orig -NewName $Target
}

Start-Service $Service
