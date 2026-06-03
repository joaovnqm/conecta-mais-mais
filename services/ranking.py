from pathlib import Path
from typing import Any

from database.repositories.ranking_repository import RankingRepository
from models.ranking import (
    XP_ACTIONS,
    get_level_by_xp,
    get_missing_xp_for_next_level,
    get_next_level,
)


class RankingService:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.repository = RankingRepository(db_path=db_path)

    def award_points(
        self,
        user_id: int,
        event_id: int | None,
        action_type: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        """
        Dá XP ao usuário por uma ação realizada no evento.
        """

        if action_type not in XP_ACTIONS:
            return {
                "success": False,
                "message": "Tipo de ação inválido.",
                "unlocked_achievements": [],
            }

        inserted = self.repository.add_xp_entry(
            user_id=user_id,
            event_id=event_id,
            action_type=action_type,
            description=description,
        )

        if not inserted:
            return {
                "success": False,
                "message": "Essa pontuação já foi registrada para este usuário neste evento.",
                "unlocked_achievements": [],
            }

        unlocked_achievements = self.repository.update_user_achievements(
            user_id)

        action = XP_ACTIONS[action_type]

        return {
            "success": True,
            "message": f"{action.points} XP adicionados: {action.label}.",
            "points": action.points,
            "action": action.label,
            "unlocked_achievements": unlocked_achievements,
        }

    def get_user_summary(self, user_id: int) -> dict[str, Any]:
        total_xp = self.repository.get_user_total_xp(user_id)
        current_level = get_level_by_xp(total_xp)
        next_level = get_next_level(total_xp)
        missing_xp = get_missing_xp_for_next_level(total_xp)
        stats = self.repository.get_user_stats(user_id)
        achievements = self.repository.get_user_achievements(user_id)

        return {
            "user_id": user_id,
            "total_xp": total_xp,
            "current_level": {
                "name": current_level.name,
                "icon": current_level.icon,
                "min_xp": current_level.min_xp,
                "max_xp": current_level.max_xp,
            },
            "next_level": None if next_level is None else {
                "name": next_level.name,
                "icon": next_level.icon,
                "min_xp": next_level.min_xp,
                "max_xp": next_level.max_xp,
            },
            "missing_xp": missing_xp,
            "stats": stats,
            "achievements": achievements,
        }

    def get_leaderboard(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.repository.get_leaderboard(limit=limit)

        leaderboard: list[dict[str, Any]] = []

        for position, row in enumerate(rows, start=1):
            user_id = int(row["user_id"])
            total_xp = int(row["total_xp"])
            level = get_level_by_xp(total_xp)
            stats = self.repository.get_user_stats(user_id)

            leaderboard.append({
                "position": position,
                "user_id": user_id,
                "total_xp": total_xp,
                "level_name": level.name,
                "level_icon": level.icon,
                "events_attended": stats["events_attended"],
                "certificates_received": stats["certificates_received"],
                "presentations_done": stats["presentations_done"],
            })

        return leaderboard

    def get_available_actions(self) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []

        for action in XP_ACTIONS.values():
            actions.append({
                "key": action.key,
                "label": action.label,
                "points": action.points,
                "description": action.description,
            })

        return actions

    def rebuild_user_achievements(self, user_id: int) -> list[dict[str, Any]]:
        return self.repository.update_user_achievements(user_id)
