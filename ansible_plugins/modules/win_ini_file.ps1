#!powershell
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# WANT_JSON
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Michael DeHaan <michael.dehaan@gmail.com>, 2014, and others
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# Helper function to parse Ansible JSON arguments from a file passed as
# the single argument to the module
# Example: $params = Parse-Args $args
Function Parse-Args($arguments)
{
    $parameters = New-Object psobject;
    If ($arguments.Length -gt 0)
    {
        $parameters = Get-Content $arguments[0] | ConvertFrom-Json;
    }
    $parameters;
}

# Helper function to set an "attribute" on a psobject instance in powershell.
# This is a convenience to make adding Members to the object easier and
# slightly more pythonic
# Example: Set-Attr $result "changed" $true
Function Set-Attr($obj, $name, $value)
{
    # If the provided $obj is undefined, define one to be nice
    If (-not $obj.GetType)
    {
        $obj = New-Object psobject
    }

    $obj | Add-Member -Force -MemberType NoteProperty -Name $name -Value $value
}

# Helper function to convert a powershell object to JSON to echo it, exiting
# the script
# Example: Exit-Json $result
Function Exit-Json($obj)
{
    # If the provided $obj is undefined, define one to be nice
    If (-not $obj.GetType)
    {
        $obj = New-Object psobject
    }

    echo $obj | ConvertTo-Json -Depth 99
    Exit
}

# Helper function to add the "msg" property and "failed" property, convert the
# powershell object to JSON and echo it, exiting the script
# Example: Fail-Json $result "This is the failure message"
Function Fail-Json($obj, $message = $null)
{
    # If we weren't given 2 args, and the only arg was a string, create a new
    # psobject and use the arg as the failure message
    If ($message -eq $null -and $obj.GetType().Name -eq "String")
    {
        $message = $obj
        $obj = New-Object psobject
    }
    # If the first args is undefined or not an object, make it an object
    ElseIf (-not $obj.GetType -or $obj.GetType().Name -ne "PSCustomObject")
    {
        $obj = New-Object psobject
    }

    Set-Attr $obj "msg" $message
    Set-Attr $obj "failed" $true
    echo $obj | ConvertTo-Json -Depth 99
    Exit 1
}

# Helper function to get an "attribute" from a psobject instance in powershell.
# This is a convenience to make getting Members from an object easier and
# slightly more pythonic
# Example: $attr = Get-Attr $response "code" -default "1"
#Note that if you use the failifempty option, you do need to specify resultobject as well.
Function Get-Attr($obj, $name, $default = $null,$resultobj, $failifempty=$false, $emptyattributefailmessage)
{
    # Check if the provided Member $name exists in $obj and return it or the
    # default
    If ($obj.$name.GetType)
    {
        $obj.$name
    }
    Elseif($failifempty -eq $false)
    {
        $default
    }
    else
    {
        if (!$emptyattributefailmessage) {$emptyattributefailmessage = "Missing required argument: $name"}
        Fail-Json -obj $resultobj -message $emptyattributefailmessage
    }
    return
}

# Helper filter/pipeline function to convert a value to boolean following current
# Ansible practices
# Example: $is_true = "true" | ConvertTo-Bool
Function ConvertTo-Bool
{
    param(
        [parameter(valuefrompipeline=$true)]
        $obj
    )

    $boolean_strings = "yes", "on", "1", "true", 1
    $obj_string = [string]$obj

    if (($obj.GetType().Name -eq "Boolean" -and $obj) -or $boolean_strings -contains $obj_string.ToLower())
    {
        $true
    }
    Else
    {
        $false
    }
    return
}


