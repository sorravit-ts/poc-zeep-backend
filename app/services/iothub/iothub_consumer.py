import threading
from typing import Optional

from azure.eventhub import EventHubConsumerClient
from app.core.config import IOTHUB_EVENTHUB_CONNECTION_STRING, CONSUMER_GROUP, IOTHUB_EVENTHUB_NAME


class EventHubConsumerService:
    def __init__(self) -> None:
        # ใช้สำหรับสั่งหยุด consumer จากภายนอก (เช่นตอน shutdown)
        self._stop_event = threading.Event()

        # flag กัน start ซ้ำ
        self._started = False

        # EventHub client (สร้างตอน start)
        self.client: Optional[EventHubConsumerClient] = None

    # =========================
    # Event Callbacks
    # =========================

    def on_event(self, partition_context, event):
        """
        ถูกเรียกเมื่อมี telemetry message เข้ามาจาก IoT Hub
        (ผ่าน Event Hub compatible endpoint)
        """

        # ถ้ามีคำสั่งให้หยุดแล้ว ไม่ต้องประมวลผลต่อ
        if self._stop_event.is_set():
            return

        # ดึง payload (body) ออกมาเป็น string
        payload = event.body_as_str(encoding="utf-8")

        # application properties ที่ส่งมาพร้อม message
        properties = event.properties or {}

        print("📩 Telemetry received")
        print("Payload:", payload)
        print("Properties:", properties)
        print("-" * 40)

        # commit checkpoint
        # บอก Event Hub ว่า event นี้ถูกประมวลผลแล้ว
        partition_context.update_checkpoint(event)

    def on_partition_initialize(self, partition_context):
        """
        ถูกเรียกเมื่อ consumer เชื่อมต่อ partition สำเร็จ
        """
        print(f"🟢 Connected to partition {partition_context.partition_id}")

    def on_partition_close(self, partition_context, reason):
        """
        ถูกเรียกเมื่อ partition ถูกปิด
        (เช่น rebalance, shutdown)
        """
        print(f"🔴 Partition {partition_context.partition_id} closed: {reason}")

    # =========================
    # Lifecycle
    # =========================

    def start(self) -> None:
        """
        เริ่ม EventHub consumer
        - ควรถูกเรียกจาก background thread
        - method นี้จะ block จนกว่าจะ stop
        """

        # กัน start ซ้ำ
        if self._started:
            print("⚠️ EventHubConsumerService already started")
            return

        self._started = True
        self._stop_event.clear()

        # สร้าง EventHub consumer client
        self.client = EventHubConsumerClient.from_connection_string(
            conn_str=IOTHUB_EVENTHUB_CONNECTION_STRING,
            consumer_group=CONSUMER_GROUP,
            eventhub_name=IOTHUB_EVENTHUB_NAME,
        )

        print("🚀 EventHub consumer started, listening telemetry...")

        try:
            # ใช้ context manager เพื่อให้ client ปิดอย่างถูกต้อง
            with self.client:
                self.client.receive(
                    on_event=self.on_event,
                    on_partition_initialize=self.on_partition_initialize,
                    on_partition_close=self.on_partition_close,
                    starting_position="@latest",  # รับเฉพาะ event ใหม่
                )

        except Exception as e:
            # ถ้า error เกิดขึ้นโดยไม่ได้สั่ง stop
            if not self._stop_event.is_set():
                print("❌ EventHub consumer error:", e)
                raise

        finally:
            # reset state เมื่อ consumer หยุด
            self._started = False
            print("🛑 EventHub consumer stopped")

    def stop(self) -> None:
        """
        หยุด EventHub consumer
        - ควรถูกเรียกจาก FastAPI shutdown
        """

        # ถ้าหยุดไปแล้ว ไม่ต้องทำซ้ำ
        if self._stop_event.is_set():
            return

        print("🛑 Stopping EventHub consumer...")
        self._stop_event.set()

        # สำคัญมาก:
        # การ close client จะทำให้ receive() unblock
        # และออกจาก loop ได้อย่างปลอดภัย
        if self.client:
            self.client.close()
