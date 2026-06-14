import asyncio
import logging
from fastapi import FastAPI
from routes import base,data,nlp,auth, interview, email_ingestion,inter,job
from services.gmail_ingestion_service import GmailIngestionService

logger = logging.getLogger(__name__)
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware 
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_span():
   settings = get_settings()# equal to i take obj from class  don't write get_settings.MONGODB_URL
   
   app.mongo_conn=AsyncIOMotorClient(settings.MONGODB_URL)
   app.db_client =app.mongo_conn[settings.MONGODB_DATABASE]
   llm_provider_factory = LLMProviderFactory(settings)
   vectordb_provider_factory =VectorDBProviderFactory(settings)
   # generation client
   app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
   app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

   # embedding client
   app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
   app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                            embedding_size=settings.EMBEDDING_MODEL_SIZE)

   app.vectordb_client=vectordb_provider_factory.create(
      provider=settings.VECTOR_DB_BAKEND
   )# return QdrantDBProvider which contain all functions of vector database
   app.vectordb_client.connect()
   app.template_parser = TemplateParser(
      language = settings.PRIMARY_LANG,
      default_language = settings.DEFAULT_LANG,
   )

   app.gmail_ingestion_service = None
   app.gmail_ingestion_task = None
   if settings.GMAIL_INGESTION_ENABLED:
      try:
         app.gmail_ingestion_service = GmailIngestionService(
            db_client=app.db_client,
            settings=settings,
         )
         app.gmail_ingestion_task = asyncio.create_task(
            app.gmail_ingestion_service.poll_forever()
         )
      except Exception as exc:
         logger.error("Failed to start Gmail ingestion service: %s", exc)

#Case A — 1 user uploads a file Only 1 connection is used at a time, but it is reused for multiple requests.
  
@app.on_event("shutdown")#closes all connections when FastAPI shuts down.
async def shutdown_span():
   app.mongo_conn.close()
   app.vectordb_client.disconnect()
   
   gmail_task = getattr(app, "gmail_ingestion_task", None)
   if gmail_task is not None:
      gmail_task.cancel()
      try:
         await gmail_task
      except asyncio.CancelledError:
         pass


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
app.include_router(auth.auth_router)
app.include_router(inter.interview_router1)
app.include_router(interview.interview_router)
app.include_router(email_ingestion.email_ingestion_router)
app.include_router(job.job_router)






#v7:
#Project Boilerplates
#The MVC Architecture
#Pydantic-Settings
#FastAPI Depends Module
#How to Separate Logics
#How to construct your first Controller
#Validate Uploaded Files
#The power of Enums
#Control The Responses
#Dynamic Assets Creation
#aiofiles
#uploading chunking
#In a long-running app or containerized deployment, 
#leaving connections open can cause MongoDB to refuse new connections after a while.
#If you restart FastAPI multiple times during dev without closing, you can hit “too many connections” on Mongo.
"""
Case B — Many users uploading files simultaneously (without restarting FastAPI) :FastAPI does NOT open a new connection for each user, it reuses the pool.
Case C — FastAPI is restarted repeatedly without closing the client

Each restart creates a new connection pool

Old pools are left open → MongoDB sees many open connections

Eventually you may hit the MongoDB max connection limit

⚠ This is the danger of not calling mongo_conn.close() — it’s only relevant when the app is restarted, not during normal user requests.
"""