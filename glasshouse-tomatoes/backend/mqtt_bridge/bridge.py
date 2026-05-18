#!/usr/bin/env python3
"""
GlassHouse MQTT → TimescaleDB Bridge
=====================================
Subscribes to sensor node topics and writes measurements to the database.
"""

import os
import json
import logging
from datetime import datetime

import paho.mqtt.client as mqtt
import psycopg2
from psycopg2.extras import execute_values

# ─── Configuration ──────────────────────────────────────────────────────────
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://gh_user:changeme@localhost:5432/glasshouse",
)
TOPIC = "glasshouse/+/telemetry"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("mqtt_bridge")


# ─── Database ───────────────────────────────────────────────────────────────
def get_db_conn():
    return psycopg2.connect(DB_URL)


def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS measurements (
                time TIMESTAMPTZ NOT NULL,
                node_id TEXT NOT NULL,
                vwc_percent DOUBLE PRECISION,
                ec_ms_cm DOUBLE PRECISION,
                temp_c DOUBLE PRECISION,
                battery_mv INTEGER,
                rssi_dbm INTEGER,
                seq INTEGER,
                PRIMARY KEY (time, node_id)
            );
            """
        )
        cur.execute(
            """
            SELECT create_hypertable('measurements', 'time', if_not_exists => TRUE);
            """
        )
    conn.commit()


def insert_measurement(conn, payload: dict):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO measurements
            (time, node_id, vwc_percent, ec_ms_cm, temp_c, battery_mv, rssi_dbm, seq)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (time, node_id) DO NOTHING;
            """,
            (
                payload.get("timestamp") or datetime.utcnow().isoformat(),
                payload["node_id"],
                payload.get("vwc_percent"),
                payload.get("ec_ms_cm"),
                payload.get("temp_c"),
                payload.get("battery_mv"),
                payload.get("rssi_dbm"),
                payload.get("seq"),
            ),
        )
    conn.commit()


# ─── MQTT Callbacks ─────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker at %s:%d", MQTT_HOST, MQTT_PORT)
        client.subscribe(TOPIC)
        logger.info("Subscribed to %s", TOPIC)
    else:
        logger.error("MQTT connection failed, rc=%d", rc)


def on_message(client, userdata, msg):
    logger.debug("Message on %s: %s", msg.topic, msg.payload.decode())
    try:
        payload = json.loads(msg.payload.decode())
        insert_measurement(userdata["db"], payload)
        logger.info("Inserted measurement from %s", payload.get("node_id"))
    except Exception as exc:
        logger.error("Failed to process message: %s", exc)


# ─── Main ───────────────────────────────────────────────────────────────────
def main():
    logger.info("Starting MQTT bridge...")
    conn = get_db_conn()
    ensure_table(conn)
    logger.info("Database ready.")

    client = mqtt.Client()
    client.user_data_set({"db": conn})
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        client.disconnect()
        conn.close()


if __name__ == "__main__":
    main()
