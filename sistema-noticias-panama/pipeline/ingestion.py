from scrapers import scrap_tvn_news_section
import pandas as pd
from pathlib import Path


def scrap_news(scraper: function, sources: list) -> list:
    news_data = []
    for source in sources:
        news_data.extend(scraper(source))
    return news_data


if __name__ == "__main__":
    configs = [
        {
            "scraper": scrap_tvn_news_section,
            "sources": [
                "https://www.tvn-2.com/nacionales/",
                "https://www.tvn-2.com/mundo/",
                "https://www.tvn-2.com/contenido-exclusivo/",
                "https://www.tvn-2.com/entretenimiento/",
                "https://www.tvn-2.com/tvmax/lpf/",
                "https://www.tvn-2.com/tvmax/futbol-internacional/",
                "https://www.tvn-2.com/tvmax/beisbol-nacional/",
                "https://www.tvn-2.com/tvmax/beisbol/",
                "https://www.tvn-2.com/tvmax/mas-deportes/"
            ],
            "output":f"{Path(__file__).parent}/../data/raw/noticias_tvn.csv"
        }
    ]

    for config in configs:
        news_data = scrap_news(config["scraper"], config["sources"])
        df = pd.DataFrame(news_data)
        df.to_csv(config["output"], index=False)
        print(f"Scraped {config["output"].split("/")[-1]}")