function Get-IniContent
{
<#
.Synopsis
  Reads the contents of an INI file into an OrderedDictionary
.Description
  The dictionary can be manipulated the same way a Hashtable can, by
  adding or removing keys to the various sections.

  By using an OrderedDictionary, the contents of the file can be
  roundtripped through the Out-IniFile cmdlet.

  Nested INI sections represented like the following are supported:

  [foo]
  name = value
  [[bar]]
  name = value
  ;name = value

  Comment lines prefixed with a ; are returned in the output with a name
  of {Comment-X} where X is the comment index within the entire INI file

  Comments also have an IsComment property attached to the values, so
  that Out-IniFile may properly handle them.
.Notes
  Inspiration from Oliver Lipkau <oliver@lipkau.net>
  http://tinyurl.com/9g4zonn
.Inputs
  String or FileInfo
.Outputs
  Collections.Specialized.OrderedDictionary
  Keys with a OrderdedDictionary Value are representative of sections

  Sections may be nested to any arbitrary depth
.Parameter Path
  Specifies the path to the input file. Can be a string or FileInfo
  object
.Example
  $configFile = Get-IniContent .\foo.ini

  Description
  -----------
  Parses the foo.ini file contents into an OrderedDictionary for local
  reading or manipulation
.Example
  $configFile = .\foo.ini | Get-IniContent
  $configFile.SectionName | Select *

  Description
  -----------
  Same as the first example, but using pipeline input.
  Additionally outputs all values stored in the [SectionName] section of
  the INI file.
#>
  [CmdletBinding()]
  param(
    [Parameter(ValueFromPipeline=$True, Mandatory=$True)]
    [ValidateNotNullOrEmpty()]
    [ValidateScript({ (Test-Path $_) -and ($_.Extension -eq '.ini') })]
    [IO.FileInfo]
    $Path
  )

  Process
  {
    Write-Verbose "[INFO]: Get-IniContent processing file [$Path]"

    # TODO: once Powershell 3 is common, this can be $ini = [ordered]@{}
    $ini = New-Object Collections.Specialized.OrderedDictionary

    function getCurrentOrEmptySection($section)
    {
      if (!$section)
      {
        if (!$ini.Keys -contains '')
        {
          $ini[''] = New-Object Collections.Specialized.OrderedDictionary
        }
        $section = $ini['']
      }
      return $section
    }

    $comments = 0
    $sections = @($ini)
    switch -regex -file $Path
    {
      #http://stackoverflow.com/questions/9155483/regular-expressions-balancing-group
      '\[((?:[^\[\]]|(?<BR> \[)|(?<-BR> \]))+(?(BR)(?!)))\]' # Section
      {
        $name = $matches[1]
        # since the regex above is balanced, depth is a simple count
        $depth = ($_ | Select-String '\[' -All).Matches |
          Measure-Object |
          Select -ExpandProperty Count

        # root section
        Write-Verbose "Parsing section $_ at depth $depth"
        # handles any level of nested section
        $section = New-Object Collections.Specialized.OrderedDictionary
        $sections[$depth - 1][$name] = $section
        if ($sections.Length -le $depth)
        {
          $sections += $section
        }
        else
        {
          $sections[$depth] = $section
        }
      }
      '^(;.*)$' # Comment
      {
        $section = getCurrentOrEmptySection $section
        $name = '{Comment-' + ($comments++) + '}'
        $section[$name] = $matches[1] |
          Add-Member -MemberType NoteProperty -Name IsComment -Value $true -PassThru
      }
      '(.+?)\s*=\s*(.*)' # Key
      {
        $name, $value = $matches[1..2]
        (getCurrentOrEmptySection $section)[$name] = $value
      }
    }

    Write-Verbose "[SUCCESS]: Get-IniContent processed file [$path]"
    return $ini
  }
}

