echo "Please run this from admin cmd prompt. Point the DockerInstallFolder to the desired location and the InstallerPath to the Docker Installer."

set DockerInstallFolder=D:\DockerCustomInstall
set InstallerPath=D:\gitrepos\seomaps\Docker Desktop Installer.exe

set ProgramData=%DockerInstallFolder%\ProgramData
set ProgramFiles=%DockerInstallFolder%\Program Files
set ProgramFiles(x86)=%DockerInstallFolder%\Program Files(x86)
set ProgramW6432=%DockerInstallFolder%\Program Files

echo %ProgramData%
echo %ProgramFiles%
echo %ProgramFiles(x86)%
echo %ProgramW6432%

mkdir "%DockerInstallFolder%"
mkdir "%ProgramData%"
mkdir "%ProgramFiles%"
mkdir "%ProgramFiles(x86)%"
mkdir "%ProgramW6432%"

"%InstallerPath%"