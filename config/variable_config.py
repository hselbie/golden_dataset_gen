from dotenv import load_dotenv
import os
from google import genai
class VarConfig:
    def __init__(self):
        load_dotenv()
        self.project = os.getenv("PROJECT")
        self.embedding_model = os.getenv("EMBEDDING_MODEL")
        self.location = os.getenv("LOCATION")
        self.llm = os.getenv("LLM")
        self.datastore_id = os.getenv("DATASTORE_ID")
        self.grounding_enabled = int(os.getenv("GROUNDING", 0))
        self.google_api_key_ = os.getenv("GAPIKEY")
        self.client = genai.Client(vertexai=True, project=self.project, location=self.location)


#%%        
# import vertexai

# from vertexai.preview.generative_models import (
#     GenerationConfig,
#     GenerativeModel,
#     Tool,
#     grounding,
#     HarmCategory,
#     HarmBlockThreshold
# )

# # TODO(developer): Update and un-comment below lines
# PROJECT_ID = "zinc-forge-302418"
# data_store_id = "google-store_1719441609798"

# vertexai.init(project=PROJECT_ID, location="us-central1")

# model = GenerativeModel("gemini-1.5-flash-001")

# tool = Tool.from_retrieval(
#     grounding.Retrieval(
#         grounding.VertexAISearch(
#             datastore=data_store_id,
#             project=PROJECT_ID,
#             location="global",
#         )
#     )
# )

# prompt = "How do I make an appointment to renew my driver's license?"
# response = model.generate_content(
#     prompt,
#     tools=[tool],
#     safety_settings={
#         HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#             },
#     generation_config=GenerationConfig(
#         temperature=0.0,
#     ),
# )

# print(response.text)
# # %%
