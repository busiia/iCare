from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Mock DB
pacientes = {}
respostas = {}

# Modelos
class Paciente(BaseModel):
    nome: str
    cpf: str
    nome_mae: str

class Questionario(BaseModel):
    cpf: str
    mobilidade: bool
    alimentacao: bool
    higiene: bool
    trabalho: bool
    dor: bool

class Relatorio(BaseModel):
    nome: str
    cpf: str
    score: int
    classificacao: str
    assinatura_paciente: Optional[str] = None

# Rota de admissão
@app.post("/paciente/admitir")
def admitir_paciente(paciente: Paciente):
    if paciente.cpf in pacientes:
        raise HTTPException(status_code=400, detail="Paciente já cadastrado.")
    pacientes[paciente.cpf] = paciente
    return {"mensagem": "Paciente admitido com sucesso."}

# Rota de questionário
@app.post("/questionario/responder")
def responder_questionario(q: Questionario):
    if q.cpf not in pacientes:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    
    score = (
        int(q.mobilidade) * 20 +
        int(q.alimentacao) * 20 +
        int(q.higiene) * 20 +
        int(q.trabalho) * 20 +
        (0 if q.dor else 20)
    )
    
    classificacao = (
        "Paliativo" if score < 50 else
        "Monitoramento" if score < 75 else
        "Estável"
    )
    
    respostas[q.cpf] = {
        "score": score,
        "classificacao": classificacao
    }
    
    return {"mensagem": "Respostas registradas com sucesso.", "score": score, "classificacao": classificacao}

# Rota de relatório
@app.get("/relatorio/{cpf}", response_model=Relatorio)
def obter_relatorio(cpf: str):
    if cpf not in pacientes or cpf not in respostas:
        raise HTTPException(status_code=404, detail="Dados incompletos para o CPF fornecido.")
    
    paciente = pacientes[cpf]
    resultado = respostas[cpf]
    
    return Relatorio(
        nome=paciente.nome,
        cpf=paciente.cpf,
        score=resultado["score"],
        classificacao=resultado["classificacao"]
    )
