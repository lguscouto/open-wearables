#!/usr/bin/env python3
"""Seed default user with Zepp connection if configured in environment."""

import os
from datetime import datetime, timezone
from uuid import uuid4

from app.database import SessionLocal
from app.models import User, UserConnection
from app.schemas.auth import ConnectionStatus
from app.schemas.enums import ProviderName
from app.schemas.model_crud.user_management.user import UserCreateInternal
from app.services.providers.zepp.client import DEFAULT_HOST
from app.services.user_service import user_service


def seed_zepp_user() -> None:
    app_token = os.getenv("ZEPP_APP_TOKEN")
    user_id_str = os.getenv("ZEPP_USER_ID")
    host = os.getenv("ZEPP_HOST", DEFAULT_HOST)

    if not app_token or not user_id_str:
        print("ZEPP_APP_TOKEN or ZEPP_USER_ID not provided, skipping Zepp auto-connect.")
        return

    with SessionLocal() as db:
        user = db.query(User).first()
        if not user:
            user = user_service.create(
                db,
                UserCreateInternal(
                    first_name="Gustavo",
                    last_name="Couto",
                    email="gustavocouto@souunisuam.com.br",
                ),
            )
            print(f"✓ Created primary user: {user.first_name} ({user.id})")

        conn = (
            db.query(UserConnection)
            .filter(
                UserConnection.user_id == user.id,
                UserConnection.provider == ProviderName.ZEPP.value,
            )
            .first()
        )
        if conn:
            conn.access_token = app_token
            conn.provider_user_id = user_id_str
            conn.refresh_token = host
            conn.status = ConnectionStatus.ACTIVE
            conn.updated_at = datetime.now(timezone.utc)
            db.add(conn)
            db.commit()
            print(f"✓ Updated Zepp connection for user {user.id}")
        else:
            conn = UserConnection(
                id=uuid4(),
                user_id=user.id,
                provider=ProviderName.ZEPP.value,
                provider_user_id=user_id_str,
                provider_username="Gustavo",
                access_token=app_token,
                refresh_token=host,
                scope="workouts activity sleep biometrics",
                status=ConnectionStatus.ACTIVE,
                token_expires_at=None,
                updated_at=datetime.now(timezone.utc),
            )
            db.add(conn)
            db.commit()
            print(f"✓ Created Zepp connection for user {user.id}")


if __name__ == "__main__":
    seed_zepp_user()
