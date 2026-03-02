import os
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from datetime import datetime

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
FROM_EMAIL = "abramiriccardo4@gmail.com"
TO_EMAIL = "milanotoonight@gmail.com"
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

def fetch_tech_news():
    """
    Recupera le 5 notizie tech piu' rilevanti dalle ultime 24 ore
    """
    news = []
    
    # Notizie da Reuters Technology
    try:
        response = requests.get('https://www.reuters.com/technology/', timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('a', {'data-testid': 'Link'}, limit=10)
        for article in articles:
            if len(news) >= 5:
                break
            title_elem = article.find(['span', 'h3'])
            if title_elem:
                title = title_elem.get_text(strip=True)
                link = article.get('href', '')
                if title and len(title) > 15 and not link.startswith('#'):
                    if not link.startswith('http'):
                        link = 'https://www.reuters.com' + link
                    news.append({
                        'title': title,
                        'link': link,
                        'source': 'Reuters'
                    })
    except Exception as e:
        print(f"Errore Reuters: {e}")
    
    # Notizie da TechCrunch
    if len(news) < 5:
        try:
            response = requests.get('https://techcrunch.com/', timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('a', limit=20)
            for article in articles:
                if len(news) >= 5:
                    break
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if title and len(title) > 15 and 'techcrunch' in link.lower() and title not in [n['title'] for n in news]:
                    news.append({
                        'title': title,
                        'link': link,
                        'source': 'TechCrunch'
                    })
        except Exception as e:
            print(f"Errore TechCrunch: {e}")
    
    # Notizie da The Verge
    if len(news) < 5:
        try:
            response = requests.get('https://www.theverge.com/', timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('a', limit=20)
            for article in articles:
                if len(news) >= 5:
                    break
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if title and len(title) > 15 and not link.startswith('#') and title not in [n['title'] for n in news]:
                    if not link.startswith('http'):
                        link = 'https://www.theverge.com' + link
                    news.append({
                        'title': title,
                        'link': link,
                        'source': 'The Verge'
                    })
        except Exception as e:
            print(f"Errore The Verge: {e}")
    
    return news[:5]

def format_news_body(news_list):
    """
    Formatta le notizie nel corpo dell'email secondo il formato richiesto:
    TITOLO DELLA NOTIZIA
    Testo descrittivo una riga sola.
    Fonte: Nome Testata
    Link: URL
    """
    body = ""
    
    if not news_list:
        body = "Non e' stato possibile recuperare notizie al momento."
    else:
        for idx, news in enumerate(news_list, 1):
            # Titolo in MAIUSCOLO
            title_upper = news['title'].upper()
            
            # Testo descrittivo (usa il dominio come descrizione breve)
            description = f"Ultima notizia da {news['source']}"
            
            # Formatta secondo lo schema richiesto
            body += title_upper + "\n"
            body += description + ".\n"
            body += "Fonte: " + news['source'] + "\n"
            body += "Link: " + news['link'] + "\n"
            
            if idx < len(news_list):
                body += "\n"
    
    return body

def send_email():
    # Recupera le notizie
    news_list = fetch_tech_news()
    
    # Formatta il corpo della email
    subject = "notizie tech del giorno"
    body = format_news_body(news_list)
    
    # Crea il messaggio
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    
    # Invia l'email
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email inviata con successo a {TO_EMAIL}")
        print(f"Notizie inviate: {len(news_list)}")
        return True
    except Exception as e:
        print(f"Errore nell'invio dell'email: {e}")
        return False

if __name__ == "__main__":
    send_email()
