# 🚀 Instruções para Executar o Projeto de Backup com gRPC

## ✅ Pré-requisitos

- Python 3.10 ou superior instalado.
- Ter o `pip` funcionando corretamente.
- Ter o `protoc` instalado (ou gerar os arquivos via `grpcio-tools` no Python).

---

## 🔧 Passo a Passo para Executar

### ① Clone ou baixe o projeto

Navegue até a pasta onde deseja salvar e rode:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

Ou baixe como ZIP e extraia.

---

### ② Crie um ambiente virtual (recomendado)

No terminal, dentro da pasta do projeto:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
```

---

### ③ Instale as dependências

```bash
pip install grpcio grpcio-tools
```

---

### ④ Gere os arquivos a partir do arquivo `.proto`

Execute:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. backup.proto
```

Isto irá gerar dois arquivos:

- `backup_pb2.py`
- `backup_pb2_grpc.py`

---

### ⑤ Execute o servidor

No terminal, dentro da pasta do projeto:

```bash
python server.py
```

O servidor ficará rodando na porta `50051` aguardando requisições.

---

### ⑥ Execute o cliente

Abra um **outro terminal**, ative o ambiente virtual novamente:

```bash
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
```

E rode:

```bash
python client.py
```

O cliente apresentará opções para:

- Enviar arquivo (Upload)
- Baixar arquivo (Download)
- Listar arquivos disponíveis no servidor
- Deletar arquivos no servidor

---

## 📂 Pasta de arquivos

Os arquivos enviados e baixados ficam armazenados na pasta `arquivos/` que estará no mesmo diretório do `server.py`.

---

## ⚙️ Parar o servidor e o cliente

- Para parar, pressione `CTRL + C` no terminal onde eles estão rodando.

---

## 🚩 Observação

Sempre que abrir um novo terminal, lembre-se de ativar o ambiente virtual antes de rodar qualquer comando:

```bash
source venv/bin/activate
```

---

