import asyncio
import logging
from app.worker import celery_app
from app.services.pubsub import sync_publish_progress
from app.services import llm
from app.db.store import store

logger = logging.getLogger(__name__)

async def process_document_async(task_id: str, file_path: str, user_id: str):
    try:
        # Step 1: Parsing & Extraction with Gemma (Secondary model)
        sync_publish_progress(task_id, user_id, {"status": "processing", "step": "parsing", "progress": 10})
        
        # Read file (simplified, assume plain text for now, but should handle pdf/docx later)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parsed = await llm.generate(
            prompt=f"Parse this document:\n\n{content}",
        )
        
        sync_publish_progress(task_id, user_id, {"status": "processing", "step": "extraction", "progress": 30})
        extracted = await llm.generate(
            prompt=f"Extract clauses:\n\n{parsed}",
        )

        # Step 2: Risk Assessment & Deep Analysis with Qwen (Primary model)
        sync_publish_progress(task_id, user_id, {"status": "processing", "step": "risk_assessment", "progress": 60})
        risk_analysis = await llm.generate(
            prompt=f"Assess risks:\n\n{extracted}",
        )

        sync_publish_progress(task_id, user_id, {"status": "processing", "step": "report", "progress": 80})
        report = await llm.generate(
            prompt=f"Write final report:\n\n{risk_analysis}",
        )

        # Update DB
        await store.connect()
        # Ensure DocumentTask update logic here via raw sql or Prisma client
        # store.db.documenttask.update(...)
        
        sync_publish_progress(task_id, user_id, {"status": "completed", "progress": 100, "report": report})

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        sync_publish_progress(task_id, user_id, {"status": "failed", "error": str(e)})
        raise e
    finally:
        await store.disconnect()

@celery_app.task(bind=True, max_retries=3)
def process_document(self, file_path: str, user_id: str):
    """
    Celery task to process a document.
    Runs an asyncio event loop internally to interface with async services.
    """
    task_id = self.request.id
    try:
        asyncio.run(process_document_async(task_id, file_path, user_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
