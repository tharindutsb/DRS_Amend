from fastapi import FastAPI
import logging

app = FastAPI()

#setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

