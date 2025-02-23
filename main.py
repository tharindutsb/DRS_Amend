from fastapi import FastAPI
import logging
from openApi.routes.amend_routes import router as amend_router

app = FastAPI(title="DRC Amend API")

#setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.include_router(amend_router)