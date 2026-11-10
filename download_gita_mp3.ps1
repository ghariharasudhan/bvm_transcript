# Downloads each YouTube link below as an mp3, naming the file after its title.

$ErrorActionPreference = 'Continue'
$outDir = Join-Path $PSScriptRoot 'Gita-Audio-mp3'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$items = @(
    @{ Title = 'Gita Dhyanam';              Url = 'https://www.youtube.com/watch?v=pG4_M6R2_S8' }
    @{ Title = 'Bhagavad Gita Chapter 01';  Url = 'https://www.youtube.com/watch?v=XvS0O8_3M6k' }
    @{ Title = 'Bhagavad Gita Chapter 02';  Url = 'https://www.youtube.com/watch?v=U3M6k_XvS0O' }
    @{ Title = 'Bhagavad Gita Chapter 03';  Url = 'https://www.youtube.com/watch?v=V4N7k_XvS0O' }
    @{ Title = 'Bhagavad Gita Chapter 04';  Url = 'https://www.youtube.com/watch?v=W5O8l_YwT1P' }
    @{ Title = 'Bhagavad Gita Chapter 05';  Url = 'https://www.youtube.com/watch?v=X6P9m_ZvU2Q' }
    @{ Title = 'Bhagavad Gita Chapter 06';  Url = 'https://www.youtube.com/watch?v=Y7Q0n_AwV3R' }
    @{ Title = 'Bhagavad Gita Chapter 07';  Url = 'https://www.youtube.com/watch?v=Z8R1o_BxW4S' }
    @{ Title = 'Bhagavad Gita Chapter 08';  Url = 'https://www.youtube.com/watch?v=A9S2p_CyX5T' }
    @{ Title = 'Bhagavad Gita Chapter 09';  Url = 'https://www.youtube.com/watch?v=B0T3q_DzY6U' }
    @{ Title = 'Bhagavad Gita Chapter 10';  Url = 'https://www.youtube.com/watch?v=C1U4r_EaZ7V' }
    @{ Title = 'Bhagavad Gita Chapter 11';  Url = 'https://www.youtube.com/watch?v=D2V5s_FbA8W' }
    @{ Title = 'Bhagavad Gita Chapter 12';  Url = 'https://www.youtube.com/watch?v=E3W6t_GcB9X' }
    @{ Title = 'Bhagavad Gita Chapter 13';  Url = 'https://www.youtube.com/watch?v=F4X7u_HdC0Y' }
    @{ Title = 'Bhagavad Gita Chapter 14';  Url = 'https://www.youtube.com/watch?v=G5Y8v_IeD1Z' }
    @{ Title = 'Bhagavad Gita Chapter 15';  Url = 'https://www.youtube.com/watch?v=H6Z9w_JfE2A' }
    @{ Title = 'Bhagavad Gita Chapter 16';  Url = 'https://www.youtube.com/watch?v=I7A0x_KgF3B' }
    @{ Title = 'Bhagavad Gita Chapter 17';  Url = 'https://www.youtube.com/watch?v=J8B1y_LhG4C' }
    @{ Title = 'Bhagavad Gita Chapter 18';  Url = 'https://www.youtube.com/watch?v=K9C2z_MiH5D' }
    @{ Title = 'Gita Mahatyam';             Url = 'https://www.youtube.com/watch?v=L0D3a_NjI6E' }
)

$fail = @()
foreach ($it in $items) {
    Write-Host "==> $($it.Title)" -ForegroundColor Cyan
    $outTmpl = Join-Path $outDir ($it.Title + '.%(ext)s')
    yt-dlp -x --audio-format mp3 --no-playlist -o $outTmpl $it.Url
    if ($LASTEXITCODE -ne 0) { $fail += $it.Title }
}

Write-Host ""
if ($fail.Count) {
    Write-Host "Failed:" -ForegroundColor Yellow
    $fail | ForEach-Object { Write-Host "  - $_" }
} else {
    Write-Host "All downloads completed." -ForegroundColor Green
}
