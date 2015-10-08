$package = 'PyWin32'
$build = '219'

try {
  # python.exe should be in PATH based on
  #simulate the unix command for finding things in path
  #http://stackoverflow.com/questions/63805/equivalent-of-nix-which-command-in-powershell
  function Which([string]$cmd)
  {
    Get-Command -ErrorAction "SilentlyContinue" $cmd |
      Select -ExpandProperty Definition
  }


  # Use PYTHONHOME if it exists, or fallback to 'Where' to search PATH
  if ($Env:PYTHONHOME) { $localPython = Join-Path $Env:PYTHONHOME 'python.exe' }

  if (!$Env:PYTHONHOME -or !(Test-Path $localPython))
    { $localPython = Which python.exe }

  if (!(Test-Path $localPython))
  {
    Write-ChocolateyFailure 'PyWin32 requires a Python runtime to install'
    return
  }

  $pythonRoot = Split-Path $localPython

  $sitePackages = (Join-Path (Join-Path $pythonRoot 'Lib') 'site-packages')
  if (!(Test-Path $sitePackages))
  {
    Write-ChocolateyFailure 'Could not find Python site-packages directory'
    return
  }

  $7zip = Which 7z.exe
  # guess that a bad install didn't put it in PATH
  if (!$7zip)
  {
    $7zip = $Env:ProgramFiles, ${Env:ProgramFiles(x86)} |
      % { Join-Path (Join-Path $_ '7-zip') '7z.exe' } |
      ? { Test-Path $_ } |
      Select -First 1
  }
  if (!(Test-Path $7zip))
  {
    Write-ChocolateyFailure 'PyWin32 requires 7zip to silently install'
    return
  }

  $pythonVersion = &$localPython --version 2>&1

  $simpleVersion = $pythonVersion |
    Select-String -Pattern '^.*\s+(\d\.\d)(\.\d+){0,1}$' |
    % { $_.Matches.Groups[1].Value }

  # http://www.jordanrinke.com/2011/06/22/pywin32-silent-install/

  $destination = Join-Path $Env:Temp "pywin32-$build.$simpleVersion.exe"
  $params = @{
    packageName = $package;
    fileFullPath = $destination;
    url = "http://sourceforge.net/projects/pywin32/files/pywin32/Build%20$build/pywin32-$build.win32-py$simpleVersion.exe/download";
    url64bit = "http://sourceforge.net/projects/pywin32/files/pywin32/Build%20$build/pywin32-$build.win-amd64-py$simpleVersion.exe/download";
  }

  # no special 64-bit for these python versions
  if ('2.5', '2.4', '2.3' -contains $simpleVersion)
  {
    $params.url64bit = $params.url
  }

  Get-ChocolateyWebFile @params

  $pyWin32Temp = Join-Path $Env:Temp 'pywin32-temp'
  &$7zip x -y $destination "-o$pyWin32Temp"

  # NOTE: Copy Instead of Move in order to avoid issues when already installed
  #       and using -force switch
  'PLATLIB', 'SCRIPTS' |
    % { Join-Path $pywin32Temp $_ } |
    Get-ChildItem |
    Copy-Item -Destination $sitePackages -force -recurse

  # some files are copied to c:\windows\system32
  # NOTE: Former install procedure does not work with ansible
  &$localPython "$sitePackages\pywin32_postinstall.py" -install ;
  Remove-Item "$sitePackages\pywin32_postinstall.py"

  $pyWin32Temp, $destination |
    Remove-Item -Recurse -ErrorAction SilentlyContinue

  Write-ChocolateySuccess $package
} catch {
  Write-ChocolateyFailure $package "$($_.Exception.Message)"
  throw
}
