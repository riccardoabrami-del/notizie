import os
import smtplib
import requests
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
from html import unescape
import re

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
FROM_EMAIL = "abramiriccardo4@gmail.com"
TO_EMAIL = "oscar.logoteta@we-wealth.com"
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

# Feed RSS reali e affidabili - aggiornati in tempo reale
RSS_FEEDS = [
    {"url": "https://techcrunch.com/feed/", "source": "TechCrunch"},
    {"url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "source": "Ars Technica"},
    {"url": "https://www.theverge.com/rss/index.xml", "source": "The Verge"},
    {"url": "https://feeds.feedburner.com/venturebeat/SZYF", "source": "VentureBeat"},
    {"url": "https://www.wired.com/feed/rss", "source": "Wired"},
]

def clean_html(text):
    """Rimuove tag HTML e decodifica entita' HTML"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_tech_news():
    """Recupera notizie tech reali dai feed RSS delle principali testate"""
    news = []
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'}

    for feed in RSS_FEEDS:
        if len(news) >= 5:
            break
        try:
            response = requests.get(feed["url"], timeout=15, headers=headers)
            response.raise_for_status()

            root = ET.fromstring(response.content)

            # Supporta sia RSS 2.0 (<channel><item>) che Atom (<entry>)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}

            # Prova formato RSS 2.0
            items = root.findall('.//item')

            # Se non trova item, prova formato Atom
            if not items:
                items = root.findall('.//atom:entry', ns)
                if not items:
                    items = root.findall('.//{http://www.w3.org/2005/Atom}entry')

            for item in items[:3]:
                if len(news) >= 5:
                    break

                # Titolo
                title_elem = item.find('title')
                if title_elem is None:
                    title_elem = item.find('{http://www.w3.org/2005/Atom}title')
                title = clean_html(title_elem.text) if title_elem is not None else ""

                if not title or len(title) < 10:
                    continue

                # Link
                link = ""
                link_elem = item.find('link')
                if link_elem is not None:
                    link = link_elem.text or link_elem.get('href', '')
                if not link:
                    link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                    if link_elem is not None:
                        link = link_elem.get('href', '')

                # Descrizione
                desc = ""
                for tag in ['description', 'summary', '{http://www.w3.org/2005/Atom}summary',
                             'content', '{http://www.w3.org/2005/Atom}content']:
                    desc_elem = item.find(tag)
                    if desc_elem is not None and desc_elem.text:
                        desc = clean_html(desc_elem.text)
                        break

                # Tronca descrizione a ~250 caratteri mantenendo frasi complete
                if len(desc) > 250:
                    desc = desc[:250].rsplit(' ', 1)[0] + '...'

                news.append({
                    'title': title,
                    'description': desc if desc else "Leggi l'articolo completo al link.",
                    'link': link.strip() if link else '',
                    'source': feed['source']
                })

            print(f"[{feed['source']}] trovate {len([n for n in news if n['source'] == feed['source']])} notizie")

        except Exception as e:
            print(f"Errore {feed['source']}: {e}")

    return news[:5]

def format_news_body(news_list):
    """Formatta le notizie per il corpo dell'email"""
    oggi = datetime.now(timezone(timedelta(hours=1))).strftime("%d/%m/%Y")
    body = f"NOTIZIE TECH DEL {oggi}\n"
    body += "=" * 40 + "\n\n"

    if not news_list:
        body += "Non e' stato possibile recuperare notizie al momento. Riprova piu' tardi."
    else:
        for idx, news in enumerate(news_list, 1):
            body += f"{idx}. {news['title'].upper()}\n"
            body += f"{news['description']}\n"
            body += f"Fonte: {news['source']}\n"
            body += f"Link: {news['link']}\n"
            if idx < len(news_list):
                body += "\n" + "-" * 40 + "\n\n"

    return body

def send_email():
    news_list = fetch_tech_news()
    oggi = datetime.now(timezone(timedelta(hours=1))).strftime("%d/%m/%Y")
    subject = f"Notizie Tech del {oggi}"
    body = format_news_body(news_list)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email inviata con successo a {TO_EMAIL}")
        print(f"Notizie inviate: {len(news_list)}")
        for n in news_list:
            print(f"  - [{n['source']}] {n['title']}")
        return True
    except Exception as e:
        print(f"Errore nell'invio dell'email: {e}")
        return False

if __name__ == "__main__":
    send_email()
