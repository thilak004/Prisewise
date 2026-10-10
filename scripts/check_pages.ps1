try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $doc = $word.Documents.Open('C:\Users\vtila\Videos\WEBSCRAP PROJ\WEB_SCRAPING_AND_PRODUCT_PRICE_ANALYSIS_DOCUMENTATION.docx')
    $pages = $doc.ComputeStatistics(2) # 2 = wdStatisticPages
    $doc.Close()
    $word.Quit()
    Write-Host "WORD_PAGE_COUNT: $pages"
} catch {
    Write-Host "ERROR: $_"
}
