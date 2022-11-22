# code snippet to allow remote access to the RLM web service from a specific IP

$RuleName = "Reprise License Server Web GUI"
$Rule = Get-NetFirewallRule -DisplayName $RuleName

# show all details, not  necessary for changing them but helpful for debugging:
$Rule | Select-Object *

# show current address filters:
$Rule | Get-NetFirewallAddressFilter

# store currently allowed remote IPs in a variable:
$RemoteIPsCur = ($Rule | Get-NetFirewallAddressFilter).RemoteAddress

# define remote IPs to be added to the rule:
$RemoteIPsAdd = @("10.17.34.5")

# combine them, remove duplicates
$RemoteIPsNew = $RemoteIPsAdd + $RemoteIPsCur | Select-Object -Unique

# update the rule with the new remote IPs
Set-NetFirewallRule -DisplayName $RuleName -RemoteAddress $RemoteIPsNew