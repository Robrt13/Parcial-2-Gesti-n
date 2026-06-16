from bs4 import BeautifulSoup
import requests, csv


def start_session(headers: dict) -> requests.Session:
    session = requests.Session()
    session.headers.update(headers)
    return session


def create_html_parser(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def create_xml_parser(xml: str) -> BeautifulSoup:
    return BeautifulSoup(xml, "xml")


def save_to_csv(data: list[dict], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        campos = ["medio", "titulo", "fecha", "categoria_original", "texto", "url"]
        writer = csv.DictWriter(file, fieldnames=campos)
        writer.writeheader()
        writer.writerows(data)
        print(f"Saved to: {output_path.split('/')[-1]}")