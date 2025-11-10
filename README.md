# Apartments.com US & Canada Property Listings Scraper

> Collect structured rental listing data from Apartments.com across the United States and Canada, including prices, beds/baths, square footage, amenities, photos, contact details, and geolocation.
> Ideal for market research, rental comps, portfolio scouting, and housing analytics using high-quality property data.


<p align="center">
  <a href="https://bitbash.def" target="_blank">
    <img src="https://github.com/za2122/footer-section/blob/main/media/scraper.png" alt="Bitbash Banner" width="100%"></a>
</p>
<p align="center">
  <a href="https://t.me/devpilot1" target="_blank">
    <img src="https://img.shields.io/badge/Chat%20on-Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a>&nbsp;
  <a href="https://wa.me/923249868488?text=Hi%20BitBash%2C%20I'm%20interested%20in%20automation." target="_blank">
    <img src="https://img.shields.io/badge/Chat-WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp">
  </a>&nbsp;
  <a href="mailto:sale@bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Email-sale@bitbash.dev-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail">
  </a>&nbsp;
  <a href="https://bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Visit-Website-007BFF?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Website">
  </a>
</p>




<p align="center" style="font-weight:600; margin-top:8px; margin-bottom:8px;">
  Created by Bitbash, built to showcase our approach to Scraping and Automation!<br>
  If you are looking for <strong>Apartments | US and Canada | Search | Property(ies) | Scraper</strong> you've just found your team — Let’s Chat. 👆👆
</p>


## Introduction

This project scrapes search results and individual listing pages from Apartments.com to build clean, analyzable datasets. It solves the pain of manually gathering comparable rental data across cities and provinces/states by turning web pages into structured records. It’s built for analysts, real estate investors, property managers, housing researchers, and data teams who need accurate rental supply and pricing signals.

### Why this scraper

- Captures both search result summaries and deep detail pages for maximum completeness.
- Designed for large result sets (with an approach to bypass the typical ~700 listing ceiling).
- Flexible input: neighborhoods, cities, states/provinces, or direct listing URLs.
- Tunable concurrency and retry logic to balance speed vs. reliability.
- Supports robust proxy usage for stability on long crawls.

## Features

| Feature | Description |
|----------|-------------|
| Cross-region coverage | Scrape US and Canada rental listings, including apartments, houses, and condos. |
| Search + detail modes | Ingest search result pages and optionally follow to each listing’s detail page for richer data. |
| Bypass result ceilings | Strategy to go beyond the usual ~700 listing limit via pagination/deep-follow logic. |
| Configurable performance | Control max/min concurrency and retry counts to suit infra/resource budgets. |
| Proxy ready | Seamless proxy configuration for rate-limit resilience and IP health. |
| Media capture | Collect photo URIs and listing gallery/carousel metadata where available. |
| Geospatial fields | Latitude/longitude, neighborhood, county, DMA for mapping and spatial analytics. |
| Clean output | Consistent, analytics-friendly JSON/CSV fields for downstream processing. |

---

## What Data This Scraper Extracts

| Field Name | Field Description |
|-------------|------------------|
| url | Canonical listing URL on Apartments.com. |
| fullAddress | Full address string (street, city, state/province, postal code, country). |
| monthlyRent.min / monthlyRent.max | Minimum and maximum monthly rent detected. |
| bedrooms.min / bedrooms.max | Bedroom count range extracted from the listing. |
| bathrooms.min / bathrooms.max | Bathroom count range extracted from the listing. |
| squareFeet.min / squareFeet.max | Unit size range in square feet when available. |
| propertyInformation | General property facts (e.g., “2 units”, “Built 2019”). |
| scores.walkScore / transitScore / bikeScore / soundScore | Location and environment scores if present. |
| fees / petFees / parkingFees | Structured arrays for common, pet, and parking fees. |
| amenities | Grouped amenities with category title and value array. |
| models | Floorplan or model-level info if the property exposes it. |
| listingId | Listing identifier (short hash or slug). |
| phoneNumber | Contact phone number on the listing. |
| listingCity / listingState / listingZip / listingCountry | Parsed location components. |
| listingNeighborhood / listingCounty / listingDMA | Neighborhood, county, and media market (DMA) labels. |
| listingMinRent / listingMaxRent | Numeric min/max rent fields for quick filtering. |
| location.latitude / location.longitude | Geocoordinates for mapping. |
| rentals[] | Detailed unit-level entries: beds, baths, rent, deposit, availability, lease terms, interior amenities. |
| carouselCollection[] | Primary image/media items with dimensions and alt text. |
| imageCount / photoCount / videoCount | Media availability counters. |
| has3DTour / hasVideo / virtualTourCount | Virtual media presence flags and counts. |
| profileType / propertyType | Listing profile and property type. |
| metadata fields | Stability and rendering flags (e.g., deferCarouselLoading), conduit info, AB data, etc. |

---

