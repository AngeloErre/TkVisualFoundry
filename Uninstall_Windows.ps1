$ErrorActionPreference = 'Stop'
$root = Join-Path $env:LOCALAPPDATA 'Programs\VisualTkStudio'
if (!(Test-Path -LiteralPath $root) -or ((Get-Item -LiteralPath $root).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Unrecognized or linked installation root' }
$manifest = Join-Path $root '.visualtk-install.json'
if ((Get-Item -LiteralPath $manifest).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked manifest' }
$data = Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
if ($data.format -ne 1 -or $data.product -ne 'VisualTkStudio' -or $data.token -notmatch '^[a-f0-9]{32}$') { throw 'Unrecognized installation manifest' }
function SafePath($relative) {
  if ([IO.Path]::IsPathRooted($relative) -or $relative.Contains(':') -or (($relative -split '[/\\]') | Where-Object { $_ -eq '..' -or $_ -eq '.' })) { throw 'Unsafe installation path' }
  $path = Join-Path $root $relative
  $item = $path
  while ($item -ne $root) {
    if ((Test-Path -LiteralPath $item) -and ((Get-Item -LiteralPath $item -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Linked installation file' }
    $item = Split-Path $item -Parent
  }
  return $path
}
$remove = @()
foreach ($file in $data.files.PSObject.Properties) {
  $path = SafePath $file.Name
  if (Test-Path -LiteralPath $path -PathType Leaf) {
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower() -eq $file.Value) { $remove += $path } else { Write-Host "Keeping modified file: $path" }
  }
}
Write-Host 'Projects, modified/untracked files, settings, history and system Python are preserved.'
if ((Read-Host 'Uninstall TkVisualFoundry? [y/N]') -notmatch '^(y|yes|s|si)$') { exit 0 }
$environment = SafePath '.venv'
if ($data.environment -and (Test-Path -LiteralPath $environment)) {
  $owner = SafePath '.venv/.visualtk-owner'
  if (!(Test-Path -LiteralPath $owner) -or (Get-Content -LiteralPath $owner -Raw) -ne $data.token) { throw 'Environment ownership mismatch' }
  Add-Type -AssemblyName Microsoft.VisualBasic
  [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($environment, [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs, [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin)
}
$shortcutName = $data.shortcut_name
if (!$shortcutName) { $shortcutName = 'VisualTk Studio.lnk' }
if ($shortcutName -notin @('TkVisualFoundry.lnk','VisualTk Studio.lnk')) { throw 'Unexpected shortcut name' }
$shortcuts = @(@{Name=$shortcutName; Hash=$data.shortcut_sha256})
if ($data.legacy_shortcut_sha256) { $shortcuts += @{Name='VisualTk Studio.lnk'; Hash=$data.legacy_shortcut_sha256} }
foreach ($entry in $shortcuts) {
  $shortcut = Join-Path $env:APPDATA ('Microsoft\Windows\Start Menu\Programs\'+$entry.Name)
  if ((Test-Path -LiteralPath $shortcut) -and (Get-FileHash -LiteralPath $shortcut -Algorithm SHA256).Hash.ToLower() -eq $entry.Hash) { Remove-Item -LiteralPath $shortcut }
}
$key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\VisualTkStudio'
if ((Test-Path -LiteralPath $key) -and (Get-ItemProperty -LiteralPath $key).VTSToken -eq $data.token) { Remove-Item -LiteralPath $key }
foreach ($path in $remove) { Remove-Item -LiteralPath $path -Force }
Remove-Item -LiteralPath $manifest -Force
# Remove only empty directories that contained managed files; preserve unknown folders.
$directories = @()
foreach ($file in $remove) {
  $directory = Split-Path $file -Parent
  while ($directory -ne $root) { $directories += $directory; $directory = Split-Path $directory -Parent }
}
$directories | Sort-Object -Unique -Descending | ForEach-Object {
  if ((Test-Path -LiteralPath $_) -and !(Get-ChildItem -LiteralPath $_ -Force)) { Remove-Item -LiteralPath $_ }
}
if (!(Get-ChildItem -LiteralPath $root -Force)) { Remove-Item -LiteralPath $root }
Write-Host 'Uninstalled. Modified or personal files, if any, remain in the installation folder.'
