try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $doc = $word.Documents.Open('C:\Users\vtila\Videos\WEBSCRAP PROJ\WEB_SCRAPING_AND_PRODUCT_PRICE_ANALYSIS_DOCUMENTATION.docx')
    Write-Host "Total Pages: " $doc.ComputeStatistics(2)
    
    # Iterate through paragraphs with heading styles
    foreach ($p in $doc.Paragraphs) {
        $text = $p.Range.Text.Trim()
        if ($text -match "^(Chapter|1\.|2\.|3\.|4\.|5\.|6\.|7\.|8\.|9\.|10\.|11\.|CERTIFICATE|DECLARATION|ACKNOWLEDGEMENT|ABSTRACT|Table of Contents|List of Figures|List of Tables)") {
            $pageNum = $p.Range.Information(3) # 3 = wdActiveEndPageNumber
            Write-Host "$pageNum : $text"
        }
    }
    
    $doc.Close()
    $word.Quit()
} catch {
    Write-Host "ERROR: $_"
}
