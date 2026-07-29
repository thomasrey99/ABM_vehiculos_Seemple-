from fastapi import APIRouter, Depends
from app.core.security import verify_api_key

appRouter= APIRouter(dependencies=[Depends(verify_api_key)])