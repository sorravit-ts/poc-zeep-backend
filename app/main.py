import threading
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.pods import pods_control, pods_create, pods_delete, pods_get
from app.services.iothub.iothub_consumer import EventHubConsumerService

consumer = EventHubConsumerService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------- startup ----------
    consumer_thread = threading.Thread(
        target=consumer.start,
        name="eventhub-consumer",
        daemon=True,
    )
    consumer_thread.start()

    app.state.consumer_thread = consumer_thread

    print("✅ EventHub consumer thread started")

    yield

    # ---------- shutdown ----------
    print("🛑 Shutting down EventHub consumer...")
    consumer.stop()

    consumer_thread.join(timeout=5)

    print("✅ EventHub consumer stopped")



app = FastAPI(lifespan=lifespan)

app.include_router(pods_control.router)
app.include_router(pods_create.router)
app.include_router(pods_get.router)
app.include_router(pods_delete.router)
    


