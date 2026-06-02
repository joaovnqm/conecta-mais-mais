from database.ranking_schema import create_ranking_tables, get_default_db_path
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    db_path = get_default_db_path()
    create_ranking_tables(db_path)

    print("Tabelas de ranking criadas/verificadas com sucesso.")
    print(f"Banco usado: {db_path}")


if __name__ == "__main__":
    main()
