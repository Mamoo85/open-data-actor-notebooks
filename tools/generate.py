"""Generate one Colab notebook per actor from the shared catalog + sample inputs."""
import json, sys, pathlib, pprint
import nbformat as nbf

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHARED = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("C:/gng/lanes/apify/distribution/repos/_shared")
USER = "transparent_meteorite"
REPO = "Mamoo85/open-data-actor-notebooks"

# slug -> (display columns, analysis code, privacy note or None)
CFG = {
"amazon-product-search": (["asin","title","brand","price","rating","reviewCount","isPrime","boughtInPastMonth"],
 "df['price']=pd.to_numeric(df['price'],errors='coerce')\nprint(df.groupby('brand')['price'].agg(['count','mean']).sort_values('count',ascending=False).head(10))\nprint('Top by review count:')\ndf.sort_values('reviewCount',ascending=False)[['title','reviewCount','rating']].head(5)", None),
"app-store-reviews": (["type","appName","title","rating","version","date","developer","genre","ratingAverage"],
 "rev=df[df['type']=='review'].copy()\nrev['rating']=pd.to_numeric(rev['rating'],errors='coerce')\nprint(rev['rating'].value_counts().sort_index())\nprint('Mean rating of sampled reviews:',round(rev['rating'].mean(),2))",
 "Review author names are dropped from the table; only ratings and review-level fields are shown."),
"ats-open-roles": (["company","ats","title","department","location","seniority","postedAt"],
 "print(df.groupby('company').size().rename('open roles in sample'))\nprint(df['seniority'].value_counts(dropna=False))\ndf['department'].value_counts().head(10)", None),
"building-permits-leads": (["city","state","permitType","status","issueDate","valuation","propertyAddress"],
 "df['valuation']=pd.to_numeric(df['valuation'],errors='coerce')\ndf.groupby('city')['valuation'].agg(['count','sum','max'])",
 "Contractor/applicant columns are not displayed; property-level fields only."),
"city-council-agendas": (["city","body","meetingDate","agendaStatus","title","matterType","meetingUrl"],
 "print(df['body'].value_counts())\ndf['meetingDate'].value_counts().sort_index()", None),
"company-enrichment-by-domain": (["domain","status","companyName","description","language","emailProvider","spfPresent","pagesFetched","techCount"],
 "print(df[['domain','techCount']])\nprint(df['emailProvider'].value_counts(dropna=False))",
 "Email, phone and social-handle columns are dropped before display; only company-level fields are shown."),
"company-news-monitor": (["title","sourceName","publishedAt","country","sentiment","matchedKeywords"],
 "print(df['sentiment'].value_counts(dropna=False))\ndf['sourceName'].value_counts().head(10)", None),
"developer-signals": (["source","recordType","kind","title","domain","createdAt","points","numComments","packageName","latestVersion","downloadsLastMonth"],
 "pk=df[df['recordType']=='package'].copy()\npk['downloadsLastMonth']=pd.to_numeric(pk['downloadsLastMonth'],errors='coerce')\nprint('Package downloads, last month:')\nprint(pk[['packageName','downloadsLastMonth']].sort_values('downloadsLastMonth',ascending=False).to_string(index=False))\nst=df[df['recordType']=='story'].copy()\nst['points']=pd.to_numeric(st['points'],errors='coerce')\nst.sort_values('points',ascending=False)[['title','points','numComments']].head(5)",
 "Post author handles are dropped from the table."),
"domain-intelligence-lookup": (["domain","registered","registrar","ageDays","hasSpf","hasDmarc","dmarcPolicy","sslIssuer","sslDaysLeft","securityHeadersScore","subdomainCount"],
 "for c in ['ageDays','sslDaysLeft','securityHeadersScore','subdomainCount']:\n    df[c]=pd.to_numeric(df[c],errors='coerce')\nprint(df[['domain','ageDays','sslDaysLeft','securityHeadersScore']].sort_values('ageDays',ascending=False).to_string(index=False))\nprint('DMARC policies:',df['dmarcPolicy'].value_counts(dropna=False).to_dict())", None),
"federal-grants-contracts": (["source","recordType","title","agency","status","postedDate","closeDate","amountCeiling","amount","recipient"],
 "df['best_amount']=pd.to_numeric(df['amount'].fillna(df['amountCeiling']),errors='coerce')\nprint(df.groupby('recordType')['best_amount'].agg(['count','sum']))\ndf.sort_values('best_amount',ascending=False)[['title','agency','best_amount']].head(5)", None),
"fmcsa-new-carrier-leads": (["usdot","city","state","power_units","total_drivers","carrier_operation_label","census_status","registered_date_iso"],
 "for c in ['power_units','total_drivers']:\n    df[c]=pd.to_numeric(df[c],errors='coerce')\nprint(df['state'].value_counts())\nprint('Median fleet (power units):',df['power_units'].median())\ndf['carrier_operation_label'].value_counts(dropna=False)",
 "Carrier legal names, officers, emails and phone numbers are NOT displayed (they can identify individual owner-operators). Only the USDOT number and company-level fields are shown."),
"linkedin-public-jobs": (["title","company","location","postedAt","seniority","employmentType","applicantsText","companySize","companyIndustry"],
 "print(df['company'].value_counts().head(10))\nprint(df['seniority'].value_counts(dropna=False))\ndf['employmentType'].value_counts(dropna=False)", None),
"local-business-leads": (["name","category","city","state","postcode","website","openingHours","googleMapsUrl"],
 "print(df['category'].value_counts())\nprint('With a website:', int(df['website'].notna().sum()), 'of', len(df))\ndf['postcode'].value_counts().head(10)",
 "Phone and email columns are dropped before display; business name, category, address and website are shown."),
"meta-ad-library": (["pageName","isActive","startDate","daysRunning","platforms","ctaText","displayFormat","mediaType","variationsCount"],
 "df['daysRunning']=pd.to_numeric(df['daysRunning'],errors='coerce')\nprint(df['displayFormat'].value_counts(dropna=False))\ndf.sort_values('daysRunning',ascending=False)[['pageName','daysRunning','ctaText']].head(5)", None),
"new-business-filings": (["entityName","state","filingDate","entityType","status","entityId"],
 "print(df['state'].value_counts())\ndf['entityType'].value_counts(dropna=False)",
 "Registered-agent names and addresses are not displayed (agents are often individuals)."),
"sanctions-screening": (["query_no","status","bestScore","matchCount","topMatchList","topMatchPrograms","listsChecked"],
 "df['bestScore']=pd.to_numeric(df['bestScore'],errors='coerce')\nprint(df['status'].value_counts())\nprint(df[['query_no','status','bestScore']].to_string(index=False))\nprint('Screening aid only; a possible match is a prompt for human review, not a determination.')",
 "Screened names are replaced by 'name #N' and matched entity names are not displayed, so no person names are stored in this notebook's output."),
"sec-form-d-funding-leads": (["entityName","entityType","issuerState","filingDate","industryGroup","totalOfferingAmount","totalAmountSold","numberOfInvestors","revenueRange"],
 "for c in ['totalOfferingAmount','totalAmountSold','numberOfInvestors']:\n    df[c]=pd.to_numeric(df[c],errors='coerce')\nprint(df['industryGroup'].value_counts())\ndf.sort_values('totalOfferingAmount',ascending=False)[['entityName','totalOfferingAmount','totalAmountSold']].head(5)",
 "Phone numbers and related-person (executive/director) data are not displayed; issuer-level fields only."),
"shopify-store-leads": (["storeName","primaryDomain","isShopify","country","province","currency","publishedProductsCount","appCount","themeName","priceMedian","productsOnSalePct"],
 "for c in ['publishedProductsCount','appCount','priceMedian']:\n    df[c]=pd.to_numeric(df[c],errors='coerce')\nprint(df[['storeName','publishedProductsCount','appCount','priceMedian']].to_string(index=False))\nfor _,r in df.iterrows(): print(r['storeName'],'-> apps:',r['appsDetected'])",
 "Email, phone and social contact columns are dropped before display; store-level fields only."),
"sitemap-link-inventory": (["site","url","pathGroup","pathDepth","priority","changefreq","checked","statusCode","responseMs"],
 "df['responseMs']=pd.to_numeric(df['responseMs'],errors='coerce')\nprint(df['statusCode'].value_counts(dropna=False))\nprint(df['pathGroup'].value_counts().head(10))\nprint('Median response (ms):',df['responseMs'].median())", None),
"technical-seo-page-audit": (["url","statusCode","score","ttfbMs","title","titleLength","metaDescriptionLength","h1Count","wordCount","brokenLinkCount","indexable"],
 "r=df.iloc[0]\nprint('Score:',r['score'])\nprint('Issue counts:',r.get('issueCounts'))\nfor i in (r.get('issues') or [])[:8]:\n    print('-',i if isinstance(i,str) else (i.get('message') or i))", None),
"warn-layoff-alerts": (["company","city","county","state","layoff_count","notice_date","layoff_date","wda"],
 "df['layoff_count']=pd.to_numeric(df['layoff_count'],errors='coerce')\nprint('Total workers in sample:',int(df['layoff_count'].sum()))\ndf.groupby('city')['layoff_count'].sum().sort_values(ascending=False)",
 "Company-level notices only; no contact data is displayed."),
"website-contact-extractor": (["domain","status","companyName","emailCount","phoneCount","hasContactPage","pagesCrawled","responded"],
 "df[['emailCount','phoneCount','pagesCrawled']]=df[['emailCount','phoneCount','pagesCrawled']].apply(pd.to_numeric,errors='coerce')\nprint('Share of sites exposing a contact page:', round(df['hasContactPage'].mean(),2))\ndf[['domain','emailCount','phoneCount','pagesCrawled']]",
 "Actual email addresses, phone numbers and named contacts are NOT displayed. Only counts and company-level fields are shown, so no personal data is stored in this notebook."),
"website-tech-stack-detector": (["url","status","title","server","n_technologies","categories"],
 "from collections import Counter\ncnt=Counter(t['name'] for ts in df['technologies'] if isinstance(ts,list) for t in ts)\nprint('Most common technologies:',cnt.most_common(8))", None),
"workday-jobs-scraper": (["company","title","location","country","remoteType","timeType","postedOn","salaryMin","salaryMax","salaryCurrency"],
 "for c in ['salaryMin','salaryMax']:\n    df[c]=pd.to_numeric(df[c],errors='coerce')\nprint(df.groupby('company').size().rename('roles in sample'))\nprint(df['remoteType'].value_counts(dropna=False))\ndf.groupby('company')[['salaryMin','salaryMax']].median()", None),
"google-maps-places-scraper": (["title","categoryName","city","state","totalScore","reviewsCount","website","claimedByOwner","permanentlyClosed","rank"],
 "for c in ['totalScore','reviewsCount']:\n    df[c]=pd.to_numeric(df[c],errors='coerce')\nprint(df['categoryName'].value_counts().head(8))\nprint('With a website:', int(df['website'].notna().sum()), 'of', len(df))\ndf.sort_values('reviewsCount',ascending=False)[['title','totalScore','reviewsCount']].head(10)",
 "Phone numbers and emails are dropped before display; business name, category, rating and website are shown."),
"tiktok-public-profile-scraper": (["account","createTimeISO","playCount","diggCount","commentCount","shareCount","engagementRate","isSponsored","text"],
 "for c in ['playCount','diggCount','commentCount','shareCount']:\n    df[c]=pd.to_numeric(df[c],errors='coerce')\nprint(df[['playCount','diggCount','commentCount','shareCount']].describe().loc[['count','mean','max']])\ndf.sort_values('playCount',ascending=False)[['account','playCount','diggCount']].head(5)",
 "Public posts of public accounts only. Contact columns (bio emails, linked socials) are dropped before display."),
"youtube-comments-scraper": (["videoTitle","text","likeCount","replyCount","isReply","hasCreatorHeart","isPinned","publishedAtApprox"],
 "for c in ['likeCount','replyCount']:\n    df[c]=pd.to_numeric(df[c],errors='coerce')\nprint('Comments:',len(df),'| mean likes:',round(df['likeCount'].mean(),1))\ndf.sort_values('likeCount',ascending=False)[['text','likeCount','replyCount']].head(5)",
 "Commenter names, handles and channel links are dropped before display; comment text and engagement counts are shown."),
"amazon-bestsellers": (["rank","asin","title","price","currency","stars","reviewsCount","listType","category","countryCode"],
 "for c in ['rank','price','stars','reviewsCount']:\n    df[c]=pd.to_numeric(df[c],errors='coerce')\nprint(df.groupby('listType')['price'].agg(['count','median']))\ndf.sort_values('rank')[['rank','title','price','stars','reviewsCount']].head(10)", None),
"sam-gov-opportunities": (["title","solicitationNumber","noticeType","postedDate","responseDeadline","department","naicsCode","pscCode","setAside","samUrl"],
 "print(df['noticeType'].value_counts())\nprint(df['department'].value_counts().head(8))\ndf.sort_values('responseDeadline')[['title','department','responseDeadline']].head(10)",
 "Contracting-officer names, emails and phone numbers are not displayed; notice-level fields only."),
}

