#!/usr/bin/env python3
import os
import re
import io
import requests
from PIL import Image

IGNORE_MEDIA_IDS = {
    '0fdef751204647a3bbd7eaa2827ed4f9.png',
    '11062b_ca1d837ce7194421b781ee7384061a8e~mv2.png',
    'c00ea0_abc869958c81485e861d1b511202a977~mv2.jpg'
}

PAGES = [
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/hindelveston-extension',
        'prefix': 'project-hindolveston'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/the-rise-sheringham',
        'prefix': 'project-therise'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/cromer-conversion',
        'prefix': 'project-norwichroad'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/oakwood-house-extensions-norfolk',
        'prefix': 'service-extensions'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/conversions-north-norfolk',
        'prefix': 'service-conversions'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/bathrooms-north-norfolk',
        'prefix': 'service-bathrooms'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/kitchens-north-norfolk',
        'prefix': 'service-kitchens'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/windows-north-norfolk',
        'prefix': 'service-windows'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/roofing-north-norfolk',
        'prefix': 'service-roofing'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/plumbing-heating-north-norfolk',
        'prefix': 'service-plumbing'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/underfloor-heating-north-norfolk',
        'prefix': 'service-ufh'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/landscaping-north-norfolk',
        'prefix': 'service-landscaping'
    },
    {
        'url': 'https://www.oakwoodbuildingservicesnorfolk.co.uk/',
        'prefix': 'homepage'
    }
]

HOMEPAGE_SERVICE_MAPPING = [
    'service-renovations',
    'service-electrical',
    'service-pointing',
    'service-plastering',
    'service-damp',
    'service-landscaping'
]

def extract_media_ids(html_text):
    matches = re.findall(r'static\.wixstatic\.com/media/([a-zA-Z0-9_~\-]+\.[a-zA-Z0-9]+)', html_text)
    cleaned = []
    for m in matches:
        media_id = m.split('/')[0]
        if media_id not in IGNORE_MEDIA_IDS and media_id not in cleaned:
            cleaned.append(media_id)
    return cleaned

def download_and_convert(media_id, output_path, quality=82):
    if os.path.exists(output_path):
        print(f"Skipping existing file: {output_path}")
        return True

    url = f"https://static.wixstatic.com/media/{media_id}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

            img.save(output_path, "WEBP", quality=quality)
            print(f"Saved: {output_path} (from {media_id})")
            return True
        else:
            print(f"Failed to fetch {url}: status {r.status_code}")
            return False
    except Exception as e:
        print(f"Error processing {media_id}: {e}")
        return False

def main():
    os.makedirs("images", exist_ok=True)
    downloaded_media = set()

    for page in PAGES:
        print(f"\nCrawling {page['url']} ...")
        try:
            r = requests.get(page['url'], timeout=15)
            if r.status_code != 200:
                print(f"Failed to load page {page['url']}: {r.status_code}")
                continue

            media_ids = extract_media_ids(r.text)
            print(f"Found {len(media_ids)} media IDs for prefix '{page['prefix']}'")

            prefix = page['prefix']

            if prefix == 'homepage':
                for idx, media_id in enumerate(media_ids):
                    if media_id in downloaded_media:
                        continue
                    downloaded_media.add(media_id)

                    service_name = HOMEPAGE_SERVICE_MAPPING[idx % len(HOMEPAGE_SERVICE_MAPPING)]
                    count = 1
                    filename = f"images/{service_name}.webp"
                    while os.path.exists(filename):
                        count += 1
                        filename = f"images/{service_name}-{count}.webp"

                    download_and_convert(media_id, filename)
            else:
                for idx, media_id in enumerate(media_ids):
                    if media_id in downloaded_media:
                        continue
                    downloaded_media.add(media_id)

                    if idx == 0:
                        filename = f"images/{prefix}.webp"
                    else:
                        filename = f"images/{prefix}-{idx + 1}.webp"

                    if os.path.exists(filename):
                        count = idx + 1
                        while os.path.exists(f"images/{prefix}-{count}.webp"):
                            count += 1
                        filename = f"images/{prefix}-{count}.webp"

                    download_and_convert(media_id, filename)

        except Exception as e:
            print(f"Error crawling {page['url']}: {e}")

if __name__ == "__main__":
    main()
