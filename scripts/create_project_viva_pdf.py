from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    KeepTogether,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = Path("output/pdf/PriceWise_Project_Guide_and_Viva.pdf")

QUESTIONS = [
    ("What problem does PriceWise solve?", "It reduces the effort of checking the same product across several online stores and highlights price differences."),
    ("What is the project objective?", "To collect or load product offers, clean them, compare prices, show analytics, and recommend attractive deals."),
    ("Who are the users?", "Online shoppers who want a quick, data-driven price comparison before buying."),
    ("What are the four architectural layers?", "Ingestion, data pipeline, analytics and ML, and the Streamlit presentation layer."),
    ("Which language and framework are used?", "Python is the language and Streamlit builds the interactive web interface."),
    ("Why Streamlit?", "It lets us build a multi-page data application with Python, widgets, charts, and fast reruns."),
    ("What is the role of Pandas?", "Pandas loads CSV data, cleans fields, filters offers, groups records, and calculates summaries."),
    ("What is Plotly used for?", "It creates interactive bar, line, pie, and distribution charts in the dashboard."),
    ("What is the primary data source today?", "The checked-in data/pricewise_data.csv file. It contains prepared product offers used by the dashboard."),
    ("Does the current project scrape live retail websites?", "No. scraper_config.py is set to demo mode. The current UI uses the prepared CSV; the Live Scraping button is also a simulation."),
    ("Why is the scraper separated from the UI?", "It decouples slower data collection from fast dashboard interaction and makes each part easier to maintain."),
    ("What fields are stored for an offer?", "Product name, category, platform, price, original price, discount, rating, availability, URL, scrape date, and optional image path."),
    ("How is schema flexibility achieved?", "The loader maps common column aliases such as name/title and price/current_price to canonical fields."),
    ("What happens if optional fields are absent?", "The application hides dependent UI or analysis safely instead of failing."),
    ("How are numeric values cleaned?", "Currency symbols, commas, and whitespace are removed, then values are converted with invalid values becoming missing."),
    ("How does the pipeline validate data?", "It limits valid price, discount, and rating ranges, normalizes dates, and removes rows without product name or price."),
    ("How are duplicates handled?", "Exact duplicates are removed; duplicate product name and platform records keep the lowest price."),
    ("Why keep the lowest duplicate price?", "For the same listed product on the same platform, the lowest usable observed offer is the most useful comparison value."),
    ("What is the BaseScraper?", "A reusable HTTP component that handles robots.txt checks, delays, caching, redirects, retries, and errors."),
    ("How does it behave on HTTP 429?", "It stops that source immediately and reports rate limiting rather than repeatedly requesting it."),
    ("How are temporary server failures handled?", "5xx errors and connection or timeout failures can retry with exponential backoff, up to the configured retry count."),
    ("How does it respect website policies?", "It checks robots.txt, uses a declared user agent, applies a request delay, and has no CAPTCHA bypass logic."),
    ("What does caching do?", "It saves successful responses locally so identical requests can be reused and fewer requests are sent."),
    ("How does search work?", "The home page builds one best-price record per product, then filters it with typed search and fuzzy suggestions."),
    ("Which filters are available?", "Category, platform, and price range; they narrow the dataset before listings and analytics are calculated."),
    ("How does exact product comparison work?", "It matches the selected product name, groups records by platform, and uses the lowest platform price."),
    ("How is potential saving calculated?", "Potential saving equals the average price across available platforms minus the lowest price."),
    ("What happens when exact products cannot be matched?", "The category comparison tab shows the cheapest product on each platform within the selected category."),
    ("What analytics are available?", "Price summary, category and platform averages, discount distribution, product counts, and platform offer share."),
    ("What does platform market share mean here?", "It is the share of offers in this dataset, not the company real commercial market share."),
    ("How does price history work?", "When scrape dates exist, the application groups a selected product by date using the day's minimum observed price."),
    ("What is the watchlist?", "A session-level list of product names saved by a user during the current Streamlit session."),
    ("What is the deal score?", "A weighted heuristic combining lower price 40%, discount 25%, rating 20%, and availability 15%."),
    ("Why normalize score components?", "Price, percentage discount, and ratings use different scales; normalization puts them onto a comparable 0-1 scale."),
    ("What is MCDA in this project?", "Multi-Criteria Decision Analysis: it combines several shopping criteria into one deal score."),
    ("What ML algorithm is used?", "Logistic Regression classifies whether an offer is a good deal according to the project target definition."),
    ("What are the ML input features?", "Category, platform, discount, and rating, when those columns are available."),
    ("What target label does the code use?", "An offer is labeled good when its price is below the median price of the loaded dataset."),
    ("How are categorical features prepared?", "OneHotEncoder converts category and platform values into binary indicator columns and ignores unseen values safely."),
    ("How is the model evaluated in the app?", "The data is split 80:20 with random_state 42 and the UI reports held-out accuracy."),
    ("Is good-deal prediction the same as best-deal score?", "No. The score is a transparent weighted rule; the classifier learns a below-median label from the dataset."),
    ("What are the ML limitations?", "The target is relative to the dataset, not a verified real bargain; accuracy can change with data quality and class balance."),
    ("Why use handle_unknown ignore?", "It prevents failure if a user selects a category or platform not seen while the model was trained."),
    ("What dataset scale is used?", "1,500 offers representing 300 distinct product names across five categories and 13 platforms."),
    ("Which categories are covered?", "Beauty, Books, Electronics, Fashion, and Home."),
    ("What tests are included?", "Pipeline tests cover invalid values and duplicate rules; scraper tests cover 429 handling and 5xx retry behavior."),
    ("How can it be deployed?", "With Streamlit Community Cloud or the supplied Dockerfile, which starts Streamlit on port 8501."),
    ("What are major limitations?", "No live sources are configured, matching uses exact names, prices can vary by location or payment offer, and the watchlist is not persistent."),
    ("What would you improve first?", "Use authorized APIs or permitted sources, add canonical product matching, persist history in a database, and add price-drop alerts."),
    ("How do you defend the project value?", "It demonstrates the full flow from responsible ingestion design and data cleaning to consumer-facing analytics and explainable recommendations."),
]


