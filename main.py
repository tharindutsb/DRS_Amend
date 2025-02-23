from fastapi import FastAPI
import logging
from openApi.routes.amend_routes import router as amend_router

app = FastAPI()

# #setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

app.include_router(amend_router)

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)