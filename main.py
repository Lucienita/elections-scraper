import csv
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ALLOWED_URL_START = (
    "https://www.volby.cz/pls/ps2017nss/ps32",
    "https://volby.cz/pls/ps2017nss/ps32",
)
CSV_HEADER = ["code", "location", "registered", "envelopes", "valid"]


def check_arguments(arguments: list[str]) -> tuple[str, str]:
    """Ověří argumenty z příkazové řádky a vrátí odkaz a název souboru.

    Pokud argumenty nejsou v pořádku, vypíše upozornění a ukončí program.
    """
    if len(arguments) != 3:
        sys.exit(
            "Zadej přesně 2 argumenty: odkaz na územní celek "
            "a název výstupního souboru."
        )

    url, file_name = arguments[1], arguments[2]

    if not url.startswith(ALLOWED_URL_START):
        sys.exit(
            "První argument musí být odkaz na územní celek z volby.cz "
            "(volby 2017)."
        )
    if not file_name.endswith(".csv"):
        sys.exit("Druhý argument musí být název souboru s příponou .csv.")

    return url, file_name


def get_soup(url: str) -> BeautifulSoup:
    """Stáhne stránku a vrátí ji jako objekt BeautifulSoup."""
    response = requests.get(url)
    if response.status_code != 200:
        sys.exit(f"Stránku se nepodařilo načíst: {url}")
    return BeautifulSoup(response.content, "html.parser")


def clean_number(text: str) -> int:
    """Převede text jako '1 224' (s nezlomitelnou mezerou) na číslo."""
    return int(text.replace("\xa0", "").replace(" ", ""))


def get_municipalities(soup: BeautifulSoup, url: str) -> list[dict]:
    """Vrátí seznam obcí územního celku s kódem, názvem a odkazem."""
    municipalities = []

    for cell in soup.find_all("td", class_="cislo"):
        link = cell.find("a")
        if link is None:
            # prázdné řádky na konci tabulek nemají odkaz
            continue

        name_cell = cell.find_next_sibling("td")
        municipalities.append({
            "code": link.get_text(strip=True),
            "location": name_cell.get_text(strip=True),
            # odkaz na stránce je relativní, urljoin z něj udělá celý
            "url": urljoin(url, link["href"]),
        })

    return municipalities


def get_summary(soup: BeautifulSoup) -> list[int]:
    """Vrátí voliče v seznamu, vydané obálky a platné hlasy obce."""
    summary = []
    for header in ("sa2", "sa3", "sa6"):
        cell = soup.find("td", headers=header)
        summary.append(clean_number(cell.get_text(strip=True)))
    return summary


def get_party_results(soup: BeautifulSoup) -> dict[str, int]:
    """Vrátí slovník {název strany: počet hlasů} pro jednu obec."""
    results = {}

    # výsledky stran jsou rozdělené do dvou tabulek (t1 a t2)
    for table in ("t1", "t2"):
        names = soup.find_all("td", headers=f"{table}sb2")
        votes = soup.find_all("td", headers=f"{table}sb3")

        for name, vote in zip(names, votes):
            party = name.get_text(strip=True)
            if party == "-":
                continue
            results[party] = clean_number(vote.get_text(strip=True))

    return results


def scrape_municipality(municipality: dict) -> dict:
    """Stáhne výsledky jedné obce a vrátí je jako jeden slovník."""
    soup = get_soup(municipality["url"])
    registered, envelopes, valid = get_summary(soup)

    row = {
        "code": municipality["code"],
        "location": municipality["location"],
        "registered": registered,
        "envelopes": envelopes,
        "valid": valid,
    }
    row.update(get_party_results(soup))
    return row


def scrape_district(url: str) -> list[dict]:
    """Stáhne výsledky všech obcí územního celku."""
    municipalities = get_municipalities(get_soup(url), url)

    if not municipalities:
        sys.exit("Na zadaném odkazu se nenašly žádné obce.")

    return [scrape_municipality(item) for item in municipalities]


def save_to_csv(rows: list[dict], file_name: str) -> None:
    """Uloží výsledky všech obcí do CSV souboru."""
    # názvy stran se doplní za základní sloupce podle první obce
    parties = [key for key in rows[0] if key not in CSV_HEADER]

    with open(file_name, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_HEADER + parties)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Spustí celý scraper."""
    url, file_name = check_arguments(sys.argv)

    print(f"STAHUJI DATA Z VYBRANÉHO URL: {url}")
    rows = scrape_district(url)

    print(f"UKLÁDÁM DO SOUBORU: {file_name}")
    save_to_csv(rows, file_name)

    print("UKONČUJI election-scraper")


if __name__ == "__main__":
    main()
