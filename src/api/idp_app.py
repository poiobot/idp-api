from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import domain.model  # noqa: F401 — resolve forward references before router imports
from routers.crud import claim_crud_api, document_crud_api, document_classification_crud_api, extraction_result_crud_api, insurance_policy_crud_api, policy_holder_crud_api
from api.service_descriptor import router as describe_router
from api import settings
from lib.representation import install_representations
app = FastAPI()

install_representations(app)

origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"]
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)

app.include_router(claim_crud_api.router)
app.include_router(document_crud_api.router)
app.include_router(document_classification_crud_api.router)
app.include_router(extraction_result_crud_api.router)
app.include_router(insurance_policy_crud_api.router)
app.include_router(policy_holder_crud_api.router)
app.include_router(describe_router)

try:
	import hooks_config
except ImportError:
	pass


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=2112)
