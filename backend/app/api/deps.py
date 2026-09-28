from __future__ import annotations
import os
import uuid
from typing import Generator, Annotated, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

_bearer = HTTPBearer(auto_error=False)
_engine = None
_SessionLocal = None


def _get_session_factory():
    global _engine, _SessionLocal
    if _SessionLocal is None:
        url = os.getenv('DATABASE_URL', 'sqlite+pysqlite:///:memory:')
        is_mem = url in ('sqlite+pysqlite:///:memory:', 'sqlite:///:memory:')
        if is_mem:
            _engine = create_engine(url, connect_args={'check_same_thread': False}, poolclass=StaticPool)
            @event.listens_for(_engine, 'connect')
            def _pragma(dbapi_conn, _record):
                c = dbapi_conn.cursor()
                c.execute('PRAGMA foreign_keys=ON')
                c.close()
        else:
            from backend.app.infra.db.session import create_db_engine
            _engine = create_db_engine(url=url)
        from backend.app.infra.db.session import create_all_tables
        create_all_tables(_engine)
        _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False, expire_on_commit=False)
    return _SessionLocal


def get_db():
    factory = _get_session_factory()
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]


class CurrentUser:
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role


def get_current_user(request: Request, db: DbDep, credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)):
    x_user_id = request.headers.get('x-user-id')
    if x_user_id:
        try:
            uid = uuid.UUID(x_user_id)
            role = 'COMERCIAL'
            if str(uid) == '00000000-0000-0000-0000-000000000002':
                role = 'OPERADOR'
            elif str(uid) == '00000000-0000-0000-0000-000000000003':
                role = 'ADMIN'
            return CurrentUser(id=uid, email='mock@cotarco.ao', role=role)
        except ValueError:
            pass
    if credentials:
        pass
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'error': {'code': 'NOT_AUTHENTICATED', 'message': 'Token required', 'request_id': ''}})


UserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_role(*roles):
    def _checker(current_user: UserDep):
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={'error': {'code': 'FORBIDDEN', 'message': f'Required role: {roles}', 'request_id': ''}})
        return current_user
    return _checker
