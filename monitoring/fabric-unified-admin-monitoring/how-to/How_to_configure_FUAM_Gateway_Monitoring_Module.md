
# FUAM Gateway Monitoring

Documentation state: **Preview**

Configuring and deploying the push-data-ingestion solution on a single host machine.


## Prerequisites
- A Power BI or Fabric capacity (PPU, Pro 'shared' workspaces are not supported)
- Ability to create a Service Principal on your tenant
- Admin access to the gateway host(s)
- Internet connection on gateway host(s)
- Opened endpoints and ports see list [here](https://learn.microsoft.com/en-us/fabric/security/fabric-allow-list-urls#onelake)

After the following steps, you will be able to:
- see the Gateway logs from your host machine in FUAM_Lakehouse (files/history/gateway_logs)
- The Powershell script uploads periodically the log files into FUAM_Lakehouse
- The Powershell script is scheduled with Task Scheduler

Open the downloaded solution package in VS Code or in another text editors. Open a new instance of the Windows Terminal


# Steps

Follow the steps to configure, deploy and schedule the gateway monitoring module for FUAM.

When you are using multiple gateway instances, the steps has to be done on each instances.

## 1. Connect e.g via RDP to you gateway host

- Navigate to the [FUAM gateway module source code](https://github.com/microsoft/fabric-toolbox/blob/FUAM-2025.8.1/monitoring/fabric-unified-admin-monitoring/src/FUAM_Gateway_Monitoring_Module.zip)

- Download the zip package on your gateway host machine (to one of your main administrative folders)
- 

## 2. Install Powershell 7

Open the Terminal on your machine

    winget search Microsoft.PowerShell
    winget install --id Microsoft.PowerShell --source winget

# 3. Setup-Configuration.ps1

- Open the PowerShellScripts/Setup-Configuration.ps1 file in text editor (VS Code, etc.)

This is a sample of the configuration properties. These properties will be persisted in a config file on the same solution folder.

    $GatewayLogUploadConfig = @{
        GatewayId              = "<YOUR-GATEWAY-ID>"
        GatewayLogsPath        = @()
        RootPath               = "raw"
        OutputPath             = ".\data"
        HeartbeatEnable        = $false
        HeartbeatInterval      = 30
        ReportSendInterval     = 30
        ReportRetention        = 10
        VerboseLogSendInterval = 600
        ServicePrincipal       = @{
            TennatId   = "<TENANT-ID>"
            AppId      = "<APP-CLIENT-ID>"
            SecretText = "<SECRET-VALUE>"
        }
        EventHubs              = @{
            UploadReports     = $false
            ConnectionStrings = @()
        }
        Lakehouse              = @{
            UploadReports = $true
            UploadLogs    = $true
            WorkspaceName = "<YOUR-WORKSPACE-NAME>"
            LakehouseName = "FUAM_Lakehouse"        
        }
        ConnectionProperties = @{
            MaximumRetryCount = 3
            RetryIntervalSec = 1
        }
    }

## 3.2 Configuration

Open the terminal (Powershell 7.x)

Navigate with cd to the right folder path of the Powershell scripts

Optionally:

    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

then:

    pwsh -File "Setup-Configuration.ps1"

Answer the following questions:

- Install PowerShell Module Az.Accounts? Needed only for Lakehouse connectivity (Y/N): Y
- Install PowerShell Module Az.Storage? Needed only for Lakehouse connectivity (Y/N): Y
- Install PowerShell Module DataGateway? Needed only for Lakehouse connectivity (Y/N): Y
- Install PowerShell Module MicrosoftPowerBIMgmt? Needed only for GatewayInfo (Y/N): Y

- Validating log path
Do you want to configure the Log Path for the Gateway Reports? (Y/N): Y

>**Gateway logs path, default:** C:\Windows\ServiceProfiles\PBIEgwService\AppData\Local\Microsoft\On-premises data gateway

- Do you want to configure the Heartbeat for the Gateway Reports? (Y/N): N

- Set intervals, retention etc., if needed.

- Do you want to configure the EventStream/EventHub for the Gateway Reports? (Y/N): N

- Do you want to configure the Service Principal? (Without SP you can´t connect to the Lakehouse) (Y/N): Y

- Set Tenant Id
- Set App Id
- Set Secret

- Do you want to configure the Lakehouse upload for the Gateway? (Y/N): Y

- Do you want to configure the Lakehouse upload for the Gateway Reports? (Y/N): Y

- Do you want to configure the Lakehouse upload for the Gateway Logs? (Y/N): Y


-----------------

## 3.3 Add SP to Workspace & Gateway Connection

- Grant access for the configured SP to the FUAM Workspace with at least **Contributor** rights

- Grant access for the configured SP to the FUAM Workspace with at least **Content Creator** rights



## 3.4 Run-UploadGatewayLogs.ps1

Run the script initially in Terminal to test the connections.
This script will upload the configured logs from the gateway-hosts into the FUAM_Lakehouse files.

    pwsh -File "Run-UploadGatewayLogs.ps1"



## 3.5 Schedule the Scripts

- Import the **Gateway-Upload Logs.xml** file within the TaskSchedulers folder into the Task Scheduler App on your Gateway Host machine.

- Configure the Security options
    - Change the user account
    - Review the other settings

- Save the task

**Congratulations!**

Now, the Gateway host sends the logs to FUAM_Lakehouse.


---------------

## Next Steps

- Configuring Power BI Report in FUAM workspace
