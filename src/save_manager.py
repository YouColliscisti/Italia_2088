import json
import os
import tempfile
from pathlib import Path


class SaveManager:
    VERSION = 2

    def __init__(self, filepath=None):
        self.filepath = Path(filepath) if filepath else Path(__file__).resolve().parent.parent / "savegame.json"
        self.last_error = ""

    @staticmethod
    def defaults():
        return {
            "version": SaveManager.VERSION,
            "active": False,
            "character_id": 1,
            "difficulty": "Normal",
            "level": 1,
            "score": 0,
            "high_score": 0,
            "completed_stories": [],
        }

    def _validated(self, raw):
        data = self.defaults()
        if not isinstance(raw, dict):
            return data
        data["active"] = bool(raw.get("active", False))
        data["character_id"] = raw.get("character_id", 1)
        if data["character_id"] not in (1, 2, 3, 4):
            data["character_id"] = 1
        data["difficulty"] = raw.get("difficulty", "Normal")
        if data["difficulty"] not in ("Easy", "Normal", "Hard"):
            data["difficulty"] = "Normal"
        for key, minimum, maximum in (("level", 1, 8), ("score", 0, None), ("high_score", 0, None)):
            value = raw.get(key, data[key])
            if isinstance(value, int) and not isinstance(value, bool) and value >= minimum:
                data[key] = min(value, maximum) if maximum else value
        data["high_score"] = max(data["high_score"], data["score"])
        completed = raw.get("completed_stories", [])
        if isinstance(completed, list):
            data["completed_stories"] = sorted({cid for cid in completed if cid in (1, 2, 3, 4)})
        return data

    def load_game_data(self):
        if not self.filepath.exists():
            return self.defaults()
        try:
            with self.filepath.open("r", encoding="utf-8") as handle:
                return self._validated(json.load(handle))
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            self.last_error = f"Save data could not be read: {exc}"
            return self.defaults()

    def _write(self, data):
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary = tempfile.mkstemp(prefix=".save_", suffix=".json", dir=self.filepath.parent)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(self._validated(data), handle, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.filepath)
            self.last_error = ""
            return True
        except OSError as exc:
            self.last_error = f"Save failed: {exc}"
            try:
                if "temporary" in locals() and os.path.exists(temporary):
                    os.remove(temporary)
            except OSError:
                pass
            return False

    def has_active_save(self):
        return self.load_game_data()["active"]

    def reset_save_data(self):
        data = self.load_game_data()
        data.update({"active": True, "character_id": 1, "level": 1, "score": 0})
        return self._write(data)

    def get_completed_stories(self):
        return self.load_game_data()["completed_stories"]

    def get_completed_stories_count(self):
        return len(self.get_completed_stories())

    def mark_story_completed(self, character_id):
        data = self.load_game_data()
        if character_id not in data["completed_stories"]:
            data["completed_stories"].append(character_id)
        data["active"] = False
        return self._write(data)

    def save_game(self, character_id, difficulty, level, score, player=None):
        data = self.load_game_data()
        data.update({
            "active": True,
            "character_id": character_id,
            "difficulty": difficulty,
            "level": level,
            "score": score,
            "high_score": max(data["high_score"], score),
        })
        return self._write(data)

    def record_high_score(self, score, keep_active=True):
        data = self.load_game_data()
        data["high_score"] = max(data["high_score"], score)
        if not keep_active:
            data["active"] = False
        return self._write(data)

    def load_high_score(self):
        return self.load_game_data()["high_score"]
