from sqlalchemy import text
from app.database import engine, SessionLocal, Base
from app import models

Base.metadata.create_all(bind=engine)


def migrate():
    db = SessionLocal()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(batches)"))
            columns = [row[1] for row in result.fetchall()]

            if 'review_status' not in columns:
                conn.execute(text(
                    "ALTER TABLE batches ADD COLUMN review_status VARCHAR(20) NOT NULL DEFAULT 'not_required'"
                ))
                conn.commit()
                print("已添加 batches.review_status 字段")
            else:
                print("batches.review_status 字段已存在")

        deliverable_batches = db.query(models.Batch).filter(
            models.Batch.status == "deliverable",
            models.Batch.review_status == "not_required"
        ).all()
        for batch in deliverable_batches:
            batch.review_status = "pending_review"
        if deliverable_batches:
            db.commit()
            print(f"已更新 {len(deliverable_batches)} 个可交付批次的复核状态为待复核")

        print("数据库迁移完成！")
    except Exception as e:
        print(f"迁移出错: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
