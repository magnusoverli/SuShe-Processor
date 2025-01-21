; Define constants for file handling and versioning
#define FileHandle
#define MyAppVersion

; Read the application version from version.txt
#expr FileHandle = FileOpen('version.txt')
#if FileHandle == 0
  #error 'Failed to open version.txt'
#endif

#expr MyAppVersion = Trim(FileRead(FileHandle))
#expr FileClose(FileHandle)

[Setup]
; Application Name
AppName=Album Presentation App
; Application Version from version.txt
AppVersion={#MyAppVersion}
; Unique GUID for the application (generate a new one for AlbumPresentationApp)
AppId={{YOUR-NEW-GUID-HERE}}
; Default installation directory
DefaultDirName={pf}\AlbumPresentationApp
; Default Start Menu group name
DefaultGroupName=AlbumPresentationApp
; Icon for the uninstaller
UninstallDisplayIcon={app}\logos\sushe_processor.ico
; Output installer filename includes version
OutputBaseFilename="AlbumPresentationApp Installer v{#MyAppVersion}"
; Compression settings
Compression=lzma2
CompressionThreads=10
SolidCompression=yes
; Ensure 64-bit compatibility
ArchitecturesInstallIn64BitMode=x64
; Setup executable icon
SetupIconFile=logos\sushe_processor.ico
; Directory to place the installer
OutputDir=.\installer\
; Required privileges (lowest for user-level installation)
PrivilegesRequired=lowest

; Optional: Re-enable these pages if user interaction for directory or program group is desired
; DisableDirPage=yes
; DisableProgramGroupPage=yes

[Files]
; Include all files from the PyInstaller `dist` folder for AlbumPresentationApp with version
Source: "dist\AlbumPresentationApp_v{#MyAppVersion}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Include additional data files like icons
Source: "logos\sushe_processor.ico"; DestDir: "{app}\logos"; Flags: ignoreversion

[Icons]
; Create a desktop shortcut
Name: "{userdesktop}\AlbumPresentationApp"; Filename: "{app}\main.exe"; WorkingDir: "{app}"
; Create a Start Menu shortcut
Name: "{group}\AlbumPresentationApp"; Filename: "{app}\main.exe"; WorkingDir: "{app}"
; Create an Uninstall shortcut in the Start Menu
Name: "{group}\Uninstall AlbumPresentationApp"; Filename: "{uninstallexe}"; IconFilename: "{app}\logos\sushe_processor.ico"

[Run]
; Launch the application after installation
Filename: "{app}\main.exe"; Description: "Launch Album Presentation App"; Flags: nowait postinstall skipifsilent

[Code]
var
  IsUpgrade: Boolean;
  UpgradePage: TWizardPage;
  UninstallOption: TRadioButton;
  UpgradeOption: TRadioButton;
  ErrorCode: Integer;

function InitializeSetup(): Boolean;
begin
  // Detect existing installation using the AppId GUID
  IsUpgrade := RegKeyExists(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{{YOUR-NEW-GUID-HERE}_is1}');
  Result := True;  // Proceed with installation
end;

procedure InitializeWizard();
begin
  if IsUpgrade then
  begin
    // Create a custom page for upgrade options
    UpgradePage := CreateCustomPage(wpWelcome, 'Existing Installation Detected', 'Album Presentation App is already installed on your computer. What would you like to do?');

    // Add radio button for upgrading the application
    UpgradeOption := TRadioButton.Create(WizardForm);
    UpgradeOption.Parent := UpgradePage.Surface;
    UpgradeOption.Caption := 'Upgrade Album Presentation App to version ' + ExpandConstant('{appversion}');
    UpgradeOption.Top := 20;
    UpgradeOption.Left := 0;
    UpgradeOption.Width := WizardForm.ClientWidth;
    UpgradeOption.Checked := True;  // Default to Upgrade

    // Add radio button for uninstalling the application
    UninstallOption := TRadioButton.Create(WizardForm);
    UninstallOption.Parent := UpgradePage.Surface;
    UninstallOption.Caption := 'Uninstall Album Presentation App';
    UninstallOption.Top := UpgradeOption.Top + UpgradeOption.Height + 10;
    UninstallOption.Left := 0;
    UninstallOption.Width := WizardForm.ClientWidth;
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  // Skip installation pages if the user chooses to uninstall
  if IsUpgrade and UninstallOption.Checked and ((PageID = wpSelectDir) or (PageID = wpSelectProgramGroup) or (PageID = wpReady)) then
    Result := True
  else
    Result := False;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True; // Allow to proceed by default
  if IsUpgrade and (CurPageID = UpgradePage.ID) then
  begin
    if UninstallOption.Checked then
    begin
      // Confirm uninstallation
      if MsgBox('Are you sure you want to uninstall Album Presentation App?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        // Run the uninstaller silently
        if ShellExec('', ExpandConstant('{uninstallexe}'), '/VERYSILENT /NORESTART', '', SW_SHOWNORMAL, ewWaitUntilTerminated, ErrorCode) then
        begin
          // Notify the user and exit the setup
          MsgBox('Album Presentation App has been uninstalled.', mbInformation, MB_OK);
          Result := False; // Prevent moving to the next page
          Abort(); // Exit the setup
        end
        else
        begin
          // Notify the user of the failure
          MsgBox('Uninstallation failed. Error code: ' + IntToStr(ErrorCode), mbError, MB_OK);
          Result := False; // Stay on the current page
        end;
      end
      else
      begin
        // User canceled uninstallation, stay on the same page
        Result := False;
      end;
    end
    else if UpgradeOption.Checked then
    begin
      // Proceed with the upgrade
      // Optionally, add any upgrade-specific code here
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssInstall) and IsUpgrade and UpgradeOption.Checked then
  begin
    MsgBox('Upgrading Album Presentation App to version ' + ExpandConstant('{appversion}'), mbInformation, MB_OK);
  end;
end;