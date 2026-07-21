from __future__ import annotations

from instream_shared.types import Role

ROLE_ORDER: dict[Role, int] = {
    Role.VIEWER: 0,
    Role.REVIEWER: 1,
    Role.OPERATOR: 2,
    Role.ADMIN: 3,
}
