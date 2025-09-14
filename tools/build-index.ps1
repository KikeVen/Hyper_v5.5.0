<#
tools/build-index.ps1

This script used to run the include resolver and generate a flattened
`Admin/dist/index.html` for demo purposes. Generating `dist` files can be
confusing because each server framework (Django, Flask, FastAPI) expects a
different templates/static layout and different helper tags for assets.

By default this script is inert and will only print instructions. To actually
run the resolver (for local demo use only) run with the --Force switch.

Example (PowerShell):
  .\tools\build-index.ps1 -Force

#>

param(
    [switch]$Force,
    [string]$Src = "Admin/src/pages-starter.html",
    [string]$Out = "Admin/dist/index.html"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$resolver = Join-Path $scriptDir 'include_resolver.py'

if (-Not $Force) {
    Write-Host "This script is inert by default. To build a local demo file run with -Force."
    Write-Host "Example: .\tools\build-index.ps1 -Force"
    Write-Host "Note: Generated files in Admin/dist are demo-only. When integrating into a framework, follow Documentation/frameworks/* guidance to place templates under 'templates/' and assets under 'static/'."
    exit 0
}

if (-Not (Test-Path $resolver)) {
    Write-Error "include_resolver.py not found in $scriptDir"
    exit 1
}

$python = "python"

& $python $resolver --input $Src --output $Out

Write-Host "Built: $Out"
