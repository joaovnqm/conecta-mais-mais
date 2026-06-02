from database.ranking_schema import create_ranking_tables, get_default_db_path


def main() -> None:
    db_path = get_default_db_path()

    create_ranking_tables(db_path, reset=True)

    print(f"Tabelas de ranking criadas/atualizadas com sucesso em: {db_path}")


if __name__ == "__main__":
    main()
