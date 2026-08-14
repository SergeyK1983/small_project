#!/bin/sh

set -eu

echo "==== Small-project start !!! ===="

echo "Migrate ... "
alembic upgrade head

echo "init_admin ... "
python -m src.cli createsuperuser admin admin

echo "Run ... "
exec uvicorn src.main:app --host 0.0.0.0 --port 8010