def para(text, style):
    return Paragraph(text.replace("&", "&amp;"), style)


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#606b7a"))
    canvas.drawString(48, 28, "PriceWise - Project Guide and Viva Preparation")
    canvas.drawRightString(A4[0] - 48, 28, f"Page {doc.page}")
    canvas.restoreState()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=48, leftMargin=48, topMargin=48, bottomMargin=48
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=27, textColor=colors.HexColor("#183b5b"), alignment=TA_CENTER, spaceAfter=10)
    subtitle = ParagraphStyle("Subtitle", parent=styles["BodyText"], fontSize=11, leading=15, textColor=colors.HexColor("#425466"), alignment=TA_CENTER, spaceAfter=22)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=colors.HexColor("#183b5b"), spaceBefore=12, spaceAfter=7)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.2, leading=14.5, spaceAfter=7)
    small = ParagraphStyle("Small", parent=body, fontSize=9.1, leading=12.4)
    q = ParagraphStyle("Question", parent=body, fontName="Helvetica-Bold", textColor=colors.HexColor("#173f5f"), spaceBefore=5, spaceAfter=2)
    a = ParagraphStyle("Answer", parent=body, leftIndent=12, textColor=colors.HexColor("#243746"), spaceAfter=6)

    story = [
        Spacer(1, 0.65 * inch),
        para("PriceWise", title),
        para("Web Scraping and Product Price Analysis System", subtitle),
        para("Project explanation, build guide, and external-lab viva preparation", subtitle),
        Spacer(1, 0.35 * inch),
        para("Project overview", h1),
        para("PriceWise is a multi-page Python web application that helps shoppers compare prepared product offers across online stores. It loads flexible CSV data, cleans and filters offers, identifies the lowest listed price, presents analytics, gives an explainable deal score, and offers a lightweight machine-learning classification.", body),
        para("The current checked-in version is a data-driven dashboard. Its scraper infrastructure is included, but it is configured in demo mode. During a presentation, state that the app uses the prepared dataset and that the Live Scraping UI is a demonstration simulation.", body),
        Spacer(1, 0.15 * inch),
        para("Dataset snapshot", h1),
    ]
    snapshot = [
        [para("Metric", small), para("Observed value", small)],
        [para("Offers", small), para("1,500", small)],
        [para("Distinct product names", small), para("300", small)],
        [para("Categories", small), para("Beauty, Books, Electronics, Fashion, Home", small)],
        [para("Platforms", small), para("13", small)],
        [para("Scrape-date span", small), para("11 September 2026 to 25 September 2026", small)],
        [para("Average offer price", small), para("Rs. 12,467.27", small)],
        [para("Price range", small), para("Rs. 155.88 to Rs. 163,104.00", small)],
    ]
    table = Table(snapshot, colWidths=[2.1 * inch, 4.55 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183b5b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#ccd6df")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f6f8fa")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [table, PageBreak(), para("How we built the project", h1)]
    phases = [
        ("1. Data ingestion design", "We added BaseScraper for polite collection from permitted sources. It supports robots.txt checks, a declared user agent, request delays, safe redirect handling, local response caching, and retries for temporary failures. It stops on forbidden access and rate limits."),
        ("2. Data pipeline", "data_pipeline.py completes the expected schema, trims text fields, converts numeric values, validates valid ranges, normalizes dates, removes invalid essential rows, and retains the lowest price for duplicate product and platform records."),
        ("3. Flexible data loader", "utils/data_loader.py recognizes common CSV column aliases. It cleans currency strings and derives a discount if price and original price exist but discount does not."),
        ("4. Analytics engine", "utils/analysis.py provides summary statistics, category and platform groupings, discount distribution, platform offer share, product counts, product-level comparison, price history, deal scoring, and prediction functions."),
        ("5. Dashboard", "The Streamlit pages implement Home, Comparison, Analytics, and About views. Users can search, filter, view product cards, compare platform offers, save a session watchlist, download comparison CSV, and inspect interactive Plotly charts."),
        ("6. Deal recommendation and ML", "The heuristic deal score uses lower price, discount, rating, and availability. Logistic Regression classifies a good deal as an offer whose price is below the loaded dataset median. Categorical features use one-hot encoding."),
        ("7. Testing and packaging", "Unit tests cover invalid prices, discounts, ratings, duplicate handling, 429 stopping behavior, and retry behavior for temporary server errors. A Dockerfile is included for container deployment."),
    ]
    for heading, text in phases:
        story += [para(heading, q), para(text, body)]
    story += [para("Demonstration sequence", h1)]
    for i, text in enumerate([
        "Install dependencies from requirements.txt and start the Streamlit application through app.py.",
        "Open Home, show category, platform, and price filters, then search for a product.",
        "Open View Details and explain the price table, lowest price, highest price, average, potential saving, chart, and CSV export.",
        "Show the category comparison option when an exact product is unavailable on several platforms.",
        "Open Analytics and explain the category, platform, discount, offer-share, and product-count charts.",
        "Demonstrate the Deal Quality form, while explaining that its target is below-median price in this dataset.",
    ], 1):
        story += [para(f"{i}. {text}", body)]
    story += [PageBreak(), para("External lab viva questions", h1), para("Use these as answer cues. Explain in your own words and do not claim live scraping or fixed ML metrics that have not been reproduced from the current code.", body)]
    for idx, (question, answer) in enumerate(QUESTIONS, 1):
        story.append(KeepTogether([
            para(f"{idx}. {question}", q),
            para(f"Answer cue: {answer}", a),
        ]))
    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)


if __name__ == "__main__":
    build()
