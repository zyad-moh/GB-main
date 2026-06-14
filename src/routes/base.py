from fastapi import FastAPI,APIRouter,Depends#more efficient detect if there is a problem at helpers.config import get_settings,settings as it is a مصدر خارجى
import os
from helpers.config import get_settings,settings
base_router=APIRouter(
   prefix="/api/v1",
   tags=["api_v1"],
)
@base_router.get("/")#dicorator
async def welcome(app_settings:settings=Depends(get_settings)):
   app_name=app_settings.APP_NAME
   return {
      "app_name": app_name
      }