import sqlite3

from services.event_important_dates_update_service import EventImportantDatesUpdateService


DATABASE_PATH = "conecta++.db"


EVENT_LINKS_BY_ID = {
    # Eventos nacionais / SBC
    1: "https://sbsi.sbc.org.br/2026/chamada-pesquisa.php",
    2: "https://cbsoft.sbc.org.br/2026/pt/symposiums/sbes/call/",
    3: "https://sbbd.org.br/2026/trilha-principal/",
    4: "https://bracis.sbc.org.br/2026/bracis/",
    5: "https://bracis.sbc.org.br/2026/eniac/",
    7: "https://bracis.sbc.org.br/2026/kdmile/",
    8: "https://bracis.sbc.org.br/2026/stil/",
    9: "https://www.webmedia.org.br/datas-importantes/index.html",
    10: "https://ci2s-enterprise.com.ar/2025/12/16/1st-call-for-papers-on-the-29th-workshop-on-requirements-engineering/",
    11: "https://cbsoft.sbc.org.br/2026/pt/symposiums/sbcars/call/",
    12: "https://cbsoft.sbc.org.br/2026/pt/symposiums/sast/call/",
    13: "https://csbc.sbc.org.br/2026/brasnam/",
    14: "https://erbd2026.dv.utfpr.edu.br/",
    15: "https://sbbd.org.br/2026/wtdbd/",

    # Eventos internacionais
    16: "https://conf.researchr.org/dates/icse-2026",
    17: "https://conf.researchr.org/dates/fse-2026",
    18: "https://conf.researchr.org/dates/ease-2026",
    19: "https://conf.researchr.org/dates/RE-2026",
    20: "https://conf.researchr.org/dates/saner-2026",
    21: "https://conf.researchr.org/home/issta-2026",
    22: "https://vldb.org/2026/important-dates.html",
    23: "https://icde2026.github.io/important-dates.html",
    24: "https://edbticdt2026.github.io/?contents=important_dates.html",
    25: "https://aaai.org/conference/aaai/aaai-26/",
    26: "https://2026.ijcai.org/important-dates/",
    27: "https://icml.cc/Conferences/2026/CallForPapers",

    # Evento local / inovação
    28: "https://doity.com.br/cesar-beat",
}


def update_event_links() -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("\nAtualizando links oficiais por ID...\n")

    for event_id, official_url in EVENT_LINKS_BY_ID.items():
        cursor.execute(
            """
            UPDATE events
            SET official_url = ?,
                auto_update_dates = 1
            WHERE event_id = ?
            """,
            (official_url, event_id)
        )

        print(f"ID: {event_id}")
        print(f"Link: {official_url}")
        print(f"Linhas alteradas: {cursor.rowcount}")
        print("-" * 80)

    conn.commit()
    conn.close()


def list_events_with_links() -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT event_id, name, official_url, auto_update_dates
        FROM events
        ORDER BY event_id
        """
    )

    print("\nEventos cadastrados:\n")

    for event_id, name, official_url, auto_update_dates in cursor.fetchall():
        print(f"ID: {event_id}")
        print(f"Nome: {name}")
        print(f"Link oficial: {official_url or 'SEM LINK'}")
        print(f"Atualização automática: {auto_update_dates}")
        print("-" * 80)

    conn.close()


def force_update_important_dates() -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT event_id, name, official_url
        FROM events
        WHERE official_url IS NOT NULL
          AND official_url != ''
          AND COALESCE(auto_update_dates, 1) = 1
        ORDER BY event_id
        """
    )

    events = cursor.fetchall()
    conn.close()

    service = EventImportantDatesUpdateService(DATABASE_PATH)

    print("\nForçando atualização das datas importantes...\n")

    for event_id, name, official_url in events:
        success, message = service.update_event_dates(event_id, official_url)

        print(f"ID: {event_id}")
        print(f"Evento: {name}")
        print(f"URL: {official_url}")
        print(f"Resultado: {success} - {message}")
        print("-" * 80)


if __name__ == "__main__":
    update_event_links()
    list_events_with_links()
    force_update_important_dates()
