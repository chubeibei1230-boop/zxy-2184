from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app import models, auth

Base.metadata.create_all(bind=engine)


def init_data():
    db = SessionLocal()

    try:
        admin_count = db.query(models.User).filter(models.User.username == "admin").count()
        if admin_count == 0:
            admin = models.User(
                username="admin",
                name="系统管理员",
                role="admin",
                password_hash=auth.get_password_hash("admin123")
            )
            db.add(admin)
            print("创建管理员账号: admin / admin123")

        tech_count = db.query(models.User).filter(models.User.username == "tech1").count()
        if tech_count == 0:
            tech1 = models.User(
                username="tech1",
                name="张工艺",
                role="technician",
                password_hash=auth.get_password_hash("123456")
            )
            tech2 = models.User(
                username="tech2",
                name="李工艺",
                role="technician",
                password_hash=auth.get_password_hash("123456")
            )
            db.add_all([tech1, tech2])
            print("创建工艺员账号: tech1/123456, tech2/123456")

        insp_count = db.query(models.User).filter(models.User.username == "insp1").count()
        if insp_count == 0:
            insp1 = models.User(
                username="insp1",
                name="王质检",
                role="inspector",
                password_hash=auth.get_password_hash("123456")
            )
            insp2 = models.User(
                username="insp2",
                name="赵质检",
                role="inspector",
                password_hash=auth.get_password_hash("123456")
            )
            db.add_all([insp1, insp2])
            print("创建质检员账号: insp1/123456, insp2/123456")

        style_count = db.query(models.Style).count()
        if style_count == 0:
            styles = [
                models.Style(code="ST001", name="涡轮叶片A型", description="航空发动机涡轮叶片"),
                models.Style(code="ST002", name="涡轮叶片B型", description="航空发动机涡轮叶片"),
                models.Style(code="ST003", name="导向器叶片", description="燃气轮机导向器叶片"),
                models.Style(code="ST004", name="整体叶盘", description="整体叶盘精密铸件"),
                models.Style(code="ST005", name="燃烧室壳体", description="燃烧室壳体铸件"),
            ]
            db.add_all(styles)
            print("创建款式数据")

        wax_batch_count = db.query(models.WaxBatch).count()
        if wax_batch_count == 0:
            today = date.today()
            wax_batches = [
                models.WaxBatch(code="WB202406001", material="K417G高温合金蜡料", production_date=today - timedelta(days=30), quantity=500, remark="优质蜡料"),
                models.WaxBatch(code="WB202406002", material="K417G高温合金蜡料", production_date=today - timedelta(days=15), quantity=800, remark=""),
                models.WaxBatch(code="WB202406003", material="DZ417G定向凝固蜡料", production_date=today - timedelta(days=7), quantity=300, remark=""),
            ]
            db.add_all(wax_batches)
            print("创建蜡料批次数据")

        mold_count = db.query(models.Mold).count()
        if mold_count == 0:
            molds = [
                models.Mold(code="M001", name="A型模具-1", style_id=1, max_cavities=4, status="available"),
                models.Mold(code="M002", name="A型模具-2", style_id=1, max_cavities=4, status="available"),
                models.Mold(code="M003", name="B型模具-1", style_id=2, max_cavities=6, status="available"),
                models.Mold(code="M004", name="导向器模具-1", style_id=3, max_cavities=2, status="available"),
                models.Mold(code="M005", name="叶盘模具-1", style_id=4, max_cavities=1, status="available"),
                models.Mold(code="M006", name="燃烧室模具-1", style_id=5, max_cavities=1, status="maintenance"),
            ]
            db.add_all(molds)
            print("创建模具数据")

        station_count = db.query(models.Station).count()
        if station_count == 0:
            stations = [
                models.Station(code="S001", name="浇注台1号", type="pour", status="idle"),
                models.Station(code="S002", name="浇注台2号", type="pour", status="idle"),
                models.Station(code="S003", name="脱模台1号", type="demold", status="idle"),
                models.Station(code="S004", name="修边台1号", type="trim", status="idle"),
                models.Station(code="S005", name="修边台2号", type="trim", status="idle"),
                models.Station(code="S006", name="质检台1号", type="inspect", status="idle"),
            ]
            db.add_all(stations)
            print("创建台位数据")

        cycle_count = db.query(models.InspectionCycle).count()
        if cycle_count == 0:
            cycles = [
                models.InspectionCycle(style_id=1, cycle_days=7),
                models.InspectionCycle(style_id=2, cycle_days=7),
                models.InspectionCycle(style_id=3, cycle_days=10),
                models.InspectionCycle(style_id=4, cycle_days=14),
                models.InspectionCycle(style_id=5, cycle_days=14),
            ]
            db.add_all(cycles)
            print("创建质检周期数据")

        batch_count = db.query(models.Batch).count()
        if batch_count == 0:
            today = date.today()
            batches = [
                models.Batch(
                    code="B202406001", style_id=1, wax_batch_id=1, mold_id=1, station_id=1,
                    technician_id=2, inspector_id=4, status="deliverable",
                    planned_start_date=today - timedelta(days=20), planned_end_date=today - timedelta(days=10),
                    actual_start_date=datetime.now() - timedelta(days=20), actual_end_date=datetime.now() - timedelta(days=12),
                    quantity=20, remark="首批试制"
                ),
                models.Batch(
                    code="B202406002", style_id=1, wax_batch_id=2, mold_id=1, station_id=1,
                    technician_id=2, inspector_id=4, status="pending_inspect",
                    planned_start_date=today - timedelta(days=5), planned_end_date=today + timedelta(days=2),
                    actual_start_date=datetime.now() - timedelta(days=5),
                    quantity=20, remark=""
                ),
                models.Batch(
                    code="B202406003", style_id=2, wax_batch_id=2, mold_id=3, station_id=2,
                    technician_id=3, inspector_id=5, status="molding",
                    planned_start_date=today - timedelta(days=2), planned_end_date=today + timedelta(days=5),
                    actual_start_date=datetime.now() - timedelta(days=2),
                    quantity=30, remark=""
                ),
                models.Batch(
                    code="B202406004", style_id=3, wax_batch_id=3, mold_id=4, station_id=2,
                    technician_id=2, inspector_id=4, status="reworking",
                    planned_start_date=today - timedelta(days=10), planned_end_date=today - timedelta(days=3),
                    actual_start_date=datetime.now() - timedelta(days=10),
                    quantity=10, remark="表面缺陷需返工"
                ),
                models.Batch(
                    code="B202406005", style_id=1, wax_batch_id=1, mold_id=2, station_id=1,
                    technician_id=3, inspector_id=None, status="pending_pour",
                    planned_start_date=today + timedelta(days=1), planned_end_date=today + timedelta(days=8),
                    quantity=20, remark=""
                ),
            ]
            db.add_all(batches)
            print("创建批次数据")

        process_count = db.query(models.ProcessRecord).count()
        if process_count == 0:
            now = datetime.now()
            process_records = [
                models.ProcessRecord(
                    batch_id=1, type="pour", operator_id=2, record_time=now - timedelta(days=20),
                    temperature=68.5, pressure=0.5, hold_time=120, cooling_time=300, remark="正常"
                ),
                models.ProcessRecord(
                    batch_id=1, type="demold", operator_id=2, record_time=now - timedelta(days=18),
                    temperature=25.0, cooling_time=180, remark="脱模顺利"
                ),
                models.ProcessRecord(
                    batch_id=1, type="trim", operator_id=2, record_time=now - timedelta(days=17),
                    remark="修边完成"
                ),
                models.ProcessRecord(
                    batch_id=1, type="bubble", operator_id=2, record_time=now - timedelta(days=16),
                    bubble_description="叶尖位置少量气泡", bubble_count=2, remark="轻微"
                ),
                models.ProcessRecord(
                    batch_id=2, type="pour", operator_id=2, record_time=now - timedelta(days=5),
                    temperature=68.0, pressure=0.5, hold_time=120, cooling_time=300, remark="正常"
                ),
                models.ProcessRecord(
                    batch_id=2, type="demold", operator_id=2, record_time=now - timedelta(days=3),
                    temperature=25.0, cooling_time=180, remark=""
                ),
                models.ProcessRecord(
                    batch_id=2, type="trim", operator_id=2, record_time=now - timedelta(days=2),
                    remark=""
                ),
                models.ProcessRecord(
                    batch_id=2, type="bubble", operator_id=2, record_time=now - timedelta(days=1),
                    bubble_description="叶根部位气泡较多", bubble_count=8, remark="较严重"
                ),
                models.ProcessRecord(
                    batch_id=3, type="pour", operator_id=3, record_time=now - timedelta(days=2),
                    temperature=69.0, pressure=0.55, hold_time=130, cooling_time=320, remark=""
                ),
                models.ProcessRecord(
                    batch_id=4, type="pour", operator_id=2, record_time=now - timedelta(days=10),
                    temperature=68.5, pressure=0.5, hold_time=120, cooling_time=300, remark=""
                ),
                models.ProcessRecord(
                    batch_id=4, type="demold", operator_id=2, record_time=now - timedelta(days=8),
                    temperature=25.0, cooling_time=180, remark=""
                ),
                models.ProcessRecord(
                    batch_id=4, type="trim", operator_id=2, record_time=now - timedelta(days=7),
                    remark=""
                ),
                models.ProcessRecord(
                    batch_id=4, type="bubble", operator_id=2, record_time=now - timedelta(days=6),
                    bubble_description="多处气泡", bubble_count=12, remark="严重"
                ),
                models.ProcessRecord(
                    batch_id=4, type="rework", operator_id=2, record_time=now - timedelta(days=4),
                    rework_reason="气泡缺陷", rework_count=1, remark="正在返工"
                ),
            ]
            db.add_all(process_records)
            print("创建工艺记录数据")

        inspection_count = db.query(models.InspectionRecord).count()
        if inspection_count == 0:
            now = datetime.now()
            inspection_records = [
                models.InspectionRecord(
                    batch_id=1, inspector_id=4, inspect_time=now - timedelta(days=12),
                    dimension_deviation="最大偏差0.02mm，符合要求", surface_flatness=0.015,
                    is_pass=True, opinion="尺寸合格，表面质量良好，可交付"
                ),
            ]
            db.add_all(inspection_records)
            print("创建质检记录数据")

        db.commit()
        print("数据初始化完成！")

    except Exception as e:
        print(f"初始化数据出错: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_data()
