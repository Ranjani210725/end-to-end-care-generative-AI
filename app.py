from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.llms import Cohere
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os

app =Flask(__name__)
load_dotenv()

PINECONE_API_KEY=os.environ.get("PINECONE_API_KEY")
COHERE_API_KEY=os.environ.get("COHERE_API_KEY")

os.environ["PINECONE_API_KEY"]= PINECONE_API_KEY
os.environ["COHERE_API_KEY"]=COHERE_API_KEY

embeddings=download_hugging_face_embeddings()

index_name="carebot"


docsearch=PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings

)
retriever=docsearch.as_retriever(search_type="similarity",search_kwargs={"k":3})

llm= Cohere(temperature=0.4,max_tokens=500)
prompt=ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        ("human","{input}"),
    ]
)

question_answer_chain=create_stuff_documents_chain(llm,prompt)
rag_chain=create_retrieval_chain(retriever,question_answer_chain)

@app.route("/")
def index():
    return render_template('chat.html')

###@app.route("/get", methods=["POST"])
#def chat():
 #   msg = request.form["msg"]
  #  input = msg
   # print(input)
    #response = rag_chain.invoke({"input": msg})
    #print("Response :",response["answer"])
    #return str(response["answer"])
@app.route("/get", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data["message"]
    print("User Input:", msg)
    response = rag_chain.invoke({"input": msg})
    print("Response:", response["answer"])
    return jsonify({"reply": response["answer"]})




if __name__=='__main__':
    app.run(host="0.0.0.0",port=8080,debug=True)
     