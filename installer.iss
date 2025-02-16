#define MyAppName "RamanImage"
#define MyAppVersion "1.0"
#define MyAppPublisher "RamanTools"
#define MyAppExeName "ImageReconstructor.exe"

[Setup]
AppId={{B8A4D520-2A85-4713-B532-A1E652C8D3B4}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={userdesktop}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=RamanImage_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
CreateAppDir=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional tasks:"

[Files]
; Main executable and dependencies
Source: "dist\ImageReconstructor\ImageReconstructor.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ImageReconstructor\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; Copy application data
Source: "config\*"; DestDir: "{commonappdata}\{#MyAppName}\config"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "data\*"; DestDir: "{commonappdata}\{#MyAppName}\data"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 移動 data 資料夾到應用程式主目錄
Filename: "{cmd}"; Parameters: "/C move ""{commonappdata}\{#MyAppName}\data"" ""{app}\data"""; Flags: runhidden

; 移動 config 資料夾到應用程式主目錄
Filename: "{cmd}"; Parameters: "/C move ""{commonappdata}\{#MyAppName}\config"" ""{app}\config"""; Flags: runhidden

; 啟動應用程式
Filename: "{app}\{#MyAppExeName}"; Description: "Launch application"; Flags: nowait postinstall skipifsilent



[Dirs]
; Create and set permissions for application data directories
Name: "{commonappdata}\{#MyAppName}"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\data"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\output"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\config"; Permissions: users-full