import json

from app.database import SessionLocal
from app.models import ModuleMetadata, FlashcardPages


def seed_database():
    db = SessionLocal()

    try:
        # 檢查 M001 是否已存在，避免重複 seed
        existing_module = db.query(ModuleMetadata).filter(ModuleMetadata.module_id == "M001").first()
        if existing_module:
            print("Seed data already exists. Skipping insert.")
            return

        module = ModuleMetadata(
            module_id="M001",
            source_document="金融業運用人工智慧(AI)指引",
            source="金融監督管理委員會（FSC Taiwan）",
            domain_tags_json=json.dumps([
                "金融科技",
                "AI治理",
                "風險管理",
                "生成式AI",
                "法遵"
            ], ensure_ascii=False),
            warning_text="你有 7 分鐘閱讀 5 張卡片，閱讀完後將立即進入測驗。"
        )

        flashcards = [
            FlashcardPages(
                page_id="P001",
                module_id="M001",
                sequence_number=1,
                page_title="金融業為何需要 AI？",
                domain_tag="#金融科技",
                page_content_json=json.dumps({
                    "text": [
                        "AI 已廣泛應用於金融市場，可帶來以下效益：",
                        "提升營運效率",
                        "降低成本",
                        "優化客戶體驗",
                        "強化風險管理",
                        "協助法遵",
                        "防制金融犯罪",
                        "強化資安防禦",
                        "支持永續發展",
                        "但若導入不當，也可能造成客戶損失與市場信任危機。"
                    ]
                }, ensure_ascii=False)
            ),
            FlashcardPages(
                page_id="P002",
                module_id="M001",
                sequence_number=2,
                page_title="AI 六大核心原則",
                domain_tag="#AI治理",
                page_content_json=json.dumps({
                    "text": [
                        "建立治理與問責機制",
                        "重視公平性與以人為本",
                        "保護隱私與客戶權益",
                        "確保系統穩健與安全性",
                        "落實透明性與可解釋性",
                        "促進永續發展"
                    ]
                }, ensure_ascii=False)
            ),
            FlashcardPages(
                page_id="P003",
                module_id="M001",
                sequence_number=3,
                page_title="AI 系統生命週期",
                domain_tag="#風險管理",
                page_content_json=json.dumps({
                    "text": [
                        "系統規劃與設計",
                        "資料蒐集與輸入",
                        "模型建立與驗證",
                        "系統部署與監控",
                        "金融機構須在每個階段進行風險控管。"
                    ]
                }, ensure_ascii=False)
            ),
            FlashcardPages(
                page_id="P004",
                module_id="M001",
                sequence_number=4,
                page_title="生成式 AI 的風險",
                domain_tag="#生成式AI",
                page_content_json=json.dumps({
                    "text": [
                        "是否產生偏見或歧視",
                        "是否洩漏客戶資料",
                        "輸出內容是否正確",
                        "是否有人工審核機制",
                        "第三方模型是否可信任",
                        "即使使用外部 AI 工具，金融機構仍須負責最終風險管理。"
                    ]
                }, ensure_ascii=False)
            ),
            FlashcardPages(
                page_id="P005",
                module_id="M001",
                sequence_number=5,
                page_title="客戶權益與透明揭露",
                domain_tag="#法遵",
                page_content_json=json.dumps({
                    "text": [
                        "告知客戶這是 AI 提供的服務",
                        "說明 AI 功能與可能影響",
                        "提供替代方案（人工服務）",
                        "保護客戶隱私",
                        "提供申訴與救濟管道",
                        "核心精神：科技不能凌駕客戶權益。"
                    ]
                }, ensure_ascii=False)
            )
        ]

        db.add(module)
        db.add_all(flashcards)
        db.commit()

        print("Seed data inserted successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()