function Out-IniFile
{
<#
.Synopsis
  Write the contents of a Hashtable or OrderedDictionary to an INI file
.Description
  The input can either be a standard Powershell hash created with @{},
  an [ordered]@{} in Powershell 3, an OrderedDictionary created by the
  Get-IniContent cmdlet.

  Will write out the fully nested structure to an INI file
.Notes
  Inspiration from Oliver Lipkau <oliver@lipkau.net>
  http://tinyurl.com/94tdhdx
.Inputs
  Accepts either a Collections.Specialized.OrderedDictionary or
  a standard Powershell Hashtable
.Outputs
  Returns an IO.FileInfo object if -PassThru is specified
  System.IO.FileSystemInfo
.Parameter InputObject
  Specifies the OrderedDictionary or Hashtable to be written to the file
.Parameter FilePath
  Specifies the path to the output file.
.Parameter Encoding
  Specifies the type of character encoding used in the file. Valid
  values are "Unicode", "UTF7", "UTF8", "UTF32", "ASCII",
  "BigEndianUnicode", "Default", and "OEM". "Unicode" is the default.

  "Default" uses the encoding of the system's current ANSI code page.

  "OEM" uses the current original equipment manufacturer code page
  identifier for the operating system.
.Parameter Append
  Adds the output to the end of an existing file, instead of replacing
  the file contents.
.Parameter Force
  Allows the cmdlet to overwrite an existing read-only file. Even using
  the Force parameter, the cmdlet cannot override security restrictions.
.Parameter PassThru
  Returns the newly written FileInfo. By default, this cmdlet does not
  generate any output.
.Example
  @{ Section = @{ Foo = 'bar'; Baz = 1} } |
    Out-IniFile -FilePath .\foo.ini

  Description
  -----------
  Writes the given Hashtable to foo.ini as

  [Section]
  Baz=1
  Foo=bar
.Example
  @{ Section = [ordered]@{ Foo = 'bar'; Baz = 1} } |
    Out-IniFile -FilePath .\foo.ini

  Description
  -----------
  Writes the given Hashtable to foo.ini, in the given order

  [Section]
  Foo=bar
  Baz=1
.Example
  @{ Section = [ordered]@{ Foo = 'bar'; Baz = 1} } |
    Out-IniFile -FilePath .\foo.ini -Force

  Description
  -----------
  Same as previous example, except that foo.ini is overwritten should
  it already exist
.Example
  $file = @{ Section = [ordered]@{ Foo = 'bar'; Baz = 1} } |
    Out-IniFile -FilePath .\foo.ini

  Description
  -----------
  Same as previous example, except that the FileInfo object is returned
.Example
  $config = Get-IniContent .\foo.ini
  $config.Section.Value = 'foo'

  $config | Out-IniFile -Path .\foo.ini -Force


  Description
  -----------
  Parses the foo.ini file contents into an OrderedDictionary with the
  Get-IniContent cmdlet.  Manipulates the contents, then overwrites the
  existing file.
#>

  [CmdletBinding()]
  Param(
    [Parameter(ValueFromPipeline=$true, Mandatory=$true)]
    [ValidateScript({ ($_ -is [Collections.Specialized.OrderedDictionary]) -or `
      ($_ -is [Hashtable]) })]
    [ValidateNotNullOrEmpty()]
    $InputObject,

    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [ValidateScript({ Test-Path $_ -IsValid })]
    [string]
    $FilePath,

    [Parameter(Mandatory=$false)]
    [ValidateSet('Unicode','UTF7','UTF8','UTF32','ASCII','BigEndianUnicode',
      'Default','OEM')]
    [string]
    $Encoding = 'Unicode',

    [Parameter()]
    [switch]
    $Append,

    [Parameter()]
    [switch]
    $Force,

    [Parameter()]
    [switch]
    $PassThru
  )

  process
  {
    Write-Verbose "[INFO]: Out-IniFile writing file [$FilePath]"
    if ((New-Object IO.FileInfo($FilePath)).Extension -ne '.ini')
    {
      Write-Warning 'Out-IniFile [$FilePath] does not end in .ini extension'
    }

    if ((Test-Path $FilePath) -and (!$Force))
    {
      throw "The -Force switch must be applied to overwrite $outFile"
    }

    $outFile = $null
    if ($append) { $outFile = Get-Item $FilePath -ErrorAction SilentlyContinue }
    if ([string]::IsNullOrEmpty($outFile) -or (!(Test-Path $outFile)))
      { $outFile = New-Item -ItemType File -Path $FilePath -Force:$Force }

    #recursive function write sections at various depths
    function WriteKeyValuePairs($dictionary, $sectionName = $null, $depth = 0)
    {
      #Sections - take into account nested depth
      if ((![string]::IsNullOrEmpty($sectionName)) -and ($depth -gt 0))
      {
        $sectionName = "$('[' * $depth)$sectionName$(']' * $depth)"
        Write-Verbose "[INFO]: writing section $sectionName to $outFile"
        Add-Content -Path $outFile -Value $sectionName -Encoding $Encoding
      }

      $dictionary.GetEnumerator() |
        % {
          if ($_.Value -is [Collections.Specialized.OrderedDictionary] -or
            $_.Value -is [Hashtable])
          {
            Write-Verbose "[INFO]: Writing section [$($_.Key)] of $sectionName"
            WriteKeyValuePairs $_.Value $_.Key ($depth + 1)
          }
          elseif ($_.Value.IsComment -or ($_.Key -match '^\{Comment\-[\d]+\}'))
          {
            Write-Verbose "[INFO]: Writing comment $($_.Value)"
            Add-Content -Path $outFile -Value $_.Value -Encoding $Encoding
          }
          else
          {
            Write-Verbose "[INFO]: Writing key $($_.Key)"
            Add-Content -Path $outFile -Value "$($_.Key)=$($_.Value)" `
              -Encoding $Encoding
          }
        }
    }

    WriteKeyValuePairs $InputObject

    Write-Verbose "[SUCCESS]: Out-IniFile wrote file [$outFile]"
    if ($PassThru) { return $outFile }
  }
}

