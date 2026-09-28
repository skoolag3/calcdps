# Etapa 1: instala as dependências da aplicação
FROM python:3.12-slim AS builder

WORKDIR /app

# Copia primeiro apenas o requirements para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências em uma pasta separada
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Etapa 2: imagem final, mais limpa e menor
FROM python:3.12-slim

WORKDIR /app

# Copia somente as dependências instaladas na etapa anterior
COPY --from=builder /install /usr/local

# Copia os arquivos do projeto
COPY . .

# Porta padrão utilizada pelo Streamlit
EXPOSE 8501

# Executa a aplicação permitindo acesso externo ao container
CMD ["streamlit", "run", "ini.py", "--server.address=0.0.0.0", "--server.port=8501"]