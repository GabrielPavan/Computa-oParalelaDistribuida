import streamlit as st
import grpc
import backup_pb2
import backup_pb2_grpc
from google.protobuf.empty_pb2 import Empty
import os
import pandas as pd

# 🎯 Configurações do cliente gRPC
channel = grpc.insecure_channel(
    'localhost:50051',
    options=[
        ('grpc.max_receive_message_length', 200 * 1024 * 1024),
        ('grpc.max_send_message_length', 200 * 1024 * 1024),
    ]
)
stub = backup_pb2_grpc.BackupServiceStub(channel)


# 🎨 Configuração da página
st.set_page_config(page_title="Sistema de Backup gRPC", page_icon="💾")

st.title("💾 Sistema de Backup com gRPC")
st.subheader("Interface Web para envio e gerenciamento de arquivos")


# 🔄 Inicializa estado da sessão para a lista de arquivos
if 'arquivos' not in st.session_state:
    response = stub.ListFiles(Empty())
    st.session_state.arquivos = list(response.filenames)


# 🔁 Função para atualizar a lista de arquivos
def atualizar_lista_arquivos():
    response = stub.ListFiles(Empty())
    st.session_state.arquivos = list(response.filenames)


# 📤 Upload de Arquivo
st.header("📤 Enviar Arquivo")
uploaded_file = st.file_uploader("Escolha um arquivo para enviar")

if uploaded_file is not None:
    if st.button("Enviar"):
        file_content = uploaded_file.read()
        response = stub.UploadFile(backup_pb2.FileChunk(
            filename=uploaded_file.name,
            content=file_content
        ))
        if response.success:
            st.success(f"Arquivo '{uploaded_file.name}' enviado com sucesso!")
            atualizar_lista_arquivos()
        else:
            st.error(f"Erro ao enviar o arquivo '{uploaded_file.name}'")

# 📄 Listar Arquivos
st.subheader("📄 Arquivos Disponíveis no Servidor:")

if st.session_state.arquivos:
    cols = st.columns(2)  # Divide em duas colunas

    for idx, file in enumerate(st.session_state.arquivos):
        with cols[idx % 2]:
            st.markdown(f"""
        <div style='
            background-color:#1f1f1f;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 10px;
            border: 1px solid #444;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        '>
            <h5 style='color:#00CFFF; margin: 0;'>📄 {file}</h5>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Nenhum arquivo encontrado no servidor.")

# 📥 Download de Arquivo
st.header("📥 Baixar Arquivo")

if st.session_state.arquivos:
    download_file = st.selectbox("Selecione o arquivo para download:", st.session_state.arquivos)

    if download_file:
        try:
            response = stub.DownloadFile(backup_pb2.FileRequest(filename=download_file))
            if response.content:
                st.download_button(
                    label="Baixar",
                    data=response.content,
                    file_name=download_file,
                    mime="application/octet-stream"
                )
            else:
                st.error("Arquivo não encontrado no servidor.")
        except Exception as e:
            st.error(f"Erro no download: {e}")
else:
    st.info("Nenhum arquivo disponível para download no servidor.")


# 🗑️ Deletar Arquivo
st.header("🗑️ Deletar Arquivo")

if st.session_state.arquivos:
    delete_file = st.selectbox("Selecione o arquivo para deletar:", st.session_state.arquivos)

    if st.button("Deletar"):
        response = stub.DeleteFile(backup_pb2.FileRequest(filename=delete_file))
        if response.success:
            st.success(f"Arquivo '{delete_file}' deletado com sucesso.")
            atualizar_lista_arquivos()
        else:
            st.error(f"Erro ao deletar o arquivo '{delete_file}' ou arquivo não encontrado.")
else:
    st.info("Nenhum arquivo disponível para deletar no servidor.")