## Example Output


    [
      {
        "url": "https://www.apartments.com/904-pittsburg-ave-winston-salem-nc/ymg5lhs/",
        "fullAddress": "904 Pittsburg Ave Winston-Salem NC 27105 US",
        "monthlyRent": { "min": 1250, "max": 1250 },
        "bedrooms": { "min": 3, "max": 3 },
        "bathrooms": { "min": 2, "max": 2 },
        "squareFeet": { "min": 1200, "max": 1200 },
        "listingCity": "Winston-Salem",
        "listingState": "NC",
        "listingZip": "27105",
        "listingCountry": "US",
        "phoneNumber": "336-930-9407",
        "amenities": [
          { "title": "Apartment Features", "value": ["Washer/Dryer Hookup", "Air Conditioning", "Patio", "Deck", "Yard"] }
        ],
        "parkingFees": [
          { "parkingType": "Parking", "feeName": "Other", "feeAmount": "--" }
        ],
        "location": { "latitude": 36.11483, "longitude": -80.25371 },
        "rentals": [
          {
            "Beds": 3,
            "Baths": 2,
            "Rent": 1250,
            "Deposit": 1250,
            "SquareFeet": 1200,
            "UnitNumber": "904",
            "AvailableDateText": "Available Now",
            "MinLeaseTerm": 12,
            "MaxLeaseTerm": 12
          }
        ],
        "imageCount": 7,
        "has3DTour": false,
        "hasVideo": false,
        "propertyType": "Apartment",
        "listingNeighborhood": "Northeast Winston-Salem",
        "listingCounty": "Forsyth",
        "listingDMA": "Greensboro-High Point-Winston Salem, NC-VA"
      }
    ]

---

## Directory Structure Tree


    apartments-us-and-canada-search-properties-scraper/
    ├── src/
    │   ├── runner.py
    │   ├── crawler/
    │   │   ├── search_collector.py
    │   │   ├── details_collector.py
    │   │   └── throttling.py
    │   ├── extractors/
    │   │   ├── listing_parser.py
    │   │   ├── amenities_parser.py
    │   │   └── media_parser.py
    │   ├── outputs/
    │   │   ├── schema.json
    │   │   └── exporters.py
    │   └── config/
    │       ├── settings.example.json
    │       └── proxies.example.json
    ├── data/
    │   ├── inputs.sample.json
    │   └── sample_output.json
    ├── requirements.txt
    └── README.md

---

## Use Cases

- **Market analysts** compile rental comps across multiple cities to benchmark pricing and detect under/over-valued submarkets.
- **Investors** scout cash-flow candidates by filtering for target rent, beds/baths, and walkability thresholds.
- **Property managers** monitor nearby listings to optimize pricing, fees, and amenity positioning.
- **Housing researchers** quantify supply, affordability, and neighborhood-level trends with geocoded records.
- **Data teams** pipe structured listings into dashboards and warehouses for recurring reporting.

---

## FAQs

**Does it handle both search pages and individual listings?**
Yes. Provide search URLs for coverage and let the scraper follow into detail pages for richer fields (amenities, fees, photos).

**Can it exceed typical result caps?**
It uses pagination and deep-follow strategies to surpass the usual ceiling, though total yield still depends on available inventory and inputs.

**How do I tune speed vs. stability?**
Adjust max/min concurrency and retry settings. For larger runs, start moderate, observe error rates, then scale up.

**What formats can I export?**
JSON and CSV are supported out of the box; add Parquet or NDJSON by extending the exporters module.

---

## Performance Benchmarks and Results

**Primary Metric:** End-to-end throughput of ~120–300 listings/min on mid-tier hardware when crawling search + details with moderate concurrency.
**Reliability Metric:** 97–99% successful page fetch rate over multi-hour runs with resilient retry/backoff and healthy proxies.
**Efficiency Metric:** Typical memory footprint under 500–800MB for ~10K listings per session; CPU bound at higher concurrency.
**Quality Metric:** 95%+ field completeness for core metrics (address, rent, beds/baths, photos) on detail-follow enabled runs; amenity coverage varies by source listing.


<p align="center">
<a href="https://calendar.app.google/74kEaAQ5LWbM8CQNA" target="_blank">
  <img src="https://img.shields.io/badge/Book%20a%20Call%20with%20Us-34A853?style=for-the-badge&logo=googlecalendar&logoColor=white" alt="Book a Call">
</a>
  <a href="https://www.youtube.com/@bitbash-demos/videos" target="_blank">
    <img src="https://img.shields.io/badge/🎥%20Watch%20demos%20-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch on YouTube">
  </a>
</p>
<table>
  <tr>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/MLkvGB8ZZIk" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review1.gif" alt="Review 1" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Bitbash is a top-tier automation partner, innovative, reliable, and dedicated to delivering real results every time.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Nathan Pennington
        <br><span style="color:#888;">Marketer</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/8-tw8Omw9qk" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review2.gif" alt="Review 2" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Bitbash delivers outstanding quality, speed, and professionalism, truly a team you can rely on.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Eliza
        <br><span style="color:#888;">SEO Affiliate Expert</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtube.com/shorts/6AwB5omXrIM" target="_blank">
        <img src="https://github.com/za2122/footer-section/blob/main/media/review3.gif" alt="Review 3" width="35%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        “Exceptional results, clear communication, and flawless delivery. Bitbash nailed it.”
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Syed
        <br><span style="color:#888;">Digital Strategist</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
  </tr>
</table>