# Columns whose name contains one of these are dropped from every DataFrame before display
DROP_PAT = ["email", "phone", "author", "registeredagent", "contractor", "officer",
            "linkedin", "facebook", "instagram", "youtube", "tiktok", "socials", "twitter"]
KEEP = ["emailCount", "phoneCount", "emailProvider"]


def make(a, sample):
    slug, title = a["slug"], a["title"].split(":")[0]
    cols, analysis, privacy = CFG[slug]
    store = f"https://apify.com/{USER}/{slug}"
    colab = f"https://colab.research.google.com/github/{REPO}/blob/main/notebooks/{slug}.ipynb"
    badge = f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab})"
    desc = a["description"].split(". 1")[0].rstrip(".")
    md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
    cells = []
    priv_md = f"\n\n**Privacy:** {privacy}" if privacy else ""
    cells.append(md(f"# {title}\n\n{badge}\n\n**What:** {desc}.\n\n**Why:** run the [`{slug}`]({store}) Apify actor from Python and analyse the result as a pandas DataFrame, with no scraping code to maintain.\n\n> **Disclosure:** I am the author of this actor. It is pay-per-result; the free plan credit on a new Apify account covers a trial run like this one (this notebook uses a very small sample input)." + priv_md))
    cells.append(md("## 1. Setup"))
    cells.append(code(
"""!pip install -q apify-client pandas

import os, getpass
try:
    from google.colab import userdata
    APIFY_TOKEN = userdata.get('APIFY_TOKEN')          # Colab: add it under the key icon (Secrets)
except Exception:
    APIFY_TOKEN = os.environ.get('APIFY_TOKEN') or getpass.getpass('Apify API token: ')
assert APIFY_TOKEN, 'An Apify API token is required (a free account is enough).'
print('Token loaded.')"""))
    cells.append(md("## 2. Input\nA deliberately small sample so the run is cheap and quick. See the [actor page](" + store + ") for every option."))
    cells.append(code("run_input = " + pprint.pformat(sample, indent=4, width=100, sort_dicts=False)))
    cells.append(md("## 3. Run the actor and read the dataset"))
    cells.append(code(
f"""from apify_client import ApifyClient

client = ApifyClient(APIFY_TOKEN)
run = client.actor('{USER}/{slug}').call(run_input=run_input)
# apify-client v2 returns a dict, v3 a Run object; handle both
get = (lambda k, a: run[k]) if isinstance(run, dict) else (lambda k, a: getattr(run, a))
items = list(client.dataset(get('defaultDatasetId', 'default_dataset_id')).iterate_items())
print('Run status:', get('status', 'status'), '| items:', len(items))"""))
    cells.append(md("## 4. Tabulate" + ("\n\n" + privacy if privacy else "")))
    pre = ""
    if slug == "sanctions-screening":
        pre = "df['query_no'] = ['name #%d' % (i + 1) for i in range(len(df))]\n"
    if slug == "website-contact-extractor":
        pre += "df['hasContactPage'] = df['contactPageUrl'].notna()\n"
    if slug == "company-enrichment-by-domain":
        pre += "df['techCount'] = df['techStack'].apply(lambda t: t.get('count') if isinstance(t, dict) else None)\n"
    if slug == "tiktok-public-profile-scraper":
        pre += "df['account'] = df['authorMeta'].apply(lambda a: a.get('name') if isinstance(a, dict) else None)\n"
    if slug == "website-tech-stack-detector":
        pre += ("df['n_technologies'] = df['technologies'].apply(lambda t: len(t) if isinstance(t, list) else 0)\n"
                "df['categories'] = df['categoriesSummary'].apply(lambda c: ', '.join(sorted(c)) if isinstance(c, dict) else '')\n"
                "TECH = df['technologies'].copy()\n")
    cells.append(code(
f"""import pandas as pd
pd.set_option('display.max_colwidth', 70)
pd.set_option('display.width', 200)

df = pd.DataFrame(items)
{pre}
# Privacy: remove contact / personal-data columns before anything is displayed
DROP = {json.dumps(DROP_PAT)}
KEEP = {json.dumps(KEEP)}
df = df[[c for c in df.columns if c in KEEP or not any(p in c.lower() for p in DROP)]]
SHOW = [c for c in {json.dumps(cols)} if c in df.columns]
df[SHOW]"""))
    cells.append(md("## 5. A quick analysis"))
    if slug == "website-tech-stack-detector":
        analysis = analysis.replace("df['technologies']", "TECH")
    cells.append(code(analysis))
    cells.append(md(f"## Next steps\n\n- Raise the limits in the input cell to run a larger sample.\n- Schedule the actor or call it from your own pipeline: [{slug} on the Apify Store]({store}).\n- Check the Store page for the current pay-per-result price before scaling up.\n\nGenerated by `tools/generate.py`."))
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata = {"colab": {"name": f"{slug}.ipynb", "provenance": []},
                   "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    return nb


def main():
    cat = json.load(open(SHARED / "catalog.json", encoding="utf-8"))
    samples = json.load(open(SHARED / "sample_inputs.json", encoding="utf-8"))
    out = ROOT / "notebooks"
    out.mkdir(exist_ok=True)
    for a in cat:
        nbf.write(make(a, samples[a["slug"]]), out / f"{a['slug']}.ipynb")
    print("wrote", len(cat))
    json.dump([{"slug": a["slug"], "title": a["title"].split(":")[0],
                "desc": a["description"].split(". 1")[0].rstrip(".")} for a in cat],
              open(ROOT / "tools" / "actors.json", "w"), indent=1)


if __name__ == "__main__":
    main()
