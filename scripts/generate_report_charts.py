import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set aesthetics
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 11

os.makedirs('docs_assets', exist_ok=True)

# Load dataset
df = pd.read_csv('data/pricewise_data.csv')

# 1. Flowchart & Architecture
def make_flowchart():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.axis('off')
    
    boxes = [
        ("Data Extraction\n(Web Scrapers & APIs)", 0.1, 0.5, "#2B6CB0"),
        ("Raw CSV Ingestion\n(1,500 Multi-Platform Offers)", 0.3, 0.5, "#2C7A7B"),
        ("Data Preprocessing\n(Deduplication, Cleaning, Type-Cast)", 0.5, 0.5, "#D69E2E"),
        ("Analytics & ML Engine\n(Deal Scoring & Logistic Regression)", 0.7, 0.5, "#DD6B20"),
        ("Streamlit Multi-Page UI\n(Search, Compare, Insights)", 0.9, 0.5, "#319795")
    ]
    
    for text, x, y, color in boxes:
        ax.text(x, y, text, ha='center', va='center', color='white', weight='bold',
                bbox=dict(boxstyle='round,pad=0.8', facecolor=color, edgecolor='none', alpha=0.95),
                fontsize=9)
        
    for i in range(len(boxes) - 1):
        x1 = boxes[i][1] + 0.08
        x2 = boxes[i+1][1] - 0.08
        ax.annotate('', xy=(x2, 0.5), xytext=(x1, 0.5),
                    arrowprops=dict(arrowstyle="->", lw=2.5, color='#4A5568'))
        
    ax.set_title("Figure 4.2: End-to-End Workflow Flowchart of PriceWise System", fontsize=13, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_workflow.png', bbox_inches='tight')
    plt.close()

def make_architecture():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.axis('off')
    
    layers = [
        ("Presentation Layer\n(Streamlit UI: Home, Comparison, Analytics, Prediction)", 0.8, "#3182CE"),
        ("Machine Learning & Analytics Layer\n(Deal Quality Predictor, Best Deal Algorithm, Aggregations)", 0.6, "#38A169"),
        ("Data Preprocessing & Pipeline Layer\n(Schema Validation, Deduplication, Standardization, One-Hot Encoding)", 0.4, "#DD6B20"),
        ("Data Ingestion & Storage Layer\n(CSV Data Store, Scraper Engine, Rate Limiter, Error Handler)", 0.2, "#805AD5")
    ]
    
    for title, y, color in layers:
        ax.text(0.5, y, title, ha='center', va='center', color='white', weight='bold',
                bbox=dict(boxstyle='round,pad=1.0', facecolor=color, edgecolor='none', alpha=0.9),
                fontsize=11)
        
    for i in range(len(layers) - 1):
        ax.annotate('', xy=(0.5, layers[i][1] - 0.06), xytext=(0.5, layers[i+1][1] + 0.06),
                    arrowprops=dict(arrowstyle="<->", lw=2, color='#2D3748'))
        
    ax.set_title("Figure 4.1: Four-Tier System Architecture Diagram", fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_architecture.png', bbox_inches='tight')
    plt.close()

# 2. Bar Graphs: Category Average Price and Average Discount
def make_bar_graphs():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    
    cat_price = df.groupby('category')['price'].mean().reset_index()
    cat_disc = df.groupby('category')['discount'].mean().reset_index()
    
    colors = ['#3182CE', '#38A169', '#E53E3E', '#DD6B20', '#805AD5']
    
    bars1 = ax1.bar(cat_price['category'], cat_price['price'], color=colors, edgecolor='black', alpha=0.85)
    ax1.set_title("Average Product Price by Category (₹)", weight='bold')
    ax1.set_ylabel("Price in INR (₹)")
    ax1.set_xlabel("Category")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 1000, f"₹{int(yval):,}", ha='center', va='bottom', fontsize=8, weight='bold')
        
    bars2 = ax2.bar(cat_disc['category'], cat_disc['discount'], color=colors, edgecolor='black', alpha=0.85)
    ax2.set_title("Average Discount Percentage by Category (%)", weight='bold')
    ax2.set_ylabel("Average Discount (%)")
    ax2.set_xlabel("Category")
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f"{yval:.1f}%", ha='center', va='bottom', fontsize=8, weight='bold')
        
    plt.suptitle("Figure 6.1: Category-Wise Price and Discount Comparison", fontsize=14, weight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_bar_category.png', bbox_inches='tight')
    plt.close()

# 3. Pie Chart: Platform Market Share
def make_pie_chart():
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    plat_counts = df['platform'].value_counts()
    
    colors = sns.color_palette('pastel')[0:len(plat_counts)]
    wedges, texts, autotexts = ax.pie(plat_counts.values, labels=plat_counts.index, autopct='%1.1f%%',
                                      startangle=140, colors=colors, textprops=dict(color="black", size=9))
    for at in autotexts:
        at.set_fontsize(8)
        at.set_weight('bold')
        
    ax.set_title("Figure 6.2: Platform Market Share & Product Offer Distribution", fontsize=13, weight='bold', pad=15)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_pie_marketshare.png', bbox_inches='tight')
    plt.close()

# 4. Histogram: Price and Discount Distribution
def make_histogram():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    
    # Filter price for histogram readability
    sns.histplot(df['price'], bins=25, kde=True, ax=ax1, color='#3182CE', edgecolor='black')
    ax1.set_title("Price Distribution Across All Offers", weight='bold')
    ax1.set_xlabel("Price in INR (₹)")
    ax1.set_ylabel("Frequency (Count)")
    
    sns.histplot(df['discount'].dropna(), bins=20, kde=True, ax=ax2, color='#38A169', edgecolor='black')
    ax2.set_title("Discount Percentage Distribution", weight='bold')
    ax2.set_xlabel("Discount (%)")
    ax2.set_ylabel("Frequency (Count)")
    
    plt.suptitle("Figure 6.3: Histograms of Product Prices and Discounts", fontsize=14, weight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_histogram_price.png', bbox_inches='tight')
    plt.close()

# 5. Box Plot: Category-wise Price Spread
def make_box_plot():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    sns.boxplot(x='category', y='price', data=df, ax=ax, palette='Set2')
    ax.set_yscale('log')
    ax.set_title("Figure 6.4: Log-Scaled Price Distribution Across Categories (Box Plot)", weight='bold', fontsize=13)
    ax.set_xlabel("Category", weight='bold')
    ax.set_ylabel("Price (INR, Log Scale)", weight='bold')
    plt.tight_layout()
    plt.savefig('docs_assets/fig_boxplot_category.png', bbox_inches='tight')
    plt.close()

# 6. Line Chart: Price Fluctuations
def make_line_chart():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    date_cat = df.groupby(['scraped_date', 'category'])['price'].mean().reset_index()
    sns.lineplot(data=date_cat, x='scraped_date', y='price', hue='category', marker='o', ax=ax, palette='tab10')
    ax.set_title("Figure 6.5: Average Price Trends Over Time Across Product Categories", weight='bold', fontsize=13)
    ax.set_xlabel("Scraped Date", weight='bold')
    ax.set_ylabel("Average Price (₹)", weight='bold')
    plt.xticks(rotation=30)
    ax.legend(title='Category', loc='upper right')
    plt.tight_layout()
    plt.savefig('docs_assets/fig_line_price_trend.png', bbox_inches='tight')
    plt.close()

# 7. Scatter Plot: Price vs Discount
def make_scatter_plot():
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    sns.scatterplot(data=df, x='price', y='discount', hue='category', alpha=0.7, palette='Dark2', ax=ax)
    sns.regplot(data=df, x='price', y='discount', scatter=False, ax=ax, color='red', line_kws={'linestyle':'--'})
    ax.set_title("Figure 6.6: Scatter Plot of Price vs. Discount Percentage with Trendline", weight='bold', fontsize=13)
    ax.set_xlabel("Price in INR (₹)", weight='bold')
    ax.set_ylabel("Discount (%)", weight='bold')
    plt.tight_layout()
    plt.savefig('docs_assets/fig_scatter_price_discount.png', bbox_inches='tight')
    plt.close()

# 8. Project-Specific Visualizations: Multi-platform Comparison
def make_project_specific():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    sample_prod = "Apple iPhone 16 (128 GB)"
    sample_df = df[df['product_name'] == sample_prod].drop_duplicates(subset=['platform'])
    
    bars = ax.bar(sample_df['platform'], sample_df['price'], color='#2B6CB0', edgecolor='black', width=0.5)
    ax.set_title(f"Figure 6.7: Multi-Platform Price Comparison for '{sample_prod}'", weight='bold', fontsize=13)
    ax.set_ylabel("Price in INR (₹)", weight='bold')
    ax.set_xlabel("E-Commerce Platform", weight='bold')
    
    min_price = sample_df['price'].min()
    for bar in bars:
        height = bar.get_height()
        if height == min_price:
            bar.set_color('#38A169')
            ax.text(bar.get_x() + bar.get_width()/2.0, height + 1000, f"BEST DEAL\n₹{int(height):,}",
                    ha='center', va='bottom', fontsize=8, weight='bold', color='#22543D')
        else:
            ax.text(bar.get_x() + bar.get_width()/2.0, height + 1000, f"₹{int(height):,}",
                    ha='center', va='bottom', fontsize=8)
            
    plt.ylim(0, sample_df['price'].max() * 1.18)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_multiplatform_compare.png', bbox_inches='tight')
    plt.close()

# 9. Composite Deal Score Tiers
def make_deal_score_chart():
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    
    # Calculate deal score
    p_norm = 1 - (df['price'] - df['price'].min()) / (df['price'].max() - df['price'].min())
    d_norm = df['discount'] / 100.0
    r_norm = df['rating'] / 5.0
    scores = 0.40 * p_norm + 0.25 * d_norm + 0.20 * r_norm + 0.15 * 1.0
    
    tiers = []
    for s in scores:
        if s >= 0.75: tiers.append("Excellent")
        elif s >= 0.55: tiers.append("Good")
        elif s >= 0.35: tiers.append("Average")
        else: tiers.append("Poor")
        
    s_counts = pd.Series(tiers).value_counts()[['Excellent', 'Good', 'Average', 'Poor']]
    colors = ['#38A169', '#3182CE', '#DD6B20', '#E53E3E']
    
    bars = ax.bar(s_counts.index, s_counts.values, color=colors, edgecolor='black', width=0.55)
    ax.set_title("Figure 6.8: Composite Deal Score Tier Distribution Across Dataset", weight='bold', fontsize=13)
    ax.set_xlabel("Deal Tier", weight='bold')
    ax.set_ylabel("Number of Offers", weight='bold')
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, h + 15, f"{int(h)} ({h/len(scores)*100:.1f}%)",
                ha='center', va='bottom', fontsize=9, weight='bold')
        
    plt.tight_layout()
    plt.savefig('docs_assets/fig_deal_score_tiers.png', bbox_inches='tight')
    plt.close()

# 10. ML Evaluation Charts: Confusion Matrix & ROC Curve & Coefficients
def make_ml_eval_charts():
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix, roc_curve, auc, classification_report
    
    work = df.copy()
    median_price = work['price'].median()
    work['is_good_deal'] = (work['price'] < median_price).astype(int)
    
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    cat_encoded = encoder.fit_transform(work[['category', 'platform']])
    cat_names = encoder.get_feature_names_out(['category', 'platform'])
    
    X_num = work[['discount', 'rating']].fillna(0).values
    X = np.hstack([X_num, cat_encoded])
    y = work['is_good_deal'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    cm = confusion_matrix(y_test, y_pred)
    
    # 10.1 Confusion Matrix
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,
                xticklabels=['Not Good Deal (0)', 'Good Deal (1)'],
                yticklabels=['Not Good Deal (0)', 'Good Deal (1)'])
    ax.set_title("Figure 7.1: Confusion Matrix for Deal Quality Classifier", weight='bold', fontsize=12)
    ax.set_xlabel("Predicted Label", weight='bold')
    ax.set_ylabel("True Label", weight='bold')
    plt.tight_layout()
    plt.savefig('docs_assets/fig_confusion_matrix.png', bbox_inches='tight')
    plt.close()
    
    # 10.2 ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    ax.plot(fpr, tpr, color='#2B6CB0', lw=2.5, label=f'ROC curve (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], color='gray', lw=1.5, linestyle='--')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate (1 - Specificity)', weight='bold')
    ax.set_ylabel('True Positive Rate (Sensitivity)', weight='bold')
    ax.set_title('Figure 7.2: Receiver Operating Characteristic (ROC) Curve', weight='bold', fontsize=12)
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig('docs_assets/fig_roc_curve.png', bbox_inches='tight')
    plt.close()
    
    # 10.3 Feature Importances
    all_feature_names = ['discount', 'rating'] + list(cat_names)
    coefs = model.coef_[0]
    coef_df = pd.DataFrame({'feature': all_feature_names, 'coefficient': coefs})
    coef_df['abs_coef'] = coef_df['coefficient'].abs()
    top_coef = coef_df.sort_values('abs_coef', ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    colors = ['#38A169' if c > 0 else '#E53E3E' for c in top_coef['coefficient']]
    ax.barh(top_coef['feature'], top_coef['coefficient'], color=colors, edgecolor='black')
    ax.axvline(0, color='black', linewidth=1)
    ax.set_title("Figure 7.3: Top 10 Feature Coefficients in Logistic Regression", weight='bold', fontsize=12)
    ax.set_xlabel("Coefficient Weight (Log Odds Impact)", weight='bold')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig('docs_assets/fig_feature_importance.png', bbox_inches='tight')
    plt.close()

# 11. Mockup UI / Output Screenshots
def make_ui_screenshots():
    # 11.1 Input dataset preview table image
    fig, ax = plt.subplots(figsize=(11, 4), dpi=300)
    ax.axis('off')
    sub_df = df[['product_name', 'category', 'platform', 'price', 'discount', 'rating', 'availability']].head(8)
    sub_df['price'] = sub_df['price'].apply(lambda x: f"₹{int(x):,}")
    sub_df['discount'] = sub_df['discount'].apply(lambda x: f"{x}%")
    table = ax.table(cellText=sub_df.values, colLabels=sub_df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.1, 1.8)
    for k, cell in table._cells.items():
        if k[0] == 0:
            cell.set_facecolor('#2B6CB0')
            cell.set_text_props(color='white', weight='bold')
        elif k[0] % 2 == 1:
            cell.set_facecolor('#EDF2F7')
    ax.set_title("Figure 8.1: PriceWise Input Dataset Snapshot (Sample Rows)", weight='bold', fontsize=12, pad=15)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_input_dataset.png', bbox_inches='tight')
    plt.close()

    # 11.2 Preprocessing steps image
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.axis('off')
    stages = [
        ("1. Raw Scraping", "1,540 Raw Offers\nDuplicate keys & NA\nUnstandardized prices", "#4A5568"),
        ("2. Cleaning & Typing", "Currency symbol purge\nFloat & Int conversions\nDate formatting YYYY-MM-DD", "#3182CE"),
        ("3. Deduplication", "Product + Platform unique\nPreserve lowest price\nDrop exact duplicates", "#38A169"),
        ("4. Imputation & Scaling", "Zero/median rating fill\nMin-Max feature bounds\nCategorical One-Hot", "#D69E2E"),
        ("5. Clean Storage", "1,500 Valid Offers\n10 Standard Columns\nAnalytics-ready CSV", "#805AD5")
    ]
    for i, (title, desc, color) in enumerate(stages):
        x = 0.1 + i * 0.2
        ax.text(x, 0.65, title, ha='center', va='center', color='white', weight='bold',
                bbox=dict(boxstyle='square,pad=0.6', facecolor=color, edgecolor='none'), fontsize=9)
        ax.text(x, 0.35, desc, ha='center', va='center', color='#2D3748',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#F7FAFC', edgecolor=color, lw=1.5), fontsize=8)
        if i < len(stages) - 1:
            ax.annotate('', xy=(x + 0.08, 0.65), xytext=(x + 0.04, 0.65),
                        arrowprops=dict(arrowstyle="->", lw=2, color='#718096'))
    ax.set_title("Figure 8.2: Data Pipeline Transformation and Preprocessing Stages", weight='bold', fontsize=12, pad=15)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_preprocessing_pipeline.png', bbox_inches='tight')
    plt.close()

    # 11.3 Streamlit UI Home Mockup
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.axis('off')
    # Background card
    ax.fill([0, 10, 10, 0], [0, 0, 6, 6], color='#F8FAFC', ec='#CBD5E1', lw=1.5)
    # Header bar
    ax.fill([0, 10, 10, 0], [5.2, 5.2, 6, 6], color='#1E293B')
    ax.text(0.5, 5.6, "🛒 PriceWise — Intelligent Product Search & Price Comparison", color='white', weight='bold', fontsize=12, va='center')
    # Search box
    ax.fill([0.5, 7.5, 7.5, 0.5], [4.4, 4.4, 4.9, 4.9], color='white', ec='#94A3B8', lw=1)
    ax.text(0.7, 4.65, "🔍 Search e.g. iPhone 16, Sony Headphones, Dell XPS...", color='#64748B', fontsize=9, va='center')
    ax.fill([7.7, 9.5, 9.5, 7.7], [4.4, 4.4, 4.9, 4.9], color='#2563EB')
    ax.text(8.6, 4.65, "Search Deals", color='white', weight='bold', fontsize=9, va='center', ha='center')
    # Filter tags
    ax.text(0.5, 4.0, "Category: [Electronics ▼]   Platform: [All Platforms ▼]   Max Price: [₹1,50,000]", fontsize=9, color='#334155', weight='bold')
    # Product card 1
    ax.fill([0.5, 9.5, 9.5, 0.5], [2.2, 2.2, 3.7, 3.7], color='white', ec='#E2E8F0', lw=1)
    ax.text(0.8, 3.2, "Apple iPhone 16 (128 GB) — Electronics", weight='bold', fontsize=11, color='#0F172A')
    ax.text(0.8, 2.7, "Lowest Price: ₹74,900 on Amazon   |   Original: ₹79,900   |   Discount: 6.3%   |   Rating: ⭐ 4.6/5.0", fontsize=9, color='#334155')
    ax.fill([7.8, 9.2, 9.2, 7.8], [2.4, 2.4, 2.9, 2.9], color='#16A34A')
    ax.text(8.5, 2.65, "Compare Prices", color='white', weight='bold', fontsize=8, va='center', ha='center')
    # Product card 2
    ax.fill([0.5, 9.5, 9.5, 0.5], [0.4, 0.4, 1.9, 1.9], color='white', ec='#E2E8F0', lw=1)
    ax.text(0.8, 1.4, "Sony WH-1000XM5 Wireless Noise Cancelling — Audio", weight='bold', fontsize=11, color='#0F172A')
    ax.text(0.8, 0.9, "Lowest Price: ₹26,990 on Croma   |   Original: ₹29,990   |   Discount: 10.0%   |   Rating: ⭐ 4.7/5.0", fontsize=9, color='#334155')
    ax.fill([7.8, 9.2, 9.2, 7.8], [0.6, 0.6, 1.1, 1.1], color='#16A34A')
    ax.text(8.5, 0.85, "Compare Prices", color='white', weight='bold', fontsize=8, va='center', ha='center')
    ax.set_title("Figure 8.3: PriceWise Web Interface — Home & Search Dashboard", weight='bold', fontsize=12, pad=15)
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-0.2, 6.4)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_ui_home.png', bbox_inches='tight')
    plt.close()

    # 11.4 Streamlit UI Compare Mockup
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.axis('off')
    ax.fill([0, 10, 10, 0], [0, 0, 6, 6], color='#F8FAFC', ec='#CBD5E1', lw=1.5)
    # Header
    ax.fill([0, 10, 10, 0], [5.2, 5.2, 6, 6], color='#1E293B')
    ax.text(0.5, 5.6, "📊 Price Comparison — Apple iPhone 16 (128 GB)", color='white', weight='bold', fontsize=12, va='center')
    # Metrics
    metrics = [("Lowest Price", "₹74,900", "#16A34A"), ("Average Price", "₹77,420", "#2563EB"), ("Max Saving", "₹5,000 (6.3%)", "#D97706"), ("Best Platform", "Amazon", "#9333EA")]
    for i, (m_title, m_val, m_col) in enumerate(metrics):
        x = 0.5 + i * 2.3
        ax.fill([x, x+2.1, x+2.1, x], [4.0, 4.0, 4.9, 4.9], color='white', ec=m_col, lw=1.5)
        ax.text(x+1.05, 4.6, m_title, ha='center', fontsize=8, color='#64748B')
        ax.text(x+1.05, 4.25, m_val, ha='center', fontsize=11, weight='bold', color=m_col)
    # Comparison table / bar
    ax.text(0.5, 3.5, "Live Platform Offers Breakdown:", weight='bold', fontsize=10, color='#0F172A')
    offers = [
        ("Amazon", "₹74,900", "₹79,900", "6.3% off", "⭐ 4.6", "Best Deal"),
        ("Flipkart", "₹75,499", "₹79,900", "5.5% off", "⭐ 4.5", "Good"),
        ("Croma", "₹77,900", "₹79,900", "2.5% off", "⭐ 4.4", "Average"),
        ("Reliance Digital", "₹78,900", "₹79,900", "1.3% off", "⭐ 4.3", "Average"),
        ("Tata CLiQ", "₹79,900", "₹79,900", "0.0% off", "⭐ 4.2", "Poor")
    ]
    for j, (plat, pr, orig, disc, rat, tier) in enumerate(offers):
        y = 2.9 - j * 0.5
        ax.fill([0.5, 9.5, 9.5, 0.5], [y, y, y+0.42, y+0.42], color='white' if j%2==0 else '#F1F5F9', ec='#E2E8F0')
        ax.text(0.8, y+0.21, plat, weight='bold', fontsize=9, va='center')
        ax.text(2.6, y+0.21, pr, weight='bold', fontsize=9, va='center', color='#16A34A')
        ax.text(4.2, y+0.21, f"Orig: {orig}", fontsize=8, va='center', color='#64748B')
        ax.text(5.8, y+0.21, disc, fontsize=8, va='center', color='#2563EB')
        ax.text(7.2, y+0.21, rat, fontsize=8, va='center')
        badge_col = '#16A34A' if tier=='Best Deal' else ('#2563EB' if tier=='Good' else '#94A3B8')
        ax.text(8.7, y+0.21, tier, weight='bold', fontsize=8, va='center', color=badge_col)
    ax.set_title("Figure 8.4: Multi-Platform Price Comparison Dashboard View", weight='bold', fontsize=12, pad=15)
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-0.2, 6.4)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_ui_compare.png', bbox_inches='tight')
    plt.close()

    # 11.5 Streamlit UI ML Prediction Mockup
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.axis('off')
    ax.fill([0, 10, 10, 0], [0, 0, 6, 6], color='#F8FAFC', ec='#CBD5E1', lw=1.5)
    ax.fill([0, 10, 10, 0], [5.2, 5.2, 6, 6], color='#1E293B')
    ax.text(0.5, 5.6, "🤖 Machine Learning Deal Quality Classifier", color='white', weight='bold', fontsize=12, va='center')
    
    # Form box
    ax.fill([0.5, 5.0, 5.0, 0.5], [0.8, 0.8, 4.8, 4.8], color='white', ec='#CBD5E1', lw=1)
    ax.text(0.8, 4.4, "Product Deal Evaluator Inputs", weight='bold', fontsize=10, color='#0F172A')
    ax.text(0.8, 3.8, "Category: Electronics", fontsize=9, color='#334155')
    ax.text(0.8, 3.2, "Platform: Amazon", fontsize=9, color='#334155')
    ax.text(0.8, 2.6, "Discount (%): 18.5%", fontsize=9, color='#334155')
    ax.text(0.8, 2.0, "Rating: 4.6 / 5.0", fontsize=9, color='#334155')
    ax.fill([0.8, 4.7, 4.7, 0.8], [1.1, 1.1, 1.6, 1.6], color='#2563EB')
    ax.text(2.75, 1.35, "Predict Deal Quality", color='white', weight='bold', fontsize=9, va='center', ha='center')
    
    # Result Card
    ax.fill([5.4, 9.5, 9.5, 5.4], [0.8, 0.8, 4.8, 4.8], color='#F0FDF4', ec='#22C55E', lw=2)
    ax.text(7.45, 4.3, "PREDICTION RESULT", ha='center', weight='bold', fontsize=11, color='#15803D')
    ax.text(7.45, 3.5, "🎉 GOOD DEAL!", ha='center', weight='bold', fontsize=18, color='#16A34A')
    ax.text(7.45, 2.8, "Model Confidence: 89.4%", ha='center', weight='bold', fontsize=11, color='#15803D')
    ax.text(7.45, 2.2, "• Price is substantially below platform median\n• High customer rating score (> 4.5)\n• Strong competitive discount tier",
            ha='center', fontsize=8, color='#166534')
    ax.fill([6.0, 8.9, 8.9, 6.0], [1.1, 1.1, 1.6, 1.6], color='#16A34A')
    ax.text(7.45, 1.35, "Proceed to Store Offer", color='white', weight='bold', fontsize=9, va='center', ha='center')
    
    ax.set_title("Figure 8.5: Machine Learning Deal Quality Prediction UI Result", weight='bold', fontsize=12, pad=15)
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-0.2, 6.4)
    plt.tight_layout()
    plt.savefig('docs_assets/fig_ui_ml_prediction.png', bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    print("Generating flowchart & architecture...")
    make_flowchart()
    make_architecture()
    print("Generating EDA charts...")
    make_bar_graphs()
    make_pie_chart()
    make_histogram()
    make_box_plot()
    make_line_chart()
    make_scatter_plot()
    make_project_specific()
    make_deal_score_chart()
    print("Generating ML charts...")
    make_ml_eval_charts()
    print("Generating UI mockups & pipeline visuals...")
    make_ui_screenshots()
    print("All charts generated successfully in docs_assets/!")
