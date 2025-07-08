from fastapi import FastAPI, status, Depends
from sqlalchemy.orm import Session
from fastapi.params import Body
import classes
import model
from database import engine, get_db
from model import Menu
from bs4 import BeautifulSoup
import requests
from datetime import datetime

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

# class Mensagem(BaseModel):
#     titulo: str = "Luiz"
#     conteudo: str = "Martini"
#     publicada: bool = True

@app.get("/")
def read_root():
    return {"Hello": "lala"}

@app.post("/criar", status_code=status.HTTP_201_CREATED)
def criar_valores(nova_mensagem: classes.Mensagem, db: Session = Depends(get_db)):
    mensagem_criada = model.Model_Mensagem(**nova_mensagem.model_dump())
    db.add(mensagem_criada)
    db.commit()
    db.refresh(mensagem_criada)
    return{"Mensagem": mensagem_criada}

@app.get("/quadrado/{num}")
def square(num: int): 
    return num ** 2

@app.post("/scrape")
def scrape_and_save(db: Session = Depends(get_db)):
    url_base = "https://ufu.br"
    resposta = requests.get(url_base)
    if resposta.status_code != 200:
        return {"erro": "Falha ao acessar o site"}

    soup = BeautifulSoup(resposta.content, 'html.parser')
    barra = soup.find('ul', class_='sidebar-nav nav-level-0')
    if barra is None:
        return {"erro": "Estrutura HTML não encontrada"}

    linhas = barra.find_all('li', class_='nav-item')
    iniciar = False
    inseridos = 0

    for li in linhas:
        texto = li.text.strip()
        if "graduação" in texto.lower():
            iniciar = True
        if iniciar:
            link = url_base + li.a.get('href')
            menu = Menu(menuNav=texto, link=link, created_at=datetime.now())
            db.add(menu)
            inseridos += 1

    db.commit()
    return {"status": f"{inseridos} menus inseridos com sucesso"}