Function Do-Ini
{
    param(
        [Parameter(Mandatory = $True)]
        [string] $dest,
        [Parameter(Mandatory = $True)]
        [string] $section,
        $option  = $NULL,
        $value   = $NULL,
        [string] $state   = "present",
        [boolean]$backup  = $FALSE
    )

    $changed = $FALSE

    If (Test-Path $dest) {
        # File exists, load the Ini File into a dictionary
        $cp = Get-IniContent $dest
    } Else {
        # File does not exist, create an empty dictionary
        $cp = [ordered]@{}
    }

    #Write-Output "cp:", $cp

    if ($state -eq "absent") {
        if (($option -eq $NULL) -and ($value -eq $NULL)) {
            if ($cp.Contains($section)) {
                $cp.Remove($section)
                $changed = $TRUE
            }
        } Else {
            if ($option -eq $NULL) {
                if ($cp.Contains($section)) {
                    $section_ = $cp.Get_Item($section)
                    if ($section_.Contains($option)) {
                        $section_.Remove($option)
                        $changed = $TRUE
                    }
                }
            }
        }
    }

    if ($state -eq "present") {
        # DEFAULT section is always there by DEFAULT, so never try to add it
        if ((-Not $cp.Contains($section)) -And ($section.ToUpper() -ne "DEFAULT")) {
            $cp.Add($section, [ordered]@{})
            $changed = $TRUE
        }
        if (($option -ne $NULL) -And ($value -ne $NULL)) {
            If ($cp.Contains($section)) {
                $section_ = $cp.Get_Item($section)
                If ($section_.Contains($option)) {
                    $value_ = $section_.Get_Item($option)
                    if ($value -ne $value_) {
                        $section_.Set_Item($option, $value)
                        $changed = $TRUE
                    }
                } Else {
                    $section_.Add($option, $value)
                    $changed = $TRUE
                }
            } Else {
                $cp.Add($section, [ordered]@{$option = $value})
                $changed = $TRUE
            }
        }
    }

    if ($changed -eq $TRUE) {
        Try {
            if ($backup -eq $TRUE) {
                $filename = $dest + "." + $(Get-Date -UFormat "%Y-%m-%d@%H.%M~")
                Copy-Item -Path $dest -Destination $filename
            }
            $filename = $dest
            $cp | Out-IniFile -FilePath $filename -Force -Encoding Default
        } Catch {
            Fail-Json (New-Object psobject) ("Can't create {0}" -f $filename);
        }   
    }

    return $changed
}

# result
$result = New-Object psobject @{
    changed = $FALSE
}

$params = Parse-Args $args;

$dest = Get-Attr $params "dest" $FALSE;
If ($dest -eq $FALSE)
{
    Fail-Json (New-Object psobject) "missing required argument: dest";
}

$section = Get-Attr $params "section" $FALSE;
If ($section -eq $FALSE)
{
    Fail-Json (New-Object psobject) "missing required argument: section";
}

$option = Get-Attr $params "option" $NULL;
$value  = Get-Attr $params "value" $NULL;

$backup  = Get-Attr $params "backup" "no";
If ($backup -NotIn "yes", "no")
{
    Fail-Json (New-Object psobject) "invalid argument for backup";
} Else {
    If ($backup -eq "yes") {
        $backup = $TRUE
    } Else {
        $backup = $FALSE
    }
}

# JH Following advice from Chris Church, only allow the following states
# in the windows version for now:
# state - file, directory, touch, absent
# (originally was: state - file, link, directory, hard, touch, absent)
$state = Get-Attr $params "state" "present";
If ($state -NotIn "present", "absent")
{
    Fail-Json (New-Object psobject) "invalid argument for state";
}

$result.dest    = $dest
$result.changed = Do-Ini $dest $section $option $value $state $backup
$result.msg     = "OK"

Exit-Json $result
