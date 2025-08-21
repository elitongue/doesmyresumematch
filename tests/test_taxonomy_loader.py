import sys
from pathlib import Path

import yaml
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
from app.taxonomy import loader  # noqa: E402


def test_loader_idempotent(tmp_path, monkeypatch):
    db_path = tmp_path / "skills.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    engine = loader.init_db()
    loader.load_skills(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    data = yaml.safe_load(Path(loader.__file__).with_name("skills.yaml").read_text())
    expected_skills = sum(len(v) for v in data.values())
    expected_aliases = sum(len(item.get("aliases", [])) for v in data.values() for item in v)

    assert session.query(loader.Skill).count() == expected_skills
    assert session.query(loader.SkillAlias).count() == expected_aliases

    session.close()
    loader.load_skills(engine)
    session = Session()

    assert session.query(loader.Skill).count() == expected_skills
    assert session.query(loader.SkillAlias).count() == expected_aliases
    session.close()
