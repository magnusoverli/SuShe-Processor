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
AppName=SuSheProcessor
; Application Version from version.txt
AppVersion={#MyAppVersion}
; Unique GUID for the application (generate a new one for SuSheProcessor)
AppId={{68d52c10-b192-4693-ad33-afe541ff7b2b}}
; Default installation directory
DefaultDirName={commonpf}\SuSheProcessor
; Default Start Menu group name
DefaultGroupName=SuSheProcessor
; Icon for the uninstaller
UninstallDisplayIcon={app}\logos\sushe_processor.ico
; Output installer filename includes version
OutputBaseFilename="SuSheProcessor Installer v{#MyAppVersion}"
; Compression settings
Compression=lzma2
CompressionThreads=10
SolidCompression=yes
; Ensure 64-bit compatibility
ArchitecturesInstallIn64BitMode=x64compatible
; Setup executable icon
SetupIconFile=logos\sushe_processor.ico
; Directory to place the installer
OutputDir=.\installer\
; Required privileges (lowest for user-level installation)
PrivilegesRequired=admin

; Optional: Re-enable these pages if user interaction for directory or program group is desired
; DisableDirPage=yes
; DisableProgramGroupPage=yes

[Files]
; Include all files from the PyInstaller `dist` folder for SuSheProcessor with version
Source: "dist\SuSheProcessor_v{#MyAppVersion}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Include additional data files like icons
Source: "logos\sushe_processor.ico"; DestDir: "{app}\logos"; Flags: ignoreversion

[Icons]
; Create a desktop shortcut for all users
Name: "{commondesktop}\SuSheProcessor"; Filename: "{app}\SuSheProcessor.exe"; WorkingDir: "{app}"
; Create a Start Menu shortcut for all users
Name: "{commonprograms}\SuSheProcessor"; Filename: "{app}\SuSheProcessor.exe"; WorkingDir: "{app}"
; Create an Uninstall shortcut in the Start Menu for all users
Name: "{commonprograms}\Uninstall SuSheProcessor"; Filename: "{uninstallexe}"; IconFilename: "{app}\logos\sushe_processor.ico"

[Run]
; Launch the application after installation
Filename: "{app}\SuSheProcessor.exe"; Description: "Launch SuSheProcessor"; Flags: nowait postinstall skipifsilent

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
  IsUpgrade := RegKeyExists(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{68d52c10-b192-4693-ad33-afe541ff7b2b}');
  Result := True;  // Proceed with installation
end;

procedure InitializeWizard();
begin
  if IsUpgrade then
  begin
    // Create a custom page for upgrade options
    UpgradePage := CreateCustomPage(wpWelcome, 'Existing Installation Detected', 'SuSheProcessor is already installed on your computer. What would you like to do?');

    // Add radio button for upgrading the application
    UpgradeOption := TRadioButton.Create(WizardForm);
    UpgradeOption.Parent := UpgradePage.Surface;
    UpgradeOption.Caption := 'Upgrade SuSheProcessor to version ' + ExpandConstant('{appversion}');
    UpgradeOption.Top := 20;
    UpgradeOption.Left := 0;
    UpgradeOption.Width := WizardForm.ClientWidth;
    UpgradeOption.Checked := True;  // Default to Upgrade

    // Add radio button for uninstalling the application
    UninstallOption := TRadioButton.Create(WizardForm);
    UninstallOption.Parent := UpgradePage.Surface;
    UninstallOption.Caption := 'Uninstall SuSheProcessor';
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
      if MsgBox('Are you sure you want to uninstall SuShe Processor?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        // Run the uninstaller silently
        if ShellExec('', ExpandConstant('{uninstallexe}'), '/VERYSILENT /NORESTART', '', SW_SHOWNORMAL, ewWaitUntilTerminated, ErrorCode) then
        begin
          // Notify the user and exit the setup
          MsgBox('SuShe Processor has been uninstalled.', mbInformation, MB_OK);
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
    MsgBox('Upgrading SuShe Processor to version ' + ExpandConstant('{appversion}'), mbInformation, MB_OK);
  end;
end;