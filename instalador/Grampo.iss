; Instalador do Grampo (Inno Setup 6). Quem monta é o instalador\montar.py:
;   ISCC /DVersao=1.0.0 /DPrograma=<pasta do Grampo.exe montado> Grampo.iss  ->  dist\Grampo-1.0.0.exe
;
; Instala só para quem está usando o Windows (na pasta do usuário, sem pedir administrador).

#ifndef Versao
  #error Passe a versao: ISCC /DVersao=1.0.0 /DPrograma=<pasta>
#endif
#ifndef Programa
  #error Passe a pasta do programa montado: /DPrograma=...
#endif

[Setup]
AppId={{4F0C2B6E-9A57-4C1E-8E1D-6B3A9F2D7C41}
AppName=Grampo
AppVersion={#Versao}
AppVerName=Grampo {#Versao}
AppPublisher=TI do escritório
VersionInfoVersion={#Versao}
DefaultDirName={autopf}\Grampo
PrivilegesRequired=lowest
DisableDirPage=yes
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=Grampo-{#Versao}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=force
UninstallDisplayIcon={app}\Grampo.exe
UninstallDisplayName=Grampo
SetupIconFile=grampo.ico

[Languages]
Name: "pt"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "areadetrabalho"; Description: "Criar um atalho na Área de Trabalho"

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "{#Programa}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Grampo"; Filename: "{app}\Grampo.exe"
Name: "{autodesktop}\Grampo"; Filename: "{app}\Grampo.exe"; Tasks: areadetrabalho

[Run]
Filename: "{app}\Grampo.exe"; Description: "Abrir o Grampo agora"; Flags: nowait postinstall skipifsilent
