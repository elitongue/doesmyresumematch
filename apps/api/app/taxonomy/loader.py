import argparse
import yaml
from pathlib import Path
from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship

from ..db import Base, get_engine, get_session


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    cluster = Column(String, nullable=False)
    aliases = relationship("SkillAlias", back_populates="skill", cascade="all, delete-orphan")


class SkillAlias(Base):
    __tablename__ = "skill_aliases"

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    alias = Column(String, unique=True, nullable=False)

    skill = relationship("Skill", back_populates="aliases")


def _load_yaml():
    path = Path(__file__).with_name("skills.yaml")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def init_db(engine=None):
    engine = engine or get_engine()
    Base.metadata.create_all(bind=engine)
    return engine


def load_skills(engine=None):
    engine = engine or get_engine()
    session = get_session(engine)
    data = _load_yaml()

    names_seen: set[str] = set()
    aliases_seen: set[str] = set()

    for cluster, skills in data.items():
        for item in skills:
            name = item["name"].strip()
            key = name.lower()
            if key in names_seen:
                raise ValueError(f"Duplicate skill name: {name}")
            names_seen.add(key)

            skill_obj = session.execute(select(Skill).where(Skill.name == name)).scalar_one_or_none()
            if not skill_obj:
                skill_obj = Skill(name=name, cluster=cluster)
                session.add(skill_obj)
                session.flush()

            for alias in item.get("aliases", []):
                alias_key = alias.lower()
                if alias_key in names_seen or alias_key in aliases_seen:
                    raise ValueError(f"Duplicate alias: {alias}")
                aliases_seen.add(alias_key)

                existing_alias = session.execute(select(SkillAlias).where(SkillAlias.alias == alias)).scalar_one_or_none()
                if not existing_alias:
                    session.add(SkillAlias(skill_id=skill_obj.id, alias=alias))
    session.commit()
    session.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Load skill taxonomy into the database")
    parser.add_argument("--init", action="store_true", help="Initialize database before loading")
    args = parser.parse_args(argv)

    engine = get_engine()
    if args.init:
        init_db(engine)
    load_skills(engine)


if __name__ == "__main__":  # pragma: no cover
    main()
