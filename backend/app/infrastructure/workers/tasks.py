from app.core.celery_app import celery_app

@celery_app.task
def example_task(arg: str):
    return f"Processed: {arg}"
