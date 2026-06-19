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

            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_archives'"))
            if result.fetchone() is None:
                conn.execute(text("""
                    CREATE TABLE delivery_archives (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        batch_id INTEGER NOT NULL UNIQUE,
                        archiver_id INTEGER NOT NULL,
                        delivery_time DATETIME NOT NULL,
                        delivered_quantity INTEGER NOT NULL,
                        receiver VARCHAR(100) NOT NULL,
                        delivery_remark TEXT,
                        quality_conclusion VARCHAR(500) NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (batch_id) REFERENCES batches (id),
                        FOREIGN KEY (archiver_id) REFERENCES users (id)
                    )
                """))
                conn.commit()
                print("已创建 delivery_archives 表")
            else:
                print("delivery_archives 表已存在")

            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='rework_records'"))
            if result.fetchone() is None:
                conn.execute(text("""
                    CREATE TABLE rework_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        batch_id INTEGER NOT NULL,
                        rework_no INTEGER NOT NULL DEFAULT 1,
                        initiator_id INTEGER NOT NULL,
                        responsible_id INTEGER NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'pending',
                        rework_reason TEXT NOT NULL,
                        handling_instruction TEXT,
                        expected_finish_time DATETIME,
                        actual_finish_time DATETIME,
                        rework_result TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (batch_id) REFERENCES batches (id),
                        FOREIGN KEY (initiator_id) REFERENCES users (id),
                        FOREIGN KEY (responsible_id) REFERENCES users (id)
                    )
                """))
                conn.commit()
                print("已创建 rework_records 表")
            else:
                print("rework_records 表已存在")

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
