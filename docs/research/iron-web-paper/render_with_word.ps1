param([Parameter(Mandatory=$true)][string]$DocumentPath)
$ErrorActionPreference = 'Stop'
$taskDocPath = (Get-Item -LiteralPath $DocumentPath).FullName
$taskQaPath = Join-Path (Split-Path -Parent $taskDocPath) 'qa'
New-Item -ItemType Directory -Path $taskQaPath -Force | Out-Null
$taskPdfPath = Join-Path $taskQaPath 'manuscript.pdf'
$taskWord = $null
$taskDocument = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskDocument = $taskWord.Documents.Open($taskDocPath, $false, $true)
    $taskDocument.Repaginate()
    $taskPageCount = $taskDocument.ComputeStatistics(2)
    $taskDocument.ExportAsFixedFormat($taskPdfPath, 17)
    [pscustomobject]@{Document=$taskDocPath; PDF=$taskPdfPath; Pages=$taskPageCount} | ConvertTo-Json
} finally {
    if ($null -ne $taskDocument) {
        $taskDocument.Close(0)
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDocument)
    }
    if ($null -ne $taskWord) {
        $taskWord.Quit(0)
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord)
    }
}
